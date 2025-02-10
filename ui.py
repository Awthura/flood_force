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
        self.menu_buttons = []
        # Load start screen
        try:
            original_image = pg.image.load(os.path.join("assets/resources", "start_screen.png")).convert_alpha()
            
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
        """Draw the main menu screen with clickable buttons"""
        # Fill background with black
        self.game.screen.fill(BLACK)
        
        if self.start_screen:
            self.game.screen.blit(self.start_screen, (self.start_screen_x, self.start_screen_y))
        
        # Define button dimensions
        button_width = 200
        button_height = 40
        button_spacing = 50
        start_y = HEIGHT * 2 // 3
        
        # Clear previous buttons
        self.menu_buttons = []
        
        # Create and draw buttons
        difficulty_options = [
            ("Tutorial", 1),
            ("Easy", 2),
            ("Normal", 3),
            ("Hard", 4),
            ("Quit Game", "quit")
        ]
        
        for i, (text, value) in enumerate(difficulty_options):
            button_rect = pg.Rect(
                (WIDTH - button_width) // 2,
                start_y + i * button_spacing,
                button_width,
                button_height
            )
            
            # Store button data for click detection
            self.menu_buttons.append((button_rect, value))
            
            # Draw button
            pg.draw.rect(self.game.screen, UI_GRAY, button_rect)
            if button_rect.collidepoint(pg.mouse.get_pos()):
                pg.draw.rect(self.game.screen, UI_HIGHLIGHT, button_rect, 3)
            
            # Draw text
            text_surf = self.font_med.render(text, True, WHITE)
            text_rect = text_surf.get_rect(center=button_rect.center)
            self.game.screen.blit(text_surf, text_rect)

    def handle_menu_click(self, pos):
        """Handle mouse clicks on menu buttons"""
        for button_rect, value in self.menu_buttons:
            if button_rect.collidepoint(pos):
                if value == "quit":
                    self.game.running = False
                else:
                    self.game.current_difficulty = value
                    self.game.new(value)
                return True
        return False

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

        # Game over instructions
        instructions = [
            "M - Main Menu",
            "Q - Quit Game"
        ]
        
        for i, text in enumerate(instructions):
            instruction = self.font_med.render(text, True, WHITE)
            instruction_rect = instruction.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + i * 50)
            )
            self.game.screen.blit(instruction, instruction_rect)

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
        resources_rect = resources_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.game.screen.blit(resources_text, resources_rect)

        # Victory instructions
        instructions = [
            "M - Main Menu", 
            "Q - Quit Game"
        ]
        
        for i, text in enumerate(instructions):
            instruction = self.font_med.render(text, True, WHITE)
            instruction_rect = instruction.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 50 + i * 50)
            )
            self.game.screen.blit(instruction, instruction_rect)