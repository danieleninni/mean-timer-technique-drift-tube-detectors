##       LCP module A, Physics of Data
##      AY 2021/22, University of Padua
##
##  code by Barone Francesco Pio
##  19 gen 2022, on Linux x64 Jupyter


# requirements
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import matplotlib.colors as mc
import math
from scipy import stats



#####  !    import this file as   ####################
# from bin.plotters import plot_event_from_dataframe
# from bin.plotters import plot_event                  <- only if you work with low-level algorithm


###################
###   builders    #
###################


def plot_hits(hit_list, title = None, note = None, focus_area = False,
              legend_primer = '"[{:03d}] {:.2f}ns ({:+.2f})".format(hit_id,time,time-first_time)', 
              legend_x_shift = 0, no_axis = 'default', show_plt = True,
              tile_edgecolor = 'dimgray', tile_linewidth = 0.7, tile_alpha = 1, override_tile_colors = None,
              wire_enable = False, wire_size = 1, wire_alpha = 1, wire_color = 'k' ):
    # This function plots the detector tiles pattern and marks with colors the tiles which register a hit.
    #  input:  hit_list    a list of hits, for instance:  [ (31, 14696.6, 1, 13), (29, 14645.0, 2, 13) ]
    #                           -> each hit is a tuple containing ( HIT_ID, time [ns], layer, tile )
    #     optional:
    #          focus_area     (False)   if True restricts the are of the plot to the zone of detector
    #                                     which is affected by hits
    #          legend_primer  (format)  set the format of the legend
    #                                     -> use 'None' to disable legend
    #                                     -> available variables:   hit_id, time, prev_time, layer, tile, idx
    #          note           (None)    if there is some text, adds it in lower left side of the plot
    #                                     note: do not use it with limited_area = True
    #          ...      the other parameters change the aesthetis of the plot
    #
    #  output:   tiles     a matrix to control the properties of the tiles
    
    fig = plt.figure(figsize=(10, 2), dpi=120)
    ax  = fig.add_subplot(111)
    
    # detector pattern
    dx, dy =  42, 13           # tile shape
    n_layers, n_tiles = 4, 16  # number of layers, and number of tiles per layer
    
    # hit color list
    if override_tile_colors: color_list = [ override_tile_colors ]*len(hit_list)
    elif len(hit_list) <= 4: color_list = ['tomato','gold','seagreen','dodgerblue']
    else:
        color_list = ['tomato', 'orange', 'gold', 'springgreen', 'turquoise',
                      'dodgerblue', 'navy', 'mediumpurple','violet', 'hotpink',
                      'lightcoral','peru','olivedrab','indigo','magenta']
        
    wires = [];  tiles = [];
    for jj in range(n_layers):
        row = [];
        for ii in range(n_tiles):
            t = ptc.Rectangle( (ii*dx-dx*(jj%2)/2,jj*dy), dx, dy, 
                              edgecolor=tile_edgecolor,facecolor='none',linewidth=tile_linewidth)
            ax.add_patch( t )
            row.append(t)
            wires.append( (ii*dx-dx*(jj%2)/2 + dx/2, jj*dy + dy/2) )
            #ax.text(ii*dx+dx*(jj%2)/2, jj*dy, f'{ii+1}')
        tiles.append(row)
    del row
    
    plt.xlim(-3*dx/2, dx*n_tiles + dx);    plt.ylim(-dy*5, dy*n_layers + 5);
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout();    ax.xaxis.set_visible(False);    ax.yaxis.set_visible(False);
    
    if title: plt.title(title)
    if no_axis == 'default':
        if focus_area: no_axis = True
        else: no_axis = False
    if no_axis: ax.axis('off')
    if focus_area: tiles_range = []
    
    for idx, hit in enumerate(hit_list):
        hit_id, time, layer, tile = hit  # these values are available to legend_primer
        if idx == 0: 
            prev_time = time;  first_time = time;
        tiles[layer-1][tile].set( facecolor=mc.to_rgba(color_list[idx], alpha=tile_alpha),
                                  label=eval(legend_primer) ) 
        prev_time = time
        if focus_area: tiles_range.append(hit[3])   
        
    if focus_area:  # if true, plots only the appropriate range of tiles
        plt.xlim( -3 + dx*(min(tiles_range)-1), 3 + dx*max(tiles_range) + 3*dx/2)
        plt.ylim( -dy, dy*n_layers + 5)
        if legend_primer != 'None':
            plt.legend( prop={'size': 7}, bbox_to_anchor=(0.98 + legend_x_shift, 0.42) )
        if note: ax.text(3 + dx*(max(tiles_range)-2.5) + 3*dx/2, -dy/2 , note, size=8)
    else:
        if note: ax.text(0, -17, note, size=8)
        if legend_primer != 'None':
            plt.legend( prop={'size': 7}, bbox_to_anchor=(1 + legend_x_shift, 0.42) )
    
    if wire_enable: plt.scatter(*zip(*wires), c=wire_color, s=wire_size, alpha=wire_alpha, zorder=2)
    if show_plt: plt.show()
    return tiles, wires


def scale_lightness( mrgba, scale_l):
    rgba = mc.to_rgba( mrgba );  # converting color from matlab to rgb
    darker_color = [1]*4
    for i in range(0,3):  darker_color[i] = rgba[i]*scale_l
    darker_color[3] = 1
    return np.array(darker_color)


def plot_positions( hits_list, position_list, unsolved = False, hit_size = 18, 
                    tile_black = 0.15, marker_darken = 0.85,
                    legend_primer = '"[{:03d}] {:.2f}mm (t: {:+.2f}ns)".format(hit_id,pos,time-first_time)',
                    legend_x_shift = 0, focus_area=False,**kwargs):
    # This function plots the events as x markers given the hits list and the position of the 
    #  marker within each tile.
    #  input:  hit_list    a list of hits, for instance:  [ (31, 14696.6, 1, 13), (29, 14645.0, 2, 13) ]
    #                           -> each hit is a tuple containing ( HIT_ID, time [ns], layer, tile )
    #          position_list     a list of marker positions, for instance:  [-10, 13, -5, 17]
    #                                -> positive values shift the marker on the x positive axis
    #     optional:
    #          unresolved     (False)   if True plots the marker simmetrically to the tile wire
    #          hit_size       (18)      size of the hit marker
    #
    #                 the function inherits parameter list from plot_hits(), for instance:
    #          focus_area     (False)   if True restricts the are of the plot to the zone of detector
    #                                     which is affected by hits
    #          note           (None)    if there is some text, adds it in lower left side of the plot
    #                                     note: do not use it with limited_area = True
    #            ....
    #
    #  output:   tiles     a matrix to control the properties of the tiles
    
    n_layers, n_tiles = 4, 16  # number of layers, and number of tiles per layer
    
    if len(hits_list) != len(position_list):
        print('ERROR: hits & positions should have same elements')
    
    # hit color list
    color_list = ['tomato','gold','dodgerblue','seagreen',
                  'orange','cyan','mediumblue','violet','hotpink']
    
    tls, wrs = plot_hits( hits_list, tile_alpha = tile_black, override_tile_colors='k', 
                          legend_primer='None', show_plt = False, focus_area=focus_area, 
                          wire_enable = True, **kwargs);
    
    for idx, hit in enumerate(hits_list):
        hit_id, time, layer, tile = hit  # these values are available to legend_primer
        pos = position_list[idx]
        
        if idx == 0: 
            prev_time = time; first_time = time;  
        wire_coord = wrs[ (layer-1)*n_tiles + tile ]
        mark_coord = ( wire_coord[0] + pos, wire_coord[1] )
        plt.scatter((*mark_coord), zorder=2, c=[scale_lightness(color_list[idx], marker_darken)], 
                     marker='x', s=hit_size, label=eval(legend_primer))
        prev_time = time
        if unsolved:
            mark_coord = ( wire_coord[0] - pos, wire_coord[1] )
            plt.scatter( (*mark_coord), zorder=2, c=[scale_lightness(color_list[idx], marker_darken)], 
                          marker='x', s=hit_size)
    
    if legend_primer != 'None':
        if focus_area:
            plt.legend( prop={'size': 7}, bbox_to_anchor=(0.98 + legend_x_shift, 0.42) )
        else:
            plt.legend( prop={'size': 7}, bbox_to_anchor=(1 + legend_x_shift, 0.42) )
    
    plt.show()
    return tls, wrs





###################
###   external    #
###################




def plot_event(dic, key = None, time_sorting = True, **kwargs):
    
    if not key:  # automatic selecting the plot based on dictionary keys
        if "positions" in dic:  key = 'positional_plot'
        elif "hits" in dic:     key = 'hits_plot'
        else:
            print('ERROR (plot_event): no key found')
            return 0
    
    if time_sorting:    # performs time sorting of events
        # order by second value (the time) of each hit tuple
        sor = sorted( enumerate(dic['hits']), key=lambda tup: tup[1][1]) 
        order = [];  hits = []; 
        for t in sor:
            order.append(t[0]);  hits.append(t[1]);
        dic['hits'] = hits
        
        if "positions" in dic:
            original = dic['positions'];  sor = [];
            for i in order:
                #print(original, i, dic)
                sor.append( original[i] )
            dic['positions'] = sor

    if key == 'hits_plot':
        return plot_hits( dic["hits"], **kwargs)
    elif key == 'positional_plot':
        return plot_positions( dic["hits"], dic["positions"], **kwargs)
    else:
        print('ERROR (plot_event): invalid key')
        return 0



    
    

def plot_event_from_dataframe(df, index = None, key=None, debug =  False, **kwargs):
    
    if index != None:  # if I provide an index, I have to select index row from dataframe
        df = df.loc[[index]]
        df = df.squeeze(axis=0)  # converting to series
    
    dic =  { }
    
    if 'L1_X' in df:
        positions = []
        for i in range(1,5):  # grab only LX_POSITION
            pos = df[f'L{i}_X']
            if math.isnan( pos ): continue
            positions.append(pos)       
        dic['positions'] = positions
    
    if 'L1_TIME' or 'L2_TIME' in df:
        hits = []
        for i in range(1,5):  
            if math.isnan( df[f'L{i}_HIT'] ): continue
            tup = ( int(df[f'L{i}_HIT']) , df[f'L{i}_TIME'], i, int(df[f'L{i}_CELL']) )
            hits.append(tup)
        dic['hits'] = hits
    
    if not bool(dic):
        print('ERROR (plot_event_dataframe): no args found in dataframe, dictionary is empty')
        return 0
    
    if debug: print('PLT DF',dic)
    return plot_event(dic, key=key, **kwargs)