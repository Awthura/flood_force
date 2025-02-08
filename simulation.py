import pygame as pg
from settings import *

class WaterSimulation:
    def __init__(self, game, grid):
        self.game = game
        self.grid = grid
        self.river_x = self.grid.width // 3
        self.game_ended = False

    def update(self):
        """Single evaluation when entering weather phase."""
        if self.game.state != WEATHER or self.game_ended:
            return
            
        # One-time flood evaluation
        self.process_flooding()
        self.check_game_state()

    def process_flooding(self):
        """Process flooding from the river outwards."""
        # First reset all flooding
        self.reset_all_flooding()
        
        # Then process each row
        for y in range(self.grid.height):
            # Process right side
            self.flood_direction(y, range(self.river_x + 1, self.grid.width), "right")
            
            # Process left side
            self.flood_direction(y, range(self.river_x - 1, -1, -1), "left")

    def reset_all_flooding(self):
        """Reset all flood states at the start."""
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                tile = self.grid.tiles[y][x]
                if tile.tile_type == WATER and hasattr(tile, 'was_land'):
                    tile.tile_type = tile.original_type
                    tile.water_level = 0.0
                    tile.update_appearance()

    def flood_direction(self, y, x_range, direction):
        """Handle flooding in one direction."""
        tree_count = 0
        protected = False
        
        for x in x_range:
            tile = self.grid.tiles[y][x]
            
            # Skip original river tiles
            if tile.tile_type == WATER and not hasattr(tile, 'was_land'):
                continue
                
            # Once protected, remaining tiles in this direction are safe
            if protected:
                continue
                
            # Check for barrier
            if self.has_barrier(x, y, direction):
                protected = True
                continue
                
            # Check for trees
            if self.has_tree(tile):
                tree_count += 1
                if tree_count == 2:
                    protected = True
                    continue
            else:
                tree_count = 0
                
            # Only flood if not protected
            if not protected:
                self.flood_tile(tile)

    def has_barrier(self, x, y, direction):
        """Check for barrier protection."""
        check_x = x - 1 if direction == "right" else x + 1
        adjacent = self.grid.get_tile(check_x, y)
        
        if not adjacent or not adjacent.has_infrastructure:
            return False
            
        infra = next((i for i in self.game.infrastructure if i.tile == adjacent), None)
        return infra and infra.infra_type == BARRIER

    def has_tree(self, tile):
        """Check if tile has vegetation."""
        if not tile.has_infrastructure:
            return False
            
        infra = next((i for i in self.game.infrastructure if i.tile == tile), None)
        return infra and infra.infra_type == VEGETATION

    def flood_tile(self, tile):
        """Convert a tile to flooded state."""
        if tile.tile_type in [LAND, RIVER_BANK]:
            if not hasattr(tile, 'original_type'):
                tile.original_type = tile.tile_type
            tile.was_land = True
            tile.tile_type = WATER
            tile.water_level = 1.0
            tile.update_appearance()

    def check_game_state(self):
        """Check if any houses are flooded."""
        if self.game_ended:
            return
            
        houses_flooded = False
        
        # Debug print
        print("\nChecking house states:")
        
        # Check each house's state
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                tile = self.grid.tiles[y][x]
                if getattr(tile, 'is_house', False):
                    is_flooded = tile.tile_type == WATER
                    print(f"House at ({x}, {y}): {'Flooded' if is_flooded else 'Safe'}")
                    if is_flooded:
                        houses_flooded = True
                        break
                        
        # Update game state based on house status
        if houses_flooded:
            print("Game Over: House flooded!")
            self.game.state = GAME_OVER
        else:
            print("Victory! All houses protected!")
            self.game.state = VICTORY
            
        self.game_ended = True