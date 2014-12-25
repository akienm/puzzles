#!/usr/bin/python
# coding=utf-8

# Puzzle #3: I Love A Parade
# Akien MacIain 12/22/2014
# NPV5

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

"""
performs dependency sort on an input file to create output

format for input file:
  Francos comes before Anglos
  Francos comes after Canadio
  Canadio comes after Barbadonia
  Ethiopaea comes before Shrill Lanka
"""
import os.path
import sys
import re
import time
from datetime import datetime

# and because it's supposed to be faster than a list to remove node[0]
from collections import deque


class NodeClass:
    """ Stores one country entry. Captures name, dependencies, and subscribers """
    def __init__(self, name):
        """ Sets up instance variables """
        self.name = name
        self.dependencies = dict()
        self.subscribers = dict()
    
    def add_dependency(self, dependency):
        """ adds a dependency to this instance """
        self.dependencies[dependency.name] = dependency
        dependency.subscribers[self.name] = self
        
    def remove_dependency(self, dependency):
        """ remove dependency from this instance """
        if isinstance(dependency, basestring):
            name = dependency
        else:
            name = dependency.name
        del self.dependencies[name]
    
    def dependency_count(self):
        """ returns number of dependencies for this instance """
        return len(self.dependencies)
# end NodeClass


class NodeList:
    """
    container for nodes.

     implements a dict for quick find by name
     and a list to keep the order, as order is
     important during graph creation.
    """
    def __init__(self):
        """ inits instance vars """
        self.master_dict = dict()
        self.master_index = deque()
    
    def give(self, node_name):
        """ either finds or generates node with name specified """
        if node_name not in self.master_dict:
            new_node = NodeClass(node_name)
            self.append(new_node)
        return self.master_dict[node_name]
            
    def append(self, node):
        """ adds new node to the end of the list """
        self.master_index.append(node.name)
        self.master_dict[node.name] = node
    
    def pop_first(self):
        """ removes and returns first entry """
        name_to_pop = self.master_index.popleft()
        result = self.master_dict[name_to_pop]
        # del self.master_dict[name_to_pop]
        return result

    @staticmethod
    def add_dependency(node, dependency_node):
        """ adds dependency to specified node (made code easier to read) """
        node.add_dependency(dependency_node)

    @staticmethod
    def destroy_dependency(dependency_node):
        """ removes a dependency from all subscribers to that dependency """
        for item in dependency_node.subscribers:
            remove_from_me = dependency_node.subscribers[item]  # to get the item instead of the key
            remove_from_me.remove_dependency(dependency_node)
        del dependency_node
    
    def count(self):
        """ lets us know when we reach zero items """
        return len(self.master_index)
# end NodeList


def validate_arguments():
    """ fetch command line args and populates relevant globals """
    global input_file_name
    global compare_file_name

    # do we have correct arguments?
    if len(sys.argv) < 2:
        print "I'm sorry, you don't seem to have provided the input file name."
        print "Please add that to the end of the command line and then try again."
        print "Thanks!"
        sys.exit(1) 

    input_file_name = sys.argv[1]

    if not os.path.isfile(input_file_name):
        print "I'm sorry, the input file you specified was NOT FOUND."
        print "Please check to make sure you have the correct file name"
        print "and then try again."
        print "Thanks!"
        sys.exit(2)

    if len(sys.argv) > 2:
        compare_file_name = sys.argv[2]
        if not os.path.isfile(compare_file_name):
            compare_file_name = None

# end validate_arguments


def read_input_file():
    """ reads input file into global rules list """
    print input_file_name
    with open(input_file_name, 'r') as fh: 
        for line in fh:
            rules.append(line.strip())    
                
# end read_input_file


def create_tree():
    """ processes the global rules to create dependency tree """
    global nations

    for line in rules:
        line = line.strip()
        regex_result = regex.split(line)
    
        # extract the dependency (before/after)    
        dependency = regex_result[2]
        
        if dependency == "before": 
            country_a_name = regex_result[1]    
            country_b_name = regex_result[3]
        else:
            country_a_name = regex_result[3]    
            country_b_name = regex_result[1]
        
        # do we use an existing country_a or make a new one?
        country_a_node = nations.give(country_a_name)
    
        # do we use an existing country_b or make a new one?
        country_b_node = nations.give(country_b_name)
    
        # add the dependency
        if country_a_node not in country_b_node.dependencies:
            country_b_node.add_dependency(country_a_node)
# end create_tree


def build_graph():
    """
    builds ordered output from dependency tree

     based on Kahn, Arthur B. (1962), "Topological sorting of large networks",
      Communications of the ACM 5 (11): 558–562

     quick summary documented here: 
	 http://en.wikipedia.org/wiki/Topological_sorting#Algorithms
    """
    global nations
    rerun_these_nodes = NodeList()
    number_of_not_dirty_iterations = 0
    
    while nations.count() > 0 and number_of_not_dirty_iterations < 3:
        dirty = False
        while nations.count() > 0:
            current_node = nations.pop_first()
            if current_node.dependency_count() > 0:
                # if we still have dependencies, then just move on
                rerun_these_nodes.append(current_node)
                dirty = True
            else:
                # if we don't have any dependencies, then
                # we can add to the results
                # AND cause this item to be removed from
                # everybody else's dependency lists
                result_graph.append(current_node.name)
                nations.destroy_dependency(current_node)
                dirty = True
                
        nations = rerun_these_nodes
        rerun_these_nodes = NodeList()
        if dirty:
            number_of_not_dirty_iterations = 0
        else:
            number_of_not_dirty_iterations += 1
    
    if number_of_not_dirty_iterations == 3:
        raise Exception("Invalid input file (dependency loop detected)")
# end build_graph


def verify_output():
    """ matches the output to the original rules """
    result = True
    for line in rules:
        regex_result = regex.split(line)
        
        # extract the dependency (before/after)    
        dependency = regex_result[2]
        
        if dependency == "before": 
            country_a_name = regex_result[1]    
            country_b_name = regex_result[3]
        else:
            country_a_name = regex_result[3]    
            country_b_name = regex_result[1]
            
        country_a_position = result_graph.index(country_a_name)
        country_b_position = result_graph.index(country_b_name)
    
        if country_a_position > country_b_position:
            print "FAILED: " + country_a_name + " should be, and isn't, before " + country_b_name
            result = False

    return result
# end verify_output


def verify_to_canon():
    """ matches result list to specified canonical result file (if specified) """
    result = "Canonical match with {0} succeeded.".format(compare_file_name)
    if compare_file_name:
        counter = 0
        with open(compare_file_name, 'r') as fh:
            for line in fh:
                line = line.strip()
                if line != result_graph[counter]:
                    result = "WARNING: Canonical match with {0}\n failed first on result:{1} != canon:{2}".format(
                        compare_file_name, line, result_graph[counter])
                    break
                counter += 1
    else:
        result = "WARNING: Canonical result file not specified"

    return result
# end verify_to_canon


# global variables
regex = re.compile(r"(\w+)\s+comes\s+(before|after)\s+([\w\s]+)")
rules = []
nations = NodeList()
result_graph = []
input_file_name = None
compare_file_name = None

# these 2 are operation flags
print_metadata = True  # for debugging
do_validation = True


def main():
    """ ties everything together and prints output """
    timer = dict()
    timer["start"] = time.time()

    validate_arguments()
    timer["launched"] = time.time()

    # if we got this far, we have arguments
    # so read the file contents into global rules
    read_input_file()
    timer["read"] = time.time()
    
    create_tree()
    timer["treed"] = time.time()

    build_graph()
    timer["graphed"] = time.time()

    if do_validation:
        verify_result = verify_output()
    timer["verified"] = time.time()

    if do_validation:
        canon_result = verify_to_canon()
    timer["matched"] = time.time()

    # and finally, print it
    for item in result_graph:
        print item
    timer["printed"] = time.time()

    if print_metadata:
        print "\n------------------------------------------------------------"
        print "Metadata about the program"
        print "read file %s" % input_file_name
        print "read %d rules" % len(rules)
        print "ordered %d nations" % len(result_graph)
        if do_validation:
            print "\nValidation:"
            if not verify_result:
                print "validation against all source rules: FAILED.\n On review of the input rules, the output was incorrect"
                raise Exception("Invalid input file")
            print "validation against all source rules: Passed"
            print canon_result
        print "\nTimings:"
        print "arg processing took %f seconds" % (timer["launched"] - timer["start"])
        print "file read took      %f seconds" % (timer["read"] - timer["launched"])
        print "tree creation took  %f seconds" % (timer["treed"] - timer["read"])
        print "graph creation took %f seconds" % (timer["graphed"] - timer["treed"])
        print "tree + graph took   %f seconds" % (timer["graphed"] - timer["read"])
        if do_validation:
            print "validation took     %f seconds" % (timer["matched"] - timer["treed"])
        print "output took         %f seconds" % (timer["printed"] - timer["verified"])
        print "\ntime overall was    %f seconds" % (time.time() - timer["start"])

    with open(os.path.basename(__file__) + ".log.csv", 'a') as fh:
        fh.write("{0}, tree + graph, {1}\n".format(datetime.now(), timer["graphed"] - timer["read"]))

# end main


main()
