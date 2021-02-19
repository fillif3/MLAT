import numpy as np
from copy import deepcopy
class StateEstimation:

    def __init__(self,A,C,observations,time_stamps):
        #if len(observation)!=len(A):
        #    raise Exception("observations had to be equal to state")
        self.A = A
        self.C = C
        cmk = self.computeCmk(len(A),time_stamps)
        self.G =np.linalg.inv(np.dot(np.transpose(cmk),cmk))
        self.state = np.dot(np.dot(self.G,np.transpose(cmk)),observations)#np.dot(C,observation)

    def update(self,observation,time_step):
        transition_matrix = self.compute_transition_matrix(time_step)
        state_helper = np.dot(transition_matrix,self.state)
        transposed_C = np.transpose(self.C)
        self.G = np.linalg.inv(np.dot(transposed_C,self.C)+np.linalg.inv(np.linalg.multi_dot([transition_matrix,self.G,np.transpose(transition_matrix)])))
        self.state=state_helper+np.dot(np.dot(self.G,transposed_C),observation-np.linalg.multi_dot([self.C,transition_matrix,self.state]))
        return (np.linalg.norm(state_helper[0:2] - self.state[0:2]))/time_step

    def computeCmk(self,length,timestamps):
        #if length<=1:
        #    raise Exception("too low length to compute Cmk matrix")
        #cmk=np.array([])
        for i in range(length):
            F = np.eye(length)
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




