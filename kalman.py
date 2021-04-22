import numpy as np
from copy import deepcopy
import pymap3d as pm
from DOP import compute_R_matrix_2D
import matplotlib.pyplot as plt

class KalmanMLAT:
    def __init__(self,transition,observation_matrix,measurment,step_size,variance_TDOA,Ground_stations,height,base,method='TOA'):
        self.A=transition
        self.H=observation_matrix
        self.treshold=None
        self.number_of_outliers=0
        self.index=0
        if len(transition)==4:
            self.state = np.array([measurment[1][0],measurment[1][1],0,0])

            self.variance_TODA=variance_TDOA
            helper = self.computeRMatrix(Ground_stations,height,base)
            R = helper*variance_TDOA
            self.compute_P_Matrix(R, step_size, 4)
        else:
            #self.state = np.array([measurment[2][0], measurment[2][1], (measurment[2][0] - measurment[1][0]) / step_size[1],
            #                       (measurment[2][1] - measurment[1][1]) / step_size[1], ((measurment[2][0] - measurment[1][0])
            #                      /step_size[1] - (measurment[1][0] - measurment[0][0])/step_size[0])/(step_size[1]+step_size[0]),
            #                      ((measurment[2][1] - measurment[1][1])
            #                       / step_size[1] - (measurment[1][1] - measurment[0][1]) / step_size[0]) / (
            #                                  step_size[1] + step_size[0])]
            #                      )
            self.state = np.array([measurment[0], measurment[1], 0, 0,0,0])

            self.variance_TDOA = variance_TDOA
            R = self.computeRMatrix(Ground_stations,height,base,method)*variance_TDOA
            self.compute_P_Matrix(R,step_size,6)


    def compute_P_Matrix(self,R,step_size,length):
        if length==6:
            '''self.P = np.zeros([6, 6])
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
            self.P[1, 5] = self.P[5, 1] = -R[1, 1] / (step_size[1] + step_size[0]) ** 4'''
            self.P = np.diag(np.array([10**12,10**12,10**18,10**18,10**16,10**16]))
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

    def update_excluding_outliers(self,observation,time_step,ground_stations,altitude,base):
        P = self.P
        state= self.state
        error=self.update(observation,time_step,ground_stations,altitude,base)
        #print(np.dot(variances,error))
        if self.treshold is None:
            self.treshold = error
            return 1#error
        #return error
        if error<(self.treshold*7.5):
            #self.time_delay=0
            self.treshold -= 0.01*(self.treshold-error)
            self.number_of_outliers =0
            #print(self.treshold)

            return 1#error
        self.number_of_outliers+=1
        #print(self.treshold)
        #print(self.number_of_outliers)
        self.P=P
        self.state=state
        #self.time_delay+=time_step
        if self.number_of_outliers==5:
            self.recalculation(observation,ground_stations,altitude,time_step,base)
            print('recalculation')
            #print(self.estimation)
        return None

    def recalculation(self,observation,Ground_stations, height,step_size,base):
        if len(self.state)==4:
            self.state = np.array([observation[0], observation[1], 0, 0])
            helper = self.computeRMatrix(Ground_stations, height,base)
            R = helper * self.variance_TDOA
            self.compute_P_Matrix(R, step_size, 4)
        else:
            self.state = np.array([observation[0], observation[1], 0, 0,0,0])
            helper = self.computeRMatrix(Ground_stations, height,base)
            R = helper * self.variance_TDOA
            self.compute_P_Matrix(R, [step_size,step_size], 6)

    def update(self,measurment,step_size,groun_stations,height,base_ground_station,method='TOA'):
        transition_matrix = self.compute_transition_matrix(step_size)
        self.index+=1
        state_prediction = np.dot(transition_matrix,self.state)
        try:
            varaince_prediction = np.linalg.multi_dot([transition_matrix,self.P,np.transpose(transition_matrix)])
        except:
            print('1')

        varaince_prediction+=np.diag(np.array([10**(-2),10**(-2),10**0,10**0,10**3,10**3]))
        transposed_H = np.transpose(self.H)
        R = self.computeRMatrix(groun_stations,height,base_ground_station,method)*self.variance_TDOA
        #print(R)
        #if R[0][0]>100:
        #    print(self.index)

        kalman_gain = np.linalg.multi_dot([varaince_prediction,transposed_H,np.linalg.inv(np.linalg.multi_dot(
                                        [self.H,varaince_prediction,transposed_H])+R)])
        self.state = state_prediction + np.dot(kalman_gain,measurment-np.dot(self.H,state_prediction))
        if self.state[0]>=90:
            self.state[0]= 89
        if self.state[0]>=90:
            self.state[0]= 89
        self.P = varaince_prediction - np.linalg.multi_dot([kalman_gain,self.H,varaince_prediction])
        #return np.linalg.norm(np.array(pm.geodetic2enu(self.state[0], self.state[1], height,
        #                                               measurment[0], measurment[1], height)))

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
                if self.A[i,j]==-2:
                    transition_matrix[i, j] = 0.5*timestamp**2
        return transition_matrix

    def computeRMatrix(self,Ground_stations,height,base,method='TOA'):
        stationsGeo = []
        meter_per_lat = 111320
        meter_per_lon = 40075000 * np.cos(3.14 * self.state[0] / 180) / 360;
        for station in Ground_stations:
            stationsGeo.append(pm.enu2geodetic(station[0],station[1],station[2],base[0],base[1],base[2]))
        stationsXYZ = []
        for i,station in enumerate(stationsGeo):
            stationsXYZ.append(np.array(pm.geodetic2enu(station[0],station[1],station[2],self.state[0],self.state[1],0)))
            stationsXYZ[i][0]= stationsXYZ[i][0]/meter_per_lat
            stationsXYZ[i][1] = stationsXYZ[i][1] / meter_per_lon

        if method=='TOA':
            return  compute_R_matrix_2D(np.array(stationsXYZ),[0,0,height],method='TOA')


