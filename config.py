# PHYSICAL ENVIRONMENTAL CONSTANTS
THREE_D = True
POPULATION_SIZE = 150
dt = 0.01 * 3.154e7 # Time interval (years * seconds_per_year) - Calculated per frame
# BOX_DIMENSIONS = 0.1 * METERS_PER_LY # Dimentions of the contained simulation space (ly * meters_per_ly)
BOX_DIMENSIONS = 1e13

# FUNCTIONAL VARIABLES
SOFTENING = 1e16
SOFTENING = 1e8
MOVEMENT_FACTOR = BOX_DIMENSIONS / 200 # Determines rate at which the space moves when using the translational arrow keys
CELL_SIZE = 1000 / 10 # Size of each grid square (640 / 40 = 16 cells wide/high)
BACKGROUND_COLOR = (0, 0, 0)
GRID_COLOR = (40, 40, 40)
TRAIL_COLOR = (100, 100, 100)