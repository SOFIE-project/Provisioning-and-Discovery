## Importing the component to your project

To import the component

```
cd Discovery-and-Provisioning
pip3 install
python3
import sofie_pd_component
```

**For Eddystone URL**

To start eddystone URL
```
eddystone_url.startUrlAdvertise(URL)
```

To stop eddystone URL
```
eddystone_url.stopUrlAdvertise()
```

**For Eddystone UUID**

To start eddystone UUID
```
eddystone_uuid.startUuidAdvertise(INTERFACE, TXPOWER, NAMESPACE, INSTANCEID)
```

To stop eddystone UUID
```
eddystone_uuid.stopUuidAdvertise(INTERFACE)
```

INTERFACE: Inteerface of the BLE module, can be check using *hciconfig*

TXPOWER: 2 byte transmit power of the BLE module

NAMESPACE: 10 byte unique ID to signify your company or organization 

INSTANCEID: 6 byte instance ID to identify the device.

**For BLE Advertisement**

```
gatt_application.BLE(NAME, DEFAULT_SERVICEUUID, URI)
```
NAME: Device Name

DEFAULT_SERVICEUUID: 0x180A (Read Only)

URI: URL to advertise as 0x24 (Service Data)

For more attributes: https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile/
