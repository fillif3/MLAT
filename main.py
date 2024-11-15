import numpy as np
from mlat import MLAT
import time
import matplotlib.pyplot as plt
import statistics
if __name__ == "__main__":
    errors=[]
    errorshelper=[]
    tic = time.perf_counter()
    for _ in range(10):
        W = 9
        L = 9
        H = 3
        anchors = np.array([[0, 0, 0],
                            [W, 0, H],
                            [W, L, 0]])#,
                            #[0, L, H],
                            #[0, 0, H],
                            #[W, 0, 0],
                            #[W, L, H],
                            #[0, L, 0]])
        node = np.array([W * np.random.rand(),
                         L * np.random.rand(),
                         H * np.random.rand()])
        #print(node)
        #print(node-anchors)
        ranges = np.empty(anchors.shape[0])
        error = 0.5
        ranges_with_error = np.empty(anchors.shape[0])
        for i in range(anchors.shape[0]):
            ranges[i] = np.linalg.norm(anchors[i, :] - node)
            ranges_with_error[i] = ranges[i] + np.random.uniform(-error, error)
        # TODO: You need to define search space boundary to prevent UNEXPECTED RESULT
        # If not, search space boundary is defined as a cube constrained to
        # minimum and maximum coordinates of x, y, z of anchors
        # If anchors are in the same plane, i.e., all anchors have the same (similar)
        # coordinate of at least one axes, you MUST define search space boundary
        # So, defining search space boundary is all up to you
        bounds = np.zeros((2, anchors.shape[0]))
        for i in range(anchors.shape[1]):
            bounds[0, i] = min(anchors[:, i])
            # minimum boundary of ith axis
            bounds[1, i] = max(anchors[:, i]) # maximum boundary of ith axis
        # hard coded minimum height (0 m) of search boundary
        bounds[0, -1] = 0

        # Gradinent method
        estimator, result= MLAT.mlat(anchors, ranges_with_error,height=node[2],method='taylor2.5D')
        if estimator is None:
            print('dsa')
            continue
        '''
        print('Anchors')
        print(anchors)
        print('Node:', node)
        print('Ranges:')
        print('   ', ranges)
        print('Ranges with error:')
        print('   ', ranges_with_error)
        print('Estimator')
        print(estimator)
        print('Full result')
        print(result)
        '''
        #print(estimator)
        errors.append(np.linalg.norm(node- estimator))
        '''
        if np.linalg.norm(node- result[0])>np.linalg.norm(node- result[1]):
            errorshelper.append(np.linalg.norm(node- result[1]))
        else:
            errorshelper.append(np.linalg.norm(node- result[0]))
        '''

    toc = time.perf_counter()
    print(len(errors))
    print(toc-tic)
    print(statistics.mean(errors))
    print(statistics.median(errors))
    print(statistics.stdev(errors))
    #print(errors)
    '''
    print(statistics.mean(errorshelper))
    print(statistics.median(errorshelper))
    print(statistics.stdev(errorshelper))
    '''
    #plt.hist(errors,100)
    #plt.show()
