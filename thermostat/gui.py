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
        self.fonts['current_temperature'] = pygame.font.SysFont(self.DEFAULT_FONT, 100)
        self.fonts['temperature_range'] = pygame.font.SysFont(self.DEFAULT_FONT, 45)
        self.fonts['settings_title'] = pygame.font.SysFont(self.DEFAULT_FONT, 45)
        self.fonts['settings'] = pygame.font.SysFont(self.DEFAULT_FONT, 20)
        self.fonts['mode'] = pygame.font.SysFont(self.DEFAULT_FONT, 30)
        self.fonts['state'] = pygame.font.SysFont(self.DEFAULT_FONT, 25)
        self.fonts['external_temperature'] = pygame.font.SysFont(self.DEFAULT_FONT, 40)
        self.fonts['graph'] = pygame.font.SysFont(self.DEFAULT_FONT, 18)

        # load images
        self.images['up_arrow'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'up.png'))
        self.images['down_arrow'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'down.png'))
        self.images['settings_menu'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'gear.png'))
        self.images['back_button'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'back.png'))
        self.images['power_off'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'power_off.png'))
        self.images['power_on'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'power_on.png'))
        self.images['graph'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'graph.png'))
        self.images['clouds'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'clouds.png'))
        self.images['rain'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'rain.png'))
        self.images['clear'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'sun.png'))
        self.images['snow'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'snow.png'))
        self.images['mist'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'mist.png'))
        self.images['thunderstorm'] = pygame.image.load(os.path.join(config.ASSETS_DIR, 'thunder.png'))

        # image positions
        self.positions['current_temperature'] = pygame.Rect(205, 90, 110, 60)
        self.positions['low_temp'] = pygame.Rect(75, 105, 50, 45)
        self.positions['high_temp'] = pygame.Rect(365, 105, 50, 45)
        self.positions['low_temp_up'] = pygame.Rect(64, 32, 64, 60)
        self.positions['low_temp_down'] = pygame.Rect(64, 140, 64, 60)
        self.positions['high_temp_up'] = pygame.Rect(352, 32, 64, 60)
        self.positions['high_temp_down'] = pygame.Rect(352, 140, 64, 60)
        self.positions['settings_menu'] = pygame.Rect(405, 250, 50, 50)
        self.positions['settings_title'] = pygame.Rect(155, 30, 1, 1)
        self.positions['back_button'] = pygame.Rect(168, 256, 150, 35)
        self.positions['power_toggle'] = pygame.Rect(18, 250, 50, 50)
        self.positions['external_temp'] = pygame.Rect(190, 180, 60, 50)
        self.positions['weather_icon'] = pygame.Rect(250, 170, 50, 50)
        self.positions['mode'] = pygame.Rect(185, 270, 135, 20)
        self.positions['state'] = pygame.Rect(205, 65, 80, 20)

    def run(self):
        self.thermostat.start()

        # create window
        if utils.on_rpi():
            self.screen = pygame.display.set_mode(self.SIZE, pygame.FULLSCREEN)
            pygame.mouse.set_visible(False)
        else:
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
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    flags = self.screen.get_flags()
                    if flags:
                        self.screen = pygame.display.set_mode(self.SIZE)
                    else:
                        self.screen = pygame.display.set_mode(self.SIZE, pygame.FULLSCREEN)
                    self.draw_home_screen()
                    pygame.display.flip()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_pos = pygame.mouse.get_pos()

                    try:
                        if self.positions['power_toggle'].collidepoint(self.mouse_pos):
                            self.thermostat.toggle_power()
                        elif self.positions['settings_menu'].collidepoint(self.mouse_pos):
                            self.settings_view()
                        elif self.positions['mode'].collidepoint(self.mouse_pos):
                            self.thermostat.toggle_mode()
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
                    elif self.positions['settings_menu'].collidepoint(self.mouse_pos):
                        self.history_view()

    def history_view(self):
        """ History screen.

        Display history graph.
        Returns when back button is clicked.
        """
        self.screen.fill(self.BACKGROUND_COLOUR)
        self.screen.blit(self.images['back_button'], self.positions['back_button'])
        self.screen.blit(self.fonts['settings'].render("Past 24 Hours", 1, self.BLACK), (200, 20))
        self.screen.blit(self.fonts['settings'].render("Temperature", 1, self.BLACK), (10, 20))
        self.screen.blit(self.fonts['settings'].render("Hour", 1, self.BLACK), (400, 260))

        xaxis_start = (50, 240)
        xaxis_end = (55, 240)
        yaxis_start = (50, 240)
        yaxis_end = (50, 235)
        clock = pygame.time.Clock()

        def update_x(variable, increment, restricter):
            new_y = variable[1]
            if variable[0] == restricter:
                return variable
            else:
                new_x = variable[0] + increment
                return (new_x, new_y)

        def update_y(variable, increment, restricter):
            new_x = variable[0]
            if variable[1] == restricter:
                return variable
            else:
                new_y = variable[1] + increment
                return (new_x, new_y)

        # every 15 pixels for x axis = 360 for 24 hours
        # every 15 pixels for x axis = 180 for 12 temperature points
        history_data = utils.get_history_graph_data(self.thermostat._history)
        min_temp = min(history_data, key=lambda t: t[1])[1]
        data_points = []
        for key, value in history_data:
            x_coord = 50 + (15 * key)
            y_coord = 200 - (15 * (value - min_temp))
            data_points.append((x_coord, y_coord))
        while xaxis_end[0] != 450 or yaxis_end[1] != 40:
            clock.tick(200)

            xaxis_end = update_x(xaxis_end, 1, 450)
            yaxis_end = update_y(yaxis_end, -1, 40)
            pygame.draw.line(self.screen, self.BLACK, xaxis_start, xaxis_end, 3)
            pygame.draw.line(self.screen, self.BLACK, yaxis_start, yaxis_end, 3)
            pygame.draw.lines(self.screen, self.RED, False, data_points, 2)

            # print x axis labels (time)
            for i in range(24):
                x = 50 + (15 * i)
                if i % 2 == 0:
                    self.screen.blit(self.fonts['graph'].render(str(i), 1, self.BLACK), (x, 242))

            # print y axis labels (temperature)
            for i in range(10):
                y = i + min_temp - 1
                if y % 2 != 0:
                    self.screen.blit(self.fonts['graph'].render(str(y), 1, self.BLACK), (32, 200-(15*i)))

            pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop(shutdown=True)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_pos = pygame.mouse.get_pos()
                    if self.positions['back_button'].collidepoint(self.mouse_pos):
                        self.draw_settings_screen()
                        self.draw_settings_values()
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
        pygame.draw.rect(self.screen, self.BLACK, [170, 255, 155, 45], 2)

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
            str(round(self.thermostat.current_temperature)), 1, self.TEMP_TEXT_COLOUR)
        low_temp = self.fonts['temperature_range'].render(
            str(round(self.thermostat.temperature_range_floor)), 1, self.TEMP_TEXT_COLOUR)
        high_temp = self.fonts['temperature_range'].render(
            str(round(self.thermostat.temperature_range_ceiling)), 1, self.TEMP_TEXT_COLOUR)
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
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['external_temp'])
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['weather_icon'])

        external_temp = self.fonts['external_temperature'].render(
            '{0}C'.format(round(self.thermostat.weather_thread.temperature)), 1, self.BLACK)
        weather_icon = self.images.get(self.thermostat.weather_thread.status, self.images['clouds'])
        self.screen.blit(external_temp, self.positions['external_temp'])
        self.screen.blit(weather_icon, self.positions['weather_icon'])

        if update is True:
            pygame.display.update([self.positions['external_temp'], self.positions['weather_icon']])

    def draw_mode(self, update=True):
        """
        Draws the current mode and state on the home screen.

        :param update: if true, will update the display immediately
        """
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['mode'])
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['state'])

        mode = self.fonts['mode'].render('{0} MODE'.format(self.thermostat.mode), 1, self.BLACK)
        if self.thermostat.state == utils.State.HEAT:
            state = self.fonts['state'].render('HEATING', 1, self.RED)
            self.screen.blit(state, self.positions['state'])
        elif self.thermostat.state == utils.State.COOL:
            state = self.fonts['state'].render('COOLING', 1, self.BLUE)
            self.screen.blit(state, self.positions['state'])
        self.screen.blit(mode, self.positions['mode'])

        if update is True:
            pygame.display.update([self.positions['mode'], self.positions['state']])

    def draw_settings_screen(self):
        """
        Draws the static elements on the settings screen.
        """
        self.screen.fill(self.BACKGROUND_COLOUR)
        self.screen.blit(self.fonts['settings_title'].render('SETTINGS', 1, self.BLACK), self.positions['settings_title'])
        self.screen.blit(self.images['back_button'], self.positions['back_button'])
        self.screen.blit(self.images['graph'], self.positions['settings_menu'])

        # setting names
        pretty_settings = utils.prettify_settings(self.thermostat.settings)
        for i, setting in enumerate(pretty_settings.keys()):
            text = self.fonts['settings'].render(setting, 1, self.BLACK)
            self.screen.blit(text, (0.1*self.WIDTH, (0.25*self.HEIGHT) + (i*20)))

    def draw_settings_values(self):
        """
        Draws the settings values.
        """
        pretty_settings = utils.prettify_settings(self.thermostat.settings)
        for i, value in enumerate(pretty_settings.values()):
            text = self.fonts['settings'].render(str(value), 1, self.BLACK)
            self.screen.blit(text, (0.6*self.WIDTH, (0.25*self.HEIGHT) + (i*20)))
