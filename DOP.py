import numpy as np
from mlat import MLAT
import pymap3d as pm
import matplotlib.pyplot as plt
import seaborn as sns
def compute_DOP_MAP(anchors,lan_border,long_border,altitude=1000,lan_step=0.01,long_step=0.01,base=-1,case='3D'):
    anchors_xyz = []
    if case=='3D':
        for i in range(len(anchors)):
            anchors_xyz.append(pm.geodetic2ecef(anchors[i][0],anchors[i][1],anchors[i][2]))
    else:
        for i in range(len(anchors)):
            anchors_xyz.append(pm.geodetic2enu(anchors[i][0],anchors[i][1],anchors[i][2],anchors[base][0],anchors[base][1],anchors[base][2]))
    lan_current=lan_border[0]
    long_current = long_border[0]
    DOPs = np.zeros([2+int((lan_border[1]-lan_border[0])/lan_step),2+int((long_border[1]-long_border[0])//long_step)],dtype=np.dtype('f16'))
    i=0
    j=0
    while(lan_current<lan_border[1]):
        while (long_current < long_border[1]):

            if case=='3D':
                position = np.array(pm.geodetic2ecef(lan_current, long_current, altitude))
                DOP = compute_DOP(anchors_xyz,position,base=base)
            elif case=='2D':
                position = np.array(pm.geodetic2enu(lan_current, long_current, altitude,anchors[base][0],anchors[base][1],anchors[base][2]))
                DOP = compute_DOP_2D(anchors_xyz, position, base=base)
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
    return DOPs

def compute_DOP(anchors,position,base=-1):
    if base!=-1:
        helper = anchors[base]
        anchors[base]=anchors[-1]
        anchors[-1]=helper
    J=MLAT.compute_jacobian(anchors,position)
    Q = np.eye(3)#np.linalg.inv(np.array([[2,1,1],[1,2,1],[1,1,2]]))
    try:
        a=np.transpose(J)
        b = np.dot(J,Q)
        c = np.dot(b,a)
        d=np.linalg.inv(c)
        e=np.trace(d)
        return np.sqrt(np.trace(np.linalg.inv(np.linalg.multi_dot([J,Q,np.transpose(J)]))))
    except:
        return 0

def compute_DOP_2D(anchors,position,base=-1):
    if base!=-1:
        helper = anchors[base]
        anchors[base]=anchors[-1]
        anchors[-1]=helper
    J=MLAT.compute_jacobian2_5D(anchors,position)
    Q = np.linalg.inv(np.array([[2,1],[1,2]]))
    #print(J)
    #print('1')
    try:
        a=np.transpose(J)
        b = np.dot(J,Q)
        c = np.dot(b,a)
        d=np.linalg.inv(c)
        e=np.trace(d)
        helper=np.sqrt(np.trace(np.linalg.inv(np.linalg.multi_dot([J,Q,np.transpose(J)]))))
        return helper
    except:
        return 1

stations =[[53.39624,14.62899,2.3],
           [53.52379, 14.42902, 18.0],
           #[53.82379, 14.42902, 32.0],
           #[53.92379, 14.32902, 55.0],
           #[53.42379, 14.82902, 1.0],
           [53.47089, 14.43529, 18.3],#,
           [53.52404, 14.94064, 44.7]]

#h = 1000
min_lan = 53.0
max_lan = 53.9
min_long = 14.0
max_long = 15.5
#lan_step =0.01
#long_step=0.01

Dops = compute_DOP_MAP(stations,[min_lan,max_lan],[min_long,max_long],altitude=100,base=-1,case='3D')

#for i in range(len(Dops)):
#    for j in range(len(Dops[0])):37928
#        if Dops[i,j]>2000:
#            Dops[i,j]=2000
print(np.min(Dops))
print(np.log(Dops))
ax = sns.heatmap(Dops)
plt.show()