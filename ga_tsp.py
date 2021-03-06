# -*- coding: UTF-8 -*-
from collections.__init__ import defaultdict
import random
import sys
import operator
import copy
import math
import time
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
# from matplotlib import style
# style.use ("fivethirtyeight")

landscape="global"


def init_landscape(num_cities):
	"""Generate list of random x,y co-ordinates in 2D space.
	Only need to represent this seed route - not all possible x,y in the space."""
	global landscape
	# landscape = [(0, 0), (94, 21), (200, 5), (21, 65), (157, 134), (10, 12), (74, 14), (12,190), (6, 2), (100, 100), (12, 24)]
	random.seed (982)
	landscape = []
	co_count = 0
	while co_count <= num_cities:
		x = random.randint (0, 50)
		y = random.randint (0, 50)
		pair = (x,y)
		landscape.append(pair)
		co_count+=1
	print(f"Landscape {landscape}")
	return landscape


def init_population(population, num_cities):
	"""Create initial population."""
	random.seed(123)
	seed_route = list (range (0, num_cities))
	print(f"seed_route {seed_route}")
	pop_counter = 0
	new_pop = []
	while pop_counter < population:
		new_seed = copy.deepcopy(seed_route)
		# print(f"new_seed {new_seed}")
		shuffle(new_seed)
		# print(f"shuffled {new_seed}")
		new_pop.append(new_seed)
		pop_counter+=1
	# print(f"new_pop {new_pop}")
	return new_pop


def list_to_dict(incoming_list):
	"""Helper function converts route list to dict and renumbers city ready for further processing."""
	# This only deals with list of lists so chops up single lists.
	route_counter = 0
	converted_dict = []
	for item in incoming_list:
		route_dictionary = {"id": 0, "cities": [], "norm":0, "distance": 0}
		route_dictionary["id"] = route_counter
		route_dictionary["cities"] = item
		converted_dict.append(route_dictionary)
		route_counter+=1
	return converted_dict


def measure_route(population, num_cities):
	"""Calculate total distance for each chromosome dictionary and return updated population."""
	route_counter = len(population) + 1
	for each_chromosome in population:
		each_chromosome["id"] = route_counter
		each_chromosome["distance"] = calculate_distance (each_chromosome, num_cities)
		route_counter+=1
	return population


def calculate_distance(route_dictionary, num_cities):
	"""Given route dictionary and the number of cities as arguments in a route return total Euclidean distance for entire route
	including back to base to two decimal places."""
	total_distance = 0
	counter = 0
	while counter < num_cities-1:
		city_1 = route_dictionary["cities"][counter]
		city_2 = route_dictionary["cities"][counter+1]
		step_distance = get_distance(city_1, city_2)
		total_distance = total_distance + step_distance
		counter += 1
	back_to_start = get_distance (route_dictionary["cities"][0], route_dictionary["cities"][num_cities - 1])
	total_distance = total_distance + back_to_start
	route_dictionary["distance"] = round(total_distance,2)
	return total_distance


def get_distance(city_1, city_2):
	"""Given two city labels as argument and the global landscape, look up x,y coordinates and return
	Euclidean distance between them to two decimal places."""
	global landscape
	this_distance = math.hypot((landscape[city_1][0] - landscape[city_1][1]), (landscape[city_2][0] - landscape[city_2][1]))
	return this_distance


def sort_distances(pop_returned):
	"""Rank population by route distance - shorter distance is better."""
	pop_returned.sort(key=lambda e: e['distance'])
	return pop_returned


def analyse_population(measured_pop):
	"""Takes population with measured routes as input, returns min, max, norm, route lengths."""
	print (f"population IN analyse {measured_pop}")
	ranked_population=sort_distances(measured_pop)
	min_value=ranked_population[0]["distance"]
	max_value=ranked_population[-1]["distance"]
	# print(f"1 Min {min_value} Max {max_value}")
	ranked_stats = min_value, max_value, ranked_population
	return ranked_stats

def normalise(ranked_stats):
	min_value, max_value, ranked_population = ranked_stats
	normalised = normalise_distances (min_value,max_value,ranked_population)
	# print(f"2 Min {min_value} Max {max_value} Ranked {ranked_population}")
	# print(f"RUN STATS {run_stats}")
	return normalised

def normalise_distances(min_value, max_value,ranked_population):
	"""Normalise distances, takes min, max of ranked_population, returns normalised value for each distance."""
	# print(f"Ranked pop IN {len(ranked_population)} {ranked_population}")
	for each_route in ranked_population:
		# print (f"{each_route['distance']} {min_value} {max_value}")
		each_route["norm"] = (each_route["distance"]-min_value)/(max_value-min_value)
	# print(f"Normalise OUT {len(ranked_population)} {ranked_population}")
	return ranked_population


def select_elite(ranked_population, num_elite):
	# print(f"ranked_population {ranked_population}")
	# elite_num = round(len(ranked_population)*num_elite)/100
	# TODO Change num_elite to elite_num
	elite = ranked_population[0:num_elite]
	# print (f"select_elite out {elite}")
	return elite


def utility_function(elite_ids, fit_pop):
	"""Main function."""
	elite_list = []
	elite_pointer=0
	while elite_pointer < len(elite_ids):
		for each_dict in fit_pop:
			for key, value in each_dict.items ():
				if key == "id" and value == elite_ids[elite_pointer]:
					elite_list.append(each_dict["cities"])
				else:
					pass
		elite_pointer += 1
	return elite_list


""" The important thing to remember with 'crossover' is that there is no
one right way of doing it."""

def mutate(chromosome):
	"""Simple mutation function exchanging two cities so as not to create duplicate cities. """
	# print("Mutating")
	random_cities = list (range (0, len (chromosome["cities"])))
	x,y = random.sample (random_cities, 2)
	chromosome["cities"][x], chromosome["cities"][y] = chromosome["cities"][y], chromosome["cities"][x]
	return chromosome

	# Mutation with probability of p_mutate
def mutate_pool(new_pool, p_mutate):
	""" Mutate new_pool"""
	for chromosome in new_pool:
		int_random = random.uniform (0, 1)
		if int_random <= p_mutate:
			target_c = chromosome
			mutate (target_c)
			chromosome = target_c
			new_pool.append(chromosome)
		elif int_random > p_mutate:
			pass
	# print (f"mutated {new_pool}")
	return new_pool

def single_crossover(current_elite, num_cities, population, p_mutate):
	"""Single point crossover and mutation."""
	# Add all members of the elite list to the new pool.
	new_pool = current_elite
	# split_point = random.randint(0,num_cities)
	split_point = round(num_cities / 2)
	p_counter = len(current_elite)
	only_routes=[]
	# print(f"New pool{new_pool}")
	for existing_route in current_elite:
		while p_counter <= population:
			p_1, p_2 = random.sample (current_elite, 2)
			parent_1 = p_1["cities"][0:split_point]
			parent_2 = p_2["cities"][split_point:]
			child = parent_1 + parent_2
			for key, value in existing_route.items ():
				if key == "cities":
					# print (f"existing_route {value}")
					# print (f"child {child}")
					if value != child:
						existing_route["cities"]=child
						new_pool.append(existing_route)
					elif value == child:
						pass
			p_counter += 1
	# print (f"new_pool {new_pool}")
	return new_pool





def run_genetic(runs, population, num_cities, num_elite, p_mutate):
	"""Calls main functions."""
	# INITIAL SETUP
	startTime = time.time ()
	global landscape
	landscape=init_landscape(num_cities)
	initial_pop=init_population(population,num_cities)
	new_generation = list_to_dict (initial_pop)
	run_count = 0
	while run_count < runs:
		print(f"\rRun {run_count}\n", end="")
		measured_pop = measure_route (new_generation, num_cities)
		# print (f"\n measured_pop")
		# for _ in measured_pop:
		# 	print (f"{_}")
		rank_stats = analyse_population(measured_pop)
		analysed = (rank_stats)
		current_elite = select_elite(analysed, num_elite)
		# print(f"\n current_elite {len(current_elite)}")
		# for _ in current_elite:
		# 	print(f"{_}")
		new_generation=single_crossover(current_elite, num_cities, population, p_mutate)
		# print(f"\n new_generation {len(new_generation)}")
		# for _ in new_generation:
		# 	print(f"{_}")
		# new_generation=mutate_pool(new_pool, p_mutate)
		# print(f"New generation\n")
		# for _ in new_generation:
		# 	print(f"{_}")
		run_count += 1
		print(run_count)
		# sys.stdout.flush ()
	endTime = time.time ()
	totalTime = endTime - startTime
	print(f"\rElapsed time {round(totalTime,3)}\n", end="")


# CALL MAIN LOOP
run_genetic(runs=20, population=50, num_cities=20, num_elite=6, p_mutate=0.20)
#
# 	print (f"COMPLETE")
	# # Use df and matplotlib to chart results
	# min_distance_data.sort ()
	# labels = ['run', 'min_dist', 'max_dist']
	# df_min_dist = pd.DataFrame.from_records (min_distance_data, columns=labels)
	# min = df_min_dist['min_dist'].min ()
	# max = df_min_dist['max_dist'].max ()
	# mean = df_min_dist.loc[:, "min_dist"].mean ()
	# print (f"Stats Min {min} Max {max} Mean {mean}")
	#
	# ax = plt.gca ()
	# plt.axis ([0, generations, 0, df_min_dist['max_dist'].max ()])
	# df_min_dist.plot (kind='line', x='run', y='min_dist', ax=ax)
	# plt.title ("TSP GA")
	# plt.show ()








