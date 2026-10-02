import pygame
import sys
import random
import numpy as np
import scipy.integrate as integrate
import matplotlib
import csv
import config


# # READ
# with open('data.csv', mode='r', newline='', encoding='utf-8') as file:
#     reader = csv.reader(file)
#     header = next(reader)  # Skips and saves the header row
#     for row in reader:
#         print(row)  # Each row is a list of strings

# # WRITE
# data = [
#     ['Name', 'Age', 'City'],
#     ['Alice', '30', 'New York'],
#     ['Bob', '25', 'Los Angeles']
# ]

# with open('output.csv', mode='w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
#     writer.writerows(data)


# SETUP & CONFIGURATION CONSTANTS
SCREEN_SIZE = 1000
FPS = 300

# PHYSICAL CONSTANTS
G = 6.6743e-11 # Gravitational Constant
SOLAR_MASS = 1.989e30
SECONDS_PER_YEAR = 3.154e7
METERS_PER_LY = 9.461e15

# COLORS
BLACK = (0, 0, 0)
GREY = (50, 50, 50)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)


# DATA SETS
solar_system_bodies = [
    # [Mass, Distance, X-pos, Y-pos, U-vel, V-vel]
    [1.9885e30, 0.0, 0.0, 0.0, 0.0, 0.0],  # Sun
    [3.3011e23, 5.7909e10, -3.7073e10, -4.4486e10, 36776.81, -30648.19],   # Mercury
    [4.8675e24, 1.0821e11,  1.0688e11,  1.6935e10, -5480.87,  34589.74],   # Venus
    [5.9722e24, 1.4960e11, -2.3430e10,  1.4775e11, -29417.59, -4664.84],   # Earth
    [6.4171e23, 2.2794e11,  3.8186e10,  2.2472e11, -23788.87,  4042.44],   # Mars
    [1.8982e27, 7.7855e11, -6.6100e10, -7.7574e11,  13009.23, -1108.51],   # Jupiter
    [5.6834e26, 1.4335e12, -6.3712e11, -1.2841e12,  8619.45,  -4276.52],   # Saturn
    [8.6810e25, 2.8725e12,  2.2382e12, -1.8005e12,  4260.63,   5296.24],   # Uranus
    [1.0241e26, 4.4951e12,  3.8410e12,  2.3352e12, -2822.75,   4642.98],   # Neptune
    [1.3030e22, 5.9064e12, -4.7575e12,  3.4912e12, -2791.73,  -3804.38]    # Pluto
]


# CLASSES
################################################################
# ----------------------------------------------------------------
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
        self.x_scale_factor = 1.0
        self.y_scale_factor = 1.0
        self.draw_radius = 0.0 # interger render pixel size (derived from mass)
        self.color = list(BLACK)
        self.color = list(WHITE)

        self.trailing_data_initial_point = [0.0, 0.0]
        self.trailing_data = []
        self.trailing_data_length = 1000 # how long is the tail

    # Physics calculation methods
    def update_acceleration(self, x_m, y_m, z_m, mass_m):
        """ CALCULATE NEW ACCELERATION (a = - Gm * r / ||r||^3) derived from ma = -GMm / r^2
        
        takes position (r) parameters and calculates the new acceration of M experienced by
        the orbiting body m. (a = - Gm * r / ||r||^3) derived from ma = -GMm / r^2
        """
        dx = self.x - x_m
        dy = self.y - y_m
        dz = self.z - z_m
        mag_r_cubed = ((dx**2) + (dy**2) + (dz**2) + (config.SOFTENING**2)) ** (3/2) # calculate mag of ||r||^3
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
        adtx = self.ax * config.dt 
        adty = self.ay * config.dt
        adtz = self.az * config.dt
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
        vdtx = self.vx * config.dt 
        vdty = self.vy * config.dt
        vdtz = self.vz * config.dt
        # add r + vdt
        self.x += vdtx 
        self.y += vdty
        self.z += vdtz

        # Scales the position coordinates to fit the screen size
        self.scale_x = self.x_scale_factor * SCREEN_SIZE * (self.x / config.BOX_DIMENSIONS)
        self.scale_y = self.y_scale_factor * SCREEN_SIZE * (self.y / config.BOX_DIMENSIONS)
        self.scale_z = SCREEN_SIZE * (self.z / config.BOX_DIMENSIONS)

        self.trailing_data_initial_point = [self.scale_x, self.scale_y]
        
        self.draw_radius = 1000 * (self.mass * (self.scale_z + 800) / SCREEN_SIZE / 1.5e29) # scales draw_radius with mass AND distance from viewer
        if self.draw_radius < 1.0:
            self.draw_radius = 1.0
        if self.draw_radius > 6.0:
            self.draw_radius = 6.0
        # self.draw_radius = 5.0

        # if self.scale_z >= 0.0 and self.scale_z <= SCREEN_SIZE:
        #     self.color[0] = abs(int(255 * (self.scale_z / SCREEN_SIZE))) # R-channel
        #     self.color[1] = abs(int(255 * (self.scale_z / SCREEN_SIZE))) # B-channel
        #     self.color[2] = abs(int(220 * (self.scale_z / SCREEN_SIZE))) # G-channel            

    def update_trailing_data(self):
        """"""
        # UPDATE TRAILING DATA LIST
        # Initial line
        if len(self.trailing_data) == 0:
            self.trailing_data.append([self.trailing_data_initial_point, [self.scale_x, self.scale_y]])
        
        elif len(self.trailing_data) < self.trailing_data_length:
            self.trailing_data.append([self.trailing_data[-1][1], [self.scale_x, self.scale_y]])
        
        else:
            del self.trailing_data[0]
            self.trailing_data.append([self.trailing_data[-1][1], [self.scale_x, self.scale_y]])            

    # Render to screen
    def draw(self, surface):
        """ Convert floats to integers ONLY during the rendering phase """
        render_pos = (int(self.scale_x), int(self.scale_y))
        pygame.draw.circle(surface, self.color, render_pos, self.draw_radius)

    def draw_trails(self, surface):
        trail_color = [0, 0, 0]
        trail_color_z = trail_color
        for i in self.trailing_data:
            pygame.draw.line(surface, trail_color_z, i[0], i[1], width=1)
            if trail_color_z[0] < config.TRAIL_COLOR[0]:
                trail_color[0] += 1
                trail_color[1] += 1
                trail_color[2] += 1
                # trail_color_z = [abs(int(trail_color[0]) * (self.scale_z / SCREEN_SIZE) * self.draw_radius/5),
                #                  abs(int(trail_color[1]) * (self.scale_z / SCREEN_SIZE) * self.draw_radius/5),
                #                  abs(int(trail_color[2]) * (self.scale_z / SCREEN_SIZE) * self.draw_radius/5)
                #                  ]
            else:
                pass


# POPULATION ENTITY CLASS
class ParticlePopulation:
    """ Generates and maintains a list of distinct particles of varying masses, positions
    and velocities 
    """
    def __init__(self):
        self.population = []

    def generate_random_particle(self, pos_range=(0, config.BOX_DIMENSIONS), vel_range=(-10, 10), mass_range=(1.5e29, 6.0e32)):
        """ Generates a single particle with random values within specified limits. """
        # mass = random.uniform(*mass_range) # use if we want a uniform IMF
        a_scale = mass_range[0] / SOLAR_MASS
        b_scale = mass_range[1] / SOLAR_MASS
        mass_scale = bounded_exponential_decay(a_scale, b_scale, lambd=2.35)
        mass = mass_scale * SOLAR_MASS        
        
        # Generate 3D/2D coordinates for position and velocity
        position = [random.uniform(*pos_range) for _ in range(3)]
        x = position[0]
        y = position[1]
        if config.THREE_D == True:
            z = position[2]
        else:
            z = config.BOX_DIMENSIONS

        velocity = [random.uniform(*vel_range) for _ in range(3)]
        vx = velocity[0]
        vy = velocity[1]
        if config.THREE_D == True:
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
    start_x = int(x_offset % config.CELL_SIZE)
    start_y = int(y_offset % config.CELL_SIZE)

    # Draw vertical lines from top to bottom
    for x in range(start_x, SCREEN_SIZE + int(config.CELL_SIZE), int(config.CELL_SIZE)):
        pygame.draw.line(screen, config.GRID_COLOR, (x, 0), (x, SCREEN_SIZE))
        
    # Draw horizontal lines from left to right
    for y in range(start_y, SCREEN_SIZE + int(config.CELL_SIZE), int(config.CELL_SIZE)):
        pygame.draw.line(screen, config.GRID_COLOR, (0, y), (SCREEN_SIZE, y))


# MAIN SIMULATION LOOP
################################################################
# should be a class!!

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

    # Instantiate our physics object(s)
    cluster = ParticlePopulation()
    # cluster.generate_multiple(count=POPULATION_SIZE)

    ####
    for body in solar_system_bodies:
        ss_object = (Particle(x=body[2], y=body[3], z=0.0, vx=body[4], vy=body[5], vz=0.0, mass=body[0]))
        cluster.population.append(ss_object)

    ####
    
    running = True
    while running:
        
        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            for k in range(len(cluster.population)):
                cluster.population[k].y += config.MOVEMENT_FACTOR
            y_offset += SCREEN_SIZE * (config.MOVEMENT_FACTOR / config.BOX_DIMENSIONS)

        if keys[pygame.K_DOWN]:
            for k in range(len(cluster.population)):
                cluster.population[k].y -= config.MOVEMENT_FACTOR
            y_offset -= SCREEN_SIZE * (config.MOVEMENT_FACTOR / config.BOX_DIMENSIONS)

        if keys[pygame.K_LEFT]:
            for k in range(len(cluster.population)):
                cluster.population[k].x += config.MOVEMENT_FACTOR
            x_offset += SCREEN_SIZE * (config.MOVEMENT_FACTOR / config.BOX_DIMENSIONS)

        if keys[pygame.K_RIGHT]:
            for k in range(len(cluster.population)):
                cluster.population[k].x -= config.MOVEMENT_FACTOR
            x_offset -= SCREEN_SIZE * (config.MOVEMENT_FACTOR / config.BOX_DIMENSIONS)

        ## unfortunately the way this is set up alters and affects the physics
        ## i need to totally rething the zoom from the ground up
        ## the arrow keys should be fine as is since theyre just applying translation
        if keys[pygame.K_EQUALS]:
            for k in range(len(cluster.population)):
                cluster.population[k].z += config.MOVEMENT_FACTOR
                cluster.population[k].x_scale_factor *= 1.01
                cluster.population[k].y_scale_factor *= 1.01
            config.CELL_SIZE = config.CELL_SIZE * 1.01

        if keys[pygame.K_MINUS]:
            for k in range(len(cluster.population)):
                cluster.population[k].z -= config.MOVEMENT_FACTOR
                cluster.population[k].x_scale_factor /= 1.01
                cluster.population[k].y_scale_factor /= 1.01
            config.CELL_SIZE = config.CELL_SIZE / 1.01


        # CALCULATE AND RENDER FPS
        current_fps = clock.get_fps()
        fps_text = font.render(f"FPS: {round(current_fps, 1)}", True, (255, 255, 255))


        # CALCULATE AND RENDER SIMULATION TIME ELAPSED
        t_elapsed += config.dt / SECONDS_PER_YEAR
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
            cluster.population[k].update_trailing_data()


        # RENDERING (Clear -> Draw -> Flip)
        screen.fill(config.BACKGROUND_COLOR)  # Clear screen with dark gray
        draw_grid_lines(screen, x_offset, y_offset)
        # _.draw here
        for i in cluster.population:
            if not any(keys):
                i.draw_trails(screen)
            else:
                i.trailing_data = []
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
## Code in some preset systems - i.e. a stable solar system (need to determine initial starting conditions
## Fix FPS issues. sim can run at whatever speed dt*CPS (calculations/sec) but only update the screen at 60 FPS
## ---- Define what we want on the screen - i.e. 100,000 yrs per sec
## ---- Years per rendered frame = target rate / FPS i.e. 100,000/60 = 1666.7 yrs
## ---- Now we need to figure out how many calculations per sec to match the dt time interval
## ---- rendered frame rate / dt should give the loop CPS
## Add redshift coloration
## Add write capibility for data capture (.csv) - allows for slower heavier processing
## - that can be loaded back in and "replayed" in real-time
## Create matplotlib capibilities and explore properties and phenomenon that
## - that emerge from the physics
## Use real-world GAIA data sets of stellar motions within known star clusters to predict future kinematics and
## - and measure various emergent properties (total orbital energy, mass(r) profile, freq of orbit captures)
## - WEBDA specifically for star cluster catalogs!
## Model gravitational contributions of IM and DM halos
## Determine if a star achieves escape velocity and remove star after a certain distance from the group
## Add button to re-center the cluster on the group
## Add a faint, fixed star background for aesthetics
## Model uniform mass density extending though space to infinity


## COMPLETED IMPROVEMENTS
##
## Code in IMF for initializing populaiton
## Rework with real-world units and scale to fit screen as needed
## Create ghost trails for particles
## Model in 3 dimensions
## Zoom and translational controls


## STELLAR COLOR SPECTRUM TRANSISITONS
##
## (255, 000, 000)    -->       RED    .
## (255, 255, 000)    -->    YELLOW    ..
## (000, 000, 255)    -->      BLUE    ....
## (255, 255, 255)    -->     WHITE    ........