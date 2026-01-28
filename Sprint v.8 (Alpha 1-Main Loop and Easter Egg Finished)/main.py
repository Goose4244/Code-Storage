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
ground_sprite = pygame.image.load("ground_800x250 (1).png").convert_alpha()
GROUND_HEIGHT = 250
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT

# ---------------------------
# Load Idle Sprite & Set Dimensions
# ---------------------------
GORILLA_BASE_SCALE = 0.44  
gorilla_idle_sprite = pygame.image.load("gorilla_idle.png").convert_alpha()

gorilla_width = int(gorilla_idle_sprite.get_width() * GORILLA_BASE_SCALE)
gorilla_height = int(gorilla_idle_sprite.get_height() * GORILLA_BASE_SCALE)

gorilla_idle_sprite = pygame.transform.scale(gorilla_idle_sprite, (gorilla_width, gorilla_height))
gorilla_idle_right = gorilla_idle_sprite
gorilla_idle_left = pygame.transform.flip(gorilla_idle_sprite, True, False)

# ---------------------------
# Load Gorilla Walk Animation
# ---------------------------
GORILLA_WALK_SCALE = 0.70  
GORILLA_WALK_FRAMES = 6
gorilla_walk_sheet = pygame.image.load("gorilla_walking_alt.png").convert_alpha()

walk_sheet_width = gorilla_walk_sheet.get_width()
walk_sheet_height = gorilla_walk_sheet.get_height()
GORILLA_FRAME_WIDTH = walk_sheet_width // GORILLA_WALK_FRAMES
GORILLA_FRAME_HEIGHT = walk_sheet_height

gorilla_walk_frames = []
for i in range(GORILLA_WALK_FRAMES):
    frame = gorilla_walk_sheet.subsurface(pygame.Rect(i * GORILLA_FRAME_WIDTH, 0, GORILLA_FRAME_WIDTH, GORILLA_FRAME_HEIGHT))
    frame = pygame.transform.scale(frame, (gorilla_width, gorilla_height))
    gorilla_walk_frames.append(frame)

gorilla_walk_frame_index = 0.0
GORILLA_ANIM_SPEED = 0.18

# ---------------------------
# Load Gorilla Interaction Animation
# ---------------------------
INTERACT_FRAMES = 6
INTERACT_SCALE = 0.35
interact_sheet = pygame.image.load("gorilla_pounding.png").convert_alpha()
FRAME_WIDTH = interact_sheet.get_width() // INTERACT_FRAMES
FRAME_HEIGHT = interact_sheet.get_height()

gorilla_interact_frames = []
for i in range(INTERACT_FRAMES):
    frame = interact_sheet.subsurface(pygame.Rect(i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT))
    frame = pygame.transform.scale(frame, (int(FRAME_WIDTH * INTERACT_SCALE), int(FRAME_HEIGHT * INTERACT_SCALE)))
    gorilla_interact_frames.append(frame)

gorilla_interaction = GorillaInteraction(gorilla_interact_frames, anim_speed=0.25, repeat_count=4)

# --- Easter Egg Assets (Updated Scaling) ---
HUMAN_SCALE = 0.15  # Tweak this (0.1 to 0.2) to make them look shorter/taller
harambe_sleeping = pygame.image.load("harambe.png").convert_alpha()
harambe_sleeping = pygame.transform.scale(harambe_sleeping, (gorilla_width, gorilla_height))

# Load and scale the human sprites
scared_sprite = pygame.image.load("scared.png").convert_alpha()
scared_sprite = pygame.transform.scale(
    scared_sprite, 
    (int(scared_sprite.get_width() * HUMAN_SCALE), int(scared_sprite.get_height() * HUMAN_SCALE))
)

surprised_sprite = pygame.image.load("surprised.png").convert_alpha()
surprised_sprite = pygame.transform.scale(
    surprised_sprite, 
    (int(surprised_sprite.get_width() * HUMAN_SCALE), int(surprised_sprite.get_height() * HUMAN_SCALE))
)

character_x = -100
character_target_x = 50
# This ensures the human's feet are at the same "depth" as the gorilla's feet
character_y_offset = 38

# ---------------------------
# Load & Prepare Palm Tree Sprite
# ---------------------------
palm_tree_sprite = pygame.image.load("palm_tree.png").convert_alpha()
PALM_TREE_SCALE = 0.23  
palm_tree_sprite = pygame.transform.scale(palm_tree_sprite, (int(palm_tree_sprite.get_width() * PALM_TREE_SCALE), int(palm_tree_sprite.get_height() * PALM_TREE_SCALE)))
palm_tree_width = palm_tree_sprite.get_width()
palm_tree_height = palm_tree_sprite.get_height()
palm_tree_sprite_left = pygame.transform.flip(palm_tree_sprite, True, False)

# ---------------------------
# Load Tree Damage + Explosion + Stump Sprites
# ---------------------------
TREE_DAMAGED_SCALE = 0.22
TREE_STUMP_SCALE = 0.52
TREE_EXPLODE_SCALE = 0.6

tree_damaged_original = pygame.image.load("palm_tree_damaged.png").convert_alpha()
tree_damaged_sprite = pygame.transform.scale(tree_damaged_original, (int(tree_damaged_original.get_width() * TREE_DAMAGED_SCALE), int(tree_damaged_original.get_height() * TREE_DAMAGED_SCALE)))

tree_stump_original = pygame.image.load("palm_tree_stump.png").convert_alpha()
tree_stump_sprite = pygame.transform.scale(tree_stump_original, (int(tree_stump_original.get_width() * TREE_STUMP_SCALE), int(tree_stump_original.get_height() * TREE_STUMP_SCALE)))

TREE_EXPLODE_FRAMES = 6
TREE_EXPLODE_ANIM_SPEED = 0.16
tree_explode_original = pygame.image.load("palm_tree_explosion.png").convert_alpha()
tree_explode_frames = []
for i in range(TREE_EXPLODE_FRAMES):
    frame = tree_explode_original.subsurface(pygame.Rect(i * (tree_explode_original.get_width() // TREE_EXPLODE_FRAMES), 0, tree_explode_original.get_width() // TREE_EXPLODE_FRAMES, tree_explode_original.get_height()))
    frame = pygame.transform.scale(frame, (int(frame.get_width() * TREE_EXPLODE_SCALE), int(frame.get_height() * TREE_EXPLODE_SCALE)))
    tree_explode_frames.append(frame)

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
# Load & Prepare Sunbird
# ---------------------------
SUNBIRD_SCALE = 0.128
NUM_FRAMES = 6
sunbird_sheet = pygame.image.load("sunbird_6_frames.png").convert_alpha()
SUNBIRD_FRAME_WIDTH = sunbird_sheet.get_width() // NUM_FRAMES
sunbird_frames = []
for i in range(NUM_FRAMES):
    frame = sunbird_sheet.subsurface(pygame.Rect(i * SUNBIRD_FRAME_WIDTH, 0, SUNBIRD_FRAME_WIDTH, sunbird_sheet.get_height()))
    frame = pygame.transform.scale(frame, (int(frame.get_width() * SUNBIRD_SCALE), int(frame.get_height() * SUNBIRD_SCALE)))
    sunbird_frames.append(frame)

sunbird_x = -sunbird_frames[0].get_width()
sunbird_y = random.randint(20, 170)
sunbird_speed = 2
sunbird_direction = "right"
sunbird_frame_index = 0.0
SUNBIRD_ANIM_SPEED = 0.20

# ---------------------------
# Game Variables
# ---------------------------
gorilla_x = 200
gorilla_y = GROUND_Y - gorilla_height + 60
gorilla_vel = 0.8
typing_mode = False
user_input = ""
SECRET_WORD = "harambe"
EASTER_EGG = "easter_egg"
scripted_timer = 0 

WALKING, APPROACHING, INTERACTING = "walking", "approaching", "interacting"
gorilla_state = WALKING
target_tree = None
gorilla_direction = "right"
gorilla_steps_remaining = random.randint(60, 180)
gorilla_pause_frames = 0
gorilla_facing_right = True
interact_timer = random.randint(10 * FPS, 22 * FPS)
trees_destroyed = 0
MAX_TREES_DESTROYED = 4

# ---------------------------
# Game Loop
# ---------------------------
while run_game:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_game = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                typing_mode = not typing_mode
                user_input = ""
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

    sim_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False}
    interaction_frame = None 

    # --- Gorilla AI State Machine ---
    if gorilla_state == EASTER_EGG:
        scripted_timer += 1
        
        # Step 1: Gorilla moves to center, Character runs in
        if scripted_timer < 150:
            if character_x < character_target_x:
                character_x += 3
            
            center_x = (SCREEN_WIDTH // 2) - (gorilla_width // 2)
            if abs(gorilla_x - center_x) > 2:
                if gorilla_x < center_x:
                    gorilla_x += gorilla_vel
                    gorilla_facing_right = True
                else:
                    gorilla_x -= gorilla_vel
                    gorilla_facing_right = False
        
        # Step 2: Ending
        if scripted_timer > 480: # 150 (intro) + 600 (10sec wait)
            run_game = False

    elif gorilla_state == WALKING:
        if not gorilla_interaction.is_active():
            interact_timer -= 1
        if interact_timer <= 0 and trees_destroyed < MAX_TREES_DESTROYED:
            alive_trees = [t for t in trees if t["state"] == "alive"]
            if alive_trees:
                target_tree = min(alive_trees, key=lambda t: abs(t["pos"][0] - gorilla_x))
                gorilla_state = APPROACHING
            else:
                interact_timer = random.randint(15 * FPS, 30 * FPS)

        if gorilla_pause_frames > 0:
            gorilla_pause_frames -= 1
        else:
            if gorilla_steps_remaining > 0:
                if gorilla_direction == "right": sim_keys[pygame.K_RIGHT] = True; gorilla_facing_right = True
                else: sim_keys[pygame.K_LEFT] = True; gorilla_facing_right = False
                gorilla_steps_remaining -= 1
            else:
                choice = random.random()
                if choice < 0.33: gorilla_pause_frames = random.randint(3*FPS, 8*FPS)
                elif choice < 0.66: gorilla_direction = "left" if gorilla_direction == "right" else "right"
                gorilla_steps_remaining = random.randint(30, 180)

    elif gorilla_state == APPROACHING:
        stop_x = target_tree["pos"][0] + (palm_tree_width // 2) - (gorilla_width // 2)
        if abs(gorilla_x - stop_x) > 2:
            if gorilla_x < stop_x: gorilla_x += gorilla_vel; gorilla_facing_right = True
            else: gorilla_x -= gorilla_vel; gorilla_facing_right = False
        else:
            gorilla_state = INTERACTING
            gorilla_interaction.start()

    elif gorilla_state == INTERACTING:
        interaction_frame, interaction_finished = gorilla_interaction.update()
        if interaction_finished:
            target_tree["state"] = "damaged"
            target_tree["anim_index"] = 0.0
            trees_destroyed += 1
            interact_timer = random.randint(15 * FPS, 30 * FPS)
            gorilla_state = WALKING

    # --- Movement & Animation Logic ---
    gorilla_is_moving = (
        (gorilla_state == WALKING and gorilla_pause_frames == 0 and (sim_keys[pygame.K_LEFT] or sim_keys[pygame.K_RIGHT])) 
        or gorilla_state == APPROACHING 
        or (gorilla_state == EASTER_EGG and scripted_timer < 150)
    )

    if gorilla_is_moving and gorilla_state != INTERACTING:
        gorilla_walk_frame_index = (gorilla_walk_frame_index + GORILLA_ANIM_SPEED) % GORILLA_WALK_FRAMES
    else:
        gorilla_walk_frame_index = 0

    if gorilla_x <= 0: gorilla_direction = "right"; gorilla_facing_right = True
    if gorilla_x >= SCREEN_WIDTH - gorilla_width: gorilla_direction = "left"; gorilla_facing_right = False

    if sim_keys[pygame.K_LEFT] and gorilla_x > 0: gorilla_x -= gorilla_vel
    if sim_keys[pygame.K_RIGHT] and gorilla_x < SCREEN_WIDTH - gorilla_width: gorilla_x += gorilla_vel

    # --- Sunbird Logic ---
    if sunbird_direction == "right":
        sunbird_x += sunbird_speed
        if sunbird_x > SCREEN_WIDTH: sunbird_direction = "left"; sunbird_y = random.randint(20, 170)
    else:
        sunbird_x -= sunbird_speed
        if sunbird_x < -sunbird_frames[0].get_width(): sunbird_direction = "right"; sunbird_y = random.randint(20, 170)
    sunbird_frame_index = (sunbird_frame_index + SUNBIRD_ANIM_SPEED) % NUM_FRAMES
    current_sunbird_frame = sunbird_frames[int(sunbird_frame_index)]
    if sunbird_direction == "left": current_sunbird_frame = pygame.transform.flip(current_sunbird_frame, True, False)

    # --- Tree Animation Update ---
    for tree in trees:
        if tree["state"] == "damaged":
            tree["anim_index"] += 1
            if tree["anim_index"] >= 15:
                tree["state"], tree["anim_index"] = "exploding", 0.0
                tree["explode_anchor"] = (tree["pos"][0] + (palm_tree_width // 2), GROUND_Y - palm_tree_height + 275)
        elif tree["state"] == "exploding":
            tree["anim_index"] += TREE_EXPLODE_ANIM_SPEED
            if tree["anim_index"] >= TREE_EXPLODE_FRAMES: tree["state"] = "stump"

    # --- Drawing ---
    screen.fill((173, 216, 230))
    if typing_mode: pygame.draw.circle(screen, (255, 255, 0), (770, 30), 10)
    if gorilla_state == EASTER_EGG: pygame.draw.circle(screen, (255, 0, 0), (770, 30), 10)

    for i, tree in enumerate(trees):
        if tree["state"] == "exploding":
            frame = tree_explode_frames[int(tree["anim_index"])]
            screen.blit(frame, (tree["explode_anchor"][0] - frame.get_width()//2, tree["explode_anchor"][1] - frame.get_height()//2))
        elif tree["state"] == "damaged":
            screen.blit(tree_damaged_sprite, (tree["pos"][0] + (palm_tree_width//2) - (tree_damaged_sprite.get_width()//2), GROUND_Y - tree_damaged_sprite.get_height() + 100))
        elif tree["state"] == "stump":
            screen.blit(tree_stump_sprite, (tree["pos"][0] + (palm_tree_width//2) - (tree_stump_sprite.get_width()//2), GROUND_Y - tree_stump_sprite.get_height() + 32))
        elif tree["state"] == "alive":
            screen.blit(palm_tree_sprite if i % 2 == 0 else palm_tree_sprite_left, tree["pos"])

    screen.blit(ground_sprite, (-150, GROUND_Y))
    screen.blit(current_sunbird_frame, (sunbird_x, sunbird_y))

    # --- Draw Scared Character (Aligned with Gorilla) ---
    if gorilla_state == EASTER_EGG:
        char_img = scared_sprite if scripted_timer < 150 else surprised_sprite
        
        # This formula matches your gorilla's draw_y logic exactly
        char_draw_y = (GROUND_Y - char_img.get_height() + character_y_offset) + 25
        
        screen.blit(char_img, (character_x, char_draw_y))

    # --- Draw Gorilla / Harambe ---
    if gorilla_state == EASTER_EGG and scripted_timer >= 150:
        screen.blit(harambe_sleeping, (gorilla_x, GROUND_Y - harambe_sleeping.get_height() + 38))
    else:
        if gorilla_state == INTERACTING: current_gorilla_frame = interaction_frame or gorilla_idle_right
        elif gorilla_is_moving: current_gorilla_frame = gorilla_walk_frames[int(gorilla_walk_frame_index)]
        else: current_gorilla_frame = gorilla_idle_right
        
        if not gorilla_facing_right: current_gorilla_frame = pygame.transform.flip(current_gorilla_frame, True, False)
        screen.blit(current_gorilla_frame, (gorilla_x, GROUND_Y - current_gorilla_frame.get_height() + 38))

    # The flash starts at frame 150 and ends at 330 (150 + 180 = 330)
    if gorilla_state == EASTER_EGG and 150 <= scripted_timer <= 270:
        screen.fill((255, 255, 255))

    pygame.display.update()

pygame.quit()