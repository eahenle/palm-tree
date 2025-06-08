#!/bin/bash

LOG="/home/pi/auth-bot/update.log"

"*/15 * * * * /home/pi/auth-bot/poll-github.sh >> $LOG 2>&1" | crontab -e
"@reboot sleep 15 && /usr/bin/python3 /home/pi/auth-bot/post-ngrok-to-discord.py >> $LOG 2>&1" | crontab -e 
"@reboot sleep 15 && /usr/bin/python3 /home/pi/auth-bot/post-ngrok-to-discord-and-github.py >> $LOG 2>&1" | crontab -e 

