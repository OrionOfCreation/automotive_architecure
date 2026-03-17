#!/usr/bin/env python3
import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)              # bus 0, CE0 -> /dev/spidev0.0
spi.max_speed_hz = 1000000  # 1 MHz pour commencer
spi.mode = 0b00             # tester mode 0 en premier
spi.bits_per_word = 8

def read_ad7475():
    # lecture de 2 octets
    raw = spi.xfer2([0x00, 0x00])

    # concatène les 2 octets
    value = (raw[0] << 8) | raw[1]

    # sur beaucoup de montages AD7475 : 12 bits utiles dans les bits de poi>
    adc = (value >> 4) & 0x0FFF

    return raw, adc

try:
    while True:
        raw, adc = read_ad7475()

        # conversion en tension si REF = 5V
        voltage = adc * 5 / 4095.0

        print(f"Brut SPI = {raw} | ADC = {adc:4d} | Tension = {voltage:.3f}>")
        time.sleep(0.2)

except KeyboardInterrupt:
    spi.close()
    print("\nArrêt.")