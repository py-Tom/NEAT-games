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
bg_img = pygame.image.load(os.path.join(curr_dir, "images", "bg.png"))
sky_img = pygame.image.load(os.path.join(curr_dir, "images", "sky_m.png"))
bleachers_img = pygame.image.load(os.path.join(curr_dir, "images", "bleachers_m.png"))
track_img = pygame.image.load(os.path.join(curr_dir, "images", "track_m.png"))


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
        self.y0 = y

        self.jump = False
        self.a = 0
        self.b = 0
        self.t = 0

    def draw(self, win):
        """
        Animate runner.

        win: game window (pygame Surface / Window)

        return: None
        """

        win.blit(self.img, (self.x, self.y))

    def move(self):
        if self.y < self.y0 or self.jump:
            self.jump = False
            self.t += 1
            d = self.b * self.t + self.a * self.t ** 2
            self.y = d + self.y0
            print(d, self.y)

        else:
            print(self.t)
            self.y = self.y0
            self.t = 0
            self.b = 0
            if self.img_index == 8:
                self.img_index = 0
            else:
                self.img_index += 1

            self.img = runner_img[self.img_index]

    def high_jump(self):
        if not self.jump and self.y == self.y0:
            self.jump = True
            self.a = 4 / 9
            self.b = -40 / 3
            self.img = runner_img[8]

    def long_jump(self):
        if not self.jump and self.y == self.y0:
            self.jump = True
            self.a = 1 / 36
            self.b = -15 / 9
            self.img = runner_img[2]

    def low_jump(self):
        if not self.jump and self.y == self.y0:
            self.jump = True
            self.a = 4 / 15
            self.b = -8
            self.img = runner_img[0]

    def short_jump(self):
        if not self.jump and self.y == self.y0:
            self.jump = True
            self.a = 2 / 15
            self.b = -4
            self.img = runner_img[5]


class Background:
    def __init__(self, y):
        self.x1 = 0
        self.x2 = WIN_WIDTH
        self.y = y
        self.v_x = VELOCITY
        self.img = bg_img
        self.width = bg_img.get_width()

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


class Track(Background):
    """The base on which the runner and hurdles are located."""

    def __init__(self, y):
        """
        Create a running track.

        y: height of base (int)

        return: None
        """
        super().__init__(y)
        self.v_x = VELOCITY
        self.img = track_img
        self.width = track_img.get_width()


class Bleachers(Background):
    """Moving background."""

    def __init__(self, y):
        """
        y: height of base (int)

        return: None
        """
        super().__init__(y)
        self.v_x = 1
        self.img = bleachers_img
        self.width = bleachers_img.get_width()


class Sky(Background):
    """Moving background."""

    def __init__(self, y):
        """
        y: height of base (int)

        return: None
        """
        super().__init__(y)
        self.v_x = 0.5
        self.img = sky_img
        self.width = sky_img.get_width()


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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    print("pressed w")
                    runners[0].high_jump()
                if event.key == pygame.K_d:
                    print("pressed d")
                    runners[0].long_jump()
                if event.key == pygame.K_s:
                    print("pressed s")
                    runners[0].low_jump()
                if event.key == pygame.K_a:
                    print("pressed a")
                    runners[0].short_jump()

        sky_m.move()
        bleachers_m.move()
        track_m.move()
        for runner in runners:
            runner.move()
        draw_window(win, runners, track_m, bleachers_m, sky_m)


if __name__ == "__main__":
    main()