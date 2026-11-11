"""Prüft, dass die Absicherung des Codes (Schleifenzähler, Zeilenmerker) gültiges Java nicht kaputt macht und Fehlerzeilen stimmen."""
import sys, json
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from javarun import baue_jar, run_many
baue_jar()
LV = {"grid": ["L...K"], "tragkraft": 1, "ziel": {}, "owned": ["scanner", "hubwagen", "terminal", "kompass"]}
TORTUR = r'''
import java.util.*;
import java.util.function.*;

interface Form { double flaeche(); default String name() { return "Form"; } }
enum Ampel { ROT, GELB, GRUEN; Ampel naechste() { return values()[(ordinal() + 1) % 3]; } }
record Punkt(int x, int y) { int summe() { return x + y; } }
abstract class Basis {
    protected int wert;
    static int zaehler;
    static { zaehler = 10; }
    { wert = 1; }
    Basis(int w) { this.wert += w; }
    abstract int rechne() throws Exception;
}
class Kind extends Basis implements Form {
    Kind(int w) { super(w); zaehler++; }
    Kind() { this(5); }
    @Override int rechne() throws Exception { if (wert > 100) throw new Exception("zu gross"); return wert * 2; }
    @Override public double flaeche() { return wert; }
}
class Box<T extends Comparable<T>> {
    private T inhalt;
    Box(T t) { inhalt = t; }
    <R> R wandle(Function<T, R> f) { return f.apply(inhalt); }
}
public class Main {
    static int[] daten = { 3, 1, 2 };
    static int fak(int n) { return n <= 1 ? 1 : n * fak(n - 1); }
    static String tag(int t) {
        switch (t) {
            case 1: return "Mo";
            case 2: { String s = "Di"; return s; }
            default: return "?";
        }
    }
    public static void main(String[] args) throws Exception {
        int summe = 0;
        for (int d : daten) summe += d;
        int i = 0;
        do { i++; } while (i < 3);
        do i++; while (i < 5);
        if (i == 5) System.out.println("a " + summe + " " + i);
        else System.out.println("falsch");
        if (i > 9) { System.out.println("x"); } else if (i > 4) { System.out.println("b"); } else { System.out.println("y"); }
        outer:
        for (int a = 0; a < 3; a++) {
            for (int b = 0; b < 3; b++) {
                if (b == 1) continue outer;
                if (a == 2) break outer;
                System.out.println("c" + a + b);
            }
        }
        Kind k = new Kind();
        try {
            System.out.println("d " + k.rechne() + " " + Basis.zaehler + " " + k.name());
            int[] leer = new int[0];
            leer[1] = 2;
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("e gefangen");
        } finally {
            System.out.println("f finally");
        }
        Runnable r = new Runnable() {
            int n = 2;
            @Override public void run() { n++; System.out.println("g " + n); }
        };
        r.run();
        List<Integer> l = new ArrayList<>(List.of(4, 2, 9));
        l.forEach(x -> {
            if (x > 3) {
                System.out.println("h " + x);
            }
        });
        Map<String, List<Integer>> m = new HashMap<>() {{ put("k", l); }};
        String art = switch (Ampel.ROT.naechste()) { case GELB -> "gelb"; default -> { String t = "sonst"; yield t; } };
        System.out.println("i " + m.get("k").size() + " " + art + " " + tag(2) + " " + new Punkt(1, 2).summe() + " " + fak(5));
        System.out.println("j " + new Box<>("abc").wandle(s -> s.length()) + " " + String.class.getSimpleName());
        while (true) { i++; if (i > 7) break; }
        Object o = l;
        if (o instanceof List<?> li && !li.isEmpty()) System.out.println("k " + li.get(0));
        synchronized (o) { System.out.println("l"); }
        int[][] g = { { 1, 2 }, { 3 } };
        var sb = new StringBuilder(); for (int[] z : g) { for (int v : z) sb.append(v); }
        System.out.println("m " + sb);
    }
}
'''
ERW = "a 6 5\nb\nc00\nc10\nd 12 11 Form\ne gefangen\nf finally\ng 3\nh 4\nh 9\ni 3 gelb Di 3 120\nj 3 String\nk 4\nl\nm 123\n"
def prog(body, vor=""):
    return "import java.util.*;\npublic class Main {\n" + vor + "    public static void main(String[] args) {\n" + body + "    }\n}\n"
FAELLE = [
    (prog("        int a = 1;\n        int[] f = new int[2];\n        f[5] = 1;\n"), 6),
    (prog("        rechts();\n        rechts();\n        hoch();\n        rechts();\n"), 6),
    (prog("        hilf(2);\n", "    static void hilf(int n) {\n        for (int i = 0; i < n; i++) {\n            links();\n        }\n    }\n"), 5),
    (prog("        String s = null;\n        if (posX() == 0) {\n            s.length();\n        }\n"), 6),
    (prog("        List<Integer> l = new ArrayList<>();\n        l.forEach(x -> rechts());\n        List.of(1, 2).forEach(x -> {\n            nimm();\n        });\n"), 7),
    (prog("        f(1);\n", "    static int f(int n) {\n        return f(n + 1);\n    }\n"), 4),
    (prog("        Knoten k = new Knoten();\n        while (k != null) {\n            k = k.next;\n        }\n        k.wert = 3;\n").replace("public class Main", "class Knoten { int wert; Knoten next; }\npublic class Main"), 9),
]
res = run_many([(TORTUR, LV)] + [(c, LV) for c, _ in FAELLE], marken=True)
bad = 0
r = res[0]
if r["error"] or r["output"] != ERW:
    bad += 1; print("TORTUR FEHLER", r["error"], repr(r["output"]))
for (c, line), r in zip(FAELLE, res[1:]):
    ok = r["error"] and r["error"]["kind"] == "runtime" and r["error"]["line"] == line
    print("Zeile erwartet", line, "bekommen", (r["error"] or {}).get("line"), "OK" if ok else "FEHLER", "|", (r["error"] or {}).get("msg", "")[:70].replace("\n", " "))
    bad += not ok
print("FEHLER:", bad)
sys.exit(1 if bad else 0)
