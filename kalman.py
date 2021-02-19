import numpy as np
from copy import deepcopy
import pymap3d as pm

class KalmanMLAT:
    def __init__(self,transition,observation_matrix,measurment,step_size,variance_TDOA,Ground_stations,height,base):
        self.A=transition
        self.H=observation_matrix
        if len(transition)==4:
            self.state = np.array([measurment[1][0],measurment[1][1],0,0])

            self.variance_TODA=variance_TDOA
            J = self.compute_jacobian(Ground_stations,height,base)
            R = 2*variance_TDOA**2*np.linalg.inv(np.dot(np.transpose(J),J))
            self.compute_P_Matrix(R, step_size, 4)
        else:
            self.state = np.array([measurment[2][0], measurment[2][1], (measurment[2][0] - measurment[1][0]) / step_size[1],
                                   (measurment[2][1] - measurment[1][1]) / step_size[1], ((measurment[2][0] - measurment[1][0])
                                  /step_size[1] - (measurment[1][0] - measurment[0][0])/step_size[0])/(step_size[1]+step_size[0]),
                                  ((measurment[2][1] - measurment[1][1])
                                   / step_size[1] - (measurment[1][1] - measurment[0][1]) / step_size[0]) / (
                                              step_size[1] + step_size[0])]
                                  )

            self.variance_TODA = variance_TDOA
            J = self.compute_jacobian(Ground_stations, height, base)
            R = 2 * variance_TDOA ** 2 * np.linalg.inv(np.dot(np.transpose(J), J))
            self.compute_P_Matrix(R,step_size,6)


    def compute_P_Matrix(self,R,step_size,length):
        if length==6:
            self.P = np.zeros([6, 6])
            self.P[0, 0] = R[0, 0]
            self.P[0, 0] = R[0, 0]
            self.P[1, 1] = R[1, 1]
            self.P[2, 2] = 2 * R[0, 0] / (step_size[1] ** 2)
            self.P[3, 3] = 2 * R[1, 1] / (step_size[1] ** 2)
            self.P[4, 4] = 4 * R[0, 0] / ((step_size[1] + step_size[0]) ** 4)
            self.P[5, 5] = 4 * R[0, 0] / ((step_size[1] + step_size[0]) ** 4)
            self.P[0, 2] = self.P[2, 0] = -R[0, 0] / step_size[1]
            self.P[1, 3] = self.P[3, 1] = -R[1, 1] / step_size[1]
            self.P[2, 4] = self.P[4, 2] = -R[0, 0] / (step_size[1] + step_size[0]) ** 2
            self.P[3, 5] = self.P[5, 3] = -R[1, 1] / (step_size[1] + step_size[0]) ** 2
            self.P[0, 4] = self.P[4, 0] = -R[0, 0] / (step_size[1] + step_size[0]) ** 4
            self.P[1, 5] = self.P[5, 1] = -R[1, 1] / (step_size[1] + step_size[0]) ** 4
        else:

            self.P = np.zeros([4, 4])
            self.P[0, 0] = R[0, 0]
            self.P[1, 1] = R[1, 1]
            self.P[2, 2] = 2 * R[0, 0] / (step_size ** 2)
            self.P[3, 3] = 2 * R[1, 1] / (step_size ** 2)
            self.P[0, 2] = self.P[2, 0] = -R[0, 0] / step_size
            self.P[1, 3] = self.P[3, 1] = -R[1, 1] / step_size
            '''
            self.P = np.zeros([4, 4])
            self.P[0, 0] = 1000
            self.P[1, 1] =  1000
            self.P[2, 2] =  1000000
            self.P[3, 3] =  1000000
            self.P[0, 2] =  1000000
            self.P[1, 3] =  1000000'''

    def update(self,measurment,step_size,groun_stations,height,base_ground_station):
        transition_matrix = self.compute_transition_matrix(step_size)
        state_prediction = np.dot(transition_matrix,self.state)
        varaince_prediction = np.linalg.multi_dot([transition_matrix,self.P,np.transpose(transition_matrix)])
        transposed_H = np.transpose(self.H)
        J = self.compute_jacobian(groun_stations,height,base_ground_station)
        R = 2 * self.variance_TODA ** 2 * np.linalg.inv(np.dot(np.transpose(J), J))
        kalman_gain = np.linalg.multi_dot([varaince_prediction,transposed_H,np.linalg.inv(np.linalg.multi_dot(
                                        [self.H,varaince_prediction,transposed_H])+R)])
        self.state = state_prediction + np.dot(kalman_gain,measurment-np.dot(self.H,state_prediction))
        self.P = varaince_prediction - np.linalg.multi_dot([kalman_gain,self.H,varaince_prediction])

    def compute_jacobian(self,anchors,height,base):
        jacobian=np.zeros([len(anchors)-1,2])
        #d = (base[0],base[1],base[2])
        #c = (self.state[0],self.state[1])
        position = np.array(pm.geodetic2enu(self.state[0],self.state[1],height,base[0],base[1],base[2]))
        #station = np.array(pm.geodetic2enu(anchors[-1][0],anchors[-1][1],anchors[-1][2],base[0],base[1],base[2]))
        dist_to_refernce = np.linalg.norm(position-anchors[-1])
        refence_derievative = (position[0:2]-anchors[-1][0:2])/dist_to_refernce
        for i in range(len(anchors)-1):
            #station = pm.geodetic2enu(anchors[i][0], anchors[i][1], anchors[i][2], base[0], base[1], base[2])
            jacobian[i,:] = (position[0:2]-anchors[i][0:2])/np.linalg.norm(position-anchors[i])-refence_derievative
        return jacobian


    def compute_transition_matrix(self,timestamp):
        transition_matrix = deepcopy(self.A)
        for i in range(len(self.A)):
            for j in range(len(self.A)):
                if self.A[i,j]==-1:
                    transition_matrix[i, j] = timestamp
        return transition_matrix