# -*- coding: UTF-8 -*-
from collections.__init__ import defaultdict
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

#  TEST LINE ADDED

def init_population(population, num_cities):
	"""Create initial population."""
	random.seed(123)
	seed_route = list (range (0, num_cities))
	print(f"seed_route {seed_route}")
	pop_counter = 0
	new_pop = []
	while pop_counter <= population:
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
		route_dictionary = {}
		route_dictionary = {"id": 0, "cities": [], "norm":0, "distance": 0}
		route_dictionary["id"] = route_counter
		route_dictionary["cities"] = item
		converted_dict.append(route_dictionary)
		route_counter+=1
	# print(f"{converted_dict}")
	return converted_dict


def measure_route(population, num_cities):
	"""Calculate total distance for each chromosome dictionary and return updated population."""
	# print (f"population IN {population}")
	for each_chromosome in population:
		each_chromosome["distance"] = calculate_distance (each_chromosome, num_cities)
	# print (f"population OUT {population}")
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
	# print(f"Distances {city_1, city_2, abs(this_distance)}")
	return this_distance


def sort_distances(pop_returned):
	"""Rank population by route distance - shorter distance is better."""
	pop_returned.sort(key=lambda e: e['distance'])
	return pop_returned


def analyse_population(population):
	"""Takes population with measured routes as input, returns min, max, norm, route lengths."""
	ranked_population=sort_distances(population)
	min_value=ranked_population[0]["distance"]
	max_value=ranked_population[-1]["distance"]
	run_stats=normalise_distances (min_value, max_value, ranked_population)
	print(f"Min {min_value} Max {max_value}")
	return ranked_population


def normalise_distances(min_value, max_value,ranked_population):
	"""Normalise distances, takes min, max of ranked_population, returns normalised value for each distance."""
	for each_distance in ranked_population:
		normalised = (each_distance["distance"]-min_value)/(max_value-min_value)
		each_distance["norm"]=round(normalised,2)
	return ranked_population


def select_elite(ranked_population, elite_prop):
	elite_num = int((len(ranked_population)*elite_prop)/100)
	elite=ranked_population[0:elite_num]
	print (f"select_elite out {elite}")
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
		elite_pointer+=1
	# for x in elite_list:
	# 	print(f"Elite {x}")
	return elite_list

def divide_parents(list_to_split, parents_size):
	"""From http://bit.ly/2SYwPwY
	Splits list into N parents each of parents_size"""
	for i in range (0, len (list_to_split), parents_size):
		yield list_to_split[i:i + parents_size]

def mutate(chromosome):
	"""Simple mutation function exchanging two cities so as not to create duplicate cities. """
	# print(new_route)
	random_cities = list (range (0, len (chromosome)))
	rand_items = random.sample (random_cities, 2)
	chromosome[rand_items[0]], chromosome[rand_items[1]] = chromosome[rand_items[1]], chromosome[rand_items[0]]
	return chromosome

def single_crossover(elite_list, num_cities, population):
	"""Single point crossover and mutation. This version applies single point crossover to all the elite chromosomes
	by random selection of parents"""
	# TODO Shuffle?
	# Add all members of the elite list to the new pool.
	new_pool = elite_list
	print (f"single cross IN {new_pool}")
	# split_point = random.randint(0,10)
	split_point=round(num_cities/2)
	elite_l = len(elite_list)
	counter = elite_l
	while counter < population:
		route_dictionary = {"id": 0, "cities": [], "norm": 0, "distance": 0}
		parent_1 = random.randint (0, elite_l)
		parent_2 = random.randint (0, elite_l)
		x = elite_list[parent_1]["cities"][0:split_point]
		y = elite_list[parent_2]["cities"][split_point:]
		route_dictionary["cities"] = x + y
		new_pool.append(route_dictionary)
		route_dictionary = {"id": 0, "cities": [], "norm": 0, "distance": 0}
		a = elite_list[parent_2]["cities"][split_point:]
		b = elite_list[parent_1]["cities"][0:split_point]
		route_dictionary["cities"] = a + b
		new_pool.append (route_dictionary)
		counter+=2
		# print(new_pool)
	print (f"single cross OUT {new_pool}")
	return new_pool

	# Mutation with probability of p_mutate
def mutate_pool(population, new_pool, p_mutate):
	""" Mutate new_pool"""
	for chromosome in new_pool:
		while len(new_pool) < population:
			int_random = random.uniform (0, 1)
			if int_random <= p_mutate:
				target_c = chromosome
				mutate (target_c)
				chromosome = target_c
				new_pool.append (chromosome)
			elif int_random > p_mutate:
				pass
	# print (f"{len(new_pool)}")
	# for item in new_pool:
	# 	print (f"{item}")
	return new_pool

#
def run_genetic(runs, population, num_cities, elite_prop, p_mutate):
	"""Calls main functions."""
	# INITIAL SETUP
	global landscape
	landscape=init_landscape(num_cities)
	initial_pop=init_population(population,num_cities)
	new_generation = list_to_dict (initial_pop)
	run_count = 0
	while run_count < runs:
		print (f"\rRun {run_count} ", end="")
		fit_pop = measure_route (new_generation, num_cities)
		ranked_population = analyse_population(fit_pop)
		current_elite = select_elite (ranked_population, elite_prop)
		new_generation = single_crossover (current_elite, num_cities, population)
		# x_pool=mutate_pool(population, new_pool, p_mutate)
		print (f"new_generation {len(new_generation)}")
		yield new_generation
		for item in new_generation:
			print (f"{item}")
		sys.stdout.flush ()
		run_count += 1

# CALL MAIN LOOP
run_genetic(runs=10, population=40, num_cities=8, elite_prop=50, p_mutate=0.30)
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








