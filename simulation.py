import pygame as pg
import random
from settings import *

class WaterSimulation:
    def __init__(self, game, grid):
        """Initialize water simulation with game and grid references."""
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
        river_x = self.grid.width // 3
        
        for y in range(self.grid.height):
            # Process tiles right of the river
            for x in range(river_x + 2, self.grid.width):
                tile = self.grid.tiles[y][x]
                if not self.is_protected(tile, "right"):
                    self.apply_rain(tile, current_weather['rain'])
            
            # Process tiles left of the river
            for x in range(river_x - 2, -1, -1):
                tile = self.grid.tiles[y][x]
                if not self.is_protected(tile, "left"):
                    self.apply_rain(tile, current_weather['rain'])

    def apply_rain(self, tile, rain_amount):
        """Apply rain effects to a single tile."""
        if tile.tile_type == WATER and not hasattr(tile, 'was_land'):
            return  # Skip original river tiles
            
        tile.water_level = min(1.0, tile.water_level + rain_amount)
        if tile.water_level >= FLOOD_THRESHOLD and tile.tile_type == LAND:
            tile.was_land = True
            tile.tile_type = WATER
            print(f"Tile at ({tile.x}, {tile.y}) flooded by rain")
        tile.update_appearance()

    def simulate_water_flow(self):
        """Simulate water flowing from river in both directions."""
        river_x = self.grid.width // 3
        
        for y in range(self.grid.height):
            # Simulate rightward flow
            water_level = 1.0
            for x in range(river_x + 2, self.grid.width):
                tile = self.grid.tiles[y][x]
                if self.is_protected(tile, "right"):
                    water_level = 0.0
                    if tile.tile_type == WATER and hasattr(tile, 'was_land'):
                        tile.tile_type = LAND
                        tile.water_level = 0.0
                else:
                    tile.water_level = water_level
                    if tile.water_level >= FLOOD_THRESHOLD and tile.tile_type == LAND:
                        tile.was_land = True
                        tile.tile_type = WATER
                
                tile.update_appearance()
                water_level *= 0.95  # Slightly reduced decay rate
            
            # Simulate leftward flow (similar logic)
            water_level = 1.0
            for x in range(river_x - 2, -1, -1):
                tile = self.grid.tiles[y][x]
                if self.is_protected(tile, "left"):
                    water_level = 0.0
                    if tile.tile_type == WATER and hasattr(tile, 'was_land'):
                        tile.tile_type = LAND
                        tile.water_level = 0.0
                else:
                    tile.water_level = water_level
                    if tile.water_level >= FLOOD_THRESHOLD and tile.tile_type == LAND:
                        tile.was_land = True
                        tile.tile_type = WATER
                
                tile.update_appearance()
                water_level *= 0.95  # Consistent decay rate

    def is_protected(self, tile, direction):
        """Check if a tile is protected from flooding."""
        def has_vegetation(check_tile):
            """Helper to check if a tile has vegetation."""
            if check_tile and check_tile.has_infrastructure:
                infra = next((sprite for sprite in self.game.infrastructure 
                            if sprite.tile == check_tile), None)
                return infra and infra.infra_type == VEGETATION
            return False
        
        def has_barrier(check_tile):
            """Helper to check if a tile has a barrier."""
            if check_tile and check_tile.has_infrastructure:
                infra = next((sprite for sprite in self.game.infrastructure 
                            if sprite.tile == check_tile), None)
                return infra and infra.infra_type == BARRIER
            return False

        # Determine which tiles to check based on flow direction
        if direction == "right":
            check_x = tile.x - 1
            far_check_x = tile.x - 2
        else:
            check_x = tile.x + 1
            far_check_x = tile.x + 2

        # Check for barrier protection first
        adjacent_tile = self.grid.get_tile(check_x, tile.y)
        if adjacent_tile and adjacent_tile.tile_type == RIVER_BANK and has_barrier(adjacent_tile):
            return True

        # Check for consecutive vegetation protection
        adjacent_tile = self.grid.get_tile(check_x, tile.y)
        far_tile = self.grid.get_tile(far_check_x, tile.y)
        
        if has_vegetation(adjacent_tile) and has_vegetation(far_tile):
            # All tiles beyond consecutive vegetation are protected
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