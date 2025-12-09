# CS303-honeypot

## The implementation steps for all of this are as follows:

First of all what you need to do is either download Oracle VM or download FusionWareVM

Next what you'll need to implement is create 3 of these instances of vms so you'll have an attacker vm, server vm and victim vm.

Next on the server vm you'll want to clone this repo and do python3 server.py and connect to the website of http://<IP>:8080/website

From here you'll be able to edit the whitelisted IP and MAC address in the true login.txt and make sure the victim has the ability to log into the website. While this is going on you can run an arp spoofing program that connects to the victim IP and MAC and reroute their packets through the attacker. 

And thats about it. 