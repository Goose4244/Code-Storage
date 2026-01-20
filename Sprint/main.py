import pygame

# Initialize Pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sprite Movement Test")

# Load sprite
sprite = pygame.image.load("gorilla.png").convert_alpha()

# Scale sprite (adjust size as needed)
SPRITE_SCALE = 0.10   # 10% of original size
sprite = pygame.transform.scale(
    sprite,
    (int(sprite.get_width() * SPRITE_SCALE),
     int(sprite.get_height() * SPRITE_SCALE))
)

sprite_width = sprite.get_width()
sprite_height = sprite.get_height()

# Create flipped version of sprite for left movement
sprite_right = sprite
sprite_left = pygame.transform.flip(sprite, True, False)

# Starting position
x = 200

# Direction of gorilla for sprite management
facing_right = True

# Ground setup
GROUND_Y = 350

# Place sprite on top of ground
y = GROUND_Y - sprite_height + 20

vel = 5
run = True

clock = pygame.time.Clock()

# Game loop
while run:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()

    # Horizontal movement only
    if keys[pygame.K_LEFT] and x > 0:
        x -= vel
        facing_right = False

    if keys[pygame.K_RIGHT] and x < 800 - sprite_width:
        x += vel
        facing_right = True

    # --- DRAWING ---
    screen.fill((173, 216, 230))  # Sky

    # Ground
    pygame.draw.rect(screen, (140, 101, 62), (0, GROUND_Y, 800, 350))

    # Draw sprite or mirrored sprite based on direction
    if facing_right:
        screen.blit(sprite_right, (x, y))
    else:
        screen.blit(sprite_left, (x, y))

    pygame.display.update()

# Quit Pygame
pygame.quit()
