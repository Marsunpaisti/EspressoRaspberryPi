import time
import board
import digitalio
import pwmio
import adafruit_max31855
import numpy as np

spi = board.SPI()
cs = digitalio.DigitalInOut(board.D8)
heaterPin = pwmio.PWMOut(board.D4, frequency=1, duty_cycle=0, variable_frequency=False)
#heaterPin = digitalio.DigitalInOut(board.D4)
#heaterPin.switch_to_output(False)

max31855 = adafruit_max31855.MAX31855(spi, cs)
i = 0
while True:
    i += 1
    tempC = max31855.temperature
    print(f"Temperature: {tempC:.2f}")
    #state = ("On" if heaterPin.value == True else "Off")
    #state = ("On" if heaterPin.duty_cycle != 0 else "Off")
    dutyCycleRatio = 0.5
    heaterPin.duty_cycle = round(dutyCycleRatio * 65535)
    #print(f"Pin {heaterPin._pin} {state}")
        
    time.sleep(3.0)
