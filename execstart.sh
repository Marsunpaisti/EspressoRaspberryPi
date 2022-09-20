/sbin/iw dev wlan0 set power_save off
/usr/bin/python /home/pi/PythonScripts/EspressoRaspberryPi/gaggiaserver.py > /home/pi/gaggiaserver.log 2>&1
/usr/bin/python /home/pi/PythonScripts/EspressoRaspberryPi/shutdownallpins.py > /home/pi/gaggiaserver.log 2>&1
