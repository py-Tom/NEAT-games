# NEAT-mini-games
This repository allows you to observe the AI learning process. You can watch the population of sprites trying to survive and beat the game. The Python implementation of the NEAT neuroevolution algorithm ([neat-python](https://github.com/CodeReclaimers/neat-python)) was used to play the mini-games .


## How to use
Run the file with the corresponding game name.


## Flappy Bird
Goal of this game is to avoid obstacles by correctly timed jumps. Neural network takes 3 inputs: position of bird and positions of upper and lower obstacles. The output is based on a sigmoidal function, its value determines whether the bird should jump ```(output > 0.5)``` or not.

//gif here


## Cars
Goal of this game is to avoid obstacles by turning car left or right. Neural network takes 3 inputs: position of car and positions of left and right obstacles. The output is based on the hyperbolic tangent function, its value determines whether the car should turn left ```(output > 0)``` or right ```(output < 0)```.

//gif here
