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
import threading


class EventProcessor(threading.Thread):

    def __init__(self, data_file_name):
        threading.Thread.__init__(self)
        self.output_buffer = deque()
        self.data_file_name = data_file_name
        self.lock = threading.Lock()
        self.stream_initialized = False
        self.stream_complete = False
        self.start()

    def event_generator(self):
        while (not self.stream_complete) or self.output_buffer:
            while not self.output_buffer:
                pass
            event = self.output_buffer.popleft()
            yield event

        yield False

    def run(self):

        class Bag(object):
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        class Event(object):
            def __init__(self, time, city):
                self.time = time
                self.city = city

            def __str__(self):
                return "{0} {1}".format(self.time, self.city)

            def __repr__(self):
                return "{0} {1}".format(self.time, self.city)

        counters = Bag(
            most_recent=float(0),
            least_recent=float(10000000000),
            most_recent_printed=0,
            count_of_printed=0,
            read_count=0,
            read_cycle_count=0,
            new_target=None
        )
        flags = Bag(
            spacing=float(300),
            items_to_read_per_cycle=50000
        )

        cycling_buffer = dict()
        output_buffer = self.output_buffer

        data_file_name = self.data_file_name
        line = None
        city = None
        time_of_entry_numeric = None

        def prep_data():  # uses line, counters
            line.strip()
            sep = line.find(" ")
            city = line[sep:].strip()
            time_of_entry = float(line[0:sep])
            if time_of_entry > counters.most_recent:
                counters.most_recent = time_of_entry
            if time_of_entry < counters.least_recent:
                counters.least_recent = time_of_entry
            counters.new_target = counters.most_recent - flags.spacing
            return time_of_entry, city

        def add_entry():  # uses time_of_entry, city, cycling_buffer
            if time_of_entry_numeric not in cycling_buffer:
                cycling_buffer[time_of_entry_numeric] = []
            current_event = Event(time_of_entry_numeric, city)
            current_event.line = line
            cycling_buffer[time_of_entry_numeric].append(current_event)

        def process_one():  # uses event_key, cycling_buffer, counters
            event_list = cycling_buffer[event_key]
            for event in event_list:
                counters.count_of_printed += 1
                output_buffer.append(event)
                if event.time < counters.most_recent_printed:
                    raise Exception("sort failed")
                counters.most_recent_printed = event.time
                counters.least_recent = event.time
            del cycling_buffer[event_key]

        with open(data_file_name, 'r') as input_file:

            for line in input_file:
                counters.read_count += 1
                counters.read_cycle_count += 1

                time_of_entry_numeric, city = prep_data()  # uses line, counters

                add_entry()  # uses time_of_entry, city, cycling_buffer

                if (counters.least_recent <= counters.new_target) and \
                        (counters.read_cycle_count > flags.items_to_read_per_cycle):
                    counters.read_cycle_count = 0
                    keys_to_test = list(cycling_buffer.keys())
                    keys_to_test.sort(None, None, False)
                    for event_key in keys_to_test:
                        if cycling_buffer[event_key][0].time < counters.new_target:
                            process_one()  # uses event_key, cycling_buffer, counters)
                        else:
                            break
                    self.stream_initialized = True

        if cycling_buffer:
            keys_to_test = list(cycling_buffer.keys())
            keys_to_test.sort()
            for event_key in keys_to_test:
                process_one()  # event_key, cycling_buffer, counters)

        self.stream_initialized = True
        self.stream_complete = True

_event_processors = dict()


def event_stream(data_file_name):
    global _event_processors
    if data_file_name not in _event_processors:
        _event_processors[data_file_name] = EventProcessor(data_file_name)
    generator = _event_processors[data_file_name].event_generator()
    return generator


output_handle = None


def update_model(event):
    global output_handle
    if not output_handle:
        output_handle = open("result.txt", 'w')
    if event:
        # output_handle.write(event.__str__())
        output_handle.write(event.line)
    else:
        output_handle.close()


def main():
    start = time.time()
    if len(sys.argv) < 2 or (len(sys.argv) > 1 and (not os.path.isfile(sys.argv[1]))):
        # if we got here, we have to create the input file
        data_file_name = "data.txt"
        if not os.path.isfile(data_file_name):
            create_sample_file(data_file_name)
    else:
        # we use passed file
        # so we need to extract it from the args
        data_file_name = sys.argv[1]

    # data_file_name = "data.txt"
    # create_sample_file(data_file_name)

    generator = event_stream(data_file_name)
    for event in generator:
        update_model(event)
        # print event
    #keep_going = True
    #while keep_going:
    #    event = event_stream(data_file_name)
    #    if event:
    #        # print event
    #        pass
    #    else:
    #        keep_going = False

    end = time.time()
    print end - start
# end main


# main()
cProfile.run('main()', None, "tottime")

