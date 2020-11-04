"""
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed
# with this work for additional information regarding copyright
# ownership.  The ASF licenses this file to you under the Apache
# License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License.  You may obtain a copy of the
# License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

"""

"""
BLE Application Description

This is the custom BLE application for the discovery and provisioning component. It
creates a custom Service and Advertising packet for the component.

"""

import sys
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from .advertisement import Advertisement
from .advertisement import advertisement_callback, adv_error_callback
from .gatt_server import Service, Characteristic
from .gatt_server import application_callback, app_error_callback

SERVICE_NAME = "org.bluez"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
UART_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
UART_RX_CHARACTERISTIC_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UART_TX_CHARACTERISTIC_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
EDDYSTONE_UUID = None
mainloop = None

# Transmitter for the BLE
class TxCharacteristic(Characteristic):
    """ Transmitter characteristic for the UART service"""

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index, UART_TX_CHARACTERISTIC_UUID, ["notify"], service
        )
        self.notifying = False
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.on_console_input)

    def on_console_input(self, fd, condition):
        """ This method is used to get the input from the user to be send over BLE transmitter."""
        s = fd.readline()
        if s.isspace():
            pass
        else:
            self.send_tx(s)
        return True

    def send_tx(self, s):
        """ This method is used to send the message to the client."""
        if not self.notifying:
            return
        value = []
        for c in s:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

    def StartNotify(self):
        """ Starts a notification session from this characteristic if it supports value notifications or indications. """
        if self.notifying:
            return
        self.notifying = True

    def StopNotify(self):
        """ This method will cancel any previous StartNotify transaction. """
        if not self.notifying:
            return
        self.notifying = False


# Receiver for the BLE
class RxCharacteristic(Characteristic):
    """ Receiver characteristic for the UART service"""

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index, UART_RX_CHARACTERISTIC_UUID, ["write-without-response"], service
        )

    def WriteValue(self, value, options):
        """Issues a request to write the value of the characteristic."""
        print("remoting: {}".format(bytearray(value).decode()))
        global EDDYSTONE_UUID
        EDDYSTONE_UUID = bytearray(value).decode()
        mainloop.quit()


# Custom UART Service
class UartService(Service):
    """ Custom Service for the GATT """

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, UART_SERVICE_UUID, True)
        self.add_characteristic(TxCharacteristic(bus, 0, self))
        self.add_characteristic(RxCharacteristic(bus, 1, self))


class Application(dbus.service.Object):
    """ Application class for the BLE device """

    def __init__(self, bus):
        self.path = "/"
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        return response


class CustomApplication(Application):
    """ BLE custom application with UART service """

    def __init__(self, bus):
        Application.__init__(self, bus)
        self.add_service(UartService(bus, 0))


# BLE Custom Advertisement with URL
class CustomAdvertisement(Advertisement):
    """ BLE Custom Advertisement with URL """

    def __init__(self, bus, index, name, uuid, url):
        Advertisement.__init__(self, bus, index, "peripheral")
        self.add_service_uuid(uuid)
        self.include_tx_power = True
        self.add_local_name(name)
        self.add_data(0x24, self.string_hex(url))


# Finding adapter for bluetooth
def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(SERVICE_NAME, "/"), DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()
    for o, props in objects.items():
        if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props:
            return o
        print("Skip adapter:", o)
    return None


# Main Class
def BLE(name, uuid, url):
    global mainloop
    # Communicate with system services
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    # BLE Adapter
    adapter = find_adapter(bus)
    if not adapter:
        print("Interface not found")
        return
    # Interface for Services and advertisement
    service_manager = dbus.Interface(
        bus.get_object(SERVICE_NAME, adapter), GATT_MANAGER_IFACE
    )
    ad_manager = dbus.Interface(
        bus.get_object(SERVICE_NAME, adapter), LE_ADVERTISING_MANAGER_IFACE
    )
    # Custom BLE service and advertisement
    application = CustomApplication(bus)
    advertisement = CustomAdvertisement(bus, 0, name, uuid, url)

    mainloop = GLib.MainLoop()

    # >Resgister the BLE
    service_manager.RegisterApplication(
        application.get_path(),
        {},
        reply_handler=application_callback,
        error_handler=app_error_callback,
    )
    ad_manager.RegisterAdvertisement(
        advertisement.get_path(),
        {},
        reply_handler=advertisement_callback,
        error_handler=adv_error_callback,
    )

    try:
        mainloop.run()
        advertisement.Release()
        return EDDYSTONE_UUID
    except KeyboardInterrupt:
        advertisement.Release()
