import pandas as pd
from matplotlib import pyplot as plt
import math
#Actually an implementation of the strongest base station selection method

data = pd.read_csv('2018-09-18T20-03-15-500000_1_data_wide.csv')
#Removes unnecessary columns for ease of use in findClosestEdges function
edgeData = data.drop(columns = ['Datetime', 'beaconid', 'realx', 'realy'])
edges = pd.read_csv('edges.csv')
#Remove all edges that are not for beacon 1, can't be used for all files
edges = edges[edges['beaconid'] == 1]


fingerprints_raw = pd.read_csv('2018-09-24T23-12-34-500000_1_data_wide.csv')
fingerprint_map = fingerprints_raw.drop(columns=['Datetime', 'beaconid']).rename(
    {'realx': 'mapx', 'realy': 'mapy'}, axis=1).iloc[::2, :].reset_index(drop=True)


def find_closest_edges():
    closest_edge = pd.DataFrame(columns=['edge'])
    for index, row in edgeData.iterrows():
        #Finds the edge with the largest rssi (Signal strength)
        idmax = row.idxmax().replace("edge_","")
        new_row = {'edge': idmax}
        closest_edge = closest_edge.append(new_row, ignore_index=True)
    return closest_edge

def estimate_movement(closest_edge):
    movement_df = pd.DataFrame(columns=['time', 'estimated_x', 'estimated_y', 
                                        'closest_edge', 'real_x', 'real_y'])
    for index, row in data.iterrows():
        #Finds the closest edge for the current index
        edge = closest_edge.iloc[index]['edge']
        #Finds the closest edge from the edges dataframe,
        #which has the x and y of that edge
        c_edge = edges.loc[edges['edgenodeid'] == int(edge)]
        new_row = {'time': row['Datetime'], 'estimated_x': c_edge['edge_x'].values[0],
                   'estimated_y': c_edge['edge_y'].values[0], 'closest_edge': edge, 
                   'real_x': row['realx'], 'real_y': row['realy']}
        movement_df = movement_df.append(new_row, ignore_index=True)
    return movement_df

def calculate_error(movementDf):
    error_df = pd.DataFrame(columns=['error'])
    for index, row in movementDf.iterrows():
        #Pythagorean formula
        error = math.sqrt(math.pow(float(row['real_x']) - float(row['estimated_x']), 2)
                    +math.pow(float(row['real_y'])-float(row['estimated_y']), 2))
        new_row = {'error': float(error)}
        error_df = error_df.append(new_row, ignore_index=True)
    return error_df

def print_movement(movementDf):
    for index, row in movementDf.iterrows():
        print("At time", row['time'], "user was at", row['estimated_x'], row['estimated_y'])

def plot_error(error_df, title):
    #print(error_df)
    new_error = error_df['error'].round(2)
    #print(new_error)
    error = error_df.error.astype(float)
    mean = error_df['error'].mean()
    print("SBS mean", mean)

    error_plot = error.plot.bar(x='error', rot=0)
    plt.axhline(y=mean, color='r', linestyle='-')
    error_plot.set_title(title)
    error_plot.set_ylabel("Meters")
    labels = ["Error", "Avg. error"]
    handles, _ = error_plot.get_legend_handles_labels()
    handles.append(plt.axhline(y=mean, color='r', linestyle='-'))
    error_plot.legend(handles = handles[0:], labels = labels)
    plt.show()


closest_edge = find_closest_edges()
movementDf = estimate_movement(closest_edge)
error_df = calculate_error(movementDf)
#printMovement(movementDf)
plt.axes().get_xaxis().set_visible(False)
plot_error(error_df, "Error for SBS")


def find_all_nn():
    nn_movementdf = pd.DataFrame(columns=['time', 'realx', 'realy', 'mapx', 'mapy', 'error'])
    for index, row in data.iterrows():
        eu_dist = 9999
        lowest_row_index = 9999
        for index2, row2 in fingerprint_map.iterrows():
            

            edge1 = math.pow(row['edge_1'] - row2['edge_1'],2)
            edge2 = math.pow(row['edge_2'] - row2['edge_2'],2)
            edge3 = math.pow(row['edge_3'] - row2['edge_3'],2)
            edge8 = math.pow(row['edge_8'] - row2['edge_8'],2)
            edge9 = math.pow(row['edge_9'] - row2['edge_9'],2)
            edge10 = math.pow(row['edge_10'] - row2['edge_10'],2)
            edge11 = math.pow(row['edge_11'] - row2['edge_11'],2)
            edge12 = math.pow(row['edge_12'] - row2['edge_12'],2)
            edge13 = math.pow(row['edge_13'] - row2['edge_13'],2)

            c_dist = math.sqrt(edge1 + edge2 + edge3 + edge8 + edge9 + edge10 + edge11 + edge12 + edge13)

            if(c_dist < eu_dist):
                eu_dist = c_dist
                lowest_row_index = index2

        #print(lowest_row_index, eu_dist)
        map_row = fingerprint_map.loc[lowest_row_index]
        error = math.sqrt(math.pow(row['realx'] - map_row['mapx'], 2)+math.pow(row['realy'] - map_row['mapy'], 2))
        new_row = {'time': row['Datetime'], 'realx': row['realx'], 'realy': row['realy'], 'mapx': map_row['mapx'], 'mapy': map_row['mapy'], 'error': error}
        nn_movementdf = nn_movementdf.append(new_row, ignore_index=True)

    #print(nn_movementdf)
    return nn_movementdf
    
def find_3_nn():
    nn_movementdf = pd.DataFrame(columns=['time', 'realx', 
                         'realy', 'mapx', 'mapy', 'error'])
    for index, row in data.iterrows():
        eu_dist = 9999
        lowest_row_index = 9999
        three_strongest = edgeData.loc[index].nlargest(n=3)
        first_ss = three_strongest[0]
        first_edge = three_strongest.index[0]
        second_ss = three_strongest[1]
        second_edge = three_strongest.index[1]
        third_ss = three_strongest[2]
        third_edge = three_strongest.index[2]

        for index2, row2 in fingerprint_map.iterrows():
            first = math.pow(first_ss - row2[first_edge], 2)
            second = math.pow(second_ss - row2[second_edge], 2)
            third = math.pow(third_ss - row2[third_edge], 2)
            c_dist = math.sqrt(first + second + third)

            if(c_dist < eu_dist):
                eu_dist = c_dist
                lowest_row_index = index2
        map_row = fingerprint_map.loc[lowest_row_index]
        error = math.sqrt(math.pow(row['realx'] - map_row['mapx'], 2)
                +math.pow(row['realy'] - map_row['mapy'], 2))
        new_row = {'time': row['Datetime'], 'realx': row['realx'], 
                   'realy': row['realy'], 'mapx': map_row['mapx'], 
                   'mapy': map_row['mapy'], 'error': error}
        nn_movementdf = nn_movementdf.append(new_row, ignore_index=True)
    return nn_movementdf 

#it brokey
def plot_all_error(sbs, three, _all):
    
    print(three)
    all_error_df = pd.DataFrame(columns=['sbs', 'three', 'all'])
    for index, row in sbs.iterrows():
        new_row = {'sbs': row['error'], 'three': three.loc[index]['error'], 'all': _all.loc[index]['error']}
        all_error_df = all_error_df.append(new_row, ignore_index=True)

    #print(all_error_df)
    #print(error_df)
    #new_error = error_df['error'].round(2)
    #print(new_error)
    #error = error_df.error.astype(float)
    #mean = error_df['error'].mean()

    error_plot = all_error_df.plot.bar(x='sbs', rot=0)
    all_error_df.plot.bar(x='three', ax = error_plot, color="C2")
    all_error_df.plot.bar(x='all', ax = error_plot, color="C3")
    #plt.axhline(y=mean, color='r', linestyle='-')
    #error_plot.set_title("Error for n-n algorithm")
    #error_plot.set_ylabel("Meters")
    #labels = ["Error", "Avg. error"]
    #handles, _ = error_plot.get_legend_handles_labels()
    #handles.append(plt.axhline(y=mean, color='r', linestyle='-'))
    #error_plot.legend(handles = handles[0:], labels = labels)
    
    plt.show()           

            

three_nn = find_3_nn()
all_nn = find_all_nn()

#plot_all_error(error_df, three_nn, all_nn)

print("three mean ", three_nn['error'].mean())
print("all mean", all_nn['error'].mean())
plt.axes().get_xaxis().set_visible(False)
plot_error(three_nn, "Error for 3-nn")
plt.axes().get_xaxis().set_visible(False)
plot_error(all_nn, "Error for all-nn")


