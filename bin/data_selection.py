##       LCP module A, Physics of Data
##      AY 2021/22, University of Padua
##
##  code by Barone Francesco Pio
##  19 gen 2022, on Linux x64 Jupyter


# requirements
import pandas as pd
import numpy as np
import math
from scipy import stats




#############################
### dataframe preprocessing #
#############################

def preprocess_dataset(data):  # doing some preprocessing on the Run data

    # detector, layer, tile
    data['detector'] = pd.Series( (data["TDC_CHANNEL"]/64).apply(np.ceil) + data["FPGA"]*2 , dtype='int')
    data['layer'] = pd.Series( data.TDC_CHANNEL%4, dtype='int')
    data['layer'].replace( {0:1, 2:2, 3:3, 1:4}, inplace=True)
    data['tile']  = pd.Series( ( ((data.TDC_CHANNEL-1)%64)/4 ).apply(np.floor) , dtype='int')

    # time [ns]
    t0 = data.ORBIT_CNT.min() # NOTE: because ORBIT_CNT is huge, I shift the time values by the minimum ORBIT_CNT
    data['t'] = pd.Series( (data.ORBIT_CNT-t0)*3564*25 + data.BX_COUNTER*25 + data.TDC_MEAS*25/30)

    # manage trigger hits
    data = data.rename(columns={"HEAD": "trigger"})  # since HEAD is useless, I use it as a trigger marker
    data.loc[data.TDC_CHANNEL > 128, ['detector','layer','tile']] = 0  # because these values do not make sense for triggers
    data.loc[data.TDC_CHANNEL <= 128, 'trigger'] = 0
    
    return data

##  call the function as:   data = preprocess_dataset(data)




def read_preprocessed_dataset(file_name):
    evs = pd.read_csv(file_name, sep=",")
    evs['LAYERS'] = evs['LAYERS'].astype(str)
    for i in range(1, 5):
        evs['L'+str(i)+'_HIT'] = evs['L'+str(i)+'_HIT'].astype('Int64')
        evs['L'+str(i)+'_CELL'] = evs['L'+str(i)+'_CELL'].astype('Int64')
    return evs





##########################################
### data selection: close hit clustering #
##########################################


def enhanced_close_hit_clustering(data, time_tolerance = 390, keep_rejected = True):
    ## note:  input must be the dataframe to process WITHOUT the triggers
    
    events = []        # list which stores the selected events
    evs_det = []
    if keep_rejected:
        rejected = []  # if asked, store the sensitivity-rejected events
        rej_det = []
        
    for i in range(1,62,2):
    
        # margins for the active mask
        lma, rma = i, i+3
        # margins for the sensitivity mask (inclusive)
        lms, rms = max(0, i-4), min(64, i+7)
        
        # slicing by TDC_CHANNEL & selection
        df = data[ ((data['TDC_CHANNEL']-1)%64).between(lms-1,rms-1,inclusive='both') ].sort_values(by=['detector','t'])
        df['dt'] = df['t'] - df['t'].shift(1)  # calculating dt
        df.loc[df['dt'] < 0, 'dt'] = 10e6      # solving detector interface issue
        m = df['dt'] < time_tolerance          # mask value with meaningful dt 
        df = df[m.shift(-1)|m]                 # cross-shift the mask to take also the first event of each cluster
        
        # clustering over time and checking event shape
        reject = False
        chain, chain_len = [], 0
        
        rep_checker = np.zeros(4)  # used to discard candidates with hit repetition among layers
        for row in df[['TDC_CHANNEL','t', 'layer','tile','dt','detector']].itertuples(): 
            
            # first element of a new cluster
            if row.dt > time_tolerance:
                
                # store if value is good
                if (((chain_len == 3) or (chain_len == 4)) and (rep_checker.max()==1)):
                    dett = row.detector
                    if not reject:
                        events.append( chain )
                        evs_det.append( dett )
                    elif keep_rejected:
                        rejected.append( chain )
                        rej_det.append( dett )
                
                # resetting the data structure
                reject = False
                chain, chain_len =  [ (row.Index, row.t, row.layer, row.tile) ] , 0
                rep_checker.fill(0);
            
            # another element of cluster
            else:
                chain.append( (row.Index, row.t, row.layer, row.tile) )
            
            # checking if hit is in active mask
            if (lma <= ((row.TDC_CHANNEL-1)%64)+1 <= rma):  
                rep_checker[row.layer-1] += 1; 
                chain_len = chain_len + 1;
            else:
                reject = True
    
    if keep_rejected: return { 'events': events, 'detectors' : evs_det }, { 'events': rejected, 'detectors' : rej_det }
    else: return { 'events': events, 'detectors' : evs_det }, {}



##################################
### data migration: save to file #
##################################

def export_events_to_dataframe(dic):
    # this function takes as input a dictionary, takes the events and creates a dataframe on it
    
    lst = dic['events']
    det = dic['detectors']
    
    unwrapped = []
    for idx, event in enumerate(lst):
        x = [None, None, None]*4 + [None]*2
        #  to optimize memory it would be great to have [0, None, 0] ...
        
        layers_id = []
        
        for hit in event:
            hit_id, time, l, tile = hit
            layers_id.append(l)  # to create the layer label
            l = int(l-1)
            x[l*3 ] = int(hit_id)
            x[l*3 + 1] = time
            x[l*3 + 2] = int(tile)
            
        sorted_list = sorted(layers_id)
        x[-1] = str(''.join(str(e) for e in sorted_list))
        x[-2] = det[idx]
        unwrapped.append(x)
    me = pd.DataFrame( unwrapped,
                       columns=['L1_HIT','L1_TIME','L1_CELL', 'L2_HIT','L2_TIME','L2_CELL',
                                'L3_HIT','L3_TIME','L3_CELL', 'L4_HIT','L4_TIME','L4_CELL','DETECTOR','LAYERS'] )
    for i in range(1,5): # converting to Int64
        me[f'L{i}_CELL'] = me[f'L{i}_CELL'].astype('Int64')
        me[f'L{i}_HIT'] = me[f'L{i}_HIT'].astype('Int64')
    return me


# call it as dout = export_events_to_dataframe(devs)     
#    ^^ evs is the dictionary in output from algorithm
#  then you can save them to a file, if you like!