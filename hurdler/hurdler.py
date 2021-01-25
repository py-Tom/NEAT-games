"""Neural Network learns to play hurdler-game."""

#  import neat
import pygame
import os

WIN_WIDTH = 1200
WIN_HEIGHT = 600

VELOCITY = 10

curr_dir = os.path.dirname(__file__)


runner_img = [
    pygame.image.load(os.path.join(curr_dir, "images", f"run_{i}.png"))
    for i in range(9)
]
bg_img = pygame.image.load(os.path.join(curr_dir, "images", f"bg.png"))
sky_img = pygame.image.load(os.path.join(curr_dir, "images", f"sky_m.png"))
bleachers_img = pygame.image.load(os.path.join(curr_dir, "images", f"bleachers_m.png"))
track_img = pygame.image.load(os.path.join(curr_dir, "images", f"track_m.png"))


class Runner:
    """A representation of a runner that is controlled by the AI / player."""

    def __init__(self, x, y):
        """
        Create a runner.

        x: position x (int)
        y: position y (int)

        return: None
        """

        self.x = x
        self.y = y
        self.img = runner_img[0]
        self.img_index = 0

    def draw(self, win):
        """
        Animate runner.

        win: game window (pygame Surface / Window)

        return: None
        """

        if self.img_index == 8:
            self.img_index = 0
        else:
            self.img_index += 1

        self.img = runner_img[self.img_index]

        win.blit(self.img, (self.x, self.y))


class Track:
    """The base on which the runner and hurdles are located."""

    def __init__(self, y):
        """
        Create a running track.

        y: height of base (int)

        return: None
        """

        self.x1 = 0
        self.x2 = WIN_WIDTH
        self.y = y
        self.v_x = VELOCITY
        self.img = track_img
        self.width = track_img.get_width()

    def move(self):
        self.x1 -= self.v_x
        self.x2 -= self.v_x

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))


class Bleachers:  # add to Track as decorator
    """Moving background."""

    def __init__(self, y):
        """
        y: height of base (int)

        return: None
        """

        self.x1 = 0
        self.x2 = WIN_WIDTH
        self.y = y
        self.v_x = 2
        self.img = bleachers_img
        self.width = bleachers_img.get_width()

    def move(self):
        self.x1 -= self.v_x
        self.x2 -= self.v_x

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))


class Sky:  # add to Track as decorator
    """Moving background."""

    def __init__(self, y):
        """
        y: height of base (int)

        return: None
        """

        self.x1 = 0
        self.x2 = WIN_WIDTH
        self.y = y
        self.v_x = 1
        self.img = sky_img
        self.width = sky_img.get_width()

    def move(self):
        self.x1 -= self.v_x
        self.x2 -= self.v_x

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))


def draw_window(win, runners, track_m, bleachers_m, sky_m):
    """
    Draw all sprites on screen and update view.

    win: game window (pygame Surface / Window)
    runners: list of Runner objects

    return: None
    """

    win.blit(bg_img, (0, 0))
    sky_m.draw(win)
    bleachers_m.draw(win)
    track_m.draw(win)

    for runner in runners:
        runner.draw(win)

    pygame.display.update()


def main():
    """Infinite loop."""

    run = True

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    sky_m = Sky(0)
    bleachers_m = Bleachers(114)
    track_m = Track(WIN_HEIGHT - track_img.get_height())

    runners = [Runner(100, 420)]

    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        sky_m.move()
        bleachers_m.move()
        track_m.move()
        draw_window(win, runners, track_m, bleachers_m, sky_m)


if __name__ == "__main__":
    main()