# -*- coding: utf-8 -*-

from pyloco import Task

class RunApp(Task):
    "execute an application"

    _name_ = "runapp"
    _version_ = "0.1.0"

    def __init__(self, parent):

        self.add_data_argument("data", type=str, help="input data")

        self.register_forward("data", type=str, help="output data")

    def perform(self, targs):

        output = targs.data

        self.add_forward(data=output)