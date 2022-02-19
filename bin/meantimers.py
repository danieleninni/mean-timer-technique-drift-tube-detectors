##       LCP module A, Physics of Data
##      AY 2021/22, University of Padua
##
##  code by Ninni Daniele
##  19 gen 2022, on Linux x64 Jupyter


# requirements
import numpy as np
import pandas as pd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import matplotlib.colors as mc
import math
from scipy import stats


#  Note: the function to read the data from can be found in bin/data_preprocessing.py



###########
### angle #
###########


# define the function that computes the crossing angle
#         ti : time recorded by the i-th layer's cell
#         tj : time recorded by the (i+2)-th layer's cell
#    v_drift : drift velocity
#          h : height of each cell
# angle_sign : sign of the crossing angle (deduced by applying the mean-timer technique)
def crossing_angle(ti, tj, v_drift, h, angle_sign):
    
    dx = np.abs(v_drift * (ti-tj))   # projection of the distance between the two hits along the direction of the layers
    angle_tan = dx / (2*h)   # tangent of the crossing angle
    angle = angle_sign * np.rad2deg(np.arctan(angle_tan))
    
    return angle



################
### meantimers #
################


# define the functions that apply the mean-timer technique to the dataset containing the events
#    tmax : maximum drift time
# v_drift : drift velocity
#       h : height of each cell
def meantimer_123(dataframe, tmax, v_drift, h):   # case layers 1-2-3
    
    df = dataframe.copy()
    t1, t2, t3 = df['L1_TIME'], df['L2_TIME'], df['L3_TIME']
    c1, c2, c3 = df['L1_CELL'], df['L2_CELL'], df['L3_CELL']
    
    df['PEDESTAL'] = (t1 + 2*t2 + t3 - 2*tmax) / 4
    
    mask = (c2 == c1)
    
    df.loc[mask, 'PATTERN'] = 'LRL_'
    df.loc[mask, 'ANGLE'] = crossing_angle(t1, t3, v_drift, h, np.sign(t1-t3))
    
    df.loc[~mask, 'PATTERN'] = 'RLR_'
    df.loc[~mask, 'ANGLE'] = crossing_angle(t1, t3, v_drift, h, np.sign(t3-t1))
    
    return df

def meantimer_124(dataframe, tmax, v_drift, h):   # case layers 1-2-4
    
    df = dataframe.copy()
    t1, t2, t4 = df['L1_TIME'], df['L2_TIME'], df['L4_TIME']
    c1, c2, c4 = df['L1_CELL'], df['L2_CELL'], df['L4_CELL']
    
    df['PEDESTAL'] = (2*t1 + 3*t2 - t4 -2*tmax) / 4
    
    mask = (c2 == c1)
    
    df.loc[mask, 'PATTERN'] = 'LR_R'
    df.loc[mask, 'ANGLE'] = crossing_angle(t2, t4, v_drift, h, np.sign(t4-t2))
    
    df.loc[~mask, 'PATTERN'] = 'RL_L'
    df.loc[~mask, 'ANGLE'] = crossing_angle(t2, t4, v_drift, h, np.sign(t2-t4))
    
    return df

def meantimer_134(dataframe, tmax, v_drift, h):   # case layers 1-3-4
    
    df = dataframe.copy()
    t1, t3, t4 = df['L1_TIME'], df['L3_TIME'], df['L4_TIME']
    c1, c3, c4 = df['L1_CELL'], df['L3_CELL'], df['L4_CELL']
    
    df['PEDESTAL'] = (-t1 + 3*t3 + 2*t4 -2*tmax) / 4
    
    mask = (c4 == c1)
    
    df.loc[mask, 'PATTERN'] = 'L_LR'
    df.loc[mask, 'ANGLE'] = crossing_angle(t1, t3, v_drift, h, np.sign(t1-t3))
    
    df.loc[~mask, 'PATTERN'] = 'R_RL'
    df.loc[~mask, 'ANGLE'] = crossing_angle(t1, t3, v_drift, h, np.sign(t3-t1))
    
    return df

def meantimer_234(dataframe, tmax, v_drift, h):   # case layers 2-3-4
    
    df = dataframe.copy()
    t2, t3, t4 = df['L2_TIME'], df['L3_TIME'], df['L4_TIME']
    c2, c3, c4 = df['L2_CELL'], df['L3_CELL'], df['L4_CELL']
    
    df['PEDESTAL'] = (t2 + 2*t3 + t4 -2*tmax) / 4
    
    mask = (c3 == c2)
    
    df.loc[mask, 'PATTERN'] = '_RLR'
    df.loc[mask, 'ANGLE'] = crossing_angle(t2, t4, v_drift, h, np.sign(t4-t2))
    
    df.loc[~mask, 'PATTERN'] = '_LRL'
    df.loc[~mask, 'ANGLE'] = crossing_angle(t2, t4, v_drift, h, np.sign(t2-t4))
    
    return df
 
def meantimer_1234(dataframe, tmax, v_drift, h):   # case layers 1-2-3-4
    
    df = dataframe.copy()
    t1, t2, t3, t4 = df['L1_TIME'], df['L2_TIME'], df['L3_TIME'], df['L4_TIME']
    c1, c2, c3, c4 = df['L1_CELL'], df['L2_CELL'], df['L3_CELL'], df['L4_CELL']
    
    df['PEDESTAL'] = (t1 + 3*t2 + 3*t3 + t4 - 4*tmax) / 8
    
    mask = (c4 == c1)
    angles_tol = 5   # tolerance (deg) on the differences between [crossing angles computed using layers 1-3] and [crossing angles computed using layers 2-4]
    
    df.loc[mask, 'PATTERN'] = 'LRLR'
    angles_13 = crossing_angle(t1, t3, v_drift, h, np.sign(t1-t3))
    angles_24 = crossing_angle(t2, t4, v_drift, h, np.sign(t4-t2))
    d_angles = np.abs(angles_13 - angles_24)
    angles_mask = (d_angles < angles_tol)
    df.loc[mask & angles_mask, 'ANGLE'] = ((angles_13 + angles_24) / 2)
    df.loc[mask & ~angles_mask, 'ANGLE'] = 'FAIL'
    
    df.loc[~mask, 'PATTERN'] = 'RLRL'
    angles_13 = crossing_angle(t1, t3, v_drift, h, np.sign(t3-t1))
    angles_24 = crossing_angle(t2, t4, v_drift, h, np.sign(t2-t4))
    d_angles = np.abs(angles_13 - angles_24)
    angles_mask = (d_angles < angles_tol)
    df.loc[~mask & angles_mask, 'ANGLE'] = ((angles_13 + angles_24) / 2)
    df.loc[~mask & ~angles_mask, 'ANGLE'] = 'FAIL'

    return df


################################
### general meantimer function #
################################
    
def meantimer(dataframe):
    
    df = dataframe.copy()
    
    # dictionary used to select the appropriate function
    meantimers = {'123'  : meantimer_123,
                  '124'  : meantimer_124,
                  '134'  : meantimer_134,
                  '234'  : meantimer_234,
                  '1234' : meantimer_1234}

    # dictionary used to convert the pattern of the trajectory into signs of the positions in the cells
    LR_to_sign = {'L' : -1,
                  'R' : +1,
                  '_' : 0}
    
    # detector parameters
    tmax = 390   # maximum drift time (ns)
    L = 42   # length of each cell (mm)
    h = 13   # height of each cell (mm)
    v_drift = L / (2*tmax)   # drift velocity (mm/ns)
    
    # apply the mean-timer functions to the dataset
    df['PEDESTAL'] = pd.Series(dtype='float')
    df['PATTERN'] = pd.Series(dtype='str')
    df['ANGLE'] = pd.Series(dtype='float')
    
    for i in meantimers:
        mask = (df['LAYERS'] == i)
        df[mask] = (meantimers[i])(df[mask], tmax, v_drift, h)
        
    df = df[df['ANGLE'] != 'FAIL']   # reject 4-hits events for which it is not possible to compute the crossing angle properly
    
    for i in range(1, 5):
        df['L'+str(i)+'_DRIFT'] = df['L'+str(i)+'_TIME'] - df['PEDESTAL']
        df = df[((df['L'+str(i)+'_DRIFT'] < tmax) & (df['L'+str(i)+'_DRIFT'] > 0)) | (np.isnan(df['L'+str(i)+'_DRIFT']))]   # reject events with drift times >= 'tmax' or <= 0
        df['L'+str(i)+'_X'] = v_drift * df['L'+str(i)+'_DRIFT'] * (df['PATTERN'].str[i-1]).replace(LR_to_sign)
    
    df = df.reset_index(drop=True)
    
    return df