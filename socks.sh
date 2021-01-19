#!/bin/bash

# Set up socks connection so locally running django can see the Prisme test server
# Make sure you are connected to the VPN to access the server
ssh -D 8888 10.240.76.38
