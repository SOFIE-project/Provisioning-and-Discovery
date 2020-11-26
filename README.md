# SOFIE Discovery and Provisiong component

**Table of contents:**

- [Description](#description)
    - [Architecture Overview](#architecture-overview)
    - [Main Concepts](#main-concepts)
    - [Relation with SOFIE](#relation-with-sofie)
    - [Key Technologies](#key-technologies)

- [Usage](#usage)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Execution](#execution)


## Description

The goal of SOFIE provisioning and discovery component is to provision the IoT device to a working state with the platform and to enable the discovery of new IoT resources along with their related metadata. Using this functionality, it is possible to decentralise the process of making new resources available to systems utilising the SOFIE framework. This component works along with SOFIE semantic representation component to provide meta-data for the IoT devices. 

Examples of how P&D component can be utilised include:

- [IoT Beacon discovery and provisioning](/doc/example-game.md) example discover new IoT devices usable for expanding the game world and automatically add them to the resource database, the provisioning interface updates the IoT device with required configurations to work with the platform.  

- [SMOG Locker](/doc/import_component.md) example uses discovery interface to advertise specific Unique ID to discover locker nearby.


### Architecture Overview

![High Level Architecture](/imgs/archi.png)

Figure 1: High Level Architecture of the Component

The first functionality of the component is to provision the devices using the meta-data.  The process of provisioning involves enrolling a device into the system and getting each device configured to provide a required service and send data to the right place on the network. The first part is establishing the initial connection between the device and the IoT solution by registering the device. In the component, Provisioning interface goes through the meta-data and checks against the requirement before provisioning the device to the database. This also acts as the filter for either accepting or rejecting the newly discovered IoT resource. After enrolling the device, the interface provides for the configuration related information for the device to bring it to a working state, and also includes defining the desired state of the device. 

The second functionality of the component is discovery of the new IoT resources. This component interface provides operations to perform a scan and discover open IoT devices nearby. It also provides an interface to discover devices published on the local (WLAN, etc.) network. The discovery interface lists newly discovered devices along with their related meta-data before enrolling them the system.

### Main Concepts

The design of the architecture is driven by the discvoery scenario of the SOFIE Gaming Pilot.

![Internals](/imgs/discovery_internal.png)

Figure 2: Internals of the Component

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

### Relation with SOFIE

The discovery and provisiong component works with semantic representation file, it may be used by other SOFIE components and applications as necessary.

Only Mobile gaming pilot utilise the P&D component for discovering and managing the new IoT devices to be used inside the game world. 

### Key Technologies

The software modules are implemented in **Python 3** Currently the component supports the Eddystone and custom GATT application over **Bluetooth Low Energy** (BLE) and **DNS-Service Discovery**.

***

## Usage

The `/src` directory contains the code implementing the python application.

The `/_webthing.servie`is a template file for DNS-SD custom service.

The `/src/sofie_pd_component/dns/controller/static/semantic.json` is a template file for semantic representation


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

### Execution

Before starting DNS-SD, create a DNS service file and copy to `/etc/avahi/service/`

Before starting the server, create a semantic representaion file and copy to `src/python_app/controller/static`

To start the Command Line Interface
```
cd Discovery-and-Provisioning/src
python3 cli.py
```
Change the URL in the cli file to point the Semantic Representation file.

After starting the interface, there are limited options to perform

**'dns'**: Start the DNS-SD

**'ble'**: Start the BLE with custom advertising and UART service.

**'eddystone'** : Start or Stop Eddystone URL

**'help'**: To get the commands

**'exit'**: Exit the interface

### Import the component

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

***
## License

This component is licensed under the Apache License 2.0.
