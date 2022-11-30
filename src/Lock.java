public class Lock {
    char type; // write / read lock
    int transactionId;
    int startTime; // the time that a transaction gets the lock
    int siteId; // the id of target site - stores copies

    public Lock(char type, int transactionId, int startTime) {
        this.type = type;
        this.transactionId = transactionId;
        this.startTime = startTime;
    }

}
