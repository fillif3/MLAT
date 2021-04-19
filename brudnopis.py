'''import gmplot
import os
from DOP import compute_DOP_MAP
from color_gradient import linear_gradient
# GoogleMapPlotter return Map object
# Pass the center latitude and
# center longitude
gmap1 = gmplot.GoogleMapPlotter(53.45,
                                14.6,13, apikey = '' )

# Pass the absolute path

stations =[[53.39624,14.62899,2.3],
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
lan_step =0.01
long_step=0.02

colors = linear_gradient("#0000FF","#FF0000",n=30)

Dops,lan,lon,val = compute_DOP_MAP(stations,[min_lan,max_lan],[min_long,max_long],altitude=5000,base=0,case='2D',lan_step=lan_step,long_step=long_step)
for x,y,z in zip(lan,lon,val):
    rectangle = zip(*[
        (x-lan_step/2, y-long_step/2),
        (x-lan_step/2,  y+long_step/2),
        (x+lan_step/2,  y+long_step/2),
        (x+lan_step/2,  y-long_step/2)
    ])
    if z>30:
        gmap1.polygon(*rectangle, face_color='k', edge_color='cornflowerblue', edge_width=0,face_alpha=0.6)
    else:
        print(int(z))
        gmap1.polygon(*rectangle, face_color=colors['hex'][int(z)], edge_color=colors['hex'][int(z)], edge_width=0, face_alpha=0.6)
for station in stations:
    gmap1.circle(station[0], station[1], 400,  ew=3, color='green')

dir_path = os.path.dirname(os.path.realpath(__file__))+'/test.html'
gmap1.draw(dir_path)'''

import control
import numpy as np
A = np.array([[1,0,0.1,0,0.005,0],[0,1,0,0.1,0,0.005],[0,0,1,0,0.1,0],[0,0,0,1,0,0.1],[0,0,0,0,1,0],[0,0,0,0,0,1]])
C = np.array([[1,0,0,0,0,0],[0,1,0,0,0,0]])
O = control.obsv(A, C)
print(np.linalg.matrix_rank(O))