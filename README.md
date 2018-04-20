# CS5541-hw6
Scheduling Simulator
Benjamin A. Slack
04.17.2018

This python (3.6.5) based script simulates Uniprocess and Realtime
scheduling algorithms using simple text based tasks specifications.

Usage:

./python3 schedule.py <filepath> ...

Filepath can be any valid path to a test file, of the format specified
in the design specification (U, RA, RP). Wildcards are allowed as are
multiple entries.

Output:
All output is sent to stdout, each domain fires off simulators for
there respective scheduling algoritms.