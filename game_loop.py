import pygame as pg
from settings import *

class GameLoop:
    def __init__(self, game):
        self.game = game
        self.level = 1
        self.score = 0
        self.high_score = 0
        self.reset_level_stats()

    def reset_level_stats(self):
        """Reset statistics for new level"""
        self.flood_percentage = 0
        self.resources_spent = 0
        self.infrastructure_built = 0
        self.turns_taken = 0

    def update(self):
        """Main game loop update"""
        if self.game.state == PLANNING:
            self.update_planning()
        elif self.game.state == WEATHER:
            self.update_weather()
        elif self.game.state == ASSESSMENT:
            self.update_assessment()

    def update_planning(self):
        """Update planning phase"""
        # Track resources spent
        current_resources = self.game.resources
        self.resources_spent = STARTING_RESOURCES - current_resources
        
        # Track infrastructure built
        self.infrastructure_built = len(self.game.infrastructure)

    def update_weather(self):
        """Update weather phase"""
        self.turns_taken = self.game.water_sim.turn_counter
        
        # Only check for game over after simulation is complete
        if self.turns_taken >= MAX_TURNS:
            self.calculate_results()
            if self.flood_percentage > MAX_FLOOD_PERCENTAGE:
                self.game.state = GAME_OVER
            else:
                self.game.state = ASSESSMENT

    def update_assessment(self):
        """Update assessment phase"""
        # Already calculated in calculate_results()
        pass

    def calculate_results(self):
        """Calculate level results and scoring"""
        # Calculate flood percentage
        flood_tiles = 0
        total_land_tiles = 0
        
        for row in self.game.grid.tiles:
            for tile in row:
                if tile.tile_type == LAND:
                    total_land_tiles += 1
                    if tile.water_level > FLOOD_THRESHOLD:
                        flood_tiles += 1
        
        self.flood_percentage = (flood_tiles / total_land_tiles * 100 
                               if total_land_tiles > 0 else 0)

        # Calculate level score
        flood_score = max(0, 100 - self.flood_percentage)  # 0-100 points for flood prevention
        resource_score = (self.game.resources / STARTING_RESOURCES) * 50  # 0-50 points for resource management
        time_score = ((MAX_TURNS - self.turns_taken) / MAX_TURNS) * 50  # 0-50 points for speed
        
        level_score = int(flood_score + resource_score + time_score)
        self.score += level_score

        # Check win/lose conditions
        if self.flood_percentage > MAX_FLOOD_PERCENTAGE:
            self.game.state = GAME_OVER
        else:
            self.game.state = ASSESSMENT
            # Update high score if applicable
            self.high_score = max(self.high_score, self.score)

    def start_next_level(self):
        """Prepare and start next level"""
        self.level += 1
        self.reset_level_stats()
        
        # Increase difficulty with each level
        global MAX_TURNS, STARTING_RESOURCES
        MAX_TURNS = max(5, MAX_TURNS - 1)  # Reduce available turns
        STARTING_RESOURCES += 200  # Give more resources for harder levels
        
        # Reset game state
        self.game.new()
        self.game.state = PLANNING

    def get_level_stats(self):
        """Get current level statistics"""
        return {
            'level': self.level,
            'flood_percentage': self.flood_percentage,
            'resources_spent': self.resources_spent,
            'infrastructure_built': self.infrastructure_built,
            'turns_taken': self.turns_taken,
            'score': self.score,
            'high_score': self.high_score
        }

    # In game_loop.py
    def handle_input(self, key):
        """Handle keyboard input for game flow and state transitions"""
        print(f"GameLoop handling input. Current state: {self.game.state}")  # Debug print
        if key == pg.K_SPACE:
            if self.game.state == MENU:
                print("Starting new game from menu")  # Debug print
                self.game.new()
            elif self.game.state == PLANNING:
                print("Transitioning to weather phase")  # Debug print
                self.game.state = WEATHER
            elif self.game.state == ASSESSMENT:
                print("Starting next level")  # Debug print
                self.start_next_level()
        elif key == pg.K_r and self.game.state == GAME_OVER:
            print("Restarting game")  # Debug print
            self.game.new()