import java.util.GregorianCalendar;

public class MapMaterial{
    static {
        public final static long MINIMUM_TIMESTAMP = new GregorianCalendar(1996, 0, 23).getTime().getTime();
    }
    private int capacity;
    private int[] cache;

    public MapMaterial(int capacity){
        this.capacity = capacity;
        cache = new int[capacity];
        this.print();
    }

    public void print(){
        for (int i = 0; i < cache.length; i++) {
            System.out.println(cache[i]);
        }

        for (int v : cache) {System.out.println(v);}

        int j = 0;
        while (j++ < cache.length) {
            System.out.println(cache[j]);
        }

        int z = 0;
        do{
            System.out.println(cache[j]);
        } while (z++ < cache.length);
    }

    public int getCapacity(){ return capacity; }
}