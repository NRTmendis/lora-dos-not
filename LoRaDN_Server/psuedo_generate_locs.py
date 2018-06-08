# Author Nissanka Mendis
# Pseudo generate locations for ML
# Nissanka Mendis 2018 June.

import random

def filtAvgLocs(RSSI_tab):
	
	del_list = []
	for row in range(0,len(RSSI_tab)):
		RSSI_tab[row][0] = 1
		for col in range(1,len(RSSI_tab[row])-2): #Just RSSI values, skip locat
			if RSSI_tab[row][col] == "-150" :
				del_list.append(row)
				
	if len(del_list) >= 1 :
		for row in range(len(del_list),-1,-1):
			del RSSI_tab[del_list[row]]
	
	loc_tab = []
	for row_A in range(0,len(RSSI_tab)):
		val_found = False
		if len(loc_tab) >= 1 :
			for row_B in range(0, len(loc_tab)):
				if RSSI_tab[row_A][len(RSSI_tab[row_A])-2] == loc_tab[row_B][len(loc_tab[row_B])-2] :
					if RSSI_tab[row_A][len(RSSI_tab[row_A])-1] == loc_tab[row_B][len(loc_tab[row_B])-1] :
						for col in range(0, len(loc_tab[row_B])-2):
							loc_tab[row_B][col] = loc_tab[row_B][col] + RSSI_tab[row_A][col]
							val_found = True
		if val_found == False:
			loc_tab.append(RSSI_tab[row_A])
	
	for row in range(0,len(loc_tab)):
		for col in range(1, len(loc_tab[row_B])-2):
			loc_tab[row][col] = loc_tab[row][col] / loc_tab[row][0]
			loc_tab[row][col] = round(loc_tab[row][col])
	
	for row in range(0,len(loc_tab)):
		loc_tab[row][0] = row + 1
	
	return (loc_tab)
	
def genNewLocs(loc_tab, offset):
	
	new_locs_tab = []
	for row_A in range(0, len(loc_tab)):
		for row_B in range(row_A + 1, len(loc_tab)):
			new_row = []
			for col in range(0,len(loc_tab[row_B])):
				new_row_val=(float(loc_tab[row_A][col]) + float(loc_tab[row_B][col]))/2
				new_row.append(round(new_row_val,2)) #Keep to 1cm accuracy
			for col in range(1, len(new_row)-2):
				new_row[col] = round(new_row[col]) #Keep RSSI as integers
			new_locs_tab.append(new_row)
			
	#Filter out positions that are overlapping together
	fil_loc_tab = []
	del_list = []
	for row_A in range(0,len(new_locs_tab)):
		val_found = False
		if len(fil_loc_tab) >= 1 :
			for row_B in range(0, len(fil_loc_tab)):
				#offset = 0.2 #Points within 20cm of each other get filtered out.
				if \
				(new_locs_tab[row_A][len(new_locs_tab[row_A])-2] >= fil_loc_tab[row_B][len(fil_loc_tab[row_B])-2] - offset) \
				and \
				(new_locs_tab[row_A][len(new_locs_tab[row_A])-2] <= fil_loc_tab[row_B][len(fil_loc_tab[row_B])-2] + offset):
					if \
					(new_locs_tab[row_A][len(new_locs_tab[row_A])-1] >= fil_loc_tab[row_B][len(fil_loc_tab[row_B])-1] - offset ) \
					and \
					(new_locs_tab[row_A][len(new_locs_tab[row_A])-1] <= fil_loc_tab[row_B][len(fil_loc_tab[row_B])-1] + offset):
						if row_A not in del_list:
							del_list.append(row_A)
						val_found = True
						
		if val_found == False:
			fil_loc_tab.append(new_locs_tab[row_A])
			
	if len(del_list) >= 1 :
		rev_del_list = del_list[::-1]
		for row in rev_del_list:
			del new_locs_tab[row]
		
	for row in range(len(loc_tab)-1, -1 , -1):
		new_locs_tab.insert(0, loc_tab[row])
		
	for row in range(0,len(new_locs_tab)):
		new_locs_tab[row][0] = row + 1
		
	return (new_locs_tab)

def psuedoGenPoints(req_points, loc_tab, offset_rssi):
	
	total_locs_tab = []
	
	while ( len(total_locs_tab) < req_points ):
		for row in range(0, len(loc_tab)):
			new_row = []
			#Ramdomise RSSI offset to generate noise
			for col in range(0, len(loc_tab[row])):
				new_row.append("0")
			for col in range(1, len(new_row)-2):
				new_row[col] = loc_tab[row][col] + random.randrange(-offset_rssi, offset_rssi)
			new_row[len(new_row)-2] = loc_tab[row][len(new_row)-2]
			new_row[len(new_row)-1] = loc_tab[row][len(new_row)-1]
			total_locs_tab.append(new_row)

	for row in range(len(loc_tab)-1, -1 , -1):
		total_locs_tab.insert(0, loc_tab[row])
	for row in range(0,len(total_locs_tab)):
		total_locs_tab[row][0] = row + 1
		
	return (total_locs_tab)
