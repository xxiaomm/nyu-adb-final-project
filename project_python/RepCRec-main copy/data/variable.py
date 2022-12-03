from collections import deque

from data.value import Value
# from errors import DataError


class Variable:
    def __init__(self, var_id: str, init_value: Value, is_replicated: bool):
        self.var_id = var_id
        self.is_readable = True
        self.not_committed_value = None
        self.is_replicated = is_replicated
        self.committed_value_list = deque([init_value])

    def get_last_committed_value(self):
        res = self.committed_value_list.popleft()
        self.committed_value_list.appendleft(res)
        return res.value

    def add_committed_value(self, v):
        self.committed_value_list.appendleft(v)

    def get_not_committed_value(self):
        if not self.not_committed_value:
            print("Variable {} has no not committed value.".format(self.var_id))
        else:
            return self.not_committed_value.value
