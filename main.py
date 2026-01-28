import pygame
import random
from gorilla_tree_interaction import GorillaInteraction


# ---------------------------
# Setup / Initialization
# ---------------------------
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Autonomous Gorilla")
clock = pygame.time.Clock()
run_game = True


# ---------------------------
# Load & Prepare Ground Sprite
# ---------------------------
# Desired ground size on screen
# ---------------------------
ground_sprite = pygame.image.load("assets/ground_800x250 (1).png").convert_alpha()
GROUND_HEIGHT = 250
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT


# ---------------------------
# Load Idle Sprite & Set Dimensions
# ---------------------------
# This becomes our new "Master" reference for the gorilla's size
GORILLA_BASE_SCALE = 0.44  # Combined scale (original 0.10 * 0.70)
gorilla_idle_sprite = pygame.image.load("assets/gorilla_idle.png").convert_alpha()

# Calculate final dimensions based on the idle sprite
gorilla_width = int(gorilla_idle_sprite.get_width() * GORILLA_BASE_SCALE)
gorilla_height = int(gorilla_idle_sprite.get_height() * GORILLA_BASE_SCALE)

# Scale the actual idle sprite for drawing
gorilla_idle_sprite = pygame.transform.scale(gorilla_idle_sprite, (gorilla_width, gorilla_height))
gorilla_idle_right = gorilla_idle_sprite
gorilla_idle_left = pygame.transform.flip(gorilla_idle_sprite, True, False)


# ---------------------------
# Load Gorilla Walk Animation
# ---------------------------
GORILLA_WALK_SCALE = 0.70  # scale down to ~10% of original
GORILLA_WALK_FRAMES = 6
gorilla_walk_sheet = pygame.image.load("assets/gorilla_walking_alt.png").convert_alpha()

walk_sheet_width = gorilla_walk_sheet.get_width()
walk_sheet_height = gorilla_walk_sheet.get_height()
GORILLA_FRAME_WIDTH = walk_sheet_width // GORILLA_WALK_FRAMES
GORILLA_FRAME_HEIGHT = walk_sheet_height

gorilla_walk_frames = []

for i in range(GORILLA_WALK_FRAMES):
    frame = gorilla_walk_sheet.subsurface(
        pygame.Rect(i * GORILLA_FRAME_WIDTH, 0, GORILLA_FRAME_WIDTH, GORILLA_FRAME_HEIGHT)
    )

    # We now scale frames to match the master dimensions exactly
    frame = pygame.transform.scale(frame, (gorilla_width, gorilla_height))
    gorilla_walk_frames.append(frame)

gorilla_walk_frame_index = 0.0
GORILLA_ANIM_SPEED = 0.18


# ---------------------------
# Load Gorilla Interaction Animation
# ---------------------------
INTERACT_FRAMES = 6
INTERACT_SCALE = 0.35

interact_sheet = pygame.image.load("assets/gorilla_pounding.png").convert_alpha()

sheet_width = interact_sheet.get_width()
sheet_height = interact_sheet.get_height()
FRAME_WIDTH = sheet_width // INTERACT_FRAMES
FRAME_HEIGHT = sheet_height

gorilla_interact_frames = []

for i in range(INTERACT_FRAMES):
    frame = interact_sheet.subsurface(
        pygame.Rect(i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT)
    )


    frame = pygame.transform.scale(
        frame,
        (int(FRAME_WIDTH * INTERACT_SCALE),
         int(FRAME_HEIGHT * INTERACT_SCALE))
    )
    gorilla_interact_frames.append(frame)

# Create interaction controller
gorilla_interaction = GorillaInteraction(
    gorilla_interact_frames,
    anim_speed=0.25,
    repeat_count=4
)


# ---------------------------
# Load & Prepare Palm Tree  Sprite
# ---------------------------
palm_tree_sprite = pygame.image.load("assets/palm_tree.png").convert_alpha()
PALM_TREE_SCALE = 0.23  # scale down to ~19% of original
palm_tree_sprite = pygame.transform.scale(
    palm_tree_sprite,
    (int(palm_tree_sprite.get_width() * PALM_TREE_SCALE),
     int(palm_tree_sprite.get_height() * PALM_TREE_SCALE))
)
palm_tree_width = palm_tree_sprite.get_width()
palm_tree_height = palm_tree_sprite.get_height()
palm_tree_sprite_left = pygame.transform.flip(palm_tree_sprite, True, False)

# ---------------------------
# Load Tree Damage + Explosion + Stump Sprites (Independent Scaling)
# ---------------------------

TREE_DAMAGED_SCALE = 0.22     # <-- tweak freely
TREE_STUMP_SCALE   = 0.52     # <-- tweak freely
TREE_EXPLODE_SCALE = 0.6     # <-- tweak freely
# Explosion position tuning offsets
EXPLODE_X_OFFSET = 0     # tweak left/right
EXPLODE_Y_OFFSET = 0     # tweak up/down

# ---- Damaged Tree ----
tree_damaged_original = pygame.image.load("assets/palm_tree_damaged.png").convert_alpha()

tree_damaged_width  = int(tree_damaged_original.get_width()  * TREE_DAMAGED_SCALE)
tree_damaged_height = int(tree_damaged_original.get_height() * TREE_DAMAGED_SCALE)

tree_damaged_sprite = pygame.transform.scale(
    tree_damaged_original,
    (tree_damaged_width, tree_damaged_height)
)

# ---- Tree Stump ----
tree_stump_original = pygame.image.load("assets/palm_tree_stump.png").convert_alpha()

tree_stump_width  = int(tree_stump_original.get_width()  * TREE_STUMP_SCALE)
tree_stump_height = int(tree_stump_original.get_height() * TREE_STUMP_SCALE)

tree_stump_sprite = pygame.transform.scale(
    tree_stump_original,
    (tree_stump_width, tree_stump_height)
)

# ---- Explosion Animation ----
TREE_EXPLODE_FRAMES = 6
TREE_EXPLODE_ANIM_SPEED = 0.16

tree_explode_original = pygame.image.load("assets/palm_tree_explosion.png").convert_alpha()

explode_sheet_width  = tree_explode_original.get_width()
explode_sheet_height = tree_explode_original.get_height()
TREE_EXPLODE_FRAME_WIDTH = explode_sheet_width // TREE_EXPLODE_FRAMES

tree_explode_frames = []


for i in range(TREE_EXPLODE_FRAMES):
    frame = tree_explode_original.subsurface(
        pygame.Rect(
            i * TREE_EXPLODE_FRAME_WIDTH,
            0,
            TREE_EXPLODE_FRAME_WIDTH,
            explode_sheet_height
        )
    )

    scaled_width  = int(frame.get_width()  * TREE_EXPLODE_SCALE)
    scaled_height = int(frame.get_height() * TREE_EXPLODE_SCALE)

    frame = pygame.transform.scale(frame, (scaled_width, scaled_height))
    tree_explode_frames.append(frame)


# ---------------------------
# Explosion Frame Anchor Size (Prevents Jitter)
# ---------------------------
EXPLODE_ANCHOR_WIDTH = max(frame.get_width() for frame in tree_explode_frames)
EXPLODE_ANCHOR_HEIGHT = max(frame.get_height() for frame in tree_explode_frames)


# ---------------------------
# Palm Tree Objects
# ---------------------------
trees = [
    {"pos": (0,   GROUND_Y - palm_tree_height + 100), "state": "alive", "anim_index": 0.0, "explode_anchor": None},
    {"pos": (85,  GROUND_Y - palm_tree_height + 100), "state": "alive", "anim_index": 0.0, "explode_anchor": None},
    {"pos": (175, GROUND_Y - palm_tree_height + 100), "state": "alive", "anim_index": 0.0, "explode_anchor": None},
    {"pos": (290, GROUND_Y - palm_tree_height + 100), "state": "alive", "anim_index": 0.0, "explode_anchor": None},
    {"pos": (400, GROUND_Y - palm_tree_height + 100), "state": "alive", "anim_index": 0.0, "explode_anchor": None},
    {"pos": (515, GROUND_Y - palm_tree_height + 100), "state": "alive", "anim_index": 0.0, "explode_anchor": None},
    {"pos": (625, GROUND_Y - palm_tree_height + 100), "state": "alive", "anim_index": 0.0, "explode_anchor": None},
    {"pos": (700, GROUND_Y - palm_tree_height + 100), "state": "alive", "anim_index": 0.0, "explode_anchor": None},
]



# ---------------------------
# Load & Prepare Sunbird Sprite Sheet
# ---------------------------
SUNBIRD_SCALE = 0.128   # 10% of original size (tweak this)

NUM_FRAMES = 6
sunbird_sheet = pygame.image.load("assets/sunbird_6_frames.png").convert_alpha()

sheet_width = sunbird_sheet.get_width()
sheet_height = sunbird_sheet.get_height()
SUNBIRD_FRAME_WIDTH = sheet_width // NUM_FRAMES
SUNBIRD_FRAME_HEIGHT = sheet_height

sunbird_frames = []

for i in range(NUM_FRAMES):
    frame = sunbird_sheet.subsurface(
    pygame.Rect(i * SUNBIRD_FRAME_WIDTH, 0, SUNBIRD_FRAME_WIDTH, SUNBIRD_FRAME_HEIGHT)
    )

    # Scale each frame
    frame = pygame.transform.scale(
        frame,
        (int(SUNBIRD_FRAME_WIDTH * SUNBIRD_SCALE),
         int(SUNBIRD_FRAME_HEIGHT * SUNBIRD_SCALE))
    )

    sunbird_frames.append(frame)

SUNBIRD_FRAME_WIDTH = sunbird_frames[0].get_width()

sunbird_frame_index = 0.0

# ---------------------------
# Sunbird Variables
# ---------------------------
sunbird_x = -SUNBIRD_FRAME_WIDTH
SUNBIRD_MIN_Y = 20
SUNBIRD_MAX_Y = 170   # tweak this for how low the bird can fly
sunbird_y = random.randint(SUNBIRD_MIN_Y, SUNBIRD_MAX_Y)
sunbird_speed = 2
sunbird_direction = "right"
SUNBIRD_ANIM_SPEED = 0.20

# ---------------------------
# Game Variables
# ---------------------------
gorilla_x = 200
gorilla_y = GROUND_Y - gorilla_height + 60
gorilla_vel = 0.8

# Easter Egg Variables
typing_mode = False
user_input = ""
SECRET_WORD = "harambe"
EASTER_EGG = "easter_egg"
scripted_timer = 0  # To track how long the sequence has played

# Gorilla States
WALKING = "walking"
APPROACHING = "approaching"
INTERACTING = "interacting"

gorilla_state = WALKING
target_tree = None

# ---------------------------
# Gorilla AI Variables
# ---------------------------
gorilla_direction = "right"  # "right" or "left"
gorilla_steps_remaining = random.randint(60, 180)  # frames to walk in current direction
gorilla_pause_frames = 0  # frames to pause
gorilla_facing_right = True


# ---------------------------
# Gorilla Interaction Timer
# ---------------------------
INTERACT_MIN_TIME = 15 * FPS
INTERACT_MAX_TIME = 30 * FPS
interact_timer = random.randint(INTERACT_MIN_TIME, INTERACT_MAX_TIME)

trees_destroyed = 0
MAX_TREES_DESTROYED = 4


# Pause duration range (5-8 seconds)
PAUSE_MIN_FRAMES = 3 * FPS
PAUSE_MAX_FRAMES = 8 * FPS

# ---------------------------
# Game Loop
# ---------------------------
while run_game:
    clock.tick(FPS)

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_game = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                typing_mode = not typing_mode
                user_input = "" # Reset when toggling
            
            elif typing_mode:
                if event.key == pygame.K_RETURN:
                    if user_input.lower() == SECRET_WORD:
                        gorilla_state = EASTER_EGG
                    user_input = ""
                    typing_mode = False
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode


    # ---------------------------
    # Simulated Key State (AI Input) and Initialize interaction_frame
    # ---------------------------
    sim_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False}
    interaction_frame = None 
    # ---------------------------
    # Gorilla AI State Machine
    # ---------------------------
    
    if gorilla_state == EASTER_EGG:
        # 1. STOP all other movement logic
        sim_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False}
        
        # 2. Perform Scripted Actions
        scripted_timer += 1
        gorilla_y -= 2  # Gorilla starts floating away
        gorilla_x += random.randint(-5, 5) # Shaking effect
        
        # 3. Quit the game after 3 seconds (180 frames at 60 FPS)
        if scripted_timer > 180:
            run_game = False

    elif gorilla_state == WALKING:
        # Standard random walk logic
        if not gorilla_interaction.is_active():
            interact_timer -= 1

        # Check if it's time to destroy a tree
        if interact_timer <= 0 and trees_destroyed < MAX_TREES_DESTROYED:
            # Find the nearest alive tree
            alive_trees = [t for t in trees if t["state"] == "alive"]

            if alive_trees:
                # Calculate distances and find the closest one
                target_tree = min(alive_trees, key=lambda t: abs(t["pos"][0] - gorilla_x))
                gorilla_state = APPROACHING
            else:
                interact_timer = random.randint(INTERACT_MIN_TIME, INTERACT_MAX_TIME)

        # Random movement logic (your existing code)
        if gorilla_pause_frames > 0:
            gorilla_pause_frames -= 1
        else:
            if gorilla_steps_remaining > 0:
                if gorilla_direction == "right":
                    sim_keys[pygame.K_RIGHT] = True
                    gorilla_facing_right = True
                else:
                    sim_keys[pygame.K_LEFT] = True
                    gorilla_facing_right = False
                gorilla_steps_remaining -= 1
            else:
                choice = random.random()
                if choice < 0.33:
                    gorilla_pause_frames = random.randint(PAUSE_MIN_FRAMES, PAUSE_MAX_FRAMES)
                elif choice < 0.66:
                    gorilla_direction = "left" if gorilla_direction == "right" else "right"
                gorilla_steps_remaining = random.randint(30, 180)

    elif gorilla_state == APPROACHING:
        # Move toward target_tree
        tx = target_tree["pos"][0] # This is the tree's left edge
        
        # NEW LOGIC: (Tree Center) - (Half Gorilla Width)
        tree_center_x = tx + (palm_tree_width // 2)
        stop_x = tree_center_x - (gorilla_width // 2)
        
        if abs(gorilla_x - stop_x) > 2: # Lowered 5 to 2 for more precision
            if gorilla_x < stop_x:
                gorilla_x += gorilla_vel
                gorilla_facing_right = True
            else:
                gorilla_x -= gorilla_vel
                gorilla_facing_right = False
            
            # Use walking animation
            gorilla_walk_frame_index = (gorilla_walk_frame_index + GORILLA_ANIM_SPEED) % GORILLA_WALK_FRAMES
        else:
            # Reached the tree!
            gorilla_state = INTERACTING
            gorilla_interaction.start()

    elif gorilla_state == INTERACTING:
        # We assign it to a variable here so the drawing code below can see it
        interaction_frame, interaction_finished = gorilla_interaction.update()
        
        if interaction_finished:
            target_tree["state"] = "damaged"
            target_tree["anim_index"] = 0.0

            trees_destroyed += 1
            interact_timer = random.randint(INTERACT_MIN_TIME, INTERACT_MAX_TIME)
            gorilla_state = WALKING
            interaction_frame = None



    # ---------------------------
    # Calculate Movement State
    # ---------------------------
    # The gorilla is "moving" if it's currently walking (not paused) or approaching a tree
    gorilla_is_moving = (
        (gorilla_state == WALKING and gorilla_pause_frames == 0 and (sim_keys[pygame.K_LEFT] or sim_keys[pygame.K_RIGHT])) 
        or gorilla_state == APPROACHING
    )

    # ---------------------------
    # Update Gorilla Walk Animation
    # ---------------------------
    if gorilla_is_moving and gorilla_state != INTERACTING:
        gorilla_walk_frame_index = (
            gorilla_walk_frame_index + GORILLA_ANIM_SPEED
        ) % GORILLA_WALK_FRAMES
    else:
        gorilla_walk_frame_index = 0

    # --- Edge Handling ---
    if gorilla_x <= 0:
        gorilla_direction = "right"
        gorilla_steps_remaining = random.randint(30, 180)
        gorilla_facing_right = True
    if gorilla_x >= SCREEN_WIDTH - gorilla_width:
        gorilla_direction = "left"
        gorilla_steps_remaining = random.randint(30, 180)
        gorilla_facing_right = False

    # --- Movement Logic ---
    keys = sim_keys  # use simulated keys
    if keys[pygame.K_LEFT] and gorilla_x > 0:
        gorilla_x -= gorilla_vel
    if keys[pygame.K_RIGHT] and gorilla_x < SCREEN_WIDTH - gorilla_width:
        gorilla_x += gorilla_vel

    # ---------------------------
    # Sunbird Movement + Animation
    # ---------------------------
    if sunbird_direction == "right":
        sunbird_x += sunbird_speed
        if sunbird_x > SCREEN_WIDTH:
            sunbird_direction = "left"
            sunbird_y = random.randint(SUNBIRD_MIN_Y, SUNBIRD_MAX_Y)
    else:
        sunbird_x -= sunbird_speed
        if sunbird_x < -SUNBIRD_FRAME_WIDTH:
            sunbird_direction = "right"
            sunbird_y = random.randint(SUNBIRD_MIN_Y, SUNBIRD_MAX_Y)

    sunbird_frame_index = (sunbird_frame_index + SUNBIRD_ANIM_SPEED) % NUM_FRAMES
    current_sunbird_frame = sunbird_frames[int(sunbird_frame_index)]

    if sunbird_direction == "left":
        current_sunbird_frame = pygame.transform.flip(
            current_sunbird_frame, True, False
        )

    # ---------------------------
    # Tree Animation Updates
    # ---------------------------
    for tree in trees:

        # Damaged stays visible briefly before exploding
        if tree["state"] == "damaged":
            tree["anim_index"] += 1

        if tree["anim_index"] >= 15:
            tree["state"] = "exploding"
            tree["anim_index"] = 0.0

            # Lock explosion anchor once
            x = tree["pos"][0]
            anchor_x = x + (palm_tree_width // 2)
            anchor_y = GROUND_Y - palm_tree_height + 275

            tree["explode_anchor"] = (anchor_x, anchor_y)



        elif tree["state"] == "exploding":
            tree["anim_index"] += TREE_EXPLODE_ANIM_SPEED

            if tree["anim_index"] >= TREE_EXPLODE_FRAMES:
                tree["state"] = "stump"
                tree["anim_index"] = 0.0
                tree["explode_anchor"] = None



    # --- Drawing ---
    screen.fill((173, 216, 230))  # Fill in the sky


    # Draw Indicator Light (Top Right)
    if typing_mode:
        pygame.draw.circle(screen, (255, 255, 0), (770, 30), 10) # Yellow for typing
    if gorilla_state == EASTER_EGG:
        pygame.draw.circle(screen, (255, 0, 0), (770, 30), 10)   # Red for active script

    # Draw Palm Trees + Stumps + Explosions
    for i, tree in enumerate(trees):

        x = tree["pos"][0]

        # --- Explosion animation ---
        if tree["state"] == "exploding":
            frame = tree_explode_frames[int(tree["anim_index"])]

            anchor_x, anchor_y = tree["explode_anchor"]

            explode_x = anchor_x - (frame.get_width() // 2)
            explode_y = anchor_y - (frame.get_height() // 2)

            screen.blit(frame, (explode_x, explode_y))





        # --- Damaged tree ---
        elif tree["state"] == "damaged":
            damaged_y = GROUND_Y - tree_damaged_sprite.get_height() + 100
            damaged_x = x + (palm_tree_width // 2) - (tree_damaged_sprite.get_width() // 2)
            screen.blit(tree_damaged_sprite, (damaged_x, damaged_y))


        # --- Stump ---
        elif tree["state"] == "stump":
            stump_x = x + (palm_tree_width // 2) - (tree_stump_sprite.get_width() // 2)
            stump_y = GROUND_Y - tree_stump_sprite.get_height() + 32
            screen.blit(tree_stump_sprite, (stump_x, stump_y))


        # --- Normal tree ---
        elif tree["state"] == "alive":
            sprite = palm_tree_sprite if i % 2 == 0 else palm_tree_sprite_left
            screen.blit(sprite, tree["pos"])





    # Draw the Ground Sprite
    screen.blit(ground_sprite, (-150, GROUND_Y))  


    # Draw Sunbird
    screen.blit(current_sunbird_frame, (sunbird_x, sunbird_y))

    # --- Drawing Gorilla ---
    current_gorilla_frame = None

    if gorilla_state == INTERACTING:
        # interaction_frame was already set inside the "elif gorilla_state == INTERACTING" block
        current_gorilla_frame = interaction_frame
        if current_gorilla_frame is None:
            current_gorilla_frame = gorilla_idle_right
    elif gorilla_is_moving:
        current_gorilla_frame = gorilla_walk_frames[int(gorilla_walk_frame_index)]
    else:
        current_gorilla_frame = gorilla_idle_right

    # Flip the frame if facing left
    if not gorilla_facing_right:
        current_gorilla_frame = pygame.transform.flip(current_gorilla_frame, True, False)

    # Draw the Gorilla
    draw_y = GROUND_Y - current_gorilla_frame.get_height() + 38
    screen.blit(current_gorilla_frame, (gorilla_x, draw_y))


    pygame.display.update()


# ---------------------------
# Quit
# ---------------------------
pygame.quit()