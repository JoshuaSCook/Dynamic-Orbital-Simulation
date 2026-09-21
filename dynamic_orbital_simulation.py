import pygame
import sys
import random

# SETUP & CONFIGURATION CONSTANTS
WIDTH, HEIGHT = 800, 800
FPS = 60

# GLOBAL PHYSICAL CONSTANTS
G = 1.0 # 6.6743e-11 Gravitational Constant
#IMF(m) = m**-2.35
dt = 0.25 # Time interval
softening = 25.0





# PHYSICS ENTITY CLASS
class Particle:
    """ Tracks precision physical attributes and updates state """
    def __init__(self, x, y, vx, vy, mass):
        # Always use floating-point numbers for physics calculations
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.ax = 0.0
        self.ay = 0.0
        self.mass = float(mass)
        self.radius = float(mass / 3) # interger render pixel size (derived from mass)

    def __repr__(self):
        return str([round(self.x, 2), round(self.y, 2), round(self.vx, 2), round(self.vy, 2), round(self.mass, 2)])
    
    # Physics calculation methods
    def update_acceleration(self, x_m, y_m, vx_m, vy_m, mass_m):
        """ CALCULATE NEW ACCELERATION (a = - GM * r / ||r||^3) derived from ma = -GMm / r^2
        
        takes position (r) parameters and calculates the new acceration experienced by
        the orbiting body. (a = - GM * r / ||r||^3) derived from ma = -GMm / r^2
        """
        dx = self.x - x_m
        dy = self.y - y_m
        mag_r_cubed = ((dx**2) + (dy**2) + softening) ** (3/2) # calculate mag of ||r||^3
        a_constants = (-1) * G * mass_m / mag_r_cubed # define constants
        self.ax += dx * a_constants # multiply dx by constants to get a
        self.ay += dy * a_constants # multiply dy by constants to get a

    def update_velocity(self):
        """ CALCULATE NEW VELOCITY (v = v + a * dt)

        takes velocity (v), acceleration (a) and dt (time interval) and calculates the new
        velocity of the orbiting body. (v = v + a * dt)
        """
        adtx = self.ax * dt # multiply a * dt
        adty = self.ay * dt
        self.vx += adtx # add v + adt
        self.vy += adty

    def update_position(self):
        """ CALCULATE NEW POSITION (r = r + v * dt)

        takes position (r), velocity (v) and dt (time interval) and calculates the new
        velocity of the orbiting body. (r = r + v * dt)
        """
        vdtx = self.vx * dt # multiply v * dt
        vdty = self.vy * dt
        self.x += vdtx # add r + vdt
        self.y += vdty # add r + vdt

    # Position update
    def update_position(self):
        """ Move the particle based on current velocity """
        self.x += self.vx
        self.y += self.vy

    # Render to screen
    def draw(self, surface):
        """ Convert floats to integers ONLY during the rendering phase """
        render_pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, (0, 150, 255), render_pos, self.radius)




# POPULATION ENTITY CLASS
class ParticlePopulation:
    """ Generates and maintains a list of distinct particles of varying masses, positions and velocities """
    def __init__(self):
        self.population = []

    def __repr__(self):
        return str(self.population)

    def generate_random_particle(self, pos_range=(0, 800), vel_range=(-0.1, 0.1), mass_range=(0.5, 10.0)):
        """ Generates a single particle with random values within specified limits. """
        mass = random.uniform(*mass_range)
        
        # Generate 2D coordinates for position and velocity
        position = [random.uniform(*pos_range) for _ in range(2)]
        x = position[0]
        y = position[1]

        velocity = [random.uniform(*vel_range) for _ in range(2)]
        vx = velocity[0]
        vy = velocity[1]

        # Generates new partical and adds it to the population
        new_particle = Particle(x, y, vx, vy, mass)
        self.population.append(new_particle)

    def generate_multiple(self, count, **kwargs):
        """ Helper to generate many particles at once. """
        for i in range(count):
            self.generate_random_particle(**kwargs)





# MAIN SIMULATION LOOP
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DYNAMIC ORBITAL SIMULATION")
    clock = pygame.time.Clock()

    # Instantiate our physics object(s)
    cluster = ParticlePopulation()
    cluster.generate_multiple(count=300)

    large_star = (Particle(x=400.0, y=600.0, vx=0.0, vy=0.0, mass=20.0))
    cluster.population.append(large_star)
    
    running = True
    while running:
        # A. EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # B. PHYSICS & LOGIC UPDATES
        ## class methods to run calculations and update new positions and velocities
        for i in range(len(cluster.population)):
            for j in range(len(cluster.population)):
                if i != j:
                    cluster.population[i].update_acceleration(cluster.population[j].x, cluster.population[j].y, cluster.population[j].vx, cluster.population[j].vy, cluster.population[j].mass)

        for k in range(len(cluster.population)):
            cluster.population[k].update_velocity()
            cluster.population[k].update_position()
            cluster.population[k].ax = 0.0
            cluster.population[k].ay = 0.0



        # C. RENDERING (Clear -> Draw -> Flip)
        screen.fill((30, 30, 30))  # Clear screen with dark gray
        ## _.draw here
        for i in cluster.population:
                    i.draw(screen)
        pygame.display.flip()      # Refresh display

        # D. TIME STEP CONTROL
        clock.tick(FPS)  # Maintain steady 60 frames per second

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()