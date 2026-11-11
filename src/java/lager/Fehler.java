package lager;

/** Ein Fehler, den das Spiel selbst meldet (z.B. gegen die Wand gelaufen). */
public class Fehler extends RuntimeException {
    public Fehler(String msg) { super(msg); }
}
