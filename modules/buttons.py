"""
!/usr/bin/env python3
This Python file uses the following encoding: utf-8
"""


# Standard librarys
from time import time

# Additional pip librarys
import RPi.GPIO as GPIO


class Buttons:
    """Class Button"""
    __buttons = []

    @staticmethod
    def total():
        """Return __buttons length"""
        return len(Buttons.__buttons)

    @staticmethod
    def pull_up():
        """Return GPIO.PUD_UP"""
        return GPIO.PUD_UP

    @staticmethod
    def pull_down():
        """Return GPIO.PUD_DOWN"""
        return GPIO.PUD_DOWN

    @staticmethod
    def add(button):
        """Add new button to list"""
        Buttons.__buttons.append(button)

    @staticmethod
    def check():
        """Check all buttons in list for state etc."""
        for b in Buttons.__buttons:
            b.check()

    class NewPressed:
        """Class NewPressed"""

        def __init__(self, pin, pull_up_down, func, *, debounce_time=50):
            self.__pin = pin
            self.__pull_up_down = pull_up_down
            self.__func_pressed = func['pressed']
            self.__debounce_time = float(debounce_time)/1000
            self.__reading = 1
            self.__last_reading = 1
            self.__first_time = 0

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.__pin, GPIO.IN, pull_up_down=self.__pull_up_down)

        def check(self):
            """Check button for state etc."""
            # Button read gpio
            self.__reading = GPIO.input(self.__pin)
            # Button first down
            if self.__reading == 0 and self.__last_reading == 1:
                self.__first_time = time()
            # Button released
            if self.__reading == 1 and self.__last_reading == 0:
                # Button pressed and debounced
                if time() - self.__first_time > self.__debounce_time:
                    # If function pressed has set
                    if self.__func_pressed:
                        self.__func_pressed()
            # Assign reading to last reading
            self.__last_reading = self.__reading

    class NewPressedAdvanced:
        """NewPressedAdvanced"""

        def __init__(self, pin, pull_up_down, func, *, debounce_time=50):
            self.__pin = pin
            self.__pull_up_down = pull_up_down
            self.__func_for_pressed = func['for_pressed']
            self.__func_released = func['released']
            self.__func_pressed = func['pressed']
            self.__debounce_time = float(debounce_time)/1000
            self.__reading = 1
            self.__last_reading = 1
            self.__first_time = 0

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.__pin, GPIO.IN, pull_up_down=self.__pull_up_down)

        def check(self):
            """Check button for state etc."""
            # Button read gpio
            self.__reading = GPIO.input(self.__pin)
            # Button first down
            if self.__reading == 0 and self.__last_reading == 1:
                self.__first_time = time()
            # Button down
            if self.__reading == 0 and self.__last_reading == 0:
                # Button for pressed
                if time() - self.__first_time > self.__debounce_time:
                    # If function for pressed has set
                    if self.__func_for_pressed:
                        self.__func_for_pressed()
            # Button released
            if self.__reading == 1 and self.__last_reading == 0:
                # Button pressed and debounced
                if time() - self.__first_time > self.__debounce_time:
                    # If function released has set
                    if self.__func_released:
                        self.__func_released()
                    # If function pressed has set
                    if self.__func_pressed:
                        self.__func_pressed()
            # Assign reading to last reading
            self.__last_reading = self.__reading

    class NewHeld:
        """NewHeld"""

        def __init__(self, pin, pull_up_down, func, *, debounce_time=50, hold_time=2):
            self.__pin = pin
            self.__pull_up_down = pull_up_down
            self.__func_pressed = func['pressed']
            self.__func_held = func['held']
            self.__debounce_time = float(debounce_time)/1000
            self.__hold_time = hold_time
            self.__reading = 1
            self.__last_reading = 1
            self.__first_time = 0

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.__pin, GPIO.IN, pull_up_down=self.__pull_up_down)

        def check(self):
            """Check button for state etc."""
            # Button read gpio
            self.__reading = GPIO.input(self.__pin)
            # Button first down
            if self.__reading == 0 and self.__last_reading == 1:
                self.__first_time = time()
            # Button released
            if self.__reading == 1 and self.__last_reading == 0:
                # Button held
                if time() - self.__first_time > self.__hold_time:
                    # If function held has set
                    if self.__func_held:
                        self.__func_held()
                # Button pressed and debounced
                elif time() - self.__first_time > self.__debounce_time:
                    # If function pressed has set
                    if self.__func_pressed:
                        self.__func_pressed()
            # Assign reading to last reading
            self.__last_reading = self.__reading

    class NewHeldAdvanced:
        """Class NewHeldAdvanced"""

        def __init__(self, pin, pull_up_down, func, *, debounce_time=50, hold_time=2):
            self.__pin = pin
            self.__pull_up_down = pull_up_down
            self.__func_for_pressed = func['for_pressed']
            self.__func_for_held = func['for_held']
            self.__func_released = func['released']
            self.__func_pressed = func['pressed']
            self.__func_held = func['held']
            self.__debounce_time = float(debounce_time)/1000
            self.__hold_time = hold_time
            self.__reading = 1
            self.__last_reading = 1
            self.__first_time = 0

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.__pin, GPIO.IN, pull_up_down=self.__pull_up_down)

        def check(self):
            """Check button for state etc."""
            # Button read gpio
            self.__reading = GPIO.input(self.__pin)
            # Button first down
            if self.__reading == 0 and self.__last_reading == 1:
                self.__first_time = time()
            # Button down
            if self.__reading == 0 and self.__last_reading == 0:
                # Button for held
                if time() - self.__first_time > self.__hold_time:
                    # If function for held has set
                    if self.__func_for_held:
                        self.__func_for_held()
                # Button for pressed
                elif time() - self.__first_time > self.__debounce_time:
                    # If function for pressed has set
                    if self.__func_for_pressed:
                        self.__func_for_pressed()
            # Button released
            if self.__reading == 1 and self.__last_reading == 0:
                # Button held
                if time() - self.__first_time > self.__hold_time:
                    # If function released has set
                    if self.__func_released:
                        self.__func_released()
                    # If function held has set
                    if self.__func_held:
                        self.__func_held()
                # Button pressed and debounced
                elif time() - self.__first_time > self.__debounce_time:
                    # If function released has set
                    if self.__func_released:
                        self.__func_released()
                    # If function pressed has set
                    if self.__func_pressed:
                        self.__func_pressed()
            # Assign reading to last reading
            self.__last_reading = self.__reading
