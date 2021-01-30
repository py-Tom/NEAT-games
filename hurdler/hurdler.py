"""Neural Network (NEAT) learns to play hurdler-game."""

import os
import pickle
import random

import neat
import pygame


WIN_WIDTH = 1200
WIN_HEIGHT = 600
VELOCITY = 10
GEN_SCORE = 0

pygame.font.init()
STAT_FONT = pygame.font.SysFont("consolas", 30)

local_dir = os.path.dirname(__file__)
runner_img = [
    pygame.image.load(os.path.join(local_dir, "images", f"run_{i}.png"))
    for i in range(9)
]
bg_img = pygame.image.load(os.path.join(local_dir, "images", "bg.png"))
sky_img = pygame.image.load(os.path.join(local_dir, "images", "sky_m.png"))
bleachers_img = pygame.image.load(os.path.join(local_dir, "images", "bleachers_m.png"))
track_img = pygame.image.load(os.path.join(local_dir, "images", "track_m.png"))
hurdle_img = [
    pygame.image.load(os.path.join(local_dir, "images", f"hurdle_{i}.png"))
    for i in ["high", "low", "long", "short"]
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
        self.y0 = y

        self.jump = False
        self.a = 0
        self.b = 0
        self.c = 0
        self.t = 0

    def draw(self, win):
        """
        Show runner on screen.

        win: game window (pygame Surface / Window)

        return: None
        """

        win.blit(self.img, (self.x, self.y))

    def move(self):
        """
        Change y coord according to jump function.

        return: None
        """
        if self.y < self.y0 or self.jump:
            self.jump = False
            self.t += 1
            displacement = -self.a * self.t ** 2 - self.b * self.t - self.c
            self.y = displacement + self.y0

        else:
            self.y = self.y0
            self.t = 0
            if self.img_index == 8:
                self.img_index = 0
            else:
                self.img_index += 1

            self.img = runner_img[self.img_index]

    def high_jump(self):
        """
        airtime: 47
        max_height: 250
        """
        if not self.jump and self.y == self.y0:
            self.jump = True
            self.img = runner_img[8]
            self.a = -0.46
            self.b = 21.5
            self.c = 0.1

    def long_jump(self):
        """
        airtime: 67
        max_height: 50
        """
        if not self.jump and self.y == self.y0:
            self.jump = True
            self.img = runner_img[2]
            self.a = -0.045
            self.b = 3.0
            self.c = 0.0

    def low_jump(self):
        """
        airtime: 30
        max_height: 100
        """
        if not self.jump and self.y == self.y0:
            self.jump = True
            self.img = runner_img[0]
            self.a = -0.48074986
            self.b = 14.4224957
            self.c = -8.16871777

    def short_jump(self):
        """
        airtime: 17
        max_height: 50
        """
        if not self.jump and self.y == self.y0:
            self.jump = True
            self.img = runner_img[5]
            self.a = -0.60570686
            self.b = 9.08560296
            self.c = 15.92898888

    def get_mask(self):
        """
        Convert image to zero-one matrix.

        return: (pygame Mask)
        """
        return pygame.mask.from_surface(self.img)


class Hurdle:
    """
    Create obstacle for runners.
    x: coord px (int)
    y: coord px (int)
    """

    def __init__(self, x, y):
        # ["high", "low", "long", "short"]
        idx = random.randint(0, 3)
        self.img = hurdle_img[idx]
        self.width = self.img.get_width()
        self.height = self.img.get_height()

        if idx == 0:
            offset = 230
        elif idx == 1:
            offset = 170
        elif idx == 2:
            offset = 190
        else:
            offset = 100

        self.offset_front = offset
        self.offset_back = offset
        self.passed = False

        self.x = x + self.offset_front
        self.y = y - self.height

    def move(self):
        """
        Move image of object.

        return: None
        """
        self.x -= VELOCITY

    def draw(self, win):
        """
        Shows image on game window.

        win: game window (pygame Surface / Window)

        return: None
        """
        win.blit(self.img, (self.x, self.y))

    def get_mask(self):
        """
        Convert image to zero-one matrix.

        return: (pygame Mask)
        """

        return pygame.mask.from_surface(self.img)

    def collision(self, runner):
        """
        Check if pixels in two images are overlapping.

        return: Bool
        """
        runner_mask = runner.get_mask()
        hurlde_mask = self.get_mask()

        return runner_mask.overlap(
            hurlde_mask, (self.x - runner.x, self.y - round(runner.y))
        )


class Background:
    """
    Moving background.

    x1: image_1 coord #px (int)
    x2: image_2 coord #px (int)
    y: coord #px (int)
    v_x: x-axis velocity #px (int)
    img: (pygame Surface)
    width: #px (int)
    """

    def __init__(self, y):
        self.x1 = 0
        self.x2 = WIN_WIDTH
        self.y = y
        self.v_x = VELOCITY
        self.img = bg_img
        self.width = bg_img.get_width()

    def move(self):
        """
        Move two of the same images simultaneously in a loop.
        """

        self.x1 -= self.v_x
        self.x2 -= self.v_x

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, win):
        """
        Shows image on game window.

        win: game window (pygame Surface / Window)

        return: None
        """
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))


class Track(Background):
    """
    Moving bottom background.

    y: (int)

    return: None
    """

    def __init__(self, y):
        super().__init__(y)
        self.v_x = VELOCITY
        self.img = track_img
        self.width = track_img.get_width()


class Bleachers(Background):
    """
    Moving middle background.

    y: coord px (int)

    return: None
    """

    def __init__(self, y):
        super().__init__(y)
        self.v_x = 1
        self.img = bleachers_img
        self.width = bleachers_img.get_width()


class Sky(Background):
    """
    Moving top background.

    y: coord px (int)

    return: None
    """

    def __init__(self, y):
        super().__init__(y)
        self.v_x = 0.5
        self.img = sky_img
        self.width = sky_img.get_width()


def draw_window(
    win,
    runners,
    hurdles,
    score,
    gen_score,
    alive_score,
    track_m=None,
    bleachers_m=None,
    sky_m=None,
):
    """
    Draw all sprites on screen and update view.

    win: game window (pygame Surface / Window)
    runners: Runner objects (list)
    hurdles: Hurdle objects (list)
    score: (int)
    gen_score: number of generation (int)
    alive_score: alive genomes (int)
    track_m: moving bottom background (pygame Surface)
    bleachers_m: moving middle background (pygame Surface)
    sky_m: moving top background (pygame Surface)

    return: None
    """

    win.blit(bg_img, (0, 0))
    # sky_m.draw(win)
    # bleachers_m.draw(win)
    # track_m.draw(win)

    text_score = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text_score, (WIN_WIDTH - 10 - text_score.get_width(), 10))

    text_gen = STAT_FONT.render("Gen: " + str(gen_score), 1, (255, 255, 255))
    win.blit(text_gen, (10, 10))

    text_alive = STAT_FONT.render("Alive: " + str(alive_score), 1, (255, 255, 255))
    win.blit(text_alive, (10, 50))

    for runner in runners:
        runner.draw(win)
    for hurdle in hurdles:
        hurdle.draw(win)

    pygame.display.update()


def game(genomes, config):
    """
    Run AI controlled game.

    return: None
    """

    global GEN_SCORE
    GEN_SCORE += 1

    nets = []
    ge = []
    runners = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        runners.append(Runner(100, 420))
        g.fitness = 0
        ge.append(g)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    # sky_m = Sky(0)
    # bleachers_m = Bleachers(114)
    # track_m = Track(WIN_HEIGHT - track_img.get_height())

    hurdles = [Hurdle(1100, 540)]

    game_loop = True
    score = 0

    while game_loop:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_loop = False
                pygame.quit()
                quit()

        # sky_m.move()
        # bleachers_m.move()
        # track_m.move()

        if len(hurdles) < 5:
            hurdles.append(
                Hurdle(
                    hurdles[-1].x + hurdles[-1].width + hurdles[-1].offset_back,
                    540,
                )
            )

        hurdle_index = 0
        if len(runners) > 0:
            if len(hurdles) > 1 and runners[0].x > hurdles[0].x + hurdles[0].width:
                hurdle_index = 1
        else:
            game_loop = False
            break

        for i, runner in enumerate(runners):
            runner.move()
            ge[i].fitness += 0.1

            output = nets[i].activate(
                (
                    runner.x - hurdles[hurdle_index].x,
                    hurdles[hurdle_index].width,
                    hurdles[hurdle_index].height,
                    runner.x - hurdles[hurdle_index + 1].x,
                    hurdles[hurdle_index + 1].width,
                    hurdles[hurdle_index + 1].height,
                )
            )

            if output[0] == max(output):
                runner.high_jump()
            elif output[1] == max(output):
                runner.low_jump()
            elif output[2] == max(output):
                runner.long_jump()
            elif output[3] == max(output):
                runner.short_jump()
            else:
                pass

        remove_hurdle = []
        for hurdle in hurdles:
            for i, runner in enumerate(runners):
                if hurdle.collision(runner):
                    ge[i].fitness -= 1
                    runners.pop(i)
                    nets.pop(i)
                    ge.pop(i)

                if not hurdle.passed and hurdle.x + hurdle.width <= runner.x:
                    hurdle.passed = True
                    score += 1
                    ge[i].fitness += 1

            if hurdle.x + hurdle.width < 0:
                remove_hurdle.append(hurdle)

            hurdle.move()

        for passed in remove_hurdle:
            hurdles.remove(passed)

        alive_score = len(runners)

        draw_window(win, runners, hurdles, score, GEN_SCORE, alive_score)


def run(config_path):
    """Run simulation and train new network."""

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(game, 10)

    with open("winner.pickle", "wb") as f:
        pickle.dump(winner, f)


def replay_genome(config_path, genome_path="winner.pickle"):
    """Run simulation with trained network."""

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    genomes = [(1, genome)]
    game(genomes, config)


if __name__ == "__main__":
    config_path = os.path.join(local_dir, "config-hurdler.txt")
    # replay_genome(config_path)
    run(config_path)
