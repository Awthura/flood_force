import pygame as pg
from settings import *
vec = pg.math.Vector2

class Tile(pg.sprite.Sprite):
    def __init__(self, game, x, y, tile_type):
        self._layer = 0  # Base layer for tiles
        self.groups = game.all_sprites, game.tiles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.tile_type = tile_type
        self.water_level = 0
        self.elevation = 0
        self.has_infrastructure = False
        self.highlighted = False
        self.is_house = False
        self.initialize_tile()

    def initialize_tile(self):
        """Initialize tile appearance and properties"""
        if self.tile_type == LAND:
            self.image.fill(GRASS_GREEN)
            self.water_level = 0.0
            self.elevation = 1
        elif self.tile_type == WATER:
            self.image.fill(WATER_BLUE)
            self.water_level = 1.0
            self.elevation = 0
        elif self.tile_type == RIVER_BANK:
            self.image.fill((139, 69, 19))  # Brown color for river bank
            self.water_level = 0.0
            self.elevation = 0.5

    def update_appearance(self):
        """Update tile appearance based on current state"""
        # Base appearance
        if self.tile_type == WATER:
            self.image.fill(WATER_BLUE)
        elif self.tile_type == LAND:
            self.image.fill(GRASS_GREEN)
        elif self.tile_type == RIVER_BANK:
            self.image.fill((139, 69, 19))
        
        # Draw house if present
        if self.is_house:
            house_rect = pg.Rect(10, 10, TILESIZE-20, TILESIZE-20)
            pg.draw.rect(self.image, (139, 69, 19), house_rect)
            # Add roof
            roof_points = [(5, 20), (TILESIZE//2, 5), (TILESIZE-5, 20)]
            pg.draw.polygon(self.image, (165, 42, 42), roof_points)
        
        # Show infrastructure
        if self.has_infrastructure:
            pg.draw.rect(self.image, (100, 100, 100), self.rect.inflate(-10, -10), 2)
        
        # Show selection highlight
        if self.highlighted:
            highlight_surf = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)
            pg.draw.rect(highlight_surf, (255, 255, 255, 100), highlight_surf.get_rect())
            self.image.blit(highlight_surf, (0, 0))

    def update_water_level(self, amount):
        """Update tile's water level and visual appearance"""
        old_level = self.water_level
        self.water_level = max(0, min(1, self.water_level + amount))
        if old_level != self.water_level:
            self.update_appearance()

    def get_base_color(self):
        """Get the base color for the tile based on type and elevation"""
        if self.tile_type == LAND:
            # Vary the green based on elevation
            base_green = 139 + (self.elevation * 20)
            return (34, min(255, base_green), 34)
        elif self.tile_type == WATER:
            return WATER_BLUE
        return UI_GRAY

class Infrastructure(pg.sprite.Sprite):
    def __init__(self, game, tile, infra_type):
        self._layer = 1  # Layer above tiles
        self.groups = game.all_sprites, game.infrastructure
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.tile = tile
        self.infra_type = infra_type
        self.durability = 100
        self.efficiency = 1.0
        self.initialize_infrastructure()

    def initialize_infrastructure(self):
        """Set up infrastructure based on type"""
        if self.infra_type == BARRIER:
            self.image = pg.Surface((TILESIZE, TILESIZE))
            self.image.fill((150, 150, 150))  # Gray base
            # Add visual details for barrier
            pg.draw.rect(self.image, (100, 100, 100), self.image.get_rect(), 4)  # Dark border
            self.protection_level = 0.8
        elif self.infra_type == VEGETATION:
            self.image = pg.Surface((TILESIZE, TILESIZE))
            self.image.fill((0, 100, 0))  # Dark green base
            # Add simple tree shapes
            pg.draw.polygon(self.image, (34, 139, 34), [  # Lighter green
                (TILESIZE//2, 5),
                (TILESIZE-10, TILESIZE//2),
                (10, TILESIZE//2)
            ])
            pg.draw.rect(self.image, (139, 69, 19), (TILESIZE//2-4, TILESIZE//2, 8, TILESIZE//2))  # Brown trunk
            self.protection_level = 0.4
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.tile.rect.topleft
        self.tile.has_infrastructure = True

    def update(self):
        """Update infrastructure state"""
        if self.durability <= 0:
            self.destroy()
        elif self.water_damage():
            self.reduce_durability()

    def water_damage(self):
        """Check if infrastructure takes damage from water"""
        return self.tile.water_level > self.protection_level

    def reduce_durability(self):
        """Reduce durability based on water level"""
        damage = (self.tile.water_level - self.protection_level) * 10
        self.durability = max(0, self.durability - damage)
        self.efficiency = self.durability / 100
        self.update_appearance()

    def update_appearance(self):
        """Update visual appearance based on durability"""
        alpha = int(255 * (self.durability / 100))
        self.image.set_alpha(alpha)

    def destroy(self):
        """Remove the infrastructure"""
        self.tile.has_infrastructure = False
        self.kill()
