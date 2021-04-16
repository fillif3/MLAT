import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
import pymap3d as pm
from mlat import MLAT
from comparison import solve
from comparisonTDOA import solveTDOA
from comparisonKnownTime import solveKnownTime
import time
import statistics


foyFlag=True
githubFlag=True
githubFlagKnownTime=True
githubFlagKnownTimePlusNoise=True
githubFlagTDOA=True
closedFlag=False

CENTER = {
  "lat": 53.39624,
  "long": 14.62899
}
RADIUS = 25000
VARIANCE = 10**(-9)*70
C_VELOCITY = 299792458/ 1.0003#m/s
SET_OF_STATIONS=1
np.random.seed(46)

class receiver:
    def __init__(self,position):
        self.position=position

def place_stations_circle(number,center,radius,height_max=100):
    '''
    step = np.pi*2/number
    current_step=0
    stations=[]
    for _ in range(number):
        x=np.cos(current_step)*radius
        y=np.sin(current_step)*radius
        z=0
        #stations_xyz.append([x,y,z])
        stations.append(pm.enu2geodetic(x,y,z,center['lat'],center['long'],0))
        current_step+=step
    return stations
    '''

    if number ==1:
        return [[53.3956 , 15.0048 , 0],[53.5906 , 14.4402 , 0],[53.2016 , 14.4419 , 0]]
    if number ==2:
        return [[53.3956 , 15.0048 , 0],[53.6098, 14.7457 , 0],[53.5279 ,  14.3240 , 0],[53.2638,14.3259,0],[53.1825 ,14.7445 ,0]]
    if number ==3:
        return [[53.3956 ,14.7457 , 0],[53.6098, 14.7457 , 0],[53.5279 ,  14.3240 , 0],[53.2638,14.3259,0],[53.1825 ,14.7457 ,0]]
    if number ==4:
        return [[53.3956 , 15.0048 , 0],[53.6098, 14.7457 , 200],[53.5279 ,  14.3240 , 500],[53.2638,14.3259,200],[53.1825 ,14.7445 ,500]]
    if number ==5:
        return [[53.3956 , 15.0048 , 0],[53.5548,14.8957 , 0],[53.6209 ,  14.6290 , 0],[53.5548,14.3623,0],[53.3957 , 14.2532 ,0],
                [53.2371 , 14.3642 ,0],[53.1716 , 14.6289 ,0],[53.2371 , 14.8937 ,0]]
    raise Exception("wrong set of stations")

def plane_step(plane,t_step=0.1,input=None):
    plane['position'] += plane['velocity']*t_step+plane['acceleration']*t_step*0.5
    plane['velocity'] +=plane['acceleration']*t_step
    if input is not None:
        plane['accelartion'] +=None
    return plane

def create_plane(center,radius,radius_multiplier,direction=None,velocity=250,acceleration=0,height=5000):
    plane={}
    if direction is None:
        direction =np.pi/4#np.random.uniform(0,2*np.pi)
    x=np.cos(direction)*radius*radius_multiplier
    y=np.sin(direction)*radius*radius_multiplier
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


for setOfStations in range(1,6):
    if (setOfStations)== 2:
        closedFlag = True
    for part_of_way in range(4):
        print('For set of stations equal to '+str(setOfStations)+" and part of way equal to ",part_of_way)
        starting_radius = 2-float(part_of_way)/2
        stations = place_stations_circle(setOfStations,CENTER,25000)
        #for s in stations:
        #    plt.plot(s[0],s[1],'rx',label='stacje')
        plane = create_plane(CENTER,RADIUS,starting_radius)
        x=[]
        y=[]
        measurments_x =[]
        measurments_y =[]
        measurments_x_closed =[]
        measurments_y_closed =[]
        measurments_x_github =[]
        measurments_y_github =[]
        measurments_x_githubTDOA = []
        measurments_y_githubTDOA = []
        measurments_x_githubKnownTime=[]
        measurments_y_githubKnownTime=[]
        measurments_x_githubKnownTimePlusNoise=[]
        measurments_y_githubKnownTimePlusNoise=[]
        starting_position_for_loop =pm.geodetic2enu(CENTER['lat'],CENTER['long'],0,stations[0][0],stations[0][1],stations[0][2])
        #helper = pm.geodetic2ecef(CENTER['lat'],CENTER['long'],0)
        #print(helper)
        errorFoy =[0]
        timeFoy=[0]
        errorClosed=[0]
        errorGithub=[0]
        errorGithubTDOA = [0]
        errorGithubKnownTime=[0]
        errorGithubKnownTimePlusNoise=[0]
        timeGithub=[0]
        timeGithubTDOA = [0]
        timeGithubKnownTime=[0]
        timeGithubKnownTimePlusNoise=[0]
        for i in range(500):
            if i%10==0:
                print(i)
            plane=plane_step(plane)
            #plane = plane_step(plane)


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

                errorFoy.append(np.linalg.norm(pm.geodetic2enu(plane['position'][0],plane['position'][1],plane['position'][2],estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2])))

            #TO DO state estimator

                #estimation = estimator

                #starting_position_for_loop = estimation

            # CLOSE METHOD

            if closedFlag:

                estimator, _ = MLAT.mlat(anchors, ranges, height=plane['position'][2],
                                              starting_location=starting_position_for_loop,
                                              method='schau', base_station=base)

                estimator_earth_axis = pm.enu2geodetic(estimator[0], estimator[1], estimator[2], stations[0][0], stations[0][1],
                                                       stations[0][2])

                measurments_x_closed.append(estimator_earth_axis[0])
                measurments_y_closed.append(estimator_earth_axis[1])
                errorClosed.append(np.linalg.norm(pm.geodetic2enu(plane['position'][0],plane['position'][1],plane['position'][2],estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2])))


            # GITHUB

            if githubFlag:

                anchors,_,base= check_station_ECEF(stations)

                measurments = []

                for i in range(len(anchors)):
                    measurments.append([receiver(anchors[i]), ranges[i]/C_VELOCITY, 1])



                #print(starting_position_for_loop_github)
                t = time.time()
                estimator,ret= solve(measurments, plane['position'][2], 1,
                                    starting_position_for_loop_github)
                #print(estimator)
                timeGithub.append(timeGithub[-1] + time.time() - t)

                estimator_earth_axis = pm.ecef2geodetic(estimator[0], estimator[1], estimator[2])

                measurments_x_github.append(estimator_earth_axis[0])
                measurments_y_github.append(estimator_earth_axis[1])

                errorGithub.append(np.linalg.norm(pm.geodetic2enu(plane['position'][0],plane['position'][1],plane['position'][2],estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2])))

            # GITHUB TDOA

            if githubFlagTDOA:

                anchors,_,base= check_station_ECEF(stations)

                measurments = []

                for i in range(len(anchors)):
                    measurments.append([receiver(anchors[i]), ranges[i]/C_VELOCITY, 1])



                #print(starting_position_for_loop_github)
                t = time.time()
                estimator,ret= solveTDOA(measurments, plane['position'][2],1,
                                    starting_position_for_loop_github)
                #print(estimator)
                timeGithubTDOA.append(timeGithubTDOA[-1] + time.time() - t)

                estimator_earth_axis = pm.ecef2geodetic(estimator[0], estimator[1], estimator[2])

                measurments_x_githubTDOA.append(estimator_earth_axis[0])
                measurments_y_githubTDOA.append(estimator_earth_axis[1])

                errorGithubTDOA.append(np.linalg.norm(pm.geodetic2enu(plane['position'][0],plane['position'][1],plane['position'][2],estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2])))

            # GITHUB known time

            if githubFlagKnownTime:
                anchors,_,base= check_station_ECEF(stations)

                measurments = []

                for i in range(len(anchors)):
                    measurments.append([receiver(anchors[i]), ranges[i]/C_VELOCITY, 1])



                #print(starting_position_for_loop_github)
                t = time.time()
                estimator,ret= solveKnownTime(measurments, plane['position'][2],1,
                                    starting_position_for_loop_github,0)
                #print(estimator)
                timeGithubKnownTime.append(timeGithubKnownTime[-1] + time.time() - t)

                estimator_earth_axis = pm.ecef2geodetic(estimator[0], estimator[1], estimator[2])

                measurments_x_githubKnownTime.append(estimator_earth_axis[0])
                measurments_y_githubKnownTime.append(estimator_earth_axis[1])

                errorGithubKnownTime.append(np.linalg.norm(pm.geodetic2enu(plane['position'][0],plane['position'][1],plane['position'][2],estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2])))


            if githubFlagKnownTimePlusNoise:
                anchors,_,base= check_station_ECEF(stations)

                measurments = []

                for i in range(len(anchors)):
                    measurments.append([receiver(anchors[i]), ranges[i]/C_VELOCITY, 1])



                #print(starting_position_for_loop_github)
                t = time.time()
                estimator,ret= solveKnownTime(measurments, plane['position'][2],1,
                                    starting_position_for_loop_github,np.random.rand()*10**(-8))
                #print(estimator)
                timeGithubKnownTimePlusNoise.append(timeGithubKnownTime[-1] + time.time() - t)

                estimator_earth_axis = pm.ecef2geodetic(estimator[0], estimator[1], estimator[2])

                measurments_x_githubKnownTimePlusNoise.append(estimator_earth_axis[0])
                measurments_y_githubKnownTimePlusNoise.append(estimator_earth_axis[1])

                errorGithubKnownTimePlusNoise.append(np.linalg.norm(pm.geodetic2enu(plane['position'][0],plane['position'][1],plane['position'][2],estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2])))


            if False:
                plt.plot(measurments_x[-1],measurments_y[-1],'gx',label='Metoda otwarta')
                plt.plot(x[-1],y[-1],'b*',label='Prawdziwa pozycja')
                plt.plot(measurments_x_github[-1], measurments_y_github[-1], 'yx', label='Metoda otwarta z githuba')
                plt.show()


        #print('błąd dla algorytmu Foya wynosi:',errorFoy/1000)
        #plt.plot(x,y,label='Prawdziwa pozycja')
        if githubFlagTDOA:
            print('Średnia, mediana oraz odchylenie standardowe Githuba z TDOA:')
            print(statistics.mean(errorGithubTDOA))
            print(statistics.median(errorGithubTDOA))
            print(statistics.stdev(errorGithubTDOA))
            #plt.plot(measurments_x_githubTDOA, measurments_y_githubTDOA, 'yx',
                     #label='Metoda otwarta z githuba z TDOA')

        if githubFlagKnownTime:
            print('Średnia, mediana oraz odchylenie standardowe Githuba ze znanym czasem wynosi:')
            print(statistics.mean(errorGithubKnownTime))
            print(statistics.median(errorGithubKnownTime))
            print(statistics.stdev(errorGithubKnownTime))
           # plt.plot(measurments_x_githubKnownTime, measurments_y_githubKnownTime, 'gx',
                     #label='Metoda otwarta z githuba ze znanym czasem wysłania')

        if githubFlagKnownTimePlusNoise:
            print('Średnia, mediana oraz odchylenie standardowe Githuba ze znanym czasem i dodakotwym szumem wynosi:')
            print(statistics.mean(errorGithubKnownTimePlusNoise))
            print(statistics.median(errorGithubKnownTimePlusNoise))
            print(statistics.stdev(errorGithubKnownTimePlusNoise))
            #plt.plot(measurments_x_githubKnownTime, measurments_y_githubKnownTime, 'gx',
                     #label='Metoda otwarta z githuba ze znanym czasem wysłania')
        if githubFlag:
            print('Średnia, mediana oraz odchylenie standardowe Githuba wynosi:')
            print(statistics.mean(errorGithub))
            print(statistics.median(errorGithub))
            print(statistics.stdev(errorGithub))
            #plt.plot(measurments_x_github, measurments_y_github, 'bx', label='Metoda z githuba')
        if closedFlag:
            print('Średnia, mediana oraz odchylenie standardowe zamknięty:')
            print(statistics.mean(errorClosed))
            print(statistics.median(errorClosed))
            print(statistics.stdev(errorClosed))
            #plt.plot(measurments_x_closed, measurments_y_closed, 'gx', label='Metoda zamknięta')

        if foyFlag:
            print('Średnia, mediana oraz odchylenie standardowe foy:')
            print(statistics.mean(errorFoy))
            print(statistics.median(errorFoy))
            print(statistics.stdev(errorFoy))
            #plt.plot(measurments_x, measurments_y, 'kx', label='Metoda Foya')



#plt.plot(measurments_x_closed,measurments_y_closed,'kx',label='Metoda zamknięta')

#print(measurments_x_closed,measurments_y_closed)
#plt.plot(measurments_x,measurments_y,'gx',label='Metoda otwarta')



        #plt.legend()
        #plt.show()
        #plt.plot(timeGithub,label='SciPy method')
        #plt.plot(timeGithubKnownTime,label='SciPy method with known time')

        #plt.plot(timeFoy,label='Foy')
        #plt.legend()
        #plt.show()