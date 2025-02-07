# Essential game settings
TITLE = "Flood Force"
WIDTH = 1024
HEIGHT = 768
FPS = 60
TILESIZE = 64

# Colors
WATER_BLUE = (65, 105, 225)
GRASS_GREEN = (34, 139, 34)
UI_GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# UI specific colors
UI_BACKGROUND = (40, 40, 40)
UI_TEXT = WHITE
UI_HIGHLIGHT = (100, 100, 255)
UI_WARNING = RED

# Grid settings
GRID_WIDTH = 10
GRID_HEIGHT = 8
VICTORY = "victory"

# Weather and Flood settings
MAX_TURNS = 20                  # More turns to give time for effects
FLOOD_THRESHOLD = 0.7           # Water level that counts as flooding
MAX_FLOOD_PERCENTAGE = 40       # More forgiving flood percentage
WATER_FLOW_RATE = 0.2          # Slower water flow

# Scoring settings
SCORE_PER_RESOURCE = 10     # Points per resource saved
SCORE_PER_SAFE_TILE = 100   # Points per non-flooded tile
MIN_SCORE_TO_WIN = 1000     # Score needed to win the game

# Level progression
BASE_MAX_TURNS = 10         # Starting number of turns
TURN_DECREASE_PER_LEVEL = 1 # How many fewer turns in each level
MIN_TURNS = 5              # Minimum turns allowed
RESOURCE_INCREASE_PER_LEVEL = 200  # Additional resources per level

# Visual effect settings
WATER_OPACITY = 150
WARNING_FLASH_SPEED = 4
RAIN_INTENSITY_LEVELS = {
    'light': 0.3,
    'medium': 0.6,
    'heavy': 0.9
}

# Game states
MENU = "menu"
PLANNING = "planning"
WEATHER = "weather"
ASSESSMENT = "assessment"
GAME_OVER = "game_over"

# Resource settings
STARTING_RESOURCES = 10000  # Starting budget for each level

# Tile types
LAND = "land"
WATER = "water"
BARRIER = "barrier"
VEGETATION = "vegetation"

# Infrastructure costs
INFRASTRUCTURE_COSTS = {
    BARRIER: 100,
    VEGETATION: 50
}
INFRASTRUCTURE_EFFICIENCY = {    # How effective each type is
    BARRIER: 0.8,              # Barriers block 80% of water
    VEGETATION: 0.4            # Vegetation absorbs 40% of water
} 