import pygame

class GorillaInteraction:
    def __init__(self, frames, anim_speed=0.2, repeat_count=3):
        self.frames = frames
        self.anim_speed = anim_speed
        self.repeat_count = repeat_count

        self.frame_index = 0.0
        self.current_repeat = 0
        self.active = False

        # Optional: forward + reverse playback for smooth looping
        self.sequence = frames + frames[::-1]

    def start(self):
        self.active = True
        self.frame_index = 0.0
        self.current_repeat = 0

    def update(self):
        if not self.active:
            # Return the last known frame or idle instead of None
            return self.sequence[-1], False 

        self.frame_index += self.anim_speed

        if self.frame_index >= len(self.sequence):
            self.frame_index = 0
            self.current_repeat += 1

            if self.current_repeat >= self.repeat_count:
                self.active = False
                return None, True   # finished animation

        frame = self.sequence[int(self.frame_index)]
        return frame, False

    def is_active(self):
        return self.active
