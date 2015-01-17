#!/usr/bin/python

# Puzzle #2: logging
# Akien MacIain 12/26/2014
# algorithm 5

# logging_a4 is the fastest, but doesn't conform to the puzzle's required interfaces.
# The main reason this one is slower is because yield is significantly slower than
# print.



import os.path
import sys
import time
import cProfile
import pstats


time_overall = 0.0          # user to monitor program execution time


def event_stream(data_file_name):
    """ Sorts events into order.
    data_file_name = file name to use. If not specified (or None) use stdin
    yield: an event string until the end of the input stream
    modifies global: time_overall
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

    least_recent_entry = "99999999999.0"        # time stamp for the oldest item in the cycling buffer
    least_recent_index = 0                      # index into cycling_buffer of the least_recent_entry
    most_recent_entry = "0.0"                   # time stamp for the most recent item in the cycling buffer
    most_recent_index = 0                       # index into cycling_buffer of the most_recent_entry
    last_item_emitted = "0.0"                   # time stamp for the most recent one output. Used for validation

    def buffer_width_in_seconds():
        return most_recent_index - least_recent_index

    last_round = False                          # the outer loop tests this flag. Keep going till false
    cycling_buffer = []                         # where the events are stored for sorting

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
            new_cycling_buffer = []                 # this one will replace the old one

            for line in cycling_buffer:
                if line < hard_stop_string:
                    if line < last_item_emitted:    # output validation. could remove and save 2/10ths second per million
                        raise Exception("sort failed: current={:f} previous={:f}".format(line, last_item_emitted))
                    last_item_emitted = line
                    yield line[:-1]                 # this line is sorted and old enough to emit
                else:
                    new_cycling_buffer.append(line) # this entry isn't old enough, push to the new list to go again

            # now get ready for the next round
            cycling_buffer = new_cycling_buffer     # cuz letting the old one go out of scope was so much faster
            least_recent_entry = "99999999999.0"    # time stamp for the oldest item in the cycling buffer
        # end if

    # end while

    end = time.time()

    time_overall = end - start
# end main


def update_model(event):
    """
    provides the correct interface for the puzzle, does nothing
    :param event: required but not used
    :return: Nothing
    """
    pass


def main():
    """ main event processing loop (extrnal interface per the puzzle)
    :return: Nothing
    """
    for event in event_stream(None):    # None uses command line or stdin
        update_model(event)
        print(event)

_profile = False                        # this flag control profiling

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

