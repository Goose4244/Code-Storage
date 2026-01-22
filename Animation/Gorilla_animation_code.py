SPRITE_SIZE = 32
NUM_FRAMES = 6

sheet = pygame.image.load("gorilla_walk.png").convert_alpha()
frames = []

for i in range(NUM_FRAMES):
    frame = sheet.subsurface(
        pygame.Rect(i * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE)
    )
    frames.append(frame)

# Animation loop
frame_index = (frame_index + 0.15) % NUM_FRAMES
current_frame = frames[int(frame_index)]
