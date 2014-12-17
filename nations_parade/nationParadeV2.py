#!/usr/bin/python

# Puzzle #3: I Love A Parade
# Akien MacIain 12/11/2014

# take a list like this:
# Francos comes before Anglos
# Francos comes after Canadio
# Canadio comes after Barbadonia
# Ethiopaea comes before Shrill Lanka
#
# and produce a result like this:
# Ethiopaea
# Barbadonia
# Canadio
# Francos
# Anglos
# Shrill Lanka
#
# and don't allow this:
# Francos comes before Anglos
# Anglos comes before Francos
# should result in: Illegal request file!
#
# Usage: python nationParade.py <inputfile>

import os.path
import sys
import re
import networkx as nx
import time
import unittest


# validate_arguments()
# verifies that we have a file specified in the calling arguments
# Returns the file name as input_file_name
def validate_arguments():
	# do we have correct arguments?
	if len(sys.argv) < 2:
		print "I'm sorry, you don't seem to have provided the input file name."
		print "Please add that to the end of the command line and then try again."
		print "Thanks!"
		sys.exit(1) 

	input_file_name = sys.argv[1]

	print "Specified input file: %s" % input_file_name
	if os.path.isfile(input_file_name):
		print("Input file found.")
	else:
		print "I'm sorry, the input file you specified was NOT FOUND."
		print "Please check to make sure you have the correct file name"
		print "and then try again."
		print "Thanks!"
		sys.exit(2)

	return input_file_name
# end validate_arguments

# read_input_file(input_file_name, country_dict)
# reads the input file into the country_dict
# Returns nothing
# Modifies country_dict
def read_input_file(input_file_name, country_dict):
	try:
		with open(input_file_name, 'r') as fh: 
			for line in fh:
				add_line(country_dict, line.strip())	
	except: 
		print "I'm sorry, an error occurred when trying to open your file."
		print "You may want to verify that it's not open in some other program,"
		print "and that you have the correct permissions to read the file,"
		print "and then try again."
		print "Thanks!"
		e = sys.exc_info()[0]
		print "Error when trying to open the file:\n%s" % e 
		sys.exit(3)
# end read_input_file

# add_line(country_dict, line)
# parses line and country_dict to determine whether the country_dict
# needs to be added to, or one of it's children needs to be added to
# Returns nothing
# Modifies country_dict
def add_line(country_dict, line):
	line = line.strip()
	rresult = regex.split(line)
	
	# do we use the new one, or does one already exist?
	country_a_name = rresult[1]
	if not country_dict.has_key(country_a_name):
		country_dict[country_a_name] = []

	country_b_name = rresult[3]
	if not country_dict.has_key(country_b_name):
		country_dict[country_b_name] = []
	
	edge = rresult[2]
	
	if edge == "before":
		if not country_dict.has_key(country_b_name):
			country_dict[country_a_name].append(country_b_name)
		else:
			country_dict[country_b_name].append(country_a_name)
			
# end add_line


# global variables
regex = re.compile(r"(\w+)\s+comes\s+(before|after)\s+([\w\s]+)")
	
def main():
	timer = dict()
	timer["start"] = time.time()
	
	input_file_name = validate_arguments()
	
	timer["launched"] = time.time()

	country_dict = dict()

	# if we got this far, we have arguments
	# so read the file contents into country_dict
	read_input_file(input_file_name, country_dict)

	timer["read"] = time.time()

	# so now all the before dictss are populated
	# we rebuild the dict as a graph	
	result_graph = nx.DiGraph()
	for key, values in country_dict.iteritems():
		for value in values:
			result_graph.add_edge(key, value)

	timer["graphed"] = time.time()

	# and finally, print it
	for item in result_graph:
		print item
	#end for

	timer["printed"] = time.time()
	print "\n"
	print "time to process (excluding print) = %f" % (timer["graphed"] - timer["start"])
	print "time to print = %f" % (timer["printed"] - timer["graphed"])
	print "Done!"
# end main

main()
