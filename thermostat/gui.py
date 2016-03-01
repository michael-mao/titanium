# -*- coding: utf-8 -*-

import sys
import os

import pygame

from collections import OrderedDict

from . import utils


settings = {'Test': 1, 'Another Test': 0}
sorted_settings = OrderedDict(sorted(settings.items(), key=lambda t: t[0]))


class GUI(metaclass=utils.Singleton):

    WIDTH = 480
    HEIGHT = 320
    SIZE = (WIDTH, HEIGHT)
    BACKGROUND_COLOUR = (25, 179, 230)
    BLACK = (0, 0, 0)
    ASSETS_DIR = os.path.join(utils.BASE_DIR, 'assets')

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.SIZE)
        self.mouse_pos = (0, 0)  # mouse coordinates
        self.fonts = {}
        self.images = {}
        self.positions = {}  # image positions (Rect)
        self.settings = sorted_settings
        
        # font settings
        self.fonts['current_temperature'] = pygame.font.SysFont("monospace", 60)
        self.fonts['temperature_range'] = pygame.font.SysFont("monospace", 30)
        self.fonts['settings'] = pygame.font.SysFont("monospace", 20)
        
        # load images
        self.images['up_arrow'] = pygame.image.load(os.path.join(self.ASSETS_DIR, 'arrowUp.png'))
        self.images['down_arrow'] = pygame.image.load(os.path.join(self.ASSETS_DIR, 'arrowDown.png'))
        self.images['settings_menu'] = pygame.image.load(os.path.join(self.ASSETS_DIR, 'gear.png'))
        self.images['settings_title'] = pygame.image.load(os.path.join(self.ASSETS_DIR, 'SettingsHeader.png'))
        self.images['back_button'] = pygame.image.load(os.path.join(self.ASSETS_DIR, 'back.png'))
        
        # image positions
        self.positions['current_temperature'] = pygame.Rect(0.4*self.WIDTH, 0.4*self.HEIGHT, 128, 64)
        self.positions['low_temp'] = pygame.Rect(0.1*self.WIDTH, 0.4*self.HEIGHT, 64, 64)
        self.positions['high_temp'] = pygame.Rect(0.8*self.WIDTH, 0.4*self.HEIGHT, 64, 64)
        self.positions['low_temp_up'] = pygame.Rect(0.1*self.WIDTH, 0.1*self.HEIGHT, 64, 64)
        self.positions['low_temp_down'] = pygame.Rect(0.1*self.WIDTH, 0.7*self.HEIGHT, 64, 64)
        self.positions['high_temp_up'] = pygame.Rect(0.8*self.WIDTH, 0.1*self.HEIGHT, 64, 64)
        self.positions['high_temp_down'] = pygame.Rect(0.8*self.WIDTH, 0.7*self.HEIGHT, 64, 64)
        self.positions['settings_menu'] = pygame.Rect(0.45*self.WIDTH, 0.7*self.HEIGHT, 64, 100)
        self.positions['settings_title'] = pygame.Rect(0.32*self.WIDTH, 0, 1, 1)
        self.positions['back_button'] = pygame.Rect(0.35*self.WIDTH, 0.8*self.HEIGHT, 150, 35)

        # dummy values
        self.low_temp = 20
        self.high_temp = 25

        self.run()

    def run(self):
        self.draw_home_screen()
        pygame.display.flip()

        # home screen
        while True:
            self.draw_temperatures()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_pos = pygame.mouse.get_pos()
                    if self.positions['settings_menu'].collidepoint(self.mouse_pos):
                        self.settings_view()
                    elif self.positions['low_temp_up'].collidepoint(self.mouse_pos):
                        self.low_temp += 1
                    elif self.positions['low_temp_down'].collidepoint(self.mouse_pos):
                        self.low_temp -= 1
                    elif self.positions['high_temp_up'].collidepoint(self.mouse_pos):
                        self.high_temp += 1
                    elif self.positions['high_temp_down'].collidepoint(self.mouse_pos):
                        self.high_temp -= 1

    def settings_view(self):
        self.draw_settings_screen()
        self.draw_settings_values()
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_pos = pygame.mouse.get_pos()
                    if self.positions['back_button'].collidepoint(self.mouse_pos):
                        self.draw_home_screen()
                        pygame.display.flip()
                        return

    def draw_home_screen(self):
        self.screen.fill(self.BACKGROUND_COLOUR)
        self.screen.blit(self.images['up_arrow'], self.positions['low_temp_up'])
        self.screen.blit(self.images['down_arrow'], self.positions['low_temp_down'])
        self.screen.blit(self.images['up_arrow'], self.positions['high_temp_up'])
        self.screen.blit(self.images['down_arrow'], self.positions['high_temp_down'])
        self.screen.blit(self.images['settings_menu'], self.positions['settings_menu'])

    def draw_temperatures(self, update=True):
        # reset
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['current_temperature'])
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['low_temp'])
        pygame.draw.rect(self.screen, self.BACKGROUND_COLOUR, self.positions['high_temp'])

        # render text
        current_temperature = self.fonts['current_temperature'].render("23C", 1, (255, 255, 0))
        low_temp = self.fonts['temperature_range'].render('{0}C'.format(self.low_temp), 1, (255, 255, 0))
        high_temp = self.fonts['temperature_range'].render('{0}C'.format(self.high_temp), 1, (255, 255, 0))

        # draw text
        self.screen.blit(current_temperature, self.positions['current_temperature'])
        self.screen.blit(low_temp, self.positions['low_temp'])
        self.screen.blit(high_temp, self.positions['high_temp'])

        if update is True:
            pygame.display.update([
                self.positions['current_temperature'],
                self.positions['low_temp'],
                self.positions['high_temp'],
            ])

    def draw_settings_screen(self):
        self.screen.fill(self.BACKGROUND_COLOUR)
        self.screen.blit(self.images['settings_title'], self.positions['settings_title'])
        self.screen.blit(self.images['back_button'], self.positions['back_button'])

        # settings
        for i, setting in enumerate(self.settings.keys()):
            text = self.fonts['settings'].render(setting, 1, self.BLACK)
            self.screen.blit(text, (0.1*self.WIDTH, (0.2*self.HEIGHT) + (i*20)))

    def draw_settings_values(self):

        for i, value in enumerate(self.settings.values()):
            text = self.fonts['settings'].render(str(value), 1, self.BLACK)
            self.screen.blit(text, (0.6*self.WIDTH, (0.2*self.HEIGHT) + (i*20)))
