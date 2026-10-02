import csv
import sys
import numpy as np
import pygame
import pygame.surfarray as surfarray
from dataclasses import dataclass

filepath = "/Users/joshcook/Documents/Python/Orbital Simulation/solar_system_data.csv"

# ==============================================================================
# 1. CONFIGURATION CONSTANTS
# ==============================================================================
@dataclass(frozen=True)
class SimulationConfig:
    SCREEN_SIZE: int = 1000
    FPS: int = 60
    G: float = 6.6743e-11  # Gravitational Constant
    BLACK: tuple = (0, 0, 0)
    WHITE: tuple = (255, 255, 255)
    YELLOW: tuple = (255, 255, 0)
    BLUE: tuple = (0, 0, 255)

CONFIG = SimulationConfig()

# ==============================================================================
# 2. THE DATA CONTAINER (The Final Destination)
# ==============================================================================
@dataclass
class SimulationState:
    """Holds the live, matching numerical matrices for the active simulation."""
    names: list
    colors: list
    radii: list
    masses: np.ndarray       # Shape: (N,)
    positions: np.ndarray    # Shape: (N, 2)
    velocities: np.ndarray   # Shape: (N, 2)
    screen_coords: np.ndarray  # Shape: (N, 2) - Holds converted pixel integers

# ==============================================================================
# 3. THE PIPELINE PIPELINE LOADER
# ==============================================================================
def load_state_from_csv(filepath: str) -> SimulationState:
    """Parses an external CSV file into parallel matrices wrapped in a dataclass."""
    names, colors, radii = [], [], []
    mass_list, pos_list, vel_list = [], [], []
    
    # Map text strings from CSV directly to PyGame color tuples
    color_map = {"YELLOW": CONFIG.YELLOW, "WHITE": CONFIG.WHITE, "BLUE": CONFIG.BLUE}
    
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            names.append(row['name'])
            radii.append(int(row['radius']))
            colors.append(color_map.get(row['color'].upper(), CONFIG.WHITE))
            
            mass_list.append(float(row['mass']))
            pos_list.append([float(row['x']), float(row['y'])])
            vel_list.append([float(row['vx']), float(row['vy'])])

    num_bodies = len(names)
            
    return SimulationState(
        names=names,
        colors=colors,
        radii=radii,
        masses=np.array(mass_list, dtype=np.float64),
        positions=np.array(pos_list, dtype=np.float64),
        velocities=np.array(vel_list, dtype=np.float64),
        screen_coords=np.zeros((num_bodies, 2), dtype=np.int32)  # Initialized empty
    )

# ==============================================================================
# 4. THE MAIN SIMULATION ENGINE
# ==============================================================================
class SolarSystemSimulation:
    """Accepts the dataclass and handles execution logic and math operations."""
    def __init__(self, initial_state: SimulationState):
        pygame.init()
        self.screen = pygame.display.set_mode((CONFIG.SCREEN_SIZE, CONFIG.SCREEN_SIZE))
        pygame.display.set_caption("Vectorized Orbit Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # HERE IS THE HANDOFF: Save the dataclass container inside the engine
        self.state = initial_state
        
        # Scaling parameters: maps solar system distances (~6e12 meters) to pixels
        self.scale = (CONFIG.SCREEN_SIZE / 2) / 6.0e12 
        self.offset = CONFIG.SCREEN_SIZE // 2

    def update_physics(self, dt: float):
        """Vectorized linear algebra for N-body gravity on the dataclass fields."""
        positions = self.state.positions
        masses = self.state.masses
        
        # 1. Coordinate matrix subtraction to get 2D distance vectors [N, N, 2]
        dx = positions[np.newaxis, :, :] - positions[:, np.newaxis, :]
        
        # 2. Compute squared distances and flag self-interaction zeros to infinity
        dist_sq = np.sum(dx**2 + 1e9**2, axis=-1)
        np.fill_diagonal(dist_sq, np.inf) 
        
        # 3. Standard physics magnitude calculations
        dist = np.sqrt(dist_sq)
        inv_dist_cubed = 1.0 / (dist_sq * dist)
        
        # 4. Acceleration vector: G * m_j * dx_ij / r_ij^3
        accel = CONFIG.G * (dx * inv_dist_cubed[..., np.newaxis]) * masses[np.newaxis, :, np.newaxis]
        total_accel = np.sum(accel, axis=1)
        
        # 5. Modify the dataclass arrays directly at C-speed!
        self.state.velocities += total_accel * dt
        self.state.positions += self.state.velocities * dt

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def render(self):
        self.screen.fill(CONFIG.BLACK)
        
        # Loop through indices to draw each object
        for i in range(len(self.state.names)):
            # Convert raw coordinates to pixel space
            screen_x = int(self.state.positions[i, 0] * self.scale) + self.offset
            screen_y = int(self.state.positions[i, 1] * self.scale) + self.offset
            
            # Catch items if they fly off the screen boundaries safely
            if 0 <= screen_x < CONFIG.SCREEN_SIZE and 0 <= screen_y < CONFIG.SCREEN_SIZE:
                pygame.draw.circle(
                    self.screen, 
                    self.state.colors[i], 
                    (screen_x, screen_y), 
                    3 #self.state.radii[i]/63710000
                )
                
        pygame.display.flip()


    def render_batched(self):
        """Modifies VRAM memory directly using advanced integer array slicing."""
        # 1. Clear display to pure black
        self.screen.fill((0, 0, 0))
        
        # CRITICAL FIX: Convert physical coordinates to screen pixels using vectorized operations
        pixel_positions = (self.state.positions * self.scale) + self.offset
        self.state.screen_coords = pixel_positions.astype(np.int32)
        
        # 2. Extract local references to coordinates
        coords = self.state.screen_coords
        
        # 3. Create a boolean mask to filter out any bodies that flew off-screen.
        on_screen = (coords[:, 0] >= 0) & (coords[:, 0] < CONFIG.SCREEN_SIZE) & \
                    (coords[:, 1] >= 0) & (coords[:, 1] < CONFIG.SCREEN_SIZE)
        valid_coords = coords[on_screen]
        
        # 4. Open a direct memory pixel pointer pipeline straight to the window
        pixels = surfarray.pixels2d(self.screen)
        
        # 5. THE BATCH INJECTION: Updates all pixels simultaneously using array index slicing.
        #    (Note: If your positions are structured as X, Y, Pygame pixels2d expects pixels[x, y])
        pixels[valid_coords[:, 0], valid_coords[:, 1]] = 0xFFFFFF
        
        # 6. Delete the pixel pointer to unlock surface memory so PyGame can safely refresh
        del pixels 
        pygame.display.flip()

    def run(self):
        # Time-step progression: 86400 seconds = 1 earth day passing per frame
        total_dt = 86400 * 10
        # Sub-steps to prevent numerical blowing up
        sub_steps = 1000 
        dt = total_dt / sub_steps
        
        while self.running:
            self.handle_events()
            
            # Run the physics engine multiple times per frame at a smaller dt
            for _ in range(sub_steps):
                self.update_physics(dt)

            self.render()  # Slow draw.circle loop render call
            #self.render_batched()  # Fast batch rendering call
            self.clock.tick(CONFIG.FPS)
            
        pygame.quit()
        sys.exit()

# ==============================================================================
# 5. EXECUTION ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    # Load your external file data into the clean data structure container
    loaded_data = load_state_from_csv(filepath)
    
    # Inject the container into the execution engine and run it!
    simulation = SolarSystemSimulation(initial_state=loaded_data)
    simulation.run()