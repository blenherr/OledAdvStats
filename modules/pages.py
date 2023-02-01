"""
!/usr/bin/env python3
This Python file uses the following encoding: utf-8
"""


# Standard modules
import json
import logging
import os
import socket
import subprocess
from time import time
import threading

# Additional pip modules
import board
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import psutil

# Additional project modules


# Definitions
KB = 1024
MB = KB * 1024
GB = MB * 1024

NET_KB = 1000
NET_MB = NET_KB * 1000
NET_GB = NET_MB * 1000

# Display size
WIDTH = 128
HEIGHT = 64
FONTSIZE = 16

# Display positions
LEFT = 0
RIGHT = WIDTH
TOP = 0
BOTTOM = HEIGHT
LINE1 = TOP                 # Y position line 1
LINE2 = TOP + FONTSIZE      # Y position line 2
LINE3 = TOP + 2 * FONTSIZE  # Y position line 3
LINE4 = TOP + 3 * FONTSIZE  # Y position line 3

# Initialize i2c and OLED display
I2C = board.I2C()
OLED = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, I2C, addr=0x3C)
# Clear display
OLED.fill(0)
OLED.show()

# Create blank image for drawing. Make sure to create image with mode '1' for 1-bit color.
IMAGE = Image.new('1', (WIDTH, HEIGHT))

# Get drawing object to draw on image.
DRAW = ImageDraw.Draw(IMAGE)

# Path
REAL_PATH = os.path.dirname(os.path.realpath(__file__))

# Icons
IMG_CPU_MEM = Image.open(REAL_PATH + '/icons/cpu_mem.png')
IMG_EMMC = Image.open(REAL_PATH + '/icons/emmc.png')
IMG_HDD = Image.open(REAL_PATH + '/icons/hdd.png')
IMG_SD = Image.open(REAL_PATH + '/icons/sd.png')
IMG_SSD = Image.open(REAL_PATH + '/icons/ssd.png')
IMG_LAN = Image.open(REAL_PATH + '/icons/lan.png')
IMG_WIFI = Image.open(REAL_PATH + '/icons/wifi.png')
IMG_DOCKER = Image.open(REAL_PATH + '/icons/docker.png')
IMG_POWEROFF = Image.open(REAL_PATH + '/icons/poweroff.png')
IMG_REBOOT = Image.open(REAL_PATH + '/icons/reboot.png')
IMG_NETDOWN = Image.open(REAL_PATH + '/icons/netdown.png')
IMG_NETUP = Image.open(REAL_PATH + '/icons/netup.png')

# Text
FONT = ImageFont.truetype(REAL_PATH + '/font/PixelOperator.ttf', FONTSIZE)

PAGES_MODE_AUTO = 1
PAGES_MODE_MANUAL = 2


class Pages:
    """Class Pages"""

    __print_icon = True
    __print_text = False
    __last_loop = 0
    __mode = PAGES_MODE_AUTO
    __func_ptr = []
    __current_page = 0
    __auto_delay = 10
    __last_auto_delay = time()
    __show_icons = True

    @staticmethod
    def requirements():
        """Get PAGES_DICT"""
        PAGES_DICT = {
            'cpumem': {
                'pointer': 'simple'
            },
            'storage': {
                'pointer': 'advanced',
                'icons': ['emmc', 'hdd', 'sd', 'ssd'],
                'values': r'(^/$)|((/[a-zA-Z0-9_-]+)+$)'
            },
            'network': {
                'pointer': 'advanced',
                'icons': ['wifi', 'lan'],
                'values': r'^(wlan|eth)[0-9]{1}$'
            },
            'docker': {
                'pointer': 'simple'
            }
        }
        return PAGES_DICT

    @staticmethod
    def set_mode(m):
        """Set __mode"""
        if 'auto' in m:
            Pages.__mode = PAGES_MODE_AUTO
            return True
        if 'manual' in m:
            Pages.__mode = PAGES_MODE_MANUAL
            return True
        return False

    @staticmethod
    def set_auto_delay(i):
        """Set __auto_delay"""
        try:
            Pages.__auto_delay = abs(int(i))
            return True
        except ValueError:
            return False

    @staticmethod
    def set_show_icons(m):
        """Set __show_icons"""
        if 'yes' in m:
            Pages.__show_icons = True
            return True
        if 'no' in m:
            Pages.__show_icons = False
            return True
        return False

    @staticmethod
    def get_show_icons():
        """Get __show_icons"""
        return Pages.__show_icons

    @staticmethod
    def get_print_icon():
        """Get __print_icon"""
        return Pages.__print_icon

    @staticmethod
    def set_print_icon(b):
        """Set __print_icon"""
        Pages.__print_icon = b

    @staticmethod
    def get_print_text():
        """Get __print_text"""
        return Pages.__print_text

    @staticmethod
    def set_print_text(b):
        """Set __print_text"""
        Pages.__print_text = b

    @staticmethod
    def get_last_loop():
        """Get __last_loop"""
        return Pages.__last_loop

    @staticmethod
    def set_last_loop(i):
        """Set __last_loop"""
        Pages.__last_loop = i

    @staticmethod
    def total():
        """Return __func_ptr length"""
        return len(Pages.__func_ptr)

    @staticmethod
    def add(page_dict):
        """Add page to funtion pointer list"""
        Pages.__func_ptr.append(page_dict)

    @staticmethod
    def str_to_ptr(s):
        """Convert function pointer string to function pointer"""
        if 'cpumem' in s:
            return CpuMem.page
        elif 'storage' in s:
            return Storage.page
        elif 'network' in s:
            return Network.page
        elif 'docker' in s:
            return Docker.page
        else:
            return None

    @staticmethod
    def get_pixel_offset(value, digits):
        """Get pixel length offset"""
        return 7 * (digits - len(str(int(value))))

    @staticmethod
    def next():
        """Go to next page"""
        if not Pages.Screensaver.display_status():
            Pages.__current_page += 1
            if Pages.__current_page >= Pages.total():
                Pages.__current_page = 0
        Pages.Screensaver.turn_display_on()
        Pages.reset()

    @staticmethod
    def previous():
        """Go to previous page"""
        if not Pages.Screensaver.display_status():
            Pages.__current_page -= 1
            if Pages.__current_page < 0:
                Pages.__current_page = Pages.total() - 1
        Pages.Screensaver.turn_display_on()
        Pages.reset()

    @staticmethod
    def reset():
        """Perform reset all pages"""
        Pages.set_print_icon(True)
        Pages.set_print_text(False)
        Pages.set_last_loop(0)
        CpuMem.reset()
        Storage.reset()
        Network.reset()
        Docker.reset()

    @staticmethod
    def show():
        """Show pages in auto or manual mode"""
        if Pages.__mode is PAGES_MODE_AUTO:
            """Auto mode - Cycle thru pages"""
            if time() - Pages.__last_auto_delay >= Pages.__auto_delay:
                Pages.__last_auto_delay = time()
                Pages.next()
            Pages.__func_ptr[Pages.__current_page]['ptr'](
                Pages.__func_ptr[Pages.__current_page]['args'])
        elif Pages.__mode is PAGES_MODE_MANUAL:
            """Manual mode - Show current selected page"""
            Pages.Screensaver.logic()
            if not Pages.Screensaver.display_status():
                Pages.__func_ptr[Pages.__current_page]['ptr'](
                    Pages.__func_ptr[Pages.__current_page]['args'])

    @staticmethod
    def poweroff():
        """Show ipoweroff image"""
        # Draw a black filled box to clear the image
        DRAW.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
        # Draw bitmap
        DRAW.bitmap((32, 0), IMG_POWEROFF, fill=1)
        # Display image
        OLED.image(IMAGE)
        OLED.show()

    @staticmethod
    def reboot():
        """Show reboot image"""
        # Draw a black filled box to clear the image
        DRAW.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
        # Draw bitmap
        DRAW.bitmap((32, 0), IMG_REBOOT, fill=1)
        # Display image
        OLED.image(IMAGE)
        OLED.show()

    class Screensaver:
        """Class Screensaver"""

        __time_delay = 5  # Value in minutes
        __last_delay = time()
        __status = False

        @staticmethod
        def set(t):
            """set"""
            try:
                Pages.Screensaver.__time_delay = abs(int(t))
                return True
            except ValueError:
                return False

        @staticmethod
        def enabled():
            """enabled"""
            if Pages.Screensaver.__time_delay == 0:
                return False
            else:
                return True

        @staticmethod
        def display_status():
            """display_status"""
            return Pages.Screensaver.__status

        @staticmethod
        def turn_display_on():
            """Turn display on"""
            Pages.Screensaver.__status = False
            Pages.Screensaver.__last_delay = time()

        @staticmethod
        def turn_display_off():
            """Turn display off"""
            OLED.fill(0)
            OLED.show()

        @staticmethod
        def logic():
            """logic"""
            if Pages.Screensaver.__time_delay == 0:
                return
            if time() - Pages.Screensaver.__last_delay >= Pages.Screensaver.__time_delay * 60:
                if not Pages.Screensaver.__status:
                    Pages.Screensaver.turn_display_off()
                Pages.Screensaver.__status = True


class CpuMem:
    """Class CpuMem"""

    __sleep = 1
    __error_printed = False

    @staticmethod
    def reset():
        """reset"""
        CpuMem.__error_printed = False

    @staticmethod
    def page(args):
        """Content of cpumem page"""
        try:
            this_loop = time()
            # Draw icon
            if Pages.get_show_icons() and Pages.get_print_icon():
                Pages.set_last_loop(this_loop)
                Pages.set_print_icon(False)
                # Draw a black filled box to clear the image
                DRAW.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
                # Draw bitmap
                DRAW.bitmap((32, 0), IMG_CPU_MEM, fill=1)
                # Display image
                OLED.image(IMAGE)
                OLED.show()
            # Draw text
            elif (this_loop - Pages.get_last_loop() >= 1 and not Pages.get_print_text()) or (this_loop - Pages.get_last_loop() >= CpuMem.__sleep and Pages.get_print_text()):
                Pages.set_last_loop(this_loop)
                Pages.set_print_text(True)
                # Draw a black filled box to clear the image
                DRAW.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
                # Line 1
                # CPU utilization in %
                cpu = psutil.cpu_percent()
                buffer = f'CPU {round(cpu, 1):.1f}%' if cpu < 10 else f'CPU {round(cpu, 0):.0f}%'
                DRAW.text((LEFT, LINE1), buffer, font=FONT, fill=255)
                # CPU frequency in MHz
                freq = psutil.cpu_freq().current
                buffer = f'{round(freq, 0):.0f} MHz'
                DRAW.text((RIGHT, LINE1), buffer,
                          font=FONT, fill=255, anchor="ra")
                # Line 2 - Average system load in %
                DRAW.text((LEFT, LINE2), 'LOAD', font=FONT, fill=255)
                load = [l / psutil.cpu_count() * 100 for l in psutil.getloadavg()]
                buffer = f'{round(load[0], 1):.1f}% ' if load[0] < 10 else f'{round(load[0], 0):.0f}% '
                buffer += f'{round(load[1], 1):.1f}% ' if load[1] < 10 else f'{round(load[1], 0):.0f}% '
                buffer += f'{round(load[2], 1):.1f}%' if load[2] < 10 else f'{round(load[2], 0):.0f}%'
                DRAW.text((RIGHT, LINE2), buffer,
                          font=FONT, fill=255, anchor="ra")
                # Line 3 - CPU temperature in °C
                DRAW.text((LEFT, LINE3), 'TEMP', font=FONT, fill=255)
                temperature = psutil.sensors_temperatures()
                cpu_thermal_current = round(
                    temperature['cpu_thermal'][0].current, 1)
                buffer = f'{cpu_thermal_current:.1f} °C'
                DRAW.text((RIGHT, LINE3), buffer,
                          font=FONT, fill=255, anchor="ra")
                # Line 4 - Used Memory in MB
                DRAW.text((LEFT, LINE4), 'MEM', font=FONT, fill=255)
                memory = psutil.virtual_memory()
                if memory.total / GB < 1:
                    buffer = f'{round(memory.used / MB):3d} MB / {round(memory.total / MB):3d} MB'
                else:
                    buffer = f'{round(memory.used / MB):4d} MB / {round(memory.total / GB):1d} GB'
                DRAW.text((RIGHT, LINE4), buffer,
                          font=FONT, fill=255, anchor="ra")
                # Display image
                OLED.image(IMAGE)
                OLED.show()
        except Exception as e:
            if not CpuMem.__error_printed:
                logging.exception(e)
                CpuMem.__error_printed = True


class Storage:
    """Class Storage"""

    __sleep = 1
    __error_printed = False

    @staticmethod
    def reset():
        """reset"""
        Storage.__error_printed = False

    @staticmethod
    def page(args):
        """Content of storage page"""
        try:
            this_loop = time()
            # Draw icon
            if Pages.get_show_icons() and Pages.get_print_icon():
                Pages.set_last_loop(this_loop)
                Pages.set_print_icon(False)
                # Draw a black filled box to clear the image
                DRAW.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
                # Draw bitmap
                if args['icon'] == 'emmc':
                    DRAW.bitmap((32, 0), IMG_EMMC, fill=1)
                elif args['icon'] == 'hdd':
                    DRAW.bitmap((32, 0), IMG_HDD, fill=1)
                elif args['icon'] == 'sd':
                    DRAW.bitmap((32, 0), IMG_SD, fill=1)
                elif args['icon'] == 'ssd':
                    DRAW.bitmap((32, 0), IMG_SSD, fill=1)
                # Display image
                OLED.image(IMAGE)
                OLED.show()
            # Draw text
            elif (this_loop - Pages.get_last_loop() >= 1 and not Pages.get_print_text()) or (this_loop - Pages.get_last_loop() >= Storage.__sleep and Pages.get_print_text()):
                Pages.set_last_loop(this_loop)
                Pages.set_print_text(True)
                # Draw a black filled box to clear the image
                DRAW.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
                mount_point = args['value']
                if not os.path.ismount(mount_point):
                    if not Storage.__error_printed:
                        e = f'Path \'{mount_point}\' is not a mount point!'
                        logging.error(e)
                        Storage.__error_printed = True
                    buffer = 'Path'
                    DRAW.text((LEFT, LINE1), buffer, font=FONT, fill=255)
                    buffer = f'\'{mount_point}\''
                    DRAW.text((LEFT, LINE2), buffer, font=FONT, fill=255)
                    buffer = 'is not a'
                    DRAW.text((LEFT, LINE3), buffer, font=FONT, fill=255)
                    buffer = 'mount point!'
                    DRAW.text((LEFT, LINE4), buffer, font=FONT, fill=255)

                else:
                    # Get data
                    disk_usage = psutil.disk_usage(mount_point)
                    # Line 1 - Mount point
                    buffer = 'MOUNT  ' + mount_point
                    if DRAW.textsize(buffer, font=FONT)[0] <= WIDTH:
                        DRAW.text((LEFT, LINE1), 'MOUNT', font=FONT, fill=255)
                        buffer = mount_point
                        DRAW.text((RIGHT, LINE1), buffer,
                                  font=FONT, fill=255, anchor="ra")
                    else:
                        DRAW.text((LEFT, LINE1), mount_point,
                                  font=FONT, fill=255)
                    # Line 2 - Used space
                    DRAW.text((LEFT, LINE2), 'USED', font=FONT, fill=255)
                    if disk_usage.used / GB < 1:
                        buffer = f'{round(disk_usage.used / MB, 3):.3f} MB'
                    else:
                        buffer = f'{round(disk_usage.used / GB, 3):.3f} GB'
                    DRAW.text((RIGHT, LINE2), buffer,
                              font=FONT, fill=255, anchor="ra")
                    # Line 3 - Free space
                    DRAW.text((LEFT, LINE3), 'FREE', font=FONT, fill=255)
                    if disk_usage.used / GB < 1:
                        buffer = f'{round(disk_usage.free / MB, 3):.3f} MB'
                    else:
                        buffer = f'{round(disk_usage.free / GB, 3):.3f} GB'
                    DRAW.text((RIGHT, LINE3), buffer,
                              font=FONT, fill=255, anchor="ra")
                    # Line 4 - Total space
                    DRAW.text((LEFT, LINE4), 'TOTAL', font=FONT, fill=255)
                    if disk_usage.used / GB < 1:
                        buffer = f'{round(disk_usage.total / MB, 3):.3f} MB'
                    else:
                        buffer = f'{round(disk_usage.total / GB, 3):.3f} GB'
                    DRAW.text((RIGHT, LINE4), buffer,
                              font=FONT, fill=255, anchor="ra")
                # Display image
                OLED.image(IMAGE)
                OLED.show()
        except Exception as e:
            if not Storage.__error_printed:
                logging.exception(e)
                Storage.__error_printed = True


class Network:
    """Class Network"""

    __sleep = 1
    __last_in = -1.0
    __last_out = -1.0
    __error_printed = False

    @staticmethod
    def get_usage_in(interface):
        """Get incomming network treffic"""
        stat = psutil.net_io_counters(pernic=True, nowrap=True)[interface]
        this_in = stat.bytes_recv
        if Network.__last_in >= 0:
            usage_in = this_in - Network.__last_in
        else:
            usage_in = 0.0
        Network.__last_in = this_in
        return usage_in

    @staticmethod
    def get_usage_out(interface):
        """Get outgoing network treffic"""
        stat = psutil.net_io_counters(pernic=True, nowrap=True)[interface]
        this_out = stat.bytes_sent
        usage_in = 0.0
        if Network.__last_out >= 0:
            usage_in = this_out - Network.__last_out
        Network.__last_out = this_out
        return usage_in

    @staticmethod
    def get_ipv4(interface):
        """Get IPv4 Address from interface"""
        res = '?'
        try:
            iface = psutil.net_if_addrs()[interface]
            for addr in iface:
                if addr.family is socket.AddressFamily.AF_INET:
                    return addr.address
        except Exception as e:
            logging.exception(e)
        return res

    @staticmethod
    def reset():
        """Perform reset"""
        Network.__last_in = -1.0
        Network.__last_out = -1.0
        Network.__error_printed = False

    @staticmethod
    def page(args):
        """Content of network page"""
        try:
            this_loop = time()
            # Draw icon
            if Pages.get_show_icons() and Pages.get_print_icon():
                Pages.set_last_loop(this_loop)
                Pages.set_print_icon(False)
                # Draw a black filled box to clear the image
                DRAW.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
                # Draw bitmap
                if args['icon'] == 'lan':
                    DRAW.bitmap((32, 0), IMG_LAN, fill=1)
                elif args['icon'] == 'wifi':
                    DRAW.bitmap((32, 0), IMG_WIFI, fill=1)
                # Display image
                OLED.image(IMAGE)
                OLED.show()
            # Draw text
            elif (this_loop - Pages.get_last_loop() >= 1 and not Pages.get_print_text()) or (this_loop - Pages.get_last_loop() >= Network.__sleep and Pages.get_print_text()):
                Pages.set_last_loop(this_loop)
                Pages.set_print_text(True)
                # Draw a black filled box to clear the image
                DRAW.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
                interface = args['value']
                if not os.path.exists(f'/sys/class/net/{interface}'):
                    if not Network.__error_printed:
                        e = f'Network interface \'{interface}\' does not exist!'
                        logging.error(e)
                        Network.__error_printed = True
                    buffer = 'Network interface'
                    DRAW.text((LEFT, LINE1), buffer, font=FONT, fill=255)
                    buffer = f'\'{interface}\''
                    DRAW.text((LEFT, LINE2), buffer, font=FONT, fill=255)
                    buffer = 'does not exist'
                    DRAW.text((LEFT, LINE3), buffer, font=FONT, fill=255)
                    # buffer = 'mount point!'
                    # DRAW.text((LEFT, LINE4), buffer, font=FONT, fill=255)
                else:
                    # Line 1 - Hostname
                    DRAW.text((LEFT, LINE1), socket.gethostname(),
                              font=FONT, fill=255)
                    # Line 2 - IP address
                    DRAW.text((LEFT, LINE2), Network.get_ipv4(
                        interface), font=FONT, fill=255)
                    # Line 3 - Usage sent
                    DRAW.bitmap((1, LINE3), IMG_NETUP, fill=1)
                    usage_out = Network.get_usage_out(interface)
                    # Byte
                    if usage_out < NET_KB:
                        buffer = f'{round(usage_out / NET_KB, 3):.3f} KB/s'
                    # Kilo Byte
                    elif round(usage_out / NET_KB, 3) < 10:
                        buffer = f'{round(usage_out / NET_KB, 3):.3f} KB/s'
                    elif round(usage_out / NET_KB, 2) < 100:
                        buffer = f'{round(usage_out / NET_KB, 2):.2f} KB/s'
                    elif round(usage_out / NET_KB, 1) < 1000:
                        buffer = f'{round(usage_out / NET_KB, 1):.1f} KB/s'
                    # Mega Byte
                    elif round(usage_out / NET_MB, 3) < 10:
                        buffer = f'{round(usage_out / NET_MB, 3):.3f} MB/s'
                    elif round(usage_out / NET_MB, 2) < 100:
                        buffer = f'{round(usage_out / NET_MB, 2):.2f} MB/s'
                    elif round(usage_out / NET_MB, 1) < 1000:
                        buffer = f'{round(usage_out / NET_MB, 1):.1f} MB/s'
                    DRAW.text((LEFT + 11, LINE3), buffer, font=FONT, fill=255)
                    # Line 4 - Usage received
                    DRAW.bitmap((1, LINE4), IMG_NETDOWN, fill=1)
                    usage_in = Network.get_usage_in(interface)
                    # Byte
                    if usage_in < NET_KB:
                        buffer = f'{round(usage_in / NET_KB, 3):.3f} KB/s'
                    # Kilo Byte
                    elif round(usage_in / NET_KB, 3) < 10:
                        buffer = f'{round(usage_in / NET_KB, 3):.3f} KB/s'
                    elif round(usage_in / NET_KB, 2) < 100:
                        buffer = f'{round(usage_in / NET_KB, 2):.2f} KB/s'
                    elif round(usage_in / NET_KB, 1) < 1000:
                        buffer = f'{round(usage_in / NET_KB, 1):.1f} KB/s'
                    # Mega Byte
                    elif round(usage_in / NET_MB, 3) < 10:
                        buffer = f'{round(usage_in / NET_MB, 3):.3f} MB/s'
                    elif round(usage_in / NET_MB, 2) < 100:
                        buffer = f'{round(usage_in / NET_MB, 2):.2f} MB/s'
                    elif round(usage_in / NET_MB, 1) < 1000:
                        buffer = f'{round(usage_in / NET_MB, 1):.1f} MB/s'
                    DRAW.text((LEFT + 11, LINE4), buffer, font=FONT, fill=255)
                    # Line 4 - Interface
                    buffer = interface
                    DRAW.text((RIGHT, LINE4), buffer,
                              font=FONT, fill=255, anchor="ra")
                # Display image
                OLED.image(IMAGE)
                OLED.show()
        except Exception as e:
            if not Network.__error_printed:
                logging.exception(e)
                Network.__error_printed = True


class Docker:
    """Class Docker"""

    __sleep = 5
    __state_list = None
    __usage_json = None
    __thread = None
    __error_printed = False

    @staticmethod
    def get_docker_status():
        """Get docker status"""
        try:
            subprocess.check_output(
                'systemctl is-active docker',
                shell=True
            ).decode('utf-8')
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def get_running_list():
        """Get docker running list"""
        try:
            output_str = subprocess.check_output(
                'docker ps --all --format "{{.State}},"',
                shell=True,
                stderr=subprocess.STDOUT
            ).decode('utf-8')[:-2]
            Docker.__state_list = output_str.split(',\n')
        except Exception as e:
            logging.exception(e)
            return False

    @staticmethod
    def get_usage_json():
        """Get docker usage json"""
        try:
            output_str = '[' + subprocess.check_output('docker stats --no-stream --format \'{\"CPUPerc\":{{ .CPUPerc }}, \"MemUsage\":{{ json .MemUsage }}, "PIDs":{{ .PIDs }}},\'',
                                                       shell=True, stderr=subprocess.STDOUT).decode('utf-8').replace('%', '')[:-2] + ']'
            Docker.__usage_json = json.loads(output_str)
        except Exception as e:
            logging.exception(e)

    @staticmethod
    def memory_str_to_float(s):
        """Convert memory string to float"""
        if 'KiB' in s:
            return float(s.replace('KiB', '')) * KB
        if 'MiB' in s:
            return float(s.replace('MiB', '')) * MB
        if 'GiB' in s:
            return float(s.replace('GiB', '')) * GB
        return float(s.replace('B', ''))

    @staticmethod
    def reset():
        """Perform reset"""
        try:
            Docker.__state_list = None
            Docker.__usage_json = None
            Docker.__error_printed = False
            if Docker.__thread is not None:
                if Docker.__thread.is_alive():
                    Docker.__thread = None
        except Exception as e:
            logging.exception(e)

    @staticmethod
    def page(args):
        """Content of docker page"""
        try:
            this_loop = time()
            # Draw icon
            if Pages.get_show_icons() and Pages.get_print_icon():
                Pages.set_last_loop(this_loop)
                Pages.set_print_icon(False)
                # Draw a black filled box to clear the image
                DRAW.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
                # Draw bitmap
                DRAW.bitmap((32, 0), IMG_DOCKER, fill=1)
                # Display image
                OLED.image(IMAGE)
                OLED.show()
            # Draw text
            elif (this_loop - Pages.get_last_loop() >= 1 and not Pages.get_print_text()) or (this_loop - Pages.get_last_loop() >= Docker.__sleep and Pages.get_print_text()):
                Pages.set_last_loop(this_loop)
                Pages.set_print_text(True)
                # Draw a black filled box to clear the image
                DRAW.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
                if not Docker.get_docker_status():
                    if not Docker.__error_printed:
                        e = 'Docker service is not active or not installed!'
                        logging.error(e)
                        Docker.__error_printed = True
                    buffer = 'Docker service'
                    DRAW.text((LEFT, LINE1), buffer, font=FONT, fill=255)
                    buffer = 'is not active'
                    DRAW.text((LEFT, LINE2), buffer, font=FONT, fill=255)
                    buffer = 'or not installed!'
                    DRAW.text((LEFT, LINE3), buffer, font=FONT, fill=255)
                    # buffer = ''
                    # DRAW.text((LEFT, LINE4), buffer, font=FONT, fill=255)
                else:
                    Docker.get_running_list()
                    if Docker.__thread is None or not Docker.__thread.is_alive():
                        Docker.__thread = threading.Thread(
                            target=Docker.get_usage_json)
                        Docker.__thread.daemon = True
                        Docker.__thread.start()
                    Pages.set_last_loop(this_loop)
                    # Draw a black filled box to clear the image
                    DRAW.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
                    # Line 1 - running containers / total containers
                    DRAW.text((LEFT, LINE1), 'RUNNING', font=FONT, fill=255)
                    if Docker.__state_list is not None:
                        running = Docker.__state_list.count('running')
                        total = len(Docker.__state_list)
                        buffer = f'{running:d} / {total:d}'
                    else:
                        buffer = 'get data'
                    DRAW.text((RIGHT, LINE1), buffer,
                              font=FONT, fill=255, anchor="ra")
                    # Line 2 - CPU usage total
                    DRAW.text((LEFT, LINE2), 'CPU LOAD', font=FONT, fill=255)
                    if Docker.__usage_json is not None:
                        load = round(sum(float(i['CPUPerc'])
                                         for i in Docker.__usage_json), 2)
                        buffer = f'{load:.2f} %'
                    else:
                        buffer = 'get data'
                    DRAW.text((RIGHT, LINE2), buffer,
                              font=FONT, fill=255, anchor="ra")
                    # Line 3 - Memory usage total
                    DRAW.text((LEFT, LINE3), 'MEM', font=FONT, fill=255)
                    if Docker.__usage_json is not None:
                        mem = round(sum([Docker.memory_str_to_float(
                            x) for x in i['MemUsage'].split(' / ')][0] for i in Docker.__usage_json))
                        total = Docker.memory_str_to_float(
                            Docker.__usage_json[0]['MemUsage'].split(' / ')[1])
                        if total / GB < 1:
                            buffer = f'{round(mem / MB):4d} MB / {round(total / MB):1d} MB'
                        else:
                            buffer = f'{round(mem / MB):4d} MB / {round(total / GB):1d} GB'
                    else:
                        buffer = 'get data'
                    DRAW.text((RIGHT, LINE3), buffer,
                              font=FONT, fill=255, anchor="ra")
                    # Line 4 - PIDs total
                    DRAW.text((LEFT, LINE4), 'PIDS', font=FONT, fill=255)
                    if Docker.__usage_json is not None:
                        pids = round(sum(float(i['PIDs'])
                                         for i in Docker.__usage_json))
                        buffer = f'{pids:6d}'
                    else:
                        buffer = 'get data'
                    DRAW.text((RIGHT, LINE4), buffer,
                              font=FONT, fill=255, anchor="ra")
                # Display image
                OLED.image(IMAGE)
                OLED.show()
        except Exception as e:
            if not Docker.__error_printed:
                logging.exception(e)
                Docker.__error_printed = True
