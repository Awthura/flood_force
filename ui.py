import pygame as pg
from settings import *

class UI:
    def __init__(self, game):
        self.game = game
        self.font_big = pg.font.Font(None, 64)
        self.font_med = pg.font.Font(None, 32)
        self.font_small = pg.font.Font(None, 24)

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

    def draw_menu(self):
        """Draw the main menu screen"""
        title = self.font_big.render("FLOOD FORCE", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.game.screen.blit(title, title_rect)

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