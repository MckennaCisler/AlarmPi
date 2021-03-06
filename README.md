# AlarmPi - A Raspberry Pi-based alarm clock with a configuration web interface

## Features
 - Settings for each day of the week
 - Sleep cycle alignment system for setting alarms aligned with REM cycles
 - Sound file and Pandora based alarms
 - Configuration web interface with responsive design and automatic configuration saving
 - 3D printed case and button and speaker configuration

## How to install
Simply clone the repository and run `install.sh`, which will install dependencies (in `requirements.txt`) and configure pianobar, the Pandora streaming system.

To start up the daemon (`backend/alarmpi.py`) and webserver (`backend/server.py`) automatically, add a command to run one of the included start scripts to `/etc/rc.local`:

`bash /home/pi/AlarmPi/start.sh` or `python /home/pi/AlarmPi/start.py`

The scripts will automatically run the application as the pi user to keep logfiles from being written as root.

To change the password for the web interface, generate the SHA-256 hash of your desired password using a tool such as [this one](https://www.xorbin.com/tools/sha256-hash-calculator), and then set `LOGIN_PASSWORD_HASH` in `server.py` to that hash.

I suggest you launch the web interface to get a better sense of the configuration and features of the project.

## Physical setup
The AlarmPi requires several physical add-ons to the Pi:
 - Three [buttons](http://www.digikey.com/product-detail/en/e-switch/RP3502MABLK/EG1932-ND/280450) ('dismiss,' 'snooze,' and 'sleep now' for using the cycle-aligned alarm)
 - A small speaker and a headphone cable (I got these from a pair of old headphones)
 - A small [3W amplifier](https://www.amazon.com/uxcell%C2%AE-PAM8403-Digital-Amplifier-2-5-5V/dp/B00EZI0RGA/ref=sr_1_2?rps=1&ie=UTF8&qid=1468202034&sr=8-2&keywords=PAM8403&refinements=p_85%3A2470955011) to boost the speaker
 - (Optional) A buzzer or LED to give feedback for button presses

I have also created a 3D-printed case (hosted on [OnShape](https://cad.onshape.com/documents/572a233d16a9cb5c5a07492d/w/6e8dac4342ebed8540e47ba9/e/8249a621653d40b8929a5b40)) for housing a Raspberry Pi 2 with all these required components.

Unfortunately, I do not have more extensive documentation on the physical assembly, but if you are interested in more help feel free to contact me at mckennacisler@gmail.com.
