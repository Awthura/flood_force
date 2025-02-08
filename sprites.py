import pygame as pg
from settings import *
import os

class Tile(pg.sprite.Sprite):
    def __init__(self, game, x, y, tile_type):
        self._layer = 0
        self.groups = game.all_sprites, game.tiles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.water_level = 0
        self.elevation = 0
        self.has_infrastructure = False
        self.highlighted = False
        self.is_house = False
        
        # Store images for different states
        self.images = self.load_tile_images()
        self.image = self.images[self.tile_type]
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        
        self.initialize_tile()

    def load_tile_images(self):
        """Load all possible tile images."""
        images = {}
        image_types = {
            LAND: "land.png",
            WATER: "water.png",
            RIVER_BANK: "river_bank.png"
        }
        
        for tile_type, image_name in image_types.items():
            image_path = os.path.join("resources", image_name)
            try:
                image = pg.image.load(image_path).convert_alpha()
                images[tile_type] = pg.transform.scale(image, (TILESIZE, TILESIZE))
            except:
                print(f"Failed to load image: {image_path}")
                surface = pg.Surface((TILESIZE, TILESIZE))
                surface.fill(self.get_default_color(tile_type))
                images[tile_type] = surface
        return images

    def get_default_color(self, tile_type):
        """Get default color for fallback rendering."""
        if tile_type == LAND:
            return GRASS_GREEN
        elif tile_type == WATER:
            return WATER_BLUE
        elif tile_type == RIVER_BANK:
            return (139, 69, 19)  # Brown
        return GRAY

    def initialize_tile(self):
        """Initialize tile properties."""
        if self.tile_type == LAND:
            self.water_level = 0.0
            self.elevation = 1
        elif self.tile_type == WATER:
            self.water_level = 1.0
            self.elevation = 0
        elif self.tile_type == RIVER_BANK:
            self.water_level = 0.0
            self.elevation = 0.5

    def update_appearance(self):
        """Update tile appearance based on current state."""
        # Use the appropriate base image for current tile type
        self.image = self.images[self.tile_type].copy()
        
        # Add water overlay for flooding
        if self.water_level > 0 and self.tile_type != WATER:
            water_overlay = self.images[WATER].copy()
            water_overlay.set_alpha(int(self.water_level * 255))
            self.image.blit(water_overlay, (0, 0))
        
        # Add house if present
        if self.is_house:
            try:
                house_image = pg.image.load(os.path.join("resources", "house.png")).convert_alpha()
                house_image = pg.transform.scale(house_image, (TILESIZE-10, TILESIZE-10))
                self.image.blit(house_image, (5, 5))
            except:
                house_rect = pg.Rect(10, 10, TILESIZE-20, TILESIZE-20)
                pg.draw.rect(self.image, (139, 69, 19), house_rect)
                roof_points = [(5, 20), (TILESIZE//2, 5), (TILESIZE-5, 20)]
                pg.draw.polygon(self.image, (165, 42, 42), roof_points)
        
        # Show infrastructure
        if self.has_infrastructure:
            pg.draw.rect(self.image, (100, 100, 100), 
                        self.rect.inflate(-10, -10), 2)
        
        # Show selection highlight
        if self.highlighted:
            highlight_surf = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)
            pg.draw.rect(highlight_surf, (255, 255, 255, 100), 
                        highlight_surf.get_rect())
            self.image.blit(highlight_surf, (0, 0))

class Infrastructure(pg.sprite.Sprite):
    def __init__(self, game, tile, infra_type):
        self._layer = 1
        self.groups = game.all_sprites, game.infrastructure
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.tile = tile
        self.infra_type = infra_type
        self.durability = 100
        self.efficiency = 1.0
        
        # Load image based on type
        self.base_image = self.load_infra_image()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = self.tile.rect.topleft
        
        self.tile.has_infrastructure = True

    def load_infra_image(self):
        """Load infrastructure image based on type."""
        image_name = ""
        if self.infra_type == BARRIER:
            image_name = "barrier.png"
        elif self.infra_type == VEGETATION:
            image_name = "vegetation.png"
            
        try:
            image = pg.image.load(os.path.join("resources", image_name)).convert_alpha()
            return pg.transform.scale(image, (TILESIZE, TILESIZE))
        except:
            surface = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)
            if self.infra_type == BARRIER:
                surface.fill((150, 150, 150))
                pg.draw.rect(surface, (100, 100, 100), surface.get_rect(), 4)
            elif self.infra_type == VEGETATION:
                surface.fill((0, 100, 0))
                pg.draw.polygon(surface, (34, 139, 34), [
                    (TILESIZE//2, 5),
                    (TILESIZE-10, TILESIZE//2),
                    (10, TILESIZE//2)
                ])
                pg.draw.rect(surface, (139, 69, 19), 
                           (TILESIZE//2-4, TILESIZE//2, 8, TILESIZE//2))
            return surface

    def update(self):
        """Update infrastructure state."""
        if self.durability <= 0:
            self.destroy()
        self.update_appearance()

    def update_appearance(self):
        """Update visual appearance based on durability."""
        self.image = self.base_image.copy()
        self.image.set_alpha(int(255 * (self.durability / 100)))

    def destroy(self):
        """Remove the infrastructure."""
        self.tile.has_infrastructure = False
        self.kill()