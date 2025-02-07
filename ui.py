import pygame as pg
from settings import *

class UI:
    def __init__(self, game):
        """Initialize the UI with a reference to the game instance
        
        Args:
            game: The main Game instance that this UI will render for
        """
        self.game = game
        # Initialize fonts for different text sizes
        self.font_big = pg.font.Font(None, 64)    # Large text for titles
        self.font_med = pg.font.Font(None, 32)    # Medium text for important info
        self.font_small = pg.font.Font(None, 24)  # Small text for details

    def draw(self):
        """Draw the appropriate UI elements based on game state"""
        current_state = self.game.state
        print(f"Drawing UI for state: {current_state}")  # Debug info
        
        if current_state == MENU:
            self.draw_menu()
        elif current_state in [PLANNING, WEATHER]:
            self.draw_game_ui()
        elif current_state == GAME_OVER:
            self.draw_game_over()
        elif current_state == VICTORY:
            self.draw_victory()

    def draw_menu(self):
        """Draw the main menu screen"""
        # Draw title
        title = self.font_big.render("FLOOD FORCE", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.game.screen.blit(title, title_rect)

        # Draw start instructions
        start_text = self.font_med.render("Press SPACE to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
        self.game.screen.blit(start_text, start_rect)

    def draw_game_ui(self):
        """Draw the in-game UI elements"""
        # Resources display
        resource_text = self.font_med.render(f"Budget: ${self.game.resources}", True, WHITE)
        self.game.screen.blit(resource_text, (10, 10))

        # Current phase
        phase_text = self.font_med.render(f"Phase: {self.game.state.title()}", True, WHITE)
        self.game.screen.blit(phase_text, (10, 50))

        # Show flood percentage during weather phase
        if self.game.state == WEATHER:
            flood_text = self.font_med.render(
                f"Flood: {self.game.flood_percentage:.1f}% (Max: {MAX_FLOOD_PERCENTAGE}%)", 
                True, 
                RED if self.game.flood_percentage > MAX_FLOOD_PERCENTAGE else WHITE
            )
            self.game.screen.blit(flood_text, (10, 90))

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
        for i, text in enumerate(controls_text):
            help_text = self.font_small.render(text, True, WHITE)
            self.game.screen.blit(help_text, (WIDTH - 200, 10 + i * 30))

    def draw_game_over(self):
        """Draw the game over screen"""
        self._draw_overlay()  # Darken the background
        
        # Game Over message
        title = self.font_big.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.game.screen.blit(title, title_rect)

        # Show flood percentage
        flood_text = self.font_med.render(
            f"Flood Percentage: {self.game.flood_percentage:.1f}%", True, WHITE
        )
        flood_rect = flood_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.game.screen.blit(flood_text, flood_rect)

        # Restart instruction
        restart_text = self.font_med.render("Press R to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
        self.game.screen.blit(restart_text, restart_rect)

    def draw_victory(self):
        """Draw the victory screen"""
        self._draw_overlay()  # Darken the background
        
        # Victory message
        title = self.font_big.render("VICTORY!", True, GREEN)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.game.screen.blit(title, title_rect)

        # Show statistics
        stats = [
            f"Houses Protected!",
            f"Flood Percentage: {self.game.flood_percentage:.1f}%",
            f"Resources Left: ${self.game.resources}"
        ]
        for i, stat in enumerate(stats):
            text = self.font_med.render(stat, True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
            self.game.screen.blit(text, rect)

        # Continue instruction
        continue_text = self.font_med.render("Press R to Play Again", True, WHITE)
        continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT * 3 // 4))
        self.game.screen.blit(continue_text, continue_rect)

    def _draw_overlay(self):
        """Helper method to draw a semi-transparent overlay"""
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.game.screen.blit(overlay, (0, 0))