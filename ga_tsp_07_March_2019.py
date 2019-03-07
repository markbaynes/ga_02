# -*- coding: UTF-8 -*-
from collections.__init__ import defaultdict
import numpy as np
import random
import sys
import operator
import copy
import math
import collections
from collections import defaultdict

from decimal import Decimal
from random import shuffle
from operator import itemgetter
import itertools
import pandas as pd
import pprint
import plotly.plotly as py
import plotly.tools as tls
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
style.use ("fivethirtyeight")

landscape="global"

def init_landscape(num_cities):
	"""Generate list of random x,y co-ordinates in 2D space.
	Only need to represent this seed route - not all possible x,y in the space."""
	global landscape
	np.random.seed (123)
	landscape = np.random.randint (1, 100, (num_cities, 2))
	# print(f"Landscape {landscape}")
	return landscape

def init_population(population, num_cities):
	""""""
	random.seed(123)
	pop_counter = 0
	new_pop = []
	while pop_counter <= population:
		new_route= np.random.permutation(num_cities)
		new_pop.append(new_route)
		pop_counter+=1
	# print(new_pop)
	return new_pop

def list_to_dict(incoming_list):
	"""Helper function converts route list to dict and renumbers city ready for further processing."""
	# This only deals with list of lists so chops up single lists.
	route_counter = 0
	converted_dict = []
	for item in incoming_list:
		ga_dict = {}
		ga_dict = {"id": 0, "cities": [], "distance": 0}
		ga_dict["id"] = route_counter
		ga_dict["cities"] = item
		converted_dict.append(ga_dict)
		route_counter+=1
	# print(f"{converted_dict}")
	return converted_dict

def measure_route(population, num_cities=10):
	"""Calculate total distance for each chromosome dictionary and return updated population."""
	for each_chromosome in population:
		each_chromosome["distance"] = calculate_distance (each_chromosome, num_cities)
	return population

def calculate_distance(ga_dict, num_cities=10):
	"""Given route dictionary and the number of cities as arguments in a route return total Euclidean distance for entire route
	including back to base to two decimal places."""
	total_distance = 0
	counter = 0
	while counter < num_cities-1:
		city_1 = ga_dict["cities"][counter]
		city_2 = ga_dict["cities"][counter+1]
		step_distance = get_distance(city_1, city_2)
		total_distance = total_distance + step_distance
		counter += 1
	back_to_start = get_distance (ga_dict["cities"][0], ga_dict["cities"][num_cities - 1])
	total_distance = total_distance + back_to_start
	return round(total_distance,2)

def get_distance(city_1, city_2):
	"""Given two city labels as argument and the global landscape, look up x,y coordinates and return
	Euclidean distance between them to two decimal places."""
	global landscape
	this_distance = math.hypot(landscape[city_1][0] - landscape[city_1][1], landscape[city_2][0] - landscape[city_2][1])
	# print(f"{city_1, city_2, round(this_distance,2)}")
	return int(this_distance)

def sort_distances(pop_returned):
	"""Rank population by route distance - shorter distance is better."""
	pop_returned.sort(key=lambda e: e['distance'])
	return pop_returned

def run_stats(population):
	"""Takes population with measured routes as input, returns min and max route lengths."""
	min_value = 0
	max_value = 0
	distance_data = []
	for route in population:
		if isinstance (route, dict):
			run_data = {}
			run_data = {"id": 0, "distance": 0, "norm":0}
			for key, value in route.items ():
				if key == "id":
					run_data["id"]=value
				elif key == "distance":
					run_data["distance"]=value
			distance_data.append(run_data)
	sorted_distances=sort_distances(distance_data)
	# print(sorted_distances)
	min_value=sorted_distances[0]["distance"]
	max_value=sorted_distances[-1]["distance"]
	run_stats=min_value, max_value, sorted_distances
	print(f"Min {min_value} Max {max_value}")
	return run_stats

def normalise_distances(min_value, max_value,sorted_distances):
	"""Normalise distances, takes min, max of sorted_distances, returns normalised value for each distance."""
	for each_distance in sorted_distances:
		normalised = (each_distance["distance"]-min_value)/(max_value-min_value)
		each_distance["norm"]=normalised
	# print(sorted_distances)
	return sorted_distances

def select_elite(sorted_distances, elite_prop):
	elite_num = int((len(sorted_distances)*elite_prop)/100)
	elite=sorted_distances[0:elite_num]
	elite_ids=[]
	print(f"Elite {elite_num}")
	for champion in elite:
		elite_ids.append(champion["id"])
	print(elite_ids)
	return elite_ids

def main_genetic(elite_ids, fit_pop):
	"""Main function."""
	elite_list = []
	# print (fit_pop)
	# Get the elite dictionaries
	id_count = 0
	elite_pointer=0
	while elite_pointer < len(elite_ids):
		for each_dict in fit_pop:
			for key, value in each_dict.items ():
				if key == "id" and value == elite_ids[elite_pointer]:
					elite_list.append(each_dict)
				else:
					pass
		elite_pointer+=1
	print(elite_list)





def run_genetic(runs, population, num_cities, elite_prop):
	"""Calls main functions."""
	# INITIAL SETUP
	global landscape
	landscape=init_landscape(num_cities)
	initial_pop=init_population(population,num_cities)
	new_pop = list_to_dict (initial_pop)
	fit_pop=measure_route(new_pop, num_cities)
	min_value, max_value, sorted_distances=run_stats(fit_pop)
	sorted_distances=normalise_distances(min_value, max_value, sorted_distances)
	elite_ids=select_elite (sorted_distances, elite_prop)
	main_genetic(elite_ids, fit_pop)
	# MAIN LOOP
	# extract_fittest(ranked_pop, elite_prop)

run_genetic(runs=50, population=50, num_cities=10, elite_prop=20)

# def extract_fittest(distance_data, elite_prop):
# 	"""Get the N fittest chromosomes (those with shortest route) as a percentage of the ranked population."""
# 	elite_num = int((len(distance_data)*elite_prop)/100)
# 	elite=distance_data[1:elite_num]
# 	# print(distance_data)
# 	# print(elite)
# 	return elite



