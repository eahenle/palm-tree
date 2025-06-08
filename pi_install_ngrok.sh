#!/bin/bash
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-arm.zip
unzip ngrok-stable-linux-arm.zip
sudo mv ngrok /usr/local/bin
ngrok config add-authtoken $NGROK_TOKEN
sudo echo "
[Unit]
Description=Ngrok Webhook Tunnel
After=network.target

[Service]
ExecStart=/usr/local/bin/ngrok http 9000 --log=stdout
Restart=on-failure
User=pi
Environment=NGROK_AUTHTOKEN=<your-ngrok-authtoken>

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/ngrok-webhook.service

sudo systemctl daemon-reexec
sudo systemctl enable ngrok-webhook
sudo systemctl start ngrok-webhook
