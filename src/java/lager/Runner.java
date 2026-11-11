package lager;

import java.io.*;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.eclipse.jdt.core.compiler.IProblem;
import org.eclipse.jdt.internal.compiler.ClassFile;
import org.eclipse.jdt.internal.compiler.Compiler;
import org.eclipse.jdt.internal.compiler.DefaultErrorHandlingPolicies;
import org.eclipse.jdt.internal.compiler.ICompilerRequestor;
import org.eclipse.jdt.internal.compiler.classfmt.ClassFileReader;
import org.eclipse.jdt.internal.compiler.env.ICompilationUnit;
import org.eclipse.jdt.internal.compiler.env.INameEnvironment;
import org.eclipse.jdt.internal.compiler.env.NameEnvironmentAnswer;
import org.eclipse.jdt.internal.compiler.impl.CompilerOptions;
import org.eclipse.jdt.internal.compiler.problem.DefaultProblemFactory;

/** Übersetzt den Code aus dem Editor mit dem Eclipse-Compiler und lässt ihn in der Lagerhalle laufen. */
public final class Runner {
    static final String DATEI = "Main.java";
    static final String VORSPANN = "import static lager.Befehle.*; import lager.Feld; ";
    static final String TICK = "lager.Welt.tick()";
    /** Diese Werte darf ein Level je Variante austauschen */
    static final String[] VARIABEL = { "grid", "nummern", "regal", "auftrag", "lieferung", "ziel" };

    // ---------- Übersetzen ----------

    static final class Unit implements ICompilationUnit {
        final String code;
        Unit(String code) { this.code = code; }
        public char[] getFileName() { return DATEI.toCharArray(); }
        public char[] getContents() { return code.toCharArray(); }
        public char[] getMainTypeName() { return "Main".toCharArray(); }
        public char[][] getPackageName() { return new char[0][]; }
        public boolean ignoreOptionalProblems() { return true; }
    }

    static String join(char[][] parts, char[] last) {
        StringBuilder sb = new StringBuilder();
        if (parts != null) for (char[] p : parts) { if (sb.length() > 0) sb.append('.'); sb.append(p); }
        if (last != null) { if (sb.length() > 0) sb.append('.'); sb.append(last); }
        return sb.toString();
    }

    /** Sagt dem Compiler, welche Klassen es gibt: alles, was der Klassenlader findet (JDK und lager.*). */
    static final class Env implements INameEnvironment {
        static final ClassLoader CL = Runner.class.getClassLoader();
        static final Map<String, Boolean> PAKET = new HashMap<>();
        static final Map<String, byte[]> CACHE = new HashMap<>();

        static byte[] bytes(String cls) {
            if (CACHE.containsKey(cls)) return CACHE.get(cls);
            byte[] r = null;
            try (InputStream in = CL.getResourceAsStream(cls.replace('.', '/') + ".class")) {
                if (in != null) {
                    ByteArrayOutputStream bo = new ByteArrayOutputStream(); byte[] b = new byte[8192]; int n;
                    while ((n = in.read(b)) > 0) bo.write(b, 0, n);
                    r = bo.toByteArray();
                }
            } catch (IOException e) { r = null; }
            CACHE.put(cls, r);
            return r;
        }
        NameEnvironmentAnswer find(String cls) {
            byte[] b = cls.indexOf('.') < 0 ? null : bytes(cls);
            if (b == null) return null;
            try { return new NameEnvironmentAnswer(new ClassFileReader(b, cls.toCharArray(), true), null); }
            catch (Exception e) { return null; }
        }
        public NameEnvironmentAnswer findType(char[][] compound) { return find(join(compound, null)); }
        public NameEnvironmentAnswer findType(char[] type, char[][] p) { return find(join(p, type)); }
        public boolean isPackage(char[][] parent, char[] name) {
            String n = join(parent, name);
            Boolean known = PAKET.get(n);
            if (known != null) return known;
            boolean r = Character.isLowerCase(n.charAt(n.lastIndexOf('.') + 1)) && bytes(n) == null;
            PAKET.put(n, r);
            return r;
        }
        public void cleanup() { }
    }

    /** Ergebnis: entweder Klassen oder der erste Fehler als [Zeile, Meldung]. */
    static Object[] compile(String code, Map<String, byte[]> outs) {
        Map<String, String> o = new HashMap<>();
        o.put(CompilerOptions.OPTION_Source, "17"); o.put(CompilerOptions.OPTION_Compliance, "17"); o.put(CompilerOptions.OPTION_TargetPlatform, "17");
        o.put(CompilerOptions.OPTION_LineNumberAttribute, CompilerOptions.GENERATE);
        final Object[] first = { null, null };
        ICompilerRequestor req = res -> {
            if (res.getProblems() != null) for (IProblem p : res.getProblems())
                if (p.isError() && (first[0] == null || p.getSourceLineNumber() < (Integer) first[0])) { first[0] = p.getSourceLineNumber(); first[1] = p.getMessage(); }
            for (ClassFile cf : res.getClassFiles()) outs.put(join(cf.getCompoundName(), null), cf.getBytes());
        };
        new Compiler(new Env(), DefaultErrorHandlingPolicies.proceedWithAllProblems(), new CompilerOptions(o), req, new DefaultProblemFactory(Locale.ENGLISH))
            .compile(new ICompilationUnit[] { new Unit(code) });
        return first[0] == null ? null : first;
    }

    // ---------- Schleifen absichern ----------

    /** Springt über Zeichenketten, Zeichen und Kommentare ab Position i. Liefert die Position danach oder i. */
    static int skip(String s, int i) {
        char c = s.charAt(i);
        if (c == '"') {
            if (s.startsWith("\"\"\"", i)) { int e = s.indexOf("\"\"\"", i + 3); return e < 0 ? s.length() : e + 3; }
            for (int k = i + 1; k < s.length(); k++) { char d = s.charAt(k); if (d == '\\') k++; else if (d == '"' || d == '\n') return k + 1; }
            return s.length();
        }
        if (c == '\'') {
            for (int k = i + 1; k < s.length(); k++) { char d = s.charAt(k); if (d == '\\') k++; else if (d == '\'' || d == '\n') return k + 1; }
            return s.length();
        }
        if (c == '/' && i + 1 < s.length()) {
            if (s.charAt(i + 1) == '/') { int e = s.indexOf('\n', i); return e < 0 ? s.length() : e; }
            if (s.charAt(i + 1) == '*') { int e = s.indexOf("*/", i + 2); return e < 0 ? s.length() : e + 2; }
        }
        return i;
    }

    /** Baut in jede while- und for-Bedingung einen Zähler ein. Zeilennummern bleiben gleich. */
    static String absichern(String s) {
        TreeMap<Integer, String> ins = new TreeMap<>();
        int i = 0, n = s.length();
        while (i < n) {
            int j = skip(s, i);
            if (j != i) { i = j; continue; }
            char c = s.charAt(i);
            if (!Character.isJavaIdentifierStart(c)) { i++; continue; }
            int a = i;
            while (i < n && Character.isJavaIdentifierPart(s.charAt(i))) i++;
            String word = s.substring(a, i);
            if (a > 0 && (Character.isJavaIdentifierPart(s.charAt(a - 1)) || s.charAt(a - 1) == '.')) continue;
            if (!word.equals("while") && !word.equals("for")) continue;
            int p = i;
            while (p < n && Character.isWhitespace(s.charAt(p))) p++;
            if (p >= n || s.charAt(p) != '(') continue;
            int depth = 0, close = -1;
            List<Integer> semis = new ArrayList<>();
            for (int k = p; k < n; k++) {
                int e = skip(s, k);
                if (e != k) { k = e - 1; continue; }
                char d = s.charAt(k);
                if (d == '(' || d == '[' || d == '{') depth++;
                else if (d == ')' || d == ']' || d == '}') { depth--; if (depth == 0) { close = k; break; } }
                else if (d == ';' && depth == 1) semis.add(k);
            }
            if (close < 0) continue;
            int von, bis;
            if (word.equals("while")) { von = p + 1; bis = close; }
            else if (semis.size() == 2) { von = semis.get(0) + 1; bis = semis.get(1); }
            else continue;                                        // for (x : liste) endet von selbst
            String cond = s.substring(von, bis).trim();
            if (cond.isEmpty() || cond.equals("true")) {          // sonst würde der Compiler ein fehlendes return melden
                int b = close + 1;
                while (b < n && Character.isWhitespace(s.charAt(b))) b++;
                if (b < n && s.charAt(b) == '{') ins.merge(b + 1, " " + TICK + ";", String::concat);
            } else {
                ins.merge(von, " " + TICK + " && (", String::concat);
                ins.merge(bis, ")", (x, y) -> y + x);
            }
        }
        zeilenMarken(s, ins);
        StringBuilder sb = new StringBuilder(s);
        for (Map.Entry<Integer, String> e : ins.descendingMap().entrySet()) sb.insert(e.getKey(), e.getValue());
        return sb.toString();
    }

    static final Set<String> KEIN_ANFANG = new HashSet<>(Arrays.asList("else", "catch", "finally", "while", "super", "this", "case", "default"));
    static final Set<String> BLOCK_DAVOR = new HashSet<>(Arrays.asList("else", "try", "do", "finally", "static", "->", ":"));
    static final Pattern VOR_KLAMMER = Pattern.compile("(?s).*?\\b(switch|new\\s+[\\w.]+(\\s*<[^;{}()]*>)?|record\\s+\\w+(\\s*<[^;{}()]*>)?)\\s*$");

    /**
     * Schreibt vor jede Anweisung, die sicher als solche erkennbar ist, einen Merker mit ihrer Zeilennummer.
     * Im Browser liefert die Java-Maschine keine Zeilennummern, so weiß das Spiel trotzdem, wo ein Fehler passiert ist.
     * Arten von geschweiften Klammern: B = Block mit Anweisungen, C = Klassenkörper, S = switch, A = alles andere (z.B. Array).
     */
    static void zeilenMarken(String s, TreeMap<Integer, String> ins) {
        int n = s.length(), paren = 0, zeile = 1;
        Deque<Character> art = new ArrayDeque<>();
        Deque<Integer> gemerkt = new ArrayDeque<>(), offen = new ArrayDeque<>();
        String prev = "";
        int letzteOffene = -1;
        boolean klasse = false;
        int i = 0;
        while (i < n) {
            int j = skip(s, i);
            if (j != i) {
                for (int k = i; k < j; k++) if (s.charAt(k) == '\n') zeile++;
                if (s.charAt(i) != '/') prev = "\"";
                i = j; continue;
            }
            char c = s.charAt(i);
            if (c == '\n') zeile++;
            if (Character.isWhitespace(c)) { i++; continue; }
            if (Character.isJavaIdentifierStart(c)) {
                int a = i;
                while (i < n && Character.isJavaIdentifierPart(s.charAt(i))) i++;
                String word = s.substring(a, i);
                if (!prev.equals(".") && (word.equals("class") || word.equals("interface") || word.equals("enum") || word.equals("record"))) klasse = true;
                prev = word;
                continue;
            }
            boolean grenze = false;
            if (c == '(') { paren++; offen.push(i); }
            else if (c == ')') { paren--; if (!offen.isEmpty()) letzteOffene = offen.pop(); }
            else if (c == '{') {
                char k;
                if (prev.equals(")")) k = klasse ? 'C' : letzteOffene >= 0 && VOR_KLAMMER.matcher(s.substring(Math.max(0, letzteOffene - 200), letzteOffene)).matches()
                        ? (s.substring(Math.max(0, letzteOffene - 200), letzteOffene).trim().endsWith("switch") ? 'S' : 'C') : 'B';
                else if (BLOCK_DAVOR.contains(prev)) k = prev.equals(":") && art.peek() != null && art.peek() == 'C' ? 'A' : 'B';
                else if (prev.equals(";") || prev.equals("{") || prev.equals("}")) k = art.isEmpty() ? 'A' : 'B';
                else if (klasse) k = 'C';
                else if (prev.equals(">") || (!prev.isEmpty() && Character.isJavaIdentifierStart(prev.charAt(0)))) k = 'B';   // z.B. throws IOException {
                else k = 'A';
                art.push(k); gemerkt.push(paren); paren = 0; klasse = false;
                grenze = k == 'B';
            } else if (c == '}') {
                if (!art.isEmpty()) { art.pop(); paren = gemerkt.pop(); }
                klasse = false;
                grenze = !art.isEmpty() && art.peek() == 'B' && paren == 0;
            } else if (c == ';') {
                klasse = false;
                grenze = !art.isEmpty() && art.peek() == 'B' && paren == 0;
            }
            prev = c == '-' && i + 1 < n && s.charAt(i + 1) == '>' ? "->" : String.valueOf(c);
            i += prev.length();
            if (!grenze) continue;
            int p = i, z = zeile;                                  // nächstes Token suchen
            while (p < n) {
                int e = skip(s, p);
                if (e != p && s.charAt(p) == '/') { for (int k = p; k < e; k++) if (s.charAt(k) == '\n') z++; p = e; continue; }
                if (!Character.isWhitespace(s.charAt(p))) break;
                if (s.charAt(p) == '\n') z++;
                p++;
            }
            if (p >= n || !Character.isJavaIdentifierStart(s.charAt(p))) continue;
            int q = p;
            while (q < n && Character.isJavaIdentifierPart(s.charAt(q))) q++;
            if (KEIN_ANFANG.contains(s.substring(p, q))) continue;
            ins.merge(p, "lager.Welt.z(" + z + "); ", String::concat);
        }
    }

    // ---------- Fehlermeldungen ----------

    static String erklaere(String msg) {
        String[][] regeln = {
            { "Syntax error, insert \";\".*", "Am Ende der Anweisung fehlt ein Semikolon ;" },
            { "Syntax error, insert \"}\".*", "Es fehlt eine schließende geschweifte Klammer }" },
            { "Syntax error, insert \"\\)\".*", "Es fehlt eine schließende runde Klammer )" },
            { "Syntax error on token \"(.+?)\", delete this token", "Das Zeichen $1 ist hier zu viel." },
            { "Syntax error on token \"(.+?)\", (.+) expected.*", "Bei $1 stimmt etwas nicht: Hier wird $2 erwartet." },
            { "Syntax error, insert \"(.+?)\" to complete (.+)", "Hier fehlt noch etwas: $1" },
            { "The method (\\w+)\\((.*?)\\) is undefined for the type (\\w+)", "Die Methode $1(...) gibt es nicht. Tippfehler, oder hast du sie noch nicht geschrieben? Groß- und Kleinschreibung zählt." },
            { "The method (\\w+)\\((.*?)\\) in the type (\\w+) is not applicable for the arguments \\((.*?)\\)", "$1 erwartet ($2), bekommen hat es ($4). Anzahl oder Typ der Argumente passt nicht." },
            { "(\\w+) cannot be resolved to a variable", "Die Variable $1 ist nicht bekannt. Ist sie deklariert (z.B. int $1 = ...) und richtig geschrieben?" },
            { "(\\w+) cannot be resolved to a type", "Den Typ $1 gibt es nicht. Tippfehler, oder fehlt oben ein import (z.B. import java.util.*;)?" },
            { "(\\w+) cannot be resolved", "$1 ist nicht bekannt. Tippfehler, oder noch nicht deklariert?" },
            { "Type mismatch: cannot convert from (.+) to (.+)", "Typfehler: Ein Wert vom Typ $1 passt nicht in den Typ $2." },
            { "String literal is not properly closed by a double-quote", "Der Text in Anführungszeichen wird nicht geschlossen. Es fehlt ein \"" },
            { "This method must return a result of type (.+)", "Diese Methode muss auf jedem Weg mit return einen Wert vom Typ $1 zurückgeben." },
            { "Duplicate local variable (\\w+)", "Die Variable $1 gibt es in diesem Block schon. Beim zweiten Mal ohne Typ schreiben: $1 = ..." },
            { "The local variable (\\w+) may not have been initialized", "Die Variable $1 hat vielleicht noch keinen Wert. Gib ihr bei der Deklaration einen Startwert." },
            { "Incompatible operand types (.+) and (.+)", "$1 und $2 kann man nicht miteinander vergleichen." },
            { "Cannot make a static reference to the non-static (method|field) (.+)", "Aus einer static-Methode wie main erreichst du $2 nur über ein Objekt (mit new erzeugen) oder indem du es selbst static machst." },
            { "The type (\\w+) must implement the inherited abstract method (.+)", "Die Klasse $1 muss die abstrakte Methode $2 noch implementieren." },
            { "The constructor (.+) is undefined", "Den Konstruktor $1 gibt es nicht. Anzahl oder Typ der Argumente passt nicht." },
            { "Unhandled exception type (\\w+)", "Die Ausnahme $1 muss mit try/catch behandelt oder mit throws weitergegeben werden." },
            { "The public type (\\w+) must be defined in its own file", "In dieser Datei darf nur die Klasse Main public sein. Schreib vor $1 kein public." },
            { "Void methods cannot return a value", "Eine void-Methode gibt nichts zurück. Ändere den Rückgabetyp oder nimm den Wert hinter return weg." },
            { "The operator (.+) is undefined for the argument type\\(s\\) (.+)", "Der Operator $1 funktioniert nicht mit den Typen $2." },
            { "Cannot instantiate the type (\\w+)", "Von $1 kann man kein Objekt erzeugen, weil es abstrakt oder ein Interface ist." },
        };
        for (String[] r : regeln) {
            Matcher m = Pattern.compile(r[0]).matcher(msg);
            if (m.matches()) return m.replaceFirst(Matcher.quoteReplacement(r[1]).replace("\\$", "$")) + "\n(Compiler: " + msg + ")";
        }
        return msg;
    }

    static final String[][] HINWEISE = {
        { "NullPointerException", "Du benutzt etwas, das null ist, also auf kein Objekt zeigt. Wurde es mit new erzeugt? Ist die Liste schon zu Ende?" },
        { "ArrayIndexOutOfBoundsException", "Der Index liegt außerhalb des Arrays. Gültig sind 0 bis length - 1." },
        { "IndexOutOfBoundsException", "Der Index liegt außerhalb der Liste. Gültig sind 0 bis size() - 1." },
        { "StackOverflowError", "Die Rekursion hört nicht auf. Fehlt der Basisfall, oder wird das Problem bei jedem Aufruf nicht kleiner?" },
        { "ArithmeticException", "Rechenfehler, meistens eine Division durch 0." },
        { "ClassCastException", "Ein Objekt wurde in einen Typ umgewandelt, der es gar nicht ist." },
        { "ConcurrentModificationException", "Eine Liste darf nicht verändert werden, während eine for-each-Schleife über sie läuft." },
        { "NoSuchElementException", "Es wurde ein Element verlangt, das es nicht gibt (z.B. aus einer leeren Sammlung)." },
        { "NegativeArraySizeException", "Ein Array kann keine negative Größe haben." },
    };

    // ---------- Ausführen ----------

    public static String run(String code, String levelJson) {
        try {
            Map<String, Object> level = Json.map(Json.parse(levelJson));
            Map<String, byte[]> outs = new HashMap<>();
            Object[] err = compile(VORSPANN + absichern(code), outs);
            if (err != null) {
                Map<String, Object> r = new LinkedHashMap<>(), e = new LinkedHashMap<>();
                e.put("kind", "syntax"); e.put("line", err[0]); e.put("msg", erklaere((String) err[1]));
                r.put("error", e); r.put("output", ""); r.put("won", false);
                return Json.str(r);
            }
            Map<String, Object> r = lauf(code, level, outs);
            List<Object> tests = Json.list(level.get("varianten"));
            if (!tests.isEmpty()) {
                String hinweis = null;
                boolean ok = false;
                if (r.get("error") == null && Boolean.TRUE.equals(r.get("reached"))) {
                    for (Object o : tests) {
                        Map<String, Object> v = Json.map(o), lv = new LinkedHashMap<>(level);
                        for (String k : VARIABEL) if (v.containsKey(k)) lv.put(k, v.get(k));
                        Map<String, Object> t = lauf(code, lv, outs);
                        if (t.get("error") != null || !Boolean.TRUE.equals(t.get("reached"))) {
                            String grund = t.get("error") != null ? "Fehler: " + Json.map(t.get("error")).get("msg") : "Am Ende: " + t.get("fehlt") + ".";
                            hinweis = "Der Auftrag auf der Karte klappt. Dein Code muss aber auch bei anderen Aufträgen funktionieren.\nTest „" + v.get("text") + "“: " + grund;
                            break;
                        }
                    }
                    ok = hinweis == null;
                }
                Map<String, Object> c = new LinkedHashMap<>();
                c.put("label", "Klappt auch bei anderen Aufträgen (" + tests.size() + " Tests)"); c.put("ok", ok);
                Json.list(r.get("checks")).add(c);
                r.put("won", Boolean.TRUE.equals(r.get("won")) && ok);
                r.put("hinweis", hinweis);
            }
            return Json.str(r);
        } catch (Throwable t) {
            StringWriter sw = new StringWriter(); t.printStackTrace(new PrintWriter(sw));
            Map<String, Object> r = new LinkedHashMap<>(), e = new LinkedHashMap<>();
            e.put("kind", "runtime"); e.put("line", null); e.put("msg", "Interner Fehler im Spiel: " + sw);
            r.put("error", e); r.put("output", ""); r.put("won", false); r.put("events", new ArrayList<>()); r.put("checks", new ArrayList<>());
            return Json.str(r);
        }
    }

    static Map<String, Object> lauf(String code, Map<String, Object> level, final Map<String, byte[]> outs) throws Exception {
        Welt welt = new Welt(level);
        ClassLoader cl = new ClassLoader(Runner.class.getClassLoader()) {
            @Override protected Class<?> findClass(String n) throws ClassNotFoundException {
                byte[] b = outs.get(n); if (b == null) throw new ClassNotFoundException(n);
                return defineClass(n, b, 0, b.length);
            }
        };
        Method main = null;
        List<String> namen = new ArrayList<>(outs.keySet());
        namen.remove("Main"); namen.add(0, "Main");
        for (String n : namen) {
            if (!outs.containsKey(n)) continue;
            try { Method m = cl.loadClass(n).getDeclaredMethod("main", String[].class); if (Modifier.isStatic(m.getModifiers())) { main = m; break; } }
            catch (NoSuchMethodException e) { /* nächste Klasse */ }
        }
        Map<String, Object> error = null;
        ByteArrayOutputStream bo = new ByteArrayOutputStream();
        if (main == null) {
            error = new LinkedHashMap<>();
            error.put("kind", "runtime"); error.put("line", 1);
            error.put("msg", "Es fehlt die Startmethode. Java beginnt immer hier:\npublic static void main(String[] args) { ... }");
        } else {
            PrintStream alt = System.out;
            Welt.w = welt;
            System.setOut(new PrintStream(bo, true, "UTF-8"));
            try {
                main.setAccessible(true);
                main.invoke(null, (Object) new String[0]);
            } catch (InvocationTargetException ite) {
                Throwable e = ite.getCause();
                Integer line = null;
                if (System.getProperty("lager.marken") == null)   // die Tests schalten den Stacktrace ab, um die Merker zu prüfen
                    for (StackTraceElement st : e.getStackTrace()) if (DATEI.equals(st.getFileName())) { line = st.getLineNumber(); break; }
                if (line == null && welt.zeile > 0) line = welt.zeile;   // im Browser gibt es keine Zeilennummern im Stacktrace
                String name = e.getClass().getSimpleName();
                String msg = e instanceof Fehler ? e.getMessage() : name + (e.getMessage() != null ? ": " + e.getMessage() : "");
                for (String[] h : HINWEISE) if (h[0].equals(name)) msg += "\n" + h[1];
                error = new LinkedHashMap<>();
                error.put("kind", "runtime"); error.put("line", line); error.put("msg", msg);
            } finally {
                System.setOut(alt);
                Welt.w = null;
            }
        }
        String plain = code.replaceAll("(?s)/\\*.*?\\*/", "").replaceAll("//.*", "");
        List<Object> checks = new ArrayList<>();
        boolean alle = true;
        for (String art : new String[] { "needs", "verboten" }) for (Object o : Json.list(level.get(art))) {
            Map<String, Object> n = Json.map(o), c = new LinkedHashMap<>();
            boolean ok = Pattern.compile((String) n.get("pattern"), Pattern.MULTILINE).matcher(plain).find() == art.equals("needs");
            c.put("label", n.get("label")); c.put("ok", ok);
            checks.add(c); alle &= ok;
        }
        Map<String, Object> ziel = Json.map(level.get("ziel"));
        if (ziel.containsKey("max_lies")) {
            int max = Json.num(ziel.get("max_lies"));
            Map<String, Object> c = new LinkedHashMap<>();
            boolean ok = welt.liesAnzahl <= max && welt.liesAnzahl > 0;
            c.put("label", "Höchstens " + max + "-mal lies() (bisher " + welt.liesAnzahl + ")"); c.put("ok", ok);
            checks.add(c); alle &= ok;
        }
        boolean exakt = Boolean.TRUE.equals(level.get("exakt"));
        String fehlt = welt.fehlt(ziel, exakt);
        List<String> zuviel = new ArrayList<>();
        for (String k : new String[] { "kiste", "fass" })
            if (exakt && ziel.containsKey(k) && welt.stock.getOrDefault(k, 0) > Json.num(ziel.get(k))) zuviel.add(k);
        String out = bo.toString("UTF-8");
        Map<String, Object> r = new LinkedHashMap<>();
        r.put("error", error);
        r.put("output", out.length() > 2000 ? out.substring(0, 2000) : out);
        r.put("checks", checks);
        r.put("won", fehlt == null && error == null && alle);
        r.put("reached", fehlt == null);
        r.put("zuviel", zuviel);
        r.put("events", welt.events);
        r.put("carried", welt.carry.size());
        r.put("fehlt", fehlt);
        return r;
    }

    /** Für build.py und test.py: liest eine JSON-Liste von [code, level] und schreibt die Ergebnisse als JSON-Liste. */
    public static void main(String[] args) throws Exception {
        String in = new String(System.in.readAllBytes(), StandardCharsets.UTF_8);
        StringBuilder sb = new StringBuilder("[");
        for (Object o : Json.list(Json.parse(in))) {
            List<Object> job = Json.list(o);
            if (sb.length() > 1) sb.append(",\n");
            sb.append(run((String) job.get(0), Json.str(job.get(1))));
        }
        new PrintStream(new FileOutputStream(FileDescriptor.out), true, "UTF-8").println(sb.append("]"));
    }
}
