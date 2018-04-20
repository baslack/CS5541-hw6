from typing import *
from collections import deque
from copy import deepcopy


class Task:
    def __init__(self, name: str, arrival: int, estimated: int, priority: int = 0):
        self.name: str = name
        self.arrival: int = arrival
        self.estimated: int = estimated
        self.priority: int = priority
        self.started: Union[int, None] = None
        self.stopped: Union[int, None] = None
        self.remaining: int = estimated
        self.completed: Union[int, None] = None
        self.serviced: Union[int, None] = None
        self.waited: int = 0

    def service(self, ticks: int):
        self.remaining -= ticks

    def wait(self, ticks: int):
        self.waited += ticks

    def is_done(self) -> bool:
        return self.remaining <= 0


class RealtimeTask(Task):
    def __init__(self,
                 name: str,
                 arrival: int,
                 estimated: int,
                 start_dln: Optional[int] = None,
                 end_dln: Optional[int] = None):
        super(RealtimeTask, self).__init__(name, arrival, estimated)
        self.start_dln: Optional[int] = start_dln
        self.end_dln: Optional[int] = end_dln
        self.missed: bool = False

    def miss_check(self, time: int) -> None:
        if self.start_dln is not None:
            if time > self.start_dln and self.started is None:
                self.missed = True
        if self.end_dln is not None:
            if time >= self.end_dln and self.remaining:
                self.missed = True

    def is_done(self) -> bool:
        return self.missed or super(RealtimeTask, self).is_done()


class Simulator:
    def __init__(self, tasks: List[Task]):
        self.tasks: List[Task] = tasks

    def all_done(self) -> bool:
        done: bool = True
        for this_task in self.tasks:
            done = done and this_task.is_done()
        return done

    def run(self):
        pass


class FCFS(Simulator):
    def __init__(self, tasks: List[Task]):
        super(FCFS, self).__init__(tasks)
        self.tasks.sort(key=lambda x: x.arrival)
        self.ready: Deque[Task] = deque(tasks)
        self.running: Optional[Task] = None

    def run(self):
        print("FCFS:")
        clk: int = 0
        while self.ready:
            self.running = self.ready.popleft()
            self.running.started = clk
            clk += self.running.estimated
            self.running.completed = clk
            # clk += 1
            print("{}:{}->{}".format(self.running.name,
                                     self.running.started,
                                     self.running.completed))


class RR(Simulator):
    def __init__(self, tasks: List[Task], quantum: int):
        super(RR, self).__init__(tasks)
        self.ready: Deque[Task] = deque()
        self.running: Optional[Task] = None
        self.quantum: int = quantum

    def run(self):
        print("RR:")
        clk: int = 0
        time_slice: int = 0
        while not self.all_done():
            for this_task in self.tasks:
                if this_task.arrival == clk:
                    self.ready.append(this_task)
            if self.running is None and len(self.ready):
                self.running = self.ready.popleft()
                self.running.started = clk
            elif self.running is not None:
                self.running.service(1)
                time_slice += 1
                if self.running.is_done():
                    self.running.completed = clk
                    print("{}:{}->{}".format(self.running.name,
                                             self.running.started,
                                             self.running.completed))
                    if len(self.ready):
                        self.running = self.ready.popleft()
                        self.running.started = clk
                    else:
                        self.running = None
                    time_slice = 0
                elif time_slice == self.quantum:
                    self.running.stopped = clk
                    print("{}:{}->{}".format(self.running.name,
                                             self.running.started,
                                             self.running.stopped))
                    self.ready.append(self.running)
                    self.running = self.ready.popleft()
                    self.running.started = clk
                    time_slice = 0
            clk += 1


class SPN(Simulator):
    def __init__(self, tasks: List[Task]):
        super(SPN, self).__init__(tasks)
        self.ready: List[Task] = list()
        self.running: Optional[Task] = None

    def run(self):
        print("SPN:")
        clk = 0
        while not self.all_done():
            for this_task in self.tasks:
                if this_task.arrival == clk:
                    self.ready.append(this_task)
            self.ready.sort(key=lambda x: x.estimated, reverse=True)
            if self.running is None and len(self.ready):
                self.running = self.ready.pop()
                self.running.started = clk
            else:  #running not Node
                self.running.service(1)
                if self.running.is_done():
                    self.running.completed = clk
                    print("{}:{}->{}".format(self.running.name,
                                             self.running.started,
                                             self.running.completed))
                    if len(self.ready):
                        self.running = self.ready.pop()
                        self.running.started = clk
                    else:
                        self.running = None
            clk += 1


class SRT(Simulator):
    def __init__(self, tasks: List[Task]):
        super(SRT, self).__init__(tasks)
        self.ready: List[Task] = list()
        self.running: Optional[Task] = None

    def run(self):
        print("SRT")
        clk = 0
        while not self.all_done():
            for this_task in self.tasks:
                if this_task.arrival == clk:
                    self.ready.append(this_task)
            self.ready.sort(key=lambda x: x.remaining, reverse=True)
            if self.running is None and len(self.ready):
                self.running = self.ready[-1]
                self.running.started = clk
            elif self.running is not None:
                self.running.service(1)
                if self.running.is_done():
                    self.running.completed = clk
                    self.ready.remove(self.running)
                    print("{}:{}->{}".format(self.running.name,
                                             self.running.started,
                                             self.running.completed))
                    if len(self.ready):
                        self.running = self.ready[-1]
                        self.running.started = clk
                    else:
                        self.running = None
                elif self.running != self.ready[-1]:
                    self.running.stopped = clk
                    print("{}:{}->{}".format(self.running.name,
                                             self.running.started,
                                             self.running.stopped))
                    self.running = self.ready[-1]
                    self.running.started = clk
            clk += 1


class HRRN(Simulator):
    def __init__(self, tasks: List[Task]):
        super(HRRN, self).__init__(tasks)
        self.ready: List[Task] = list()
        self.running: Optional[Task] = None

    def run(self):
        print("HRRN:")
        clk = 0
        while not self.all_done():
            for this_task in self.tasks:
                if this_task.arrival == clk:
                    self.ready.append(this_task)
            self.ready.sort(key=lambda x: (x.waited + x.estimated) / x.estimated)
            if self.running is None and len(self.ready):
                self.running = self.ready.pop()
                self.running.started = clk
            elif self.running is not None:
                self.running.service(1)
                for this_task in self.ready:
                    if this_task != self.running:
                        this_task.wait(1)
                self.ready.sort(key=lambda x: (x.waited + x.estimated) / x.estimated)
                if self.running.is_done():
                    self.running.completed = clk
                    print("{}:{}->{}".format(self.running.name,
                                             self.running.started,
                                             self.running.completed))
                    if len(self.ready):
                        self.running = self.ready.pop()
                        self.running.started = clk
                    else:
                        self.running = None
            clk += 1


class ED(Simulator):
    def __init__(self, tasks: List[RealtimeTask]):
        self.tasks: List[RealtimeTask] = tasks
        self.ready: List[RealtimeTask] = list()
        self.running: Optional[RealtimeTask] = None
        self.missed: List[RealtimeTask] = list()

    def run(self):
        print("ED:")
        clk = 0
        while not self.all_done():
            for this_task in self.tasks:
                if this_task.arrival == clk:
                    self.ready.append(this_task)
            if len(self.ready):
                for this_task in self.ready:
                    this_task.miss_check(clk)
                    if this_task.missed:
                        self.ready.remove(this_task)
                        # print("{}:Missed".format(this_task.name))
                        self.missed.append(this_task)
            self.ready.sort(key=lambda x: x.start_dln, reverse=True)
            if self.running is None and len(self.ready):
                self.running = self.ready.pop()
                self.running.started = clk
            elif self.running is not None:
                self.running.service(1)
                if self.running.is_done():
                    self.running.completed = clk
                    print("{}:{}->{}".format(self.running.name,
                                             self.running.started,
                                             self.running.completed))
                    while len(self.missed):
                        print("{}:Missed".format(self.missed.pop().name))
                    if len(self.ready):
                        self.running = self.ready.pop()
                        self.running.started = clk
                    else:
                        self.running = None
            clk += 1


class EDUI(Simulator):
    def __init__(self, tasks: List[RealtimeTask], idle_allowed: int = 20):
        self.tasks: List[RealtimeTask] = tasks
        self.idle_allowed: int = idle_allowed
        self.ready: List[RealtimeTask] = list()
        self.running: Optional[RealtimeTask] = None
        self.missed: List[RealtimeTask] = list()

    def run(self):
        print("EDUI:")
        clk = 0
        idle = 0
        while not self.all_done():
            for this_task in self.tasks:
                if this_task.arrival == clk:
                    self.ready.append(this_task)
            if len(self.ready):
                for this_task in self.ready:
                    this_task.miss_check(clk)
                    if this_task.missed:
                        # print("{}:Missed".format(this_task.name))
                        self.ready.remove(this_task)
                        self.missed.append(this_task)
            self.ready.sort(key=lambda x: x.start_dln, reverse=True)
            if self.running is None and idle > self.idle_allowed and len(self.ready):
                self.running = self.ready.pop()
                self.running.started = clk
                idle = 0
            elif self.running is None and len(self.ready):
                self.ready.reverse()
                for this_task in self.ready:
                    if this_task.start_dln == clk:
                        self.running = this_task
                        break
                if self.running is not None:
                    self.running.started = clk
                    self.ready.remove(self.running)
                    idle = 0
            elif self.running is not None:
                self.running.service(1)
                idle = 0
                if self.running.is_done():
                    self.running.completed = clk
                    print("{}:{}->{}".format(self.running.name,
                                             self.running.started,
                                             self.running.completed))
                    while len(self.missed):
                        print("{}:Missed".format(self.missed.pop().name))
                    if len(self.ready):
                        self.running = self.ready.pop()
                        self.running.started = clk
                    else:
                        self.running = None
            else:
                idle += 1
            clk += 1


class RFCSC(Simulator):
    def __init__(self, tasks: List[RealtimeTask]):
        self.tasks: List[RealtimeTask] = tasks
        self.ready: Deque[RealtimeTask] = deque()
        self.running: Optional[RealtimeTask] = None
        self.missed: List[RealtimeTask] = list()

    def run(self):
        print("RFCSC:")
        clk = 0
        while not self.all_done():
            for this_task in self.tasks:
                if this_task.arrival == clk:
                    self.ready.append(this_task)
            for this_task in self.ready:
                this_task.miss_check(clk)
                if this_task.missed:
                    self.missed.append(this_task)
            temp = deque()
            for this_task in self.ready:
                if not this_task.missed:
                    temp.append(this_task)
            self.ready = temp
            if self.running is None and len(self.ready):
                self.running = self.ready.popleft()
                self.running.started = clk
            elif self.running is not None:
                self.running.service(1)
                if self.running.is_done():
                    self.running.completed = clk
                    print("{}:{}->{}".format(self.running.name,
                                             self.running.started,
                                             self.running.completed))
                    while len(self.missed):
                        print("{}:Missed".format(self.missed.pop().name))
                    if len(self.ready):
                        self.running = self.ready.popleft()
                        self.running.started = clk
                    else:
                        self.running = None
            clk += 1


class FP(Simulator):
    def __init__(self, tasks: List[RealtimeTask], end: int = 100):
        self.tasks: List[RealtimeTask] = tasks
        self.end: int = end
        for this_task in self.tasks:
            this_task.priority = self.tasks.index(this_task)
        self.task_indexes: Dict[str, int] = dict()
        for this_task in self.tasks:
            self.task_indexes[this_task.name] = 1
        self.ready: List[RealtimeTask] = list()
        self.running: Optional[RealtimeTask] = None
        self.missed: List[RealtimeTask] = list()

    def run(self):
        print("FP:")
        clk = 0
        while not clk > self.end:
            #spawn new task
            for this_task in self.tasks:
                if clk % this_task.end_dln == this_task.arrival:
                    new_task = deepcopy(this_task)
                    new_task.name = this_task.name + "({})".format(self.task_indexes[this_task.name])
                    new_task.end_dln = this_task.end_dln * self.task_indexes[this_task.name]
                    self.task_indexes[this_task.name] += 1
                    self.ready.append(new_task)
            for this_task in self.ready:
                this_task.miss_check(clk)
                if this_task.missed:
                    # print("{}:Missed".format(this_task.name))
                    self.missed.append(this_task)
                    self.ready.remove(this_task)
            self.ready.sort(key=lambda x: x.priority, reverse=True)
            if self.running is None and len(self.ready):
                self.running = self.ready.pop()
                self.running.started = clk
            elif self.running is not None:
                self.running.service(1)
                if len(self.ready):
                    if self.running.priority > self.ready[-1].priority:
                        self.running.stopped = clk
                        print("{}:{}->{}".format(self.running.name,
                                                 self.running.started,
                                                 self.running.stopped))
                        while len(self.missed):
                            print("{}:Missed".format(self.missed.pop().name))
                        temp = self.ready.pop()
                        self.ready.append(self.running)
                        self.running = temp
                        self.running.started = clk
                if self.running.is_done():
                    self.running.completed = clk
                    print("{}:{}->{}".format(self.running.name,
                                             self.running.started,
                                             self.running.completed))
                    while len(self.missed):
                        print("{}:Missed".format(self.missed.pop().name))
                    if len(self.ready):
                        self.running = self.ready.pop()
                        self.running.started = clk
                    else:
                        self.running = None
            clk += 1


class EDCD(Simulator):
    def __init__(self, tasks: List[RealtimeTask], end: int):
        self.tasks: List[RealtimeTask] = tasks
        self.end: int = end
        self.task_indexes: Dict[str, int] = dict()
        for this_task in self.tasks:
            self.task_indexes[this_task.name] = 1
        self.ready: List[RealtimeTask] = list()
        self.running: Optional[RealtimeTask] = None
        self.missed: List[RealtimeTask] = list()

    def run(self):
        print("EDCD:")
        clk = 0
        while not clk > self.end:
            #spawn new tasks
            for this_task in self.tasks:
                if clk % this_task.end_dln == this_task.arrival:
                    new_task = deepcopy(this_task)
                    new_task.name = this_task.name + "({})".format(self.task_indexes[this_task.name])
                    new_task.end_dln = this_task.end_dln * self.task_indexes[this_task.name]
                    self.task_indexes[this_task.name] += 1
                    self.ready.append(new_task)
            #check for misses
            for this_task in self.ready:
                this_task.miss_check(clk)
                if this_task.missed:
                    # print("{}:Missed".format(this_task.name))
                    self.missed.append(this_task)
                    self.ready.remove(this_task)
            # sort ready que by end dealine
            self.ready.sort(key=lambda x: x.end_dln, reverse=True)
            # if not running and ready queue, get a task
            if self.running is None and len(self.ready):
                self.running = self.ready.pop()
                self.running.started = clk
            # if is runnung, service it (from last clk tick)
            elif self.running is not None:
                self.running.service(1)
                # if done, print
                if self.running.is_done():
                    self.running.completed = clk
                    print("{}:{}->{}".format(self.running.name,
                                             self.running.started,
                                             self.running.completed))
                    # print any misses
                    while len(self.missed):
                        print("{}:Missed".format(self.missed.pop().name))
                    # more in the ready queue? add it
                    if len(self.ready):
                        self.running = self.ready.pop()
                        self.running.started = clk
                    else:
                        self.running = None
                # not done, check the deadline
                else:
                    if len(self.ready):
                        if self.running.end_dln > self.ready[-1].end_dln:
                            self.running.stopped = clk
                            print("{}:{}->{}".format(self.running.name,
                                                     self.running.started,
                                                     self.running.stopped))
                            while len(self.missed):
                                print("{}:Missed".format(self.missed.pop().name))
                            temp = self.ready.pop()
                            self.ready.append(self.running)
                            self.running = temp
                            self.running.started = clk
            clk += 1
