import pygame as pg
import sys
from settings import *
from sprites import *
from grid import Grid
from simulation import *
from weather_effects import *
from ui import UI
from game_loop import GameLoop
from controller import *

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        
        # Initialize sprite groups
        self.all_sprites = pg.sprite.Group()
        self.tiles = pg.sprite.Group()
        self.infrastructure = pg.sprite.Group()
        self.ui_elements = pg.sprite.Group()
        
        # Initialize controllers and UI
        self.mouse_controller = MouseController(self)
        self.ui = UI(self)
        self.game_loop = GameLoop(self)
        
        # Initialize game attributes
        self.resources = STARTING_RESOURCES
        self.score = 0
        self.flood_percentage = 0
        self.state = MENU
        self.running = True

        self.rain_effect = RainEffect(self)
        self.water_overlay = WaterOverlay(self)


    def run(self):
        print("Game running. State:", self.state)  # Debug print
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def new(self):
        """Initialize a new game/level"""
        print("Starting new game...")  # Debug print
        # Clear existing sprites
        self.all_sprites.empty()
        self.tiles.empty()
        self.infrastructure.empty()
        self.ui_elements.empty()
        
        # Create grid and initialize houses
        self.grid = Grid(self, GRID_WIDTH, GRID_HEIGHT)
        self.grid.place_houses()  # Place houses right after grid creation
        
        # Initialize other game components
        self.water_sim = WaterSimulation(self, self.grid)
        self.resources = STARTING_RESOURCES
        self.state = PLANNING
        
        # Reinitialize mouse controller and toolbar
        self.mouse_controller = MouseController(self)
        
        print(f"Game state changed to: {self.state}")  # Debug print

    def update(self):
        """Update game state"""
        self.game_loop.update()
        self.all_sprites.update()
        
        if self.state == PLANNING:
            self.mouse_controller.update()
        elif self.state == WEATHER:
            self.rain_effect.update()
            self.water_overlay.update()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.KEYDOWN:
                print(f"Key pressed: {event.key}")  # Debug print
                self.handle_keypress(event.key)
            if event.type == pg.MOUSEBUTTONDOWN and self.state == PLANNING:
                self.mouse_controller.handle_click(event.pos, event.button)
            if event.type == pg.MOUSEBUTTONUP and self.state == PLANNING:
                self.mouse_controller.handle_release()

    def draw(self):
        self.screen.fill(BLACK)  # Clear screen
        
        if self.state == MENU:
            self.ui.draw()
        else:
            self.all_sprites.draw(self.screen)
            # Draw water overlays
        if self.state in [PLANNING, WEATHER]:
            for sprite in self.tiles:
                self.water_overlay.draw_water_level(sprite, self.screen)
        
        # Draw infrastructure health bars
        for sprite in self.infrastructure:
            InfrastructureIndicator(sprite).draw(self.screen)
        
        # Draw rain effect on top
        self.rain_effect.draw(self.screen)
        
        # Draw UI
        self.ui.draw()
        
        pg.display.flip()

    def handle_keypress(self, key):
        """Handle keyboard input"""
        # Let game loop handle state transitions
        self.game_loop.handle_input(key)
        
        # Handle tool selection in planning phase
        if self.state == PLANNING:
            if key == pg.K_b:  # 'b' key
                print("B key pressed - selecting barrier")  # Debug print
                self.mouse_controller.toolbar.select_tool(BARRIER)
            elif key == pg.K_v:  # 'v' key
                print("V key pressed - selecting vegetation")  # Debug print
                self.mouse_controller.toolbar.select_tool(VEGETATION)
            elif key == pg.K_r:  # 'r' key
                print("R key pressed - selecting remove")  # Debug print
                self.mouse_controller.toolbar.select_tool("remove")

    def quit(self):
        pg.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    main()