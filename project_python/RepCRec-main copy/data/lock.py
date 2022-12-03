from collections import deque
from enum import Enum

# Lock and Lock Manager definition

class LockType(Enum):
    R = 0,
    W = 1

# definition of lock, contains write-lock and read-lock
class Lock:
    def __init__(self, trans_id: str, var_id: str, lock_type: LockType) -> None:
        self.trans_id = trans_id  # transaction id
        self.var_id = var_id  # variable id
        self.lock_type = lock_type  # either R or W


class ReadLock(Lock):
    def __init__(self, trans_id: str, var_id: str) -> None:
        super(ReadLock, self).__init__(trans_id, var_id, LockType.R)



class WriteLock(Lock):
    def __init__(self, trans_id: str, var_id: str) -> None:
        super(WriteLock, self).__init__(trans_id, var_id, LockType.W)


# definition of Lock Manager

class LockManager:

    def __init__(self, var_id: str) -> None:

        self.var_id = var_id
        self.current_lock = None
        self.lock_queue = deque()       # block locks in the queue
        self.shared_read_lock = deque()  # Stores all the trans_id that are sharing the read lock, including current lock.

    # share read lock with other transactions
    def share_read_lock(self, trans_id: str):

        if self.current_lock.lock_type == LockType.R and trans_id not in self.shared_read_lock:
            self.shared_read_lock.append(trans_id)
        else:
            print("{}'s current lock on {} is a write lock, can not be shared.".format(self.current_lock.trans_id, self.current_lock.var_id))
 

    # promote read-lock to write-lock
    def promote_current_lock(self, write_lock: WriteLock) -> None:

        if not self.current_lock or len(self.shared_read_lock) != 1 or self.current_lock.lock_type != LockType.R or write_lock.trans_id not in self.shared_read_lock:
            print("ERROR: Can not promote lock.")

        # remove read lock from shared read lock queue, then promote it to a write lock
        self.shared_read_lock.remove(write_lock.trans_id)
        self.current_lock = write_lock
        print("Finish promotion, the current write lock is: ", self.current_lock)
        
           
    # release lock
    def release_lock(self, trans_id: str) -> None:

        if self.current_lock:
            if self.current_lock.lock_type == LockType.R:
                if trans_id in self.shared_read_lock:
                    self.shared_read_lock.remove(trans_id)
                if len(self.shared_read_lock) == 0:
                    self.current_lock = None
            else:
                if self.current_lock.trans_id == trans_id:
                    self.current_lock = None


    # blocked lock should be added to the queue
    def add_lock_to_queue(self, lock) -> None:

        for waited_lock in self.lock_queue:
            if waited_lock.trans_id == lock.trans_id:
                if waited_lock.lock_type == lock.lock_type or lock.lock_type == LockType.R:
                    return
        self.lock_queue.append(lock)


    # remove unbloked lock from the queue
    def remove_lock_from_queue(self, trans_id) -> None:
        self.lock_queue = deque()
        for lock in self.lock_queue:
            if lock.trans_id != trans_id:
                self.lock_queue.append(lock)


    def set_current_lock(self, lock):
        self.current_lock = lock
        if lock.lock_type == LockType.R:
            self.shared_read_lock.append(lock.trans_id)

    # check if there is a write lock in the queue
    def has_write_lock(self):
        for lock in self.lock_queue:
            if lock.lock_type == LockType.W:
                return True
        return False



    def has_other_write_lock(self, trans_id):
        for lock in self.lock_queue:
            if lock.lock_type == LockType.W and lock.trans_id != trans_id:
                return True
        return False

    # clear lock table
    def clear(self):
        self.current_lock = None
        self.lock_queue.clear()
        self.shared_read_lock.clear()



# R conlicts with W, W conflicts with R and W
def is_conflict(lock1, lock2) -> bool:
    if lock1.trans_id == lock2.trans_id:
        return False
    if lock1.lock_type == LockType.R and lock2.lock_type == LockType.R:
        return False

    return True


