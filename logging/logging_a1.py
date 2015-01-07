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


def tee(file_handle, data, print_too):
    file_handle.write("{0}\n".format(data))
    if print_too:
        print data
    for stream in (sys.stdout, sys.stderr):
        stream.flush()


# end tee


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


class Event:
    def __init__(self, time, city):
        self.time = time
        self.city = city


class Bag:
    def __init__(self):
        pass


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

    cycling_buffer = dict()

    counters = Bag()
    counters.most_recent = float(0)
    counters.least_recent = float(10000000000)
    counters.most_recent_printed = 0
    counters.count_of_printed = 0
    counters.read_count = 0
    counters.read_cycle_count = 0
    counters.new_target = None

    flags = Bag()
    flags.spacing = float(300)
    flags.items_to_read_per_cycle = 50000
    flags.stop_at = -1
    flags.debug_halt = False

    def prep_data(line, counters):
        line.strip()
        city = line[line.find(" "):].strip()
        time_of_entry = line[0:line.find(" ")]
        time_of_entry_numeric = float(time_of_entry)
        if time_of_entry_numeric > counters.most_recent:
            counters.most_recent = time_of_entry_numeric
        if time_of_entry_numeric < counters.least_recent:
            counters.least_recent = time_of_entry_numeric
        counters.new_target = counters.most_recent - flags.spacing
        return time_of_entry_numeric, city

    def add_entry(time_of_entry_numeric, city, cycling_buffer):
        if time_of_entry_numeric not in cycling_buffer:
            cycling_buffer[time_of_entry_numeric] = []
        current_event = Event(time_of_entry_numeric, city)
        cycling_buffer[time_of_entry_numeric].append(current_event)

    def process_one(event_key, cycling_buffer, counters):
        event_list = cycling_buffer[event_key]
        for event in event_list:
            counters.count_of_printed += 1
            tee(output_file, "{0} {1}".format(event.time, event.city), False)
            if event.time < counters.most_recent_printed:
                raise Exception("sort failed")
            counters.most_recent_printed = event.time
            counters.least_recent = event.time
        del cycling_buffer[event_key]

    with open("result.txt", 'w') as output_file:
        with open(data_file_name, 'r') as input_file:

            for line in input_file:
                counters.read_count += 1
                counters.read_cycle_count += 1
                if (counters.read_count > flags.stop_at) and (flags.stop_at != -1):
                    flags.debug_halt = True
                if flags.debug_halt:
                    break

                time_of_entry_numeric, city = prep_data(line, counters)

                add_entry(time_of_entry_numeric, city, cycling_buffer)

                if counters.least_recent <= counters.new_target and \
                                counters.read_cycle_count > flags.items_to_read_per_cycle:
                    counters.read_cycle_count = 0
                    keys_to_test = list(cycling_buffer.keys())
                    keys_to_test.sort(None, None, False)
                    for event_key in keys_to_test:
                        if cycling_buffer[event_key][0].time < counters.new_target:
                            process_one(event_key, cycling_buffer, counters)
                        else:
                            break

        keys_to_test = list(cycling_buffer.keys())
        keys_to_test.sort()
        for event_key in keys_to_test:
            process_one(event_key, cycling_buffer, counters)

    end = time.time()
    print end - start
# end main

main()
# cProfile.run('main()')
