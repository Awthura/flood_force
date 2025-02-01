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
        self.initialize_tile()

    def initialize_tile(self):
        if self.tile_type == LAND:
            self.image.fill(GRASS_GREEN)
            self.elevation = 1
        elif self.tile_type == WATER:
            self.image.fill(WATER_BLUE)
            self.water_level = 1
        else:
            self.image.fill(UI_GRAY)

    def update_water_level(self, amount):
        """Update tile's water level and visual appearance"""
        old_level = self.water_level
        self.water_level = max(0, min(1, self.water_level + amount))
        if old_level != self.water_level:
            self.update_appearance()

    def update_appearance(self):
        """Update tile appearance based on water level and infrastructure"""
        # Create a copy of the base tile
        base_color = self.get_base_color()
        self.image.fill(base_color)
        
        # Add water level indicator
        if self.water_level > 0:
            water_height = int(TILESIZE * self.water_level)
            water_rect = pg.Rect(0, TILESIZE - water_height, TILESIZE, water_height)
            pg.draw.rect(self.image, WATER_BLUE, water_rect)

        # Add infrastructure indicator if present
        if self.has_infrastructure:
            pg.draw.rect(self.image, (100, 100, 100), self.rect.inflate(-10, -10), 2)

        # Add highlight if tile is being hovered over
        if self.highlighted:
            highlight_surf = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)
            pg.draw.rect(highlight_surf, (255, 255, 255, 100), highlight_surf.get_rect())
            self.image.blit(highlight_surf, (0, 0))

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

class UIElement(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height, text='', color=UI_GRAY):
        self._layer = 2  # Top layer for UI
        self.groups = game.all_sprites, game.ui_elements
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.text = text
        self.active = False
        self.render_text()

    def render_text(self):
        if self.text:
            font = pg.font.Font(None, 32)
            text_surface = font.render(self.text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            self.image.blit(text_surface, text_rect)

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        self.active = self.rect.collidepoint(mouse_pos)
        if self.active:
            self.image.set_alpha(200)
        else:
            self.image.set_alpha(255)

class ToolBar:
    def __init__(self, game):
        self.game = game
        self.tools = [
            Tool(game, 10, HEIGHT - 60, BARRIER, "Barrier Wall (B)", 100),
            Tool(game, 120, HEIGHT - 60, VEGETATION, "Vegetation (V)", 50),
            Tool(game, 230, HEIGHT - 60, "remove", "Remove (R)", 0),
        ]
        self.selected_tool = None
        self.create_tool_buttons()

    def select_tool(self, tool_type):
        print(f"Selecting tool: {tool_type}")  # Debug print
        # Deselect all tools first
        for tool in self.tools:
            tool.deselect()
        
        # Find and select the requested tool
        for tool in self.tools:
            if tool.tool_type == tool_type:
                tool.select()
                self.selected_tool = tool
                print(f"Tool selected: {tool.tool_type}")  # Debug print
                return True
        return False

    def get_current_tool(self):
        return self.selected_tool.tool_type if self.selected_tool else None
    
    def create_tool_buttons(self):
        for tool in self.tools:
            self.game.ui_elements.add(tool)

    def handle_click(self, pos):
        for tool in self.tools:
            if tool.rect.collidepoint(pos):
                self.selected_tool = tool if self.selected_tool != tool else None
                # Deselect other tools
                for other_tool in self.tools:
                    if other_tool != tool:
                        other_tool.selected = False
                tool.selected = not tool.selected
                return True
        return False

class Tool(pg.sprite.Sprite):
    def __init__(self, game, x, y, tool_type, name, cost):
        self._layer = 2
        self.groups = game.all_sprites, game.ui_elements
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.tool_type = tool_type
        self.name = name
        self.cost = cost
        self.selected = False
        print(f"Created tool: {tool_type}")  # Debug print
        
        # Create tool button
        self.image = pg.Surface((100, 50))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.update_appearance()
    
    def select(self):
        self.selected = True
        self.update_appearance()
        print(f"Selected tool: {self.tool_type}")  # Debug print

    def deselect(self):
        self.selected = False
        self.update_appearance()

    def update_appearance(self):
        # Draw button background
        color = (100, 100, 255) if self.selected else (70, 70, 70)
        self.image.fill(color)
        
        # Draw button text
        font = pg.font.Font(None, 24)
        text = font.render(f"{self.name}", True, (255, 255, 255))
        cost_text = font.render(f"${self.cost}", True, (255, 255, 255))
        
        # Center text
        text_rect = text.get_rect(centerx=self.image.get_width()//2, top=5)
        cost_rect = cost_text.get_rect(centerx=self.image.get_width()//2, bottom=45)
        
        self.image.blit(text, text_rect)
        if self.cost > 0:
            self.image.blit(cost_text, cost_rect)

    def update(self):
        self.update_appearance()

class MouseController:
    def __init__(self, game):
        self.game = game
        self.toolbar = ToolBar(game)
        self.hover_tile = None
        self.dragging = False
        self.last_placed = None

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        self.update_hover(mouse_pos)
        if self.dragging:
            self.handle_drag(mouse_pos)

    def update_hover(self, pos):
        # Only show hover effect during PLANNING state
        if self.game.state != PLANNING:
            if self.hover_tile:
                self.hover_tile.highlighted = False
                self.hover_tile.update_appearance()
            self.hover_tile = None
            return

        # Convert mouse position to grid coordinates
        grid_x, grid_y = self.game.grid.pixel_to_grid(*pos)
        new_hover = self.game.grid.get_tile(grid_x, grid_y)
        
        # Update hover highlighting
        if self.hover_tile != new_hover:
            if self.hover_tile:
                self.hover_tile.highlighted = False
                self.hover_tile.update_appearance()
            self.hover_tile = new_hover
            if self.hover_tile:
                self.hover_tile.highlighted = True
                self.hover_tile.update_appearance() 

    def handle_click(self, pos, button):
        print(f"Mouse click at {pos}, button {button}")  # Debug print
        current_tool = self.toolbar.get_current_tool()
        print(f"Current tool: {current_tool}")  # Debug print

        # Get clicked tile
        grid_x, grid_y = self.game.grid.pixel_to_grid(*pos)
        clicked_tile = self.game.grid.get_tile(grid_x, grid_y)
        
        if clicked_tile and self.game.state == PLANNING:
            print(f"Valid tile clicked at ({grid_x}, {grid_y})")  # Debug print
            if button == 1 and current_tool:  # Left click and tool selected
                if self.can_place_infrastructure(clicked_tile, current_tool):
                    print(f"Placing {current_tool} on tile")  # Debug print
                    self.place_infrastructure(clicked_tile, current_tool)
                else:
                    print("Cannot place infrastructure here")  # Debug print

    def handle_release(self):
        self.dragging = False
        self.last_placed = None

    def start_placement(self, tile):
        tool = self.toolbar.get_current_tool()
        if tool and self.can_place_infrastructure(tile, tool):
            self.place_infrastructure(tile, tool)
            self.dragging = True
            self.last_placed = tile

    def handle_drag(self, pos):
        grid_x, grid_y = self.game.grid.pixel_to_grid(*pos)
        current_tile = self.game.grid.get_tile(grid_x, grid_y)
        
        if current_tile and current_tile != self.last_placed:
            tool = self.toolbar.get_current_tool()
            if tool and self.can_place_infrastructure(current_tile, tool):
                self.place_infrastructure(current_tile, tool)
                self.last_placed = current_tile

    def can_place_infrastructure(self, tile, tool_type):
        if tool_type == "remove":
            return tile.has_infrastructure
        
        return (
            tile.tile_type == LAND and
            not tile.has_infrastructure and
            self.game.resources >= INFRASTRUCTURE_COSTS[tool_type]
        )

    def place_infrastructure(self, tile, tool_type):
        if tool_type == "remove":
            self.remove_infrastructure(tile)
            return

        cost = INFRASTRUCTURE_COSTS[tool_type]
        if self.game.resources >= cost:
            Infrastructure(self.game, tile, tool_type)
            self.game.resources -= cost
            print(f"Placed {tool_type}, remaining resources: {self.game.resources}")

    def remove_infrastructure(self, tile):
        if tile.has_infrastructure:
            for sprite in self.game.infrastructure:
                if sprite.tile == tile:
                    sprite.kill()
                    tile.has_infrastructure = False
                    # Optionally refund some resources
                    self.game.resources += INFRASTRUCTURE_COSTS[sprite.infra_type] // 2
                    break