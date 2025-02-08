import pygame as pg
from settings import *
vec = pg.math.Vector2
from sprites import *

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
        # Position tools at bottom with more spacing
        button_y = HEIGHT - 100  # Move up a bit from bottom
        self.tools = [
            Tool(game, 20, button_y, BARRIER, "Barrier Wall (B)", 100),
            Tool(game, 220, button_y, VEGETATION, "Vegetation (V)", 50),
            Tool(game, 420, button_y, "remove", "Remove (R)", 0),
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
        
        # Create larger tool button
        self.image = pg.Surface((180, 80))  # Increased size
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.update_appearance()
    
    def select(self):
        self.selected = True
        self.update_appearance()

    def deselect(self):
        self.selected = False
        self.update_appearance()

    def update_appearance(self):
        # Draw button background
        color = (100, 100, 255) if self.selected else (70, 70, 70)
        self.image.fill(color)
        
        # Draw button text with larger fonts
        name_font = pg.font.Font(None, 36)  # Bigger font for name
        cost_font = pg.font.Font(None, 32)  # Slightly smaller for cost
        
        # Draw name text
        text = name_font.render(f"{self.name}", True, (255, 255, 255))
        text_rect = text.get_rect(centerx=self.image.get_width()//2, top=15)
        self.image.blit(text, text_rect)
        
        # Draw cost text if applicable
        if self.cost > 0:
            cost_text = cost_font.render(f"${self.cost}", True, (255, 255, 255))
            cost_rect = cost_text.get_rect(centerx=self.image.get_width()//2, 
                                         bottom=self.image.get_height()-10)
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
        """Determine if infrastructure can be placed on a given tile.
        
        The rules are:
        - Barriers can only be placed on river bank tiles
        - Vegetation can be placed on both land and river bank tiles
        - Cannot place anything on house tiles or existing infrastructure
        - Must have sufficient resources
        """
        if tool_type == "remove":
            return tile.has_infrastructure
        
        # Check if we have enough resources first
        if self.game.resources < INFRASTRUCTURE_COSTS[tool_type]:
            return False
            
        # Check if tile is already occupied
        if tile.has_infrastructure or tile.is_house:
            return False
            
        # Apply specific placement rules for each type
        if tool_type == BARRIER:
            return tile.tile_type == RIVER_BANK  # Barriers only on river banks
        elif tool_type == VEGETATION:
            return tile.tile_type in [LAND, RIVER_BANK]  # Trees on both land and river banks
        
        return False

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