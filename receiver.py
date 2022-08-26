import os
import socket
import threading
import struct
import time

def listenForData(sock):
    sock.bind(('127.0.0.1', 7788))
    print("Listening for data...")
    while True:
        try:
            data, addr = sock.recvfrom(1024)        
            timestamp, boilerTemperature, heaterDutyCycle = struct.unpack("!fff", data)
            print(f"Received data: T: {timestamp} Temp: {boilerTemperature} HeaterDutyCycle: {heaterDutyCycle}")
        except OSError as e:
            print(f"Socket closed")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    listener = threading.Thread(target=listenForData, args=(sock,))
    listener.start()

    while True:
        try: 
            time.sleep(5)
        except KeyboardInterrupt:
            print("Exiting")
            sock.close()
            os._exit(0)

if __name__ == "__main__":
    main()