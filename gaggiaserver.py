import math
import threading
from time import time
import socketio
import argparse
from eventlet import wsgi, listen, monkey_patch
from gaggiacontroller import GaggiaController
import collections

monkey_patch()
print(f"Monkeypatched: {threading.current_thread.__module__}")


parser = argparse.ArgumentParser(description="PID Control and SocketIO server for Gaggia Classic Pro",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--ip", action="store",
                    help="Send UDP telemetry to ip address", required=False, default=None)
parser.add_argument("-p", "--port", action="store",
                    help="Send UDP telemetry to port", default=7788)
parser.add_argument("-d", "--disableprints", action="store_true",
                    help="Disable prints", default=False)
args = parser.parse_args()
config = vars(args)
DATA_SEND_IP = config["ip"]
DATA_SEND_PORT = config["port"]
DISABLE_PRINTS = config["disableprints"]
MAX_RETAINED_TELEMETRY_HISTORY = 30
telemetryAddress = None
if (DATA_SEND_IP != None):
    telemetryAddress = (DATA_SEND_IP, DATA_SEND_PORT)

# create a Socket.IO server
sio = socketio.Server(async_mode="eventlet", cors_allowed_origins="*")
# wrap with a WSGI application
app = socketio.WSGIApp(sio)


telemetryHistory = collections.deque(maxlen=MAX_RETAINED_TELEMETRY_HISTORY)


def sendAndStoreTelemetry(telemetryData: dict):
    global telemetryHistory
    telemetryHistory.append(telemetryData)
    sio.emit("telemetry", telemetryData)


def sendInitialDataOnConnect():
    global telemetryHistory
    sio.emit("telemetryHistory", list(telemetryHistory))


gaggiaController = GaggiaController(
    telemetryAddress, sendAndStoreTelemetry, DISABLE_PRINTS)

app.static_files = {
    "/": "./frontendBuild/index.html",
    "/static": "./frontendBuild/static"
}


def debugPrint(text: str):
    if (DISABLE_PRINTS):
        return
    print(text)


@sio.event
def connect(sid, environ):
    debugPrint(f"New connection: {sid}")
    sendInitialDataOnConnect()


@sio.on("set_brew_setpoint")
def set_brew_setpoint_handler(sid, data):
    return gaggiaController.setBrewSetpoint(data)


@sio.on("set_steam_setpoint")
def set_steam_setpoint_handler(sid, data):
    return gaggiaController.setSteamSetpoint(data)


@sio.on("set_shot_time_limit")
def set_shot_time_limit_handler(sid, data):
    return gaggiaController.setShotTimeLimit(data)


@sio.on("test_print")
def test_print_handler(sid, data):
    print(f"tp {data}")
    return "ack"


def startListening():
    wsgi.server(listen(("", 80)), app)


def mockTelemetrySender():
    sio.sleep(3)
    for i in range(1, 2000):
        telemetryData = {}
        telemetryData["ts"] = round(time()*1000)
        telemetryData["temp"] = math.sin(
            time() * (2*math.pi / 120)) * 40 + 60
        telemetryData["out"] = 0
        telemetryData["set"] = 93
        sendAndStoreTelemetry(telemetryData)
        sio.sleep(1)


if __name__ == "__main__":
    # gaggiaController.start()
    serverThread = threading.Thread(
        target=startListening, args=(), daemon=True)
    testSignalsThread = threading.Thread(target=mockTelemetrySender, args=())
    testSignalsThread.start()
    serverThread.start()

    try:
        testSignalsThread.join()
    except:
        print("Woop")
    # gaggiaController.controlLoopThread.join()
