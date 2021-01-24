"""Neural Network learns to play hurdler-game."""

#  import neat
import pygame
import os

WIN_WIDTH = 1000
WIN_HEIGHT = 500

curr_dir = os.path.dirname(__file__)

runner_img = [
    pygame.image.load(os.path.join(curr_dir, "images", f"run_{i}.png"))
    for i in range(9)
]


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

        print(self.img_index)
        self.img = runner_img[self.img_index]

        win.blit(self.img, (self.x, self.y))


def draw_window(win, runners):
    """
    Draw all sprites on screen and update view.

    win: game window (pygame Surface / Window)
    runners: list of Runner objects

    return: None
    """
    background = pygame.Surface(win.get_size())
    background.fill((100, 133, 255))

    win.blit(background, (0, 0))

    for runner in runners:
        runner.draw(win)

    pygame.display.update()


def main():
    """Infinite loop."""

    run = True

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    runners = [Runner(100, 330)]

    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        draw_window(win, runners)


if __name__ == "__main__":
    main()