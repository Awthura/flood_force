import pygame as pg
from settings import *

class GameLoop:
    def __init__(self, game):
        self.game = game
        self.level = 1
        self.score = 0
        self.flood_percentage = 0

    def update(self):
        if self.game.state == PLANNING:
            self.update_planning()
        elif self.game.state == WEATHER:
            self.update_weather()

    def update_planning(self):
        self.game.mouse_controller.update()

    def update_weather(self):
        # Update water simulation
        self.game.water_sim.update()
        self.calculate_results()

    def calculate_results(self):
        flood_tiles = 0
        total_land_tiles = 0
        
        for row in self.game.grid.tiles:
            for tile in row:
                if tile.tile_type == WATER and hasattr(tile, 'was_land'):
                    flood_tiles += 1
                if tile.tile_type == LAND or (tile.tile_type == WATER and hasattr(tile, 'was_land')):
                    total_land_tiles += 1
        
        self.flood_percentage = (flood_tiles / total_land_tiles * 100) if total_land_tiles > 0 else 0
        if self.flood_percentage > MAX_FLOOD_PERCENTAGE:
            self.game.state = GAME_OVER

    def handle_input(self, key):
        if key == pg.K_SPACE:
            if self.game.state == MENU:
                self.game.new()
            elif self.game.state == PLANNING:
                self.game.state = WEATHER
        elif key == pg.K_r and (self.game.state == GAME_OVER or self.game.state == VICTORY):
            self.game.new()