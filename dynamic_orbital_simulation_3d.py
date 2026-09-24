import pygame
import sys
import random
import numpy as np
import scipy.integrate as integrate


# SETUP & CONFIGURATION CONSTANTS
SCREEN_SIZE = 1000
FPS = 60

# GLOBAL PHYSICAL CONSTANTS
G = 6.6743e-11 # Gravitational Constant
SOLAR_MASS = 1.989e30
SECONDS_PER_YEAR = 3.154e7
METERS_PER_LY = 9.461e15

# FUNCTIONAL CONSTANTS
POPULATION_SIZE = 240
dt = 10000 * SECONDS_PER_YEAR # Time interval (years * seconds_per_year) - Calculated per frame
BOX_DIMENSIONS = 10 * METERS_PER_LY # Dimentions of the contained simulation space (ly * meters_per_ly)
SOFTENING = 1e16
THREE_D = True
MOVEMENT_FACTOR = BOX_DIMENSIONS / 200
CELL_SIZE = SCREEN_SIZE / 10            # Size of each grid square (640 / 40 = 16 cells wide/high)
GRID_COLOR = (30, 30, 30)        # Grid line color


# CLASSES
################################################################

# PHYSICS ENTITY CLASS
class Particle:
    """ Tracks precision physical attributes and updates state """
    def __init__(self, x, y, z, vx, vy, vz, mass):
        # Always use floating-point numbers for physics calculations
        self.mass = float(mass)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.vx = float(vx)
        self.vy = float(vy)
        self.vz = float(vz)

        # will derive and compute these values below
        self.ax = 0.0
        self.ay = 0.0
        self.az = 0.0
        self.scale_x = 0.0
        self.scale_y = 0.0
        self.scale_z = 0.0
        self.draw_radius = 0.0 # interger render pixel size (derived from mass)
        self.color = [0, 0, 0]

    # Physics calculation methods
    def update_acceleration(self, x_m, y_m, z_m, mass_m):
        """ CALCULATE NEW ACCELERATION (a = - Gm * r / ||r||^3) derived from ma = -GMm / r^2
        
        takes position (r) parameters and calculates the new acceration of M experienced by
        the orbiting body m. (a = - Gm * r / ||r||^3) derived from ma = -GMm / r^2
        """
        dx = self.x - x_m
        dy = self.y - y_m
        dz = self.z - z_m
        mag_r_cubed = ((dx**2) + (dy**2) + (dz**2) + (SOFTENING**2)) ** (3/2) # calculate mag of ||r||^3
        a_constants = (-1) * G * mass_m / mag_r_cubed # define constants
        # multiply dx, dy and dz by constants to get ax, ay and az
        self.ax += dx * a_constants 
        self.ay += dy * a_constants 
        self.az += dz * a_constants 

    def update_velocity(self):
        """ CALCULATE NEW VELOCITY (v = v + a * dt)

        takes velocity (v), acceleration (a) and dt (time interval) and calculates the new
        velocity of the orbiting body. (v = v + a * dt)
        """
        # multiply a * dt
        adtx = self.ax * dt 
        adty = self.ay * dt
        adtz = self.az * dt
        # add v + adt
        self.vx += adtx 
        self.vy += adty
        self.vz += adtz

    def update_position(self):
        """ CALCULATE NEW POSITION (r = r + v * dt)

        takes position (r), velocity (v) and dt (time interval) and calculates the new
        velocity of the orbiting body. (r = r + v * dt)
        """
        # multiply v * dt
        vdtx = self.vx * dt 
        vdty = self.vy * dt
        vdtz = self.vz * dt
        # add r + vdt
        self.x += vdtx 
        self.y += vdty
        self.z += vdtz

        # Scales the position coordinates to fit the screen size
        self.scale_x = SCREEN_SIZE * (self.x / BOX_DIMENSIONS)
        self.scale_y = SCREEN_SIZE * (self.y / BOX_DIMENSIONS)
        self.scale_z = SCREEN_SIZE * (self.z / BOX_DIMENSIONS)
        
        self.draw_radius = 0.2 * (self.mass * (self.scale_z + 800) / SCREEN_SIZE / 1.5e29) # scales draw_radius with mass AND distance from viewer
        if self.draw_radius < 1.0:
            self.draw_radius = 1.0

        if self.scale_z > 0.0 and self.scale_z < SCREEN_SIZE:
            self.color[0] = abs(int(255 * (self.scale_z / SCREEN_SIZE))) # R-channel
            self.color[1] = abs(int(255 * (self.scale_z / SCREEN_SIZE))) # B-channel
            self.color[2] = abs(int(220 * (self.scale_z / SCREEN_SIZE))) # G-channel            

    # Render to screen
    def draw(self, surface):
        """ Convert floats to integers ONLY during the rendering phase """
        render_pos = (int(self.scale_x), int(self.scale_y))
        pygame.draw.circle(surface, self.color, render_pos, self.draw_radius)


# POPULATION ENTITY CLASS
class ParticlePopulation:
    """ Generates and maintains a list of distinct particles of varying masses, positions
    and velocities 
    """
    def __init__(self):
        self.population = []

    def generate_random_particle(self, pos_range=(0, BOX_DIMENSIONS), vel_range=(-100, 100), mass_range=(1.5e29, 6.0e32)):
        """ Generates a single particle with random values within specified limits. """
        # mass = random.uniform(*mass_range) # use if we want a uniform IMF
        a_scale = mass_range[0] / SOLAR_MASS
        b_scale = mass_range[1] / SOLAR_MASS
        mass_scale = bounded_exponential_decay(a_scale, b_scale, lambd=2.35)
        mass = mass_scale * SOLAR_MASS        
        
        # Generate 3D coordinates for position and velocity
        position = [random.uniform(*pos_range) for _ in range(3)]
        x = position[0]
        y = position[1]
        if THREE_D == True:
            z = position[2]
        else:
            z = 0.0

        velocity = [random.uniform(*vel_range) for _ in range(3)]
        vx = velocity[0]
        vy = velocity[1]
        if THREE_D == True:
            vz = velocity[2]
        else:
            vz = 0.0

        # Generates new partical and adds it to the population
        new_particle = Particle(x, y, z, vx, vy, vz, mass)
        self.population.append(new_particle)

    def generate_multiple(self, count, **kwargs):
        """ Helper to generate many particles at once. """
        for i in range(count):
            self.generate_random_particle(**kwargs)


# FUNCTIONS
################################################################

def bounded_exponential_decay(a, b, lambd=2.35):
    """ Returns a randomly generated number (stellar mass) according to an exponential
    decay function described by lambda (2.35) and between upper and lower bounds
    """
    # Python's built-in math.exp(x) can be replaced by 2.718281828459045 ** x
    e = 2.718281828459045
    
    # Calculate bounds in CDF space
    cdf_a = e ** (-lambd * a)
    cdf_b = e ** (-lambd * b)
    
    # Pick a random uniform spot between the scaled bounds
    u = random.uniform(cdf_a, cdf_b)
    
    # Approximate natural log using Python's log built-in via the math module is bypassed 
    # by using random.expovariate with a loop or inverse transform approximation.
    # Alternatively, a clean way without log is to use rejection sampling:
    
    max_y = e ** (-lambd * a) if lambd > 0 else e ** (-lambd * b)
    while True:
        x = random.uniform(a, b)
        y = random.uniform(0, max_y)
        if y <= e ** (-lambd * x):
            return x


def draw_grid_lines(screen, x_offset, y_offset):
    start_x = int(x_offset % CELL_SIZE)
    start_y = int(y_offset % CELL_SIZE)

    # Draw vertical lines from top to bottom
    for x in range(start_x, SCREEN_SIZE + int(CELL_SIZE), int(CELL_SIZE)):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_SIZE))
        
    # Draw horizontal lines from left to right
    for y in range(start_y, SCREEN_SIZE + int(CELL_SIZE), int(CELL_SIZE)):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_SIZE, y))


# MAIN SIMULATION LOOP
################################################################

def main():
    """ Contains the main program loop. It initiates the simulations and processes
    the main physics updates and handles the rendering updates each loop.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("DYNAMIC ORBITAL SIMULATION")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    t_elapsed = 0.0
    x_offset = 0.0
    y_offset = 0.0
    global CELL_SIZE

    # Instantiate our physics object(s)
    cluster = ParticlePopulation()
    cluster.generate_multiple(count=POPULATION_SIZE)
    
    running = True
    while running:
        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            for k in range(len(cluster.population)):
                cluster.population[k].y += MOVEMENT_FACTOR
            y_offset += SCREEN_SIZE * (MOVEMENT_FACTOR / BOX_DIMENSIONS)

        if keys[pygame.K_DOWN]:
            for k in range(len(cluster.population)):
                cluster.population[k].y -= MOVEMENT_FACTOR
            y_offset -= SCREEN_SIZE * (MOVEMENT_FACTOR / BOX_DIMENSIONS)

        if keys[pygame.K_LEFT]:
            for k in range(len(cluster.population)):
                cluster.population[k].x += MOVEMENT_FACTOR
            x_offset += SCREEN_SIZE * (MOVEMENT_FACTOR / BOX_DIMENSIONS)

        if keys[pygame.K_RIGHT]:
            for k in range(len(cluster.population)):
                cluster.population[k].x -= MOVEMENT_FACTOR
            x_offset -= SCREEN_SIZE * (MOVEMENT_FACTOR / BOX_DIMENSIONS)

        if keys[pygame.K_EQUALS]:
            for k in range(len(cluster.population)):
                cluster.population[k].z += MOVEMENT_FACTOR
                cluster.population[k].x *= 1.01
                cluster.population[k].y *= 1.01
            CELL_SIZE = CELL_SIZE * 1.01

        if keys[pygame.K_MINUS]:
            for k in range(len(cluster.population)):
                cluster.population[k].z -= MOVEMENT_FACTOR
                cluster.population[k].x /= 1.01
                cluster.population[k].y /= 1.01
            CELL_SIZE = CELL_SIZE / 1.01
            

        # CALCULATE AND RENDER FPS
        current_fps = clock.get_fps()
        fps_text = font.render(f"FPS: {round(current_fps, 1)}", True, (255, 255, 255))

        # CALCULATE AND RENDER SIMULATION TIME ELAPSED
        t_elapsed += dt / SECONDS_PER_YEAR
        t_elapsed_text = font.render("t = " + f"{int(t_elapsed):,}" + " years", True, (255, 255, 255))

        # PHYSICS & LOGIC UPDATES
        # class methods to run calculations and update new positions and velocities
        for i in range(len(cluster.population)):
            for j in range(len(cluster.population)):
                if i != j:
                    cluster.population[i].update_acceleration(cluster.population[j].x, cluster.population[j].y, cluster.population[j].z, cluster.population[j].mass)

        for k in range(len(cluster.population)):
            cluster.population[k].update_velocity()
            cluster.population[k].update_position()
            cluster.population[k].ax = 0.0
            cluster.population[k].ay = 0.0
            cluster.population[k].az = 0.0

        # RENDERING (Clear -> Draw -> Flip)
        screen.fill((10, 10, 10))  # Clear screen with dark gray
        draw_grid_lines(screen, x_offset, y_offset)
        # _.draw here
        for i in cluster.population:
            i.draw(screen)
        screen.blit(fps_text, (10, 10))
        screen.blit(t_elapsed_text, (10, 40))
        pygame.display.flip()      # Refresh display

        # TIME STEP CONTROL
        clock.tick(FPS)  # Maintain steady 60 frames per second

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()




## FUTURE IMPROVEMENTS
##
## Code in IMF for initializing populaiton
## Rework with real-world units and scale to fit screen as needed
## Code in some preset systems - i.e. a stable solar system (need to determine initial starting conditions)
## Create ghost trails for particles
## Fix FPS issues. sim can run at whatever speed dt*CPS (calculations/sec) but only update the screen at 60 FPS
## ---- Define what we want on the screen - i.e. 100,000 yrs per sec
## ---- Years per rendered frame = target rate / FPS i.e. 100,000/60 = 1666.7 yrs
## ---- Now we need to figure out how many calculations per sec to match the dt time interval
## ---- rendered frame rate / dt should give the loop CPS
## Model in 3 dimensions
## Add redshift coloration
## Zoom and translational controls