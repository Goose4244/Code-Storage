import pygame
import random

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
ground_sprite = pygame.image.load("ground_800x250 (1).png").convert_alpha()
GROUND_HEIGHT = 250
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT


# ---------------------------
# Load & Prepare Gorilla Sprite
# ---------------------------
gorilla_sprite = pygame.image.load("gorilla.png").convert_alpha()
GORILLA_SCALE = 0.10  # scale down to ~10% of original
gorilla_sprite = pygame.transform.scale(
    gorilla_sprite,
    (int(gorilla_sprite.get_width() * GORILLA_SCALE),
     int(gorilla_sprite.get_height() * GORILLA_SCALE))
)
gorilla_width = gorilla_sprite.get_width()
gorilla_height = gorilla_sprite.get_height()
gorilla_sprite_right = gorilla_sprite
gorilla_sprite_left = pygame.transform.flip(gorilla_sprite, True, False)


# ---------------------------
# Load Gorilla Walk Animation
# ---------------------------
GORILLA_WALK_SCALE = 0.70  # scale down to ~10% of original
GORILLA_WALK_FRAMES = 6
gorilla_walk_sheet = pygame.image.load("gorilla_walk.png").convert_alpha()

walk_sheet_width = gorilla_walk_sheet.get_width()
walk_sheet_height = gorilla_walk_sheet.get_height()
GORILLA_FRAME_WIDTH = walk_sheet_width // GORILLA_WALK_FRAMES
GORILLA_FRAME_HEIGHT = walk_sheet_height

gorilla_walk_frames = []

for i in range(GORILLA_WALK_FRAMES):
    frame = gorilla_walk_sheet.subsurface(
        pygame.Rect(i * GORILLA_FRAME_WIDTH, 0, GORILLA_FRAME_WIDTH, GORILLA_FRAME_HEIGHT)
    )

    # Scale to match your existing gorilla size
    scaled_width = int(gorilla_width * GORILLA_WALK_SCALE)
    scaled_height = int(gorilla_height * GORILLA_WALK_SCALE)

    frame = pygame.transform.scale(
    frame,
    (scaled_width, scaled_height)
    )

    gorilla_walk_frames.append(frame)

gorilla_walk_frame_index = 0.0
GORILLA_ANIM_SPEED = 0.18

# Gorilla Idle Sprite
gorilla_idle_scale = 0.70  # scale down to ~10% of original
gorilla_idle_sprite = pygame.image.load("gorilla_idle.png").convert_alpha()
gorilla_idle_sprite = pygame.transform.scale(
    gorilla_idle_sprite,
    (int(gorilla_width * gorilla_idle_scale), int(gorilla_height * gorilla_idle_scale))
)

gorilla_idle_right = gorilla_idle_sprite
gorilla_idle_left = pygame.transform.flip(gorilla_idle_sprite, True, False)


# ---------------------------
# Load & Prepare Palm Tree  Sprite
# ---------------------------
palm_tree_sprite = pygame.image.load("palm_tree.png").convert_alpha()
PALM_TREE_SCALE = 0.19  # scale down to ~19% of original
palm_tree_sprite = pygame.transform.scale(
    palm_tree_sprite,
    (int(palm_tree_sprite.get_width() * PALM_TREE_SCALE),
     int(palm_tree_sprite.get_height() * PALM_TREE_SCALE))
)
palm_tree_width = palm_tree_sprite.get_width()
palm_tree_height = palm_tree_sprite.get_height()
palm_tree_sprite_left = pygame.transform.flip(palm_tree_sprite, True, False)

# ---------------------------
# Load & Prepare Sunbird Sprite Sheet
# ---------------------------
SUNBIRD_SCALE = 0.10   # 10% of original size (tweak this)

NUM_FRAMES = 6
sunbird_sheet = pygame.image.load("sunbird_6_frames.png").convert_alpha()

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

# ---------------------------
# Gorilla AI Variables
# ---------------------------
gorilla_direction = "right"  # "right" or "left"
gorilla_steps_remaining = random.randint(60, 180)  # frames to walk in current direction
gorilla_pause_frames = 0  # frames to pause
gorilla_facing_right = True

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

    # --- Gorilla AI / Simulated Key Presses ---
    sim_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False}

    if gorilla_pause_frames > 0:
        gorilla_pause_frames -= 1  # paused, do nothing
    else:
        if gorilla_steps_remaining > 0:
            # Continue moving in current direction
            if gorilla_direction == "right":
                sim_keys[pygame.K_RIGHT] = True
                gorilla_facing_right = True
            else:
                sim_keys[pygame.K_LEFT] = True
                gorilla_facing_right = False
            gorilla_steps_remaining -= 1
        else:
            # Decide next action randomly
            choice = random.random()
            if choice < 0.33:
                # Pause for random 3-8 seconds
                gorilla_pause_frames = random.randint(PAUSE_MIN_FRAMES, PAUSE_MAX_FRAMES)
            elif choice < 0.66:
                # Flip direction
                gorilla_direction = "left" if gorilla_direction == "right" else "right"
            # Reset steps for next movement burst
            gorilla_steps_remaining = random.randint(30, 180)

        
        # ---------------------------
        # Gorilla Animation State
        # ---------------------------
        gorilla_is_moving = gorilla_pause_frames == 0 and (
            sim_keys[pygame.K_LEFT] or sim_keys[pygame.K_RIGHT]
        )

        if gorilla_is_moving:
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

    # --- Drawing ---
    screen.fill((173, 216, 230))  # Fill in the sky

    screen.blit(palm_tree_sprite, (35, GROUND_Y - palm_tree_height + 90))  # Draw the Palm Tree Sprite
    screen.blit(palm_tree_sprite_left, (600, GROUND_Y - palm_tree_height + 90))  # Draw another Palm Tree Sprite
    screen.blit(palm_tree_sprite_left, (200, GROUND_Y - palm_tree_height + 90))  # Draw another Palm Tree Sprite
    screen.blit(palm_tree_sprite, (500, GROUND_Y - palm_tree_height + 90))  # Draw another Palm Tree Sprite

    screen.blit(ground_sprite, (-150, GROUND_Y))  # Draw the Ground Sprite


    # Draw Sunbird
    screen.blit(current_sunbird_frame, (sunbird_x, sunbird_y))

    # Draw Gorilla
    if gorilla_is_moving:
        current_gorilla_frame = gorilla_walk_frames[int(gorilla_walk_frame_index)]
    else:
        current_gorilla_frame = gorilla_idle_right

    if not gorilla_facing_right:
        current_gorilla_frame = pygame.transform.flip(
            current_gorilla_frame, True, False
        )

    screen.blit(current_gorilla_frame, (gorilla_x, gorilla_y))

    pygame.display.update()


# ---------------------------
# Quit
# ---------------------------
pygame.quit()
