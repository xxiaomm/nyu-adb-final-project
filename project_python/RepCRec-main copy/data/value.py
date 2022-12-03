class Value:
    def __init__(self, value):
        self.value = value


class NotCommittedValue(Value):
    def __init__(self, value, trans_id):
        super(NotCommittedValue, self).__init__(value)
        self.trans_id = trans_id


class CommitValue(Value):
    def __init__(self, value, time_to_commit: int):
        super(CommitValue, self).__init__(value)
        self.time_to_commit = time_to_commit


class ResultValue(Value):
    def __init__(self, value, is_success: bool):
        super(ResultValue, self).__init__(value)
        self.is_success = is_success
