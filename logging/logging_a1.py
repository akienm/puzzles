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


class Profiler():
    profile_data = dict()
    accum = 0
    state = 1
    last_started = 2
    name = 3

    @classmethod
    def start(cls, passed_name):
        if passed_name in cls.profile_data:
            data = cls.profile_data[passed_name]
            if data[cls.state] != "started":
                data[cls.state] = "started"
                data[cls.last_started] = time.time()
                cls.profile_data[passed_name] = data
        else:
            data = [0, "started", time.time(), passed_name]
            cls.profile_data[passed_name] = data

    @classmethod
    def stop(cls, passed_name):
        if passed_name in cls.profile_data:
            data = cls.profile_data[passed_name]
            if data[cls.state] == "started":
                data[cls.state] = "paused"
                data[cls.accum] = time.time() - data[cls.last_started]
                data[cls.last_started] = 0
                cls.profile_data[passed_name] = data

    @classmethod
    def dump(cls, output_file_handle=False):
        close_file = False
        if not output_file_handle:
             output_file_handle = open('profile.log', 'a')

        biggest = 0
        cls.tee(output_file_handle, "----------------------------------", True)
        cls.tee(output_file_handle, "Profiling results: {0}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())), True)
        list_of_names = list()
        for item in cls.profile_data.items():
            list_of_names.append(item[1])
        list_of_names.sort(None, None, True)
        for item in list_of_names:
            if item[cls.state] == "started":
                profile(item[cls.name])   # stops that timer
            cls.tee(output_file_handle, "  name: {0}, time: {1}".format(item[cls.name], item[cls.accum]), True)
            if item[cls.accum] > biggest:
                biggest = item[cls.accum]
        cls.tee(output_file_handle, "----------------------------------", True)

        if close_file:
            output_file_handle.close()
        return biggest

    @classmethod
    def tee(cls, file_handle, data, print_flag):
        if file_handle:
            file_handle.write("{0}\n".format(data))
        if print_flag:
            print data
# end tee


def tee(file_handle, data, print_too):
    file_handle.write("{0}\n".format(data))
    if print_too:
        print data
    for stream in (sys.stdout, sys.stderr):
        stream.flush()
# end tee


def create_sample_file(write_file_name):
    """ creates sample data file """
    Profiler.start("sample create")
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
                fh.write(log_line(now)+"\n")

    Profiler.stop("sample create")
# end create_sample_file


class Event:
    def __init__(self):
        self.time = 0.0
        self.city = ""


def main():

    if len(sys.argv) < 2 or (len(sys.argv) > 1 and (not os.path.isfile(sys.argv[1]))):
        # we have to create file
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
    most_recent = float(0)
    least_recent = float(10000000000)
    most_recent_printed = 0
    count_of_printed = 0
    read_count = 0
    read_cycle_count = 0

    spacing = float(300)
    items_to_read_per_cycle = 50000
    stop_at = -1
    debug_halt = False

    print "cycle count: {0} width in seconds: {1}".format(items_to_read_per_cycle, spacing)

    start_read = time.time()
    Profiler.start("overall")
    with open("result.txt", 'w') as output:
        with open(data_file_name, 'r') as fh:

            Profiler.start("everything_else")  # starts
            for line in fh:
                read_count += 1
                read_cycle_count += 1
                if read_count > stop_at and stop_at != -1:
                    debug_halt = True
                if debug_halt:
                    break

                city = line[line.find(" "):].strip()
                time_of_entry = line[0:line.find(" ")]
                time_of_entry_numeric = float(time_of_entry)
                if time_of_entry_numeric > most_recent:
                    most_recent = time_of_entry_numeric
                if time_of_entry_numeric < least_recent:
                    least_recent = time_of_entry_numeric

                cycling_buffer[time_of_entry] = city
                new_target = most_recent - spacing
                if least_recent <= new_target and read_cycle_count > items_to_read_per_cycle:
                    read_cycle_count = 0
                    Profiler.stop("everything_else")
                    Profiler.start("make_list")
                    keys_to_test = list(cycling_buffer.keys())
                    Profiler.stop("make_list")
                    Profiler.start("sort")
                    keys_to_test.sort(None, None, False)
                    Profiler.stop("sort")
                    Profiler.start("everything_else")
                    for item in keys_to_test:
                        item_numeric = float(item)
                        if item_numeric < new_target:
                            count_of_printed += 1
                            message = "time:{0} city:{1} output#:{2} time:{3} #inqueue:{4} queuesize: {5}".format(item, cycling_buffer[item], count_of_printed, time.time() - start_read, len(cycling_buffer), most_recent - least_recent)
                            tee(output, message, False)
                            if item_numeric < most_recent_printed:
                                raise Exception("sort failed")
                            most_recent_printed = item_numeric
                            least_recent = item_numeric
                            del cycling_buffer[item]
                        else:
                            break


        Profiler.start("flush")
        Profiler.start("make_list")
        keys_to_test = list(cycling_buffer.keys())
        print "keys now: {0}".format(len(keys_to_test))
        print "width in seconds: {0}".format(most_recent - least_recent)
        Profiler.stop("make_list")
        Profiler.start("sort")
        keys_to_test.sort()
        Profiler.stop("sort")
        Profiler.start("everything_else")
        for item in keys_to_test:
            count_of_printed += 1
            message = "time:{0} city:{1} output#:{2} time:{3} #inqueue:{4} queuesize: {5}".format(item, cycling_buffer[item], count_of_printed, time.time() - start_read, len(cycling_buffer), most_recent - least_recent)
            tee(output, message, False)
            del cycling_buffer[item]
        Profiler.stop("everything_else")
        Profiler.stop("flush")

        Profiler.stop("overall")

        Profiler.dump()
# end main


main()
