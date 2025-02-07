import pygame as pg
import random
from settings import *

class WaterSimulation:
    def __init__(self, game, grid):
        """Initialize water simulation with game and grid references.
        
        The simulation manages water flow from the river (located at 1/3 of grid width)
        eastward, applying protection rules from barriers and vegetation.
        """
        self.game = game
        self.grid = grid
        
        # Define weather phases for varying rain intensity
        self.weather_phases = [
            {'rain': 0.2, 'duration': 5},  # Light rain
            {'rain': 0.3, 'duration': 3},  # Medium rain
            {'rain': 0.4, 'duration': 2}   # Heavy rain
        ]
        self.current_phase = 0

    def update(self):
        """Main update loop for weather simulation."""
        if self.game.state == WEATHER:
            self.simulate_rain()
            self.simulate_water_flow()
            self.check_flooding()

    def simulate_rain(self):
        """Add water from rainfall and check for flooding."""
        current_weather = self.weather_phases[self.current_phase]
        river_x = self.grid.width // 3  # Calculate river position
        
        for y in range(self.grid.height):
            for x in range(river_x + 1, self.grid.width):  # Start right of river
                tile = self.grid.tiles[y][x]
                
                if not self.is_protected(tile):
                    # Apply rain effect
                    rain_amount = current_weather['rain']
                    tile.water_level = min(1.0, tile.water_level + rain_amount)
                    
                    # Check for flooding
                    if tile.water_level >= FLOOD_THRESHOLD and tile.tile_type == LAND:
                        tile.was_land = True
                        tile.tile_type = WATER
                        print(f"Tile at ({x}, {y}) flooded by rain")
                    
                    tile.update_appearance()

    def simulate_water_flow(self):
        """Simulate water flowing from west to east, starting from the river."""
        river_x = self.grid.width // 3
        
        for y in range(self.grid.height):
            water_level = 1.0  # Start with full water at river
            
            for x in range(river_x + 1, self.grid.width):
                tile = self.grid.tiles[y][x]
                
                if self.is_protected(tile):
                    # Protected tiles become/stay dry
                    water_level = 0.0
                    if tile.tile_type == WATER and hasattr(tile, 'was_land'):
                        tile.tile_type = LAND
                        tile.water_level = 0.0
                        print(f"Protected tile at ({x}, {y}) restored to land")
                else:
                    # Unprotected tiles receive water flow
                    tile.water_level = water_level
                    water_level *= 0.9  # Water level gradually decreases
                    
                    if tile.water_level >= FLOOD_THRESHOLD and tile.tile_type == LAND:
                        tile.was_land = True
                        tile.tile_type = WATER
                        print(f"Tile at ({x}, {y}) flooded by water flow")
                
                tile.update_appearance()

    def is_protected(self, tile):
        """Check if a tile is protected by barriers or vegetation.
        
        A tile is protected if:
        1. There is a barrier directly to its left
        2. There are two consecutive vegetation tiles to its left
        """
        # Check for barrier protection
        left_tile = self.grid.get_tile(tile.x - 1, tile.y)
        if left_tile and left_tile.has_infrastructure:
            left_infra = next((sprite for sprite in self.game.infrastructure 
                             if sprite.tile == left_tile), None)
            if left_infra and left_infra.infra_type == BARRIER:
                return True

        # Check for consecutive vegetation protection
        if left_tile and left_tile.has_infrastructure:
            far_left_tile = self.grid.get_tile(tile.x - 2, tile.y)
            if far_left_tile and far_left_tile.has_infrastructure:
                left_infra = next((sprite for sprite in self.game.infrastructure 
                                 if sprite.tile == left_tile), None)
                far_left_infra = next((sprite for sprite in self.game.infrastructure 
                                     if sprite.tile == far_left_tile), None)
                if (left_infra and left_infra.infra_type == VEGETATION and 
                    far_left_infra and far_left_infra.infra_type == VEGETATION):
                    return True
        
        return False

    def check_flooding(self):
        """Check game end conditions based on house safety and flood percentage."""
        flood_count = 0
        total_land_tiles = 0
        houses_flooded = False

        # Check house status
        for row in self.grid.tiles:
            for tile in row:
                if hasattr(tile, 'is_house') and tile.is_house:
                    if tile.tile_type == WATER:
                        houses_flooded = True
                        print(f"House flooded at ({tile.x}, {tile.y})")
                        break

        # Calculate flood percentage
        for row in self.grid.tiles:
            for tile in row:
                if tile.tile_type == LAND or hasattr(tile, 'was_land'):
                    total_land_tiles += 1
                    if tile.tile_type == WATER and hasattr(tile, 'was_land'):
                        flood_count += 1

        # Update game state
        self.game.flood_percentage = (flood_count / total_land_tiles * 100) if total_land_tiles > 0 else 0
        print(f"Current flood percentage: {self.game.flood_percentage}%")
        
        if houses_flooded or self.game.flood_percentage > MAX_FLOOD_PERCENTAGE:
            print("Game Over: Houses flooded or flood percentage too high")
            self.game.state = GAME_OVER
        elif self.game.flood_percentage <= MAX_FLOOD_PERCENTAGE:
            print("Victory achieved!")
            self.game.state = VICTORY