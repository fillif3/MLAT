import numpy as np
from copy import deepcopy
import sys


PRINT_FLAG = 0

# PLANE_UPDATE_VARIANCE=0.01

class Cloud:
    def __init__(self, number_of_particles, state,varaince):
        self.particles = []
        self.variance=varaince

        for i in range(number_of_particles):
            self.particles.append(self.Particle(np.random.normal(state,varaince),i,varaince))
        self.timer = 0
        self.state = np.array([0.0, 0.0, 0.0])
        # self.estimated_position_tester = np.array([0.0,0.0,0.0])



    def motion_update(self, t_step):
        for par in self.particles:
            par.motion_update(t_step)

    def get_new_msg(self, obsevation,t_step):
        self.motion_update(t_step)
        for par in self.particles:
            par.sensor_update(obsevation)
        self.sample_new_particles()
        new_esitmated_position = np.array([0.0, 0.0, 0.0])
        for i, p in enumerate(self.particles):
            new_esitmated_position += p.state[0:3]
        new_esitmated_position /= len(self.particles)
        self.state =new_esitmated_position



    def sample_new_particles(self):
        self.normalize_weights()
        max_weight = self.sum_weights()
        upper = max_weight / (len(self.particles) + 1)
        tresh = upper
        new_particles = []
        sum_weights = self.particles[0].weight
        i = 0
        while not len(new_particles) == len(self.particles):
            if sum_weights < tresh:
                i = i + 1
                sum_weights = sum_weights + self.particles[i].weight
            else:
                tresh = tresh + upper
                new_particles.append(deepcopy(self.particles[i]))
        self.particles = new_particles

    def normalize_weights(self):
        min_weight = sys.float_info.max
        for p in self.particles:
            if p.weight < min_weight:
                min_weight = p.weight
        for p in self.particles:
            p.weight -= min_weight

    def sum_weights(self):
        out = 0
        for par in self.particles:
            out = out + par.weight
        return out

    class Particle:
        def __init__(self, state, i,variance):
            self.state = state
            self.weight = 0
            self.id = i  # for debuging
            self.variance=variance

        def motion_update(self, t_step):
            if t_step < 0:
                raise Exception("Negative time step")
            self.state = np.random.normal(self.state, self.variance*t_step)
            self.state[0:3] += self.state[3:6] * t_step
            if len(self.state==9):
                self.state[3:6] += self.state[6:9]*t_step




        def sensor_update(self, obsevation):
            # get plane's id

            # Predict measurment
            #new_ranges = np.zeros(len(anchors)-1)
            #base = np.linalg.norm(anchors[-1]-self.state[0:3])
            #error = 0
            #for i in range(len(new_ranges)):
            #    new_ranges[i] = np.linalg.norm(anchors[i]-self.state[0:3])-base
            #    error+=abs(new_ranges[i]-ranges[i])
            error = np.linalg.norm(obsevation-self.state[0:3])

            self.weight = -error




