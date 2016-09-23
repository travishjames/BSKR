# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 17:20:23 2016

@author: Sarick
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import csv
import datetime
from dateutil import parser
import dateutil
os.chdir("C:\\Users\\Sarick\\Documents\\Python Scripts")
week_raw_160910 = pd.read_csv('turnstile_160910.csv')
week_raw_160917 = pd.read_csv('turnstile_160917.csv')
week_raw_160903 = pd.read_csv('turnstile_160903.csv')

week_raw_160910.columns = ['C/A', 'UNIT', 'SCP', 'STATION', 'LINENAME', 'DIVISION', 'DATE', 'TIME', 'DESC', 'ENTRIES', 'EXITS']
new_df=week_raw_160910.drop(['LINENAME', 'DIVISION', 'DESC', 'EXITS'], axis = 1)
#http://stackoverflow.com/questions/19377969/combine-two-columns-of-text-in-dataframe-in-pandas-python
new_df['DATETIME'] = new_df.DATE.astype(str).str.cat(new_df.TIME.astype(str), sep=' ')
#from dateutil, makes datetime object
dt_converter = lambda x: parser.parse(x)
new_df['DATETIME'] = new_df['DATETIME'].map(dt_converter)

new_df_date = week_raw_160910.drop(['LINENAME', 'DIVISION', 'DESC', 'EXITS', 'TIME'], axis = 1)
new_df_date['DATE'] = new_df_date['DATE'].map(dt_converter)

new_df_entries = new_df_date['ENTRIES'].sub(new_df_date['ENTRIES'].shift(), fill_value = 0)
new_df_date = new_df_date.drop('ENTRIES', axis = 1)
new_df_date = pd.concat([new_df_date, new_df_entries], axis = 1, join_axes = [new_df_date.index])

new_df2 = new_df_date.groupby('DATE')['ENTRIES'].sum()

