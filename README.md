# WiFi_Capture 

Goals:
Scan WiFi channels, capture WiFi signals, tag them, filter them, and store them into a POSTGRE SQL database in a real time manner.

Description:
This code runs for managing three Humming Boards. Each Humming Board runs Kismet Server for WiFi data capture.  Kismet server allows the Wi-Fi receivers to operate in monitor mode and allows for manual control of which channel to scan and for how long as well as which signal type to collect (801.11 / 802.15).
The WiFi capture class performs several functions upon initialization.  First verification is performed to make sure that all three Humming Boards are up and running.  The second check is to verify that Kismet server is running. The third check is to verify that the NTP client service is running. 
Once activated each receiver channel sends the captured data to the WIFI Capture CLASS which runs on the Signal Processing Unit (SPU).  The SPU sends all command and control messages to the receiver channels so as to when to start, stop, channel, and signal type to collect.  All three receiver channels scan simultaneously to scan every channel and detect all possible Wi-Fi emitters.  In addition the WiFi capture class must also filter out any emitters that are not access points.
It is important that the receivers be time coherent so as to sample each channel at the same time for data coherency purposes.   Timing is done by using Network Time Protocol (NTP) server running on the SPU. Each receiver channel subscribes to this service to provide accurate time stamps for all data collection.  Connectivity from the receiver channels to the SPU is via 1 Gbps Ethernet via CATt6.  Power for each SBC will be via a power distribution unit.Data from the WiFi capture Class is sent to a database in real time for further process.

