## Step 1 - Install the P&D Component

Clone the repository and Install python app project dependencies.

```
git clone https://github.com/SOFIE-project/Discovery-and-Provisioning.git
cd Discovery-and-Provisioning
python3 setup.py install 
```
## Step 2 - Create semantic representaion file

Before starting the component, semantic file should be updated to include details of IoT device meta-data. 

[Semantic template file](src/sofie_pd_component/dns/controller/static/semantic.json)

## Step 3 - Deploy semantic file

**For DNS-SD**

Copy Semantic file to `src/python_app/controller/static`

**For BLE and Eddystone**

Upload the file to hosting server e.g. Amazon Web Server.

Change the URL in the cli file to point the semantic representation file link.

## Step 4 - Start the Component CLI

To start the Command Line Interface

```
cd Discovery-and-Provisioning/src
python3 cli.py
```

## Step 5 - Excute the Protocols

**For DNS-SD**

Before starting DNS-SD, create a DNS service file and copy to `/etc/avahi/service/`

[DNS template file](_webthing.service)

After starting the interface, type *dns* to start the DNS-SD

Use the Android Application and select DNS option to discover and provison this IoT device.

<img src="/imgs/app1.jpg" width="162" hight="351">  <img src="/imgs/app2.jpg" width="162" hight="351"> <img src="/imgs/app3.jpg" width="162" hight="351">


**For BLE GATT Application**

After starting the interface, type *ble* to start the custom GATT application over Bluetooth Low Energy

Use the Android Application and select BLE option to discover and provison this IoT device.

<img src="/imgs/app1.jpg" width="162" hight="351"> <img src="/imgs/app4.jpg" width="162" hight="351">

## Step 6 - Configration of IoT Device

After discoverying the device, Android application check the resource database and updates the device with the Eddystone UUID to work with SOFIE Game pilot.
