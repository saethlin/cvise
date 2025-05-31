import logging
import os
import shutil
import tempfile

from cvise.passes.abstract import AbstractPass, BinaryState, PassResult

class UnPubPass(AbstractPass):
    def check_prerequisites(self):
        return True

    def __count_instances(self, test_case):
        with open(test_case) as in_file:
            lines = in_file.readlines()
        return sum('pub' in line for line in lines)

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
            if 'pub ' in line:
                if state.index == nth:
                    data[l] = data[l].replace('pub ', '')
                    break
                nth += 1

        tmp = os.path.dirname(test_case)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, dir=tmp) as tmp_file:
            tmp_file.writelines(data)

        shutil.move(tmp_file.name, test_case)

        return (PassResult.OK, state)
