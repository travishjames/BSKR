# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 15:29:14 2016
@author: dhkim
"""
#%%
from __future__ import division
import pandas as pd
from pandas import Series, DataFrame 
import urllib2
from bs4 import BeautifulSoup
from itertools import islice
import seaborn as sns
import glob, os
#%%
csv_file_name = []

for file in glob.glob("turnstile*.csv"):
    csv_file_name.append(file)
    
datafiles = []
concat_list = []
for csv_file in csv_file_name:
    concat_list.append(pd.read_csv(csv_file)) 
df = pd.concat(concat_list)  
#%%
#dictionary = {}

df.columns = df.columns.map(lambda x: str(x).strip())
usecols = df.columns[4:]

#grouped_object = list(df.groupby(['C/A','UNIT','SCP','STATION']))

#for group in grouped_object:
#    dictionary[group[0]] = group[1][usecols].values
    
#%%  
#from collections import defaultdict
from dateutil.parser import parse

#time_dictionary = {}

#for key,values in dictionary.items():
#    list_of_times = map(lambda x: [parse(' '.join(x[2:4])), x[5]], values)
#    time_dictionary[key] = list_of_times
#%%
df['DATETIME'] = df[['DATE','TIME']].apply(lambda x: ' '.join(x),axis=1)
#%%
df['DATETIME'] = df['DATETIME'].map(lambda x: parse(x)) 
#%%
df.drop(['DATE','TIME'], axis=1, inplace=True)
#%%
df['DAY'] = df['DATETIME'].map(lambda x:x.day)
df['Entered'] = ''
#%%
'''
Each block of turnstiles is called a “Control Area” or “C.A” in the downloaded data. 
Each turnstile is designated with a “SCP” number For each SCP in each C.A we have measurements every 4 hours. 
Each station can include multiple C.A’s. 
We want to compress this data down so that we have a total number of entries and exits for each day. 
Figuring this out is complicated by the fact that each turnstile is equipped with a counter 
that does not reset at the start of each day. 
To see this, you can plot the daily values for an individual SCP in a station.
'''

pd.options.mode.chained_assignment = None

listz = []  

grouped_object = df.groupby(['C/A','UNIT','SCP','STATION'])

for category, dataframe in grouped_object:    
    
    dataframe['Entered'] = (dataframe['ENTRIES'] - dataframe['ENTRIES'].shift()).abs()  
    dataframe['Exited'] = (dataframe['EXITS'] - dataframe['EXITS'].shift()).abs()
    
    dataframe.loc[dataframe['Entered']>3000, 'Entered'] = 0
    dataframe.loc[dataframe['Exited']>3000, 'Exited'] = 0
    
    listz.append(dataframe)    
    
df1 = pd.concat(listz, ignore_index=True)
df1.fillna(0, inplace=True)
#%%

df_concatenated = df1.groupby(['C/A','UNIT','SCP','STATION','DAY'])[['Entered','Exited']].sum()
df_concatenated['IMPRESSIONS'] = df_concatenated.Entered + df_concatenated.Exited
df_concatenated = df_concatenated.reset_index()

#%%
df_concatenated_station = df1.groupby(['STATION','DAY'])[['Entered','Exited']].sum()
df_concatenated_station['IMPRESSIONS'] = df_concatenated_station.Entered + df_concatenated_station.Exited
df_concatenated_station = df_concatenated_station.reset_index() 

#%%
df_concatenated_station.to_csv('./df_concatenated_station_v3.csv')
#%%
import matplotlib.pyplot as plt 
import numpy as np

def get_top_50(grp):
    return grp.sort_values("IMPRESSIONS", ascending = False).head(50)
    # maybe the .head(50) is not reliable

# dude so check this out
    
top50 = df_concatenated_station.groupby('DAY').apply(get_top_50)
# wait so top50 is good no? each day has 50 stations
# so what yielded 64 again im confused 
# oh gotcha im retarded 

#%%
'''
used median instead of mean so that the large outlier days don't affect our data
'''
df_concatenated_day = top50.groupby(['DAY'])[['Entered','Exited']].median()
df_concatenated_day['IMPRESSIONS'] = df_concatenated_day.Entered + df_concatenated_day.Exited
df_concatenated_day = df_concatenated_day.reset_index()

# median impression of top 50 stations by day 
#%% it already ran 


#%% 

# http://stackoverflow.com/questions/4674473/valueerror-setting-an-array-element-with-a-sequence
n_groups = 7
index = np.arange(n_groups)

plt.bar(index, df_concatenated_day['IMPRESSIONS'], color="#b3ccff", align = "center", alpha = .8, width = .5)

plt.xticks(index, ('Saturday','Sunday','Monday','Tuesday','Wednesday','Thursday', 'Friday'), rotation = 45)
plt.xlabel('Day')
plt.ylabel('Median Impressions')
plt.title("Median Impressions Across 50 Stations By Day")

plt.plot(df_concatenated_day['IMPRESSIONS'], color="black", alpha = .8)
plt.show()
#%%
df_net_station = top50.groupby(['STATION'])[['Entered','Exited']].median()
df_net_station['IMPRESSIONS'] = df_net_station.Entered + df_net_station.Exited
df_net_station = df_net_station.reset_index()

#%%
n_groups = 64

listz = df_net_station['STATION'].unique()

index = np.arange(n_groups)
plt.bar(index, df_net_station['IMPRESSIONS'], color="#b3ccff", alpha = .8, width = .55)

plt.xlabel('64 Stations')
plt.ylabel('Total Impressions Across 64 Stations')

plt.title("Net Impressions By Station") # whats the ttile 
plt.show()
#%%

import seaborn as sns 
sns.boxplot(df_net_station['IMPRESSIONS'])
plt.title("Boxplot of Net Impressions By Station") # whats the ttile 


# violin plot to visualize the density estimate and box plot combined in one graph 
# in order to visualize how our data was distributed
# we realized that a long tail on the right indicating that our data contained a couple 

'''
count        64.000000
mean      91286.484375
std       65551.707994
min       23990.000000
25%       49727.750000
50%       72320.500000
75%      124201.750000
max      319170.000000
'''
#%%

common_stations = []
for x in range(10,17):
    common_stations.append(list(top50.loc[x]['STATION']))
#Get intersection of all common stations    
result = set(common_stations[0])
for s in common_stations[1:]:
    result.intersection_update(s)
print result    
result_list = list(result)

common_df = top50[top50['STATION'].isin(result_list)]


#%%


common_df_sum = common_df.groupby(['STATION'])['IMPRESSIONS'].median()

n_groups = 38

index = np.arange(n_groups)
plt.bar(index, list(common_df_sum), color="#b3ccff", alpha = .8, width = .5)
plt.xticks(index,result_list, rotation = 90)

plt.xlabel('Station')
plt.ylabel('Impressions For Each Common Station')

plt.title("Impressions Per Station for Common Stations") # whats the ttile 
plt.show()

#%%

unique_stations = []
for x in range(10,17):
    unique_stations.append(list(top50.loc[x]['STATION']))
#Get intersection of all common stations    
result2 = set(unique_stations[0])
for s in unique_stations[1:]:
    
    result2.intersection_update(s)
print result2    
result_list2 = list(result2)

unique_df = top50[~top50['STATION'].isin(result_list2)]

#%%

unique_df_sum = unique_df.groupby(['STATION'])['IMPRESSIONS'].median()
unique_df_sum2 = unique_df_sum.reset_index()
unique_list_name = list(unique_df_sum2['STATION'])
n_groups = 26

index = np.arange(n_groups)
plt.bar(index, list(unique_df_sum), color="#b3ccff", alpha = .8, width = .5)

plt.xticks(index,unique_list_name, rotation = 90)
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

plt.xlabel('Unique Stations')
plt.ylabel('Impressions for Unique Stations')

plt.title("Impressions Per Station for Unique Stations") # whats the ttile 
plt.show()

sns.boxplot(list(unique_df_sum))
plt.title("Boxplot For Unique Stations")
plt.xlabel("Impressions")
sns.boxplot(list(common_df_sum))
plt.title("Boxplot For Common Stations")
plt.xlabel("Impressions")