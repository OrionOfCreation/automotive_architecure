#!/usr/bin/env python3
"""
Lecture SPI (AD7475 → gaz) + réception CAN bus
Envoi toutes les 0.5s vers l'API Flask du tableau de bord.

Dépendances :
    pip install spidev requests python-can

Activation de l'interface CAN sur le Raspberry Pi (à faire une fois) :
    sudo ip link set can0 type can bitrate 500000
    sudo ip link set up can0
"""

import spidev
import time
import threading
import requests
import can

# ── Configuration ──────────────────────────────────────────────────────────────

API_BASE    = "http://127.0.0.1:5000"
CAN_CHANNEL = "can0"       # Interface SocketCAN du RS485 CAN HAT
CAN_BITRATE = 500_000      # Adapter si nécessaire (250000, 125000, …)

# CAN IDs
CAN_ID_LIGHTS = 0x100      # STM32 – éclairage  (1 octet, bits 0-5)
CAN_ID_SPEED  = 0x120      # ESP32 – vitesse     (1 octet, 0..100 %)
CAN_ID_RADAR  = 0x200      # STM32 – radar recul (decimal 200 = 0xC8, octets 0-3)
CAN_ID_AEB    = 0x301      # ESP32 – freinage    (1 octet, 0 ou 1)

# ── SPI – capteur de gaz AD7475 ───────────────────────────────────────────────

spi = spidev.SpiDev()
spi.open(0, 1)
spi.max_speed_hz = 1_000_000
spi.mode          = 0b00
spi.bits_per_word = 8

def read_ad7475() -> int:
    """Retourne la valeur brute 12 bits du CAN AD7475 (0–4095)."""
    raw   = spi.xfer2([0x00, 0x00])
    value = (raw[0] << 8) | raw[1]
    return (value >> 4) & 0xFFFF

# ── État partagé des éclairages (mis à jour par le thread CAN) ────────────────

lights_state = {
    "low_beam":   0,   # headlights      – bit 1
    "high_beam":  0,   # full_headlights – bit 0
    "turn_left":  0,   # left_blinker    – bit 4 (ou forcé par warning)
    "turn_right": 0,   # right_blinker   – bit 3 (ou forcé par warning)
}
lights_lock = threading.Lock()

# ── État partagé vitesse + AEB (mis à jour par le thread CAN) ─────────────────

speed_state = {"value": 0}    # 0..100 (speed_cmd_pct de l'ESP32)
aeb_state   = {"value": 0}    # 0 ou 1
speed_lock  = threading.Lock()
aeb_lock    = threading.Lock()

# ── État partagé radar recul (mis à jour par le thread CAN) ───────────────────
# Les capteurs sont reçus de droite à gauche (vue depuis le véhicule) :
#   data[0] = arr_d_ext  (Arrière Droit  Extérieur)
#   data[1] = arr_d_int  (Arrière Droit  Intérieur)
#   data[2] = arr_g_int  (Arrière Gauche Intérieur)
#   data[3] = arr_g_ext  (Arrière Gauche Extérieur)

radar_state = {
    "arr_d_ext": 255,
    "arr_d_int": 255,
    "arr_g_int": 255,
    "arr_g_ext": 255,
}
radar_lock = threading.Lock()

# ── Thread de réception CAN ───────────────────────────────────────────────────

def can_listener():
    """
    Écoute en continu le bus CAN et dispatche selon l'ID :

        0x100 – STM32 éclairage   : DATA[0] bits 0-5
        0x120 – ESP32 vitesse     : DATA[0] = speed_cmd_pct (0..100)
        0x301 – ESP32 AEB         : DATA[0] = 0 ou 1
    """
    try:
        bus = can.interface.Bus(
            channel = CAN_CHANNEL,
            bustype = "socketcan",
            bitrate = CAN_BITRATE,
        )
        print(f"[CAN] Interface {CAN_CHANNEL} ouverte")
        print(f"[CAN]   écoute 0x{CAN_ID_LIGHTS:03X} (éclairage)")
        print(f"[CAN]   écoute 0x{CAN_ID_RADAR:03X}  (radar recul)")
        print(f"[CAN]   écoute 0x{CAN_ID_SPEED:03X}  (vitesse)")
        print(f"[CAN]   écoute 0x{CAN_ID_AEB:03X}  (AEB)")
    except Exception as e:
        print(f"[CAN] Impossible d'ouvrir {CAN_CHANNEL} : {e}")
        return

    try:
        for msg in bus:
            aid = msg.arbitration_id

            # ── 0x100 : éclairage ────────────────────────────────────────────
            if aid == CAN_ID_LIGHTS:
                byte = msg.data[0]
                # blind_spot      = (byte >> 5) & 1   # non câblé sur le dashboard
                left_blinker    = (byte >> 4) & 1
                right_blinker   = (byte >> 3) & 1
                warning         = (byte >> 2) & 1
                headlights      = (byte >> 1) & 1
                full_headlights =  byte       & 1

                if warning:
                    left_blinker  = 1
                    right_blinker = 1

                with lights_lock:
                    lights_state["low_beam"]   = headlights
                    lights_state["high_beam"]  = full_headlights
                    lights_state["turn_left"]  = left_blinker
                    lights_state["turn_right"] = right_blinker

            # ── 0x200 : radar recul ─────────────────────────────────────
            # data[0..3] = distances capteurs, de droite à gauche (vue véhicule)
            # data[4] = status  |  data[7] = counter  (ignorés)
            elif aid == CAN_ID_RADAR:
                with radar_lock:
                    radar_state["arr_d_ext"] = int(msg.data[0])
                    radar_state["arr_d_int"] = int(msg.data[1])
                    radar_state["arr_g_int"] = int(msg.data[2])
                    radar_state["arr_g_ext"] = int(msg.data[3])

            # ── 0x120 : vitesse (0..100) ─────────────────────────────────────
            elif aid == CAN_ID_SPEED:                
                with speed_lock:
                    speed_state["value"] = int(msg.data[0])

            # ── 0x301 : AEB (0 ou 1) ─────────────────────────────────────────
            elif aid == CAN_ID_AEB:
                with aeb_lock:
                    aeb_state["value"] = 1 if msg.data[0] else 0

    except Exception as e:
        print(f"[CAN] Erreur lors de la réception : {e}")
    finally:
        bus.shutdown()

# ── Envoi vers l'API Flask ────────────────────────────────────────────────────

def post(endpoint: str, payload: dict) -> str:
    """POST vers l'API Flask. Retourne 'OK' ou le message d'erreur."""
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=1)
        return "OK" if r.status_code == 200 else f"HTTP {r.status_code}"
    except requests.exceptions.RequestException as e:
        return f"ERR {e}"

# ── Point d'entrée ────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # Démarrage du thread CAN en arrière-plan (daemon → s'arrête avec le process)
    t = threading.Thread(target=can_listener, daemon=True)
    t.start()

    print(f"[GAZ] Démarrage de l'envoi vers {API_BASE}…")

    try:
        while True:
            # ── Gaz ──────────────────────────────────────────────────────────
            adc_value = read_ad7475()
            gas_level = int(adc_value)
            # Décommenter la ligne suivante pour ramener en 0-255 :
            # gas_level = int((adc_value / 4095.0) * 255)

            gas_status = post("/api/gas", {"value": gas_level})
            print(f"[GAZ] ADC={adc_value:4d}  gas_level={gas_level:4d}  → {gas_status}")

            # ── Radar recul ───────────────────────────────────────────────────
            with radar_lock:
                snapshot_radar = dict(radar_state)

            for sensor, value in snapshot_radar.items():
                status = post(f"/api/radar/{sensor}", {"value": value})
                print(f"[CAN] {sensor:<12s} = {value:3d}  → {status}")

            # ── Éclairage ────────────────────────────────────────────────────
            with lights_lock:
                snapshot_lights = dict(lights_state)

            for light, value in snapshot_lights.items():
                status = post(f"/api/lights/{light}", {"status": value})
                print(f"[CAN] {light:<12s} = {value}  → {status}")

            # ── Vitesse ───────────────────────────────────────────────────────
            with speed_lock:
                speed_val = speed_state["value"]

            status = post("/api/speed", {"value": speed_val})
            print(f"[CAN] speed        = {speed_val:3d}  → {status}")

            # ── AEB (freinage d'urgence) ──────────────────────────────────────
            with aeb_lock:
                aeb_val = aeb_state["value"]

            status = post("/api/braking/emergency", {"status": aeb_val})
            print(f"[CAN] aeb          = {aeb_val}    → {status}")

            time.sleep(0.5)

    except KeyboardInterrupt:
        spi.close()
        print("\n[INFO] Arrêt du script.")