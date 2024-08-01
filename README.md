# dbus-fronius-smartmeter Service

## Purpose

This service is meant to be run on a raspberry Pi with Venus OS from Victron.

The Python script cyclically reads data from the Fronius SmartMeter via the Fronius REST API and publishes information on the dbus, using the service name com.victronenergy.grid. This makes the Venus OS work as if you had a physical Victron Grid Meter installed.

## Configuration

Copy/rename the `config.sample.ini` file to `config.ini` in the `dbus-fronius-smartmeter` directory.

In the Python file, you should put the IP of your Fronius device that hosts the REST API. In my setup, it is the IP of the Fronius Symo, which gets the data from the Fronius Smart Metervia the RS485 connection between them.

## Installation

If you have a CerboGX, you'd first have to enable the root user ([Venus OS:Root Access](https://www.victronenergy.com/live/ccgx:root_access#root_access)) and have a working SSH connection.

### Install script

1. Login to your venusOS device as root
2. Execute following steps to install
    ```bash
    # change to temp folder
    cd /tmp

    # download service files
    wget -O /tmp/dbus-fronius-smartmeter.zip https://github.com/RalfZim/venus.dbus-fronius-smartmeter/archive/refs/heads/master.zip

    # unzip folder
    unzip dbus-fronius-smartmeter.zip

    # move files
    mv -f /tmp/venus.dbus-fronius-smartmeter-main/dbus-fronius-smartmeter /data/etc/

    # copy default config file
    cp /data/etc/dbus-fronius-smartmeter/config.sample.ini /data/etc/dbus-fronius-smartmeter/config.ini

    # edit the config file with vi or nano
    vi /data/etc/dbus-fronius-smartmeter/config.ini
    #nano /data/etc/dbus-fronius-smartmeter/config.ini
    ```

3. Install
    ```bash
    bash /data/etc/dbus-fronius-smartmeter/install.sh
    ```

### updating (optional)

```bash
  # backup config file
  mv /data/etc/dbus-fronius-smartmeter/config.ini /data/etc/dbus-fronius-smartmeter_config_backup.ini

  # remove old files
  rm -rf /tmp/venus.dbus-fronius-smartmeter-main

  # If updating: cleanup existing service
  rm -rf /data/etc/dbus-fronius-smartmeter

  # ... install 

  # restore config file
  mv /data/etc/dbus-fronius-smartmeter_config.ini /data/etc/dbus-fronius-smartmeter/config.ini
```

### uninstall

```bash
bash /data/etc/dbus-fronius-smartmeter/uninstall.sh
```

### restart

```bash
bash /data/etc/dbus-fronius-smartmeter/restart.sh
```

## Debugging

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

You can also check the logs:

`tail -n100 -f /var/log/dbus-fronius-smartmeter/current`

## Hardware

In my installation at home, I am using the following Hardware:

- Fronius Symo - PV Grid Tied Inverter (three phases)
- Fronius Smart Meter 63A-3 - (three phases)
- Victron MultiPlus-II - Battery Inverter (single phase)
- Raspberry Pi 3B+ - For running Venus OS
- Pylontech US2000 Plus - LiFePO Battery

Also tested with:

- Fronius Symo 5.0.3-M (3p)
- Fronius TS65A-3 (3p)
- Victron MultiPlus-II 48/3000/35-32 (1p) as 2p setup ESS
- CerboGX
- Pylontech US3000C parallel (2)