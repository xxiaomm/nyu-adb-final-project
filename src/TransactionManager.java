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

    public boolean createTransaction(int transId, boolean isRO) {
        if (!transactionTable.containsKey(transId)) {
            System.out.println("Create new Transaction: T"+ transId);
            if (isRO)
                System.out.println("Transaction T"+ transId+ " is read-only.");

            Transaction trans = new Transaction(transId, currentTime, isRO);

            transactionTable.put(transId, trans);
            return true;
        } else {
            System.out.println("Transaction "+transId +" existed.");
            return true;
        }
    }

    public boolean operationRead(int transId, int varIndex) {

        return true;
    }


}
