import pygame as pg
from settings import *

class WaterSimulation:
    def __init__(self, game, grid):
        self.game = game
        self.grid = grid
        self.game_ended = False
        self.barrier_trees = set()  # New set to track barrier trees

    def process_flooding(self):
        """Process flooding from curved river outwards."""
        # Clear previous barrier trees
        self.barrier_trees.clear()
        
        # Process each row
        for y in range(self.grid.height):
            # Get river center for this row
            river_center = self.grid.get_river_center(y)
            
            # Process right side - start from after river bank
            self.flood_direction(y, range(river_center + 2, self.grid.width), "right")
            # Process left side - start from before river bank
            self.flood_direction(y, range(river_center - 1, -1, -1), "left")

    def find_river_center(self, y):
        """Find the center of the river at given y coordinate."""
        # Look for middle of water tiles in this row
        water_tiles = []
        for x in range(self.grid.width):
            if self.grid.tiles[y][x].tile_type == WATER:
                water_tiles.append(x)
        
        if water_tiles:
            return sum(water_tiles) // len(water_tiles)
        return self.grid.width // 3  # Fallback to default position

    def check_tree_barrier(self, tile):
        """Check if a tree becomes a barrier due to adjacent trees."""
        if not self.has_tree(tile):
            return False
        
        # Check all 8 adjacent tiles
        adjacent_coords = [
            (tile.x - 1, tile.y), (tile.x + 1, tile.y),  # left, right
            (tile.x, tile.y - 1), (tile.x, tile.y + 1),  # up, down
            (tile.x - 1, tile.y - 1), (tile.x + 1, tile.y - 1),  # diagonal up
            (tile.x - 1, tile.y + 1), (tile.x + 1, tile.y + 1)   # diagonal down
        ]
        
        # Count adjacent trees
        adjacent_tree_count = sum(
            1 for x, y in adjacent_coords 
            if (0 <= x < self.grid.width and 0 <= y < self.grid.height) 
            and self.has_tree(self.grid.tiles[y][x])
        )
        
        # If it becomes a barrier, add to barrier trees set
        is_barrier = adjacent_tree_count >= 3
        if is_barrier:
            self.barrier_trees.add(tile)
        
        return is_barrier

    def flood_direction(self, y, x_range, direction):
        """Handle flooding in ladder pattern with tree barrier logic."""
        steps_from_river = 0
        flooded_direction = set()  # Track which tiles have been flooded in this direction
        
        for x in x_range:
            # Check for barriers first
            if self.has_barrier(x, y, direction):
                return  # Still stop at barriers
            
            tile = self.grid.tiles[y][x]
            
            # Skip original river tiles
            if tile.tile_type == WATER and not hasattr(tile, 'was_land'):
                continue
            
            # Check if tree acts as a barrier
            if self.check_tree_barrier(tile):
                return
            
            # Only process land and river bank tiles
            if tile.tile_type in [LAND, RIVER_BANK]:
                # Flood the current tile
                self.flood_tile(tile)
                flooded_direction.add((x, y))
                
                # If this is the first step, flood adjacent tiles
                if steps_from_river == 0:
                    adjacent_x = x - 1 if direction == "right" else x + 1
                    if 0 <= adjacent_x < self.grid.width:
                        adjacent_tile = self.grid.tiles[y][adjacent_x]
                        if not self.check_tree_barrier(adjacent_tile):
                            self.flood_tile(adjacent_tile)
                            flooded_direction.add((adjacent_x, y))
                
                # Apply vertical spread for subsequent steps
                if steps_from_river > 0:
                    self.apply_vertical_spread(x, y, steps_from_river, flooded_direction, direction)
                
                steps_from_river += 1

    def apply_vertical_spread(self, x, y, distance, flooded_direction, original_direction):
        """Apply vertical flooding equally upwards and downwards."""
        spread = min(distance, 4)  # Limit the spread to a maximum of 8 tiles
        
        # Spread both upwards and downwards
        for i in range(1, spread + 1):
            # Spread upwards
            if y - i >= 0:
                tile = self.grid.tiles[y - i][x]
                # Only spread if not already flooded in this direction and no tree barrier
                if self.check_tree_barrier(tile):
                    break
                if (x, y - i) not in flooded_direction:
                    # Check that we don't spread back in the opposite direction
                    neighbor_left = self.grid.get_tile(x - 1, y - i)
                    neighbor_right = self.grid.get_tile(x + 1, y - i)
                    
                    can_spread = (
                        (original_direction == "right" and 
                        (not neighbor_left or neighbor_left.tile_type != WATER)) or
                        (original_direction == "left" and 
                        (not neighbor_right or neighbor_right.tile_type != WATER))
                    )
                    
                    if can_spread:
                        self.flood_tile(tile)
                        flooded_direction.add((x, y - i))

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
        
        # Clear barrier trees
        self.barrier_trees.clear()

    def has_barrier(self, x, y, direction):
        """Check for barrier protection with curved river."""
        # Adjust check_x based on river curve
        river_center = self.grid.get_river_center(y)
        
        # Check appropriate position based on direction
        if direction == "right":
            check_x = x - 1  # Check to the left
        else:
            check_x = x + 1  # Check to the right
        
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

    def get_barrier_trees(self):
        """Return the set of trees acting as barriers."""
        return self.barrier_trees

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