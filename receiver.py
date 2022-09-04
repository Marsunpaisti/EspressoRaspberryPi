import os
import socket
import threading
import struct
import time
import argparse

parser = argparse.ArgumentParser(description="Sends dummy data over UDP to target ip and port", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--ip", action="store", help="Receive ip address", default="0.0.0.0")
parser.add_argument("-p", "--port", action="store", help="Receive port", default=7788)
args = parser.parse_args()
config = vars(args)
IP = config["ip"]
PORT = config["port"]

def listenForData(sock: socket.socket):
    print("Listening for data...")
    while True:
        try:    
            data, addr = sock.recvfrom(1024)        
            timestamp, boilerTemperature, heaterDutyCycle = struct.unpack("fff", data)
            print(f"Rcv T: {timestamp:.2f} Temp: {boilerTemperature} HeaterDutyCycle: {heaterDutyCycle}")
        except OSError as e:
            print(f"Socket closed")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind((IP, PORT))
    threading.Thread(target=listenForData,args=(sock,)).start()
    while True:
        try: 
            time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting")
            sock.close()
            os._exit(0)

if __name__ == "__main__":
    main()