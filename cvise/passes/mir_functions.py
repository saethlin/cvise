import logging
import os
import shutil
import tempfile
import re

from cvise.passes.abstract import AbstractPass, BinaryState, PassResult

class MirFunctionsPass(AbstractPass):
    def check_prerequisites(self):
        return True

    def __count_instances(self, test_case):
        with open(test_case) as in_file:
            lines = in_file.readlines()
        return sum('fn ' in line for line in lines)

    def new(self, test_case, check_sanity=None):
        instances = self.__count_instances(test_case)
        return BinaryState.create(instances)

    def advance(self, test_case, state):
        return state.advance()

    def advance_on_success(self, test_case, state):
        return state.advance_on_success(self.__count_instances(test_case))

    def transform(self, test_case, state, process_event_notifier):
        with open(test_case) as in_file:
            data = in_file.readlines()

        first_line_to_remove = 0
        nth = 0
        for l,line in enumerate(data):
            data[l] = line.strip()
            if data[l].startswith("fn "):
                if state.index == nth:
                    start = l
                    end = l
                    while !data[end].startswith("fn "):
                        end += 1
                    break
                nth += 1

        tmp = os.path.dirname(test_case)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, dir=tmp) as tmp_file:
            tmp_file.writelines(data)

        shutil.move(tmp_file.name, test_case)

        return (PassResult.OK, state)
