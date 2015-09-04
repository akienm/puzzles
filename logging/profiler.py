class Profiler():
    profile_data = dict()
    accum = 0
    state = 1
    last_started = 2
    name = 3
    biggest = 0

    def __init__(self):
        pass

    @classmethod
    def start(cls, passed_name):
        if passed_name in cls.profile_data:
            data = cls.profile_data[passed_name]
            if data[cls.state] != "started":
                data[cls.state] = "started"
                data[cls.last_started] = time.time()
                cls.profile_data[passed_name] = data
            else:
                raise Exception("asked to start profiler {0} when already started".format(passed_name))
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
            else:
                raise Exception("asked to stop profiler {0} when already stopped".format(passed_name))

    @classmethod
    def dump_as_string(cls):
        cls.biggest = 0
        result = ""
        result += "----------------------------------\n"
        result += "Profiling results: {0}\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        list_of_names = list()
        for item in cls.profile_data.items():
            list_of_names.append(item[1])
        list_of_names.sort(None, None, True)
        for item in list_of_names:
            if item[cls.state] == "started":
                Profiler.stop(item[cls.name])   # stops that timer
            result += "  name: {0}, time: {1}\n".format(item[cls.name], item[cls.accum])
            if item[cls.accum] > cls.biggest:
                cls.biggest = item[cls.accum]
        result += "----------------------------------\n"
        return result

    @classmethod
    def dump(cls, output_file_handle=False):
        close_file = False
        if not output_file_handle:
             output_file_handle = open('profile.log', 'a')

        result = cls.dump_as_string()
        cls.tee(output_file_handle, result, True)

        if close_file:
            output_file_handle.close()
        return cls.biggest

    @classmethod
    def tee(cls, file_handle, data, print_flag):
        if file_handle:
            file_handle.write("{0}\n".format(data))
        if print_flag:
            print data
# end tee
