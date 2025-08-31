from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

camera_pos = (0, 500, 500)
camera_angle = 0
camera_height = 200
camera_distance = 200
camera_mode = "third_person"

player_pos = [0, 0, 30]
player_angle = 180
player_life = 5
player_speed = 10
player_is_dead = False

game_score = 0
bullets_missed = 0
auto_target_mode = False
fovY = 100
GRID_LENGTH = 5000
win = False

LEVEL_SCORE = 10
current_level = 1
player_speed_increment = 3
enemy_speed_increment = 0.2

god_mode_active = False
god_mode_kills_remaining = 0
god_mode_collisions_remaining = 0 
god_mode_used_this_level = False
GOD_MODE_KILLS = 5
god_mode_message = ""  
message_timer = 0   
auto_message_text = ""
auto_message_timer = 0
paused = False
pause_message = ""  
pause_message_timer = 0  
level_up_message = "" 
level_up_message_timer = 0  

BUILDINGS_PER_SIDE = 10
BUILDING_MIN_HEIGHT = 500
BUILDING_MAX_HEIGHT = 1200

bullets = []
bullet_speed = 70
MAX_BULLETS = 10

enemies = []
enemy_speed = 0.5
enemy_pulse = 0
enemy_pulse_direction = 1

TREE_COUNT = 300
TREE_POSITIONS = []

PILLAR_POSITIONS = [
    (-GRID_LENGTH + 500, -GRID_LENGTH + 500, "health"),
    ( GRID_LENGTH - 500,  GRID_LENGTH - 500, "ammo")     
]


godmode_last_fire_time = 0
godmode_rotation_speed = 1
godmode_fire_interval = 0.25

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_grid():
    glBegin(GL_QUADS)

    grid_size = 30
    quad_length = (2 * GRID_LENGTH) / grid_size

    for row in range(grid_size):
        for col in range(grid_size):
            x_start = -GRID_LENGTH + col * quad_length
            x_end = x_start + quad_length
            y_start = -GRID_LENGTH + row * quad_length
            y_end = y_start + quad_length

            if (row + col) % 2 == 0:
                glColor3f(0.13, 0.33, 0.13)
            else:
                glColor3f(0.18, 0.55, 0.34)

            glVertex3f(x_start, y_end, 0)
            glVertex3f(x_end, y_end, 0)
            glVertex3f(x_end, y_start, 0)
            glVertex3f(x_start, y_start, 0)

    glEnd()
        
def draw_pillars():
    for (px, py, ptype) in PILLAR_POSITIONS:
        if ptype == "health":
            glColor3f(0.0, 1.0, 0.0)  # green
        elif ptype == "ammo":
            glColor3f(1.0, 1.0, 0.0)  # yellow
        glPushMatrix()
        glTranslatef(px, py, 0)
        glScalef(60, 60, 1000) 
        glutSolidCube(1.0)
        glPopMatrix()

def generate_buildings_continuous():
    global BUILDING_POSITIONS
    BUILDING_POSITIONS = []

    segment_length = (2 * GRID_LENGTH) / BUILDINGS_PER_SIDE

    for side in ["north", "south", "east", "west"]:
        for i in range(BUILDINGS_PER_SIDE):
            height = random.randint(BUILDING_MIN_HEIGHT, BUILDING_MAX_HEIGHT)
            color = (random.uniform(0.1, 0.5), random.uniform(0.1, 0.5), random.uniform(0.1, 0.5))

            if side == "north":
                x = -GRID_LENGTH + i * segment_length + segment_length/2
                y = GRID_LENGTH
                width = segment_length
                depth = 200
            elif side == "south":
                x = -GRID_LENGTH + i * segment_length + segment_length/2
                y = -GRID_LENGTH
                width = segment_length
                depth = 200
            elif side == "east":
                x = GRID_LENGTH
                y = -GRID_LENGTH + i * segment_length + segment_length/2
                width = 200
                depth = segment_length
            else:  # west
                x = -GRID_LENGTH
                y = -GRID_LENGTH + i * segment_length + segment_length/2
                width = 200
                depth = segment_length

            BUILDING_POSITIONS.append([x, y, width, depth, height, color])

def draw_buildings_continuous():
    glPushMatrix()
    for b in BUILDING_POSITIONS:
        x, y, width, depth, height, color = b
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(x, y, height / 2)
        glScalef(width, depth, height)
        glutSolidCube(1.0)
        glPopMatrix()
        
        glColor3f(0.0, 0.0, 0.0) 
        rows = max(2, int(height / 150)) 
        cols = max(2, int(width / 150)) 
        window_w = width / cols * 0.5
        window_h = height / rows * 0.5
        window_d = 10

        for row in range(rows):
            wz = (row + 0.5) * (height / rows)

            # North side
            for col in range(cols):
                wx = x - width/2 + (col + 0.5) * (width / cols)
                wy = y + depth/2 + 0.1
                glPushMatrix()
                glTranslatef(wx, wy, wz)
                glScalef(window_w, window_d, window_h)
                glutSolidCube(1)
                glPopMatrix()

            # South side
            for col in range(cols):
                wx = x - width/2 + (col + 0.5) * (width / cols)
                wy = y - depth/2 - 0.1
                glPushMatrix()
                glTranslatef(wx, wy, wz)
                glScalef(window_w, window_d, window_h)
                glutSolidCube(1)
                glPopMatrix()

            # East side
            for col in range(cols):
                wx = x + width/2 + 0.1
                wy = y - depth/2 + (col + 0.5) * (depth / cols)
                glPushMatrix()
                glTranslatef(wx, wy, wz)
                glScalef(window_d, window_w, window_h)
                glutSolidCube(1)
                glPopMatrix()

            # West side
            for col in range(cols):
                wx = x - width/2 - 0.1
                wy = y - depth/2 + (col + 0.5) * (depth / cols)
                glPushMatrix()
                glTranslatef(wx, wy, wz)
                glScalef(window_d, window_w, window_h)
                glutSolidCube(1)
                glPopMatrix()
    glPopMatrix()


    
def check_building_collision(new_x, new_y, buffer=50):
    for b in BUILDING_POSITIONS:
        x, y, width, depth, height, color = b
        
        x_min = x - width/2 - buffer
        x_max = x + width/2 + buffer
        y_min = y - depth/2 - buffer
        y_max = y + depth/2 + buffer
        
        if x_min <= new_x <= x_max and y_min <= new_y <= y_max:
            return True
    return False

def draw_player():
    glPushMatrix() 
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 0, 1)
    
    if not player_is_dead:
        # Head
        glColor3f(0.7, 0.42, 0.22)  # skin color
        glPushMatrix()
        glTranslatef(0, 0, 40)
        glScalef(25, 25, 25)
        glutSolidCube(1.0)
        glPopMatrix()

        # Body
        glColor3f(0.4, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(0, 0, 15)
        glScalef(20, 25, 30)
        glutSolidCube(1.0)
        glPopMatrix()

        # Leg 1
        glColor3f(0.0, 0.0, 0.8)
        glPushMatrix()
        glTranslatef(0, -10, -20)
        glRotatef(180, 1, 0, 0)
        glScalef(10, 10, 35)
        glutSolidCube(1.0)
        glPopMatrix()

        # Leg 2
        glPushMatrix()
        glTranslatef(0, 10, -20)
        glRotatef(180, 1, 0, 0)
        glScalef(10, 10, 35)
        glutSolidCube(1.0)
        glPopMatrix()
          
        # Arm 1    
        glColor3f(0.94, 0.81, 0.70)  
        glPushMatrix()
        glTranslatef(10, -15, 30)
        glRotatef(90, 0, 1, 0) 
        glScalef(8, 8, 35)
        glutSolidCube(1.0)
        glPopMatrix()  
        
        # Arm 2
        glColor3f(0.94, 0.81, 0.70)  
        glPushMatrix()
        glTranslatef(10, 15, 30)
        glRotatef(90, 0, 1, 0)
        glScalef(8, 8, 35)
        glutSolidCube(1.0)
        glPopMatrix()  

        # Gun
        glColor3f(0.5, 0.5, 0.5)
        glPushMatrix()
        glTranslatef(10, 0, 30)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 8, 2, 70, 24, 2)
        glPopMatrix()
        
    else:
        glRotatef(-90, 0, 1, 0)
        # Head)
        glColor3f(0.7, 0.42, 0.22)  # skin color
        glPushMatrix()
        glTranslatef(0, 0, 40)
        glScalef(25, 25, 25)
        glutSolidCube(1.0)
        glPopMatrix()

        # Body
        glColor3f(0.4, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(0, 0, 15)
        glScalef(20, 25, 30)
        glutSolidCube(1.0)
        glPopMatrix()

        # Leg 1
        glColor3f(0.0, 0.0, 0.8)
        glPushMatrix()
        glTranslatef(0, -10, -20)
        glRotatef(180, 1, 0, 0)
        glScalef(10, 10, 35)
        glutSolidCube(1.0)
        glPopMatrix()

        # Leg 2
        glPushMatrix()
        glTranslatef(0, 10, -20)
        glRotatef(180, 1, 0, 0)
        glScalef(10, 10, 35)
        glutSolidCube(1.0)
        glPopMatrix()
          
        # Arm 1    
        glColor3f(0.94, 0.81, 0.70)  
        glPushMatrix()
        glTranslatef(10, -15, 30)
        glRotatef(90, 0, 1, 0) 
        glScalef(8, 8, 35)
        glutSolidCube(1.0)
        glPopMatrix()  
        
        # Arm 2
        glColor3f(0.94, 0.81, 0.70)  
        glPushMatrix()
        glTranslatef(10, 15, 30)
        glRotatef(90, 0, 1, 0)
        glScalef(8, 8, 35)
        glutSolidCube(1.0)
        glPopMatrix()  

        # Gun
        glColor3f(0.5, 0.5, 0.5)
        glPushMatrix()
        glTranslatef(25, 0, 30)
        glRotatef(90, 0, 1, 0)
        glScalef(10, 10, 70)
        glutSolidCube(1.0)
        glPopMatrix()

    glPopMatrix()

def draw_bullets():
    for i in bullets:
        glPushMatrix()
        glTranslatef(i[0], i[1], i[2])
        glColor3f(0.0, 0.0, 0.0)
        glutSolidCube(10)
        glPopMatrix()

def draw_enemies():
    for enemy in enemies:
        x, y, z, phase = enemy 
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Rotate enemies to face the player
        angle_to_player = math.degrees(math.atan2(player_pos[1] - y, player_pos[0] - x))
        glRotatef(angle_to_player - 90, 0, 0, 1)

        # Head
        glColor3f(0.0, 0.8, 0.0)  
        glPushMatrix()
        glTranslatef(0, 0, 60)
        glScalef(20, 20, 20)
        glutSolidCube(1)
        glPopMatrix()

        # Left eye
        glColor3f(1.0, 0.0, 0.0) 
        glPushMatrix()
        glTranslatef(-5, 10, 65)
        glScalef(5, 5, 5)
        glutSolidCube(1)
        glPopMatrix()

        # Right eye
        glColor3f(1.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(5, 10, 65)
        glScalef(5, 5, 5)
        glutSolidCube(1)
        glPopMatrix()

        # Body
        glColor3f(0.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(0, 0, 40)
        glScalef(20, 10, 30)
        glutSolidCube(1)
        glPopMatrix()

        # Left arm
        glColor3f(0.0, 0.5, 0.0)
        glPushMatrix()
        glTranslatef(-12, 0, 45)
        glScalef(7, 25, 7)
        glutSolidCube(1)
        glPopMatrix()

        # Right arm
        glPushMatrix()
        glTranslatef(12, 0, 45)
        glScalef(7, 25, 7)
        glutSolidCube(1)
        glPopMatrix()

        # Left leg
        glColor3f(0.0, 0.0, 0.8) 
        glPushMatrix()
        glTranslatef(-5, 0, 15)
        glScalef(7, 7, 25)
        glutSolidCube(1)
        glPopMatrix()

        # Right leg
        glPushMatrix()
        glTranslatef(5, 0, 15) 
        glScalef(7, 7, 25)
        glutSolidCube(1)
        glPopMatrix()

        glPopMatrix()

def Enemies():
    global enemies
    enemies = []
    for i in range(50):
        SpawnEnemy()

def SpawnEnemy():
    x = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
    y = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
    
    while abs(x - player_pos[0]) < 200 and abs(y - player_pos[1]) < 200:
        x = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        y = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
    
    base_z = 30
    phase = random.uniform(0, 2 * math.pi)  # random phase fo each enemy
    enemies.append([x, y, base_z, phase])
    
def generate_tree_positions(min_distance = 150):
    global TREE_POSITIONS
    TREE_POSITIONS = []
    attempts = 0
    while len(TREE_POSITIONS) < TREE_COUNT and attempts < TREE_COUNT * 20:
        x = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        y = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)

        too_close = False
        for (tx, ty) in TREE_POSITIONS:
            dx = x - tx
            dy = y - ty
            if math.sqrt(dx * dx + dy * dy) < min_distance:
                too_close = True
                break

        if not too_close:
            TREE_POSITIONS.append((x, y))

        attempts += 1


def draw_tree(x, y, trunk_height=110, trunk_radius=30, leaf_height=200, leaf_radius=100):
    # Trunk
    glColor3f(0.55, 0.27, 0.07) 
    glPushMatrix()
    glTranslatef(x, y, 0)
    gluCylinder(gluNewQuadric(), trunk_radius, trunk_radius, trunk_height, 20, 5)
    glPopMatrix()

    # Leaves
    glColor3f(0.0, 0.5, 0.0)
    glPushMatrix()
    glTranslatef(x, y, trunk_height)
    glRotatef(-90, 0, 0, 1)
    glutSolidCone(leaf_radius, leaf_height, 20, 20)
    glTranslatef(0, 0, trunk_height)
    glColor3f(0.0, 0.3, 0.0)
    glutSolidCone(leaf_radius * 0.6, leaf_height * 0.6, 20, 20)
    glTranslatef(0, 0, trunk_height - 50)
    glColor3f(0.0, 0.1, 0.0)
    glutSolidCone(leaf_radius * 0.4, leaf_height * 0.4, 20, 20)
    glPopMatrix()

def draw_all_trees():
    for pos in TREE_POSITIONS:
        draw_tree(pos[0], pos[1])
        
def check_tree_collision(new_x, new_y, radius = 70):
    for (tx, ty) in TREE_POSITIONS:
        dx = new_x - tx
        dy = new_y - ty
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < radius:
            return True
    return False

def steer_away_from_trees(x, y, avoid_radius = 120, strength = 1.0):
    ax, ay = 0.0, 0.0
    for (tx, ty) in TREE_POSITIONS:
        dx = x - tx
        dy = y - ty
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < avoid_radius and dist > 1:
            force = strength * (1.0 / dist - 1.0 / avoid_radius)
            ax += (dx / dist) * force * avoid_radius
            ay += (dy / dist) * force * avoid_radius
    return ax, ay

def FireBullet():
    if player_is_dead == True:
        return
    
    angle = math.radians(player_angle)
    direction_x = math.cos(angle)
    direction_y = math.sin(angle)

    gun_x = player_pos[0]+direction_x * 80
    gun_y = player_pos[1]+direction_y * 80
    gun_z = player_pos[2]+ 30
    
    bullets.append([gun_x, gun_y, gun_z, direction_x, direction_y, 0])
    
def UpdateBullets():
    global bullets, enemies, game_score, bullets_missed, god_mode_active, god_mode_kills_remaining
    bullets_to_remove = []
    
    for i, j in enumerate(bullets):
        j[0] += j[3] * bullet_speed
        j[1] += j[4] * bullet_speed
        
        if abs(j[0]) > GRID_LENGTH or abs(j[1]) > GRID_LENGTH:
            bullets_to_remove.append(i)
            if not god_mode_active:
                bullets_missed += 1
                print("Bullet Missed:", bullets_missed)
            continue

        for m, n in enumerate(enemies):
            # Previous bullet position
            prev_x = j[0] - j[3] * bullet_speed
            prev_y = j[1] - j[4] * bullet_speed
            prev_z = j[2]
            
            # Distance from enemy to bullet segment
            dx = n[0] - prev_x
            dy = n[1] - prev_y
            dz = n[2] - prev_z
            distance_to_segment = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if distance_to_segment < 60:
                bullets_to_remove.append(i)
                enemies.pop(m)
                SpawnEnemy()
                if not god_mode_active:
                    game_score += 1
                else:
                    god_mode_kills_remaining -= 1
                    game_score += 1
                    if god_mode_kills_remaining <= 0:
                        god_mode_active = False
                        print("God Mode Deactivated due to kill limit!")
                break
    
    for i in sorted(bullets_to_remove, reverse=True):
        if i < len(bullets):
            bullets.pop(i)

def UpdateEnemies():
    global enemies, player_life, player_is_dead, enemy_pulse, enemy_pulse_direction
    global god_mode_active, god_mode_kills_remaining, game_score
    
    time_now = time.time()
    
    i = 0
    while i < len(enemies):
        enemy = enemies[i]
        
        dx = player_pos[0] - enemy[0]
        dy = player_pos[1] - enemy[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            
            move_x = dx
            move_y = dy

            ax, ay = steer_away_from_trees(enemy[0], enemy[1], avoid_radius=120, strength=2.0)
            move_x += ax
            move_y += ay

            mag = math.sqrt(move_x*move_x + move_y*move_y)
            if mag > 0:
                move_x /= mag
                move_y /= mag

            enemy[0] += move_x * enemy_speed
            enemy[1] += move_y * enemy_speed
            enemy[3] = 1.0 + enemy_pulse

            base_z = 30
            amplitude = 10 
            speed = 2.0  
            phase = enemy[3] 
            enemy[2] = base_z + amplitude * math.sin(speed * time_now + phase)
            
            if distance < 60 and not player_is_dead:
                if not god_mode_active:
                    player_life -= 1
                    if player_life <= 0:
                        Game_Over()   
                else:
                    god_mode_kills_remaining -= 1
                    if god_mode_kills_remaining <= 0:
                        god_mode_active = False
                        print("God Mode Deactivated due to too many collisions!")        
                enemies.pop(i)
                SpawnEnemy()
                continue 
        i += 1 
        
def check_pillar_collision():
    global player_life, bullets, bullets_missed
    
    for (px, py, ptype) in PILLAR_POSITIONS:
        dx = player_pos[0] - px
        dy = player_pos[1] - py
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 100: 
            if ptype == "health":
                player_life = 5
            elif ptype == "ammo":
                bullets.clear()    
                if not god_mode_active:
                    bullets_missed = 0

def Game_Over():
    global player_is_dead
    player_is_dead = True

def Restart_Game():
    global player_pos, player_angle, player_life, player_is_dead
    global game_score, bullets_missed, bullets, auto_target_mode, camera_mode
    global current_level, player_speed, enemy_speed, enemies, enemy_pulse, enemy_pulse_direction
    global god_mode_active, god_mode_kills_remaining, god_mode_used_this_level
    global god_mode_message, message_timer, godmode_last_fire_time, god_mode_collisions_remaining
    global auto_message_text, auto_message_timer, win
    global TREE_POSITIONS

    player_pos = [0, 0, 30]
    player_angle = 180
    player_life = 5
    player_is_dead = False
    player_speed = 10
    
    game_score = 0
    bullets_missed = 0

    bullets = []
    auto_target_mode = False
    camera_mode = "third_person"

    current_level = 1
    enemy_speed = 0.5
    enemies = []
    enemy_pulse = 0
    enemy_pulse_direction = 1

    god_mode_active = False
    god_mode_kills_remaining = 0
    god_mode_collisions_remaining = 0
    god_mode_used_this_level = False
    god_mode_message = ""
    message_timer = 0
    godmode_last_fire_time = 0

    auto_message_text = ""
    auto_message_timer = 0
    
    win = False
    generate_tree_positions()
    generate_buildings_continuous()

    Enemies()

    
def update_level():
    global current_level, player_speed, enemy_speed, win, level_up_message, level_up_message_timer

    new_level = int((game_score // LEVEL_SCORE) + 1)
    if new_level > current_level:
        current_level = new_level
        player_speed = player_speed + player_speed_increment
        enemy_speed = enemy_speed + enemy_speed_increment
        level_up_message = "Leveled Up!"
        level_up_message_timer = 180 
        if current_level > 3:
            win = True
        print(f"Level Up! Current Level: {current_level}")
    

def Auto_Target_Mode_Activate():
    global player_angle, godmode_last_fire_time, game_score, LEVEL_SCORE
    if not auto_target_mode:
        return
    if game_score < LEVEL_SCORE:
        return
    speed = godmode_rotation_speed
    interval = godmode_fire_interval
    player_angle = (player_angle + speed) % 360

    angle_tolerance = 0.5
    for enemy in enemies:
        dx = enemy[0] - player_pos[0]
        dy = enemy[1] - player_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        if distance == 0:
            continue
        target_angle = math.degrees(math.atan2(dy, dx))
        angle_diff = (target_angle - player_angle + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360

        if abs(angle_diff) <= angle_tolerance:
            current_time = time.time()
            if current_time - godmode_last_fire_time > interval:
                FireBullet()
                print("Player Bullet Fired!")
                godmode_last_fire_time = current_time
            break

def keyboardListener(key, x, y):
    global player_pos, player_angle, auto_target_mode, bullets_missed, auto_message_text, auto_message_timer, current_level
    global god_mode_active, god_mode_kills_remaining, god_mode_used_this_level, god_mode_message, message_timer, LEVEL_SCORE, god_mode_collisions_remaining
    global paused, pause_message, pause_message_timer, camera_angle, camera_mode
    
    if not player_is_dead or key == b'r':
        if key == b'w':
            if not player_is_dead:     
                angle_rad = math.radians(player_angle)
                dx = math.cos(angle_rad) * player_speed
                dy = math.sin(angle_rad) * player_speed
                
                new_x = player_pos[0] + dx
                new_y = player_pos[1] + dy
                
                if abs(new_y) < GRID_LENGTH - 50 and abs(new_y) < GRID_LENGTH - 50 and not check_tree_collision(new_x, new_y)and not check_building_collision(new_x, new_y):
                    player_pos[1] = new_y
                    player_pos[0] = new_x
                    
        if key == b's':
            if not player_is_dead:
                angle_rad = math.radians(player_angle)
                dx = math.cos(angle_rad) * player_speed
                dy = math.sin(angle_rad) * player_speed
                
                new_x = player_pos[0] - dx
                new_y = player_pos[1] - dy
                
                if abs(new_y) < GRID_LENGTH - 50 and abs(new_y) < GRID_LENGTH - 0 and not check_tree_collision(new_x, new_y)and not check_building_collision(new_x, new_y):
                    player_pos[1] = new_y
                    player_pos[0] = new_x    
                    
        if key == b'a':
            if not player_is_dead and not auto_target_mode:
                player_angle = (player_angle + 5) % 360
                if camera_mode == "third_person":
                    camera_angle = player_angle + 180
        
        if key == b'd':
            if not player_is_dead and not auto_target_mode:
                player_angle = (player_angle - 5) % 360
                if camera_mode == "third_person":
                    camera_angle = player_angle + 180
                
        if key == b'g':
            if god_mode_active:
                god_mode_active = False
                god_mode_used_this_level = True
                god_mode_message = "God Mode Deactivated! You cannot use it again this level."
                message_timer = 180 
            else:
                if not god_mode_used_this_level or game_score >= (current_level - 1) * LEVEL_SCORE:
                    god_mode_active = True
                    god_mode_kills_remaining = GOD_MODE_KILLS
                    god_mode_collisions_remaining = GOD_MODE_KILLS
                    god_mode_used_this_level = True
                    god_mode_message = f"God Mode Activated! Kills Remaining: {god_mode_kills_remaining}"
                    message_timer = 180
                else:
                    god_mode_message = "Cannot activate God Mode yet. Reach next level first!"
                    message_timer = 180
        
        if key == b't':
            if not player_is_dead:
                if game_score >= LEVEL_SCORE:
                    auto_target_mode = not auto_target_mode
                    auto_message_text = "Auto Target Mode Activated!"
                else:
                    auto_message_text = "Can't be activated. Auto Target Mode Requires 10+ Score"
                auto_message_timer = 180
        
        if key == b'r':
            Restart_Game()
            
        if key == b'p':
            paused = not paused
            if paused:
                pause_message = "Game Paused"
            else:
                pause_message = "Game Resumed"
            pause_message_timer = 180 

def specialKeyListener(key, x, y):
    global camera_angle, camera_height
    
    if key == GLUT_KEY_UP:
        camera_height += 10
        if camera_height > 1000:
            camera_height = 1000
    
    if key == GLUT_KEY_DOWN:
        camera_height -= 10
        if camera_height < 100:
            camera_height = 100
    
    if key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle + 5) % 360
    
    if key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle - 5) % 360
        

def mouseListener(button, state, x, y):
    global camera_mode
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not player_is_dead:
            FireBullet()
            print("Player Bullet Fired!")
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if camera_mode == "third_person":
            camera_mode = "first_person"
        else:
            camera_mode = "third_person"

def GetTargetEnemy():
    nearest_enemy = None
    min_distance = float('inf')
    
    for i in enemies:
        dx = i[0] - player_pos[0]
        dy = i[1] - player_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < min_distance:
            min_distance = distance
            nearest_enemy = i
    
    return nearest_enemy

def update_camera():
    global camera_pos
    
    if camera_mode == "first_person":
        angle_rad = math.radians(player_angle)
        
        cam_x = player_pos[0] + math.cos(angle_rad) * 20
        cam_y = player_pos[1] + math.sin(angle_rad) * 20
        cam_z = player_pos[2] + 40
        
        camera_pos = (cam_x, cam_y, cam_z)
    else:
        angle_rad = math.radians(camera_angle)
        cam_x = player_pos[0] + math.cos(angle_rad) * camera_distance
        cam_y = player_pos[1] + math.sin(angle_rad) * camera_distance
        cam_z = camera_height
        camera_pos = (cam_x, cam_y, cam_z)    

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 7000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    update_camera()
    x, y, z = camera_pos
    z += 30
    
    if camera_mode == "first_person":
        angle_rad = math.radians(player_angle)
        look_x = player_pos[0] + math.cos(angle_rad) * 100
        look_y = player_pos[1] + math.sin(angle_rad) * 100
        look_z = player_pos[2] + 30
        gluLookAt(x, y, z, look_x, look_y, look_z, 0, 0, 1)
        
    else:
        gluLookAt(x, y, z, player_pos[0], player_pos[1], player_pos[2], 0, 0, 1)

def idle():
    global win, paused
    
    if win:
        glutPostRedisplay()
        return
    
    if not player_is_dead and (bullets_missed < 10 or god_mode_active) and not paused:
        UpdateBullets()
        UpdateEnemies()
        check_pillar_collision()
        
        if auto_target_mode:
            Auto_Target_Mode_Activate()
        
        update_level()    
            
    glutPostRedisplay()

def showScreen():
    global message_timer, god_mode_message, auto_message_timer, auto_message_text, win
    global pause_message_timer, pause_message, level_up_message_timer, level_up_message
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 700)
    glEnable(GL_DEPTH_TEST)
    setupCamera()
    if win:
        draw_text(420, 400, "YOU WIN!")
        draw_text(400, 370, "Press R to Restart")
        glutSwapBuffers()
        return
    draw_grid()
    draw_buildings_continuous()
    draw_pillars()
    draw_all_trees()
    draw_player()
    draw_bullets()
    draw_enemies()

    if not player_is_dead and bullets_missed < 10:
        draw_text(10, 770, f"Player Life Remaining: {player_life}")
        draw_text(10, 740, f"Game Score: {game_score}")
        draw_text(10, 710, f"Player Bullets Missed: {bullets_missed}")
        draw_text(800, 770, f"Current Level: {current_level}")
        
        if auto_message_timer > 0:
            draw_text(10, 650, auto_message_text)
            auto_message_timer -= 1
    
        if message_timer > 0 and god_mode_message:
            draw_text(10, 680, god_mode_message)
            message_timer -= 1
            if message_timer == 0:
                god_mode_message = ""
        
        if pause_message_timer > 0:
            draw_text(450, 770, pause_message)
            pause_message_timer -= 1
            if pause_message_timer == 0:
                pause_message = ""        
        
        if level_up_message_timer > 0:
            draw_text(800, 740, level_up_message)
            level_up_message_timer -= 1
            if level_up_message_timer == 0:
                level_up_message = ""        
    
    elif player_is_dead:
        draw_text(10, 770, f"Game is Over. Your Score is {game_score}.")
        draw_text(10, 740, 'Press  "R" to Restart The Game.')
    
    elif bullets_missed >= 10:
        draw_text(10, 770, "Missed too Many Bullets")
        draw_text(10, 740, 'Press  "R" to Restart The Game.')
        if not player_is_dead:
            Game_Over()  
            
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 700)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Zombie Warfare")
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    Enemies()
    generate_tree_positions()
    generate_buildings_continuous()
    
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glutMainLoop()

if __name__ == "__main__":

    main()

