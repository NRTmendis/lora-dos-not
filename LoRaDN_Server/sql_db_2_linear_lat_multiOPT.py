""" Created by Nissanka Mendis on 23/07/2018"""
#Linear Regression alternative system

import os
import sqlite3
import csv
import json
import time
import numpy as np
import math
from copy import deepcopy
import scipy.optimize as optimize
from scipy import stats
import sys
sys.path.insert(1, '..')
from utils import get_current_world, get_gateways

# SETTINGS CONSTANTS
CURRENT_WORLD = get_current_world()

# SQlite DB name
Lora_GTW_DB = "lora_GTW.db"

# GTW training CSV Out name
Lora_GTW_PP = "lora_GTW_PP.csv"

# PKT query CSV Out name
Lora_NODE_PP = "Lora_NODE_PP.csv"

# Room 710
Gw_Loc_db = get_gateways(CURRENT_WORLD, lists=True)

def Gateway_Check(jsonData):
    try:
        json_Dict = json.loads(jsonData)
        gw_id = str(json_Dict['gtiD'])
        for x in range(0, len(Gw_Loc_db)):
            if Gw_Loc_db[x][0] == gw_id:
                return (gw_id)
        return ("Not Found")  # Not a gateway id
    except:
        return ("Not Found")  # Not a gateway packet

def new_cell_for_ML(db_ids):
	# Re-connect to server
	conn = sqlite3.connect(Lora_GTW_DB)
	curs = conn.cursor()

	# Set all Gateway RSSI to -150dB, noise floor level
	Gw_RSSI = [-150]
	for x in range(1, len(Gw_Loc_db)):
		Gw_RSSI.append(-150)
	# Get the PKTs Longitude and Lattitude
	curs.execute(
		'SELECT pkt_longitude FROM Lora_Gateway_PKT_Data WHERE id =' + str(db_ids[0]))
	pkt_long = curs.fetchone()[0]
	if (pkt_long is None) or (pkt_long == ""):
		pkt_long = 0

	curs.execute(
		'SELECT pkt_latitude FROM Lora_Gateway_PKT_Data WHERE id =' + str(db_ids[0]))
	pkt_lat = curs.fetchone()[0]
	if (pkt_lat is None) or (pkt_lat == ""):
		pkt_lat = 0

	for x in db_ids:
		curs.execute(
			'SELECT gateway_id FROM Lora_Gateway_PKT_Data WHERE id =' + str(x))
		pkt_gtiD = curs.fetchone()[0]
		curs.execute(
			'SELECT pkt_data FROM Lora_Gateway_PKT_Data WHERE id =' + str(x))
		pkt_data = curs.fetchone()[0]
		gw_check_id = Gateway_Check(pkt_data)
		curs.execute(
			'SELECT pkt_rssi FROM Lora_Gateway_PKT_Data WHERE id =' + str(x))
		pkt_rssi = int(curs.fetchone()[0])
		# Set RSSI values from gateways
		for y in range(0, len(Gw_Loc_db)):
			if Gw_Loc_db[y][0] == pkt_gtiD:
				Gw_RSSI[y] = pkt_rssi
				if gw_check_id == "Not Found":
					Gw_RSSI[y] = pkt_rssi +58 # +58 For non-antenna connections
			if gw_check_id != "Not Found":
				if Gw_Loc_db[y][0] == gw_check_id:
					# The packet was from a gateway so max dB set heuristically
					Gw_RSSI[y] = -28


	new_cell_row = Gw_RSSI
	new_cell_row.insert(0, (db_ids[0]))  # Add iD to front
	#new_cell_row.append(mean_RSSI)
	new_cell_row.append(pkt_long)
	new_cell_row.append(pkt_lat)
	conn.close()
	return (new_cell_row)

def update_CSVs_from_DB(row_num):
	conn = sqlite3.connect(Lora_GTW_DB)
	curs = conn.cursor()
	curs.execute('SELECT max(id) FROM Lora_Gateway_PKT_Data')
	max_id = int(curs.fetchone()[0]) + 1
	conn.close()
	row = row_num
	DATA_to_GTW_CSV = []
	DATA_to_NODE_CSV = []
	node_matrix_ids = []
	gw_matrix_ids = []

	while row <= max_id:
		conn = sqlite3.connect(Lora_GTW_DB)
		curs = conn.cursor()
		curs.execute('INSERT INTO Lora_Gateway_PKT_Data DEFAULT VALUES')
		curs.execute(
			'SELECT pkt_data FROM Lora_Gateway_PKT_Data WHERE id =' + str(row))
		pkt_data_one = curs.fetchone()[0]
		curs.execute(
			'SELECT pkt_longitude FROM Lora_Gateway_PKT_Data WHERE id =' + str(row))
		pkt_long = curs.fetchone()[0]
		pkt_matrix_ids = None
		pkt_matrix_ids = [row]
		row_max = row + 12
		while row_max > max_id:
			row_max = row_max - 1
		for x in range(row + 1, row_max):
			curs.execute(
				'SELECT pkt_data FROM Lora_Gateway_PKT_Data WHERE id =' + str(x))
			pkt_data_query = curs.fetchone()[0]
			if pkt_data_query == pkt_data_one:
				pkt_matrix_ids.append(x)
		curs.execute(
			'DELETE FROM Lora_Gateway_PKT_Data WHERE id =' + str(max_id))
		conn.close()
		row = row + 1
		if pkt_matrix_ids is not None:
			if len(pkt_matrix_ids) >= 3:
				gw_check_id = Gateway_Check(pkt_data_one)
				if gw_check_id != "Not Found":
					DATA_to_GTW_CSV.append(new_cell_for_ML(pkt_matrix_ids))
					gw_matrix_ids.append(pkt_matrix_ids)
				else:
					if (pkt_long is None) or (pkt_long == ""):
						DATA_to_NODE_CSV.append(
							new_cell_for_ML(pkt_matrix_ids))
						node_matrix_ids.append(pkt_matrix_ids)
	cc_nd = len(node_matrix_ids) - 1
	cc_nd_tab = []
	while (cc_nd >= 1):
		try:
			if set(node_matrix_ids[cc_nd-1]).issuperset(set(node_matrix_ids[cc_nd])):
				cc_nd_tab.append(cc_nd)
		except:
			pass
		cc_nd = cc_nd-1
	for x in cc_nd_tab:
		del node_matrix_ids[x]
		del DATA_to_NODE_CSV[x]
	cc_gw = len(gw_matrix_ids) - 1
	cc_gw_tab = []
	while (cc_gw >= 1):
		try:
			if set(gw_matrix_ids[cc_gw-1]).issuperset(set(gw_matrix_ids[cc_gw])):
				cc_gw_tab.append(cc_gw)
		except:
			pass
		cc_gw = cc_gw-1
	for x in cc_gw_tab:
		del gw_matrix_ids[x]
		del DATA_to_GTW_CSV[x]
	conn = sqlite3.connect(Lora_GTW_DB)
	curs = conn.cursor()
	conn.close()
	
	return (DATA_to_GTW_CSV, DATA_to_NODE_CSV, node_matrix_ids, (max_id - 1))

def linregress(x, y):
    """ Return R^2 where x and y are array-like."""

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return slope, intercept,r_value**2	

	
def Max_rs2(y_int_RSSI, x_array, y_array):
	x_arrayZ = deepcopy(x_array)
	y_arrayZ = deepcopy(y_array)
	
	for count  in range(0, int(len(x_array)/len(Gw_Loc_db))):
		x_arrayZ.append(0)
		y_arrayZ.append(y_int_RSSI)
	gradient, y_intercept, rs2 = linregress(x_arrayZ,y_arrayZ)
	Max_rs2_err = 1 - rs2
	return (Max_rs2_err)
	
def calc_lin_rel(testValX):
#Calculate y = mx + c for all gateways where y is RSSI and x is log(distance)
	testVal = testValX
	Gw_Loc_temp = Gw_Loc_db
	for row in testVal:
		del row[0]  
	gateway_lin = []
	for x2 in range (0, len(Gw_Loc_temp)):
		x_val_arr = []
		y_val_arr = []
		for x in range(0, len(testVal)):
			y_val = testVal[x][x2]
			x_val = math.sqrt( math.fabs(float(testVal[x][-2]) - float(Gw_Loc_temp[x2][2])) + math.fabs(float(testVal[x][-1]) - float(Gw_Loc_temp[x2][1])))
			if x_val == 0:
				pass
			else:
				if y_val == -150:
					pass
				else:
					x_val_arr.append(math.log10(x_val)) #Log scale for linear relationship between RSSI and distance
					y_val_arr.append(y_val)
		
		init_RSSI = -28
		
		best_fit_lin = optimize.minimize(
		Max_rs2,                         # The error function
		init_RSSI,            # The initial guess
		args=(x_val_arr, y_val_arr), # Additional parameters for mse
		method='L-BFGS-B',           # The optimisation algorithm
		bounds=((-40,-25),),
		options={
			'ftol':1e-9,         # Tolerance
			'maxiter': 1e+9      # Maximum iterations
		})

		
		y_int_best = float(best_fit_lin.x)
		
		
		for count  in range(0, int(len(x_val_arr)/len(Gw_Loc_db))):
			x_val_arr.append(0)
			y_val_arr.append(y_int_best)
		
		gradient, y_intercept, rs2 = linregress(x_val_arr,y_val_arr)
		fit_lin = [gradient, y_intercept]
		print("LinG function with OPTIMIZE:"+str(x2)+": Slope: "+str(gradient)+" Intercept: "+ str(y_intercept)+" R_squared: "+ str(rs2))
		
		"""
		print("X Val Array "+str(x2)+" : ")
		for rob in x_val_arr:
			print(rob)
		print("Y Val Array "+str(x2)+" : ")
		for rob in y_val_arr:
			print(rob)
		"""
		
		
		gateway_lin.append(fit_lin)
	return(gateway_lin) #Output [m,c]

def calc_radial_dist(gateway_lin, query_rssi):
	out_dist = []
	for d_val in range(0, len(query_rssi)):
		l_one_dist = []
		for val in range(0, len(gateway_lin)):
			dist = math.pow(10,((query_rssi[d_val][val] - gateway_lin[val][1])/gateway_lin[val][0]))
			l_one_dist.append(dist)
		out_dist.append(l_one_dist)
	return (out_dist)

def calc_single_err_dist(old_position, new_position):
	out_dist = math.sqrt( math.fabs(float(old_position[0]) - float(new_position[0])) + math.fabs(float(old_position[1]) - float(new_position[1])))
	return out_dist
	
def extract_gw_pos(Gw_Loc_db):
	pure_pos = Gw_Loc_db
	for row in pure_pos:
		del row[0] 
		
	return pure_pos
	
def init_loc(pure_pos, test_dist_one):
	#Returns closest Gateway for initial guess
	pure_posX = deepcopy(pure_pos)
	test_dist_oneX = deepcopy(test_dist_one)
	min_index = np.argmin(test_dist_oneX)
	return(pure_posX[min_index])

def mse(x, locations, distances):
	mse = 0.0
	count = 0
	for location, distance in zip(locations, distances):
		distance_calculated = calc_single_err_dist(x, location)
		mse += math.pow(distance_calculated - distance, 2.0)
		count = count + 1
	return (mse / count)
	
def filt_not_rec(pure_posX, test_dist_oneX):
	#Remove gateways that did not receive the packet from calculation
	pure_pos = deepcopy(pure_posX)
	test_dist_one = deepcopy(test_dist_oneX)
	to_del = []
	for val in range(0, len(test_dist_one)):
		if test_dist_one[val] >= 20:
			to_del.append(val)
		if test_dist_one[val] <= 0.1:
			to_del.append(val)
	

	to_del = list(reversed(to_del))
	for valx in to_del:
		del pure_pos[valx]
		del test_dist_one[valx]
	
	return (pure_pos, test_dist_one)

def setup_loc(loc_points):
	loc_pointsX = []
	loc_pointsX = deepcopy(loc_points)
	rel_points = calc_lin_rel(loc_pointsX)
	Gw_loc_db_temp = get_gateways(CURRENT_WORLD, lists=True)
	pure_gw_pos = extract_gw_pos(Gw_loc_db_temp)
	return(rel_points, pure_gw_pos)
	
def predict_loc(pure_gw_posX, rel_pointsX, test_query_arrX):
	#Linear optimization solution to multilateration
	pure_gw_pos = deepcopy(pure_gw_posX)
	rel_points = deepcopy(rel_pointsX)
	test_query_arr = deepcopy(test_query_arrX)
	
	for row in test_query_arr:
		del row[0]  # Remove ID from array.
		del row[-1] #get rid of default x
		del row[-1] #get rid of default y

	test_dist = calc_radial_dist(rel_points,test_query_arr)
	
	
	location_answers = []
	for x in range(0, len(test_dist)):
		filt_gw_pos, filt_test_dist = filt_not_rec(pure_gw_pos, test_dist[x])
		init_guess = init_loc(filt_gw_pos, filt_test_dist)

		result = optimize.minimize(
		mse,                         # The error function
		init_guess,            # The initial guess
		args=(filt_gw_pos, filt_test_dist), # Additional parameters for mse
		method='L-BFGS-B',           # The optimisation algorithm
		options={
			'ftol':1e-9,         # Tolerance
			'maxiter': 1e+9      # Maximum iterations
		})
		
		location = result.x
		location_answers.append(location)
	
	return (location_answers)

def update_SQL_DB_loc(node_loc_ARR, node_ID_ARR):
    conn = sqlite3.connect(Lora_GTW_DB)
    curs = conn.cursor()
    for x in range(0, len(node_ID_ARR)):
        for id_Z in node_ID_ARR[x]:
            curs.execute(
                '''UPDATE Lora_Gateway_PKT_Data SET pkt_longitude = ? WHERE id = ?''', (node_loc_ARR[x][0], id_Z))
            curs.execute(
                '''UPDATE Lora_Gateway_PKT_Data SET pkt_latitude = ? WHERE id = ?''', (node_loc_ARR[x][1], id_Z))
    conn.commit()
    conn.close()
	
#***************Main Code Here*********************************************************************************************


row_num = 1
node_loc_points, node_loc_queries, node_matrix_id, row_num = update_CSVs_from_DB(row_num)
node_loc_points_temp = deepcopy(node_loc_points)

#node_loc_points_temp = [[1, -47,-37,-49,-43,-52,-63,  2.38 ,   1.48], [2, -48,-35,-46,-46,-40,-57,  6.28 ,   1.48], [4, -55,-54,-46,-51,-37,-61, 14.98 ,   1.48], [5, -52,-43,-41,-47,-39,-53, 11.08 ,   1.48], [6, -44,-51,-46,-42,-36,-52,  9.78  ,  1.48], [7, -43,-47,-42,-38,-53,-47,  2.38  ,  6.68], [8, -43,-44,-48,-45,-45,-49, 14.98  ,  6.68], [9, -36,-43,-37,-38,-51,-45,  9.78  ,  6.68], [10, -38,-46,-42,-39,-52,-45, 11.29   , 9.84], [11, -48,-49,-42,-40,-46,-52,  3.75 ,   9.84], [14, -40,-43,-43,-31,-53,-47,  1.15 ,   9.84], [15, -35,-52,-42,-35,-49,-44,  7.65  ,  9.84], [16, -39,-52,-43,-46,-52,-38,  3.59,   19.88], [17, -29,-48,-47,-47,-59,-46, 11.49 ,  19.88], [18, -38,-49,-46,-41,-53,-47,  7.65  , 12.44], [19, -31,-62,-41,-49,-51,-34,  7.65,   15.04], [20, -44,-56,-49,-44,-54,-39,  7.65 ,  17.64], [21, -40,-49,-42,-54,-55,-38,  3.59  , 14.68], [23, -38,-53,-46,-46,-62,-38, 11.49 ,  14.68]]

start_loc, start_gw = setup_loc(node_loc_points_temp) #Setup linear system
while True:
	if len(node_loc_queries) > 0:
		for rob in node_loc_queries:
			print(rob)
		node_loc_points_temp = deepcopy(node_loc_points)
		#if len(node_loc_points_temp) >= 25 :
		#	start_loc, start_gw = setup_loc(node_loc_points_temp) #Setup linear system
		start_gw_loc = deepcopy(start_gw)
		node_loc_answer = predict_loc(start_gw_loc, start_loc,node_loc_queries)
		for rob in node_loc_answer:
			print(rob)
	#update_SQL_DB_loc(node_loc_answer, node_matrix_id)
	time.sleep(1)
	node_loc_points, node_loc_queries, node_matrix_id, row_num = update_CSVs_from_DB(row_num)

