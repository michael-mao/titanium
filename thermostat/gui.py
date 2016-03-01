# -*- coding: utf-8 -*-

import sys
import os

import pygame

from . import utils


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
        self.text = {}
        
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
        self.positions['low_temp_up'] = pygame.Rect(0.1*self.WIDTH, 0.1*self.HEIGHT, 64, 64)
        self.positions['low_temp_down'] = pygame.Rect(0.1*self.WIDTH, 0.7*self.HEIGHT, 64, 64)
        self.positions['high_temp_up'] = pygame.Rect(0.8*self.WIDTH, 0.1*self.HEIGHT, 64, 64)
        self.positions['high_temp_down'] = pygame.Rect(0.8*self.WIDTH, 0.7*self.HEIGHT, 64, 64)
        self.positions['settings_menu'] = pygame.Rect(0.45*self.WIDTH, 0.7*self.HEIGHT, 64, 100)
        self.positions['settings_title'] = pygame.Rect(0.32*self.WIDTH, 0, 1, 1)
        self.positions['back_button'] = pygame.Rect(0.35*self.WIDTH, 0.8*self.HEIGHT, 150, 35)

        # text
        self.text['current_temperature'] = self.fonts['current_temperature'].render("23C", 1, (255, 255, 0))
        self.text['low_temp'] = None
        self.text['high_temp'] = None

        # dummy values
        self.low_temp = 20
        self.high_temp = 25

    def run(self):

        while True:
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

            # re-render text
            self.text['low_temp'] = self.fonts['temperature_range'].render('{0}C'.format(self.low_temp), 1, (255, 255, 0))
            self.text['high_temp'] = self.fonts['temperature_range'].render('{0}C'.format(self.high_temp), 1, (255, 255, 0))

            # draw images
            self.screen.fill(self.BACKGROUND_COLOUR)
            self.screen.blit(self.images['up_arrow'], self.positions['low_temp_up'])
            self.screen.blit(self.images['down_arrow'], self.positions['low_temp_down'])
            self.screen.blit(self.images['up_arrow'], self.positions['high_temp_up'])
            self.screen.blit(self.images['down_arrow'], self.positions['high_temp_down'])
            self.screen.blit(self.images['settings_menu'], self.positions['settings_menu'])
            
            # draw text
            self.screen.blit(self.text['current_temperature'], (0.4*self.WIDTH, 0.4*self.HEIGHT))
            self.screen.blit(self.text['low_temp'], (0.1*self.WIDTH, 0.4*self.HEIGHT))
            self.screen.blit(self.text['high_temp'], (0.8*self.WIDTH, 0.4*self.HEIGHT))
            pygame.display.flip()

    def settings_view(self):

        while True:
            # draw settings menu
            self.screen.fill(self.BACKGROUND_COLOUR)
            self.screen.blit(self.images['settings_title'], self.positions['settings_title'])
            self.screen.blit(self.images['back_button'], self.positions['back_button'])

            # display settings menu options
            self.screen.blit(self.fonts['settings'].render("Timezone", 1, (0, 0, 0)), (0.1*self.WIDTH, 0.2*self.HEIGHT))
            self.screen.blit(self.fonts['settings'].render("City", 1, (0, 0, 0)), (0.1*self.WIDTH, 0.2*self.HEIGHT + 20))
            self.screen.blit(self.fonts['settings'].render("Country", 1, (0, 0, 0)), (0.1*self.WIDTH, 0.2*self.HEIGHT + 40))
            self.screen.blit(self.fonts['settings'].render("Temperature Unit", 1, (0, 0, 0)), (0.1*self.WIDTH, 0.2*self.HEIGHT + 60))
            self.screen.blit(self.fonts['settings'].render("House Type", 1, (0, 0, 0)), (0.1*self.WIDTH, 0.2*self.HEIGHT + 80))
            self.screen.blit(self.fonts['settings'].render("House Size", 1, (0, 0, 0)), (0.1*self.WIDTH, 0.2*self.HEIGHT + 100))
            self.screen.blit(self.fonts['settings'].render("Temp. Low Range", 1, (0, 0, 0)), (0.1*self.WIDTH, 0.2*self.HEIGHT + 120))
            self.screen.blit(self.fonts['settings'].render("Temp. High Range", 1, (0, 0, 0)), (0.1*self.WIDTH, 0.2*self.HEIGHT + 140))

            # Assign variables
            Timezone = "EST"
            City = "Toronto"
            Country = "Canada"
            TemperatureUnit = "Celcius"
            HouseType = "apartment"
            HouseSize = "700"

            # display variables
            self.screen.blit(self.fonts['settings'].render(Timezone, 1, (0, 0, 0)), (0.6*self.WIDTH, 0.2*self.HEIGHT))
            self.screen.blit(self.fonts['settings'].render(City, 1, (0, 0, 0)), (0.6*self.WIDTH, 0.2*self.HEIGHT + 20))
            self.screen.blit(self.fonts['settings'].render(Country, 1, (0, 0, 0)), (0.6*self.WIDTH, 0.2*self.HEIGHT + 40))
            self.screen.blit(self.fonts['settings'].render(TemperatureUnit, 1, (0, 0, 0)), (0.6*self.WIDTH, 0.2*self.HEIGHT + 60))
            self.screen.blit(self.fonts['settings'].render(HouseType, 1, (0, 0, 0)), (0.6*self.WIDTH, 0.2*self.HEIGHT + 80))
            self.screen.blit(self.fonts['settings'].render(HouseSize, 1, (0, 0, 0)), (0.6*self.WIDTH, 0.2*self.HEIGHT + 100))
            self.screen.blit(self.fonts['settings'].render(str(self.low_temp), 1, (0, 0, 0)), (0.6*self.WIDTH, 0.2*self.HEIGHT + 120))
            self.screen.blit(self.fonts['settings'].render(str(self.high_temp), 1, (0, 0, 0)), (0.6*self.WIDTH, 0.2*self.HEIGHT + 140))

            pygame.display.flip()
            # check for event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_pos = pygame.mouse.get_pos()
                    if self.positions['back_button'].collidepoint(self.mouse_pos):
                        return
