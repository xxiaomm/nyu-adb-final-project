import java.util.*;

// DM: site 1-10: stores the copies of variables
public class Site {
    static final int VARIABLE_NUM = 20; // total 20 variables

    int id;
    boolean failed;
    boolean recovered;
    int recoverTime;
    int lastFailTime;
    HashMap<Integer, List<Lock>> lockTable;     // <variable index, locks>
    HashMap<Integer, Lock> waitingLockTable;    // <variable index, lock>
    HashMap<Integer, List<Variable>> variableTable; // <variable index, versions of values>


    public Site(int id) {
        this.id = id;
        failed = false;
        recovered = false;
        recoverTime = -1;
        lastFailTime = -1;
        lockTable = new HashMap<>();
        waitingLockTable = new HashMap<>();

        variableTable = new HashMap<>();

        // odd index: 1 + index mod 10, even index: all sites
        for (int i = 1; i <= VARIABLE_NUM; i++) {
            if (i % 2 == 0) {
                Variable var = new Variable(-1, 10 * i);
                variableTable.put(i, new ArrayList<>());
                variableTable.get(i).add(var);
            } else {
                if (1 + i % 10 == id) {
                    Variable var = new Variable(-1, 10 * i);
                    variableTable.put(i, new ArrayList<>());
                    variableTable.get(i).add(var);
                }
            }
        }

    }

    public boolean canGetReadLock(int transId, int varIndex) {
        if (!lockTable.containsKey(varIndex) || lockTable.get(varIndex).size() == 0)
            return true;
        // someone is writing
        if (lockTable.get(varIndex).get(0).type == 'W')
            return false;
        return true;
    }

    public boolean canGetWriteLock(int transId, int varIndex) {
        if (!lockTable.containsKey(varIndex) || lockTable.get(varIndex).size() == 0)
            return true;
        // someone is writing
        if (lockTable.get(varIndex).get(0).type == 'W') {
            // this transaction has got 'W' lock
            if (lockTable.get(varIndex).get(0).transactionId ==transId)
                return false;
            return true;
        } else {    // all is reading
            List<Lock> locks = lockTable.get(varIndex);
            for (Lock lock: lockTable.get(varIndex)) {
                // other transaction is reading
                if (lock.transactionId != transId)
                    return false;
            }
            if (!waitingLockTable.containsKey(varIndex)
                    || waitingLockTable.get(varIndex).transactionId == transId)
                return true;
            return false;
        }
    }

    public void addReadLock(int transId, int time, int varIndex) {
        // do not have the lock of this variable
        if (!lockTable.containsKey(varIndex) || lockTable.get(varIndex).size() == 0) {
            lockTable.put(varIndex, new ArrayList<>());
            lockTable.get(varIndex).add(new Lock('R', transId, time));
        } else {
            // has write-lock
            if (lockTable.get(varIndex).get(0).type=='W' 
                    && lockTable.get(varIndex).get(0).transactionId == transId)
                return;

            for (Lock lock: lockTable.get(varIndex)) {
                if (lock.transactionId == transId)
                    return;
            }

            // add new lock to the first position
            lockTable.get(varIndex).add(0, new Lock('W', transId, time));
        }

    }

    public void addWriteLock(int transId, int time, int varIndex) {
        if (!lockTable.containsKey(varIndex) || lockTable.get(varIndex).size() == 0) {
            lockTable.put(varIndex, new ArrayList<>());
            lockTable.get(varIndex).add(new Lock('W', transId, time));
        } 
        // has write-lock
        if (lockTable.get(varIndex).get(0).type == 'W' 
                && lockTable.get(varIndex).get(0).transactionId == transId)
            return;

        // add new lock to the first position
        lockTable.get(varIndex).add(0, new Lock('W', transId, time));

        
    }

    public void addWaitingLock(int transId, int time, int varIndex) {
        if (!waitingLockTable.containsKey(varIndex)) 
            waitingLockTable.put(varIndex, new Lock('W', time, transId));
    }

    ///////////////////
    public int getWaitingId(int transId, int varIndex) {
        for (Lock lock: lockTable.get(varIndex)) {
            if (lock.transactionId != transId)
                return lock.transactionId;
        }
        return -1;
    }

    public void clearWaitingLock(int transId, int varIndex) {
        if (waitingLockTable.containsKey(varIndex)
                && waitingLockTable.get(varIndex).transactionId == transId)
            waitingLockTable.remove(varIndex);
    }


    // release all locks for the transaction
    public void releaseLock(int transId) {
        for (int index: lockTable.keySet()) {
            List<Lock> locks = lockTable.get(index);
            for (int i = 0; i < locks.size(); i++) {
                if (locks.get(i).transactionId == transId)
                    locks.remove(i--); // locks.get(i--) -- object
            }
        }
    }

    // update the new value of the variable at current site
    public void write(int value, int varIndex, int time) {
        variableTable.get(varIndex).add(new Variable(value, time));
    }

    // when the site fails, clear the site
    public void siteFail() {
        lockTable.clear();
        waitingLockTable.clear();;
        failed = true;
    }


    public void siteRecover(int time, int lastFailTime) {
        recoverTime = time;
        recovered = true;
        failed = false;
        this.lastFailTime = lastFailTime;
    }
}
