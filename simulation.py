import pygame as pg
import random
from settings import *

class WaterSimulation:
    def __init__(self, game, grid):
        self.game = game
        self.grid = grid
        self.rain_intensity = 0
        self.turn_counter = 0
        self.weather_phases = [
            {'rain': 0.1, 'duration': 3},    # Light rain
            {'rain': 0.3, 'duration': 2},    # Medium rain
            {'rain': 0.5, 'duration': 1},    # Heavy rain
        ]
        self.current_phase = 0

    def update(self):
        """Main update loop for water simulation"""
        if self.game.state == WEATHER:
            self.turn_counter += 1
            self.simulate_rain()
            self.simulate_water_flow()
            self.check_flooding()

    def simulate_rain(self):
        """Add water to tiles based on current rain intensity"""
        current_weather = self.weather_phases[self.current_phase]
        
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                tile = self.grid.tiles[y][x]
                # Add water based on rain intensity and randomness
                rain_amount = current_weather['rain'] * random.uniform(0.8, 1.2)
                tile.update_water_level(rain_amount)

        # Check if we should move to next weather phase
        if self.turn_counter % current_weather['duration'] == 0:
            self.current_phase = (self.current_phase + 1) % len(self.weather_phases)

    def simulate_water_flow(self):
        """Simulate water flowing between tiles"""
        # Create a buffer for new water levels
        new_water_levels = {}
        
        # Calculate water distribution
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                tile = self.grid.tiles[y][x]
                if tile.water_level > 0:
                    self.distribute_water(tile, new_water_levels)
        
        # Apply new water levels
        for pos, level in new_water_levels.items():
            x, y = pos
            self.grid.tiles[y][x].update_water_level(level - self.grid.tiles[y][x].water_level)

    def distribute_water(self, tile, new_water_levels):
        """Calculate water distribution for a single tile"""
        neighbors = self.grid.get_neighbors(tile)
        if not neighbors:
            return

        # Get current position's water level
        current_pos = (tile.x, tile.y)
        current_level = new_water_levels.get(current_pos, tile.water_level)

        for neighbor in neighbors:
            neighbor_pos = (neighbor.x, neighbor.y)
            neighbor_level = new_water_levels.get(neighbor_pos, neighbor.water_level)

            # Calculate water flow based on height difference and infrastructure
            height_diff = tile.elevation - neighbor.elevation
            if height_diff > 0:
                # Water flows downhill
                flow_amount = min(
                    current_level * 0.3,  # Max 30% can flow at once
                    height_diff * 0.5,    # Height difference factor
                    1.0 - neighbor_level  # Can't exceed maximum water level
                )
                
                # Reduce flow if infrastructure present
                if neighbor.has_infrastructure:
                    infra = next((sprite for sprite in self.game.infrastructure 
                                if sprite.tile == neighbor), None)
                    if infra:
                        flow_amount *= (1 - infra.efficiency)

                # Update water levels
                new_water_levels[current_pos] = current_level - flow_amount
                new_water_levels[neighbor_pos] = neighbor_level + flow_amount

    def check_flooding(self):
        """Check for flooding conditions and update game state"""
        flood_count = 0
        total_tiles = 0
        
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                tile = self.grid.tiles[y][x]
                if tile.tile_type == LAND:
                    total_tiles += 1
                    if tile.water_level > FLOOD_THRESHOLD:
                        flood_count += 1
        
        # Calculate flood percentage
        flood_percentage = (flood_count / total_tiles) * 100 if total_tiles > 0 else 0
        
        # Update game state based on flooding
        if flood_percentage > MAX_FLOOD_PERCENTAGE:
            self.game.state = GAME_OVER
        elif self.turn_counter >= MAX_TURNS:
            self.game.state = ASSESSMENT

    def reset(self):
        """Reset simulation to initial state"""
        self.turn_counter = 0
        self.current_phase = 0
        self.clear_water()

    def clear_water(self):
        """Remove all water from non-water tiles"""
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                tile = self.grid.tiles[y][x]
                if tile.tile_type != WATER:
                    tile.water_level = 0