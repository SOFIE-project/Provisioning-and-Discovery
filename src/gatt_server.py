"""
BLE GATT description

GATT services share the same high-level D-Bus. Support for D-Bus Object
Manager is mandatory for external services to allow seamless
GATT declarations (Service and Characteristic) discovery. GATT Manager allows
applications to register GATT services and profiles.

Applications implementing services must register the services
using GattManager1 registration method and must implement the methods and
properties defined in GattService1 interface.
            
"""

import sys
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import array
from random import randint

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

mainloop = None

DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"


class Service(dbus.service.Object):
    """ Service Class for GATT Server """

    PATH_BASE = "/src/service"

    def __init__(self, bus, index, uuid, primary):
        """
            :param string UUID: 128-bit service UUID.
            :param boolean Primary: Indicates whether or not this GATT service is a primary service. If false, the service is secondary.
            :param array{object} Characteristics: Array of object paths representing the characteristics of this service. This property is set only when the characteristic discovery has been completed.
        """
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        """ This method gets called when the service daemon request for the Service propertises."""
        return {
            GATT_SERVICE_IFACE: {
                "UUID": self.uuid,
                "Primary": self.primary,
                "Characteristics": dbus.Array(
                    self.get_characteristic_paths(), signature="o"
                ),
            }
        }

    def get_path(self):
        """ This method gets called to get the Object path of the dbus used for the BLE service. """
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        """ This method gets called to add characteristics to the list that is later added to the GATT service."""
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        """ This method gets called when the service request for Object paths of the characteristics. """
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        """ This method gets called when the service request for all of the GATT Service characteristics. """
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        """ This method gets called when the daemon request for all of the properties of GATT Service. """
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    """ Characteristics for the GATT Service """

    def __init__(self, bus, index, uuid, flags, service):
        """
            :param string UUID: 128-bit Characteristic UUID.
            :param object Service: Object path of the GATT service the characteristc belongs to.
            :param array{byte} Value: The cached value of the characteristic. This property gets updated only after a successful read request.
            :param array{string} Flags: Defines how the characteristic value can be used.Allowed values:
                "broadcast"
                "read"
                "write-without-response"
                "write"
                "notify"
            :param array{object} Descriptors: Array of object paths representing the descriptors of this service.
            """
        self.path = service.path + "/char" + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        """ This method gets called when the service daemon request for the characteristic propertises."""
        return {
            GATT_CHRC_IFACE: {
                "Service": self.service.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
                "Descriptors": dbus.Array(self.get_descriptor_paths(), signature="o"),
            }
        }

    def get_path(self):
        """ This method gets called to get the Object path of the interface dbus used for the characteristic. """
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        """This method gets called to add descriptor to the list that is then added to the characteristics."""
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        """This method gets called to get the descriptor path."""
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        """This method gets called to get the descriptor."""
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        """ This method gets called when the service request for all of the Characteristic properties."""
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        """ Issues a request to read the value of the characteristic and returns the value if the operation was successful."""
        print("Default ReadValue called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="aya{sv}")
    def WriteValue(self, value, options):
        """ Issues a request to write the value of the characteristic."""
        print("Default WriteValue called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        """ Starts a notification session from this characteristic if it supports value notifications or indications. """
        print("Default StartNotify called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        """ This method will cancel any previous StartNotify transaction."""
        print("Default StopNotify called, returning error")
        raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE, signature="sa{sv}as")
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


# Callback for Sucess application
def application_callback():
    """ This method gets called when the a service object is registered succussfully and sent over the GATT."""
    print("GATT application registered")


# Callback for Error application
def app_error_callback(error):
    """ This method gets called when the a service object is not registered and error message is displayed to the client."""
    print("Failed to register application: " + str(error))
    mainloop.quit()
