import pygame
import sys

# SETUP & CONFIGURATION CONSTANTS
WIDTH, HEIGHT = 800, 600
FPS = 60

# GLOBAL PHYSICAL CONSTANTS
G = 6.6743e-11 # Gravitational Constant
#IMF(m) = m**-2.35

# PHYSICS ENTITY CLASS
class StarParticle:
    """ Tracks precision physical attributes and updates state """
    def __init__(self, x, y, vx, vy, mass):
        # Always use floating-point numbers for physics calculations
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.mass = float(mass)
        #self.radius = ##render pixel size (derived from mass)  
    
    # Physics calculation methods
    def calculate_acceleration(self):
        """ CALCULATE NEW ACCELERATION (a = - GM * r / ||r||^3) derived from ma = -GMm / r^2
        
        takes position (r) parameters and calculates the new acceration experienced by
        the orbiting body. (a = - GM * r / ||r||^3) derived from ma = -GMm / r^2
        """
        
        return a

    def calculate_velocity(self):
        """ CALCULATE NEW VELOCITY (v = v + a * dt)

        takes velocity (v), acceleration (a) and dt (time interval) and calculates the new
        velocity of the orbiting body. (v = v + a * dt)
        """

        return v

    def calculate_position(self):
        """ CALCULATE NEW POSITION (r = r + v * dt)

        takes position (r), velocity (v) and dt (time interval) and calculates the new
        velocity of the orbiting body. (r = r + v * dt)
        """

        return r

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



# MAIN SIMULATION LOOP
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Physics Simulation Blueprint")
    clock = pygame.time.Clock()

    # Instantiate our physics object(s)
    ## create list of particles
    
    running = True
    while running:
        # A. EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # B. PHYSICS & LOGIC UPDATES
        ## class methods to run calculations and update new positions and velocities


        # C. RENDERING (Clear -> Draw -> Flip)
        screen.fill((30, 30, 30))  # Clear screen with dark gray
        ## _.draw here
        pygame.display.flip()      # Refresh display

        # D. TIME STEP CONTROL
        clock.tick(FPS)  # Maintain steady 60 frames per second

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()