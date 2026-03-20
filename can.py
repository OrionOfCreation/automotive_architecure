#!/usr/bin/env python3
"""
Lecture SPI (AD7475 → gaz) + réception CAN bus (ID 0x100 → éclairage)
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

API_BASE = "http://127.0.0.1:5000"
CAN_CHANNEL = "can0"  # Interface SocketCAN du RS485 CAN HAT
CAN_MSG_ID = 0x100  # ID du message d'éclairage
CAN_BITRATE = 125_000  # Adapter si nécessaire (250000, 125000, …)

# ── SPI – capteur de gaz AD7475 ───────────────────────────────────────────────

spi = spidev.SpiDev()
spi.open(0, 1)
spi.max_speed_hz = 1_000_000
spi.mode = 0b00
spi.bits_per_word = 8


def read_ad7475() -> int:
    """Retourne la valeur brute 12 bits du CAN AD7475 (0–4095)."""
    raw = spi.xfer2([0x00, 0x00])
    value = (raw[0] << 8) | raw[1]
    return (value >> 4) & 0xFFFF


# ── État partagé des éclairages (mis à jour par le thread CAN) ────────────────

lights_state = {
    "low_beam": 0,  # headlights      – bit 1
    "high_beam": 0,  # full_headlights – bit 0
    "turn_left": 0,  # left_blinker    – bit 4 (ou forcé par warning)
    "turn_right": 0,  # right_blinker   – bit 3 (ou forcé par warning)
}
lights_lock = threading.Lock()

# ── Thread de réception CAN ───────────────────────────────────────────────────


def can_listener():
    """
    Écoute en continu le bus CAN.
    À chaque réception d'un message ID 0x100, décompresse RxData[0]
    exactement comme le ferait le STM32 :

        bit 5 : blind_spot       (non utilisé côté dashboard)
        bit 4 : left_blinker
        bit 3 : right_blinker
        bit 2 : warning          → force turn_left ET turn_right à 1
        bit 1 : headlights       → low_beam
        bit 0 : full_headlights  → high_beam
    """
    try:
        bus = can.interface.Bus(
            channel=CAN_CHANNEL,
            bustype="socketcan",
            bitrate=CAN_BITRATE,
        )
        print(f"[CAN] Interface {CAN_CHANNEL} ouverte, écoute ID 0x{CAN_MSG_ID:03X}…")
    except Exception as e:
        print(f"[CAN] Impossible d'ouvrir {CAN_CHANNEL} : {e}")
        return

    try:
        for msg in bus:
            if msg.arbitration_id != CAN_MSG_ID:
                continue

            byte = msg.data[0]

            # Décompression – même logique que le STM32
            # blind_spot      = (byte >> 5) & 1   # non câblé sur le dashboard
            left_blinker = (byte >> 4) & 1
            right_blinker = (byte >> 3) & 1
            warning = (byte >> 2) & 1
            headlights = (byte >> 1) & 1
            full_headlights = byte & 1

            # Warning actif → les deux clignotants s'allument simultanément
            if warning:
                left_blinker = 1
                right_blinker = 1

            with lights_lock:
                lights_state["low_beam"] = headlights
                lights_state["high_beam"] = full_headlights
                lights_state["turn_left"] = left_blinker
                lights_state["turn_right"] = right_blinker

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

            # ── Éclairage (snapshot thread-safe de l'état CAN) ───────────────
            with lights_lock:
                snapshot = dict(lights_state)

            for light, value in snapshot.items():
                status = post(f"/api/lights/{light}", {"status": value})
                print(f"[CAN] {light:<12s} = {value}  → {status}")

            time.sleep(0.5)

    except KeyboardInterrupt:
        spi.close()
        print("\n[INFO] Arrêt du script.")
