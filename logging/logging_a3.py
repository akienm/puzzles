#!/usr/bin/python

# Puzzle #2: logging
# Akien MacIain 12/26/2014
# algorithm 1 - Parametrised Periodic Sort
# Note: algorithm 0 - "Sort each time 300 is exceeded" was far too slow

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

class Bag(object):
    """ Bag is a generic container
        it's instantiated with name/value pairs
    """
    def __init__(self, **kwargs):
        """ Pushes values into object's data space dictionary
            :param kwargs: name=value pairs to put into object
            :return: Nothing
        """
        self.__dict__.update(kwargs)

class Event(object):
    """ container for event data.
        includes input data (line), time and city
    """
    def __init__(self, time, city):
        """ Pushes data into new object
            :param line: raw input used to make this record
            :param time: time as float extracted from line
            :param city: city as extracted from line
            :return: Nothing
        """
        self.time = time
        self.city = city

    def __str__(self):
        """ :return: string representation of the data """
        return self.line()

    def __repr__(self):
        """ :return: string representation of the data """
        return self.line()

    def line(self):
        return "%f %s\n" % (self.time, self.city)


def event_stream(data_file_name):
    """  This is the code that reads and sorts the incoming data,
         makes event objects from it, and populates the output queue.

         Default operating mode for this code is that this will run in
         it's own thread.
         :return: Nothing
    """

    def buffer_width_in_seconds():
        return counters.most_recent_index - counters.least_recent_index

    # counters contains all the counters. Only real use is to make
    # it visually more clear that the data in question is a counter
    counters = Bag(
        most_recent_index=float(0),               # time stamp for the most recent item in the cycling buffer
        least_recent_index=float(10000000000),    # time stamp for the oldest item in the cycling buffer
        most_recent_index_output=0,               # time stamp for the most recent one output. Used for validation
        read_cycle_count=0
    )

    # flags contains all the runtime control flags. These values are
    # all constants. Only real use is to make it visually more clear
    # that the data in question is a flag
    flags = Bag(
        spacing=float(300),                 # target spacing between most_recent_index and least_recent_index
        items_to_read_per_cycle=100000       # read this many before trying a sort
    )

    cycling_buffer = []
    last_round = False

    while not last_round:

        for read_loop_counter in xrange(0, flags.items_to_read_per_cycle):
            try:
                line = input_file_handle.readline()
            except:
                last_round = True
                break

            if not line:
                last_round = True
                break

            line = line.rstrip()
            time_of_entry, city = line.split(None, 1)
            time_of_entry = float(time_of_entry)
            current_event = [time_of_entry, line, city]

            # most_recent_index is the chronologically most recent item in the cycling_buffer
            if time_of_entry > counters.most_recent_index:
                counters.most_recent_index = time_of_entry
                counters.most_recent_event = current_event

            # least_recent_index is the chronologically least recent item in the cycling_buffer
            if time_of_entry < counters.least_recent_index:
                counters.least_recent_index = time_of_entry
                counters.least_recent_event = current_event

            cycling_buffer.append(current_event)

        if (buffer_width_in_seconds() > flags.spacing) or last_round:

            cycling_buffer.sort(None, None, True)
            hard_stop = counters.most_recent_index - flags.spacing
            new_cycling_buffer = []

            for raw_event in cycling_buffer:
                if raw_event[0] < hard_stop:
                    yield Event(raw_event[0], raw_event[1])
                else:
                    new_cycling_buffer.append(raw_event)
            cycling_buffer = new_cycling_buffer



def update_model(event):
    """ writes out event data for debugging
    :param event: the event to output
    :return: Nothing
    """
    pass


input_file_handle = None

def main():
    """ Checks for valid input file and launches processing
    :return: Nothing
    """
    global input_file_handle

    start = time.time()
    if len(sys.argv) < 2 or (len(sys.argv) > 1 and (not os.path.isfile(sys.argv[1]))):
        # if we got here, we have to create the input file
        data_file_name = "data.txt"
        if not os.path.isfile(data_file_name):
            create_sample_file(data_file_name)
        input_file_handle = sys.stdin
    else:
        # we use passed file
        # so we need to extract it from the args
        data_file_name = sys.argv[1]
        input_file_handle = open(data_file_name, 'r')

    # generator = event_stream(data_file_name)
    for event in event_stream(data_file_name):
        update_model(event)
        print event.city

    end = time.time()
    print end - start
# end main

# these flags control profiling
_profile_and_debug = False


def profile_it():
    """ Used to profile program execution
    :return: Nothing
    """
    cProfile.run('main()', "profiler.raw", "tottime")
    output_handle = open("profiler.log", 'a')
    p = pstats.Stats('profiler.raw', stream=output_handle)
    p.strip_dirs().sort_stats("tottime").print_stats(18)
    output_handle.close()


if _profile_and_debug:
    profile_it()
else:
    main()

