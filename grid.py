import pygame as pg
from settings import *
from sprites import Tile
import random

class Grid:
    def __init__(self, game, width, height):
        self.game = game
        self.width = width  # Number of tiles wide
        self.height = height  # Number of tiles high
        self.tiles = [[None for x in range(width)] for y in range(height)]
        self.tile_dict = {}  # For quick position to tile lookup
        self.initialize_grid()

    def initialize_grid(self):
        """Create initial grid layout with default tiles"""
        # Create basic terrain layout
        for y in range(self.height):
            for x in range(self.width):
                # Example: Create a river running through the middle
                if self.width // 3 <= x <= self.width // 3 + 1:
                    tile_type = WATER
                else:
                    tile_type = LAND
                self.create_tile(x, y, tile_type)

    def create_tile(self, x, y, tile_type):
        """Create a new tile at the specified grid position"""
        tile = Tile(self.game, x, y, tile_type)
        self.tiles[y][x] = tile
        self.tile_dict[(x, y)] = tile
        return tile

    def get_tile(self, x, y):
        """Get tile at grid coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def get_neighbors(self, tile):
        """Get all adjacent tiles"""
        x, y = tile.x, tile.y
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # NSEW
        
        for dx, dy in directions:
            neighbor = self.get_tile(x + dx, y + dy)
            if neighbor:
                neighbors.append(neighbor)
        
        return neighbors

    def grid_to_pixel(self, grid_x, grid_y):
        """Convert grid coordinates to pixel coordinates"""
        return (grid_x * TILESIZE, grid_y * TILESIZE)

    def pixel_to_grid(self, pixel_x, pixel_y):
        """Convert pixel coordinates to grid coordinates"""
        return (pixel_x // TILESIZE, pixel_y // TILESIZE)

    def is_valid_tile(self, x, y):
        """Check if the given coordinates are within grid bounds"""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tiles_in_range(self, center_tile, range_):
        """Get all tiles within a certain range of a center tile"""
        tiles = []
        cx, cy = center_tile.x, center_tile.y
        
        for y in range(cy - range_, cy + range_ + 1):
            for x in range(cx - range_, cx + range_ + 1):
                if self.is_valid_tile(x, y):
                    tiles.append(self.tiles[y][x])
        
        return tiles

    def update_water_flow(self):
        """Update water levels based on neighboring tiles"""
        # Create a copy of current water levels
        new_water_levels = {}
        
        # Calculate water distribution
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile.water_level > 0:
                    neighbors = self.get_neighbors(tile)
                    flowing_water = 0
                    
                    # Calculate water flow to lower elevation neighbors
                    for neighbor in neighbors:
                        if neighbor.elevation < tile.elevation:
                            flowing_water += min(
                                tile.water_level * 0.2,  # 20% flow rate
                                1 - neighbor.water_level  # Available space
                            )
                    
                    # Update water levels
                    new_level = tile.water_level - flowing_water
                    new_water_levels[(x, y)] = new_level
                    
                    # Distribute to neighbors
                    flow_per_neighbor = flowing_water / len(neighbors) if neighbors else 0
                    for neighbor in neighbors:
                        pos = (neighbor.x, neighbor.y)
                        new_water_levels[pos] = new_water_levels.get(pos, 0) + flow_per_neighbor
        
        # Apply new water levels
        for (x, y), level in new_water_levels.items():
            self.tiles[y][x].update_water_level(level)
    
    def place_houses(self):
        """Place 3 random houses on land tiles, avoiding river bank tiles.
        
        This method finds safe locations for houses by:
        1. Identifying land tiles that are at least 2 tiles away from the river
        2. Randomly selecting 3 of these tiles to place houses
        3. Marking the selected tiles as house locations
        """
        available_tiles = []
        river_x = self.width // 3  # River position is one-third from the left
        
        # Collect all valid land tiles that are at least 2 tiles away from the river
        for y in range(self.height):
            for x in range(river_x + 2, self.width):  # Start 2 tiles right of river
                tile = self.tiles[y][x]  # Fixed: Removed extra self.grid reference
                if tile.tile_type == LAND:
                    available_tiles.append(tile)
        
        # Only place houses if we have enough valid tiles
        if len(available_tiles) >= 3:
            house_tiles = random.sample(available_tiles, 3)
            for tile in house_tiles:
                tile.is_house = True
                tile.update_appearance()
                print(f"Placed house at ({tile.x}, {tile.y})")  # Debug info
        else:
            print("Warning: Not enough valid tiles for house placement")

    def apply_infrastructure_effects(self):
        """Update grid based on infrastructure effects"""
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile.has_infrastructure:
                    infra = next((sprite for sprite in self.game.infrastructure 
                                if sprite.tile == tile), None)
                    if infra:
                        # Apply infrastructure effects
                        if infra.infra_type == BARRIER:
                            # Reduce water level on protected side
                            protected_tile = self.get_tile(x + 1, y)  # Example: protects right side
                            if protected_tile:
                                protected_tile.update_water_level(-0.2 * infra.efficiency)
                        elif infra.infra_type == VEGETATION:
                            # Increase water absorption
                            tile.update_water_level(-0.1 * infra.efficiency)

    