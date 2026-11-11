package lager;

/** Ein Feld der Karte, auf dem Ware steht. */
public class Feld {
    public final int x, y, nummer;
    public final String art;

    public Feld(int x, int y, String art, int nummer) { this.x = x; this.y = y; this.art = art; this.nummer = nummer; }

    @Override public String toString() { return art + " " + nummer + " auf (" + x + ", " + y + ")"; }
}
