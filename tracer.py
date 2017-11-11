# -*- coding: utf-8 -*-
"""
Generate sequence diagrams text input for js sequence diagrams tool [1] from execution trace.

Each call is intercept and stored to generate a listing of calls. Objects are named from their
class name and a unique index.

usage :

    #Create a tracer
    t = Tracer()
    
    #start intercepting
    t.start()

    #Do some stuff    

    #stop intercepting
    t.stop()

    #dump result to the standard output
    t.dump()

Complete example in the __main__ section

Copyright 2017 Youen Péron

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Youen Péron

[1] https://bramp.github.io/js-sequence-diagrams/

"""
import sys

class NamedObject(object):
    named_objects = dict()

    def __init__(self, unnamed_object):
        self.unnamed_object = unnamed_object
        class_name = self.unnamed_object.__class__.__name__

        if class_name not in self.named_objects:
            self.named_objects[class_name] = {}

        if self.unnamed_object not in self.named_objects[class_name]:
            self.named_objects[class_name][self.unnamed_object] = len(self.named_objects[class_name])

        self.index =  self.named_objects[class_name][self.unnamed_object]


    def __repr__(self):
        return '%s[%s]' % ( 
            self.unnamed_object.__class__.__name__,
            self.index,
        )

class Call(object):

    def __init__(self, frame):

        self.frame = frame
    
    def get_caller(self):

        f_locals_caller = self.frame.f_back.f_locals
        if f_locals_caller.get('self') is None:
            print(f_locals_caller)
        return NamedObject(f_locals_caller.get('self'))

    def get_target(self):
        f_locals = self.frame.f_locals
        return NamedObject(f_locals.get('self'))

    def get_func_name(self):
        
        return self.frame.f_code.co_name


    def __repr__(self):

        return "%s -> %s : %s" % (self.get_caller(), self.get_target(),  self.get_func_name() )
    
class Return(object):

    def __init__(self, call):
        self.call = call

    def __repr__(self):

        return "%s --> %s:" % (self.call.get_target(), self.call.get_caller())

class Tracer(object):
    def __init__(self):

        self.calls = []
        self.traces = []



    def trace_call(self, frame, event, arg):
        if event != 'call':
            return
        caller = frame.f_back
        if caller is not None:
            self.push_call(Call(frame))

        return self.trace_return
        
    def trace_return(self, frame, event, arg):
        if event == 'return':
            self.pop_call()

    def pop_call(self):
        call = self.calls.pop()
        self.traces.append(Return(call))

    def push_call(self, call):
        self.calls.append(call)
        self.traces.append(call)

    def start(self):
        sys.settrace(self.trace_call)

    def stop(self):
        sys.settrace(None)
        self.traces.pop()

    def dump(self):
        for trace in self.traces:
            print(trace)



if __name__ == '__main__' :


    class Car(object):

        def __init__(self, key):

            self.__key = key
            self.__started = False

        def start(self, key, driver):
            self.__started = self.__started or key == key
            driver.check_eyes()
            driver.sun_glasses()
            driver.open_window()
            return self.__started
    
    class Driver(object):

        def __init__(self):

            self.__driving = False

        def go(self, car, key):
            self.__driving = car.start(key, self)
            car.start(key, self)
            self.check_eyes()
            Car(key).start(key, self)

        def check_eyes(self):
            return True

        @staticmethod
        def sun_glasses():
            pass

        @classmethod
        def open_window(cls):
            pass

    
    t = Tracer()
    
    t.start()
    key = "red"

    car = Car(key)

    driver = Driver() 


    Driver.sun_glasses()

    driver.go(car, key)

    

    t.stop()

    t.dump()
    # NoneType[0] -> Car[0] : __init__
    # Car[0] --> NoneType[0]:
    # NoneType[0] -> Driver[0] : __init__
    # Driver[0] --> NoneType[0]:
    # NoneType[0] -> Driver[0] : go
    # Driver[0] -> Car[0] : start
    # Car[0] -> Driver[0] : check_eyes
    # Driver[0] --> Car[0]:
    # Car[0] --> Driver[0]:
    # Driver[0] -> Car[0] : start
    # Car[0] -> Driver[0] : check_eyes
    # Driver[0] --> Car[0]:
    # Car[0] --> Driver[0]:
    # Driver[0] -> Driver[0] : check_eyes
    # Driver[0] --> Driver[0]:
    # Driver[0] -> Car[1] : __init__
    # Car[1] --> Driver[0]:
    # Driver[0] -> Car[1] : start
    # Car[1] -> Driver[0] : check_eyes
    # Driver[0] --> Car[1]:
    # Car[1] --> Driver[0]:
    # Driver[0] --> NoneType[0]:

        
