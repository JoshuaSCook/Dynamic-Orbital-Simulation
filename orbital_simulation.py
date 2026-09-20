import pygame

def button(color=(0,0,0), width=0, height=0, x_pos=0, y_pos=0, quantity=0, multiplier=1):
    '''
    creates a button with parameters that define color, size and location. It also
    returns some calculated value of any chosen variable, in this case adding or
    subtracting 1 to the varible. Used to adjust the speed (fps) of the simulation.
    '''
    button_color = color
    if mouse[0] >= x_pos and mouse[0] <= x_pos + width and mouse[1] >= y_pos and mouse[1] <= y_pos + height:
        button_color = blue
        
        if click[0] == 1:
            button_color = (100, 100, 100)
            quantity += (1 * multiplier)
            
            if quantity <= 10:
                quantity = 10

    pygame.draw.rect(win, button_color, [x_pos, y_pos, width, height])
    return(round(quantity, 2))

def button2(color=(0,0,0), width=0, height=0, x_pos=0, y_pos=0, quantity=0, multiplier=1):
    '''
    creates a button with parameters that define color, size and location. It also
    returns some calculated value of any chosen variable, in this case adding or
    subtracting 1 to the varible. Used to adjust the speed (fps) of the simulation.
    '''
    button_color = color
    if mouse[0] >= x_pos and mouse[0] <= x_pos + width and mouse[1] >= y_pos and mouse[1] <= y_pos + height:
        button_color = blue
        
        if click[0] == 1:
            button_color = (100, 100, 100)
            quantity += (0.1 * multiplier)

    pygame.draw.rect(win, button_color, [x_pos, y_pos, width, height])
    return(quantity)

def calculate_acceleration(GM=1.0, r=[0.0,0.0]):
    '''
    takes position (r) parameters and calculates the new acceration experienced by
    the orbiting body. (a = - GM * r / ||r||^3) derived from ma = -GMm / r^2
    '''
    mag_r_cubed = (r[0] ** 2 + r[1] ** 2) ** (3/2) # calculate mag of ||r||^3
    a_constants = (-1) * GM / mag_r_cubed # define constants
    a = [i * a_constants for i in r] # multiply r by constants to get a
    return a

def calculate_velocity(v=[0.0,0.0], a=[0.0,0.0], dt=1.0):
    '''
    takes velocity (v), acceleration (a) and dt (time interval) and calculates the new
    velocity of the orbiting body. (v = v + a * dt)
    '''
    adt = [i * dt for i in a] # multiply a * dt
    v = [x + y for x, y in zip(v, adt)] # add v + adt
    return v

def calculate_position(r=[0.0,0.0], v=[0.0,0.0], dt=1.0):
    '''
    takes position (r), velocity (v) and dt (time interval) and calculates the new
    velocity of the orbiting body. (r = r + v * dt)
    '''
    vdt = [i * dt for i in v] # multiply v * dt
    r = [x + y for x, y in zip(r, vdt)] # add r + vdt
    return r

# RANDOM PROGRAM PARAMETERS
win_width = 1024 # px
win_height = 768 # px
fps = 30 # defines fps (calculation iterations per second)

# STARTING VALUES
r = [1.0, 0.0] # position
v = [0.0, -0.9] # velocity
GM = 1.0 # constant
t = 0.0 # time
dt = 0.025 # time interval

# DEFINES THE COORDINATE TRANSFORMATIONS (values --> pixels)
scale = 200 # pixels per pixel
shift = [win_width / 2, win_height / 2] # x, y coordinate shifts

# COLORS
black = (0, 0, 0)
grey = (50, 50, 50)
white = (255, 255, 255)
yellow = (255, 255, 0)
blue = (0, 0, 255)

trailing_data = []
trailing_data_length = 1000 # how long is the tail

# INITIATE PYGAME
pygame.init()
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("ORBITAL SIMULATION")
pygame.font.init()
myfont = pygame.font.SysFont('monospace', 15)

run = True
# MAIN GAME LOOP
while run:
    ms_per_frame = 1000 // fps # (truncates to nearest interger)
    pygame.time.delay(ms_per_frame) # times each frame according to set fps

    # ALLOWS US TO EXIT THE GAME
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # PHYSICS CALCULATIONS
    ################################################################   
    # CALCULATE NEW ACCELERATION (a = - GM * r / ||r||^3) derived from ma = -GMm / r^2
    a = calculate_acceleration(GM, r)

    # CALCULATE NEW VELOCITY (v = v + a * dt)
    v = calculate_velocity(v, a, dt)

    # CALCULATE NEW POSITION (r = r + v * dt)
    start_r = r
    r = calculate_position(r, v, dt)

    # UPDATE TIME
    t += dt # to keep track of total elapsed time

    # RENDERING STUFF
    ################################################################
    win.fill (black)
    
    # CONVERT CALCULATED VALUES TO PIXEL COORDINATES
    start_r_scale = [i * scale for i in start_r]
    start_r_display = [x + y for x, y in zip(shift, start_r_scale)]

    r_scale = [i * scale for i in r]
    r_display = [x + y for x, y in zip(shift, r_scale)]

    # UPDATE TRAILING DATA LIST
    if len(trailing_data) < trailing_data_length:
        trailing_data.append([start_r_display, r_display])
    else:
        del trailing_data[0]
        trailing_data.append([start_r_display, r_display])

    # RENDER GRID
    pygame.draw.line(win, grey, (0, shift[1]), (win_width, shift[1]), width=1) # x-axis
    pygame.draw.line(win, grey, (shift[0], 0), (shift[0], win_height), width=1) # y-axis

    # RENDER TRAILING LINE
    for i in trailing_data:
        pygame.draw.line(win, white, i[0], i[1], width=1)
    pygame.draw.line(win, black, trailing_data[-1][0], trailing_data[-1][1], width=1) # creates a gap between planet and trace

    # RENDER GRAPHICS
    pygame.draw.circle(win, yellow, (shift[0], shift[1]), 25) # draw the star
    pygame.draw.circle(win, blue, r_display, 10) # draw the planet
    
    # RENDER TEXT DATA
    x_label = myfont.render('      POSITION: x = ' + str(round(r[0], 2)), 1, white)
    win.blit(x_label, (0, 10))

    y_label = myfont.render('                y = ' + str(round(r[1], 2)), 1, white)
    win.blit(y_label, (0, 25))

    v_mag = ((v[0] ** 2 + v[1] ** 2) ** (0.5))
    v_label = myfont.render('      VELOCITY: ' + str(round(v_mag, 2)), 1, white)
    win.blit(v_label, (0, 55))

    a_mag = ((a[0] ** 2 + a[1] ** 2) ** (0.5))
    a_label = myfont.render('  ACCELERATION: ' + str(round(a_mag, 2)), 1, white)
    win.blit(a_label, (0, 70))

    # CALCULATE AND DISPLAY TOTAL ENERGY TO CHECK FOR CONSERVATION (E_tot is proportional to (1/2 v^2) - (1 / r))
    r_mag = (r[0] ** 2 + r[1] ** 2) ** (1/2)
    E = (1/2) * (v_mag ** 2) - (1 / r_mag)
    E_label = myfont.render('  TOTAL ENERGY: ' + str(round(E, 4)), 1, white)
    win.blit(E_label, (0, 85))

    # DRAW BUTTONS
    fps = button((0,0,200), 10, 10, win_width - 20, win_height - 55, fps, 1)
    fps = button((0,0,200), 10, 10, win_width - 20, win_height - 20, fps, -1)

    fps_label = myfont.render(str(fps) + ' FPS', 1, white)
    win.blit(fps_label, (win_width - 62, win_height - 40))

    v[0] = button2((0,0,200), 10, 10, win_width - 20, win_height - 155, v[0], 1)
    v[0] = button2((0,0,200), 10, 10, win_width - 20, win_height - 120, v[0], -1)

    delta_v_label = myfont.render(str(v[0]) + ' DELTA v', 1, white)
    win.blit(delta_v_label, (win_width - 142, win_height - 140))

    # RENDER
    pygame.display.update()

pygame.quit()
