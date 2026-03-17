#!/usr/bin/env python3
import spidev
import time
import requests  # Ajout pour les requêtes HTTP

# Configuration SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
spi.mode = 0b00
spi.bits_per_word = 8

# Configuration API
API_URL = "http://127.0.0.1:5000/api/gas"

def read_ad7475():
    # Lecture de 2 octets
    raw = spi.xfer2([0x00, 0x00])
    # Concatène les 2 octets
    value = (raw[0] << 8) | raw[1]
    # Extraction des 12 bits utiles (selon ton montage)
    adc = (value >> 4) & 0x0FFF
    return adc

try:
    print(f"Démarrage de l'envoi vers {API_URL}...")
    while True:
        adc_value = read_ad7475()

        # 1. Mise à l'échelle : 12 bits (0-4095) -> 8 bits (0-255)
        # On divise par 16.058 (soit 4095/255) ou on utilise un décalage de bits
        gas_level = int((adc_value / 4095.0) * 255)

        # 2. Préparation des données pour Flask
        payload = {"value": gas_level}

        try:
            # Envoi de la donnée via POST
            response = requests.post(API_URL, json=payload, timeout=1)
            
            status = "OK" if response.status_code == 200 else f"Erreur {response.status_code}"
            print(f"ADC: {adc_value:4d} | Gas Level: {gas_level:3d} | API: {status}")
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")

        time.sleep(0.5)  # On ralentit un peu pour ne pas spammer le serveur

except KeyboardInterrupt:
    spi.close()
    print("\nArrêt du script.")