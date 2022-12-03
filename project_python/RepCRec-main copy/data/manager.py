from collections import defaultdict

from data.lock import ReadLock, WriteLock, LockManager, LockType, is_conflict
from data.value import CommitValue, NotCommittedValue, ResultValue
from data.variable import Variable

VARIABLES_NUM = 20

class DataManager:

    def __init__(self, site_id: int) -> None:
        self.site_id = site_id  # site id: 1 - 10
        self.is_up = True  
        self.variables_table = defaultdict()  # all the variables stored in the site
        self.lock_table = defaultdict()  # lock managers for each variable
        self.failed_times = []  # record all the fail time of this site
        self.recover_times = []  # record all the recover time of this site

        # initialize variables
        # replicated value, even values: store in all sites
        # odd values: store in site  i mod 10 + 1
        for i in range(1, VARIABLES_NUM + 1):
            var_id = 'x{}'.format(i)
            # replicated / even value
            if i % 2 == 0:
                self.variables_table[var_id] = Variable(
                    var_id = var_id,
                    init = CommitValue(i * 10, 0),
                    is_replicated = True
                )
                # create lock table
                self.lock_table[var_id] = LockManager(var_id)
            # not replicated / odd value
            else:
                if self.site_id == i % 10 + 1:
                    self.variables_table[var_id] = Variable(
                        var_id = var_id,
                        init = CommitValue(i * 10, 0),
                        is_replicated = False
                    )
                # create lock table
                self.lock_table[var_id] = LockManager(var_id)


    def has_variable(self, var_id: str) -> bool:
        if var_id in self.variables_table:
            return True
        return False

    '''
    read replicated value from the site: If xi is replicated, RO can read xi from site s if xi was committed at s by some
    transaction T before RO began and s was up all the time between the time when xi was committed and RO began.
    '''
    # return the value for read-only operation
    def read_only(self, var_id: str, time: int) -> ResultValue:
        var = self.variables_table[var_id]
        if not var.is_readable:
            return ResultValue(None, False)
        else:
            for commit_value in var.commit_value_list:
                if commit_value.commit_time <= time:
                    if var.is_replicated:
                        # If the site wasn't up all the time between
                        # the time when xi was committed and RO began,
                        # then this RO can abort.
                        for t in self.failed_times:
                            if commit_value < t <= time:
                                return ResultValue(None, False)
                    return ResultValue(commit_value.value, True)
            return ResultValue(None, False)

    # def read_only(self, var_id: str, time: int) -> ResultValue:
    #     """Return the snapshot value for read-only transactions.
    #     """
    #     v = self.variables_table[var_id]
    #     if not var.is_readable:
    #         return ResultValue(None, False)
    #     else:
    #         for commit_value in var.commit_value_list:
    #             if commit_value.commit_time <= time:
    #                 if var.is_replicated:
    #                     # If the site wasn't up all the time between
    #                     # the time when xi was committed and RO began,
    #                     # then this RO can abort.
    #                     for t in self.failed_times:
    #                         if commit_value < t <= time:
    #                             return ResultValue(None, False)
    #                 return ResultValue(commit_value.value, True)
    #         return ResultValue(None, False)

    def read(self, trans_id: str, var_id: str) -> ResultValue:
        var = self.variables_table[var_id]
        if not var.is_readable:
            print('{} failed to read {}.{} [Site just recovered, not readable]'.format(trans_id, var_id, self.site_id))
            return ResultValue(None, False)
        else:
            lock_manager = self.lock_table[var_id]
            current_lock = lock_manager.current_lock

            # If there's no lock on the variable, set a read lock then read directly.
            if not current_lock:
                lock_manager.set_current_lock(ReadLock(trans_id, var_id))
                return ResultValue(var.get_last_commit_value(), True)

            # There is a read lock on the variable.
            if current_lock.lock_type == LockType.R:
                # If the transaction shares the read lock, then it can read the variable.
                if trans_id in lock_manager.shared_read_lock:
                    return ResultValue(var.get_last_commit_value(), True)
                else:
                    # The transaction doesn't share the read lock, and there are other write
                    # locks waiting in front, so the read lock should wait in queue.
                    if lock_manager.has_write_lock():
                        lock_manager.add_lock_to_queue(ReadLock(trans_id, var_id))
                        print('{} failed to read {}.{} [Exist write locks waiting in front]'.format(trans_id, var_id, self.site_id))
                        return ResultValue(None, False)
                    else:
                        # There is no other write locks waiting, then share the current read lock
                        # and return the read value.
                        lock_manager.share_current_lock(trans_id)
                        return ResultValue(var.get_last_commit_value(), True)

            # There is a write lock on the variable.
            else:
                # If current transaction has already held a write lock on variable, then it
                # will read the temporary value for the write has not been committed.
                if trans_id == current_lock.trans_id:
                    return ResultValue(var.get_not_committed_value(), True)
                else:
                    lock_manager.add_lock_to_queue(ReadLock(trans_id, var_id))
                    print('{} failed to read {}.{} [Lock conflict]'.format(trans_id, var_id, self.site_id))
                    return ResultValue(None, False)


    def can_get_write_lock(self, trans_id, var_id) -> bool:
        lock_manager = self.lock_table.get(var_id)
        current_lock = lock_manager.current_lock

        if current_lock:
            if current_lock.lock_type == LockType.R:
                if len(lock_manager.shared_read_lock) != 1:
                    lock_manager.add_lock_to_queue(WriteLock(trans_id, var_id))
                    return False
                else:
                    if trans_id in lock_manager.shared_read_lock and not lock_manager.has_other_write_lock(trans_id):
                        return True
                    else:
                        lock_manager.add_lock_to_queue(WriteLock(trans_id, var_id))
                        return False
            else:
                # There are other transactions holding the write lock.
                if current_lock.trans_id == trans_id:
                    return True
                else:
                    lock_manager.add_lock_to_queue(WriteLock(trans_id, var_id))
                    return False
        return True

    # write variable
    def write(self, trans_id, var_id, value) -> None:

        lock_manager = self.lock_table.get(var_id)
        var = self.variables_table.get(var_id)
        assert lock_manager is not None and v is not None
        current_lock = lock_manager.current_lock
        if current_lock:
            if current_lock.lock_type == LockType.R:
                # If current lock is a read lock, then it must be of the same transaction,
                # and there should be no other locks waiting in queue.
                assert len(lock_manager.shared_read_lock) == 1 and \
                       trans_id in lock_manager.shared_read_lock and \
                       not lock_manager.has_other_write_lock(trans_id)
                lock_manager.promote_current_lock(WriteLock(trans_id, var_id))
                var.not_committed_value = NotCommittedValue(value, trans_id)
            else:
                # If current lock is a write lock, then it must of the same transaction.
                assert trans_id == current_lock.trans_id
                var.not_committed_value = NotCommittedValue(value, trans_id)
        else:
            lock_manager.set_current_lock(WriteLock(trans_id, var_id))
            var.not_committed_value = NotCommittedValue(value, trans_id)

    def dump(self):
        if self.is_up:
            site_status = 'up'  
        else:
            site_status = 'down'
        output = 'site {} is {}: '.format(self.site_id, site_status)
        for var in self.variables_table.values():
            output += '{}: {}, '.format(var.var_id, var.get_last_commit_value())
        print(output)

    # younger transaction aborts if deadlock
    def abort(self, trans_id):
        for lock_manager in self.lock_table.values():
            lock_manager. release_lock(trans_id)
            lock_manager.remove_lock_from_queue(trans_id)
        self.update_lock_table()

    # commit transaction
    def commit(self, trans_id, commit_time):
        # Release locks.
        for lock_manager in self.lock_table.values():
            lock_manager. release_lock(trans_id)

        # Commit temporary values.
        for var in self.variables_table.values():
            if var.not_committed_value is not None and var.not_committed_value.trans_id == trans_id:
                commit_value = var.not_committed_value.value
                var.add_commit_value(CommitValue(commit_value, commit_time))
                var.not_committed_value = None
                var.is_readable = True
        self.update_lock_table()

    def update_lock_table(self):
        for lock_manager in [x for x in self.lock_table.values() if not x.current_lock]:
            if len(lock_manager.lock_queue) == 0:
                continue
            first_waiting = lock_manager.lock_queue.popleft()

            lock_manager.set_current_lock(first_waiting)
            if first_waiting.lock_type == LockType.R and lock_manager.lock_queue:
                # If multiple read locks are blocked before a write lock, then
                # pop these read locks out of the queue and make them share the read lock.
                next_lock = lock_manager.lock_queue.popleft()
                while next_lock.lock_type == LockType.R and lock_manager.lock_queue:
                    lock_manager.shared_read_lock.add(next_lock.trans_id)
                    next_lock = lock_manager.lock_queue.popleft()
                lock_manager.lock_queue.appendleft(next_lock)

                # If the current lock is a read lock, and the next lock is the write lock
                # of the same transaction, then promote the current read lock.
                if len(lock_manager.shared_read_lock) == 1 and \
                        next_lock.trans_id == lock_manager.shared_read_lock[0]:
                    lock_manager.promote_current_lock(WriteLock(next_lock.trans_id, lock_manager.var_id))
                    lock_manager.lock_queue.popleft()

    # the site fails
    def fail(self, time: int) -> None:
        self.is_up = False
        self.failed_times.append(time)
        for lock_manager in self.lock_table.values():
            lock_manager.clear()

    # recover the site
    def recover(self, time: int) -> None:
        self.is_up = True
        self.recover_times.append(time)
        for var in self.variables_table.values():
            if var.is_replicated:
                var.is_readable = False


    def generate_blocking_graph(self) -> defaultdict:
        blocking_graph = defaultdict(set)
        for lock_manager in self.lock_table.values():
            if not lock_manager.current_lock or len(lock_manager.lock_queue) == 0:
                continue

            # Generate lock graph for the current lock with other locks in queue.
            current_lock = lock_manager.current_lock
            for lock in lock_manager.lock_queue:
                if is_conflict(current_lock, lock):
                    if current_lock.lock_type == LockType.R:
                        for shared_lock_trans_id in [x for x in lock_manager.shared_read_lock
                                                if not (x == lock.trans_id)]:
                            blocking_graph[lock.trans_id].add(shared_lock_trans_id)
                    else:
                        blocking_graph[lock.trans_id].add(current_lock.trans_id)

            # Generate lock graph for the locks in queue with each other.
            for i in range(len(lock_manager.lock_queue)):
                lock1 = lock_manager.lock_queue[i]
                for j in range(i):
                    lock2 = lock_manager.lock_queue[j]
                    if is_conflict(lock2, lock1):
                        blocking_graph[lock1.trans_id].add(lock2.trans_id)
        return blocking_graph
