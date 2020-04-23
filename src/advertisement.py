"""
BLE Advertising Description

Advertising packets are structured data which is broadcast on the BLE Advertising
channels and available for all devices in range.  Because of the limited space
available in BLE Advertising packets (32 bytes), each packet's contents must be
carefully controlled.

It constructs the correct Advertisement Data from the structured
data and configured the kernel to send the correct advertisement.

"""


from __future__ import print_function
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import binascii
import array

try:
    from gi.repository import GObject  # python3
except ImportError:
    import gobject as GObject  # python2

from random import randint

mainloop = None

LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"


class Advertisement(dbus.service.Object):
    """ Advertisement Class for BLE device """

    PATH_BASE = "/src/advertisement"

    def __init__(self, bus, index, advertising_type):
        """
        :param string Name: Name of the BLE device to shown when scanning.
        :param string Type: Determines the type of advertising packet requested. Possible values: "broadcast" or "peripheral"
        :param array{string} ServiceUUID: List of UUIDs to include in the "Service UUID" field of the Advertising Data.
        :param dict ManufacturerData: Manufactuer Data fields to include in the Advertising Data.
        :param dict ServiceData: Service Data elements to include. The keys are the UUID to associate with the data.
        :param bool IncludeTxPower: Includes the Tx Power in the advertising packet.
        """
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.local_name = None
        self.include_tx_power = None
        self.data = None
        dbus.service.Object.__init__(self, bus, self.path)

    # Get properties of BLE
    def get_properties(self):
        """ This method gets called when the service daemon request for the advertising propertises."""
        properties = dict()
        properties["Type"] = self.ad_type

        if self.service_uuids is not None:
            properties["ServiceUUIDs"] = dbus.Array(self.service_uuids, signature="s")
        if self.local_name is not None:
            properties["LocalName"] = dbus.String(self.local_name)
        if self.include_tx_power is not None:
            properties["IncludeTxPower"] = dbus.Boolean(self.include_tx_power)
        if self.data is not None:
            properties["Data"] = dbus.Dictionary(self.data, signature="yv")

        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        """ This method gets called to get the path of the interface dbus used for the BLE."""
        return dbus.ObjectPath(self.path)

    # Add Service for BLE device
    def add_service_uuid(self, uuid):
        """ This method gets called to add service uuids to the list that is added in the advertising packet."""
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    # Add name for BLE device
    def add_local_name(self, name):
        """ This method gets called to add custom name to the BLE device. """
        if not self.local_name:
            self.local_name = ""
        self.local_name = dbus.String(name)

    # Add custom data to BLE advertisement
    def add_data(self, ad_type, data):
        """This method gets called to add custom data to the advertising packet."""
        if not self.data:
            self.data = dbus.Dictionary({}, signature="yv")
        self.data[ad_type] = dbus.Array(data, signature="y")

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")

    # Get all properties of the BLE
    def GetAll(self, interface):
        """This method gets called when the service daemon request for all of the advertising properties."""
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        print("Returning props")
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature="", out_signature="yo")
    def Release(self):
        """ This method gets called when the service daemon removes the Advertisement. A client can use it to do cleanup tasks."""
        print("%s: Released!" % self.path)

    # String to Hexadecimal
    def string_hex(self, data):
        """ This method gets called to convert the string data into hex to be used in the advertising packet. """
        hex_data = binascii.b2a_hex(data.encode())
        hex_array = bytearray.fromhex(hex_data.decode("utf-8"))
        hex_array.insert(0, 0x16)
        return hex_array


# Callback for Success Advertisement
def advertisement_callback():
    """ This method gets called when the an advertisement object is registered succussfully and sent over the BLE Advertising channel. """
    print("Advertisement registered")


# Callback for Error Advertisement
def adv_error_callback(error):
    """This method gets called when the an advertisement object is not registered and error message is displayed to the client. """
    print("Failed to register advertisement: " + str(error))
    mainloop.quit()
