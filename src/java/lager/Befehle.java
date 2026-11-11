package lager;

import java.util.List;

/** Alle Befehle, die dein Code aufrufen kann. Sie sind in Main.java ohne Klassennamen verfügbar. */
public final class Befehle {
    private Befehle() { }

    private static Welt w(String befehl) { Welt.w.frei(befehl); return Welt.w; }

    public static void rechts() { w("rechts").schritt("rechts"); }
    public static void links() { w("links").schritt("links"); }
    public static void hoch() { w("hoch").schritt("hoch"); }
    public static void runter() { w("runter").schritt("runter"); }

    /** Nimmt die Ware auf diesem Feld und gibt ihre Nummer zurück. */
    public static int nimm() { return w("nimm").nimm(); }
    public static void abliefern() { w("abliefern").abliefern(); }

    public static String wasIstHier() { return w("wasIstHier").wasIstHier(); }

    public static List<Feld> finde(String art) { return w("finde").finde(art); }
    public static List<Feld> findeAlles() { return w("findeAlles").finde(null); }
    public static void geheZu(int x, int y) { w("geheZu").geheZu(x, y); }
    public static void geheZu(Feld f) { w("geheZu").geheZu(f.x, f.y); }
    public static void zurRampe() { Welt x = w("zurRampe"); x.geheZu(x.rampe[0], x.rampe[1]); }
    public static void zumKuehlraum() {
        Welt x = w("zumKuehlraum");
        if (x.kuehl == null) throw new Fehler("In dieser Halle gibt es keinen Kühlraum.");
        x.geheZu(x.kuehl[0], x.kuehl[1]);
    }

    public static boolean istFrei(String richtung) { return w("istFrei").istFrei(richtung); }
    public static void gehe(String richtung) { w("gehe").schritt(richtung); }
    public static int posX() { return w("posX").px; }
    public static int posY() { return w("posY").py; }

    public static int regalGroesse() { return w("regalGroesse").regal.length; }
    public static int lies(int fach) { return w("lies").lies(fach); }
    public static void tausche(int fachA, int fachB) { w("tausche").tausche(fachA, fachB); }
    public static void stelle(int fach, int nummer) { w("stelle").stelle(fach, nummer); }
    public static boolean istFachFrei(int fach) { return w("istFachFrei").istFachFrei(fach); }

    public static void melde(Object wert) { w("melde").melde(String.valueOf(wert)); }
    public static int auftrag() { return w("auftrag").auftrag; }
    public static int[] lieferung() { return w("lieferung").lieferung.clone(); }
}
