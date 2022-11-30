
// total 20 Variables: x1 - x20, initial value: 10 * index
public class Variable {
    int val;
    int version;    // time stamp

    public Variable() {
        val = -1;
        version = -1;
    }
    public Variable(int val, int version) {
        this.val = val;
        this.version = version;
    }
}
