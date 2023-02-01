"""
!/usr/bin/env python3
This Python file uses the following encoding: utf-8
"""


# Standard modules
import logging
import subprocess

# Additional pip modules

# Additional project modules
from modules.pages import Pages


class ButtonsFunc:
    """Class ButtonFunc"""

    @staticmethod
    def next_pressed_func():
        """When button was pressed go to next page"""
        Pages.next()

    @staticmethod
    def for_poweroff_held_func():
        """When button is held show poweroff image"""
        try:
            Pages.set_show_pages(False)
            Pages.poweroff()
        except Exception as e:
            logging.error(e)

    @staticmethod
    def poweroff_held_func():
        """When button was held execute poweroff"""
        try:
            Pages.set_show_pages(False)
            Pages.poweroff()
            subprocess.run('sudo poweroff', shell=True, check=True)
        except Exception as e:
            logging.exception(e)

    @staticmethod
    def previous_pressed_func():
        """When button was pressed go to previous page"""
        Pages.previous()

    @staticmethod
    def for_reboot_held_func():
        """When button is held show reboot image"""
        try:
            Pages.set_show_pages(False)
            Pages.reboot()
        except Exception as e:
            logging.exception(e)

    @staticmethod
    def reboot_held_func():
        """When button was held execute reboot"""
        try:
            Pages.set_show_pages(False)
            Pages.reboot()
            subprocess.run('sudo reboot', shell=True, check=True)
        except Exception as e:
            logging.exception(e)
