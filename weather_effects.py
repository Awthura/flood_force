import pygame as pg
import random
from settings import *

class RainEffect:
    def __init__(self, game):
        self.game = game
        self.drops = []
        self.intensity = 0.5  # 0 to 1
        
    def update(self):
        # Add new raindrops based on intensity
        if self.game.state == WEATHER:
            drops_to_add = int(20 * self.intensity)
            for _ in range(drops_to_add):
                self.drops.append(self.create_raindrop())
        
        # Update existing drops
        for drop in self.drops[:]:
            drop[1] += 15  # Move down
            if drop[1] > HEIGHT:
                self.drops.remove(drop)
    
    def create_raindrop(self):
        return [random.randint(0, WIDTH), random.randint(-20, 0)]
    
    def draw(self, surface):
        if self.game.state == WEATHER:
            for drop in self.drops:
                pg.draw.line(surface, (200, 200, 255), 
                           (drop[0], drop[1]), 
                           (drop[0], drop[1] + 5), 1)

class WaterOverlay:
    def __init__(self, game):
        self.game = game
        self.warning_alpha = 0
        self.warning_increasing = True
        
    def update(self):
        # Pulse warning alpha for high water levels
        if self.warning_increasing:
            self.warning_alpha += 4
            if self.warning_alpha >= 255:
                self.warning_increasing = False
        else:
            self.warning_alpha -= 4
            if self.warning_alpha <= 100:
                self.warning_increasing = True
    
    def draw_water_level(self, tile, surface):
        if tile.water_level > 0:
            # Draw water level
            water_height = int(TILESIZE * tile.water_level)
            water_rect = pg.Rect(
                tile.rect.x,
                tile.rect.bottom - water_height,
                TILESIZE,
                water_height
            )
            
            # Water color based on depth
            base_color = WATER_BLUE
            alpha = int(255 * tile.water_level)
            water_surface = pg.Surface((TILESIZE, water_height), pg.SRCALPHA)
            water_color = (*base_color, alpha)  # Create RGBA tuple
            pg.draw.rect(water_surface, water_color, 
                        (0, 0, TILESIZE, water_height))
            surface.blit(water_surface, water_rect)
            
            # Warning indicator for high water
            if tile.water_level > FLOOD_THRESHOLD:
                warning_surface = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)
                warning_color = (255, 0, 0, min(255, self.warning_alpha))  # Ensure alpha doesn't exceed 255
                pg.draw.rect(warning_surface, warning_color, 
                            warning_surface.get_rect())
                surface.blit(warning_surface, tile.rect)

class InfrastructureIndicator:
    def __init__(self, infrastructure):
        self.infrastructure = infrastructure
        self.health_bar_height = 3
        
    def draw(self, surface):
        # Draw health bar background
        health_rect = pg.Rect(
            self.infrastructure.rect.x,
            self.infrastructure.rect.y - 5,
            TILESIZE,
            self.health_bar_height
        )
        pg.draw.rect(surface, (255, 0, 0), health_rect)
        
        # Draw current health
        current_health = int(TILESIZE * (self.infrastructure.durability / 100))
        if current_health > 0:
            health_rect.width = current_health
            color = self.get_health_color(self.infrastructure.durability)
            pg.draw.rect(surface, color, health_rect)
    
    def get_health_color(self, health):
        if health > 70:
            return GREEN
        elif health > 30:
            return YELLOW
        return RED

def update_tile_appearance(tile):
    """Update tile appearance with water level indicators"""
    # Start with base color
    base_color = tile.get_base_color()
    tile.image.fill(base_color)
    
    # Add water level visualization
    if tile.water_level > 0:
        water_height = int(TILESIZE * tile.water_level)
        water_rect = pg.Rect(0, TILESIZE - water_height, TILESIZE, water_height)
        water_color = (*WATER_BLUE, int(255 * tile.water_level))
        water_surface = pg.Surface((TILESIZE, water_height), pg.SRCALPHA)
        water_surface.fill(water_color)
        tile.image.blit(water_surface, water_rect)
    
    # Add infrastructure indication
    if tile.has_infrastructure:
        pg.draw.rect(tile.image, (100, 100, 100), 
                    tile.image.get_rect().inflate(-4, -4), 2)
    
    # Add highlight if selected
    if tile.highlighted:
        highlight_surface = pg.Surface(tile.image.get_size(), pg.SRCALPHA)
        pg.draw.rect(highlight_surface, (255, 255, 255, 100), 
                    highlight_surface.get_rect())
        tile.image.blit(highlight_surface, (0, 0))