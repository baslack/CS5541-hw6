from support import *
import argparse
import os
import sys


def perror(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform Scheduling Simulation of given task file")
    parser.add_argument("files", nargs="+", help="lists of file paths to be processed")
    args = parser.parse_args()

    filepaths = [os.path.abspath(os.path.expanduser(filepath)) for filepath in args.files]

    for filepath in filepaths:
        if not os.path.exists(filepath):
            perror("schedule: {} doesn't exist\n".format(filepath))
            continue
        with open(filepath, "r") as f:
            first = f.readline().rstrip("\n")
            tokens = first.split(",")
            for token in tokens:
                token = token.strip(" ").rstrip(" ")
            type_schedule = tokens[0]
            if type_schedule == "U":
                number_of_processes = int(tokens[1])
                RR_quantum = int(tokens[2])
                tasks: List[Task] = list()
                lines = f.readlines()
                for line in lines:
                    line.rstrip("\n")
                    tokens = line.split(",")
                    for token in tokens:
                        token = token.strip(" ").rstrip(" ")
                    name = tokens[0]
                    arrival = int(tokens[1])
                    service_time = int(tokens[2])
                    tasks.append(Task(name, arrival, service_time))
                FCFS(deepcopy(tasks)).run()
                print("")
                RR(deepcopy(tasks), RR_quantum).run()
                print("")
                SPN(deepcopy(tasks)).run()
                print("")
                SRT(deepcopy(tasks)).run()
                print("")
                HRRN(deepcopy(tasks)).run()
                print("")
            elif type_schedule == "RA":
                number_of_processes = int(tokens[1])
                tasks: List[RealtimeTask] = list()
                lines = f.readlines()
                for line in lines:
                    line.rstrip("\n")
                    tokens = line.split(",")
                    for token in tokens:
                        token = token.strip(" ").rstrip(" ")
                    name = tokens[0]
                    arrival = int(tokens[1])
                    execution_time = int(tokens[2])
                    starting_deadline = int(tokens[3])
                    tasks.append(RealtimeTask(name, arrival, execution_time, starting_deadline))
                ED(deepcopy(tasks)).run()
                print("")
                EDUI(deepcopy(tasks)).run()
                print("")
                RFCSC(deepcopy(tasks)).run()
                print("")
            else:  # RP
                number_of_processes = int(tokens[1])
                ending_time = int(tokens[2])
                tasks: List[RealtimeTask] = list()
                lines = f.readlines()
                for line in lines:
                    line.rstrip("\n")
                    tokens = line.split(",")
                    for token in tokens:
                        token = token.strip(" ").rstrip(" ")
                    name = tokens[0]
                    arrival = int(tokens[1])
                    execution_time = int(tokens[2])
                    ending_deadline = int(tokens[3])
                    tasks.append(RealtimeTask(name, arrival, execution_time, end_dln=ending_deadline))
                FP(deepcopy(tasks), ending_time).run()
                print("")
                EDCD(deepcopy(tasks), ending_time).run()
                print("")
