# -*- coding: utf-8 -*-

import sys
import os

import pygame

from logging import getLogger

from . import utils, errors, config


class GUI(metaclass=utils.Singleton):

    WIDTH = 480
    HEIGHT = 320
    SIZE = (WIDTH, HEIGHT)
    DEFAULT_FONT = 'roboto'
    BACKGROUND_COLOUR = (255, 255, 255)
    TEMP_TEXT_COLOUR = (0, 204, 0)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    def __init__(self, t):
        pygame.init()
        self.screen = None
        self.mouse_pos = (0, 0)  # mouse coordinates
        self.fonts = {}
        self.images = {}
        self.positions = {}  # image positions (Rect)
        self.thermostat = t
        self.logger = getLogger('app.gui')

        # font settings
        self.fonts['current_temperature'] = pygame.font.SysFont(self.DEFAULT_FONT, 80)
        self.fonts['temperature_range'] = pygame.font.SysFont(self.DEFAULT_FONT, 45)
        self.fonts['settings'] = pygame.font.SysFont(self.DEFAULT_FONT, 20)
        self.fonts['mode'] = pygame.font.SysFont(self.DEFAULT_FONT, 30)
        self.fonts['external_temperature'] = pygame.font.SysFont(self.DEFAULT_FONT, 40)

        # load images
        self.images['up_arrow'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'up.png'))
        self.images['down_arrow'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'down.png'))
        self.images['settings_menu'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'gear.png'))
        self.images['settings_title'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'SettingsHeader.png'))
        self.images['back_button'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'back.png'))
        self.images['power_off'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'power_off.png'))
        self.images['power_on'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'power_on.png'))
        self.images['clouds'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'clouds.png'))
        self.images['rain'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'rain.png'))
        self.images['clear'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'sun.png'))
        self.images['snow'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'snow.png'))
        self.images['mist'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'mist.png'))
        self.images['thunderstorm'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'thunder.png'))

        # image positions
        self.positions['current_temperature'] = pygame.Rect(190, 96, 120, 80)
        self.positions['low_temp'] = pygame.Rect(66, 106, 70, 45)
        self.positions['high_temp'] = pygame.Rect(357, 106, 70, 45)
        self.positions['low_temp_up'] = pygame.Rect(64, 32, 64, 60)
        self.positions['low_temp_down'] = pygame.Rect(64, 140, 64, 60)
        self.positions['high_temp_up'] = pygame.Rect(352, 32, 64, 60)
        self.positions['high_temp_down'] = pygame.Rect(352, 140, 64, 60)
        self.positions['settings_menu'] = pygame.Rect(405, 250, 45, 4500)
        self.positions['settings_title'] = pygame.Rect(154, 0, 1, 1)
        self.positions['back_button'] = pygame.Rect(168, 256, 150, 35)
        self.positions['power_toggle'] = pygame.Rect(18, 250, 50, 50)
        self.positions['external_temp'] = pygame.Rect(185, 180, 60, 50)
        self.positions['weather_icon'] = pygame.Rect(250, 172, 50, 50)
        self.positions['mode'] = pygame.Rect(185, 280, 160, 40)

    def run(self):
        self.thermostat.start()

        # create window
        self.screen = pygame.display.set_mode(self.SIZE)
        self.draw_home_screen()
        pygame.display.flip()

        # home screen
        while True:
            self.draw_temperatures()
            self.draw_weather()
            self.draw_mode()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop(shutdown=True)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_pos = pygame.mouse.get_pos()

                    try:
                        if self.positions['power_toggle'].collidepoint(self.mouse_pos):
                            self.thermostat.toggle_power()
                        if self.positions['settings_menu'].collidepoint(self.mouse_pos):
                            self.settings_view()
                        elif self.positions['low_temp_up'].collidepoint(self.mouse_pos):
                            low, high = self.thermostat.temperature_range
                            self.thermostat.temperature_range = (low + 1, high)
                        elif self.positions['low_temp_down'].collidepoint(self.mouse_pos):
                            low, high = self.thermostat.temperature_range
                            self.thermostat.temperature_range = (low - 1, high)
                        elif self.positions['high_temp_up'].collidepoint(self.mouse_pos):
                            low, high = self.thermostat.temperature_range
                            self.thermostat.temperature_range = (low, high + 1)
                        elif self.positions['high_temp_down'].collidepoint(self.mouse_pos):
                            low, high = self.thermostat.temperature_range
                            self.thermostat.temperature_range = (low, high - 1)
                    except errors.TemperatureValidationError as e:
                        self.logger.debug(e)
                        # TODO: show error message

    def stop(self, shutdown=False):
        # TODO: safely terminate thread
        self.thermostat.stop()
        if shutdown is True:
            sys.exit()

    def settings_view(self):
        """ Settings screen.

        Display settings and their values.
        Returns when back button is clicked.
        """
        self.draw_settings_screen()
        self.draw_settings_values()
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop(shutdown=True)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_pos = pygame.mouse.get_pos()
                    if self.positions['back_button'].collidepoint(self.mouse_pos):
                        self.draw_home_screen()
                        pygame.display.flip()
                        return

    def draw_home_screen(self):
        """
        Draws the static elements on the home screen.
        """
        self.screen.fill(self.BACKGROUND_COLOUR)
        self.screen.blit(self.images['up_arrow'], self.positions['low_temp_up'])
        self.screen.blit(self.images['down_arrow'], self.positions['low_temp_down'])
        self.screen.blit(self.images['up_arrow'], self.positions['high_temp_up'])
        self.screen.blit(self.images['down_arrow'], self.positions['high_temp_down'])
        self.screen.blit(self.images['settings_menu'], self.positions['settings_menu'])
        self.screen.blit(self.images['power_off'], self.positions['power_toggle'])

    def draw_temperatures(self, update=True):
        """
        Draws the temperature values on the home screen.

        :param update: if true, will update the display immediately
        """
        # reset
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['current_temperature'])
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['low_temp'])
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['high_temp'])

        # render and draw text
        current_temperature = self.fonts['current_temperature'].render(
            '{0}C'.format(round(self.thermostat.current_temperature)), 1, self.TEMP_TEXT_COLOUR)
        low_temp = self.fonts['temperature_range'].render(
            '{0}C'.format(round(self.thermostat.temperature_range_floor)), 1, self.TEMP_TEXT_COLOUR)
        high_temp = self.fonts['temperature_range'].render(
            '{0}C'.format(round(self.thermostat.temperature_range_ceiling)), 1, self.TEMP_TEXT_COLOUR)
        self.screen.blit(current_temperature, self.positions['current_temperature'])
        self.screen.blit(low_temp, self.positions['low_temp'])
        self.screen.blit(high_temp, self.positions['high_temp'])

        if update is True:
            pygame.display.update([
                self.positions['current_temperature'],
                self.positions['low_temp'],
                self.positions['high_temp'],
            ])

    def draw_weather(self, update=True):
        """
        Draws the external temperature value and status icon on the home screen.

        :param update: if true, will update the display immediately
        """
        # reset
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['external_temp'])
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['weather_icon'])

        # draw
        external_temp = self.fonts['external_temperature'].render(
            '{0}C'.format(round(self.thermostat.weather_thread.temperature)), 1, self.BLACK)
        weather_icon = self.images.get(self.thermostat.weather_thread.status, self.images['clouds'])
        self.screen.blit(external_temp, self.positions['external_temp'])
        self.screen.blit(weather_icon, self.positions['weather_icon'])

        if update is True:
            pygame.display.update([
                self.positions['external_temp'],
                self.positions['weather_icon'],
            ])

    def draw_mode(self, update=True):
        """
        Draws the current mode on the home screen.

        :param update: if true, will update the display immediately
        """
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['mode'])
        mode = self.fonts['mode'].render('{0} MODE'.format(self.thermostat.mode), 1, self.BLACK)
        self.screen.blit(mode, self.positions['mode'])

        if update is True:
            pygame.display.update([self.positions['mode']])

    def draw_settings_screen(self):
        """
        Draws the static elements on the settings screen.
        """
        self.screen.fill(self.BACKGROUND_COLOUR)
        self.screen.blit(self.images['settings_title'], self.positions['settings_title'])
        self.screen.blit(self.images['back_button'], self.positions['back_button'])

        # setting names
        pretty_settings = utils.prettify_settings(self.thermostat.settings)
        for i, setting in enumerate(pretty_settings.keys()):
            text = self.fonts['settings'].render(setting, 1, self.BLACK)
            self.screen.blit(text, (0.1*self.WIDTH, (0.2*self.HEIGHT) + (i*20)))

    def draw_settings_values(self):
        """
        Draws the settings values.
        """
        pretty_settings = utils.prettify_settings(self.thermostat.settings)
        for i, value in enumerate(pretty_settings.values()):
            text = self.fonts['settings'].render(str(value), 1, self.BLACK)
            self.screen.blit(text, (0.6*self.WIDTH, (0.2*self.HEIGHT) + (i*20)))
