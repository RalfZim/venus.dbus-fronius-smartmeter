# dbus-MQTT to Grid Meter Service

### Disclaimer

This Script/Project was forked from RalfZim/venus.dbus-fronius-smartmeter. 
I removed the request area and added an MQTT subscriber / client.
You have to run Paho Client on your GXDevice to make this script work

python -m ensurepip --upgrade
pip install paho-mqtt


### Purpose

The Python script cyclically reads data from a MQTT Broker and publishes information on the dbus, using the service name com.victronenergy.grid. This makes the Venus OS work as if you had a physical Victron Grid Meter installed.

### Configuration

In the Python file, you should put the IP of your Broker

### Installation

1. Copy the files to the /data folder on your venus:

    Copy the files to the /data folder on your venus:
        /data/mqtttogrid/MQTTtoGridMeter.py
        /data/mqtttogrid/kill_me.sh
        /data/mqtttogrid/service/run
        
2. Set permissions for files:

    chmod 755 /data/mqtttogrid/service/run

    chmod 744 /data/mqtttogrid/kill_me.sh


3. Get two files from the [velib_python](https://github.com/victronenergy/velib_python) and install them on your venus:

        /data/mqtttogrid/vedbus.py
        /data/mqtttogrid/ve_utils.py


4. Add a symlink to the file /data/rc.local:

   `ln -s /data/mqtttogrid/service /service/mqtttogrid`

   Or if that file does not exist yet, store the file rc.local from this service on your Raspberry Pi as /data/rc.local .
   You can then create the symlink by just running rc.local:
  
   `rc.local`

   The daemon-tools should automatically start this service within seconds.

### Debugging

You can check the status of the service with svstat:

`svstat /service/mqtttogrid`

It will show something like this:

`/service/mqtttogrid: up (pid 10078) 325 seconds`

If the number of seconds is always 0 or 1 or any other small number, it means that the service crashes and gets restarted all the time.

When you think that the script crashes, start it directly from the command line:

`python /data/mqtttogrid/MQTTtoGridMeter.py`

and see if it throws any error messages.

If the script stops with the message

`dbus.exceptions.NameExistsException: Bus name already exists: com.victronenergy.grid"`

it means that the service is still running or another service is using that bus name.

#### Restart the script

If you want to restart the script, for example after changing it, just run the following command:

`/data/mqtttogrid/kill_me.sh`

The daemon-tools will restart the scriptwithin a few seconds.

### Hardware

In my installation at home, I am using the following Hardware:


- Victron MultiPlus-II - Battery Inverter (3phase phase)
- CerboGX
- Tasmota MQTT (modified to send every 3 seconds)

### Star this Project if you like it. If you need help start an issue :)
