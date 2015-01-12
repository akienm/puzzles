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
import random
import cProfile
from collections import deque
import pstats


class EventProcessor(object):

    """ EventProcessor
        Reads file and sorts output by time. Sorts within a 300 second window
        and jettisons results after they're returned to save memory.

        Multiple EventProcessor instances may be active at the same time,
        as they're differentiated by file name. However, this code will not
        sort across multiple input streams.
    """

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
        def __init__(self, line, time, city):
            """ Pushes data into new object
                :param line: raw input used to make this record
                :param time: time as float extracted from line
                :param city: city as extracted from line
                :return: Nothing
            """
            self.line = line
            self.time = time
            self.city = city

        def __str__(self):
            """ :return: string representation of the data """
            return self.line

        def __repr__(self):
            """ :return: string representation of the data """
            return self.line

    def __init__(self, data_file_name):
        """
        :param data_file_name: file name this instance will operate and be known by
        :return: Nothing
        """

        self.data_file_name = data_file_name    # stores file name to read
        self.stream_complete = False            # tells generator all records are in output

        # counters contains all the counters. Only real use is to make
        # it visually more clear that the data in question is a counter
        self.counters = self.Bag(
            most_recent=float(0),               # time stamp for the most recent item in the cycling buffer
            least_recent=float(10000000000),    # time stamp for the oldest item in the cycling buffer
            most_recent_output=0,               # time stamp for the most recent one output. Used for validation
            read_cycle_count=0,                 # used to help determine when to sort
            new_target=None                     # process records up to this time stamp
        )

        # flags contains all the runtime control flags. These values are
        # all constants. Only real use is to make it visually more clear
        # that the data in question is a flag
        self.flags = self.Bag(
            spacing=float(300),                 # target spacing between most_recent and least_recent
            items_to_read_per_cycle=50000       # read this many before trying a sort
        )

        # cycling_buffer contains the events spanning the
        # spacing specified in the flags.
        self.cycling_buffer = dict()

        # these variable initializations are here so that they will
        # share the scope of the parent function, making them available
        # to the sub-functions defined below
        self.line = None
        self.city = None
        self.time_of_entry = None

    def event_generator(self):
        """ This spits out events - events are removed from the BEGINNING
            of the output_buffer. (and process_one adds to the END of the
            output_buffer)
            :return: Yields an event
        """
        event_source = self.process()
        while not self.stream_complete:
            for block in event_source:
                for event_to_yield in block:
                    yield event_to_yield

    def prep_data(self):
        """  Reads amd preps the data, updates relevant counters
        :return: Nothing
        """
        sep = self.line.find(" ")
        self.city = self.line[sep+1:-1]
        self.time_of_entry = float(self.line[0:sep-1])
        self.current_event = self.Event(self.line[0:-1], self.time_of_entry, self.city)

        # most_recent is the chronologically most recent item in the cycling_buffer
        self.counters.most_recent = max(self.time_of_entry, self.counters.most_recent)

        # least_recent is the chronologically least recent item in the cycling_buffer
        self.counters.least_recent = min(self.time_of_entry, self.counters.least_recent)

        # new_target specifies the point records should be processed to
        self.counters.new_target = self.counters.most_recent - self.flags.spacing

    def add_entry(self):
        """ Creates event object and adds it to the appropriate time-
            identified entry in the cycling_buffer. This sub-list
            allows multiple entries with the same time stamp
            :return: Nothing
        """
        # if an entry for this time stamp isn't in the cycling_buffer,
        # then add one for it
        if self.time_of_entry not in self.cycling_buffer:
            self.cycling_buffer[self.time_of_entry] = []
        # now push the new event into that entry in the cycling_buffer
        self.cycling_buffer[self.time_of_entry].append(self.current_event)

    def process_one(self, output_buffer):
        """ Processes one entry in the cycling_buffer,
            puts result(s) into the FIFO output_buffer, then deletes
            it from the cycling buffer.
            :return: Nothing
        """
        event_list = self.cycling_buffer[self.event_key]
        for event in event_list:
            output_buffer.append(event)
            # lets do some inline validation just to be sure
            if event.time < self.counters.most_recent_output:
                raise Exception("sort failed event.time {0} < counters.most_recent_output {1}".format(
                    event.time, self.counters.most_recent_output))
            self.counters.most_recent_output = event.time
            self.counters.least_recent = event.time
        del self.cycling_buffer[self.event_key]

    def process(self):
        """  This is the code that reads and sorts the incoming data,
             makes event objects from it, and populates the output queue.

             Default operating mode for this code is that this will run in
             it's own thread.
             :return: Nothing
        """
        with open(self.data_file_name, 'r') as input_file:

            for self.line in input_file:
                self.counters.read_cycle_count += 1

                self.prep_data()  # uses line, counters
                self.add_entry()  # uses time_of_entry, city, cycling_buffer

                if (self.counters.least_recent <= self.counters.new_target) and \
                        (self.counters.read_cycle_count > self.flags.items_to_read_per_cycle):

                    # if there are already items in the output buffer, wait
                    # until they've all been consumed.

                    self.counters.read_cycle_count = 0  # resets this counter since we're processing the list
                    self.keys_to_test = list(self.cycling_buffer.keys())
                    self.keys_to_test.sort(None, None, False)
                    output_buffer = deque()
                    for self.event_key in self.keys_to_test:
                        if self.cycling_buffer[self.event_key][0].time < self.counters.new_target:
                            self.process_one(output_buffer)  # uses event_key, cycling_buffer, counters)
                        else:
                            break

                    # now we let the generator know that data in the output_stream is valid
                    yield output_buffer

        # we've completed reading the file.
        # are there records in the cycling buffer that still need processing?
        if self.cycling_buffer:

            self.keys_to_test = list(self.cycling_buffer.keys())
            self.keys_to_test.sort()
            output_buffer = deque()
            for self.event_key in self.keys_to_test:
                self.process_one(output_buffer)  # event_key, cycling_buffer, counters)

            yield output_buffer

        self.stream_complete = True
# end EventProcessor


# used by event_stream to store created stream handlers
_event_processors = dict()


def event_stream(data_file_name):
    """
    :param data_file_name: file to read event data from
    :return: a generator for the output of the sort process
    """
    global _event_processors
    if data_file_name not in _event_processors:
        _event_processors[data_file_name] = EventProcessor(data_file_name)
    generator = _event_processors[data_file_name].event_generator()
    return generator
# end event_stream


output_handle = None  # used by update_model to push output to a file for debugging


def update_model(event):
    """ writes out event data for debugging
    :param event: the event to output
    :return: Nothing
    """
    global output_handle
    if not output_handle:
        output_handle = open("result.txt", 'w')
    if event:
        output_handle.write(event.line)
    else:
        output_handle.close()
        output_handle = None


def create_sample_file(write_file_name):
    """ creates sample data file """
    JITTER = 275
    TICKS = 1000
    LINES_PER_TICK = 1000

    def log_line(now):
        timestamp = now - (random.random() * JITTER)
        timestamp = "{:f}".format(timestamp)
        timestamp = timestamp[4:]
        return "%s   City %d" % (timestamp, random.randint(0, 10000))

    start = time.time()

    with open(write_file_name, 'w') as fh:
        for tick in xrange(TICKS):
            now = start + tick
            for num_line in xrange(LINES_PER_TICK):
                fh.write(log_line(now) + "\n")

# end create_sample_file


def main():
    """ Checks for valid input file and launches processing
    :return: Nothing
    """

    start = time.time()

    # check args
    if len(sys.argv) < 2 or (len(sys.argv) > 1 and (not os.path.isfile(sys.argv[1]))):
        # if we got here, we have to create the input file
        data_file_name = "data.txt"
        if not os.path.isfile(data_file_name):
            create_sample_file(data_file_name)
    else:
        # we use passed file
        # so we need to extract it from the args
        data_file_name = sys.argv[1]

    # generator = event_stream(data_file_name)
    for event in event_stream(data_file_name):
        update_model(event)
        print event

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

