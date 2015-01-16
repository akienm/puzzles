#!/usr/bin/python

# Puzzle #2: logging
# Akien MacIain 12/26/2014
# algorithm 4

# As a [role] I want [feature] so that [benefit]
# Given [initial context], when [event occurs], then [ensure some outcomes]

# in order to predict location
# I as a log consumer
# require logs in order

# in order to provide logs in order
# I as a programmer
# require the incoming stream buffer to be limited in size


import os.path
import sys
import time
import cProfile
import pstats


def main():
    """ Checks for valid input file and launches processing
    :return: Nothing
    """
    if len(sys.argv) < 2:
        # if we got here, we have to create the input file
        input_file_handle = sys.stdin

    else:
        # we use passed file
        # so we need to extract it from the args
        data_file_name = sys.argv[1]
        if not os.path.isfile(data_file_name):
            raise Exception("file not found: %s" % data_file_name)
        input_file_handle = open(data_file_name, 'r')

    # flags contains all the runtime control flags. These values are
    # all constants. Only real use is to make it visually more clear
    # that the data in question is a flag
    spacing = float(300)                        # target spacing between most_recent_entry and least_recent_entry
    items_to_read_per_cycle = 1000000            # read this many before trying a sort

    # counters contains all the counters. Only real use is to make
    # it visually more clear that the data in question is a counter
    most_recent_entry = "0.0"                   # time stamp for the most recent item in the cycling buffer
    least_recent_entry = "99999999999.0"        # time stamp for the oldest item in the cycling buffer
    last_item_emitted = "0.0"                   # time stamp for the most recent one output. Used for validation
    least_recent_index = 0
    most_recent_index = 0

    def buffer_width_in_seconds():
        return most_recent_index - least_recent_index

    cycling_buffer = []
    last_round = False

    start = time.time()

    while not last_round:

        for read_loop_counter in xrange(0, items_to_read_per_cycle):
            try:
                line = input_file_handle.readline()
                if not line:
                    last_round = True
                    spacing = 0
                    break
            except:
                last_round = True
                spacing = 0
                break

            # most_recent_entry is the chronologically most recent item in the cycling_buffer
            if line > most_recent_entry:
                most_recent_entry = line

            # least_recent_entry is the chronologically least recent item in the cycling_buffer
            if line < least_recent_entry:
                least_recent_entry = line

            cycling_buffer.append(line)
        # end for

        least_recent_index = float(least_recent_entry.split(None, 1)[0])
        most_recent_index = float(most_recent_entry.split(None, 1)[0])

        if last_round or (buffer_width_in_seconds() > spacing):

            hard_stop_index = most_recent_index - spacing + 0.1
            hard_stop_string = "{:f}".format(hard_stop_index)

            cycling_buffer.sort()  # None, None, False)
            new_cycling_buffer = []

            for line in cycling_buffer:
                if line < hard_stop_string:
                    if line < last_item_emitted:
                        raise Exception("sort failed: current={:f} previous={:f}".format(line, last_item_emitted))
                    last_item_emitted = line
                    print line.rstrip()
                else:
                    new_cycling_buffer.append(line)

            # now get ready for the next round
            cycling_buffer = new_cycling_buffer
            least_recent_entry = "99999999999.0"     # time stamp for the oldest item in the cycling buffer
        # end if

    # end while

    end = time.time()

    return end - start
# end main

# these flags control profiling
_profile = False

if _profile:
    cProfile.run('main()', "profiler.raw", "tottime")
    output_handle = open("profiler.log", 'a')
    p = pstats.Stats('profiler.raw', stream=output_handle)
    p.strip_dirs().sort_stats("tottime").print_stats(18)
    output_handle.close()
else:
    result_in_seconds = main()
    output_handle = open("profiler.log", 'a')
    output_handle.write("{0}\n".format(result_in_seconds))
    output_handle.close()

