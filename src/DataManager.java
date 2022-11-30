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

    public void fail() {

    }

    public void recover(int siteId, int time) {

    }


}
