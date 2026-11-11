package lager;

import java.util.*;

/** Die Lagerhalle: Karte, Lagerist, Regal. Jede Aktion landet als Ereignis in der Liste für die Animation. */
public final class Welt {
    static final int MAX_TICKS = 400000, MAX_AKTIONEN = 3000, MAX_TIEFE = 900;
    static final String[] RICHTUNGEN = { "rechts", "links", "hoch", "runter" };
    static final int[][] DELTA = { { 1, 0 }, { -1, 0 }, { 0, -1 }, { 0, 1 } };
    /** Befehl -> Kauf, der ihn freischaltet */
    static final Map<String, String[]> FREI = new HashMap<>();
    static {
        for (String b : new String[] { "wasIstHier" }) FREI.put(b, new String[] { "scanner", "den Scanner" });
        for (String b : new String[] { "finde", "findeAlles", "geheZu", "zurRampe", "zumKuehlraum" }) FREI.put(b, new String[] { "hubwagen", "den Hubwagen" });
        for (String b : new String[] { "lies", "tausche", "stelle", "istFachFrei", "regalGroesse" }) FREI.put(b, new String[] { "terminal", "das Regal-Terminal" });
        for (String b : new String[] { "istFrei", "gehe" }) FREI.put(b, new String[] { "kompass", "den Kompass" });
    }

    static Welt w;

    final String[] rows;
    final int H, W, tragkraft;
    final Set<String> owned = new HashSet<>();
    final String[][] art;
    final int[][] nr;
    int px, py;
    final int[] rampe = new int[2];
    int[] kuehl;
    boolean waende;
    final List<int[]> fach = new ArrayList<>();
    int[] regal = new int[0];
    final List<Feld> carry = new ArrayList<>();
    final Map<String, Integer> stock = new LinkedHashMap<>();
    final List<Integer> folge = new ArrayList<>();
    String meldung;
    int liesAnzahl;
    final List<Object> events = new ArrayList<>();
    long ticks;
    int zeile, marken;
    final int auftrag;
    final int[] lieferung;

    Welt(Map<String, Object> level) {
        List<Object> g = Json.list(level.get("grid"));
        H = g.size();
        rows = new String[H];
        for (int y = 0; y < H; y++) rows[y] = (String) g.get(y);
        W = rows[0].length();
        tragkraft = Json.num(level.get("tragkraft"));
        for (Object o : Json.list(level.get("owned"))) owned.add((String) o);
        art = new String[H][W];
        nr = new int[H][W];
        int[] nummern = Json.ints(level.get("nummern"));
        int k = 0;
        for (int y = 0; y < H; y++) for (int x = 0; x < W; x++) {
            char ch = rows[y].charAt(x);
            if (ch == 'L') { rampe[0] = x; rampe[1] = y; }
            else if (ch == 'C') kuehl = new int[] { x, y };
            else if (ch == '#') waende = true;
            else if (ch == 'R') fach.add(new int[] { x, y });
            else if (ch == 'K' || ch == 'F') {
                art[y][x] = ch == 'K' ? "kiste" : "fass";
                nr[y][x] = k < nummern.length ? nummern[k] : k + 1;
                k++;
            }
        }
        px = rampe[0]; py = rampe[1];
        if (level.get("regal") != null) regal = Json.ints(level.get("regal"));
        auftrag = level.get("auftrag") == null ? 0 : Json.num(level.get("auftrag"));
        lieferung = Json.ints(level.get("lieferung"));
    }

    /** Zählt Schleifenrunden mit, damit eine Endlosschleife den Browser nicht einfriert. */
    public static boolean tick() {
        if (w != null && ++w.ticks > MAX_TICKS) throw new Fehler("Dein Code läuft viel zu lange. Steckt eine Endlosschleife drin?");
        return true;
    }

    /** Merkt sich die Zeile der Anweisung, die gerade läuft (siehe Runner.zeilenMarken). */
    public static void z(int zeile) {
        Welt x = w;
        if (x == null) return;
        x.zeile = zeile;
        // Im Browser meldet die Java-Maschine eine endlose Rekursion nicht sauber, darum misst das Spiel ab und zu selbst die Aufruftiefe
        if ((++x.marken & 31) == 0 && new Throwable().getStackTrace().length > MAX_TIEFE)
            throw new Fehler("Die Rekursion hört nicht auf: Die Methode ruft sich schon über " + MAX_TIEFE + "-mal selbst auf.\nFehlt der Basisfall, oder wird das Problem bei jedem Aufruf nicht kleiner?");
    }

    void frei(String befehl) {
        tick();
        String[] f = FREI.get(befehl);
        if (f != null && !owned.contains(f[0])) throw new Fehler(befehl + "() ist noch gesperrt. Kauf erst " + f[1] + " im Shop.");
    }

    void add(Object... ev) {
        if (events.size() >= MAX_AKTIONEN) throw new Fehler("Dein Lagerist ist erschöpft: viel zu viele Aktionen. Steckt eine Endlosschleife drin?");
        events.add(Arrays.asList(ev));
    }

    String hier() { return "(" + px + ", " + py + ")"; }

    static int richtung(String name) {
        for (int i = 0; i < 4; i++) if (RICHTUNGEN[i].equals(name)) return i;
        throw new Fehler("Die Richtung \"" + name + "\" gibt es nicht. Erlaubt sind \"rechts\", \"links\", \"hoch\" und \"runter\".");
    }

    boolean begehbar(int x, int y) {
        if (x < 0 || y < 0 || x >= W || y >= H) return false;
        char ch = rows[y].charAt(x);
        return ch != '#' && ch != 'R';
    }

    void schritt(String name) {
        int d = richtung(name), nx = px + DELTA[d][0], ny = py + DELTA[d][1];
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) throw new Fehler("Mit " + name + "() würde dein Lagerist die Halle verlassen. Er steht auf " + hier() + ".");
        if (!begehbar(nx, ny)) throw new Fehler("Mit " + name + "() läuft dein Lagerist gegen " + (rows[ny].charAt(nx) == 'R' ? "das Regal" : "eine Wand") + ". Er steht auf " + hier() + ".");
        add("walk", nx, ny);
        px = nx; py = ny;
    }

    boolean istFrei(String name) {
        int d = richtung(name);
        return begehbar(px + DELTA[d][0], py + DELTA[d][1]);
    }

    void geheZu(int x, int y) {
        if (waende) throw new Fehler("Zwischen den Wänden kommt der Hubwagen nicht durch. Hier musst du Schritt für Schritt laufen.");
        if (x < 0 || y < 0 || x >= W || y >= H) throw new Fehler("geheZu braucht eine Position in der Halle (x: 0 bis " + (W - 1) + ", y: 0 bis " + (H - 1) + ").");
        if (!begehbar(x, y)) throw new Fehler("Auf (" + x + ", " + y + ") steht das Regal, dorthin kann dein Lagerist nicht laufen.");
        while (px != x) schritt(px < x ? "rechts" : "links");
        while (py != y) schritt(py < y ? "runter" : "hoch");
    }

    String wasIstHier() {
        if (art[py][px] != null) return art[py][px];
        char ch = rows[py].charAt(px);
        return ch == 'L' ? "rampe" : ch == 'C' ? "kuehlraum" : "leer";
    }

    int nimm() {
        if (art[py][px] == null) throw new Fehler("Hier steht nichts zum Mitnehmen. Dein Lagerist steht auf " + hier() + ".");
        if (carry.size() >= tragkraft) throw new Fehler("Die Hände sind voll, mehr als " + tragkraft + " kann dein Lagerist nicht tragen. Bring erst alles mit abliefern() weg.");
        Feld f = new Feld(px, py, art[py][px], nr[py][px]);
        art[py][px] = null;
        carry.add(f);
        add("pick", px, py, f.art, f.nummer);
        return f.nummer;
    }

    void abliefern() {
        boolean anRampe = px == rampe[0] && py == rampe[1], imKuehl = kuehl != null && px == kuehl[0] && py == kuehl[1];
        if (!anRampe && !imKuehl) throw new Fehler("Abliefern geht nur an der Rampe" + (kuehl != null ? " oder im Kühlraum" : "") + ". Dein Lagerist steht auf " + hier() + ".");
        List<Object> ab = new ArrayList<>();
        for (Iterator<Feld> it = carry.iterator(); it.hasNext();) {
            Feld f = it.next();
            boolean gekuehlt = kuehl != null && f.art.equals("fass");
            if (gekuehlt != imKuehl) continue;
            it.remove();
            stock.merge(f.art, 1, Integer::sum);
            folge.add(f.nummer);
            ab.add(Arrays.asList(f.art, f.nummer));
        }
        if (ab.isEmpty() && !carry.isEmpty())
            throw new Fehler(imKuehl ? "In den Kühlraum gehören nur Fässer. Kisten bringst du zur Rampe." : "Fässer gehören in den Kühlraum, nicht an die Rampe.");
        add("deliver", ab);
    }

    List<Feld> finde(String gesucht) {
        if (gesucht != null && !gesucht.equals("kiste") && !gesucht.equals("fass")) throw new Fehler("finde kennt nur \"kiste\" und \"fass\". Alles zusammen liefert findeAlles().");
        List<Feld> r = new ArrayList<>();
        for (int y = 0; y < H; y++) for (int x = 0; x < W; x++)
            if (art[y][x] != null && (gesucht == null || gesucht.equals(art[y][x]))) r.add(new Feld(x, y, art[y][x], nr[y][x]));
        return r;
    }

    void zumFach(int i) {
        if (regal.length == 0) throw new Fehler("In dieser Halle steht kein Regal.");
        if (i < 0 || i >= regal.length) throw new Fehler("Das Regal hat nur die Fächer 0 bis " + (regal.length - 1) + ". Fach " + i + " gibt es nicht.");
        int[] f = fach.get(i);
        while (px != f[0]) schritt(px < f[0] ? "rechts" : "links");
        while (py != f[1] + 1) schritt(py < f[1] + 1 ? "runter" : "hoch");
    }

    int lies(int i) {
        zumFach(i);
        liesAnzahl++;
        add("read", i, regal[i]);
        return regal[i];
    }

    void tausche(int i, int j) {
        zumFach(i);
        if (j < 0 || j >= regal.length) throw new Fehler("Das Regal hat nur die Fächer 0 bis " + (regal.length - 1) + ". Fach " + j + " gibt es nicht.");
        zumFach(j);
        int t = regal[i]; regal[i] = regal[j]; regal[j] = t;
        add("swap", i, j);
    }

    void stelle(int i, int wert) {
        zumFach(i);
        if (regal[i] != 0) throw new Fehler("Fach " + i + " ist schon belegt (dort steht " + regal[i] + "). Prüfe vorher mit istFachFrei(" + i + ").");
        if (wert <= 0) throw new Fehler("Eine Kiste braucht eine Nummer größer als 0.");
        regal[i] = wert;
        add("put", i, wert);
    }

    boolean istFachFrei(int i) {
        if (i < 0 || i >= regal.length) throw new Fehler("Das Regal hat nur die Fächer 0 bis " + (regal.length - 1) + ". Fach " + i + " gibt es nicht.");
        return regal[i] == 0;
    }

    void melde(String text) {
        meldung = text;
        add("say", text);
    }

    /** Prüft das Ziel des Levels. Liefert null, wenn alles stimmt, sonst einen Satz, was fehlt. */
    String fehlt(Map<String, Object> ziel, boolean exakt) {
        List<String> f = new ArrayList<>();
        for (String k : new String[] { "kiste", "fass" }) {
            if (!ziel.containsKey(k)) continue;
            int soll = Json.num(ziel.get(k)), ist = stock.getOrDefault(k, 0);
            if (exakt ? ist != soll : ist < soll) f.add(ist + " " + k + " abgeliefert statt " + (exakt ? "genau " : "") + soll);
        }
        if (ziel.containsKey("folge")) {
            List<Integer> soll = new ArrayList<>();
            for (int x : Json.ints(ziel.get("folge"))) soll.add(x);
            if (!soll.equals(folge)) f.add("abgeliefert wurde in der Reihenfolge " + folge + ", verlangt war " + soll);
        }
        if (ziel.containsKey("regal") && !Arrays.equals(Json.ints(ziel.get("regal")), regal))
            f.add("im Regal steht " + Arrays.toString(regal) + ", verlangt war " + Arrays.toString(Json.ints(ziel.get("regal"))));
        if (ziel.containsKey("meldung")) {
            String soll = String.valueOf(ziel.get("meldung") instanceof Double ? (Object) Json.num(ziel.get("meldung")) : ziel.get("meldung"));
            if (meldung == null) f.add("es wurde nichts mit melde(...) gemeldet");
            else if (!soll.equals(meldung)) f.add("gemeldet wurde " + meldung + ", das stimmt nicht");
        }
        if (ziel.containsKey("max_lies") && liesAnzahl > Json.num(ziel.get("max_lies")))
            f.add("lies() wurde " + liesAnzahl + "-mal benutzt, erlaubt sind höchstens " + Json.num(ziel.get("max_lies")));
        return f.isEmpty() ? null : String.join(", ", f);
    }
}
