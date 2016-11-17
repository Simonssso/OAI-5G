OAI-5G
========================

OAI-5G is an integration of EmPOWER eNB Agent (developed by CREATE-NET) library with OpenAirInterface (developed by Eurecom). EmPOWER Agent (EMAge) provides an interface between OpenAirInterface (OAI) stack and SDN Controllers such as e.g. EmPOWER. This helps in exchange of statistics, measurements, configurations, and control the working of OAI stack by the SDN Controller.

EmPOWER eNB Agent (EMAge) is under the Apache License, Version 2.0.

OpenAirInterface is under OpenAirInterface Software Alliance license.
 * http://www.openairinterface.org/?page_id=101
 * http://www.openairinterface.org/?page_id=698

Currently supported messages between OAI-5G and SDN Controller:
 * Hello
 * UEs identifier request and reply messages
 * RRC measurements, request and reply messages
 * RRC measurements configuration request and reply messages

Pre-requisites
==============

 * Linux standard build suite (GCC, LD, AR, etc...)
 * Pthread library, necessary to handle multithreading
 * Protocol Buffers C++ (protoc) along with the C++ runtime (Version >= 3.0.0)
 * pkg-config, a helper tool used when compiling applications and libraries
 * Protobuf-c, Google protocol buffer implementation for C (Version >= 1.2.1)
 * Pre-requisites of OpenAirInterface5G
 * Agent and Protocol library from EmPOWER eNB Agent (EMAge)

Testbed
=======

This software has been developed and tested on Linux, Ubuntu 14.04 LTS with 3.19.8-031908-lowlatency and 4.8.0-040800-lowlatency kernel. Our tested consists of OAI eNB, EPC and HSS running on a single host. But, the process is similar for environment with OAI EPC and HSS on a different host than the OAI eNB.

Hardware:
 * Laptop with Intel® Core™ i7-5600U CPU @ 2.60GHz × 4
 * 16 GB RAM
 * USRP B210 (UHD driver version UHD_003.010.000.000-release)
 * Nexus 5 with sysmoUSIM-SJS1 SIM

Software:
 * Latest OAI eNB code from `develop` branch
 * Latest Openair-cn code from tag `v0.3.2` and develop branch
 * protoc (Version 3.1.0)
 * protobuf-c (Version 1.2.1)

Download & Install Instructions
===============================

Before downloading the code, please follow the instructions below:
 * Ubuntu 14.04 LTS (32-bit or 64-bit)
 * Kernel setup https://gitlab.eurecom.fr/oai/openairinterface5g/wikis/OpenAirKernelMainSetup
 * Disable C-states from BIOS (or from GRUB)
 * Disable CPU frequency scaling
 * Install low-latency kernel

OAI-5G requires protocol (libemproto) and agent (libemagent) library of EmPOWER eNB Agent to be installed before compiling.

Download and install protocol (libemproto) and agent (libemagent) library of EmPOWER eNB Agent:
```
git clone https://github.com/5g-empower/empower-enb-agent.git
cd empower-enb-agent/proto
make
sudo make install
cd ../agent
make
sudo make install
```
Create a configuration file by the name `agent.conf` and placed it in the `/etc/empower` directory. An example configuration file is provided in the folder `conf/empower` of EmPOWER eNB Agent repository.

Download and build OAI-5G:
```
git clone https://github.com/herlesupreeth/OAI-5G
```
**Rest of the instructions for building OAI-5G is similar to building OpenAirInterface5G, which can be found in the following link https://gitlab.eurecom.fr/oai/openairinterface5g/wikis/HowToConnectCOTSUEwithOAIeNB**

Once OAI-5G has been successfully compiled, you are good to go !!!

Running OAI-5G
==============

Modify the configuration file for EmPOWER eNB Agent `agent.conf` to specify the IP address and port number at which EmPOWER (or other SDN Controller) is running.

In order to run OAI-5G, follow the instructions mentioned in the section `Running eNB, EPC and HSS` in the following link https://gitlab.eurecom.fr/oai/openairinterface5g/wikis/HowToConnectCOTSUEwithOAIeNB.

The EmPOWER eNB agent can be enabled or disabled by setting or unsetting the `EMAGE_AGENT` flag in `CMakeLists.txt` file `empower-openairinterface/cmake_targets/CMakeLists.txt`.



Copyright 2016 Supreeth Herle (s.herle@create-net.org)

Licensed under the License terms and conditions for use, reproduction, and distribution of OPENAIR 5G software (the “License”); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.openairinterface.org/?page_id=101, http://www.openairinterface.org/?page_id=698.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and limitations under the License.
