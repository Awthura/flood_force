import pygame as pg
from settings import *

class UI:
    def __init__(self, game):
        self.game = game
        self.font_big = pg.font.Font(None, 64)
        self.font_med = pg.font.Font(None, 32)
        self.font_small = pg.font.Font(None, 24)

    def draw(self):
        if self.game.state == MENU:
            self.draw_menu()
        elif self.game.state in [PLANNING, WEATHER]:
            self.draw_game_ui()
        elif self.game.state == GAME_OVER:
            self.draw_game_over()
        elif self.game.state == ASSESSMENT:
            self.draw_assessment()

    def draw_menu(self):
        # Draw title
        title = self.font_big.render("FLOOD FORCE", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.game.screen.blit(title, title_rect)

        # Draw start instructions
        start_text = self.font_med.render("Press SPACE to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
        self.game.screen.blit(start_text, start_rect)

        # Draw tutorial hint
        tutorial_text = self.font_small.render("Press T for Tutorial", True, WHITE)
        tutorial_rect = tutorial_text.get_rect(center=(WIDTH // 2, HEIGHT * 3 // 4))
        self.game.screen.blit(tutorial_text, tutorial_rect)

    def draw_game_ui(self):
        # Draw resources
        resource_text = self.font_med.render(f"Budget: ${self.game.resources}", True, WHITE)
        self.game.screen.blit(resource_text, (10, 10))

        # Draw current phase
        phase_text = self.font_med.render(f"Phase: {self.game.state.title()}", True, WHITE)
        self.game.screen.blit(phase_text, (10, 50))

        # Draw turn counter in weather phase
        if self.game.state == WEATHER:
            turn_text = self.font_med.render(
                f"Turn: {self.game.water_sim.turn_counter}/{MAX_TURNS}", True, WHITE
            )
            self.game.screen.blit(turn_text, (10, 90))

        # Draw controls help
        if self.game.state == PLANNING:
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
        # Draw game over message
        gameover_text = self.font_big.render("GAME OVER", True, RED)
        gameover_rect = gameover_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.game.screen.blit(gameover_text, gameover_rect)

        # Draw flood percentage
        flood_text = self.font_med.render(
            f"Flood Percentage: {self.game.flood_percentage:.1f}%", True, WHITE
        )
        flood_rect = flood_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.game.screen.blit(flood_text, flood_rect)

        # Draw restart instructions
        restart_text = self.font_med.render("Press R to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
        self.game.screen.blit(restart_text, restart_rect)

    def draw_assessment(self):
        # Draw assessment title
        title_text = self.font_big.render("Results", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.game.screen.blit(title_text, title_rect)

        # Draw statistics
        stats = [
            f"Flood Percentage: {self.game.flood_percentage:.1f}%",
            f"Resources Remaining: ${self.game.resources}",
            f"Final Score: {self.game.score}"
        ]

        for i, stat in enumerate(stats):
            stat_text = self.font_med.render(stat, True, WHITE)
            stat_rect = stat_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
            self.game.screen.blit(stat_text, stat_rect)

        # Draw continue instructions
        continue_text = self.font_med.render("Press SPACE to Continue", True, WHITE)
        continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT * 3 // 4))
        self.game.screen.blit(continue_text, continue_rect)