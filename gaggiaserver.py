import threading
from time import sleep
import socketio
import argparse
from eventlet import wsgi, listen
from gaggiacontroller import GaggiaController


parser = argparse.ArgumentParser(description="PID Control and SocketIO server for Gaggia Classic Pro",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--ip", action="store",
                    help="Send UDP telemetry to ip address", required=False, default=None)
parser.add_argument("-p", "--port", action="store",
                    help="Send UDP telemetry to port", default=7788)
parser.add_argument("-d", "--disableprints", action="store_true",
                    help="Disable prints", default=False),
args = parser.parse_args()
config = vars(args)
DATA_SEND_IP = config["ip"]
DATA_SEND_PORT = config["port"]
DISABLE_PRINTS = config["disableprints"]

telemetryAddress = None
if (DATA_SEND_IP != None):
    telemetryAddress = (DATA_SEND_IP, DATA_SEND_PORT)

# create a Socket.IO server
sio = socketio.Server(async_mode="eventlet")
# wrap with a WSGI application
app = socketio.WSGIApp(sio)
gaggiaController = GaggiaController(telemetryAddress, sio, DISABLE_PRINTS)

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
    print(f"test_print {data}")
    return "ack"


def startListening():
    wsgi.server(listen(("", 80)), app)


def send_test_signals():
    sleep(1)
    for i in range(1, 1000000):
        sleep(1)
        telemetryData = {}
        telemetryData["temperature"] = i
        telemetryData["dutyCycle"] = 0
        telemetryData["setpoint"] = 0
        sio.emit("telemetry", telemetryData)
        print(f"Emit {i}")


if __name__ == "__main__":
    # gaggiaController.start()
    threading.Thread(target=send_test_signals, args=()).start()
    startListening()
    # gaggiaController.controlLoopThread.join()
