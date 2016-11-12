#!/bin/bash
## A script to automatically (via crontab) update the Pandora SSL certificate for Pandora
## Process attributed to Bob Saska (r35rag0th) <git@r35.net> at 
## http://everyday-tech.com/how-to-install-pianobar-on-the-raspberry-pi/
## To install: IN sudo crontab -e -u root ADD 0 13 * * 1 PATH/TO/THIS/update-pianobar-cert.sh
cert=$(openssl s_client -connect tuner.pandora.com:443 < /dev/null 2> /dev/null | openssl x509 -noout -fingerprint | tr -d ':' | cut -d'=' -f2)
sed -i "s/tls_fingerprint \= [a-zA-Z0-9]*/tls_fingerprint \= ${cert}/" ~/.config/pianobar/config
