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

- [Testing](#testing)
    - TODO

## Description

SOFIE discovery and provisioning component is to enable the discovery of new IoT resources and their related metadata. Using the component, it is possible to decentralise the process of making new resources available to systems utilising the SOFIE framework and to automate the negotiations for the terms of use and the compensation for the use of these resources. 


### Architecture Overview

![High Level Architecture](/imgs/archi.png)

**DNS Service Discovery with multicast**

DNS service discovery (DNS-SD) allows clients to discover a named list of service instances, given a service type, and to resolve those services to hostnames using standard DNS queries. It discovers devices and services on a local area network using IP protocols, without requiring the user to configure them manually. DNS service discovery requests can also be sent over a multicast link, and it can be combined with multicast-DNS (mDNS) to yield zero-configuration DNS-SD.

### Relation with SOFIE

The discovery and provisiong component works with semantic representation file, it may be used by other SOFIE components and applications as necessary.

### Main Concepts

The design of the architecture is driven by the discvoery scenario of the SOFIE Gaming Pilot. 


### Key Technologies

The software modules are implemented in **Python** and **Java**

***

## Usage

The `/android_app` directory contains the code implementing the android application.

The `/python_app` directory contains the code implementing the python application.

The `/_webthing.servie`is a template file for DNS-SD custom service.

The `/python_app/controller/static/semantic.json` is a template fiel for semantic representation


### Prerequisites

Software modules: **Python 2.7**.

Android: **API level > 21**.

Hardware module: Raspberry Pi 


### Installation

```bash
#To install DNS-SD 
sudo apt-get install avahi-daemon 

# Install python app project dependencies
cd python_app
python setup.py install 
```

### Execution

Before starting DNS-SD, create a DNS service file and copy to `/etc/avahi/service/`

Before starting the server, create a semantic representaion file and copy to `/python_app/controller/static`

To start the Flask Server and DNS-Service
```bash
cd python_app
python __init__.py
```


***
## License

This component is licensed under the Apache License 2.0.
