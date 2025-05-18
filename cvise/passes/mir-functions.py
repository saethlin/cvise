import logging
import os
import shutil
import tempfile
import re

from cvise.passes.abstract import AbstractPass, BinaryState, PassResult

regex = re.compile(r'Call\(.*?ReturnTo\((\w+)\)\s*,\s*UnwindUnreachable\(\)\s*\)')
def call_to_goto(line):
    m = regex.search(line)
    return r"Goto({})".format(m.group(1))

class MirFunctionsPass(AbstractPass):
    def check_prerequisites(self):
        return True

    def __count_instances(self, test_case):
        with open(test_case) as in_file:
            lines = in_file.readlines()
        return sum(1 for c in lines if "Call(" in c)

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

        nth = 0
        for l,line in enumerate(data):
            if "Call(" in line:
                if state.index == nth:
                    if self.arg == "Return":
                        data[l] = "Return()"
                    else:
                        data[l] = call_to_goto(line)
                    break
                nth += 1

        tmp = os.path.dirname(test_case)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, dir=tmp) as tmp_file:
            tmp_file.writelines(data)

        shutil.move(tmp_file.name, test_case)

        return (PassResult.OK, state)
