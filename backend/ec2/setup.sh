#!/bin/bash
# EC2 user-data script: install dependencies and start the Flask server on port 80.
set -e

yum update -y
yum install -y python3 python3-pip

cd /home/ec2-user/app
pip3 install -r requirements.txt

# TODO: configure as a systemd service for production
python3 app.py
