import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
import pymap3d as pm
from mlat import MLAT
from comparison import solve
from comparisonKnownTime import solveKnownTime
import time


foyFlag=True
githubFlag=True
githubFlagKnownTime=True
closedFlag=True

CENTER = {
  "lat": 53.39624,
  "long": 14.62899
}
RADIUS = 25000
VARIANCE = 10**(-9)*70
C_VELOCITY = 299792458/ 1.0003#m/s
NUMBER_OF_STATIONS=8
np.random.seed(46)

class receiver:
    def __init__(self,position):
        self.position=position

def place_stations_circle(number,center,radius,height_max=100):
    step = np.pi*2/number
    current_step=0
    stations=[]
    for _ in range(number):
        x=np.cos(current_step)*radius*np.random.uniform(0.5,1)
        y=np.sin(current_step)*radius*np.random.uniform(0.5,1)
        z=np.random.uniform(0,height_max)
        #stations_xyz.append([x,y,z])
        stations.append(pm.enu2geodetic(x,y,z,center['lat'],center['long'],0))
        current_step+=step
    return stations

def plane_step(plane,t_step=0.1,input=None):
    plane['position'] += plane['velocity']*t_step+plane['acceleration']*t_step*0.5
    plane['velocity'] +=plane['acceleration']*t_step
    if input is not None:
        plane['accelartion'] +=None
    return plane

def create_plane(center,radius,direction=None,velocity=250,acceleration=0,height=5000):
    plane={}
    if direction is None:
        direction =np.random.uniform(0,2*np.pi)
    x=np.cos(direction)*radius*0.8
    y=np.sin(direction)*radius*0.8
    z=height
    plane['position'] = np.array(pm.enu2geodetic(x,y,z,center['lat'],center['long'],0))
    vy = velocity*np.cos(np.pi+direction)/(1852*60)
    vx = velocity*np.sin(direction)/(1852*60*np.cos(center['lat']))
    vz=0
    ax = acceleration * np.cos(np.pi+direction) / (1852 * 60)
    ay = acceleration * np.sin(np.pi+direction) / (1852 * 60 * np.cos(center['lat']))
    az = 0
    plane['velocity'] = np.array([vx,vy,vz])
    plane['acceleration'] = np.array([ax,ay,az])
    return plane

def compute_ranges(stations,position,time_variance,c_vel=299792458/ 1.0003):
    range_variance = time_variance*c_vel
    ranges=[]
    for s in stations:
        rang= np.linalg.norm((np.array(pm.geodetic2enu(s[0],s[1],s[2],position[0],position[1],position[2])))) #compute distance between plane and station
        rang += np.random.normal(scale=range_variance)
        ranges.append(rang)
    #helper = ranges[0]
    ranges=np.array(ranges)#-helper
    return ranges

def check_station(position):
    position_xyz2 = np.zeros([len(position),3])
    position=np.array(position)
    for i in range(len(position)):
        position_xyz2[i,:] = pm.geodetic2enu(position[i,0],position[i,1],position[i,2],position[0,0],position[0,1],0)
    bounds = np.array([[np.min(position_xyz2[:,0]),np.min(position_xyz2[:,1]),np.min(position_xyz2[:,2])],[np.max(position_xyz2[:,0]),np.max(position_xyz2[:,1]),np.max(position_xyz2[:,2])]])

    return position_xyz2,bounds,position[0,:]

def check_station_ECEF(position):
    position_xyz2 = np.zeros([len(position),3])
    position=np.array(position)
    for i in range(len(position)):
        position_xyz2[i,:] = pm.geodetic2ecef(position[i,0],position[i,1],position[i,2])
    bounds = np.array([[np.min(position_xyz2[:,0]),np.min(position_xyz2[:,1]),np.min(position_xyz2[:,2])],[np.max(position_xyz2[:,0]),np.max(position_xyz2[:,1]),np.max(position_xyz2[:,2])]])

    return position_xyz2,bounds,position



stations = place_stations_circle(NUMBER_OF_STATIONS,CENTER,25000)
for s in stations:
    plt.plot(s[0],s[1],'rx',label='stacje')

plane = create_plane(CENTER,RADIUS,)
x=[]
y=[]
measurments_x =[]
measurments_y =[]
measurments_x_closed =[]
measurments_y_closed =[]
measurments_x_github =[]
measurments_y_github =[]
measurments_x_githubKnownTime=[]
measurments_y_githubKnownTime=[]
starting_position_for_loop =pm.geodetic2enu(CENTER['lat'],CENTER['long'],0,stations[0][0],stations[0][1],stations[0][2])
#helper = pm.geodetic2ecef(CENTER['lat'],CENTER['long'],0)
#print(helper)
errorFoy =0
timeFoy=[0]
errorClosed=0
errorGithub=0
errorGithubKnownTime=0
timeGithub=[0]
timeGithubKnownTime=[0]
for i in range(1000):
    plane=plane_step(plane)


    x.append(plane['position'][0])
    y.append(plane['position'][1])
    #plane['position'] = [53.4,14.7,1000]
    #stations = [[53.39624, 14.62899, 2.3], [53.47089, 14.43529, 18.3], [53.52404, 14.94064, 44.7]]
    #starting_position_for_loop = [100,100,100]
    ranges = compute_ranges(stations, plane['position'], time_variance= 70*10**(-9))

    starting_position_for_loop_github = pm.enu2geodetic(starting_position_for_loop[0], starting_position_for_loop[1], starting_position_for_loop[2], stations[0][0], stations[0][1],
                                           stations[0][2])
    starting_position_for_loop_github = pm.geodetic2ecef(starting_position_for_loop_github[0],starting_position_for_loop_github[1],starting_position_for_loop_github[2])
    # FOY

    if foyFlag:

        anchors,_,base= check_station(stations)
        t = time.time()
        # testing

        estimator, _ = MLAT.mlat(anchors, ranges, height=plane['position'][2], starting_location = starting_position_for_loop,
                                        method='taylor2.5D_sphere_dll', base_station=base)
        timeFoy.append(timeFoy[-1]+time.time()-t)
        estimator_earth_axis = pm.enu2geodetic(estimator[0],estimator[1],estimator[2],stations[0][0],stations[0][1],stations[0][2])
        measurments_x.append(estimator_earth_axis[0])
        measurments_y.append(estimator_earth_axis[1])

        errorFoy += np.linalg.norm(pm.geodetic2enu(plane['position'][0],plane['position'][1],plane['position'][2],estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2]))

    #TO DO state estimator

    estimation = estimator

    starting_position_for_loop = estimation

    # CLOSE METHOD

    if closedMethods:

        estimator, _ = MLAT.mlat(anchors, ranges, height=plane['position'][2],
                                      starting_location=starting_position_for_loop,
                                      method='schau', base_station=base)

        estimator_earth_axis = pm.enu2geodetic(estimator[0], estimator[1], estimator[2], stations[0][0], stations[0][1],
                                               stations[0][2])

        measurments_x_closed.append(estimator_earth_axis[0])
        measurments_y_closed.append(estimator_earth_axis[1])
        errorClosed += np.linalg.norm(pm.geodetic2enu(plane['position'][0],plane['position'][1],plane['position'][2],estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2]))


    # GITHUB

    if githubFlag:

        anchors,_,base= check_station_ECEF(stations)

        measurments = []

        for i in range(len(anchors)):
            measurments.append([receiver(anchors[i]), ranges[i]/C_VELOCITY, 0.00001])



        #print(starting_position_for_loop_github)
        t = time.time()
        estimator,ret= solve(measurments, plane['position'][2], 0.3038,
                            starting_position_for_loop_github)
        #print(estimator)
        timeGithub.append(timeGithub[-1] + time.time() - t)

        estimator_earth_axis = pm.ecef2geodetic(estimator[0], estimator[1], estimator[2])

        measurments_x_github.append(estimator_earth_axis[0])
        measurments_y_github.append(estimator_earth_axis[1])

        errorGithub += np.linalg.norm(pm.geodetic2enu(plane['position'][0],plane['position'][1],plane['position'][2],estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2]))

    # GITHUB known time

    if githubFlagKnownTime:

        anchors,_,base= check_station_ECEF(stations)

        measurments = []

        for i in range(len(anchors)):
            measurments.append([receiver(anchors[i]), ranges[i]/C_VELOCITY, 0.00001])



        #print(starting_position_for_loop_github)
        t = time.time()
        estimator,ret= solveKnownTime(measurments, plane['position'][2], 0.3038,
                            starting_position_for_loop_github,0)
        #print(estimator)
        timeGithubKnownTime.append(timeGithub[-1] + time.time() - t)

        estimator_earth_axis = pm.ecef2geodetic(estimator[0], estimator[1], estimator[2])

        measurments_x_githubKnownTime.append(estimator_earth_axis[0])
        measurments_y_githubKnownTime.append(estimator_earth_axis[1])

        errorGithubKnownTime += np.linalg.norm(pm.geodetic2enu(plane['position'][0],plane['position'][1],plane['position'][2],estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2]))


    if False:
        plt.plot(measurments_x[-1],measurments_y[-1],'gx',label='Metoda otwarta')
        plt.plot(x[-1],y[-1],'b*',label='Prawdziwa pozycja')
        plt.plot(measurments_x_github[-1], measurments_y_github[-1], 'yx', label='Metoda otwarta z githuba')
        plt.show()


#print('błąd dla algorytmu Foya wynosi:',errorFoy/1000)
plt.plot(x,y,label='Prawdziwa pozycja')
if githubFlagKnownTime:
    print('błąd dla algorytmu Githuba ze znanym czasem wynosi:',errorGithubKnownTime/1000)
    plt.plot(measurments_x_githubKnownTime, measurments_y_githubKnownTime, 'yx',
             label='Metoda otwarta z githuba ze znanym czasem wysłania')

if githubFlag:
    print('błąd dla algorytmu Githuba wynosi:',errorGithub/1000)
    plt.plot(measurments_x_githubKnownTime, measurments_y_github, 'bx', label='Metoda z githuba')
if closedFlag:
    print('błąd dla algorytmu zamkniętego wynosi:',errorClosed/1000)
    plt.plot(measurments_x_closed, measurments_y_closed, 'gx', label='Metoda zamknięta')

if foyFlag:
    print('błąd dla algorytmu otwartego wynosi:',errorFoy/1000)
    plt.plot(measurments_x, measurments_y, 'kx', label='Metoda Foya')



#plt.plot(measurments_x_closed,measurments_y_closed,'kx',label='Metoda zamknięta')

#print(measurments_x_closed,measurments_y_closed)
#plt.plot(measurments_x,measurments_y,'gx',label='Metoda otwarta')



plt.legend()
plt.show()
plt.plot(timeGithub,label='SciPy method')
plt.plot(timeGithubKnownTime,label='SciPy method with known time')

#plt.plot(timeFoy,label='Foy')
plt.legend()
plt.show()