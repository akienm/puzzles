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

# add_line(country_dict, line)
# parses line and country_dict to determine whether the country_dict
# needs to be added to, or one of it's children needs to be added to
# No return value
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
	
	country_dict = dict()
	country_list = []

	# if we got this far, we have arguments
	timer["launched"] = time.time()
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

	timer["read"] = time.time()

	# so now all the before dictss are populated
	# we rebuild the dict as a list 
	
	for key, value in country_dict.iteritems():
		temp = [key,value]
		country_list.append(temp)

	timer["filtered"] = time.time()

	# now we have a list of nested tuples 
	# use that and the magic of networkx to do the heavy lifting
	result_list = nx.DiGraph()
	for key, vals in country_list:
		for val in vals:
			result_list.add_edge(key, val)
	
	timer["graphed"] = time.time()
	# and finally, print it
	for item in result_list:
		print item
	#end for

	timer["printed"] = time.time()
	print "\n"
	print "time to process (excluding print) = %f" % (timer["graphed"] - timer["start"])
	print "Done!"
# end main

main()


			
			
			
			
			
			
			
			
			
			
			
			
			
			
			