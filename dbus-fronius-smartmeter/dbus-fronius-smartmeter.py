#!/usr/bin/env python

"""
Created by Ralf Zimmermann (mail@ralfzimmermann.de) in 2020.
This code and its documentation can be found on: https://github.com/RalfZim/venus.dbus-fronius-smartmeter
Used https://github.com/victronenergy/velib_python/blob/master/DbusFroniusSmartMeterService.py as basis for this service.
Reading information from the Fronius Smart Meter via http REST API and puts the info on dbus.
"""
try:
  import gobject  # Python 2.x
except:
  from gi.repository import GLib as gobject # Python 3.x
import platform
import logging
import sys
import os
from time import sleep, time
import configparser  # for config/ini file
import requests # for http GET
try:
  import thread   # for daemon = True  / Python 2.x
except:
  import _thread as thread   # for daemon = True  / Python 3.x

# our own packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "ext", "velib_python"))
from vedbus import VeDbusService

# get values from config.ini file
try:
    config_file = (os.path.dirname(os.path.realpath(__file__))) + "/config.ini"
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        # check inverter ip
        if "DEFAULT" in config and "inverter_ip" in config["DEFAULT"]:
            inverter_ip = config["DEFAULT"]["inverter_ip"]
            logging.debug(
                'using inverter_ip ' + config["DEFAULT"]["inverter_ip"]
            )
        else:
            print(
                'ERROR:The "config.ini" is missing an inverter IP. The driver restarts in 60 seconds.'
            )
            sleep(60)
            sys.exit()
    else:
        print(
            'ERROR:The "'
            + config_file
            + '" is not found. Did you copy or rename the "config.sample.ini" to "config.ini"? The driver restarts in 60 seconds.'
        )
        sleep(60)
        sys.exit()

except Exception:
    exception_type, exception_object, exception_traceback = sys.exc_info()
    file = exception_traceback.tb_frame.f_code.co_filename
    line = exception_traceback.tb_lineno
    print(
        f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}"
    )
    print("ERROR:The driver restarts in 60 seconds.")
    sleep(60)
    sys.exit()


# Get logging level from config.ini
# ERROR = shows errors only
# WARNING = shows ERROR and warnings
# INFO = shows WARNING and running functions
# DEBUG = shows INFO and data/values
if "DEFAULT" in config and "logging" in config["DEFAULT"]:
    if config["DEFAULT"]["logging"] == "DEBUG":
        logging.basicConfig(level=logging.DEBUG)
    elif config["DEFAULT"]["logging"] == "INFO":
        logging.basicConfig(level=logging.INFO)
    elif config["DEFAULT"]["logging"] == "ERROR":
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.WARNING)

# check device type
if "DEFAULT" in config and "device_type" in config["DEFAULT"]:
  device_type = config["DEFAULT"]["device_type"]
else:
    device_type = "Fronius TS65A-3"
    logging.debug(
        'using default device_type' + device_type
    )

# check custom name
if "DEFAULT" in config and "device_name" in config["DEFAULT"]:
  device_name = config["DEFAULT"]["device_name"]
else:
    device_name = "Fronius Smart Meter"
    logging.debug(
        'using default device_name' + device_name
    )
    

# get polling_frequency
if "DEFAULT" in config and "polling_frequency" in config["DEFAULT"]:
  polling_frequency = int(config["DEFAULT"]["polling_frequency"])
else:
    polling_frequency = 200
    logging.debug(
        'using default polling_frequency' + polling_frequency
    )

# get instance id
if "DEFAULT" in config and "device_instance" in config["DEFAULT"]:
  device_instance = int(config["DEFAULT"]["device_instance"])
else:
    device_instance = 33
    logging.debug(
        'using default device_instance' + device_instance
    )


path_UpdateIndex = '/UpdateIndex'


class DbusFroniusSmartMeterService:
  def __init__(self, servicename, deviceinstance, paths, productname, customname, inverterip, pollingfrequency):
    self._dbusservice = VeDbusService(servicename)
    self._paths = paths
    self._inverterip = inverterip

    logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

    # Create the management objects, as specified in the ccgx dbus-api document
    self._dbusservice.add_path('/Mgmt/ProcessName', __file__)
    self._dbusservice.add_path('/Mgmt/ProcessVersion', 'Unkown version, and running on Python ' + platform.python_version())
    self._dbusservice.add_path('/Mgmt/Connection', customname + " service")

    # Create the mandatory objects
    self._dbusservice.add_path('/DeviceInstance', deviceinstance)
    self._dbusservice.add_path('/ProductId', 16) # value used in ac_sensor_bridge.cpp of dbus-cgwacs
    self._dbusservice.add_path('/ProductName', productname)
    self._dbusservice.add_path("/CustomName", customname)
    self._dbusservice.add_path('/FirmwareVersion', 0.1)
    self._dbusservice.add_path('/HardwareVersion', 0)
    self._dbusservice.add_path('/Connected', 1)

    for path, settings in self._paths.items():
      self._dbusservice.add_path(
        path, settings['initial'], writeable=True, onchangecallback=self._handlechangedvalue)

    gobject.timeout_add(pollingfrequency, self._update) # pause 200ms before the next request

  def _update(self):
    try:
      meter_url = "http://" + self._inverterip + "/solar_api/v1/GetMeterRealtimeData.cgi?"\
                  "Scope=Device&DeviceId=0&DataCollection=MeterRealtimeData"
      meter_r = requests.get(url=meter_url) # request data from the Fronius PV inverter
      meter_data = meter_r.json() # convert JSON data
      meter_consumption = meter_data['Body']['Data']['PowerReal_P_Sum']
      meter_model = meter_data['Body']['Data']['Details']['Model']
      if meter_model == 'Smart Meter 63A-1':  # set values for single phase meter
        meter_data['Body']['Data']['Voltage_AC_Phase_2'] = 0
        meter_data['Body']['Data']['Voltage_AC_Phase_3'] = 0
        meter_data['Body']['Data']['Current_AC_Phase_2'] = 0
        meter_data['Body']['Data']['Current_AC_Phase_3'] = 0
        meter_data['Body']['Data']['PowerReal_P_Phase_2'] = 0
        meter_data['Body']['Data']['PowerReal_P_Phase_3'] = 0
      self._dbusservice['/Ac/Power'] = meter_consumption # positive: consumption, negative: feed into grid
      self._dbusservice['/Ac/L1/Voltage'] = meter_data['Body']['Data']['Voltage_AC_Phase_1']
      self._dbusservice['/Ac/L2/Voltage'] = meter_data['Body']['Data']['Voltage_AC_Phase_2']
      self._dbusservice['/Ac/L3/Voltage'] = meter_data['Body']['Data']['Voltage_AC_Phase_3']
      self._dbusservice['/Ac/L1/Current'] = meter_data['Body']['Data']['Current_AC_Phase_1']
      self._dbusservice['/Ac/L2/Current'] = meter_data['Body']['Data']['Current_AC_Phase_2']
      self._dbusservice['/Ac/L3/Current'] = meter_data['Body']['Data']['Current_AC_Phase_3']
      self._dbusservice['/Ac/L1/Power'] = meter_data['Body']['Data']['PowerReal_P_Phase_1']
      self._dbusservice['/Ac/L2/Power'] = meter_data['Body']['Data']['PowerReal_P_Phase_2']
      self._dbusservice['/Ac/L3/Power'] = meter_data['Body']['Data']['PowerReal_P_Phase_3']
      self._dbusservice['/Ac/Energy/Forward'] = float(meter_data['Body']['Data']['EnergyReal_WAC_Sum_Consumed'])/1000
      self._dbusservice['/Ac/Energy/Reverse'] = float(meter_data['Body']['Data']['EnergyReal_WAC_Sum_Produced'])/1000
      logging.info("House Consumption: {:.0f}".format(meter_consumption))
    except:
      logging.warning("WARNING: Could not read from Fronius PV inverter")
      self._dbusservice['/Ac/Power'] = 0  # TODO: any better idea to signal an issue?
    # increment UpdateIndex - to show that new data is available
    index = self._dbusservice[path_UpdateIndex] + 1  # increment index
    if index > 255:   # maximum value of the index
      index = 0       # overflow from 255 to 0
    self._dbusservice[path_UpdateIndex] = index
    return True

  def _handlechangedvalue(self, path, value):
    logging.debug("someone else updated %s to %s" % (path, value))
    return True # accept the change

def main():
  logging.basicConfig(level=logging.DEBUG) # use .INFO for less logging
  thread.daemon = True # allow the program to quit

  from dbus.mainloop.glib import DBusGMainLoop
  # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
  DBusGMainLoop(set_as_default=True)

  pvac_output = DbusFroniusSmartMeterService(
    servicename='com.victronenergy.grid.fronius_smart_meter',
    deviceinstance=device_instance,
    paths={
      '/Ac/Power': {'initial': 0},
      '/Ac/L1/Voltage': {'initial': 0},
      '/Ac/L2/Voltage': {'initial': 0},
      '/Ac/L3/Voltage': {'initial': 0},
      '/Ac/L1/Current': {'initial': 0},
      '/Ac/L2/Current': {'initial': 0},
      '/Ac/L3/Current': {'initial': 0},
      '/Ac/L1/Power': {'initial': 0},
      '/Ac/L2/Power': {'initial': 0},
      '/Ac/L3/Power': {'initial': 0},
      '/Ac/Energy/Forward': {'initial': 0}, # energy bought from the grid
      '/Ac/Energy/Reverse': {'initial': 0}, # energy sold to the grid
      path_UpdateIndex: {'initial': 0},
    },
    productname=device_type,
    customname=device_name,
    inverterip=inverter_ip,
    pollingfrequency=polling_frequency
  )

  logging.info('Connected to dbus, and switching over to gobject.MainLoop() (= event based)')
  mainloop = gobject.MainLoop()
  mainloop.run()

if __name__ == "__main__":
  main()
