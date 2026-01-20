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
# Game Variables
# ---------------------------
gorilla_x = 200
GROUND_Y = 350
gorilla_y = GROUND_Y - gorilla_height + 20
gorilla_vel = 5

# ---------------------------
# Gorilla AI Variables
# ---------------------------
gorilla_direction = "right"  # "right" or "left"
gorilla_steps_remaining = random.randint(60, 180)  # frames to walk in current direction
gorilla_pause_frames = 0  # frames to pause
gorilla_facing_right = True

# Pause duration range (5-8 seconds)
PAUSE_MIN_FRAMES = 5 * FPS
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
            if choice < 0.25:
                # Pause for random 5-8 seconds
                gorilla_pause_frames = random.randint(PAUSE_MIN_FRAMES, PAUSE_MAX_FRAMES)
            elif choice < 0.6:
                # Flip direction
                gorilla_direction = "left" if gorilla_direction == "right" else "right"
            # Reset steps for next movement burst
            gorilla_steps_remaining = random.randint(60, 180)

    # --- Edge Handling ---
    if gorilla_x <= 0:
        gorilla_direction = "right"
        gorilla_steps_remaining = random.randint(60, 180)
        gorilla_facing_right = True
    if gorilla_x >= SCREEN_WIDTH - gorilla_width:
        gorilla_direction = "left"
        gorilla_steps_remaining = random.randint(60, 180)
        gorilla_facing_right = False

    # --- Movement Logic ---
    keys = sim_keys  # use simulated keys
    if keys[pygame.K_LEFT] and gorilla_x > 0:
        gorilla_x -= gorilla_vel
    if keys[pygame.K_RIGHT] and gorilla_x < SCREEN_WIDTH - gorilla_width:
        gorilla_x += gorilla_vel

    # --- Drawing ---
    screen.fill((173, 216, 230))  # Fill in the sky
    pygame.draw.rect(screen, (140, 101, 62), (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))  # Draw the Ground
    screen.blit(palm_tree_sprite, (35, GROUND_Y - palm_tree_height + 57))  # Draw the Palm Tree Sprite
    screen.blit(palm_tree_sprite_left, (600, GROUND_Y - palm_tree_height + 57))  # Draw another Palm Tree Sprite
    screen.blit(palm_tree_sprite_left, (200, GROUND_Y - palm_tree_height + 57))  # Draw another Palm Tree Sprite
    screen.blit(palm_tree_sprite, (500, GROUND_Y - palm_tree_height + 57))  # Draw another Palm Tree Sprite
    if gorilla_facing_right: #Draw the Gorilla Sprite facing right
        screen.blit(gorilla_sprite_right, (gorilla_x, gorilla_y))
    else: #Draw the Gorilla Sprite facing left
        screen.blit(gorilla_sprite_left, (gorilla_x, gorilla_y))

    pygame.display.update()

# ---------------------------
# Quit
# ---------------------------
pygame.quit()
