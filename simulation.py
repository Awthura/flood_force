import pygame as pg
from settings import *

class WaterSimulation:
    def __init__(self, game, grid):
        self.game = game
        self.grid = grid
        self.river_x = self.grid.width // 3  # River position
        self.game_ended = False

    def process_flooding(self):
        """Process flooding from the river outwards."""
        # Reset all flooding first
        self.reset_all_flooding()
        
        # Process each row
        for y in range(self.grid.height):
            # Right side flooding
            self.flood_direction(y, range(self.river_x + 2, self.grid.width), "right")
            # Left side flooding
            self.flood_direction(y, range(self.river_x - 1, -1, -1), "left")

    def flood_direction(self, y, x_range, direction):
        """Handle flooding in ladder pattern with barriers."""
        steps_from_river = 0  # Track distance from the river
        
        for x in x_range:
            # Check for barriers
            if self.has_barrier(x, y, direction):
                return  # Stop flooding this row if a barrier is encountered
            
            tile = self.grid.tiles[y][x]
            
            # Skip river tiles and check for vegetation
            if tile.tile_type == WATER and not hasattr(tile, 'was_land'):
                continue
            if self.has_tree(tile):
                return  # Stop flooding at vegetation
            
            # Only process land and river bank tiles
            if tile.tile_type in [LAND, RIVER_BANK]:
                # Flood the current tile
                self.flood_tile(tile)
                
                # If this is the first step, flood adjacent tiles on the same row
                if steps_from_river == 0:
                    # Flood the tile to the left or right of the initial tile
                    adjacent_x = x - 1 if direction == "right" else x + 1
                    if 0 <= adjacent_x < self.grid.width:
                        adjacent_tile = self.grid.tiles[y][adjacent_x]
                        if not self.has_tree(adjacent_tile):
                            self.flood_tile(adjacent_tile)
                
                # Apply vertical spread for subsequent steps
                if steps_from_river > 0:
                    self.apply_vertical_spread(x, y, steps_from_river)
                
                steps_from_river += 1

    def apply_vertical_spread(self, x, y, distance):
        """Apply vertical flooding equally upwards and downwards."""
        spread = min(distance, 8)  # Limit the spread to a maximum of 8 tiles
        
        # Spread both upwards and downwards
        for i in range(1, spread + 1):
            # Spread downwards
            # if y + i < self.grid.height:
            #     tile = self.grid.tiles[y + i][x]
            #     if not self.has_tree(tile):
            #         self.flood_tile(tile)
            
            # Spread upwards
            if y - i >= 0:
                tile = self.grid.tiles[y - i][x]
                if not self.has_tree(tile):
                    self.flood_tile(tile)

    def update(self):
        """Single evaluation when entering weather phase."""
        if self.game.state != WEATHER or self.game_ended:
            return
            
        # One-time flood evaluation
        self.process_flooding()
        self.check_game_state()

    def reset_all_flooding(self):
        """Reset all flood states at the start."""
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                tile = self.grid.tiles[y][x]
                if tile.tile_type == WATER and hasattr(tile, 'was_land'):
                    tile.tile_type = tile.original_type
                    tile.water_level = 0.0
                    tile.update_appearance()

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
        print("\nChecking house states:")
        
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                tile = self.grid.tiles[y][x]
                if getattr(tile, 'is_house', False):
                    is_flooded = tile.tile_type == WATER
                    print(f"House at ({x}, {y}): {'Flooded' if is_flooded else 'Safe'}")
                    if is_flooded:
                        houses_flooded = True
                        break
                        
        if houses_flooded:
            print("Game Over: House flooded!")
            self.game.state = GAME_OVER
        else:
            print("Victory! All houses protected!")
            self.game.state = VICTORY
            
        self.game_ended = True