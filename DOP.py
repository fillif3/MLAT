    import numpy as np
from mlat import MLAT
import pymap3d as pm
import matplotlib.pyplot as plt
import statistics
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from copy import deepcopy
def compute_DOP_MAP(anchors,lan_border,long_border,altitude=1000,lan_step=0.01,long_step=0.02,base=-1,case='3D'):

    lan_current=lan_border[0]
    long_current = long_border[0]
    DOPs = np.zeros([2+int((lan_border[1]-lan_border[0])/lan_step),2+int((long_border[1]-long_border[0])//long_step)],dtype=np.dtype('f16'))
    i=0
    j=0
    x_plot_input = []
    y_plot_input = []
    z_plot_input = []

    while(lan_current<lan_border[1]):
        while (long_current < long_border[1]):
            anchors_xyz = []

            for k in range(len(anchors)):
                anchors_xyz.append(
                    pm.geodetic2enu(anchors[k][0], anchors[k][1], anchors[k][2], lan_current, long_current ,
                                    altitude))

            if case=='3D':
                position = np.array(pm.geodetic2ecef(lan_current, long_current, altitude))
                DOP = compute_DOP(anchors_xyz,position,base=base)
            elif case=='2D':


                position = np.array(pm.geodetic2enu(lan_current, long_current, altitude,lan_current, long_current ,
                                    altitude))
                DOP = compute_DOP_2D(anchors_xyz, position, base=base)
                if DOP<200000:
                    x_plot_input.append(lan_current)
                    y_plot_input.append(long_current)
                    z_plot_input.append(DOP)
            else:
                raise ValueError('case has to have different value')
            #print(DOP)
            long_current += long_step

            DOPs[i,j]=DOP
            j += 1
        lan_current+=lan_step
        i+=1
        j=0
        long_current=long_border[0]
    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    #ax.scatter(x_plot_input, y_plot_input, z_plot_input,label='error')
    #i=2
    #for arr in anchors:
    #    ax.scatter(arr[0], arr[1], 40, label=str(i))
    #    i+=1

    #plt.legend()
    #plt.show()
    return DOPs,x_plot_input,y_plot_input,z_plot_input

def compute_DOP(anchors,position,base=-1):
    print('----------')
    print(anchors)
    if base!=-1:
        helper = deepcopy(anchors[base])
        anchors[base]=anchors[-1]
        anchors[-1]=helper
    print(anchors)
    J=MLAT.compute_jacobian(anchors,position)
    print(J)
    Q = compute_Q(len(anchors)-1)#np.linalg.inv(np.array([[2,1,1,1],[1,2,1,1],[1,1,2,1],[1,1,1,2]]))
    try:
        '''
        a=np.transpose(J)
        b = np.dot(a,Q)
        c = np.dot(b,J)
        d=np.linalg.inv(c)
        e=np.trace(d)
        return np.sqrt(np.trace(np.linalg.inv(np.linalg.multi_dot([np.transpose(J),J]))))
        '''

        tran_J = np.transpose(J)
        print(tran_J)
        equation = np.dot(tran_J,J)
        print(equation)
        equation=np.linalg.inv(equation)
        print(equation)
        equation = np.dot(equation,tran_J)
        print(equation)
        equation = np.dot(equation, Q)
        print(equation)
        equation = np.dot(equation, J)
        print(equation)
        equation = np.dot(equation, np.linalg.inv(np.dot(tran_J,J)))
        print(equation)
        #equation = np.dot(equation, tran_J)

        #equation = np.linalg.multi_dot([equation,tran_J,Q,J,np.linalg.inv(np.dot(tran_J,J))])
        return np.sqrt(equation[0,0]+equation[1,1])
    except:
        return 0

def compute_DOP_2D(anchors,position,base=-1):
    if base!=-1:
        helper = deepcopy(anchors[base])
        anchors[base]=anchors[-1]
        anchors[-1]=helper
    J=MLAT.compute_jacobian2_5D(anchors,position)
    #print(J)
    Q = compute_Q(len(anchors)-1)
    #print(J)
    #print('1')
    try:

        tran_J = np.transpose(J)
        #print(tran_J)
        equation = np.dot(tran_J,J)
        #print(equation)
        equation=np.linalg.inv(equation)
        #print(equation)
        equation = np.dot(equation,tran_J)
        #print(equation)
        equation = np.dot(equation, Q)
        #print(equation)
        equation = np.dot(equation, J)
        #print(equation)
        equation = np.dot(equation, np.linalg.inv(np.dot(tran_J,J)))
        #print(equation)
        #equation = np.dot(equation, tran_J)

        #equation = np.linalg.multi_dot([equation,tran_J,Q,J,np.linalg.inv(np.dot(tran_J,J))])
        return np.sqrt(equation[0,0]+equation[1,1])
    except:
        return 1

def compute_Q(size_of_matrix):
    Q = np.eye(size_of_matrix)+np.ones((size_of_matrix,size_of_matrix))
    #for i in range(number_of_anchors):
    #    Q[i,i]+=1
    return Q

if __name__ == "__main__":
    stations =[#[53.39624,14.62899,2.3],
               [53.52379, 14.42902, 18.0],
               #[53.82379, 14.42902, 32.0],
               #[53.92379, 14.32902, 55.0],
               #[53.42379, 14.82902, 1.0],
               [53.47089, 14.43529, 18.3],
               [53.52404, 14.94064, 44.7]]

    #h = 1000
    min_lan = 53.3
    max_lan = 53.6
    min_long = 14.2
    max_long = 15.0
    #lan_step =0.01
    #long_step=0.01

    Dops = compute_DOP_MAP(stations,[min_lan,max_lan],[min_long,max_long],altitude=9000,base=0,case='2D')

    #for i in range(len(Dops)):
    #    for j in range(len(Dops[0])):37928
    #        if Dops[i,j]>2000:
    #            Dops[i,j]=2000
    print(Dops)
    plt.show()
'''

anchors = np.array([[0,-6180,50],[0,16180,70],[11756,16180,80],[19021,-6180,110],[0,-20000,25]])
alt =8500
x=np.linspace(-30000,30000,13)
y=np.linspace(-30000,30000,13)
errors =np.zeros([len(x),len(y)])
x_plot_input=[]
y_plot_input=[]
z_plot_input=[]

for i in range(len(x)):
    for j in range(len(y)):
        print([x[i],y[j],alt])
        errors[i,j] = compute_DOP_2D(anchors,[x[i],y[j],alt],base=-1)
        print(errors[i,j])
        if errors[i,j] < 10000:
            x_plot_input.append(x[i])
            y_plot_input.append(y[j])
            z_plot_input.append(errors[i,j])



print(errors)
#ax = sns.heatmap(errors,vmax=100)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x_plot_input,y_plot_input,z_plot_input)
for arr in anchors:
    ax.scatter(arr[0], arr[1], 40,'r')
plt.show()
print(statistics.mean(z_plot_input))
print(statistics.median(z_plot_input))
'''