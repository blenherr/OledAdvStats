# OLED Advanced Stats Display Script For Raspberry Pi

- [Information](#information)
- [Wiring](#wiring)
- [Installation guide](#installation-guide)
- [Configuration](#configuration)
- [Testing](#testing)
- [Add service OR crontab](#add-service-or-crontab)
- [Contribute](#contribute)
- [Acknowledgment](#acknowledgment)

# Information

The popular Raspberry Pi OLED Stats scripts tend to be very limited, so i created my own project.

Features:
- Set up multiple pages of your choice
- Auto mode: Flip through pages(Slideshow)
- Manual mode: Controlled by at least one button
- Screensaver: Turns the display off after a certain amount of time and turns it on again by pressing the button (Only supportet in manual mode)

Pages:
- CPU and memory statistics (Is only needed once)
- Storage statistics from a mount point of your choice (Set up as many as you like)
- Network statistics from a interface of your choise (Set up as many as you like)
- Docker statistics (only needed once)

| Page CPU and memory       | Page Storage              |
|:-------------------------:|:-------------------------:|
| ![Page CPU and memory](https://user-images.githubusercontent.com/122442255/216108713-0a771fbe-2ca2-4674-acc1-4d727f0c7cee.gif) | ![Page Storage](https://user-images.githubusercontent.com/122442255/216108897-bd6a272e-655c-4e1b-a867-b0c5777db277.gif) |
| Page Network              | Page Docker               |
| ![Page Network](https://user-images.githubusercontent.com/122442255/216108996-47804d36-f2cc-4833-8674-c3b6c526278b.gif) | ![Page Docker](https://user-images.githubusercontent.com/122442255/216109067-96720283-c834-4be4-b8bc-fe699c7600cb.gif) |

# Wiring
## Display
| OLED Pin | Pi GPIO Pin | Notes   |
|:---------|:------------|:--------|
| VCC      | 1           | 3.3V    |
| GND      | 9           | Ground  |
| SCL      | 5           | I2C SCL |
| SDA      | 3           | I2C SDA |
## Button(s)
Any GPIO pin you like. Connected to GND (Ground) which is pulled up internally by Raspberry Pi

# Installation guide
## 1. Update system
```
sudo apt update && sudo apt -y full-upgrade
```
## 2. Install needed packages
Install apt packages
```
sudo apt install -y python3 python3-pip i2c-tools git
```
Install pip packages
```
pip3 install pyyaml psutil adafruit-circuitpython-ssd1306
```
## 3. Enable I2C interface
Enabling I2C on the Raspberry Pi using one simple command
```
sudo raspi-config nonint do_i2c 0
```
Checking that I2C is enabled
```
sudo raspi-config nonint get_i2c
```
This command will return:
- **1** if the port is **disabled**
- **0** if the port is **enabled**

Check the I2C status
```
sudo i2cdetect -y 1
```
You should see output something like this
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --
```
Reboot if necessary
```
sudo reboot
```
## 4. Enable Docker memory stats
**(You can skip this step if you are not using Docker)**

Edit `/boot/cmdline.txt`
```
sudo nano /boot/cmdline.txt
```
Add the following options at the beginning of the line
```
systemd.unified_cgroup_hierarchy=0 cgroup_enable=memory cgroup_memory=1 
```
Save and close. Confirm that c-groups are enabled
```
cat /proc/cgroups
```
You should see output like this
```
#subsys_name    hierarchy       num_cgroups     enabled
cpuset  9       15      1
cpu     7       69      1
cpuacct 7       69      1
blkio   8       69      1
memory  11      158     1
devices 3       69      1
freezer 5       16      1
net_cls 2       15      1
perf_event      6       15      1
net_prio        2       15      1
pids    4       76      1
rdma    10      1       1
```
Reboot
```
sudo reboot
```
## 5. Clone git repository
```
git clone https://github.com/blenherr/OledAdvStats.git
```
# Configuration
Edit `config.yml`
```
nano ~/OledAdvStats/config/config.yml
```
Content of `config.yml` file:
```
# OLED Advanced Stats Display Script For Raspberry Pi  - Configuration File


main:

# Main definitions
#
#   showicons: yes, no (Is always required)
#   mode: auto, manual (Is always required)
#   autodelay: time in seconds (Disabled in manual mode)
#   screensaver: Time in minutes, 0 for off (Disabled in auto mode)
#
# Examples:
#
#  showicons: "yes"
#  mode: "auto"
#  autodelay: "10"
#
#  showicons: "yes"
#  mode: "manual"
#  screensaver: "1"

  showicons: "no"
  mode: "auto"
  autodelay: "10"
  

pages:

# You can set up as many pages as you like,
# but a minimum of two pages is required
#
# cpumem - Displays CPU and memory statistics
#   type: cpumem
#   icon: not supported (only one icon)
#   value: not supported
#
# Example:
#  - type: "cpumem"

  - type: "cpumem"

# storage - Displays statistics from a mount point of your choice
#   type: storage
#   icon: emmc, hdd, sd, ssd
#   value: your mount point
#
# Example:
#  - type: "storage"
#    icon: "sd"
#    value: "/"

  - type: "storage"
    icon: "sd"
    value: "/"
  - type: "storage"
    icon: "sd"
    value: "/boot"

# network - Displays network statistics from an interface of your choice
#   type: network
#   icon: lan, wifi
#   value: your used interface (eth0, wlan0)
#
# Example:
#  - type: "network"
#    icon: "lan"
#    value: "eth0"

  - type: "network"
    icon: "wifi"
    value: "wlan0"

# docker - Displays Docker statistics
#
#   type: docker
#   icon: not supported (only one icon)
#   value: not supported
#
# Example:
#  - type: "docker"

#  - type: "docker"


buttons:

# At least one button is required in manual mode.
# Buttons are ignored in Auto mode.
#
#   type: pressed, hold
#       pressed - Button with one function
#       hold    - Button with two functions
#   gpio: Your used GPIO pin
#   func: next, previous
#       next     - Go to the next page
#       previous - Go to the previous page
#   holdfunc: poweroff, reboot
#       poweroff - Runs 'sudo poweroff'
#       reboot   - Runs 'sudo reboot'
#   holdtime: Time in seconds
#
# Examples:
#
#  - type: "pressed"
#    gpio: "22"
#    func: "next"
#
#  - type: "hold"
#    gpio: "22"
#    func: "next"
#    holdfunc: "poweroff"
#    holdtime: "5"
#
#  - type: "pressed"
#    gpio: "23"
#    func: "previous"

  - type: "pressed"
    gpio: "22"
    func: "next"
```
# Testing
```
python3 ~/OledAdvStats/main.py
```
# Add service OR crontab
## Add service
Create `OledAdvStats.service` file
```
sudo nano /lib/systemd/system/OledAdvStats.service
```
Add following lines and change `your_user_goes_here` with your own user
```
[Unit]
Description=OLED Advanced Stats Display Script For Raspberry Pi 

[Service]
Type=simple
User=your_user_goes_here
Group=your_user_goes_here
ExecStart=/usr/bin/python3 /home/your_user_goes_here/OledAdvStats/main.py
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
```
Save and close

Enable service
```
sudo systemctl enable OledAdvStats
```
Start service
```
sudo systemctl start OledAdvStats
```
## Add crontab
Edit crontab
```
crontab -e
```
Add following lines at the bottom and change `your_user_goes_here` with your own user
```
@reboot python3 /home/your_user_goes_here/OledAdvStats/main.py &
```
Save and close

# Contribute
- Let me know if you have another idea for a new page or if you found a problem. Thank you!

# Acknowledgment
- https://github.com/mklements/OLED_Stats
