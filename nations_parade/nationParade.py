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

# class Nation stores the information about a given country
# including name, and all those who are "before" it
# It also provides the ability to check for what's before it
# and sorting all the things by least befores first
# Usage: a = Nation(string_name)
class Nation:
	#name = ''
	#before_list = []
	#before_string = ''
	#num_children = 0
	def __init__(self,name):
		self.name = name
		self.before_list = []
		self.before_string = ''
		self.num_children = 0
	# end __init__
	
	# insert_new_before(position, item)
	# inserts item into before list 
	# and updates num_children
	# No return value
	def insert_new_before(self, position, item):
		self.before_list.insert(position, item)
		self.before_string = self.before_string + "-" + item.name + "-"
		self.num_children = len(self.before_list)
	
	# is_before(passed_name)
	# checks the entire tree from this node down looking though 
	# the before list for a node who's name matches passed_name
	# Returns true for found, false for not found
	def is_before(self, passed_nation):
	    
		if passed_nation.name == self.name:
			return True
		if self.before_string.find(passed_nation.name) > -1:
			return True
		# ok, we tried the easy way, now we have to try the hard way
		if len(self.before_list) > 0:
			for item in self.before_list:
				result = item.is_before(passed_nation)
				if result:
					return result
			return False
	# end is_before
	
	# rebuild_before_string()
	# Rebuilds the before_string to have all the children and 
	# their children's children to make searches easy
	# No return value
	def rebuild_before_string(self):
		s = ''
		i = 0
		result = self.fetch_all_children_names(s, i)
		s = result[0]
		i = result[1]
		self.before_string = s
		self.num_children = i
	# end rebuild_before_string
		
	# fetch_all_children_names(s)
	# Helper used by rebuild_before_string
	# Recursively calls all children to fetch ALL
	# the names for all the befores
	# No return value
	def fetch_all_children_names(self, s, i):
		if s.find(self.name) == -1:
			s = s + "-" + self.name + "-"
			i += 1
		if self.num_children > 0:
			for item in self.before_list:
				result = item.fetch_all_children_names(s, i)
				s = result[0]
				i = result[1]
		return [s, i]
	# end fetch_all_children_names

# end Nation

# search_by_name(country_list, name)
# searches the country_list for one who's name matches the passed name
# Returns index into list -OR-
# Returns None if not found
def search_by_name(country_list, name):
	try:
		return [x.name for x in country_list].index(name)
	except:
		return None
# end search_by_name

# add_line(country_list, line)
# parses line and country_list to determine whether the country_list
# needs to be added to, or one of it's children needs to be added to
# No return value
def add_line(country_list, line):
	line = line.strip()
	rresult = regex.split(line)
	
	country_a = Nation(rresult[1])
	country_b = Nation(rresult[3])
	relationship = rresult[2]
	
	# do we use the new one, or does one already exist?
	a_index = search_by_name(country_list, country_a.name)
	if a_index:
		country_a = country_list[a_index]
	else:
		country_list.insert(0, country_a)

	b_index = search_by_name(country_list, country_b.name)
	if b_index:
		country_b = country_list[b_index]
	else:
		country_list.insert(0, country_b)

	# now country_a and country_b point to their respective objects
	# regardless of whether they're new, or retrieved from the list

	# next, we have to turn after into before
	if relationship == "after":
		temp = country_a
		country_a = country_b
		country_b = temp
	
	# check for loop
	if country_b.is_before(country_a):
		print "I'm sorry, this input file contains a loop!"
		print "Nation %s cannot be both before AND after %s" % (country_a.name, country_b.name)
		print "Please correct the problem and then try again."
		print "Thanks!"
		sys.exit(4)
	
	# and add it to the before list
	country_a.insert_new_before(0, country_b)
# end add_line

# global variables
regex = re.compile(r"(\w+)\s+comes\s+(before|after)\s+([\w\s]+)")
	
def main():
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

	# if we got this far, we have arguments
	try:
		input_file = open(input_file_name, 'r')
	except: # catch *all* exceptions
		#e = sys.exc_info()[0]
		#print "Error when trying to open the file:\n%s" % e 
		print "I'm sorry, an error occurred when trying to open your file."
		print "You may want to verify that it's not open in some other program,"
		print "and that you have the correct permissions to read the file,"
		print "and then try again."
		print "Thanks!"
		sys.exit(3)

	# and if we got this far, they're valid arguments
	
	# now we can read in all the data
	country_list = []
	line = input_file.readline()
	while line:
		add_line(country_list, line)
		line = input_file.readline()

	# so now all the before lists are populated
	# we can rebuild the before lists to capture 
	# all the children, and children of children
	for item in country_list:
		item.rebuild_before_string()
	
	# so when we get here, the items at the top of the list don't have 
	# anyone in front of them and the list is sorted so the ones with 
	# the most before them are at the end

	result_list = []
	
	# now we loop through all the countries and start moving them to 
	# the result list. we search the result list to determine positioning
	# and we do the list from the end forward
	
	for index_into_country_list in range(0, len(country_list) -1):

		result_index = -1
		current_country = country_list[index_into_country_list]

		if len(result_list) > 0:
			for index_into_results in range(len(result_list) - 1, 0, -1):
				if current_country.before_string.find(result_list[index_into_results].name) > -1:
					result_index = index_into_results
					break
					
		# at this point, we have an index into the result list or -1
		result_list.insert(result_index, current_country)
	# end for
	
	# and finally, print it
	for item in result_list:
		print item.name
	#end for
	
	print "Done!"
# end main

main()


			
			
			
			
			
			
			
			
			
			
			
			
			
			
			