#!/usr/bin/python
# maskstringnizer.py
# Generates C functions from header file bitmask macro definition,
# which help printing given integer flag in human-readable string.
#
# stringnize: 
# Converts the integer to its corresponding symbol.
# flags2str:
# Returns all bitmask symbols contained in the integer.
#
# usage:
# In stead of writing boiler plate code like
# if (flags & FILE_ATTRIBUTE_READONLY)
#     printf("read-only");
#
# You can
# $ maskstringnizer.py < winnt.h FILE_ATTRIBUTE_ > debug.c
# and
# printf(flags2str(flags));
#
# Copyright (c) 2016 Kanda.Motohiro@gmail.com
# Licensed under the Apache License, Version 2.0
import sys


def doit(iter, pattern):
    mask2str = {}
    for line in iter:
        if not line.startswith("#define") or pattern not in line:
            continue
        els = line.split()
        # print els
        s = els[1].replace(pattern, "").lower()
        v = els[2].replace("(", "").replace(")", "")
        try:
            mask = int(v, 0)
        except ValueError, e:
            sys.stderr.write(str(e) + "\n")
            continue
        mask2str[mask] = s

    if len(mask2str) == 0:
        raise Exception("no pattern %s found in stdin" % pattern)

    print cProg

    for mask, s in mask2str.iteritems():
        print '{ "%s", 0x%x }, ' % (s, mask)
    print """{ 0, 0 }
             };"""


cProg = """
#include <string.h>
#include <stdlib.h>

struct e { char *name; int mask; };
static struct e mask2str[];

static char *
stringnize(int val)
{
    struct e *e;

    for (e = &mask2str[0]; e->name != 0; e++) {
        if (e->mask == val)
            return e->name;
    }
    return "";
}

static char *
flags2str(int val)
{
    struct e *e;
    char *out = malloc(4096);

    out[0] = 0;
    for (e = &mask2str[0]; e->name != 0; e++) {
        if ((e->mask & val) == 0)
            continue;
        strcat(out, e->name);
        strcat(out, " ");
    }
    return out;
}

static struct e mask2str[] = {
"""

# from winioctl.h
sample = """
#define USN_REASON_DATA_OVERWRITE        (0x00000001)
#define USN_REASON_DATA_EXTEND           (0x00000002)
#define USN_REASON_DATA_TRUNCATION       (0x00000004)
#define USN_REASON_NAMED_DATA_OVERWRITE  (0x00000010)
"""


def _test():
    """
    Running this expects
    named_data_overwrite data_overwrite data_extend data_truncation
    data_extend
    """
    doit(sample.split("\n"), "USN_REASON_")
    print """#include <stdio.h>
int main() { char *out = flags2str(0xffffffff);
puts(out);
puts(stringnize(2));
}"""
    sys.exit(0)


def usage():
    print "usage: %s PATTERN < HEADER" % sys.argv[0]
    sys.exit(0)


def main():
    if len(sys.argv) != 2:
        usage()
    doit(sys.stdin, sys.argv[1])
    sys.exit(0)

if __name__ == '__main__':
    if "--test" in sys.argv:
        _test()
    main()
