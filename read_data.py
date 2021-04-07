import pandas as pd
from mlat import MLAT
import numpy as np
import pymap3d as pm
import matplotlib.pyplot as plt
import statistics
import time
from comparison import solve
from ufir import StateEstimation
from kalman import KalmanMLAT
from pf import Cloud
from DOP import compute_DOP_2D

class receiver:
    def __init__(self,position):
        self.position=position

Altitude = 1
Mlat_timestamp=2
MLAT_latitude=3
MLAT_longitude=4
ADSB_timestamp=5
ADSB_latitude=6
ADSB_longitude=7
Error=8
Station_0=9
Station_1=10
TDOA1=11
TDOA1_ADSB=12
TDOA1_error=13
Station_2=14
TDOA2=15
TDOA2_ADSB=16
TDOA2_error=17
Name = 0

c = 299792458/ 1.0003#m/s

R = 6371000 #m
METERS_PER_DEGREE_Y = 2*np.pi*R/360

stations =[[1043,53.39624,14.62899,2.3],
           [1004,53.52379, 14.42902, 18.0],
           [315,53.52379, 14.42902, 18.0],
           [1005,54.56688, 18.41094, 12.3],
           [316,50.28403, 19.31249, 308.3],
           [317,50.28401, 19.3125, 310.6],
           [1041,53.47089, 14.43529, 18.3],
           [1037,53.52404, 14.94064, 44.7]]

def plotStations(indexes):
    for i in indexes:
        plt.plot(stations[i][1],stations[i][2],'rx')

def plotStationsError(indexes):
    stationsSubGroup2 = []
    for i in indexes:
        stationsSubGroup2.append(stations[i])
    stationsSubGroup2 = np.array(stationsSubGroup2)
    anchors,_,_ = check_station(stationsSubGroup2[:,0])

    lonMin = np.min(stationsSubGroup2[:,2])
    lonMax = np.max(stationsSubGroup2[:, 2])
    latMin = np.min(stationsSubGroup2[:, 1])
    latMax = np.max(stationsSubGroup2[:, 1])
    lat_step = (latMax-latMin)/10
    lon_step = (lonMax - lonMin) / 10
    lat_current= latMin
    while (lat_current<latMax):
        lon_current = lonMin
        while (lon_current < lonMax):
            value = compute_DOP_2D(anchors,pm.geodetic2enu(lat_current,lon_current,100,stationsSubGroup2[0][1],stationsSubGroup2[0][2],stationsSubGroup2[0][3]))
            value2=str(value)[0:5],
            plt.text(lat_current, lon_current, value2[0], color="blue", fontsize=6)
            lon_current += lon_step
        lat_current+=lat_step
    plotStations(indexes)
    plt.show()

def check_positions_of_stations(st):
    position = np.zeros([len(st),3])

    for station in stations:
        for i,s in enumerate(st):
            if s == station[0]:
                position[i,:] = station[1::]
    return position

def transform_axis(estimator,st0):
    for station in stations:
        if st0 == station[0]:
            position = station[1::]
            break
    try:
        out = pm.enu2geodetic(estimator[0],estimator[1],estimator[2],position[0],position[1],position[2])
    except:
        return None
    return out


def check_ranges(TDOA):
    ranges = [0]
    parameter = c/(10**9)
    for T in TDOA:
        ranges.append(T*parameter)
    return ranges


def check_station(st):
    position = check_positions_of_stations(st)
    position_xyz2 = np.zeros([len(st),3])

    for i in range(3):
        position_xyz2[i,:] = pm.geodetic2enu(position[i,0],position[i,1],position[i,2],position[0,0],position[0,1],position[0,2])
    bounds = np.array([[np.min(position_xyz2[:,0]),np.min(position_xyz2[:,1]),np.min(position_xyz2[:,2])],[np.max(position_xyz2[:,0]),np.max(position_xyz2[:,1]),np.max(position_xyz2[:,2])]])

    return position_xyz2,bounds,position



def check_station_old(st0,st1,st2):
    position = check_positions_of_stations([st0,st1,st2])
    position_xyz = np.zeros([3,3])

    #for station in stations:
    #    if st0 == station[0]:
    #        position[0,:] = station[1::]
    #    if st1 == station[0]:
    #        position[1,:] = station[1::]
    #    if st2 == station[0]:
    #        position[2,:] = station[1::]
    for i in range(3):
        position_xyz[i,:] = pm.geodetic2ecef(position[i,0],position[i,1],position[i,2])
    bounds = np.array([[np.min(position_xyz[:,0]),np.min(position_xyz[:,1]),np.min(position_xyz[:,2])],[np.max(position_xyz[:,0]),np.max(position_xyz[:,1]),np.max(position_xyz[:,2])]])


    return position_xyz,bounds,position

def compute_position_error(estimator_earth_axis,lat,long,alt):
    #return np.linalg.norm([abs(estimator_earth_axis[0]-lat),abs(estimator_earth_axis[1]-long),abs(estimator_earth_axis[2]-alt)])
    helper = pm.geodetic2enu(estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2],lat,long,alt)
    return np.linalg.norm(helper)


def compute_ranges_error(estimator_earth_axis,st,ranges):
    position = check_positions_of_stations(st)
    range_computed = np.zeros(len(st))
    for i in range(len(st)):
        range_computed[i] = np.linalg.norm(pm.geodetic2enu(estimator_earth_axis[0],estimator_earth_axis[1],
                                                        estimator_earth_axis[2],position[i,0],position[i,1],position[i,2]))
    range_computed = range_computed-range_computed[0]
    error = np.linalg.norm(range_computed-ranges)
    return error

def compute_position_old_error(ADSB_lat,ADSB_long,alt,MLAT_lat,MLAT_long):
    position = pm.geodetic2enu(ADSB_lat,ADSB_long,alt,MLAT_lat,MLAT_long,alt)
    error = np.linalg.norm(position)
    return error


data = []



df = pd.DataFrame(data, columns = ['Name','Altitude','MLAT_timestamp', 'MLAT_latitude','MLAT_longitude',
                                   'ADSB_timestamp','ADSB_latitude','ADSB_longitude',
                                   'Error','Station_0','Station_1','TDOA1','TDOA1_ADSB','TDOA1_error','Station_2','TDOA2',
                                   'TDOA2_ADSB','TDOA2_error'])
i=0
helper = []
plane_name=''
flag=True
start=3
qwe=-1
with open('output_clean.txt') as f:
    for line in f:
        # 27360 ciężki
        # 27368 lekki
        # 11056 zakręt
        # 64 Błąd w połowie
        # 5456 Dbore
        # 10472 Badziew
        # 18464 W połowie uciętę
        # 37928 Przerwa
        # 42128 Najgorzej
        if i<11056:
            i = i + 1
            continue
        if i%8==0:
            #print(line.split()[1][1:-1])

            helper.append(float.fromhex(line.split()[1][1:-1]))
            if plane_name == '':
                plane_name = helper[0]
            else:
                if helper[0]!=plane_name:
                    flag=False
            helper.append(float(line.split()[3]))
        elif i%8==1:
            helper.append(float(line.split()[1][4:-2]))
            helper.append(float(line.split()[2][0:-1]))
            helper.append(float(line.split()[3]))
        elif i%8==2:
            helper.append(float(line.split()[1][4:-2]))
            helper.append(float(line.split()[2][0:-1]))
            helper.append(float(line.split()[3]))
        elif i % 8 == 3:
            helper.append(float(line.split()[6][0:-2]))
        elif i % 8 == 4:
            helper.append(float(line.split()[0]))
        elif i % 8 == 5:
            for l in line.split():
                helper.append(float(l))
        elif i % 8 == 6:
            for l in line.split():
                helper.append(float(l))
        elif i%8 ==7:
            #for i in range(len(helper)):
            #    if helper[i][-2::] == '\n':
            #        helper[i] = helper[0:-2]
            if flag:
                df.loc[i//8] = helper
            helper=[]
            flag=True



        i = i+1
        #if i==(8*5000):
        #    break
row = df.to_numpy()
errors_positions=[]
errors_ranges=[]
errors_positions_old=[]
errors_ranges_old=[]
errors_positions_correct_alt=[]
errors_ranges_correct_alt=[]

mean_time_needed=0
times=[]
times2=[]
avoided_index=[]
'''
for index in range(len(df)):

    anchors,bounds,positions = check_station_old(row[index][Station_0],row[index][Station_1],row[index][Station_2])
    #node = check_node(row['ADSB_latitude'],row['ADSB_longitude'],row['Altitude'],row['Station_0'],row['station_1'])
    #ranges = check_ranges([row[index][TDOA1],row[index][TDOA2]])

    measurments=[[receiver(anchors[0]),0,0.00001],[receiver(anchors[1]),row[index][TDOA1]*10**(-9),0.00001],[receiver(anchors[2]),row[index][TDOA2]*10**(-9),0.00001]]

    t = time.time()
    estimator, result= solve(measurments,row[index][Altitude],0.3038*250,(anchors[0]+anchors[1]+anchors[2])/3)#MLAT.mlat(anchors, ranges,height=row[index][Altitude],method='taylor2.5D_sphere',base_station=positions[0,:])

    if estimator is None:
        print(index)
        avoided_index.append(index)
        continue
    mean_time_needed += time.time() - t
    times.append(mean_time_needed)
    estimator_earth_axis = pm.ecef2geodetic(estimator[0],estimator[1],estimator[2])

    #estimator_earth_axis = transform_axis(estimator,row[index][Station_0])
    if estimator_earth_axis is None:
        continue
    errors_positions.append(compute_position_error(estimator_earth_axis,row[index][ADSB_latitude],row[index][ADSB_longitude],row[index][Altitude]))
    mean_time_needed += time.time()-t
    #corrected_estimation = ( estimator_earth_axis[0],estimator_earth_axis[1],row['Altitude'])
    #errors_positions_correct_alt.append(
    #    compute_position_error(corrected_estimation, row['ADSB_latitude'], row['ADSB_longitude'], row['Altitude']))
    #errors_ranges.append(compute_ranges_error(estimator_earth_axis,row[index][Station_0],row[index][Station_1],row[index][Station_2],ranges))
    #errors_ranges_correct_alt.append(compute_ranges_error(corrected_estimation,row['Station_0'],row['Station_1'],row['Station_2'],ranges))
    #errors_ranges_old.append(compute_ranges_error((row[index][MLAT_latitude],row[index][MLAT_longitude],row[index][Altitude]),row[index][Station_0],row[index][Station_1],row[index][Station_2],ranges))

    errors_positions_old.append(compute_position_old_error(row[index][ADSB_latitude],row[index][ADSB_longitude],row[index][Altitude],row[index][MLAT_latitude],row[index][MLAT_longitude]))

    #errors_ranges.append(compute_ranges_error(row['TDOA1_error']+row['TDOA2_error']))
    #print(1)
'''
print(len(row))

#plotStationsError([0,1,6,7])
#plt.show()
#input()

if start==4:
    A = np.array([[1,0,-1,0],[0,1,0,-1],[0,0,1,0],[0,0,0,1]],dtype=float)
    C = np.array([[1,0,0,0],[0,1,0,0]],dtype=float)
    observation = np.array([row[0][MLAT_latitude],row[0][MLAT_longitude],row[1][MLAT_latitude],row[1][MLAT_longitude],
                            row[2][MLAT_latitude],row[2][MLAT_longitude],row[3][MLAT_latitude],row[3][MLAT_longitude]])
    timestamps = [0,(row[1][Mlat_timestamp]-row[0][Mlat_timestamp])/10**9,(row[2][Mlat_timestamp]-row[1][Mlat_timestamp])/10**9,
                  (row[3][Mlat_timestamp]-row[2][Mlat_timestamp])/10**9]
    plane_state = StateEstimation(A,C,observation,timestamps)

elif start==2:
    A = np.array([[1, 0, -1, 0], [0, 1, 0, -1], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)
    C = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=float)
    observation = np.array(
        [[row[0][MLAT_latitude], row[0][MLAT_longitude]], [row[1][MLAT_latitude], row[1][MLAT_longitude]]])
    t_step = (row[1][Mlat_timestamp]-row[0][Mlat_timestamp])/10**9
    base_staion = check_positions_of_stations([row[1][Station_0]])
    anchors, _,_ = check_station([row[1][Station_0], row[1][Station_1], row[1][Station_2]])
    plane_state = KalmanMLAT(A,C,observation,t_step,50/(10**(9))*c,anchors,row[0][Altitude],base_staion[0])
elif start==3:

    A = np.array([[1,0,-1,0,0,0],[0,1,0,-1,0,0],[0,0,1,0,-1,0],[0,0,0,1,0,-1],[0,0,0,0,1,0],[0,0,0,0,0,1]],dtype=float)
    C = np.array([[1,0,0,0,0,0],[0,1,0,0,0,0]],dtype=float)
    observation = np.array(
        [[row[0][MLAT_latitude], row[0][MLAT_longitude]], [row[1][MLAT_latitude], row[1][MLAT_longitude]],
         [row[2][MLAT_latitude], row[2][MLAT_longitude]]])
    t_step = [(row[1][Mlat_timestamp]-row[0][Mlat_timestamp])/10**9,(row[2][Mlat_timestamp]-row[1][Mlat_timestamp])/10**9]
    base_staion = check_positions_of_stations([row[1][Station_0]])
    anchors, _,_ = check_station([row[1][Station_0], row[1][Station_1], row[1][Station_2]])
    plane_state = KalmanMLAT(A,C,observation,t_step,50/(10**(9))*c,anchors,row[0][Altitude],base_staion[0])
elif start==1:
    plane_state = Cloud(500, [row[0][MLAT_latitude], row[0][MLAT_longitude], row[0][Altitude], 0, 0, 0, 0, 0, 0], np.array([0.1, 0.1, 0.1, 0.00001, 0.00001, 0.00001, 0.0000001, 0.0000001, 0.0000001]))
elif start==20:
    A = np.array([[1,0,-1,0,0,0],[0,1,0,-1,0,0],[0,0,1,0,-1,0],[0,0,0,1,0,-1],[0,0,0,0,1,0],[0,0,0,0,0,1]],dtype=float)
    C = np.array([[1,0,0,0,0,0],[0,1,0,0,0,0]],dtype=float)
    observation =[]
    for i in range(20):
        observation.append(row[i][MLAT_latitude])
        observation.append(row[i][MLAT_longitude])

    timestamps = [0]
    for i in range(19):
        timestamps.append((row[i+1][Mlat_timestamp]-row[i][Mlat_timestamp])/10**9)

    plane_state = StateEstimation(A,C,observation,timestamps)
else:
    A = np.array([[1,0,-1,0,0,0],[0,1,0,-1,0,0],[0,0,1,0,-1,0],[0,0,0,1,0,-1],[0,0,0,0,1,0],[0,0,0,0,0,1]],dtype=float)
    C = np.array([[1,0,0,0,0,0],[0,1,0,0,0,0]],dtype=float)
    observation = np.array([row[0][MLAT_latitude],row[0][MLAT_longitude],row[1][MLAT_latitude],row[1][MLAT_longitude],
                            row[2][MLAT_latitude],row[2][MLAT_longitude],row[3][MLAT_latitude],row[3][MLAT_longitude],
                            row[4][MLAT_latitude],row[4][MLAT_longitude],row[5][MLAT_latitude],row[5][MLAT_longitude]])
    timestamps = [0,(row[1][Mlat_timestamp]-row[0][Mlat_timestamp])/10**9,(row[2][Mlat_timestamp]-row[1][Mlat_timestamp])/10**9,
                  (row[3][Mlat_timestamp]-row[2][Mlat_timestamp])/10**9,(row[4][Mlat_timestamp]-row[3][Mlat_timestamp])/10**9,
                  (row[5][Mlat_timestamp]-row[4][Mlat_timestamp])/10**9]
    plane_state = StateEstimation(A,C,observation,timestamps)
long_estimated=[]
lan_estimated=[]
errors_tracking_prediction=[]
for  i in range(start,len(row)):
    if start==4 or start==6or start >6:
        #errors_tracking_prediction.append(
        #print(
        #    plane_state.update([row[i][MLAT_latitude],row[i][MLAT_longitude]],
        #                       (row[i][Mlat_timestamp]-row[i-1][Mlat_timestamp])/10**9,row[i][Altitude]))
        error = plane_state.update_excluding_outliers([row[i][MLAT_latitude],row[i][MLAT_longitude]],
                               (row[i][Mlat_timestamp]-row[i-1][Mlat_timestamp])/10**9,row[i][Altitude])#,3400)
        if error is not None:
            errors_tracking_prediction.append(error)
    elif start==1:
        plane_state.get_new_msg([row[i][MLAT_latitude], row[i][MLAT_longitude],row[i][Altitude]],
                           (row[i][Mlat_timestamp] - row[i - 1][Mlat_timestamp]) / 10 ** 9)
    else:
        anchors, _, _ = check_station([row[i][Station_0], row[i][Station_1], row[i][Station_2]])
        base_staion = check_positions_of_stations([row[i][Station_0]])
        plane_state.update_excluding_outliers([row[i][MLAT_latitude], row[i][MLAT_longitude]],
                           (row[i][Mlat_timestamp] - row[i - 1][Mlat_timestamp]) / 10 ** 9,anchors,row[i][Altitude],base_staion[0])
    lan_estimated.append(plane_state.state[0])
    long_estimated.append(plane_state.state[1])
    if i%100==qwe or i==334:
        plt.plot(row[0:i, ADSB_latitude], row[0:i, ADSB_longitude])
        plt.plot(row[0:i, MLAT_latitude], row[0:i, MLAT_longitude], 'x')
        plt.plot(lan_estimated,long_estimated)
        plotStations([0,1,6,7])

        plt.show()
plt.plot(errors_tracking_prediction,'x')
#print(errors_tracking_prediction[-1])
plt.show()
plotStations([0,1,6,7])
plt.plot(row[0:i, ADSB_latitude], row[0:i, ADSB_longitude],label='ADSB data')
plt.plot(row[0:i, MLAT_latitude], row[0:i, MLAT_longitude], 'x',label='Multilateration data')
plt.plot(lan_estimated, long_estimated,label='UFIR estimation')
plt.legend()
plt.show()

#mean_time_needed=0
'''
for index in range(len(df)):
    if index in avoided_index:
        continue

    anchors,bounds,positions = check_station([row[index][Station_0],row[index][Station_1],row[index][Station_2]])
    #node = check_node(row['ADSB_latitude'],row['ADSB_longitude'],row['Altitude'],row['Station_0'],row['station_1'])
    ranges = check_ranges([row[index][TDOA1],row[index][TDOA2]])
    t = time.time()
    estimator, result= MLAT.mlat(anchors, ranges,height=row[index][Altitude],method='taylor2.5D_sphere',base_station=positions[0,:])
    estimator_earth_axis = transform_axis(estimator,row[index][Station_0])

    if estimator_earth_axis is None:
        print(index)
        continue
    mean_time_needed += time.time() - t
    errors_positions.append(compute_position_error(estimator_earth_axis,row[index][ADSB_latitude],row[index][ADSB_longitude],row[index][Altitude]))
    errors_positions_old.append(compute_position_old_error(row[index][ADSB_latitude],row[index][ADSB_longitude],row[index][Altitude],row[index][MLAT_latitude],row[index][MLAT_longitude]))
    errors_ranges.append(
        compute_ranges_error(estimator_earth_axis,[ row[index][Station_0], row[index][Station_1], row[index][Station_2]],
                             ranges))
    errors_ranges_old.append(
        compute_ranges_error((row[index][MLAT_latitude], row[index][MLAT_longitude], row[index][Altitude]),
                             [row[index][Station_0], row[index][Station_1], row[index][Station_2]], ranges))

    times2.append(mean_time_needed)

print('time needed')
print(mean_time_needed)
#errors=[]
indexes=[]
i=0
#for e1,e2 in zip(errors_positions,errors_positions_old):
#    errors.append(e1/e2)
#    indexes.append(i)
#    i=i+1
for _ in range(500):
    indexes.append(i)
    i = i + 1

errors_ranges.sort()
print(errors_ranges)
print(statistics.mean(errors_ranges))
#errors.sort()
#print(errors)
#print(statistics.mean(errors))
#plt.plot(indexes[0:len(times)],times)
plt.plot(indexes[0:len(times2)],times2)

plt.show()
# 1.092956228277192
# 0.9972731789855185
'''