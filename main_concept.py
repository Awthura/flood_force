import pygame as pg
import sys
from settings import *
from sprites import *
from controller import *
from tilemap import *
from grid import Grid
from simulation import WaterSimulation
from ui import UI
from game_loop import GameLoop

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        
        # Initialize sprite groups first
        self.all_sprites = pg.sprite.Group()
        self.tiles = pg.sprite.Group()
        self.infrastructure = pg.sprite.Group()
        self.ui_elements = pg.sprite.Group()
        
        # Then initialize controllers and UI
        self.mouse_controller = MouseController(self)
        self.ui = UI(self)
        self.game_loop = GameLoop(self)
        self.state = MENU
        
        # Initialize game attributes
        self.resources = STARTING_RESOURCES
        self.score = 0
        self.flood_percentage = 0

    def load_data(self):
        # Load all game assets (images, sounds, etc.)
        pass

    def new(self):
        """Initialize a new game/level"""
        print("Starting new game...")  # Debug print
        # Clear existing sprites
        self.all_sprites.empty()
        self.tiles.empty()
        self.infrastructure.empty()
        self.ui_elements.empty()
        
        # Create grid
        self.grid = Grid(self, GRID_WIDTH, GRID_HEIGHT)
        self.water_sim = WaterSimulation(self, self.grid)
        self.resources = STARTING_RESOURCES
        self.state = PLANNING
        print(f"Game state changed to: {self.state}")  # Debug print

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def update(self):
        """Update game state"""
        self.game_loop.update()
        self.all_sprites.update()

        if self.state == PLANNING:
            self.all_sprites.update()
            self.mouse_controller.update()
        elif self.state == WEATHER:
            self.water_sim.update()
    #        self.all_sprites.update()
        elif self.state == ASSESSMENT:
            self.check_game_results()

    def new(self):
        # Initialize sprite groups
        self.all_sprites = pg.sprite.Group()
        self.tiles = pg.sprite.Group()
        self.infrastructure = pg.sprite.Group()
        self.ui_elements = pg.sprite.Group()
        
        # Create grid
        self.grid = Grid(self, GRID_WIDTH, GRID_HEIGHT)  # Add GRID_WIDTH and GRID_HEIGHT to settings.py
        self.selected_tile = None
        self.selected_tool = None
        
    
    def handle_mouse_click(self, pos):
        # Convert mouse position to grid coordinates
        grid_x, grid_y = self.grid.pixel_to_grid(*pos)
        
        if self.state == PLANNING:
            clicked_tile = self.grid.get_tile(grid_x, grid_y)
            if clicked_tile:
                if self.selected_tool:
                    self.place_infrastructure(clicked_tile)
                else:
                    self.selected_tile = clicked_tile

    def place_infrastructure(self, tile):
        if self.selected_tool and not tile.has_infrastructure:
            # Check if we have enough resources
            cost = INFRASTRUCTURE_COSTS.get(self.selected_tool, 0)  # Add to settings.py
            if self.resources >= cost:
                Infrastructure(self, tile, self.selected_tool)
                self.resources -= cost
    
    def draw(self):
        self.screen.fill(BLACK)  # Clear screen
        
        if self.state == MENU:
            self.ui.draw()
        else:
            self.all_sprites.draw(self.screen)
            self.ui.draw()
        
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                return
            if event.type == pg.KEYDOWN:
                print(f"Key pressed: {event.key}")  # Debug print
                self.handle_keypress(event.key)
            if event.type == pg.MOUSEBUTTONDOWN and self.state == PLANNING:
                self.mouse_controller.handle_click(event.pos, event.button)
            if event.type == pg.MOUSEBUTTONUP and self.state == PLANNING:
                self.mouse_controller.handle_release()

    def simulate_weather(self):
        # Implement weather and flooding simulation
        pass

    def assess_damage(self):
        # Calculate damage and update score
        pass
    
    def check_game_results(self):
        # Calculate score based on flooding and resources used
        flood_tiles = sum(1 for row in self.grid.tiles 
                         for tile in row 
                         if tile.water_level > FLOOD_THRESHOLD)
        total_land = sum(1 for row in self.grid.tiles 
                        for tile in row 
                        if tile.tile_type == LAND)
        
        self.flood_percentage = (flood_tiles / total_land * 100 
                               if total_land > 0 else 0)
        
        if self.flood_percentage > MAX_FLOOD_PERCENTAGE:
            self.state = GAME_OVER
        else:
            self.score = int((100 - self.flood_percentage) * 
                           (self.resources / STARTING_RESOURCES))

    def draw_menu(self):
        # Draw menu screen
        pass

    def draw_ui(self):
        # Draw UI elements (resources, tools, current phase)
        pass

    def handle_keypress(self, key):
        """Handle keyboard input"""
        # Let game loop handle state transitions
        self.game_loop.handle_input(key)
        
        # Handle tool selection in planning phase
        if self.state == PLANNING:
            if key == pg.K_b:
                # Select barrier tool
                for tool in self.mouse_controller.toolbar.tools:
                    if tool.tool_type == BARRIER:
                        tool.selected = True
                    else:
                        tool.selected = False
            elif key == pg.K_v:
                # Select vegetation tool
                for tool in self.mouse_controller.toolbar.tools:
                    if tool.tool_type == VEGETATION:
                        tool.selected = True
                    else:
                        tool.selected = False
            elif key == pg.K_r:
                # Select remove tool
                for tool in self.mouse_controller.toolbar.tools:
                    if tool.tool_type == "remove":
                        tool.selected = True
                    else:
                        tool.selected = False


    def quit(self):
        pg.quit()
        sys.exit()


def main():
    game = Game()
    while game.running:
        if game.state == MENU:
            game.show_start_screen()
        game.new()
        game.run()
        if game.state == GAME_OVER:
            game.show_go_screen()


if __name__ == '__main__':
    main()