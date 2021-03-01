import numpy as np
import pandas as pd
from time import time
from copy import deepcopy
import pymap3d as pm

class MLAT:
    @staticmethod
    def __d(p1, p2):
        return np.linalg.norm(p1 - p2)

    @staticmethod
    def gdescent(anchors_in, ranges_in, bounds_in=((0, 0, 0),),
                 n_trial=10, alpha=0.001, time_threshold=None):
        anchors = np.array(anchors_in, dtype=float)
        n, dim = anchors.shape
        bounds_temp = anchors
        if bounds_in is not None:
            bounds_temp = np.append(bounds_temp, bounds_in, axis=0)
        bounds = np.empty((2, dim))
        for i in range(dim):
            bounds[0, i] = np.min(bounds_temp[:, i])
            bounds[1, i] = np.max(bounds_temp[:, i])

        if time_threshold is None:
            time_threshold = 1.0 / n_trial

        ranges = np.empty(n)
        result = pd.DataFrame(columns=['estimator', 'error'],
                              index=np.arange(n_trial))
        for i in range(n_trial):
            estimator0 = np.empty(dim)
            for j in range(dim):
                estimator0[j] = np.random.uniform(bounds[0, j], bounds[1, j])
            estimator = np.copy(estimator0)

            t0 = time()
            while True:
                for j in range(n):
                    ranges[j] = MLAT.__d(anchors[j, :], estimator)
                error = MLAT.__d(ranges_in, ranges)

                delta = np.zeros(dim)
                for j in range(n):
                    delta += (ranges_in[j] - ranges[j]) / ranges[j] * \
                             (estimator - anchors[j, :])
                delta *= 2 * alpha

                estimator_next = estimator + delta#---------------------------------------------------------
                for j in range(n):
                    ranges[j] = MLAT.__d(anchors[j, :], estimator_next)
                error_next = MLAT.__d(ranges_in, ranges)
                if error_next < error:
                    estimator = estimator_next
                else:
                    result['estimator'][i] = estimator
                    result['error'][i] = error
                    break
                if time() - t0 > time_threshold:
                    result['estimator'][i] = estimator
                    result['error'][i] = error
                    break

        return result

    @staticmethod
    def mlat(anchors_in, ranges_in, bounds_in=((0, 0, 0),), starting_location = None,
             n_trial=100, alpha=0.001, time_threshold=None,method = 'gdescent',height=None,base_station=None):
        if method == 'gdescent':
            ret = MLAT.gdescent(anchors_in, ranges_in, bounds_in,
                                n_trial, alpha, time_threshold)
            idx = np.nanargmin(ret['error'])
            estimator = ret['estimator'][idx]
            return estimator, ret

        elif method == 'chan':
            ret = MLAT.ChanExtension(anchors_in, ranges_in)
            return ret,ret
        elif method == 'schau':
            ret,estimator = MLAT.SchauExtensionAvg(anchors_in, ranges_in,height)
            return  estimator,ret
        elif method == 'geyer':
            ret, estimator = MLAT.geyer_method(anchors_in, ranges_in, height)
            return estimator, ret
        elif method == 'taylor':
            ret = MLAT.taylor(anchors_in, ranges_in, bounds_in)
            try:
                idx = np.nanargmin(ret['error'])
                estimator = ret['estimator'][idx]
                return estimator, ret
            except:
                return None,None
        elif method == 'taylor2.5D':
            ret = MLAT.taylor2_5D(anchors_in, ranges_in, height,bounds_in)
            try:
                idx = np.nanargmin(ret['error'])
                estimator = ret['estimator'][idx]
                #estimator[2] = height
                return estimator, ret
            except:
                return None,None
        elif method == 'taylor2.5D_sphere':
            ret = MLAT.taylor2_5D_sphere(anchors_in, ranges_in, height,bounds_in,base_station,starting_location=starting_location)
            try:
                idx = np.nanargmin(ret['error'])
                estimator = ret['estimator'][idx]
                #estimator[2] = height
                return estimator, ret
            except:
                return None,None
        else:
            print('wrong method')
            return None,None

    
    #-------------------------------------------------------
    @staticmethod
    def geyer_method(anchors_in, ranges_in,height):
        A = np.c_[anchors_in,-ranges_in]
        B = MLAT.computeBVector(anchors_in, ranges_in)
        invA = np.linalg.inv(A)
        D = 0.5*np.dot(invA,np.ones(4))
        E = 0.5*np.dot(invA,B)
        a = np.dot(D[0:3],D[0:3]) - D[3]**2 #check sign
        b = 2*np.dot(D[0:3],E[0:3])-1- E[3]*D[3]
        c = np.dot(E[0:3],E[0:3])- E[3]**2
        if a != 0:
            Delta = b**2-4*a*c
            if Delta < 0:
                # print("negative delta")
                return None, None
            elif Delta == 0:
                solution = [-b/(2*a)]

            else:
                solution = [(-b + np.sqrt(Delta)) / (2 * a),(-b - np.sqrt(Delta)) / (2 * a)]

        else:
            solution =[-c/b]

        if len(solution)==1:
            position = solution*D+E
            return position,position
        else:
            position1 = solution[0]*D+E
            position2 = solution[1]*D+E
            if abs(np.linalg.norm(position1[2]-height[2]))>abs(np.linalg.norm(position2[2]-height[2])):
                #print('------------------------')
                #print(height)
                #print([position1,position2])
                #print(position2)

                return [position1,position2],position2
            else:
                #print('------------------------')
                #print(height)
                #print([position1,position2])
                #print(position1)
                return [position1,position2],position1


    @staticmethod
    def computeBVector(anchors_in,ranges_in):
        out = []
        for row1,row2 in zip(anchors_in,ranges_in):
            out.append(np.linalg.norm(row1)**2-row2**2)
        return np.array(out)


    #-----------------------------------------------------
    @staticmethod
    def taylor2_5D_sphere(anchors_in, ranges_in, height, bounds_in=((0, 0, 0),), base_station=None, # TO DO Metoda wymaga znajomość varinacji
                   n_trial=5, starting_location = None, time_threshold=None):
        anchors = np.array(anchors_in, dtype=float)
        n, dim = anchors.shape
        #bounds_temp = anchors
        #if bounds_in is not None:
        #    bounds_temp = np.append(bounds_temp, bounds_in, axis=0)
        #bounds = np.empty((2, dim))
        #for i in range(dim):
        #    bounds[0, i] = np.min(bounds_temp[:, i])
        #    bounds[1, i] = np.max(bounds_temp[:, i])

        #if time_threshold is None:
        #    time_threshold = 1.0 / n_trial

        #ranges = np.empty(n)
        result = pd.DataFrame(columns=['estimator', 'error','iterations'],
                              index=np.arange(n_trial))
        for i in range(1):
            #reference = np.empty(dim)
            #for j in range(dim - 1):
            #    reference[j] = np.random.uniform(bounds[0, j], bounds[1, j])
            reference = np.array([starting_location[0],starting_location[1],height])
            tresh = (10**(3))
            for iter in range(50000):
                A = MLAT.compute_jacobian2_5D(anchors, reference)
                #u,s,v = np.linalg.svd(A,full_matrices=True)
                #A=np.dot(u,v)*s[0]
                errors = MLAT.compute_errors(anchors, ranges_in, reference)
                tran_A = np.transpose(A)
                try:
                    delta = np.dot(np.dot(np.linalg.inv(np.dot(tran_A, A)), tran_A ), errors)
                except:
                    break
                delta = np.append(delta, [0])
                estimator_next = reference + delta
                if iter>-1:
                    estimator_next = MLAT.correct_Z(estimator_next,base_station,height)

                error_next = MLAT.compute_errors(anchors, ranges_in, estimator_next)

                if (iter<3) or(np.linalg.norm(error_next) < np.linalg.norm(errors)):
                    err=np.linalg.norm(error_next)
                    reference = estimator_next
                else:
                    result['estimator'][i] = reference
                    result['error'][i] = np.linalg.norm(errors)
                    result['iterations'][i] = iter
                    if result['error'][i]<tresh or (iter>15) :
                        return result

                    break
                # if time() - t0 > time_threshold:
                #   break

        return result

    @staticmethod
    def correct_Z(estimator, base_station, height):
        geo = pm.enu2geodetic(estimator[0],estimator[1],estimator[2],base_station[0],base_station[1],base_station[2])
        new_estimator = pm.geodetic2enu(geo[0],geo[1],height,base_station[0],base_station[1],base_station[2])
        #geo2 = pm.enu2geodetic(new_estimator[0],new_estimator[1],new_estimator[2],base_station[0],base_station[1],base_station[2])
        return new_estimator#new_estimator


    @staticmethod
    def taylor2_5D(anchors_in, ranges_in, height, bounds_in=((0, 0, 0),),   #TO DO Metoda wymaga znajomość varinacji
                 n_trial=100, time_threshold=None):
        anchors = np.array(anchors_in, dtype=float)
        n, dim = anchors.shape
        bounds_temp = anchors
        if bounds_in is not None:
            bounds_temp = np.append(bounds_temp, bounds_in, axis=0)
        bounds = np.empty((2, dim))
        for i in range(dim):
            bounds[0, i] = np.min(bounds_temp[:, i])
            bounds[1, i] = np.max(bounds_temp[:, i])

        if time_threshold is None:
            time_threshold = 1.0 / n_trial

        ranges = np.empty(n)
        result = pd.DataFrame(columns=['estimator', 'error'],
                              index=np.arange(n_trial))
        for i in range(n_trial):
            referecne0 = np.empty(dim)
            for j in range(dim-1):
                referecne0[j] = np.random.uniform(bounds[0, j], bounds[1, j])
            referecne0[-1] = height
            reference = np.copy(referecne0)

            t0 = time()

            alpha=1
            for _ in range(20):
                A = MLAT.compute_jacobian2_5D(anchors, reference)
                errors = MLAT.compute_errors(anchors, ranges_in, reference)
                try:
                    delta = np.dot(np.dot(np.linalg.inv(np.dot(np.transpose(A), A)), np.transpose(A)), errors)
                except:
                    continue
                #for j in range(n):
                #    delta += (ranges_in[j] - ranges[j]) / ranges[j] * \
                #             (estimator - anchors[j, :])
                #delta *= 2 * alpha
                delta=np.append(delta,[0])
                estimator_next = reference + delta
                error_next = MLAT.compute_errors(anchors, ranges_in, estimator_next)

                if np.linalg.norm(error_next) < np.linalg.norm(errors):
                    reference = estimator_next
                else:
                    result['estimator'][i] = reference
                    result['error'][i] = np.linalg.norm(errors)
                    break
                #if time() - t0 > time_threshold:
                 #   break
        return result


    @staticmethod
    def taylor(anchors_in, ranges_in, bounds_in=((0, 0, 0),),   #TO DO Metoda wymaga znajomość varinacji
                 n_trial=15, time_threshold=None):
        anchors = np.array(anchors_in, dtype=float)
        n, dim = anchors.shape
        bounds_temp = anchors
        if bounds_in is not None:
            bounds_temp = np.append(bounds_temp, bounds_in, axis=0)
        bounds = np.empty((2, dim))
        for i in range(dim):
            bounds[0, i] = np.min(bounds_temp[:, i])
            bounds[1, i] = np.max(bounds_temp[:, i])

        if time_threshold is None:
            time_threshold = 1.0 / n_trial

        ranges = np.empty(n)
        result = pd.DataFrame(columns=['estimator', 'error'],
                              index=np.arange(n_trial))
        for i in range(n_trial):
            referecne0 = np.empty(dim)
            for j in range(dim):
                referecne0[j] = np.random.uniform(bounds[0, j], bounds[1, j])
            reference = np.copy(referecne0)

            t0 = time()

            alpha=1
            for _ in range(20):
                A = MLAT.compute_jacobian(anchors, reference)
                errors = MLAT.compute_errors(anchors, ranges_in, reference)
                try:
                    delta = np.dot(np.dot(np.linalg.inv(np.dot(np.transpose(A),A)),np.transpose(A)),errors)
                except:
                    continue
                #for j in range(n):
                #    delta += (ranges_in[j] - ranges[j]) / ranges[j] * \
                #             (estimator - anchors[j, :])
                #delta *= 2 * alpha

                estimator_next = reference + delta
                error_next = MLAT.compute_errors(anchors, ranges_in, estimator_next)

                if np.linalg.norm(error_next) < np.linalg.norm(errors):
                    reference = estimator_next
                else:
                    result['estimator'][i] = reference
                    result['error'][i] = np.linalg.norm(errors)
                    break
                #if time() - t0 > time_threshold:
                 #   break
        return result

    @staticmethod
    def compute_jacobian(anchors,position):
        jacobian=np.zeros([len(anchors)-1,3])
        dist_to_refernce = np.linalg.norm(position-anchors[-1])
        refence_derievative = (position-anchors[-1])/dist_to_refernce
        for i in range(len(anchors)-1):
            jacobian[i,:] = (position-anchors[i])/np.linalg.norm(position-anchors[i])-refence_derievative
        return jacobian

    @staticmethod
    def compute_jacobian2_5D(anchors,position):
        jacobian=np.zeros([len(anchors)-1,2])
        #print(position)
        #print(anchors)
        dist_to_refernce = np.linalg.norm(position-anchors[-1])
        refence_derievative = (position[0:2]-anchors[-1][0:2])/dist_to_refernce
        for i in range(len(anchors)-1):
            jacobian[i,:] = (position[0:2]-anchors[i][0:2])/np.linalg.norm(position-anchors[i])-refence_derievative
        return jacobian
    @staticmethod
    def compute_errors(anchors, ranges_in, reference):
        ranges_in = ranges_in[0:-1] - ranges_in[-1]
        computed_ranges = np.zeros(len(ranges_in))
        ref = np.linalg.norm(anchors[-1]-reference)
        for i in range(len(ranges_in)):
            computed_ranges[i] = np.linalg.norm(anchors[i]-reference) - ref
        errors = ranges_in-computed_ranges
        return errors


    # -----------------------------------------------------------------------------------------------
    @staticmethod
    def SchauExtensionAvg(anchors_in_to_avg, ranges_in_to_avg,height):
        samples = MLAT.sampling(4,len(anchors_in_to_avg))
        estimatorSum= np.array([0,0,0])
        estimations=0
        for s in samples:
            anchors = anchors_in_to_avg[s]
            ranges = ranges_in_to_avg[s]
            try:
                _,estimator = MLAT.SchauExtension(anchors,ranges,height)
                if estimator is not None:
                    estimatorSum = estimator + estimatorSum
                    estimations+=1
            except:
                pass
        try:
            estimator = estimatorSum/estimations
            return estimator,estimator
        except:
            return None,None





    @staticmethod
    def SchauExtension(anchors_in, ranges_in,height):
        M = MLAT.computeM(anchors_in)
        D = MLAT.computeD(ranges_in)
        T = MLAT.computeT(D,M)
        Delta,a,b,_ = MLAT.computeDelta(D,M,T)
        if Delta<0:
            #print("negative delta")
            return None,None
        elif Delta==0:
            Rs =-b/(2*a)
            position  = 0.5*np.dot(np.linalg.inv(M),(T-2*Rs*D))+anchors_in[3]
            return position,position
        else:
            Rs = (-b+np.sqrt(Delta)) / (2 * a)
            position1 = 0.5 * np.dot(np.linalg.inv(M), (T - 2 * Rs * D))+anchors_in[3]
            Rs = (-b - np.sqrt(Delta)) / (2 * a)
            position2 = 0.5 * np.dot(np.linalg.inv(M), (T - 2 * Rs * D))+anchors_in[3]
            if abs(np.linalg.norm(position1[2]-height))>abs(np.linalg.norm(position2[2]-height)):
                #print('------------------------')
                #print(height)
                #print([position1,position2])
                #print(position2)

                return [position1,position2],position2
            else:
                #print('------------------------')
                #print(height)
                #print([position1,position2])
                #print(position1)
                return [position1,position2],position1

    @staticmethod
    def computeM(anchors_in):
        M=anchors_in[0:3]
        M = M- anchors_in[3]
        return M
    @staticmethod
    def computeD(ranges_in):
        D=ranges_in[0:3]
        D = D- ranges_in[3]
        return D
    @staticmethod
    def computeT(D,M):
        T= [np.linalg.norm(M[0])**2-D[0]**2,np.linalg.norm(M[1])**2-D[1]**2,np.linalg.norm(M[2])**2-D[2]**2]
        T= np.array(T)
        return T
    @staticmethod
    def computeDelta(D,M,T):
        invM = MLAT.pseudoMonroeInverse(M)#np.linalg.inv(M)
        traD = np.transpose(D)
        trainvM = np.transpose(invM)
        traT = np.transpose(T)
        a = 4 - 4*np.dot(np.dot(np.dot(traD,trainvM),invM),D)
        b= 2 * np.dot(np.dot(np.dot(traD,trainvM),invM),T)+2*np.dot(np.dot(np.dot(traT,trainvM),invM),D)
        c = -np.dot(np.dot(np.dot(traT,trainvM),invM),T)
        Delta = b**2-4*a*c
        return Delta,a,b,c



    # -----------------------------------------------------------------------------------------------
    @staticmethod
    def ChanExtension(anchors_in, ranges_in): #For 2d sitation
        H = MLAT.createH(anchors_in,ranges_in)
        invH = np.linalg.inv(H)
        Y = MLAT.createY(anchors_in,ranges_in)
        position = 0.5*invH.dot(Y)
        return position
    @staticmethod
    def createH(anchors_in,ranges_in):
        H=[]
        for i in range(len(ranges_in)-2):
            helper=[]
            helper.append((ranges_in[i+2]-ranges_in[0])*anchors_in[i+1][0]-(ranges_in[i+1]-ranges_in[0])
                          *anchors_in[i+2][0]-(ranges_in[i+2]-ranges_in[i+1])*anchors_in[0][0])
            helper.append((ranges_in[i+2]-ranges_in[0])*anchors_in[i+1][1]-(ranges_in[i+1]-ranges_in[0])
                          *anchors_in[i+2][1]-(ranges_in[i+2]-ranges_in[i+1])*anchors_in[0][1])
            H.append(helper)
        H=np.array(H)
        return H

    @staticmethod
    def createY(anchors_in, ranges_in):
        Y=[]
        for i in range(len(ranges_in)-2):
            Y.append((ranges_in[i+2]-ranges_in[0])*MLAT.createKSqaure(anchors_in,i+1)-(ranges_in[i+2]-ranges_in[1+1])
                     *MLAT.createKSqaure(anchors_in,0)-(ranges_in[i+1]-ranges_in[0])*MLAT.createKSqaure(anchors_in,i+2)
                     +(ranges_in[i+1]-ranges_in[0])*(ranges_in[i+2]-ranges_in[0])*(ranges_in[i+2]-ranges_in[i+1]))
        Y=np.array(Y)
        return Y
    @staticmethod
    def createKSqaure(anchors_in, i):
        s = anchors_in[i][0]**2+anchors_in[i][1]**2
        return s


    #-----------------------------------

    @staticmethod
    def pseudoMonroeInverse(matrix):
        T = np.transpose(matrix)
        I = np.linalg.inv(np.dot(T,matrix))
        Matrix = np.dot(I,T)
        return Matrix

    @staticmethod
    def sampling(n, length):
        if length <= n:
            return None
        possible_combiantion = []
        varables = []
        for i in range(n):
            varables.append(i)
        possible_combiantion.append(varables)
        helper = n - 1
        while True:
            varables = deepcopy(varables)
            varables[helper] += 1

            for i in range(helper + 1, n):
                varables[i] = varables[i - 1] + 1
            if varables[-1] == length:
                helper -= 1
            else:
                possible_combiantion.append(varables)
                helper = n - 1
            if helper == -1:
                return possible_combiantion