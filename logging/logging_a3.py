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
    def __init__(self, time, city, line):
        """ Pushes data into new object
            :param line: raw input used to make this record
            :param time: time as float extracted from line
            :param city: city as extracted from line
            :return: Nothing
        """
        self.time = time
        self.city = city
        self.line = line

    def __str__(self):
        """ :return: string representation of the data """
        return self.line

    def __repr__(self):
        """ :return: string representation of the data """
        return self.line


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
        last_item_emitted=0                       # check results
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
            current_event = [time_of_entry, city, line]

            # most_recent_index is the chronologically most recent item in the cycling_buffer
            if time_of_entry > counters.most_recent_index:
                counters.most_recent_index = time_of_entry

            # least_recent_index is the chronologically least recent item in the cycling_buffer
            if time_of_entry < counters.least_recent_index:
                counters.least_recent_index = time_of_entry

            cycling_buffer.append(current_event)

        if (buffer_width_in_seconds() > flags.spacing) or last_round:

            cycling_buffer.sort(None, None, False)
            hard_stop = counters.most_recent_index - flags.spacing
            new_cycling_buffer = []

            for raw_event in cycling_buffer:
                if raw_event[0] < hard_stop:
                    if raw_event[0] < counters.last_item_emitted:
                        raise Exception("sort failed: current={:f} previous={:f}".format(raw_event[0], counters.last_item_emitted))
                    counters.last_item_emitted = raw_event[0]
                    yield Event(raw_event[0], raw_event[1], raw_event[2])
                else:
                    new_cycling_buffer.append(raw_event)
            cycling_buffer = new_cycling_buffer



def update_model(event):
    """ writes out event data for debugging
    :param event: the event to output
    :return: Nothing
    """
    pass


def create_sample_file(write_file_name):
    """ creates sample data file """
    JITTER = 275
    TICKS = 1000
    LINES_PER_TICK = 1000

    def log_line(now):
        timestamp = now - (random.random() * JITTER)
        return "%f   City %d\n" % (timestamp, random.randint(0, 10000))

    start = time.time()

    with open(write_file_name, 'w') as write_file:
        for tick in xrange(TICKS):
            now = start + tick
            for num_line in xrange(LINES_PER_TICK):
               write_file.write(log_line(now))

# end create_sample_file


input_file_handle = None


def main():
    """ Checks for valid input file and launches processing
    :return: Nothing
    """
    global input_file_handle

    data_file_name = "data.txt"
    if len(sys.argv) < 2 or (len(sys.argv) > 1 and (not os.path.isfile(sys.argv[1]))):
        # if we got here, we have to create the input file
        input_file_handle = sys.stdin
    else:
        # we use passed file
        # so we need to extract it from the args
        data_file_name = sys.argv[1]
        if not os.path.isfile(data_file_name):
            create_sample_file(data_file_name)
        input_file_handle = open(data_file_name, 'r')

    start = time.time()
    for event in event_stream(data_file_name):
        # update_model(event)
        print event
    end = time.time()

    output_handle = open("profiler.log", 'a')
    output_handle.write("{0}\n".format(end - start))
    output_handle.close()
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

