"""Neural Network learns to play hurdler-game."""

import os
import pickle
import random

import neat
import pygame

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)

WIN_WIDTH = 1200
WIN_HEIGHT = 600

VELOCITY = 10

GEN_SCORE = 0

curr_dir = os.path.dirname(__file__)


runner_img = [
    pygame.image.load(os.path.join(curr_dir, "images", f"run_{i}.png"))
    for i in range(9)
]
bg_img = pygame.image.load(os.path.join(curr_dir, "images", "bg.png"))
sky_img = pygame.image.load(os.path.join(curr_dir, "images", "sky_m.png"))
bleachers_img = pygame.image.load(os.path.join(curr_dir, "images", "bleachers_m.png"))
track_img = pygame.image.load(os.path.join(curr_dir, "images", "track_m.png"))
hurdle_img = [
    pygame.image.load(os.path.join(curr_dir, "images", f"hurdle_{i}.png"))
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
        Animate runner.

        win: game window (pygame Surface / Window)

        return: None
        """

        win.blit(self.img, (self.x, self.y))

    def move(self):
        if self.y < self.y0 or self.jump:
            self.jump = False
            self.t += 1
            displacement = -self.a * self.t ** 2 - self.b * self.t - self.c
            self.y = displacement + self.y0
            # print(displacement, self.y, self.t)

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
        return pygame.mask.from_surface(self.img)


class Hurdle:
    def __init__(self, x, y):
        # ["high", "low", "long", "short"]
        idx = random.randint(0, 3)
        self.img = hurdle_img[idx]

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
        self.y = y - self.img.get_height()

    def move(self):
        self.x -= VELOCITY

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    def collision(self, runner):
        runner_mask = runner.get_mask()
        hurlde_mask = self.get_mask()

        return runner_mask.overlap(
            hurlde_mask, (self.x - runner.x, self.y - round(runner.y))
        )


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
    runners: list of Runner objects

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


def main(genomes, config):
    """Infinite loop."""
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

    run = True
    score = 0

    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            """ if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    # print("pressed w")
                    runners[0].high_jump()
                if event.key == pygame.K_d:
                    # print("pressed d")
                    runners[0].long_jump()
                if event.key == pygame.K_s:
                    # print("pressed s")
                    runners[0].low_jump()
                if event.key == pygame.K_a:
                    # print("pressed a")
                    runners[0].short_jump() """

        # sky_m.move()
        # bleachers_m.move()
        # track_m.move()

        if len(hurdles) < 5:
            hurdles.append(
                Hurdle(
                    hurdles[-1].x
                    + hurdles[-1].img.get_width()
                    + hurdles[-1].offset_back,
                    540,
                )
            )

        hurdle_index = 0
        if len(runners) > 0:
            if (
                len(hurdles) > 1
                and runners[0].x > hurdles[0].x + hurdles[0].img.get_width()
            ):
                hurdle_index = 1
        else:
            run = False
            break

        for i, runner in enumerate(runners):
            runner.move()
            ge[i].fitness += 0.1

            output = nets[i].activate(
                (
                    runner.x - hurdles[hurdle_index].x,
                    hurdles[hurdle_index].img.get_width(),
                    hurdles[hurdle_index].img.get_height(),
                    runner.x - hurdles[hurdle_index + 1].x,
                    hurdles[hurdle_index + 1].img.get_width(),
                    hurdles[hurdle_index + 1].img.get_height(),
                )
            )
            print(output)

            if output[0] == max(output) and output[0]:
                runner.high_jump()
            elif output[1] == max(output) and output[1]:
                runner.low_jump()
            elif output[2] == max(output) and output[2]:
                runner.long_jump()
            elif output[3] == max(output) and output[3]:
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

                if not hurdle.passed and hurdle.x + hurdle.img.get_width() <= runner.x:
                    hurdle.passed = True
                    score += 1
                    ge[i].fitness += 1
                    # print("score: ", score)

            if hurdle.x + hurdle.img.get_width() < 0:
                remove_hurdle.append(hurdle)

            hurdle.move()

        for r in remove_hurdle:
            hurdles.remove(r)

        alive_score = len(runners)
        # print("hur: ", len(hurdles), "rem: ", len(remove_hurdle), "run: ", len(runners))
        draw_window(win, runners, hurdles, score, GEN_SCORE, alive_score)


def run(config_path):
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

    winner = p.run(main, 25)
    print(winner)
    with open("winner.pickle", "wb") as f:
        pickle.dump(winner, f)


def replay_genome(config_path, genome_path="winner.pickle"):
    # Load requried NEAT config
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]

    # Call game with only the loaded genome
    main(genomes, config)


if __name__ == "__main__":
    config_path = os.path.join(curr_dir, "config-hurdler.txt")
    # replay_genome(config_path)
    run(config_path)
