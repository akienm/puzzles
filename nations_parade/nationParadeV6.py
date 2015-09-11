#!/usr/bin/python
# coding=utf-8

# Puzzle #3: I Love A Parade
# Akien MacIain 12/22/2014
# NPV6

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
    global dependency_graph
    global rules

    with open(input_file_name, 'r') as fh:
        for line in fh:

            # take apart the data
            line = line.strip()
            rules.append(line)
            rresult = regex.split(line)
            dependency = rresult[2]
            country_a_name = rresult[1]
            country_b_name = rresult[3]

            # and make entries if they don't already exist
            if country_a_name not in dependency_graph:
                dependency_graph[country_a_name] = []

            if country_b_name not in dependency_graph:
                dependency_graph[country_b_name] = []

            # now add the earlier one to the
            # later one's dependency list
            if dependency == "before":
                dependency_graph[country_b_name].append(country_a_name)
            else:           # after
                dependency_graph[country_a_name].append(country_b_name)

# end read_input_file


def build_graph():
    """ go through dependency_graph and sort into result_graph """
    global dependency_graph
    global result_graph

    result_graph = []

    # go until we've consumed all the dependencies
    while dependency_graph:

        no_loop_found_this_iteration = False
        for node, edges in dependency_graph.items():
            for edge in edges:
                if edge in dependency_graph:
                    # still has edges, loop it around again
                    break
                else:
                    # this one is ready for the result_graph
                    no_loop_found_this_iteration = True
                    del dependency_graph[node]
                    result_graph.append(node)

        if not no_loop_found_this_iteration:
            raise Exception("FAILED: A loop in the dependencies was found ({0} items)".format(len(dependency_graph)))

# end build_graph


def verify_output_against_rules():
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
            print "FAILED: A loop in the dependencies was found ({0}/{1})".format(country_a_name, country_b_name)
            result = False

    return result
# end verify_output


def verify_to_canon():
    """ if canonical file specified in arguments, matches result list to canonical result file """
    result = "Canonical match with {0} succeeded.".format(compare_file_name)
    if compare_file_name:
        counter = 0
        with open(compare_file_name, 'r') as fh:
            for line in fh:
                line = line.strip()
                if line != result_graph[counter]:
                    result = "WARNING: Canonical match with {0}\n failed first on canon:{1} != result:{2}".format(
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
dependency_graph = dict()
result_graph = []
input_file_name = None
compare_file_name = None

# these 2 are operation flags
print_metadata = True  # for debugging
do_validation = True


def main():
    """ ties everything together and prints output """
    global result_graph
    timer = dict()
    timer["start"] = time.time()

    # were we passed what we needed?
    validate_arguments()
    timer["launched"] = time.time()

    # if we got this far, we have arguments
    # so read the file contents into global rules
    read_input_file()
    timer["read"] = time.time()

    # now sort the dependency_graph into the result_graph
    build_graph()
    timer["graphed"] = time.time()

    # match against the input rules
    if do_validation:
        verify_result = verify_output_against_rules()
    timer["verified"] = time.time()

    # match against the canonical file
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
                message = "FAILED: Validation against all source rules\n On review of the input rules, the output was incorrect"
                print message
                raise Exception(message)
            print "validation against all source rules: Passed"
            print canon_result
        print "\nTimings:"
        print "arg processing took %f seconds" % (timer["launched"] - timer["start"])
        print "file read took      %f seconds" % (timer["read"] - timer["launched"])
        print "graph creation took %f seconds" % (timer["graphed"] - timer["read"])
        if do_validation:
            print "validation took     %f seconds" % (timer["matched"] - timer["read"])
        print "output took         %f seconds" % (timer["printed"] - timer["verified"])
        print "\ntime overall was    %f seconds" % (time.time() - timer["start"])

# end main


main()
