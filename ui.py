import pygame as pg
import os
from settings import *

import pygame as pg
import os
from settings import *

class UI:
    def __init__(self, game):
        self.game = game
        self.font_big = pg.font.Font(None, 64)
        self.font_med = pg.font.Font(None, 32)
        self.font_small = pg.font.Font(None, 24)
        # Load start screen
        try:
            original_image = pg.image.load(os.path.join("resources", "start_screen.png")).convert_alpha()
            
            # Calculate scaling while preserving aspect ratio
            image_ratio = original_image.get_width() / original_image.get_height()
            screen_ratio = WIDTH / HEIGHT
            
            if screen_ratio > image_ratio:
                # Screen is wider than image - fit to height
                new_height = HEIGHT
                new_width = int(HEIGHT * image_ratio)
            else:
                # Screen is taller than image - fit to width
                new_width = WIDTH
                new_height = int(WIDTH / image_ratio)
                
            self.start_screen = pg.transform.scale(original_image, (new_width, new_height))
            
            # Calculate position to center the image
            self.start_screen_x = (WIDTH - new_width) // 2
            self.start_screen_y = (HEIGHT - new_height) // 2
            
        except Exception as e:
            print(f"Failed to load start screen image: {e}")
            self.start_screen = None
            self.start_screen_x = 0
            self.start_screen_y = 0

    def draw_menu(self):
        """Draw the main menu screen"""
        # Fill background with black
        self.game.screen.fill(BLACK)
        
        if self.start_screen:
            # Draw the custom start screen image centered
            self.game.screen.blit(self.start_screen, (self.start_screen_x, self.start_screen_y))
        else:
            # Fallback to text-based menu if image fails to load
            title = self.font_big.render("FLOOD FORCE", True, WHITE)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.game.screen.blit(title, title_rect)

        # Difficulty selection instructions
        difficulty_text = [
            "Select Difficulty:",
            "1 - Tutorial (Easier)",
            "2 - Easy",
            "3 - Normal",
            "4 - Hard"
        ]
        
        for i, text in enumerate(difficulty_text):
            color = WHITE if i > 0 else YELLOW  # Highlight the first text
            diff_render = self.font_med.render(text, True, color)
            diff_rect = diff_render.get_rect(
                center=(WIDTH // 2, 
                        HEIGHT * 2 // 3 + i * 40)
            )
            self.game.screen.blit(diff_render, diff_rect)

    def draw(self):
        """Draw the appropriate UI elements based on game state"""
        current_state = self.game.state
        
        if current_state == MENU:
            self.draw_menu()
        elif current_state in [PLANNING, WEATHER]:
            self.draw_game_ui()
        elif current_state == GAME_OVER:
            self.draw_game_over()
        elif current_state == VICTORY:
            self.draw_victory()

    def draw_game_ui(self):
        """Draw the in-game UI elements"""
        # Resources display on right side
        resource_text = self.font_med.render(f"Budget: ${self.game.resources}", True, WHITE)
        text_width = resource_text.get_width()
        self.game.screen.blit(resource_text, (WIDTH - text_width - 20, 10))  # 20px padding from right edge

        # Current phase
        phase_text = self.font_med.render(f"Phase: {self.game.state.title()}", True, WHITE)
        phase_width = phase_text.get_width()
        self.game.screen.blit(phase_text, (WIDTH - phase_width - 20, 50))  # Below resource text

        # Show controls during planning phase
        if self.game.state == PLANNING:
            self._draw_controls_help()

    def _draw_controls_help(self):
        """Draw the controls help panel"""
        controls_text = [
            "Controls:",
            "B - Barrier ($100)",
            "V - Vegetation ($50)",
            "R - Remove",
            "SPACE - Start Storm"
        ]
        # Keep controls panel on right side
        for i, text in enumerate(controls_text):
            help_text = self.font_small.render(text, True, WHITE)
            self.game.screen.blit(help_text, (WIDTH - 200, 90 + i * 30))  # Start below phase text

    def draw_game_over(self):
        """Draw the game over screen"""
        # Darken the background
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.game.screen.blit(overlay, (0, 0))
        
        # Game Over message
        title = self.font_big.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.game.screen.blit(title, title_rect)

        # Restart instruction
        restart_text = self.font_med.render("Press R to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
        self.game.screen.blit(restart_text, restart_rect)

    def draw_victory(self):
        """Draw the victory screen"""
        # Darken the background
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.game.screen.blit(overlay, (0, 0))
        
        # Victory message
        title = self.font_big.render("VICTORY!", True, GREEN)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.game.screen.blit(title, title_rect)

        # Resources display
        resources_text = self.font_med.render(f"Resources Left: ${self.game.resources}", True, WHITE)
        resources_rect = resources_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.game.screen.blit(resources_text, resources_rect)

        # Continue instruction
        continue_text = self.font_med.render("Press R to Play Again", True, WHITE)
        continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT * 3 // 4))
        self.game.screen.blit(continue_text, continue_rect)