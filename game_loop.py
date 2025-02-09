import pygame as pg
from settings import *

class GameLoop:
    def __init__(self, game):
        self.game = game
        self.level = 1
        self.score = 0

    def update(self):
        """Update game state based on current phase."""
        if self.game.state == PLANNING:
            self.update_planning()
        elif self.game.state == WEATHER:
            self.update_weather()

    def update_planning(self):
        """Update planning phase."""
        self.game.mouse_controller.update()

    def update_weather(self):
        """Update weather phase."""
        # Let water simulation handle everything during weather phase
        self.game.water_sim.update()
        # Don't override water simulation's game state decisions

    def handle_input(self, key):
        """Handle keyboard input."""
        if key == pg.K_SPACE:
            if self.game.state == MENU:
                self.game.new()
            elif self.game.state == PLANNING:
                self.game.state = WEATHER  # Start weather simulation