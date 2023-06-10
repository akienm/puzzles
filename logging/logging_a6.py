#!/usr/bin/python

# Puzzle #2: logging by Darrell Bishop
# Akien MacIain 12/26/2014
# algorithm 6

# this is the fastest version of this code, but does not conform to the
# interfaces required by the puzzle. (Generators aren't fast.)


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

    start = time.time()

    while not last_round:

        for read_loop_counter in range(0, items_to_read_per_cycle):
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

            for buffer_index in range(0,  len(cycling_buffer)):
                line = cycling_buffer[buffer_index]
                if line < hard_stop_string:
                    if line < last_item_emitted:
                        raise Exception("sort failed: current={:f} previous={:f}".format(line, last_item_emitted))
                    last_item_emitted = line

                    # pass back data
                    yield line[:-1]

                else:
                    for new_buffer_index in range(buffer_index, len(cycling_buffer)):
                        new_cycling_buffer.append(cycling_buffer[new_buffer_index])
                    break

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

