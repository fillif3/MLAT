import numpy as np

class StateEstimation:

    def __init__(self,A,C,observations):
        #if len(observation)!=len(A):
        #    raise Exception("observations had to be equal to state")
        self.A = A
        self.C = C
        cmk = self.computeCmk(len(A))
        self.G =np.linalg.inv(np.dot(np.transpose(cmk),cmk))
        self.state = np.dot(np.dot(self.G,np.transpose(cmk)),observations)#np.dot(C,observation)

    def update(self,observation,time_step):
        transition_matrix = self.A*time_step
        state_helper = np.dot(transition_matrix,self.state)
        transposed_C = np.transpose(self.C)
        self.G = np.linalg.inv(np.dot(transposed_C,self.C)+np.linalg.inv(np.linalg.multi_dot([transition_matrix,self.G,np.transpose(transition_matrix)])))
        self.state=state_helper+np.dot(np.dot(self.G,transposed_C),observation-np.linalg.multi_dot([self.C,transition_matrix,self.state]))

    def computeCmk(self,length):
        #if length<=1:
        #    raise Exception("too low length to compute Cmk matrix")
        #cmk=np.array([])
        for i in range(length):
            F = np.eye(length)
            for _ in range(length-i-1):
                F=np.dot(F,self.A)
            if i==0:
                cmk = np.dot(self.C,np.linalg.inv(F))
            else:
                cmk=np.concatenate((cmk,np.dot(self.C,np.linalg.inv(F))),axis=0)
        return cmk



