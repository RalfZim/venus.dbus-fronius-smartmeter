# dbus-fronius-smartmeter Service

### Purpose

This service is meant to be run on a raspberry Pi with Venus OS from Victron.

The Python script cyclically reads data from the Fronius SmartMeter via the Fronius REST API and publishes information on the dbus, using the service name com.victronenergy.grid. This makes the Venus OS work as if you had a physical Victron Grid Meter installed.

### Configuration

In the Python file, you should put the IP of your Fronius device that hosts the REST API. In my setup, it is the IP of the Fronius Symo, which gets the data from the Fronius Smart Metervia the RS485 connection between them.

### Installation

1. Copy the files to the /data folder on your venus:

   - /data/dbus-fronius-smartmeter/dbus-fronius-smartmeter.py
   - /data/dbus-fronius-smartmeter/kill_me.sh
   - /data/dbus-fronius-smartmeter/service/run

2. Set permissions for files:

   `chmod 755 /data/dbus-fronius-smartmeter/service/run`

   `chmod 744 /data/dbus-fronius-smartmeter/kill_me.sh`

3. Get two files from the [velib_python](https://github.com/victronenergy/velib_python) and install them on your venus:

   - /data/dbus-fronius-smartmeter/vedbus.py
   - /data/dbus-fronius-smartmeter/ve_utils.py

4. Add a symlink to the file /data/rc.local:

   `ln -s /data/dbus-fronius-smartmeter/service /service/dbus-fronius-smartmeter`

   Or if that file does not exist yet, store the file rc.local from this service on your Raspberry Pi as /data/rc.local .
   You can then create the symlink by just running rc.local:
  
   `rc.local`

   The daemon-tools should automatically start this service within seconds.

### Debugging

You can check the status of the service with svstat:

`svstat /service/dbus-fronius-smartmeter`

It will show something like this:

`/service/dbus-fronius-smartmeter: up (pid 10078) 325 seconds`

If the number of seconds is always 0 or 1 or any other small number, it means that the service crashes and gets restarted all the time.

When you think that the script crashes, start it directly from the command line:

`python /data/dbus-fronius-smartmeter/dbus-fronius-smartmeter.py`

and see if it throws any error messages.

If the script stops with the message

`dbus.exceptions.NameExistsException: Bus name already exists: com.victronenergy.grid"`

it means that the service is still running or another service is using that bus name.

#### Restart the script

If you want to restart the script, for example after changing it, just run the following command:

`/data/dbus-fronius-smartmeter/kill_me.sh`

The daemon-tools will restart the scriptwithin a few seconds.

### Hardware

In my installation at home, I am using the following Hardware:

- Fronius Symo - PV Grid Tied Inverter (three phases)
- Fronius Smart Meter 63A-3 - (three phases)
- Victron MultiPlus-II - Battery Inverter (single phase)
- Raspberry Pi 3B+ - For running Venus OS
- Pylontech US2000 Plus - LiFePO Battery

