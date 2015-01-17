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


time_overall = 0.0


def event_stream(data_file_name):
    """ Checks for valid input file and launches processing
    :return: Nothing
    """
    global time_overall

    if len(sys.argv) < 2:
        # if we got here, we have to create the input file
        input_file_handle = sys.stdin
    else:
        # we use passed file
        # so we need to extract it from the args
        if not data_file_name:
            data_file_name = sys.argv[1]
        if not os.path.isfile(data_file_name):
            raise Exception("file not found: %s" % data_file_name)
        input_file_handle = open(data_file_name, 'r')

    spacing = float(300)                        # target spacing between most_recent_entry and least_recent_entry
    items_to_read_per_cycle = 100000            # read this many before trying a sort

    most_recent_entry = "0.0"                   # time stamp for the most recent item in the cycling buffer
    least_recent_entry = "99999999999.0"        # time stamp for the oldest item in the cycling buffer
    last_item_emitted = "0.0"                   # time stamp for the most recent one output. Used for validation
    least_recent_index = 0
    most_recent_index = 0

    def buffer_width_in_seconds():
        return most_recent_index - least_recent_index

    cycling_buffer = []
    last_round = False

    # basic idea: Read in items_to_read_per_cycle lines. As we read them in, note the most_recent_entry and
    # least_recent_entry. That tells us how wide the cycling_buffer is. If it's below the value of spacing (300)
    # we just loop back and read some more.
    #
    # But if we do have records "older" than most_recent_entry - spacing, then we emit them to caller.
    # once we've cycled though those "old" records, we start adding the remaining records to a new list.
    # That list then becomes the new cycling_list.
    #
    # This all takes advantage of the fact that these 4 items are really inexpensive (time wise) in Python:
    #
    # list.append()
    # letting a list fall out of scope (i.e. letting it just get garbage collected)
    # sorting a list (either with some_list.sort() or sorted(some_list))
    # creating an empty list
    #
    # It's very much a brute force approach.

    start = time.time()

    while not last_round:       # until we run out of records

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
                    yield line[:-1]
                else:
                    new_cycling_buffer.append(line)

            # now get ready for the next round
            cycling_buffer = new_cycling_buffer
            least_recent_entry = "99999999999.0"     # time stamp for the oldest item in the cycling buffer
        # end if

    # end while

    end = time.time()

    time_overall = end - start
# end main


def update_model(event):
    pass


def main():
    for event in event_stream(None):  # None uses command line or stdin
        update_model(event)
        print(event)

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
    result_in_seconds = time_overall
    output_handle = open("profiler.log", 'a')
    output_handle.write("{0}\n".format(result_in_seconds))
    output_handle.close()

