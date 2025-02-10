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
from sound_manager import SoundManager
import asyncio

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
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        
        # Initialize game attributes
        self.resources = STARTING_RESOURCES
        self.score = 0
        self.flood_percentage = 0
        self.state = MENU
        self.running = True

        self.rain_effect = RainEffect(self)
        self.water_overlay = WaterOverlay(self)
        self.current_difficulty = None

    async def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
            await asyncio.sleep(0)  # Yield control back to the event loop

    def new(self, difficulty_level=2):
        """Initialize a new game/level"""
        print(f"Starting new game at difficulty level {difficulty_level}")
        
        # If no difficulty level is specified, use the last selected or default to 2
        if difficulty_level is None:
            difficulty_level = self.current_difficulty if self.current_difficulty is not None else 2
        
        # Explicitly set the current difficulty
        self.current_difficulty = difficulty_level
        level_config = DIFFICULTY_LEVELS[difficulty_level]
        
        # Update global constants dynamically
        global STARTING_RESOURCES
        STARTING_RESOURCES = level_config['starting_resources']

        # Clear existing sprites
        self.all_sprites.empty()
        self.tiles.empty()
        self.infrastructure.empty()
        self.ui_elements.empty()
        
        # Create grid with current difficulty settings
        self.grid = Grid(self, GRID_WIDTH, GRID_HEIGHT)
        
        # Place houses based on difficulty level
        self.grid.place_houses(level_config['house_count'])
        
        # Initialize other game components
        self.water_sim = WaterSimulation(self, self.grid)
        self.resources = STARTING_RESOURCES
        self.state = PLANNING
        
        # Reinitialize mouse controller and toolbar
        self.mouse_controller = MouseController(self)
        
        print(f"Game state changed to: {self.state}")

    def update(self):
        """Update game state"""
        # Update music based on current game state
        self.sound_manager.update_music(self.state)
        
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
            
            if event.type == pg.MOUSEBUTTONDOWN:
                # Handle menu clicks
                if self.state == MENU:
                    self.ui.handle_menu_click(event.pos)
                elif self.state == PLANNING:
                    self.mouse_controller.handle_click(event.pos, event.button)
            
            if event.type == pg.MOUSEBUTTONUP and self.state == PLANNING:
                self.mouse_controller.handle_release()
            
            if event.type == pg.KEYDOWN:
                print(f"Key pressed: {event.key}")  # Debug print
                self.handle_keypress(event.key)

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
            # You'll want to check if this is a tree acting as a barrier
            is_barrier_tree = (
                sprite.infra_type == VEGETATION and 
                self.water_sim.check_tree_barrier(sprite.tile)
            )
            
            indicator = InfrastructureIndicator(sprite)
            if is_barrier_tree:
                # Override the color method to always return GRAY
                indicator.get_health_color = lambda health: GRAY
            
            indicator.draw(self.screen)
        
        # Draw rain effect on top
        self.rain_effect.draw(self.screen)
        
        # Draw UI
        self.ui.draw()
        
        pg.display.flip()

    def handle_keypress(self, key):
        """Handle keyboard input"""
        # Quit game option on main menu
        if self.state == MENU and key == pg.K_q:
            self.running = False
            return

        # Let game loop handle state transitions
        self.game_loop.handle_input(key)
        
        if self.state == MENU:
            if key == pg.K_1:
                self.current_difficulty = 1
                self.new(1)  # Tutorial
            elif key == pg.K_2:
                self.current_difficulty = 2
                self.new(2)  # Easy
            elif key == pg.K_3:
                self.current_difficulty = 3
                self.new(3)  # Normal
            elif key == pg.K_4:
                self.current_difficulty = 4
                self.new(4)  # Hard
        
        # Game over/victory screen controls
        if self.state in [GAME_OVER, VICTORY]:
            if key == pg.K_m:
                # Return to main menu
                self.state = MENU
                self.all_sprites.empty()
            elif key == pg.K_q:
                # Quit the game
                self.running = False
        
        # Handle tool selection in planning phase
        if self.state == PLANNING:
            if key == pg.K_b:  # 'b' key
                print("B key pressed - selecting barrier")
                self.mouse_controller.toolbar.select_tool(BARRIER)
            elif key == pg.K_v:  # 'v' key
                print("V key pressed - selecting vegetation")
                self.mouse_controller.toolbar.select_tool(VEGETATION)
            elif key == pg.K_r:  # 'r' key
                print("R key pressed - selecting remove")
                self.mouse_controller.toolbar.select_tool("remove")

    def quit(self):
        """Clean up and quit the game"""
        self.sound_manager.stop_music()
        pg.quit()
        sys.exit()

async def main():
    game = Game()
    await game.run()

asyncio.run(main())