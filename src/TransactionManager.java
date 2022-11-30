import java.util.*;
public class TransactionManager {
    int currentTime;
    DataManager dataManager;
    HashMap<Integer,Transaction> transactionTable; // <transId, Transactions>

    public TransactionManager() {
        currentTime = 0;
        dataManager = new DataManager();
        transactionTable = new HashMap<>();
    }



}
