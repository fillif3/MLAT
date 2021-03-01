import numpy as np
from copy import deepcopy
import pymap3d as pm
class StateEstimation:

    def __init__(self,A,C,observations,time_stamps):
        #if len(observation)!=len(A):
        #    raise Exception("observations had to be equal to state")
        self.A = A
        self.C = C
        cmk = self.computeCmk(len(time_stamps),time_stamps)
        self.G =np.linalg.inv(np.dot(np.transpose(cmk),cmk))
        self.state = np.dot(np.dot(self.G,np.transpose(cmk)),observations)#np.dot(C,observation)
        self.time_delay=0
        self.treshold = None
        self.number_of_outliers=0
        self.previous_measurment=observations
        self.previous_time_steps=time_stamps
        self.maximum_memory=90
        self.estimation=0

    def recalculation(self):
        cmk = self.computeCmk(len(self.previous_time_steps),self.previous_time_steps)
        self.G =np.linalg.inv(np.dot(np.transpose(cmk),cmk))
        self.state = np.dot(np.dot(self.G,np.transpose(cmk)),self.previous_measurment)#np.dot(C,observation)
        self.time_delay=0
        self.treshold = None
        self.number_of_outliers = 0


    def update_excluding_outliers(self,observation,time_step,altitude):
        G = self.G
        state= self.state
        error=self.update(observation,time_step,altitude)
        if self.treshold is None:
            self.treshold = error
            return error
        #return error
        if error<(self.treshold*1.1):
            self.time_delay=0
            self.treshold -= 0.01*(self.treshold-error)
            self.number_of_outliers =0
            #print(self.treshold)

            return error
        self.number_of_outliers+=1
        #print(self.treshold)
        #print(self.number_of_outliers)
        self.G=G
        self.state=state
        self.time_delay+=time_step
        if self.number_of_outliers==5:
            self.recalculation()
            print('recalculation')
            print(self.estimation)
            pass
        return None

    def update(self,observation,time_step,altitude):
        self.previous_measurment.append(observation[0])
        self.previous_measurment.append(observation[1])
        self.previous_time_steps.append(time_step)
        self.estimation+=1
        if len(self.previous_time_steps)>self.maximum_memory:
            self.previous_time_steps.pop(0)
            self.previous_measurment.pop(0)
            self.previous_measurment.pop(0)
            #print(self.previous_measurment)

        time_step+=self.time_delay
        transition_matrix = self.compute_transition_matrix(time_step)
        state_helper = np.dot(transition_matrix,self.state)
        transposed_C = np.transpose(self.C)
        self.G = np.linalg.inv(np.dot(transposed_C,self.C)+np.linalg.inv(np.linalg.multi_dot([transition_matrix,self.G,np.transpose(transition_matrix)])))
        self.state=state_helper+np.dot(np.dot(self.G,transposed_C),observation-np.linalg.multi_dot([self.C,transition_matrix,self.state]))
        return np.linalg.norm(np.array(pm.geodetic2enu(state_helper[0],state_helper[1],altitude,
                                              observation[0],observation[1],altitude)))

    def computeCmk(self,length,timestamps):
        #if length<=1:
        #    raise Exception("too low length to compute Cmk matrix")
        #cmk=np.array([])
        for i in range(length):
            if length<7:
                F = np.eye(length)
            else:
                F=np.eye(6)
            for j in range(length-i-1):
                transition_matrix=self.compute_transition_matrix(timestamps[length-1-j])
                F=np.dot(F,transition_matrix)
            if i==0:
                cmk = np.dot(self.C,np.linalg.inv(F))
            else:
                cmk=np.concatenate((cmk,np.dot(self.C,np.linalg.inv(F))),axis=0)
        return cmk

    def compute_transition_matrix(self,timestamp):
        transition_matrix = deepcopy(self.A)
        for i in range(len(self.A)):
            for j in range(len(self.A)):
                if self.A[i,j]==-1:
                    transition_matrix[i, j] = timestamp
        return transition_matrix




