""" Created by Nissanka Mendis on 18/03/2018"""
#Only works with Python 2.7. As localization library only runs on that.

import sys
import numpy as np
import localization as lx
from pandas import read_csv

Gw_Loc_db = [
		["240AC4F01E023C54",6.738,12.291], #id, lat, long
		["240AC4F01E0286DC",7.34,0.555], 
		["240AC4F01E025FF4",0.363,11.976],
		["240AC4F01E023E3C",0.733,0.531]
	    ]

def loc_single_predict(test_Val, QUERY_CSV_BATCH='none_dun.csv'):
	if QUERY_CSV_BATCH != 'none.csv':
		# run batch in CSVinstead of value
		dataset_Q = read_csv(QUERY_CSV_BATCH, header=0, index_col=0)
		values_Q = dataset_Q.values
		test_Vals = values_Q.astype('float32')
	else:
		# combine test value and dataset used to train model
		for row in test_Val:
			del row[0]  # Remove ID from array.
		test_Val = array(test_Val)
		test_Vals = test_Val.astype('float32')
	
	P=lx.Project(mode='2D',solver='LSE_GC')
	for x in range(0, len(Gw_Loc_db)):
		P.add_anchor(str(Gw_Loc_db[x][0]),(str(Gw_Loc_db[x][1]), str(Gw_Loc_db[x][2])))
	
	targ = []
	label = []
	for x in range(0, len(test_Vals)):
		t,l = P.add_target()
		targ.append(t)
		label.append(l)
		
	for y in range(0, len(test_Vals)):
		for x in range(0, len(Gw_Loc_db)):
			m_pow = (20 + test_Vals[y][x])/(-37)
			m_dist =  np.power(10, m_pow)
			targ[y].add_measure(str(Gw_Loc_db[x][0]), m_dist)
	
	P.solve()
	
	for y in range(0, len(test_Vals)):
		print(targ[y].loc)

loc_single_predict(1)
	