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

    def buffer_width_in_seconds():
        return most_recent_index - least_recent_index

    # flags contains all the runtime control flags. These values are
    # all constants. Only real use is to make it visually more clear
    # that the data in question is a flag
    spacing = float(300)                        # target spacing between most_recent_index and least_recent_index
    items_to_read_per_cycle = 100000            # read this many before trying a sort

    # counters contains all the counters. Only real use is to make
    # it visually more clear that the data in question is a counter
    most_recent_index = float(0)                # time stamp for the most recent item in the cycling buffer
    least_recent_index = float(10000000000)     # time stamp for the oldest item in the cycling buffer
    last_item_emitted = 0                       # time stamp for the most recent one output. Used for validation

    cycling_buffer = []
    last_round = False

    start = time.time()

    while not last_round:

        for read_loop_counter in xrange(0, items_to_read_per_cycle):
            try:
                line = input_file_handle.readline()
            except:
                last_round = True
                break

            if not line:
                last_round = True
                break

            line = line.rstrip()
            time_of_entry = float(line.split(None, 1)[0])
            current_event = [time_of_entry, line]

            # most_recent_index is the chronologically most recent item in the cycling_buffer
            if time_of_entry > most_recent_index:
                most_recent_index = time_of_entry

            # least_recent_index is the chronologically least recent item in the cycling_buffer
            if time_of_entry < least_recent_index:
                least_recent_index = time_of_entry

            cycling_buffer.append(current_event)

        if (buffer_width_in_seconds() > spacing) or last_round:

            hard_stop = most_recent_index - spacing
            cycling_buffer.sort(None, None, False)
            new_cycling_buffer = []

            for raw_event in cycling_buffer:
                if raw_event[0] < hard_stop:
                    if raw_event[0] < last_item_emitted:
                        raise Exception("sort failed: current={:f} previous={:f}".format(raw_event[0], last_item_emitted))
                    last_item_emitted = raw_event[0]
                    print raw_event[1]
                else:
                    new_cycling_buffer.append(raw_event)
            cycling_buffer = new_cycling_buffer

    end = time.time()

    output_handle = open("profiler.log", 'a')
    output_handle.write("{0}\n".format(end - start))
    output_handle.close()
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
    main()

