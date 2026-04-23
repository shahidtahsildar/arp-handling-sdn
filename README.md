# arp-handling-sdn
# ARP Handling in SDN Networks

## Problem Statement
Implement ARP request and reply handling using an SDN controller (POX).
The controller intercepts ARP packets, generates ARP responses, enables
host discovery, and validates communication between hosts.

## Tools Used
- Mininet (network emulation)
- POX Controller (OpenFlow)
- Ubuntu 22.04 (VirtualBox VM)

## Setup & Execution Steps
1. Install Mininet: sudo apt install mininet -y
2. Clone POX: git clone https://github.com/noxrepo/pox
3. Place arp_handler.py in pox/ext/
4. Start POX: python3 pox.py arp_handler
5. Start Mininet: sudo mn --controller=remote --topo=single,3 --mac

## Expected Output
- All hosts discover each other via ARP
- pingall shows 0% packet loss
- Flow table shows installed rules
- ARP table populated on each host

## Test Scenarios
1. Normal: pingall shows full connectivity (0% dropped)
2. Failure: link brought down, host unreachable, then restored

## Screenshots
<img width="793" height="314" alt="Screenshot from 2026-04-23 01-58-20" src="https://github.com/user-attachments/assets/82d26713-ef3a-42a5-a489-8e9ed0a4b914" />

<img width="715" height="95" alt="Screenshot from 2026-04-23 01-58-40" src="https://github.com/user-attachments/assets/f4ad7319-3b41-4814-86a6-59f18a7d6dec" />

<img width="1212" height="475" alt="Screenshot from 2026-04-23 01-59-51" src="https://github.com/user-attachments/assets/c0904653-f9fb-47d0-a95f-1db0c3b0cff9" />

<img width="1092" height="76" alt="Screenshot from 2026-04-23 02-00-55" src="https://github.com/user-attachments/assets/2f15b0d3-f54c-42f8-b689-ca74aab96031" />

<img width="1093" height="277" alt="Screenshot from 2026-04-23 02-07-12" src="https://github.com/user-attachments/assets/b1bf4e97-6c26-4ff3-b915-0cda01ba2c63" />




## References
- https://github.com/noxrepo/pox
- http://mininet.org
