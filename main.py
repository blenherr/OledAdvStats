"""
!/usr/bin/env python3
This Python file uses the following encoding: utf-8
"""


# Standard modules
from datetime import datetime
import logging
import os
import sys
from time import sleep
import threading
import re

# Additional pip modules
import yaml

# Additional project modules
from modules.buttons import Buttons
from modules.buttonsfunc import ButtonsFunc
from modules.pages import Pages


REAL_PATH = os.path.dirname(os.path.realpath(__file__))


def load_config():
    """Load configuration"""
    # Load configuraton file
    if not os.path.exists(REAL_PATH + '/config/config.yml'):
        e = 'No config found!'
        logging.error(e)
        sys.exit(e)
    try:
        with open(REAL_PATH + '/config/config.yml', 'r', encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except Exception as e:
        logging.exception(e)
        sys.exit(e)
    if config is None:
        e = 'Config is not a yaml file!'
        logging.error(e)
        sys.exit(e)

    # Load main configuration
    if not 'main' in config:
        e = 'Config does not contain a \'main\' paragraph!'
        logging.error(e)
        sys.exit(e)
    config_main = config['main']
    if not 'mode' in config_main:
        e = 'Config paragraph \'main\' does not contain a \'mode\' key!'
        logging.error(e)
        sys.exit(e)
    if not 'showicons' in config_main:
        e = 'Config paragraph \'main\' does not contain a \'showicons\' key!'
        logging.error(e)
        sys.exit(e)
    if not Pages.set_show_icons(config_main['showicons']):
        e = 'Config paragraph \'main\' key \'showicons\' is not setup correctly!'
        logging.error(e)
        sys.exit(e)
    if 'auto' in config_main['mode']:
        Pages.set_mode(config_main['mode'])
        if not 'autodelay' in config_main:
            e = 'Config paragraph \'main\' does not contain a \'autodelay\' key!'
            logging.error(e)
            sys.exit(e)
        if not Pages.set_auto_delay(config_main['autodelay']):
            e = 'Config paragraph \'main\' key \'autodelay\' is not a number!'
            logging.error(e)
            sys.exit(e)
    elif 'manual' in config_main['mode']:
        Pages.set_mode(config_main['mode'])
        if not 'screensaver' in config_main:
            e = 'Config paragraph \'main\' does not contain a \'screensaver\' key!'
            logging.error(e)
            sys.exit(e)
        if not Pages.Screensaver.set(config_main['screensaver']):
            e = 'Config paragraph \'main\' key \'screensaver\' is not a number!'
            logging.error(e)
            sys.exit(e)
    else:
        e = 'Config paragraph \'main\' key \'mode\' is not setup correctly!'
        logging.error(e)
        sys.exit(e)

    # Load pages configuration
    if not 'pages' in config:
        e = 'Config does not contain a \'pages\' paragraph!'
        logging.error(e)
        sys.exit(e)
    for config_page in config['pages']:
        if not 'type' in config_page:
            e = 'Config paragraph \'pages\' is not setup correctly!'
            logging.error(e)
            sys.exit(e)
        if not config_page['type'].lower() in Pages.requirements():
            e = 'Config paragraph \'pages\' is not setup correctly!'
            logging.error(e)
            sys.exit(e)
        if 'simple' in Pages.requirements()[config_page['type'].lower()]['pointer']:
            if 'icon' in config_page:
                key = config_page['type'].lower()
                e = f'Config paragraph \'pages\' key \'{key}\' is not setup correctly!'
                logging.error(e)
                sys.exit(e)
            if 'value' in config_page:
                key = config_page['type'].lower()
                e = f'Config paragraph \'pages\' key \'{key}\' is not setup correctly!'
                logging.error(e)
                sys.exit(e)
            ptr = Pages.str_to_ptr(config_page['type'].lower())
            if ptr:
                Pages.add({
                    'ptr': ptr,
                    'args': None
                })
        if 'advanced' in Pages.requirements()[config_page['type'].lower()]['pointer']:
            if not 'icon' in config_page:
                key = config_page['type'].lower()
                e = f'Config paragraph \'pages\' key \'{key}\' is not setup correctly!'
                logging.error(e)
                sys.exit(e)
            if not 'value' in config_page:
                key = config_page['type'].lower()
                e = f'Config paragraph \'pages\' key \'{key}\' is not setup correctly!'
                logging.error(e)
                sys.exit(e)
            if not config_page['icon'] in Pages.requirements()[config_page['type'].lower()]['icons']:
                key = config_page['type'].lower()
                e = f'Config paragraph \'pages\' key \'{key}\' is not setup correctly!'
                logging.error(e)
                sys.exit(e)
            if not re.match(Pages.requirements()[config_page['type'].lower()]['values'], config_page['value']):
                key = config_page['type'].lower()
                e = f'Config paragraph \'pages\' key \'{key}\' is not setup correctly!'
                logging.error(e)
                sys.exit(e)
            ptr = Pages.str_to_ptr(config_page['type'].lower())
            if ptr:
                Pages.add({
                    'ptr': ptr,
                    'args': {'icon': config_page['icon'], 'value': config_page['value']}
                })

    # Load buttons configuration
    if 'manual' in config_main['mode']:
        if not 'buttons' in config:
            e = 'Config does not contain a \'buttons\' paragraph!'
            logging.error(e)
            sys.exit(e)
        if config['buttons'] is None:
            e = 'You need to setup at least one push button!'
            logging.error(e)
            sys.exit(e)
        for config_buttons in config['buttons']:
            if not 'type' or not 'gpio' or not 'func' in config_buttons:
                e = 'Config paragraph \'buttons\' is not setup correctly!'
                logging.error(e)
                sys.exit(e)
            try:
                GPIO = abs(int(config_buttons['gpio']))
            except Exception:
                e = 'Config paragraph \'buttons\' key \'gpio\' is not a number!'
                logging.error(e)
                sys.exit(e)
            if 'next' in config_buttons['func']:
                FUNC = ButtonsFunc.next_pressed_func
            elif 'previous' in config_buttons['func']:
                FUNC = ButtonsFunc.previous_pressed_func
            else:
                e = 'Config paragraph \'buttons\' key \'func\' is not setup correctly!'
                logging.error(e)
                sys.exit(e)
            if 'pressed' in config_buttons['type']:
                FUNC_DICT = {
                    'pressed': FUNC
                }
                Buttons.add(Buttons.NewPressed(
                    GPIO,
                    Buttons.pull_up(),
                    FUNC_DICT
                ))
            elif 'hold' in config_buttons['type']:
                if not 'holdfunc' or not 'holdtime' in config_buttons:
                    e = 'Config paragraph \'buttons\' is not setup correctly!'
                    logging.error(e)
                    sys.exit(e)
                if 'poweroff' in config_buttons['holdfunc']:
                    FOR_HELD_FUNC = ButtonsFunc.for_poweroff_held_func
                    HELD_FUNC = ButtonsFunc.poweroff_held_func
                elif 'reboot' in config_buttons['holdfunc']:
                    FOR_HELD_FUNC = ButtonsFunc.for_reboot_held_func
                    HELD_FUNC = ButtonsFunc.reboot_held_func
                else:
                    e = 'Config paragraph \'buttons\' key \'holdfunc\' is not setup correctly!'
                    logging.error(e)
                    sys.exit(e)
                FUNC_DICT = {
                    'for_pressed': None,
                    'for_held': FOR_HELD_FUNC,
                    'released': None,
                    'pressed': FUNC,
                    'held': HELD_FUNC
                }
                try:
                    HOLDTIME = abs(int(config_buttons['holdtime']))
                except Exception:
                    e = 'Config paragraph \'buttons\' key \'holdtime\' is not a number!'
                    logging.error(e)
                    sys.exit(e)
                Buttons.add(Buttons.NewHeldAdvanced(
                    GPIO,
                    Buttons.pull_up(),
                    FUNC_DICT,
                    hold_time=HOLDTIME
                ))
            else:
                e = 'Config paragraph \'buttons\' key \'type\' is not setup correctly!'
                logging.error(e)
                sys.exit(e)


run_event = None


def check_buttons(run_event):
    """Buttons need to be checked for state etc."""
    while run_event.is_set():
        Buttons.check()
        sleep(0.01)


def start_check_buttons_thread():
    """start_check_buttons_thread"""
    try:
        run_event = threading.Event()
        run_event.set()
        thread_check_buttons = threading.Thread(
            target=check_buttons, args=(run_event,))
        thread_check_buttons.daemon = True
        thread_check_buttons.start()
    except Exception as e:
        logging.error(e)


def main():
    """Main programm"""

    # logging
    log_dir = os.path.dirname(os.path.realpath(__file__)) + '/log'
    os.makedirs(log_dir, exist_ok=True)
    now = datetime.now()
    date = now.strftime('%Y_%m_%d')
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        filename=log_dir + f'/{date}.log',
        datefmt='%H:%M:%S',
        level=logging.DEBUG
    )

    load_config()

    if Buttons.total() > 0:
        start_check_buttons_thread()

    while True:
        try:
            Pages.show()
            sleep(0.01)
        except Exception as e:
            logging.exception(e)
            run_event.clear()


if __name__ == '__main__':
    main()
