import pygame as pg
from settings import *
from sprites import Tile
import math
import random

class Grid:
    def __init__(self, game, width, height):
        self.game = game
        self.width = width
        self.height = height
        self.tiles = [[None for x in range(width)] for y in range(height)]
        self.tile_dict = {}
        self.base_river_x = self.width // 2 - 1  # Center the river
        self.river_path = self.generate_river_path()
        self.initialize_grid()

    def generate_river_path(self):
        """Generate the curved river path starting from center."""
        path = []
        current_x = self.base_river_x
        meandering_chance = 0.6
        
        for y in range(self.height):
            if y > 0:
                if random.random() < meandering_chance:
                    max_shift = 1
                    shift = random.randint(-max_shift, max_shift)
                    # Ensure river stays within reasonable bounds from center
                    current_x = max(self.width//4, min(3*self.width//4 - 4, current_x + shift))
            
            path.append(current_x)
        
        # Smooth the path
        smoothed_path = path.copy()
        for y in range(1, self.height - 1):
            smoothed_path[y] = (path[y-1] + path[y] + path[y+1]) // 3
        
        return smoothed_path

    def initialize_grid(self):
        """Create initial grid layout with meandering river."""
        # First create all land tiles
        for y in range(self.height):
            for x in range(self.width):
                self.create_tile(x, y, LAND)
        
        # Then create river and banks using the pre-generated path
        for y in range(self.height):
            river_center = self.river_path[y]
            
            # Create river (2 tiles wide)
            for x in [river_center, river_center + 1]:
                self.tiles[y][x].tile_type = WATER
            
            # Create river banks
            self.tiles[y][river_center - 1].tile_type = RIVER_BANK  # Left bank
            self.tiles[y][river_center + 2].tile_type = RIVER_BANK  # Right bank
            
            # Update appearances
            for x in [river_center - 1, river_center, river_center + 1, river_center + 2]:
                self.tiles[y][x].initialize_tile()
                self.tiles[y][x].update_appearance()

    def get_river_center(self, y):
        """Get the river center for a given row."""
        return self.river_path[y]
        
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
        """Place houses evenly on both sides of the river.
        
        Places a total of 3 houses:
        - At least 1 house on each side of the river
        - Third house randomly placed on either side
        - Houses are placed only on land tiles (not river or river bank)
        - Houses must be at least 2 tiles away from river banks
        """
        river_x = self.width // 3
        left_tiles = []
        right_tiles = []
        
        # Collect valid tiles on both sides
        for y in range(self.height):
            # Left side tiles (excluding river bank area)
            for x in range(0, river_x - 2):
                tile = self.tiles[y][x]
                if tile.tile_type == LAND:
                    left_tiles.append(tile)
            
            # Right side tiles (excluding river bank area)
            for x in range(river_x + 3, self.width):
                tile = self.tiles[y][x]
                if tile.tile_type == LAND:
                    right_tiles.append(tile)
        
        # Place houses if we have enough valid tiles
        if len(left_tiles) > 0 and len(right_tiles) > 0:
            # Place one house on each side
            left_house = random.choice(left_tiles)
            left_tiles.remove(left_house)
            left_house.is_house = True
            
            right_house = random.choice(right_tiles)
            right_tiles.remove(right_house)
            right_house.is_house = True
            
            # Place third house randomly on either side
            remaining_tiles = left_tiles + right_tiles
            if remaining_tiles:
                third_house = random.choice(remaining_tiles)
                third_house.is_house = True
            
            # Update appearances
            for tile in [left_house, right_house, third_house]:
                tile.update_appearance()
                print(f"Placed house at ({tile.x}, {tile.y})")
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

    