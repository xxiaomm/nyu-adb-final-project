import java.util.*;
public class Transaction {
    int id;
    int startTime;
    boolean isRO; // read only;
    boolean aborted;
    boolean blocked;

    int transWaitingFor;

    HashMap<Integer, Integer> buffer;
    HashSet<Integer> visitedSites;
    HashMap<Integer, LinkedList<Integer>> sites;

    public Transaction(int transId, int startTime, boolean isRO) {
        this.id = transId;
        this.startTime = startTime;
        this.isRO = isRO;
        transWaitingFor = -1;
        buffer = new HashMap<>();
        visitedSites = new HashSet<>();
        sites = new HashMap<>();
    }

}
