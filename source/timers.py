from pygame.time import get_ticks


class Timer:
    def __init__(self, duration, command=None, autostart=False):
        self.duration = duration
        self.start_time = 0
        self.is_active = False
        self.command = command
        # AUTOSTART.
        if autostart:
            self.activate()

    def activate(self):
        self.is_active = True
        self.start_time = get_ticks()

    def deactivate(self):
        self.is_active = False
        self.start_time = 0

    def update(self):
        if self.is_active:
            if get_ticks() - self.start_time >= self.duration:
                self.deactivate()
                if self.command:
                    self.command()
