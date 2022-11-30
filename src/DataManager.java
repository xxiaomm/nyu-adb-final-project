import java.util.*;
public class DataManager {
    static final int SITE_NUM = 10; // total number of sites is 10
    HashMap<Integer, Site> siteTable;
    HashMap<Integer, Boolean> failedSites;  // if failed: true
    HashMap<Integer, List<Integer>> siteFailTimes;  // <siteId, all failed times>

    public DataManager() {
        siteTable = new HashMap<>();
        failedSites = new HashMap<>();
        siteFailTimes = new HashMap<>();
        for (int i = 1; i <= SITE_NUM; i++) {
            siteTable.put(i, new Site(i));
            failedSites.put(i, false);
            siteFailTimes.put(i, new ArrayList<>());
            siteFailTimes.get(i).add(-1);
        }
    }

    public int nonReplicatedRO(int siteId, int varIndex, int time) {
        Site site = siteTable.get(siteId);
        List<Variable> history = site.variableTable.get(varIndex);
        for (int i = history.size() - 1; i >= 0; i--) {
            Variable var = history.get(i);
            if (var.version <= time)    // find last committed value before time
                return var.val;
        }
        return -1;
    }


    /** read replicated value from the site:
     * If xi is replicated, RO can read xi from site s if xi was committed at s by some
     * transaction T before RO began and s was up all the time between the time when xi
     * was committed and RO began.
     */
    public String replicatedRO(int varIndex,int time,int siteId) {
        Site site = siteTable.get(siteId);
        List<Variable> history = site.variableTable.get(varIndex);
        for (int i = history.size() - 1; i >= 0; i--) {
            Variable var = history.get(i);
            // find last committed value before time
            if (var.version <= time) {
                int lastCommittedValue = var.val;
                if (alwaysUp(siteId, time, var.version))
                    return Integer.toString(lastCommittedValue);
                break;
            }
        }
        return "No qualified value";
    }

    public boolean alwaysUp(int siteId, int readStartTime, int lastCommittedTime) {
        List<Integer> filedTimes = siteFailTimes.get(siteId);
        for (int i = 0; i < filedTimes.size(); i++) {
            int t = filedTimes.get(i);
            if (lastCommittedTime < t && t < readStartTime) // not qualified
                return false;
        }
        return true;
    }

    public void write(int varIndex, int value, int siteId, int time) {
        Site site = siteTable.get(siteId);
        site.write(value, varIndex, time);
    }

    public void releaseLocks(int siteId, int transId) {
        if (failedSites.get(siteId))
            return;
        siteTable.get(siteId).releaseLock(transId);
    }

    public void fail(int siteId, int time) {
        Site site = siteTable.get(siteId);
        site.siteFail();
        failedSites.put(siteId, true);
        siteFailTimes.get(siteId).add(time);
    }

    public void recover(int siteId, int time) {
        Site site = siteTable.get(siteId);
        int sz = siteFailTimes.get(siteId).size();
        site.siteRecover(time, siteFailTimes.get(siteId).get(sz - 1));
    }

}
