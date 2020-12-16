# SOFIE Provisiong and Discovery component

**Table of contents:**

- [Description](#description)
    - [Architecture Overview](#architecture-overview)
    - [Relation with SOFIE](#relation-with-sofie)
    - [Key Technologies](#key-technologies)
- [Usage](#usage)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configration](#configration)
    - [Execution](#execution)
- [Testing](#testing)
    - [Running the Test](#Running-the-Tests)
    - [Evaluating Results](#Evaluating-Results)
- [Open Issues](#Open-Issues)
- [Future Work](#future-work)
- [Release Notes](#release-note)
- [Contact Info](#Contact)
- [License](#License)


## Description

The goal of SOFIE provisioning and discovery component is 1) to provision the IoT device to a working state with the platform and 2) to enable the discovery of new IoT resources along with their related metadata. Using this functionality, it is possible to decentralise the process of making new resources available to systems utilising the SOFIE framework. This component works along with SOFIE semantic representation component to provide meta-data for the IoT devices. 

Examples of how P&D component can be utilised include:

- [IoT Beacon discovery and provisioning](/doc/example-game.md) example discovers new IoT devices usable for expanding the game world and automatically adds them to the resource database, while the provisioning interface updates the IoT device with required configurations to work with the platform.  

- [SMAUG Locker](/doc/import_component.md) example uses discovery interface to advertise specific Unique ID to discover locker nearby.


### Architecture Overview

![High Level Architecture](/imgs/archi.png)

Figure 1: High Level Architecture of the Component

The first functionality of the component is to provision the devices using meta-data provided by the SOFIE semantic representation file. The process of provisioning involves enrolling a device into the system and getting each device configured to provide a required service and send data to the right place on the network. In the component, the Provisioning interface goes through the meta-data and checks against the requirement before provisioning the device to the database. This also acts as the filter for either accepting or rejecting the newly discovered IoT resource. After enrolling the device, the provisioning interface provides the configuration for the device to bring it to a working state with the deployed platform.

The second functionality of the component is the discovery of the new IoT resources. The Bluetooth discovery interface provides operations to perform a BLE scan and discover open IoT devices nearby using Bluetooth. It also provides a LAN discovery interface to discover devices published on the local (WLAN, etc.) network. The interfaces list newly discovered devices along with their related meta-data before enrolling them in the system.

![Internals](/imgs/usage.png)
Figure 2: Usage of the Component

As shown in Figure 2, the user [configres](#configration) the semantic file for the IoT device (Raspberry Pi for prototype) and host it on the server. The user starts the SOFIE Provisioning and Discovery component on the device. After starting the component, the user installs the mobile client [application](/android_app/README.md). User is shown multiple options to choose from that relates to the discovery protocols. The mobile client scans for the nearby IoT devices based on the protocol selected. In order to filter the newly discovered IoT devices, we use custom advertisement packages with URI link to the semantic representation file. After discovering, the mobile client downloads the semantics file that contains the meta-data for the IoT device and goes through the file. The metadata from the file is checked against the requirement provided by the user before provisioning the device to the database. If the devices pass the minimum requirement, the connection between the mobile and the IoT device is established and the device is configurated to work with the platform.

The design of the architecture is driven by the discvoery scenario of the SOFIE Gaming Pilot.

![Internals](/imgs/discovery_internal.png)

Figure 3: Internals of the Component

As shown in Figure 3, the component uses modified Bluetooth with a custom Gatt server and DNS for discovering the IoT device. The mobile client downloads the semantic representation file of the IoT device and checks for provisioning requirements before saving it to the database. The mobile application also sends configuration to the IoT device to work along with the platform.


### Relation with SOFIE

The discovery and provisiong component works with semantic representation file, it may be used by other SOFIE components and applications as necessary.

Only Mobile gaming pilot utilise the P&D component for discovering and managing the new IoT devices to be used inside the game world. 

### Key Technologies

The software modules are implemented in **Python 3** Currently the component supports the Eddystone and custom GATT application over **Bluetooth Low Energy** (BLE) and **DNS-Service Discovery**. The details of the technologies used are as following:

**Bluetooth Low Energy (BLE) with Custom Advertisement and Services**

BLE is a form of wireless communication designed especially for short-range communication. In this component, a BLE device with custom Services and advertising packet is used to Discover and Provision the IoT beacons. Custom advertising packet is used to quickly discover the BLE devices in proximity and custom services will be used to configure them to be used as a beacon.  

The Bluetooth GATT (Generic Attribute Profile) is the foundation for the design of any BLE system and defines the way an application (any central device) interacts with the end-device (the peripheral device). GATT is used exclusively after a connection has been established between the two devices. The underlying framework for GATT is the Attribute Protocol (ATT). The Bluetooth SIG defines quite a few standard Profiles, Services, and Characteristics for the GATT.

ATT defines how a BLE device exposes its data to a client and how that data is structured.
There are two roles within the ATT:

*Server*
This is the device that exposes the data it controls or contains. In this Scenario, Raspberry PI is the Server device that accepts incoming commands from a peer device and sends responses, notifications, and indications.

*Client*
This is the device that interfaces with the server with the purpose of reading the exposed data and/or controlling the server’s behavior. In this example, a mobile device that connects to the Raspberry PI sends commands and requests to it and accepts incoming notifications and indications.

When a BLE device is advertising it will periodically transmit packets contains information such as device name, Bluetooth address of the sender, etc. The advertising data fields can be used to configure a custom advertising packet. The advertising packet in this example already contains your custom name, service UUIDs and custom data i.e. URL. It also contains flags defining some of the advertising options. It is important to know that an advertising packet can consist of no more than 31 bytes.

**Eddystone URL**

Eddystone is an open beacon format developed by Google and designed with transparency and robustness in mind. Eddystone can be detected by both Android and iOS devices. Several different types of the payload can be included in the frame format. The Eddystone-URL frame broadcasts a URL using a compressed encoding format in order to fit more within the limited advertisement packet.

Once decoded, the URL can be used by any client with access to the internet. In this example, an Eddystone-URL is used to broadcast the URL of the Semantic Representation file, then any client that received this packet could download the Semantics file of the device.

**DNS Service Discovery with multicast**

DNS service discovery (DNS-SD) allows clients to discover a named list of service instances, given a service type, and to resolve those services to hostnames using standard DNS queries. It discovers devices and services on a local area network using IP protocols, without requiring the user to configure them manually. DNS service discovery requests can also be sent over a multicast link, and it can be combined with multicast-DNS (mDNS) to yield zero-configuration DNS-SD.

***

## Usage

[Src](/src) directory contains the code implementing the python application.

[Service file](/_webthing.servie)is a template file for DNS-SD custom service.

[Semantics File](/src/sofie_pd_component/dns/controller/static/semantic.json) is a template file for semantic representation that contains the metadata of the IoT device.


### Prerequisites

Software modules: **Python 3.6**.

Hardware module: **Raspberry Pi with BLE module**


### Installation

Install Avahi daemon 
```
sudo apt-get install avahi-daemon
```

Install python app project dependencies
```
python3 setup.py install 
```

### Configration

Before starting, 

Create a DNS [Service file](/_webthing.service) and copy it to Avahi directory.

```
cd Discovery-and-Provisioning
cp [Link to File] /etc/avahi/service/
```

**For DNS**
Create a [semantic representaion file](/src/sofie_pd_component/dns/controller/static/semantic.json) and copy it to internal directory.

```
cp [Link to File] src/python_app/controller/static
```

**For BLE**
Upload the semantic file to a server and change the URL in the cli [file](/src/cli.py)

### Execution

Start the Command Line Interface and use following commands
```
cd src
python3 cli.py
```
After starting the interface, the following options are availiable to perform

**'dns'**: Start the DNS-SD

**'ble'**: Start the BLE with custom advertising and UART service.

**'eddystone'** : Start or Stop Eddystone URL

**'help'**: To get the commands

**'exit'**: Exit the interface

### Import the component

To import the component

```
cd Discovery-and-Provisioning
pip3 install
python3
import DP_component
```
For more details [Link](/doc/import_component.md)

### Android Application

Android application is used for the provisoning part of the component

Please check [Android Application](/android_app/README.md)

## Testing

The `tests/` directory contains the script to test the software modules of the component. The test check that all the discovery protocols works.

### Running the Tests

To test the component, use CLI 
```
cd Discovery-and-Provisioning
pip3 install
python3 tests/test_run.py
```

### Evaluating Results

The user can evaluate the status of the component by running the tests. If all of them are passed then the component should run as intended on the Raspberry Pi.

## Open Issues

There are no major bugs or missing functionalities.

## Future Work

The component satisfies SOFIE project requirements and there is no plan to extend functionalities.

## Release  Note

### 2020-12-02
#### Added
- Mobile client added for provisioning of devices.
- Testing and validation of the component.
- Updated documentation.

### 2020-11-17
#### Added
- Updated documentation
- Example of importing the [component](/doc/import_component.md)

## Contact Info

**Contact** Ahsan Manzoor: ahsan.manzoor@rovio.com

## License

This component is licensed under the Apache License 2.0.
