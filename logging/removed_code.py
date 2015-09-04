
def tee(file_handle, data, print_too):
    """
    tee - handles output for debugging
    :param file_handle: handle to output file
    :param data: data to write
    :param print_too: print to stdout
    :return: No return
    """
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
