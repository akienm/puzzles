#!/usr/bin/python

# Interview question 3/2015
# Akien MacIain
# algorithm 1

# given two sets, how to return the union
# asked me during a phone interview, this is my answer

import os.path
import sys
import time
import cProfile
import pstats

def TC01_setmatch(s1, s2):
    result = list(set(s1) & set(s2))
    result.sort()
    return result

def TC02_intersect(l1, l2):
    result = list(set(l1).intersection(set(l2)))
    result.sort()
    return result

def TC03_simplesearch(l1, l2):
    l3 = list()
    for c in l1:
        if c in l2:
            l3.append(c)
    l3.sort()
    return l3

def TC04_stringmatch(l1,l2):
    l1.sort()
    l2.sort()
    s1 = ''.join(l1)
    l3 = list()
    for c in l2:
        if c in s1:
            l3.append(c)
    l3.sort()
    return l3

loop_tests = 0

def TC05_sortedlistmatch(l1, l2):
    global loop_tests
    l1.sort()
    l2.sort()
    l3 = []
    p1 = 0
    p2 = len(l2)
    for c in l2:
        for m in range(p1, p2):
            testchar = l1[m]
            loop_tests += 1
            if testchar < c:
                p1 = m
            if testchar == c:
                l3.append(c)
            if testchar >= c:
                break
    l3.sort
    return l3


time_overall = 0.0
iterations = 0


def main():
    global time_overall
    global iterations
    start = time.time()

    iterations = 100000

    result = []
    for i in range(0, iterations):
        l1 = ['a','c','d','e','g','h','i']
        l2 = ['b','d','f','h','j','l']
        result = TC01_setmatch(l1, l2)
    print result
    for i in range(0, iterations):
        l1 = ['a','c','d','e','g','h','i']
        l2 = ['b','d','f','h','j','l']
        result = TC02_intersect(l1, l2)
    print result
    for i in range(0, iterations):
        l1 = ['a','c','d','e','g','h','i']
        l2 = ['b','d','f','h','j','l']
        result = TC03_simplesearch(l1, l2)
    print result
    for i in range(0, iterations):
        l1 = ['a','c','d','e','g','h','i']
        l2 = ['b','d','f','h','j','l']
        result = TC04_stringmatch(l1, l2)
    print result
    for i in range(0, iterations):
        l1 = ['a','c','d','e','g','h','i']
        l2 = ['b','d','f','h','j','l']
        result = TC05_sortedlistmatch(l1, l2)
    print result

    end = time.time()

    time_overall = end - start

# these flags control profiling
_profile = True

if _profile:
    cProfile.run('main()', "profiler.raw", "tottime")
    output_handle = open("profiler.log", 'a')
    p = pstats.Stats('profiler.raw', stream=output_handle)
    p.strip_dirs().sort_stats("tottime").print_stats(18)
    output_handle.close()
    p = pstats.Stats('profiler.raw')
    p.strip_dirs().sort_stats("tottime").print_stats(18)
else:
    main()
    result_in_seconds = time_overall
    output_handle = open("profiler.log", 'a')
    output_handle.write("{0}\n".format(result_in_seconds))
    output_handle.close()

print "average loop tests per iteration %f " % (loop_tests / iterations)
print "time in seconds %f " % time_overall