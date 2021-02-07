import pandas as pd
from mlat import MLAT
import numpy as np
import pymap3d as pm
import matplotlib.pyplot as plt
import statistics
import time
from comparison import solve

class receiver:
    def __init__(self,position):
        self.position=position

Altitude = 0
MLAT_latitude=1
MLAT_longitude=2
ADSB_latitude=3
ADSB_longitude=4
Error=5
Station_0=6
Station_1=7
TDOA1=8
TDOA1_ADSB=9
TDOA1_error=10
Station_2=11
TDOA2=12
TDOA2_ADSB=13
TDOA2_error=14

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
        print(st0)
    '''
    METERS_PER_DEGREE_X = R*np.cos(position[0]*2*np.pi/360)*2*np.pi/360
    out = np.zeros(3)
    out[2] = estimator[2]
    out[0] = position[0] + estimator[0]/METERS_PER_DEGREE_Y
    out[1] = position[1] + estimator[1]/METERS_PER_DEGREE_X
    out2 = np.zeros(3)
    out2[2] = estimator[2]
    out2[0] = position[0] - estimator[0]/METERS_PER_DEGREE_Y
    out2[1] = position[1] - estimator[1]/METERS_PER_DEGREE_X
    '''
    return out


def check_ranges(TDOA1,TDOA2):
    ranges = [0]
    parameter = c/(10**9)
    ranges.append(TDOA1*parameter)
    ranges.append(TDOA2*parameter)
    return ranges


def check_station(st0,st1,st2):
    position = check_positions_of_stations([st0,st1,st2])
    position_xyz = np.zeros([3,3])
    position_xyz2 = np.zeros([3,3])

    #for station in stations:
    #    if st0 == station[0]:
    #        position[0,:] = station[1::]
    #    if st1 == station[0]:
    #        position[1,:] = station[1::]
    #    if st2 == station[0]:
    #        position[2,:] = station[1::]
    for i in range(3):
        position_xyz2[i,:] = pm.geodetic2enu(position[i,0],position[i,1],position[i,2],position[0,0],position[0,1],position[0,2])
    bounds = np.array([[np.min(position_xyz[:,0]),np.min(position_xyz[:,1]),np.min(position_xyz[:,2])],[np.max(position_xyz[:,0]),np.max(position_xyz[:,1]),np.max(position_xyz[:,2])]])


    METERS_PER_DEGREE_X = R*np.cos(position[0,0]*2*np.pi/360)*2*np.pi/360
    position_xyz[0,2] = position[0,2]
    position_xyz[1,2] = position[1,2]
    position_xyz[2,2] = position[2,2]
    position_xyz[1,0] = (position[1,1]- position[0,1])*METERS_PER_DEGREE_X
    position_xyz[2,0] = (position[2,1]- position[0,1])*METERS_PER_DEGREE_X
    position_xyz[1,1] = (position[1,0]- position[0,0])*METERS_PER_DEGREE_Y
    position_xyz[2,1] = (position[2,0]- position[0,0])*METERS_PER_DEGREE_Y

    return position_xyz2,bounds,position



def check_station_old(st0,st1,st2):
    position = check_positions_of_stations([st0,st1,st2])
    position_xyz = np.zeros([3,3])
    position_xyz2 = np.zeros([3,3])

    #for station in stations:
    #    if st0 == station[0]:
    #        position[0,:] = station[1::]
    #    if st1 == station[0]:
    #        position[1,:] = station[1::]
    #    if st2 == station[0]:
    #        position[2,:] = station[1::]
    for i in range(3):
        position_xyz2[i,:] = pm.geodetic2ecef(position[i,0],position[i,1],position[i,2])
    bounds = np.array([[np.min(position_xyz[:,0]),np.min(position_xyz[:,1]),np.min(position_xyz[:,2])],[np.max(position_xyz[:,0]),np.max(position_xyz[:,1]),np.max(position_xyz[:,2])]])


    METERS_PER_DEGREE_X = R*np.cos(position[0,0]*2*np.pi/360)*2*np.pi/360
    position_xyz[0,2] = position[0,2]
    position_xyz[1,2] = position[1,2]
    position_xyz[2,2] = position[2,2]
    position_xyz[1,0] = (position[1,1]- position[0,1])*METERS_PER_DEGREE_X
    position_xyz[2,0] = (position[2,1]- position[0,1])*METERS_PER_DEGREE_X
    position_xyz[1,1] = (position[1,0]- position[0,0])*METERS_PER_DEGREE_Y
    position_xyz[2,1] = (position[2,0]- position[0,0])*METERS_PER_DEGREE_Y

    return position_xyz2,bounds,position

def compute_position_error(estimator_earth_axis,lat,long,alt):
    #return np.linalg.norm([abs(estimator_earth_axis[0]-lat),abs(estimator_earth_axis[1]-long),abs(estimator_earth_axis[2]-alt)])
    helper = pm.geodetic2enu(estimator_earth_axis[0],estimator_earth_axis[1],estimator_earth_axis[2],lat,long,alt)
    return np.linalg.norm(helper)


def compute_ranges_error(estimator_earth_axis,st0,st1,st2,ranges):
    position = check_positions_of_stations([st0,st1,st2])
    range_computed = np.zeros(3)
    for i in range(3):
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

df = pd.DataFrame(data, columns = ['Altitude', 'MLAT_latitude','MLAT_longitude','ADSB_latitude','ADSB_longitude',
                                   'Error','Station_0','Station_1','TDOA1','TDOA1_ADSB','TDOA1_error','Station_2','TDOA2',
                                   'TDOA2_ADSB','TDOA2_error'])
i=0
helper = []
with open('output_clean.txt') as f:
    for line in f:
        if i%8==0:
            helper.append(float(line.split()[3]))
        elif i%8==1:
            helper.append(float(line.split()[2][0:-1]))
            helper.append(float(line.split()[3]))
        elif i%8==2:
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
            df.loc[i//8] = helper
            helper=[]


        i = i+1
        if i==(8*5000):
            break
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

for index in range(len(df)):

    anchors,bounds,positions = check_station_old(row[index][Station_0],row[index][Station_1],row[index][Station_2])
    #node = check_node(row['ADSB_latitude'],row['ADSB_longitude'],row['Altitude'],row['Station_0'],row['station_1'])
    #ranges = check_ranges(row[index][TDOA1],row[index][TDOA2])

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
mean_time_needed=0
for index in range(len(df)):
    if index in avoided_index:
        continue

    anchors,bounds,positions = check_station(row[index][Station_0],row[index][Station_1],row[index][Station_2])
    #node = check_node(row['ADSB_latitude'],row['ADSB_longitude'],row['Altitude'],row['Station_0'],row['station_1'])
    ranges = check_ranges(row[index][TDOA1],row[index][TDOA2])
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
        compute_ranges_error(estimator_earth_axis, row[index][Station_0], row[index][Station_1], row[index][Station_2],
                             ranges))
    errors_ranges_old.append(
        compute_ranges_error((row[index][MLAT_latitude], row[index][MLAT_longitude], row[index][Altitude]),
                             row[index][Station_0], row[index][Station_1], row[index][Station_2], ranges))

    times2.append(mean_time_needed)
print('time needed')
print(mean_time_needed)
errors=[]
indexes=[]
i=0
for e1,e2 in zip(errors_positions,errors_positions_old):
    errors.append(e1/e2)
    indexes.append(i)
    i=i+1
for _ in range(500):
    indexes.append(i)
    i = i + 1

errors_ranges.sort()
print(errors_ranges)
print(statistics.mean(errors_ranges))
errors.sort()
print(errors)
print(statistics.mean(errors))
plt.plot(indexes[0:len(times)],times)
plt.plot(indexes[0:len(times2)],times2)

plt.show()
# 1.092956228277192
# 0.9972731789855185