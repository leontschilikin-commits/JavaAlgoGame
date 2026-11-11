from textwrap import dedent

W, H = 10, 7
RAMPE = (0, 3)


def karte(**arten):
    """Baut eine Karte: karte(K=[(4, 3)], F=[...], C=[(9, 3)])."""
    rows = [["."] * W for _ in range(H)]
    rows[RAMPE[1]][RAMPE[0]] = "L"
    for ch, felder in arten.items():
        for x, y in felder:
            rows[y][x] = ch
    return ["".join(r) for r in rows]


def reihe(**arten):
    """Karte mit Feldern nur in der Reihe y = 3, z.B. reihe(K=[1, 4], F=[2])."""
    return karte(**{ch: [(x, 3) for x in xs] for ch, xs in arten.items()})


def regal(n):
    """Karte mit einem Regal aus n Fächern in der Reihe y = 1. Der Lagerist steht davor in der Reihe y = 2."""
    return karte(R=[(x, 1) for x in range(1, n + 1)])


def java(code):
    return dedent(code).lstrip("\n")


def main(body, vor="", imports=""):
    """Packt Anweisungen in public class Main { main }. vor: Methoden oder Felder in Main, imports: Zeilen ganz oben."""
    ein = lambda text, n: "".join((" " * n + z if z.strip() else "") + "\n" for z in dedent(text).strip("\n").split("\n"))
    return (imports + "\n" if imports else "") + "public class Main {\n" + (ein(vor, 4) + "\n" if vor else "") + \
        "    public static void main(String[] args) {\n" + ein(body, 8) + "    }\n}\n"


FOR = {"pattern": r"\bfor\s*\(", "label": "Benutze eine for-Schleife"}
WHILE = {"pattern": r"\bwhile\s*\(", "label": "Benutze eine while-Schleife"}
IF = {"pattern": r"\bif\s*\(", "label": "Benutze if"}
METHODE = {"pattern": r"static\s+\w+\s+(?!main\b)\w+\s*\(\s*\w+\s+\w+", "label": "Schreibe eine eigene Methode mit Parameter"}
EQUALS = {"pattern": r"\.equals\s*\(", "label": "Vergleiche Text mit .equals(...)"}
KLASSE = {"pattern": r"\bclass\s+(?!Main\b)\w+", "label": "Schreibe eine eigene Klasse"}
NEW = {"pattern": r"\bnew\s+(?!Main\b)[A-Z]\w*\s*\(", "label": "Erzeuge Objekte mit new"}
PRIVATE = {"pattern": r"\bprivate\b", "label": "Mach die Felder private"}
THIS = {"pattern": r"\bthis\.", "label": "Setze die Felder im Konstruktor mit this"}
EXTENDS = {"pattern": r"\bclass\s+\w+\s+extends\s+\w+", "label": "Leite eine Klasse mit extends ab"}
OVERRIDE = {"pattern": r"@Override", "label": "Überschreibe eine Methode mit @Override"}
SUPER = {"pattern": r"\bsuper\s*\(", "label": "Rufe den Konstruktor der Oberklasse mit super(...) auf"}
COMPARABLE = {"pattern": r"implements\s+Comparable\s*<", "label": "Implementiere das Interface Comparable"}
COMPARETO = {"pattern": r"\bcompareTo\s*\(", "label": "Schreibe die Methode compareTo"}
GENERISCH = {"pattern": r"\bclass\s+\w+\s*<\s*\w+\s*>", "label": "Schreibe eine generische Klasse (z.B. class Stapel<T>)"}
MIT_FELD = {"pattern": r"\b(?!List\b|ArrayList\b)[A-Z]\w*\s*<\s*Feld\s*>", "label": "Benutze deine Klasse mit dem Typ Feld"}
HASHMAP = {"pattern": r"\bHashMap\s*<", "label": "Benutze eine HashMap"}
PUT = {"pattern": r"\.put\s*\(", "label": "Schreibe mit .put(...) in die Map"}
LAMBDA = {"pattern": r"->", "label": "Benutze einen Lambda-Ausdruck (->)"}
STREAM = {"pattern": r"\.stream\s*\(\s*\)", "label": "Benutze .stream()"}
FILTER = {"pattern": r"\.filter\s*\(", "label": "Benutze .filter(...)"}
SORTED = {"pattern": r"\.sorted\s*\(", "label": "Benutze .sorted(...)"}
LIES = {"pattern": r"\blies\s*\(", "label": "Lies die Fächer mit lies(...)"}
RETURN = {"pattern": r"\breturn\b", "label": "Gib mit return ein Ergebnis zurück"}
KNOTEN = {"pattern": r"\bclass\s+Knoten\b", "label": "Schreibe eine Klasse Knoten"}
NEXT = {"pattern": r"\.next\b", "label": "Verkette die Knoten über das Feld next"}
ZWEI_KINDER = {"pattern": r"Knoten\s+\w+\s*,\s*\w+\s*;|Knoten\s+\w+\s*;\s*Knoten\s+\w+\s*;", "label": "Gib jedem Knoten zwei Kinder"}
INORDER = {"pattern": r"(\w+)\s*\(\s*Knoten\s+\w+\s*\)\s*\{[\s\S]*?\b\1\s*\([\s\S]*?\b\1\s*\(", "label": "Durchlaufe den Baum mit einer rekursiven Methode"}
MODULO = {"pattern": r"%", "label": "Berechne das Fach mit dem Rest-Operator %"}
TAUSCHE = {"pattern": r"\btausche\s*\(", "label": "Sortiere mit tausche(...)"}
REKURSIV2 = {"pattern": r"(\w+)\s*\(\s*int\s+\w+\s*,\s*int\s+\w+\s*\)\s*\{[\s\S]*?\b\1\s*\([\s\S]*?\b\1\s*\(",
             "label": "Schreibe eine rekursive Methode mit zwei Grenzen (von, bis)"}

OHNE_LAMBDA = {"pattern": r"->|\bComparator\b", "label": "Noch ohne Lambda und Comparator"}
OHNE_HILFEN = {"pattern": r"Collections\.reverse|\bStack\b|Deque|\.reversed\s*\(|\.sort\s*\(|\.sorted\s*\(", "label": "Ohne fertige Hilfen wie Stack, sort oder reverse"}
OHNE_STREAM = {"pattern": r"\.stream\s*\(|implements\s+Comparable", "label": "Ohne Streams und ohne Comparable"}
OHNE_SCHLEIFE = {"pattern": r"\bfor\s*\(|\bwhile\s*\(|\bdo\b", "label": "Ganz ohne for und while"}
OHNE_SAMMLUNG = {"pattern": r"ArrayList|LinkedList|\.sort\s*\(|\.sorted\s*\(|Collections|\.stream\s*\(|TreeMap|TreeSet|PriorityQueue|\bArrays\b",
                 "label": "Nur deine eigene Datenstruktur, keine fertigen Sammlungen und kein sort"}

# id, Name, Icon, Preis, Text, nötig für Level (0-basiert) oder None
SHOP = [
    {"id": "scanner", "name": "Scanner", "icon": "🔦", "preis": {"taler": 10}, "level": 3,
     "text": "Schaltet wasIstHier() frei: Dein Lagerist erkennt, ob vor ihm eine Kiste oder ein Fass steht."},
    {"id": "hubwagen", "name": "Hubwagen", "icon": "🛒", "preis": {"taler": 12}, "level": 4,
     "text": "Schaltet finde(), findeAlles(), geheZu(), zurRampe() und zumKuehlraum() frei."},
    {"id": "terminal", "name": "Regal-Terminal", "icon": "🖥️", "preis": {"taler": 30}, "level": 11,
     "text": "Schaltet das Regal frei: lies(), tausche(), stelle(), istFachFrei() und regalGroesse(). Damit beginnt Welt 2."},
    {"id": "kompass", "name": "Kompass", "icon": "🧭", "preis": {"taler": 20}, "level": 14,
     "text": "Schaltet istFrei(richtung) und gehe(richtung) frei. Damit findest du durchs Labyrinth."},
    {"id": "sackkarre", "name": "Sackkarre", "icon": "🎒", "preis": {"taler": 15}, "level": None,
     "text": "Dein Lagerist trägt 1 Stück mehr."},
    {"id": "rollschuhe", "name": "Rollschuhe", "icon": "🛼", "preis": {"taler": 12}, "level": None,
     "text": "Dein Lagerist läuft sichtbar schneller."},
    {"id": "flagge", "name": "Rampen-Ausbau", "icon": "🚩", "preis": {"taler": 25}, "level": None,
     "text": "Deine Rampe bekommt ein Vordach und eine Flagge. Reine Angeberei."},
]

LEER = main("")

LEVELS = [
    {
        "title": "Die erste Kiste",
        "task": "Geh zur Kiste, nimm sie und bring sie zur Rampe.",
        "lesson": "Das ist dein Lagerist. Er macht genau das, was in <code>main</code> steht, Anweisung für Anweisung. Jeder Befehl ist ein <b>Methodenaufruf</b> mit Klammern, und jede Anweisung endet mit einem <b>Semikolon</b>:"
                  "<pre>rechts();     // ein Feld nach rechts\nnimm();       // die Kiste hier aufheben\nabliefern();  // an der Rampe abgeben</pre>"
                  "Mit <code>links()</code> kommt er zurück. Java-Code steht immer in einer Klasse, und das Programm startet in <code>main</code>. Für jeden Auftrag bekommst du Taler für den Shop.",
        "tip": "Viermal rechts(); einmal nimm(); viermal links(); einmal abliefern();",
        "grid": karte(K=[(4, 3)]),
        "tragkraft": 1, "ziel": {"kiste": 1}, "belohnung": {"taler": 4}, "needs": [],
        "start": main("rechts();"),
        "solution": main("""
            rechts();
            rechts();
            rechts();
            rechts();
            nimm();
            links();
            links();
            links();
            links();
            abliefern();
        """),
        "warum": "Der Weg ist schon der kürzeste: 10 Aktionen. Mit der for-Schleife aus dem nächsten Level wird nur der Code kürzer, nicht der Weg.",
    },
    {
        "title": "Weit weg: for und int",
        "task": "Hol die Kiste oben rechts. Nutze for-Schleifen statt alles einzeln zu tippen.",
        "lesson": "Eine <b>for-Schleife</b> wiederholt ihren Block. In den runden Klammern stehen drei Teile: Startwert, Bedingung, Schritt."
                  "<pre>for (int i = 0; i < 7; i++) {\n    rechts();\n}</pre>"
                  "<code>int i = 0</code> legt eine <b>Variable</b> vom Typ <code>int</code> (ganze Zahl) an. In Java hat jede Variable einen festen Typ. <code>i++</code> zählt um 1 hoch. Neu sind auch <code>hoch()</code> und <code>runter()</code>.",
        "tip": "Die Kiste steht 7 nach rechts und 2 nach oben. Danach denselben Weg zurück.",
        "grid": karte(K=[(7, 1)]),
        "tragkraft": 1, "ziel": {"kiste": 1}, "belohnung": {"taler": 5}, "needs": [FOR],
        "start": main("""
            for (int i = 0; i < 7; i++) {
                rechts();
            }
        """),
        "solution": main("""
            for (int i = 0; i < 7; i++) {
                rechts();
            }
            hoch();
            hoch();
            nimm();
            runter();
            runter();
            for (int i = 0; i < 7; i++) {
                links();
            }
            abliefern();
        """),
        "warum": "Hin- und Rückweg sind die kürzesten Wege. Die Schleife läuft 7-mal, egal wie lang der Code ist: Der Aufwand hängt von der Zahl der Wiederholungen ab, nicht von der Zahl der Zeilen.",
    },
    {
        "title": "Methoden mit Parametern",
        "task": "Drei Kisten stehen 3, 5 und 7 Felder rechts der Rampe. Dein Lagerist trägt nur 1 Kiste. Schreibe eine Methode für eine Runde und rufe sie dreimal auf.",
        "lesson": "Wiederholt sich ein Ablauf, gibst du ihm als <b>Methode</b> einen Namen. Vor dem Namen steht der Rückgabetyp (<code>void</code> heißt: gibt nichts zurück), in den Klammern stehen die <b>Parameter</b> mit ihrem Typ:"
                  "<pre>static void gruesse(String name, int anzahl) {\n    for (int i = 0; i < anzahl; i++) {\n        System.out.println(\"Hallo \" + name);\n    }\n}</pre>"
                  "Aufgerufen wird sie mit <code>gruesse(\"Mia\", 2);</code>. Weil <code>main</code> selbst <code>static</code> ist, müssen deine Methoden hier auch <code>static</code> sein.",
        "tip": "In hole(int weg) gehören: weg-mal rechts(), nimm(), weg-mal links(), abliefern(). In main dann hole(3); hole(5); hole(7);",
        "grid": reihe(K=[3, 5, 7]),
        "tragkraft": 1, "ziel": {"kiste": 3}, "belohnung": {"taler": 6}, "needs": [METHODE],
        "next": "Du hast genug verdient: Kauf im Shop den Scanner für das nächste Level!",
        "start": main("hole(3);", vor="""
            static void hole(int weg) {
                for (int i = 0; i < weg; i++) {
                    rechts();
                }
            }
        """),
        "solution": main("""
            hole(3);
            hole(5);
            hole(7);
        """, vor="""
            static void hole(int weg) {
                for (int i = 0; i < weg; i++) {
                    rechts();
                }
                nimm();
                for (int i = 0; i < weg; i++) {
                    links();
                }
                abliefern();
            }
        """),
        "warum": "Er trägt nur 1 Kiste, also braucht jede Kiste ihre eigene Runde. Die Methode spart dir, denselben Ablauf dreimal zu schreiben.",
    },
    {
        "title": "Kiste oder Fass: if und equals",
        "task": "In der Reihe bis x = 7 stehen Kisten und Fässer durcheinander. Bestellt sind genau die 3 Kisten. Die Fässer bleiben stehen.",
        "lesson": "<code>wasIstHier()</code> liefert einen <b>String</b>: <code>\"kiste\"</code>, <code>\"fass\"</code>, <code>\"rampe\"</code> oder <code>\"leer\"</code>. Mit <b>if</b> entscheidet dein Code:"
                  "<pre>String wetter = \"regen\";\nif (wetter.equals(\"regen\")) {\n    System.out.println(\"Schirm\");\n} else {\n    System.out.println(\"Sonnenbrille\");\n}</pre>"
                  "Achtung, typische Java-Falle: Strings vergleicht man mit <code>.equals(...)</code>, nicht mit <code>==</code>. <code>==</code> prüft bei Objekten nur, ob es dasselbe Objekt ist.",
        "tip": "Eine for-Schleife über 7 Felder: rechts(); dann if (wasIstHier().equals(\"kiste\")) { nimm(); }. Danach 7-mal links() und abliefern().",
        "grid": reihe(K=[1, 4, 6], F=[2, 5]),
        "tragkraft": 3, "exakt": True, "ziel": {"kiste": 3, "fass": 0}, "belohnung": {"taler": 8}, "needs": [IF, EQUALS],
        "varianten": [{"text": "andere Reihenfolge in der Reihe", "grid": reihe(K=[2, 3, 7], F=[1, 5, 6])},
                      {"text": "noch eine Reihenfolge", "grid": reihe(K=[1, 2, 5], F=[3, 4, 7])}],
        "braucht": ["scanner"],
        "next": "Mit dem Hubwagen aus dem Shop findet dein Lagerist Kisten in der ganzen Halle.",
        "start": main("""
            for (int i = 0; i < 7; i++) {
                rechts();
                System.out.println(wasIstHier());
            }
        """),
        "solution": main("""
            for (int i = 0; i < 7; i++) {
                rechts();
                if (wasIstHier().equals("kiste")) {
                    nimm();
                }
            }
            for (int i = 0; i < 7; i++) {
                links();
            }
            abliefern();
        """),
        "warum": "Ein Durchlauf über die Reihe reicht: Jedes Feld wird genau einmal geprüft. Das ist linearer Aufwand, O(n).",
    },
    {
        "title": "Klassen und Objekte",
        "task": "Drei Kisten stehen verstreut in der Halle, er trägt nur 1. Schreibe eine Klasse Tour, die sich ihr Ziel merkt, und erzeuge für jede Kiste ein Objekt.",
        "lesson": "Eine <b>Klasse</b> ist ein Bauplan: Sie legt fest, welche Daten (<b>Felder</b>) ein Objekt hat und was es kann (<b>Methoden</b>). Der <b>Konstruktor</b> heißt wie die Klasse und füllt die Felder. <code>this.name</code> meint das Feld, <code>name</code> den Parameter. Mit <code>private</code> sind Felder von außen nicht sichtbar (Kapselung)."
                  "<pre>class Hund {\n    private String name;\n\n    Hund(String name) {\n        this.name = name;\n    }\n\n    void belle() {\n        System.out.println(name + \": Wuff\");\n    }\n}</pre>"
                  "Ein Objekt erzeugst du mit <code>new</code>: <code>Hund h = new Hund(\"Rex\"); h.belle();</code>. Neu vom Hubwagen: <code>geheZu(x, y)</code> und <code>zurRampe()</code>.",
        "tip": "Tour bekommt private int x und y, einen Konstruktor Tour(int x, int y) und eine Methode fahre(): geheZu(x, y); nimm(); zurRampe(); abliefern();. Die Kisten stehen auf (3, 1), (6, 5) und (8, 2).",
        "grid": karte(K=[(3, 1), (8, 2), (6, 5)]),
        "tragkraft": 1, "ziel": {"kiste": 3}, "belohnung": {"taler": 8}, "needs": [KLASSE, PRIVATE, THIS, NEW],
        "braucht": ["hubwagen"],
        "start": java("""
            class Tour {
                private int x;
                private int y;

                Tour(int x, int y) {
                    this.x = x;
                }

                void fahre() {
                    geheZu(x, y);
                }
            }

            public class Main {
                public static void main(String[] args) {
                    Tour erste = new Tour(3, 1);
                    erste.fahre();
                }
            }
        """),
        "solution": java("""
            class Tour {
                private int x;
                private int y;

                Tour(int x, int y) {
                    this.x = x;
                    this.y = y;
                }

                void fahre() {
                    geheZu(x, y);
                    nimm();
                    zurRampe();
                    abliefern();
                }
            }

            public class Main {
                public static void main(String[] args) {
                    Tour erste = new Tour(3, 1);
                    erste.fahre();
                    new Tour(6, 5).fahre();
                    new Tour(8, 2).fahre();
                }
            }
        """),
        "warum": "Jedes Tour-Objekt trägt seine eigenen Daten. Die Wege sind schon minimal, die Klasse macht den Code nur übersichtlicher: Daten und Verhalten stehen zusammen.",
    },
    {
        "title": "Vererbung: Der Kühlraum",
        "task": "Kisten gehören an die Rampe, Fässer in den Kühlraum ganz rechts. Er trägt nur 1 Stück. Leite von Auftrag eine Klasse KuehlAuftrag ab, die nur das Abliefern anders macht.",
        "lesson": "Mit <b>extends</b> erbt eine Klasse alle Felder und Methoden ihrer Oberklasse und kann einzelne Methoden <b>überschreiben</b>. <code>super(...)</code> ruft den Konstruktor der Oberklasse auf, denn Konstruktoren werden nicht vererbt."
                  "<pre>class Tier {\n    protected String name;\n    Tier(String name) { this.name = name; }\n    void sprich() { System.out.println(name + \" macht ein Geräusch\"); }\n}\n\nclass Katze extends Tier {\n    Katze(String name) { super(name); }\n    @Override\n    void sprich() { System.out.println(name + \": Miau\"); }\n}</pre>"
                  "Jede Katze <b>ist ein</b> Tier: <code>Tier t = new Katze(\"Mia\");</code> ist erlaubt. Der statische Typ ist Tier, der dynamische Katze, und <code>t.sprich()</code> ruft die Version der Katze auf (dynamische Bindung). <code>protected</code> erlaubt Unterklassen den Zugriff.",
        "tip": "KuehlAuftrag extends Auftrag: Konstruktor mit super(x, y); und @Override void liefere() { zumKuehlraum(); abliefern(); }. In main ein Array Auftrag[] mit beiden Sorten: Kisten auf (3, 1) und (5, 5), Fässer auf (6, 1) und (2, 5).",
        "grid": karte(K=[(3, 1), (5, 5)], F=[(6, 1), (2, 5)], C=[(9, 3)]),
        "tragkraft": 1, "ziel": {"kiste": 2, "fass": 2}, "belohnung": {"taler": 9}, "needs": [EXTENDS, SUPER, OVERRIDE],
        "braucht": ["hubwagen"],
        "start": java("""
            class Auftrag {
                protected int x;
                protected int y;

                Auftrag(int x, int y) {
                    this.x = x;
                    this.y = y;
                }

                void liefere() {
                    zurRampe();
                    abliefern();
                }

                void erledige() {
                    geheZu(x, y);
                    nimm();
                    liefere();
                }
            }

            public class Main {
                public static void main(String[] args) {
                    Auftrag[] liste = { new Auftrag(3, 1), new Auftrag(5, 5) };
                    for (Auftrag a : liste) {
                        a.erledige();
                    }
                }
            }
        """),
        "solution": java("""
            class Auftrag {
                protected int x;
                protected int y;

                Auftrag(int x, int y) {
                    this.x = x;
                    this.y = y;
                }

                void liefere() {
                    zurRampe();
                    abliefern();
                }

                void erledige() {
                    geheZu(x, y);
                    nimm();
                    liefere();
                }
            }

            class KuehlAuftrag extends Auftrag {
                KuehlAuftrag(int x, int y) {
                    super(x, y);
                }

                @Override
                void liefere() {
                    zumKuehlraum();
                    abliefern();
                }
            }

            public class Main {
                public static void main(String[] args) {
                    Auftrag[] liste = { new Auftrag(3, 1), new KuehlAuftrag(6, 1), new Auftrag(5, 5), new KuehlAuftrag(2, 5) };
                    for (Auftrag a : liste) {
                        a.erledige();
                    }
                }
            }
        """),
        "warum": "Die Schleife kennt nur den Typ Auftrag und ruft trotzdem die richtige liefere()-Methode auf. Das ist Polymorphie: Eine neue Sorte Auftrag braucht nur eine neue Unterklasse, die Schleife bleibt gleich.",
    },
    {
        "title": "Interfaces: Comparable",
        "task": "Der LKW will die Kisten nach Nummer aufsteigend. Er trägt nur 1. Schreibe eine Klasse Paket, die Comparable implementiert, und sortiere mit Collections.sort.",
        "lesson": "Ein <b>Interface</b> ist ein Vertrag: Es nennt Methoden, die eine Klasse anbieten muss. <code>Comparable&lt;T&gt;</code> verlangt <code>compareTo</code>: negativ heißt „ich komme vor dem anderen“, 0 gleich, positiv danach. Dann kann <code>Collections.sort</code> deine Objekte sortieren."
                  "<pre>class Buch implements Comparable&lt;Buch&gt; {\n    int seiten;\n    Buch(int seiten) { this.seiten = seiten; }\n\n    @Override\n    public int compareTo(Buch other) {\n        return this.seiten - other.seiten;\n    }\n}</pre>"
                  "<code>finde(\"kiste\")</code> liefert eine <code>List&lt;Feld&gt;</code>. Ein <code>Feld</code> hat <code>x</code>, <code>y</code>, <code>art</code> und <code>nummer</code>, und <code>geheZu(feld)</code> läuft direkt hin.",
        "tip": "Paket merkt sich ein Feld. compareTo: return this.feld.nummer - other.feld.nummer;. In main: alle Felder in eine ArrayList<Paket> packen, Collections.sort(pakete), dann der Reihe nach holen.",
        "grid": karte(K=[(7, 0), (2, 1), (8, 4), (5, 5)]),
        "nummern": [40, 10, 30, 20],
        "tragkraft": 1, "ziel": {"folge": [10, 20, 30, 40]}, "belohnung": {"taler": 9}, "needs": [COMPARABLE, COMPARETO], "verboten": [OHNE_LAMBDA],
        "varianten": [{"text": "andere Nummern auf den Kisten", "nummern": [5, 80, 60, 7], "ziel": {"folge": [5, 7, 60, 80]}},
                      {"text": "die Kisten sind schon fast sortiert", "nummern": [11, 12, 14, 13], "ziel": {"folge": [11, 12, 13, 14]}}],
        "braucht": ["hubwagen"],
        "start": java("""
            import java.util.*;

            class Paket {
                Feld feld;

                Paket(Feld feld) {
                    this.feld = feld;
                }
            }

            public class Main {
                public static void main(String[] args) {
                    List<Paket> pakete = new ArrayList<>();
                    for (Feld f : finde("kiste")) {
                        System.out.println(f);
                        pakete.add(new Paket(f));
                    }
                }
            }
        """),
        "solution": java("""
            import java.util.*;

            class Paket implements Comparable<Paket> {
                Feld feld;

                Paket(Feld feld) {
                    this.feld = feld;
                }

                @Override
                public int compareTo(Paket other) {
                    return this.feld.nummer - other.feld.nummer;
                }
            }

            public class Main {
                public static void main(String[] args) {
                    List<Paket> pakete = new ArrayList<>();
                    for (Feld f : finde("kiste")) {
                        pakete.add(new Paket(f));
                    }
                    Collections.sort(pakete);
                    for (Paket p : pakete) {
                        geheZu(p.feld);
                        nimm();
                        zurRampe();
                        abliefern();
                    }
                }
            }
        """),
        "warum": "Die Reihenfolge ist vorgeschrieben, also sind die Wege fest. Collections.sort braucht O(n log n) Vergleiche und ruft dafür nur deine compareTo-Methode auf.",
    },
    {
        "title": "Generics: Der Stapel",
        "task": "finde() liefert die Kisten hier schon aufsteigend. Der LKW wird aber von hinten beladen: Die größte Nummer muss zuerst an die Rampe. Schreibe einen generischen Stapel<T> und dreh damit die Reihenfolge um.",
        "lesson": "Mit <b>Generics</b> schreibst du eine Klasse einmal für beliebige Typen. <code>T</code> ist ein Platzhalter (Typparameter), der beim Benutzen festgelegt wird. Der Compiler prüft dann, dass nur der richtige Typ hineinkommt, und du brauchst keine Typumwandlung."
                  "<pre>class Paar&lt;T&gt; {\n    private T erstes;\n    private T zweites;\n\n    Paar(T erstes, T zweites) {\n        this.erstes = erstes;\n        this.zweites = zweites;\n    }\n\n    T gibErstes() { return erstes; }\n}\n\nPaar&lt;String&gt; p = new Paar&lt;&gt;(\"links\", \"rechts\");</pre>"
                  "Ein <b>Stapel</b> (Stack) arbeitet nach dem Prinzip LIFO: Was zuletzt hineinkam, kommt zuerst heraus.",
        "tip": "Stapel<T> hält eine private ArrayList<T>. push hängt hinten an, pop entfernt das letzte Element: inhalt.remove(inhalt.size() - 1). In main: alle Felder pushen, dann solange !stapel.istLeer() eines poppen und holen.",
        "grid": karte(K=[(4, 0), (7, 1), (2, 2), (6, 4), (3, 6)]),
        "nummern": [3, 8, 15, 21, 34],
        "tragkraft": 1, "ziel": {"folge": [34, 21, 15, 8, 3]}, "belohnung": {"taler": 10}, "needs": [GENERISCH, MIT_FELD], "verboten": [OHNE_HILFEN],
        "varianten": [{"text": "vier Kisten an anderen Plätzen", "grid": karte(K=[(8, 0), (3, 1), (5, 4), (7, 6)]), "nummern": [2, 4, 6, 9], "ziel": {"folge": [9, 6, 4, 2]}}],
        "braucht": ["hubwagen"],
        "start": java("""
            import java.util.*;

            class Stapel<T> {
                private ArrayList<T> inhalt = new ArrayList<>();

                void push(T element) {
                    inhalt.add(element);
                }

                boolean istLeer() {
                    return inhalt.isEmpty();
                }
            }

            public class Main {
                public static void main(String[] args) {
                    Stapel<Feld> stapel = new Stapel<>();
                    for (Feld f : finde("kiste")) {
                        stapel.push(f);
                    }
                }
            }
        """),
        "solution": java("""
            import java.util.*;

            class Stapel<T> {
                private ArrayList<T> inhalt = new ArrayList<>();

                void push(T element) {
                    inhalt.add(element);
                }

                T pop() {
                    return inhalt.remove(inhalt.size() - 1);
                }

                boolean istLeer() {
                    return inhalt.isEmpty();
                }
            }

            public class Main {
                public static void main(String[] args) {
                    Stapel<Feld> stapel = new Stapel<>();
                    for (Feld f : finde("kiste")) {
                        stapel.push(f);
                    }
                    while (!stapel.istLeer()) {
                        Feld f = stapel.pop();
                        geheZu(f);
                        nimm();
                        zurRampe();
                        abliefern();
                    }
                }
            }
        """),
        "warum": "push und pop arbeiten beide am Ende der ArrayList und kosten deshalb O(1). Würdest du vorne einfügen, müsste die Liste jedes Mal alle Elemente verschieben: O(n).",
    },
    {
        "title": "Inventur: HashMap",
        "task": "In der Halle stehen Kisten und Fässer. Zähle mit einer HashMap, wie viele es von jeder Art gibt, und liefere nur die Art ab, von der es mehr gibt. Alles kommt hier an die Rampe.",
        "lesson": "Die <b>Collections</b> sind Javas fertige Datenstrukturen: <code>List</code> (Reihenfolge, Index), <code>Set</code> (keine Duplikate) und <code>Map</code> (Schlüssel → Wert). Eine <code>HashMap</code> findet einen Wert über seinen Schlüssel im Schnitt in O(1)."
                  "<pre>Map&lt;String, Integer&gt; zettel = new HashMap&lt;&gt;();\nfor (String obst : List.of(\"apfel\", \"birne\", \"apfel\")) {\n    zettel.put(obst, zettel.getOrDefault(obst, 0) + 1);\n}\nSystem.out.println(zettel);              // {apfel=2, birne=1}\nSystem.out.println(zettel.get(\"apfel\"));  // 2</pre>"
                  "In spitzen Klammern stehen nur Klassen, darum <code>Integer</code> statt <code>int</code>. <code>keySet()</code> liefert alle Schlüssel. <code>findeAlles()</code> liefert Kisten und Fässer zusammen, <code>feld.art</code> ist die Art.",
        "tip": "Für jedes Feld aus findeAlles(): anzahl.put(f.art, anzahl.getOrDefault(f.art, 0) + 1). Dann den Schlüssel mit dem größten Wert suchen, alle Felder aus finde(meiste) einsammeln, zurRampe(), abliefern().",
        "grid": karte(K=[(3, 0), (7, 2), (4, 5)], F=[(5, 1), (8, 5)]),
        "tragkraft": 6, "exakt": True, "ziel": {"kiste": 3, "fass": 0}, "belohnung": {"taler": 10}, "needs": [HASHMAP, PUT],
        "varianten": [{"text": "2 Kisten und 4 Fässer", "grid": karte(K=[(2, 1), (6, 6)], F=[(4, 0), (8, 1), (5, 4), (3, 5)]), "ziel": {"kiste": 0, "fass": 4}},
                      {"text": "5 Kisten und 1 Fass", "grid": karte(K=[(2, 0), (7, 1), (4, 2), (8, 4), (5, 5)], F=[(3, 6)]), "ziel": {"kiste": 5, "fass": 0}}],
        "braucht": ["hubwagen"],
        "start": java("""
            import java.util.*;

            public class Main {
                public static void main(String[] args) {
                    Map<String, Integer> anzahl = new HashMap<>();
                    for (Feld f : findeAlles()) {
                        System.out.println(f.art);
                    }
                    System.out.println(anzahl);
                }
            }
        """),
        "solution": java("""
            import java.util.*;

            public class Main {
                public static void main(String[] args) {
                    Map<String, Integer> anzahl = new HashMap<>();
                    for (Feld f : findeAlles()) {
                        anzahl.put(f.art, anzahl.getOrDefault(f.art, 0) + 1);
                    }
                    String meiste = "";
                    for (String art : anzahl.keySet()) {
                        if (meiste.isEmpty() || anzahl.get(art) > anzahl.get(meiste)) {
                            meiste = art;
                        }
                    }
                    for (Feld f : finde(meiste)) {
                        geheZu(f);
                        nimm();
                    }
                    zurRampe();
                    abliefern();
                }
            }
        """),
        "warum": "Die Map zählt in einem einzigen Durchlauf, O(n), egal wie viele Arten es gibt. Ohne Map bräuchtest du für jede Art einen eigenen Zähler.",
    },
    {
        "title": "Lambdas: Sortieren nach Wunsch",
        "task": "Liefere die Kisten nach Nummer aufsteigend, aber nur die mit einer Nummer unter 50. Er trägt nur 1. Benutze Lambda-Ausdrücke statt einer eigenen Klasse.",
        "lesson": "Ein <b>Lambda-Ausdruck</b> ist eine Methode ohne Namen, die du wie einen Wert übergibst: links die Parameter, dann <code>-&gt;</code>, rechts das Ergebnis. Er passt überall, wo ein <b>funktionales Interface</b> erwartet wird, also ein Interface mit genau einer abstrakten Methode (z.B. <code>Comparator</code> oder <code>Predicate</code>)."
                  "<pre>List&lt;String&gt; namen = new ArrayList&lt;&gt;(List.of(\"Tom\", \"Alexander\", \"Mia\", \"Jo\"));\nnamen.removeIf(n -&gt; n.length() &lt; 3);                // Predicate: wahr oder falsch\nnamen.sort((a, b) -&gt; a.length() - b.length());     // Comparator: wie compareTo\nnamen.forEach(n -&gt; System.out.println(n));         // Consumer: tut etwas</pre>"
                  "Die Typen der Parameter erkennt der Compiler selbst.",
        "tip": "List<Feld> kisten = finde(\"kiste\"); dann kisten.removeIf(f -> f.nummer >= 50); und kisten.sort((a, b) -> a.nummer - b.nummer);. Danach der Reihe nach holen.",
        "grid": karte(K=[(3, 0), (8, 1), (5, 2), (2, 4), (7, 5), (4, 6)]),
        "nummern": [70, 20, 90, 10, 40, 60],
        "tragkraft": 1, "ziel": {"folge": [10, 20, 40]}, "belohnung": {"taler": 10}, "needs": [LAMBDA], "verboten": [OHNE_STREAM],
        "varianten": [{"text": "andere Nummern auf den Kisten", "nummern": [49, 50, 3, 99, 51, 12], "ziel": {"folge": [3, 12, 49]}},
                      {"text": "nur eine Kiste unter 50", "nummern": [88, 77, 66, 55, 44, 99], "ziel": {"folge": [44]}}],
        "braucht": ["hubwagen"],
        "start": java("""
            import java.util.*;

            public class Main {
                public static void main(String[] args) {
                    List<Feld> kisten = finde("kiste");
                    kisten.forEach(f -> System.out.println(f));
                }
            }
        """),
        "solution": java("""
            import java.util.*;

            public class Main {
                public static void main(String[] args) {
                    List<Feld> kisten = finde("kiste");
                    kisten.removeIf(f -> f.nummer >= 50);
                    kisten.sort((a, b) -> a.nummer - b.nummer);
                    for (Feld f : kisten) {
                        geheZu(f);
                        nimm();
                        zurRampe();
                        abliefern();
                    }
                }
            }
        """),
        "warum": "Erst filtern, dann sortieren: So muss sort weniger Elemente vergleichen. Der Lambda-Ausdruck ersetzt die ganze Klasse Paket aus dem Comparable-Level.",
    },
    {
        "title": "Streams: Die Pipeline",
        "task": "Liefere die 3 Kisten mit den kleinsten Nummern, aufsteigend. Die Fässer bleiben stehen. Er trägt nur 1. Löse alles in einer Stream-Pipeline, ganz ohne for und while.",
        "lesson": "Ein <b>Stream</b> schickt die Elemente einer Sammlung durch eine Pipeline: <b>Quelle</b>, beliebig viele <b>Zwischenschritte</b> (filter, map, sorted, limit) und genau ein <b>Abschluss</b> (forEach, collect, count, sum). Erst der Abschluss startet die Arbeit."
                  "<pre>List&lt;Integer&gt; zahlen = List.of(5, 12, 8, 3, 20);\nzahlen.stream()\n      .filter(z -&gt; z &gt; 4)                   // 5, 12, 8, 20\n      .sorted(Comparator.reverseOrder())    // 20, 12, 8, 5\n      .limit(2)                             // 20, 12\n      .map(z -&gt; z * 10)                     // 200, 120\n      .forEach(z -&gt; System.out.println(z));</pre>"
                  "<code>Comparator.comparingInt(f -&gt; f.nummer)</code> baut einen Comparator, der nach einer Zahl sortiert. Die Quelle bleibt unverändert.",
        "tip": "findeAlles().stream().filter(f -> f.art.equals(\"kiste\")).sorted(Comparator.comparingInt(f -> f.nummer)).limit(3).forEach(f -> { geheZu(f); nimm(); zurRampe(); abliefern(); });",
        "grid": karte(K=[(2, 0), (6, 1), (4, 2), (8, 4), (3, 5)], F=[(8, 0), (6, 5)]),
        "nummern": [45, 3, 12, 30, 7, 28, 1],
        "tragkraft": 1, "exakt": True, "ziel": {"folge": [7, 12, 28], "fass": 0}, "belohnung": {"taler": 12},
        "needs": [STREAM, FILTER, SORTED], "verboten": [OHNE_SCHLEIFE],
        "varianten": [{"text": "andere Nummern", "nummern": [9, 50, 8, 60, 7, 6, 70], "ziel": {"folge": [6, 7, 8], "fass": 0}},
                      {"text": "andere Verteilung von Kisten und Fässern", "grid": karte(K=[(5, 0), (2, 2), (7, 3), (4, 6)], F=[(3, 1), (8, 5)]),
                       "nummern": [22, 4, 33, 11, 2, 44], "ziel": {"folge": [11, 22, 33], "fass": 0}}],
        "braucht": ["hubwagen"],
        "next": "Welt 1 ist geschafft! In Welt 2 geht es um Algorithmen und Datenstrukturen. Kauf zuerst das Regal-Terminal im Shop.",
        "start": java("""
            import java.util.*;

            public class Main {
                public static void main(String[] args) {
                    findeAlles().stream()
                        .filter(f -> f.nummer > 10)
                        .forEach(f -> System.out.println(f));
                }
            }
        """),
        "solution": java("""
            import java.util.*;

            public class Main {
                public static void main(String[] args) {
                    findeAlles().stream()
                        .filter(f -> f.art.equals("kiste"))
                        .sorted(Comparator.comparingInt(f -> f.nummer))
                        .limit(3)
                        .forEach(f -> {
                            geheZu(f);
                            nimm();
                            zurRampe();
                            abliefern();
                        });
                }
            }
        """),
        "warum": "Die Pipeline beschreibt, was passieren soll, nicht wie. filter vor sorted hält die Sortierung klein, und limit(3) sorgt dafür, dass er nur drei Runden läuft.",
    },
]

# ---------- Welt 2: Algorithmen und Datenstrukturen ----------
MAZE = [
    ["..#.......",
     ".##.####.#",
     "....#.....",
     "L.#.#.##.#",
     "###...#K..",
     "....#.####",
     ".##......."],
    ["...#...#..",
     ".#.#.#.#.#",
     ".#...#...K",
     "L#####.###",
     ".#.....#..",
     ".#.###.#.#",
     "...#......"],
    ["#.....#...",
     "#.###.#.#.",
     "..#K#...#.",
     "L.#.#####.",
     ".##.......",
     ".#..#.###.",
     "...##....."],
]

WELT2 = [
    {
        "title": "Lineare Suche",
        "task": "Im Regal stehen 8 Kisten durcheinander. Finde das Fach, in dem die Kiste mit der Nummer auftrag() steht, und melde seine Nummer mit melde(...).",
        "lesson": "Willkommen im Regallager! Die Fächer sind von 0 an nummeriert wie ein <b>Array</b>. <code>lies(i)</code> läuft zu Fach i und liest die Nummer der Kiste, <code>regalGroesse()</code> ist die Anzahl der Fächer, <code>auftrag()</code> die gesuchte Nummer."
                  "<pre>int[] werte = { 7, 3, 9 };\nfor (int i = 0; i &lt; werte.length; i++) {\n    if (werte[i] == 9) {\n        System.out.println(\"gefunden bei \" + i);\n        break;   // Schleife sofort beenden\n    }\n}</pre>"
                  "Das ist die <b>lineare Suche</b>: Fach für Fach, bis es passt. Im schlechtesten Fall liest du alle n Fächer, die Laufzeit wächst also linear mit n: <b>O(n)</b>. Bei ungeordneten Daten geht es nicht besser.",
        "tip": "for (int i = 0; i < regalGroesse(); i++): if (lies(i) == auftrag()) { melde(i); break; }",
        "grid": regal(8),
        "regal": [42, 17, 8, 63, 25, 91, 30, 56], "auftrag": 91,
        "tragkraft": 1, "ziel": {"meldung": 5}, "belohnung": {"taler": 10}, "needs": [LIES, FOR],
        "varianten": [{"text": "gesucht ist die Kiste im letzten Fach", "auftrag": 56, "ziel": {"meldung": 7}},
                      {"text": "andere Kisten im Regal", "regal": [5, 99, 14, 3, 77, 21, 60, 48], "auftrag": 14, "ziel": {"meldung": 2}}],
        "braucht": ["terminal"],
        "start": main("""
            System.out.println("Gesucht: " + auftrag());
            System.out.println("Im ersten Fach steht " + lies(0));
        """),
        "solution": main("""
            for (int i = 0; i < regalGroesse(); i++) {
                if (lies(i) == auftrag()) {
                    melde(i);
                    break;
                }
            }
        """),
        "warum": "Mit break hört er auf, sobald er die Kiste hat. Im schlechtesten Fall bleibt es trotzdem bei n Lesevorgängen: O(n). Schneller geht es nur, wenn das Regal sortiert ist.",
    },
    {
        "title": "Binäre Suche",
        "task": "Diesmal ist das Regal aufsteigend sortiert. Finde das Fach mit der Nummer auftrag() und melde es. Du darfst aber höchstens 4-mal lies() benutzen.",
        "lesson": "In sortierten Daten musst du nicht alles ansehen. Die <b>binäre Suche</b> liest das mittlere Fach: Ist die Nummer dort zu klein, liegt das Ziel rechts davon, sonst links. Jeder Schritt halbiert den Bereich."
                  "<pre>int von = 0;\nint bis = 7;\nint mitte = (von + bis) / 2;   // 3, int-Division rundet ab\n// zu klein? dann: von = mitte + 1;\n// zu groß?  dann: bis = mitte - 1;</pre>"
                  "Aus 8 Fächern werden 4, 2, 1. Die Zahl der Schritte ist der Logarithmus: <b>O(log n)</b>. Bei einer Million Fächern sind das nur etwa 20 statt einer Million Lesevorgänge. Solche Unterschiede beschreibt die <b>Komplexität</b>.",
        "tip": "von = 0, bis = regalGroesse() - 1. Solange von <= bis: mitte berechnen, wert = lies(mitte). Gleich dem Auftrag: melde(mitte) und break. Kleiner: von = mitte + 1, sonst bis = mitte - 1.",
        "grid": regal(8),
        "regal": [4, 9, 15, 22, 31, 47, 58, 70], "auftrag": 58,
        "tragkraft": 1, "ziel": {"meldung": 6, "max_lies": 4}, "belohnung": {"taler": 10}, "needs": [WHILE],
        "varianten": [{"text": "gesucht ist die Kiste im ersten Fach", "auftrag": 4, "ziel": {"meldung": 0, "max_lies": 4}},
                      {"text": "andere Kisten im Regal", "regal": [2, 3, 5, 8, 13, 21, 34, 55], "auftrag": 55, "ziel": {"meldung": 7, "max_lies": 4}},
                      {"text": "gesucht ist die Nummer 13", "regal": [2, 3, 5, 8, 13, 21, 34, 55], "auftrag": 13, "ziel": {"meldung": 4, "max_lies": 4}}],
        "braucht": ["terminal"],
        "start": main("""
            int von = 0;
            int bis = regalGroesse() - 1;
            int mitte = (von + bis) / 2;
            System.out.println("In der Mitte (Fach " + mitte + ") steht " + lies(mitte));
        """),
        "solution": main("""
            int von = 0;
            int bis = regalGroesse() - 1;
            while (von <= bis) {
                int mitte = (von + bis) / 2;
                int wert = lies(mitte);
                if (wert == auftrag()) {
                    melde(mitte);
                    break;
                }
                if (wert < auftrag()) {
                    von = mitte + 1;
                } else {
                    bis = mitte - 1;
                }
            }
        """),
        "warum": "Jeder Lesevorgang halbiert den Suchbereich. Für 8 Fächer reichen höchstens 4, für 16 Fächer 5: O(log n). Voraussetzung ist, dass das Regal sortiert ist.",
    },
    {
        "title": "Rekursion: Die Summe",
        "task": "Berechne die Summe aller Nummern im Regal und melde sie. Schleifen sind verboten: Schreibe eine Methode, die sich selbst aufruft.",
        "lesson": "Eine Methode ist <b>rekursiv</b>, wenn sie sich selbst aufruft. Sie braucht immer zwei Teile: einen <b>Basisfall</b>, der ohne weiteren Aufruf antwortet, und einen <b>Rekursionsschritt</b>, der das Problem verkleinert."
                  "<pre>static int fakultaet(int n) {\n    if (n == 0) {\n        return 1;                    // Basisfall\n    }\n    return n * fakultaet(n - 1);     // kleineres Problem\n}</pre>"
                  "<code>fakultaet(3)</code> wartet auf <code>fakultaet(2)</code>, das auf <code>fakultaet(1)</code> wartet, und so weiter. Erst beim Basisfall wird zurückgerechnet. Fehlt er, endet das mit einem <code>StackOverflowError</code>.",
        "tip": "static int summe(int fach): Ist fach == regalGroesse(), dann return 0. Sonst return lies(fach) + summe(fach + 1). In main: melde(summe(0));",
        "grid": regal(6),
        "regal": [12, 5, 30, 8, 21, 4],
        "tragkraft": 1, "ziel": {"meldung": 80}, "belohnung": {"taler": 10}, "needs": [RETURN], "verboten": [OHNE_SCHLEIFE],
        "varianten": [{"text": "andere Kisten im Regal", "regal": [1, 2, 3, 4, 5, 6], "ziel": {"meldung": 21}},
                      {"text": "ein Regal mit 8 Fächern", "grid": regal(8), "regal": [10, 20, 30, 40, 50, 60, 70, 80], "ziel": {"meldung": 360}}],
        "braucht": ["terminal"],
        "next": "Für das Labyrinth im nächsten Level brauchst du den Kompass aus dem Shop.",
        "start": main("melde(summe(0));", vor="""
            static int summe(int fach) {
                return lies(fach);
            }
        """),
        "solution": main("melde(summe(0));", vor="""
            static int summe(int fach) {
                if (fach == regalGroesse()) {
                    return 0;
                }
                return lies(fach) + summe(fach + 1);
            }
        """),
        "warum": "Jeder Aufruf erledigt ein Fach und gibt den Rest weiter: n Aufrufe, also O(n), genau wie eine Schleife. Rekursion ist hier nicht schneller, aber sie ist das Werkzeug für Bäume, Backtracking und Quicksort.",
    },
    {
        "title": "Labyrinth: Backtracking",
        "task": "Irgendwo zwischen den Wänden steht eine Kiste. Finde sie, nimm sie und bring sie zurück zur Rampe. Die Wände stehen bei jedem Auftrag anders.",
        "lesson": "<b>Backtracking</b> probiert systematisch alle Möglichkeiten durch: einen Schritt gehen, von dort rekursiv weitersuchen, und wenn es nicht klappt, den Schritt <b>zurücknehmen</b> und die nächste Richtung probieren. Damit er nicht im Kreis läuft, merkt sich ein Array, wo er schon war."
                  "<pre>boolean[][] besucht = new boolean[7][10];   // [y][x], am Anfang alles false\nbesucht[3][0] = true;\n\nString[] hin     = { \"rechts\", \"runter\", \"links\", \"hoch\" };\nString[] zurueck = { \"links\", \"hoch\", \"rechts\", \"runter\" };</pre>"
                  "Vom Kompass: <code>istFrei(richtung)</code> prüft, ob in dieser Richtung keine Wand ist, <code>gehe(richtung)</code> läuft ein Feld. <code>posX()</code> und <code>posY()</code> sagen, wo er steht.",
        "tip": "In suche(): Feld als besucht markieren. Steht hier die Kiste: nimm() und return true. Sonst für jede der 4 Richtungen: wenn frei, gehe(hin[i]); wenn das Feld neu ist, rekursiv suchen; danach gehe(zurueck[i]); bei Erfolg return true. Am Ende return false.",
        "grid": MAZE[0],
        "tragkraft": 1, "ziel": {"kiste": 1}, "belohnung": {"taler": 14}, "needs": [RETURN],
        "varianten": [{"text": "ein anderes Labyrinth", "grid": MAZE[1]}, {"text": "noch ein Labyrinth", "grid": MAZE[2]}],
        "braucht": ["kompass", "scanner"],
        "start": java("""
            public class Main {
                static boolean[][] besucht = new boolean[7][10];
                static String[] hin = { "rechts", "runter", "links", "hoch" };
                static String[] zurueck = { "links", "hoch", "rechts", "runter" };

                static boolean suche() {
                    besucht[posY()][posX()] = true;
                    if (wasIstHier().equals("kiste")) {
                        nimm();
                        return true;
                    }
                    for (int i = 0; i < 4; i++) {
                        System.out.println(hin[i] + " frei: " + istFrei(hin[i]));
                    }
                    return false;
                }

                public static void main(String[] args) {
                    suche();
                    abliefern();
                }
            }
        """),
        "solution": java("""
            public class Main {
                static boolean[][] besucht = new boolean[7][10];
                static String[] hin = { "rechts", "runter", "links", "hoch" };
                static String[] zurueck = { "links", "hoch", "rechts", "runter" };

                static boolean suche() {
                    besucht[posY()][posX()] = true;
                    if (wasIstHier().equals("kiste")) {
                        nimm();
                        return true;
                    }
                    for (int i = 0; i < 4; i++) {
                        if (istFrei(hin[i])) {
                            gehe(hin[i]);
                            boolean gefunden = !besucht[posY()][posX()] && suche();
                            gehe(zurueck[i]);
                            if (gefunden) {
                                return true;
                            }
                        }
                    }
                    return false;
                }

                public static void main(String[] args) {
                    suche();
                    abliefern();
                }
            }
        """),
        "warum": "Die Suche besucht jedes Feld höchstens einmal, weil sie sich besuchte Felder merkt. Ohne das Array würde sie endlos im Kreis laufen. Der Rückweg ergibt sich von selbst: Jeder Aufruf nimmt beim Zurückkehren seinen Schritt zurück.",
    },
    {
        "title": "Verkettete Liste",
        "task": "Liefere die Kisten nach Nummer aufsteigend. Fertige Sammlungen und sort sind verboten: Baue deine eigene verkettete Liste und füge jede Kiste gleich an der richtigen Stelle ein.",
        "lesson": "Eine <b>verkettete Liste</b> besteht aus <b>Knoten</b>. Jeder Knoten hält einen Wert und eine Referenz <code>next</code> auf den nächsten. Der letzte zeigt auf <code>null</code>. Die Liste selbst merkt sich nur den ersten Knoten, den <b>Kopf</b>."
                  "<pre>class Knoten {\n    int wert;\n    Knoten next;\n    Knoten(int wert) { this.wert = wert; }\n}\n\nKnoten kopf = new Knoten(5);\nkopf.next = new Knoten(9);\nfor (Knoten k = kopf; k != null; k = k.next) {\n    System.out.println(k.wert);\n}</pre>"
                  "Einfügen heißt nur zwei Referenzen umhängen: <code>neu.next = k.next; k.next = neu;</code>. Anders als beim Array muss nichts verschoben werden. Dafür gibt es keinen direkten Zugriff auf das i-te Element.",
        "tip": "Sortiert einfügen: Ist die Liste leer oder die neue Nummer kleiner als die im Kopf, wird der neue Knoten der Kopf. Sonst mit k vom Kopf aus weiterlaufen, solange k.next != null && k.next.feld.nummer < feld.nummer, und dahinter einhängen.",
        "grid": karte(K=[(6, 0), (2, 1), (8, 2), (4, 4), (7, 5), (2, 6)]),
        "nummern": [33, 8, 51, 19, 4, 27],
        "tragkraft": 1, "ziel": {"folge": [4, 8, 19, 27, 33, 51]}, "belohnung": {"taler": 14}, "needs": [KNOTEN, NEXT], "verboten": [OHNE_SAMMLUNG],
        "varianten": [{"text": "andere Nummern auf den Kisten", "nummern": [1, 2, 3, 6, 5, 4], "ziel": {"folge": [1, 2, 3, 4, 5, 6]}},
                      {"text": "die kleinste Nummer kommt zuletzt", "nummern": [60, 50, 40, 30, 20, 10], "ziel": {"folge": [10, 20, 30, 40, 50, 60]}}],
        "braucht": ["hubwagen"],
        "start": java("""
            class Knoten {
                Feld feld;
                Knoten next;

                Knoten(Feld feld) {
                    this.feld = feld;
                }
            }

            class Liste {
                Knoten kopf;

                void fuegeSortiertEin(Feld feld) {
                    Knoten neu = new Knoten(feld);
                    neu.next = kopf;
                    kopf = neu;
                }
            }

            public class Main {
                public static void main(String[] args) {
                    Liste liste = new Liste();
                    for (Feld f : finde("kiste")) {
                        liste.fuegeSortiertEin(f);
                    }
                    for (Knoten k = liste.kopf; k != null; k = k.next) {
                        System.out.println(k.feld);
                    }
                }
            }
        """),
        "solution": java("""
            class Knoten {
                Feld feld;
                Knoten next;

                Knoten(Feld feld) {
                    this.feld = feld;
                }
            }

            class Liste {
                Knoten kopf;

                void fuegeSortiertEin(Feld feld) {
                    Knoten neu = new Knoten(feld);
                    if (kopf == null || feld.nummer < kopf.feld.nummer) {
                        neu.next = kopf;
                        kopf = neu;
                        return;
                    }
                    Knoten k = kopf;
                    while (k.next != null && k.next.feld.nummer < feld.nummer) {
                        k = k.next;
                    }
                    neu.next = k.next;
                    k.next = neu;
                }
            }

            public class Main {
                public static void main(String[] args) {
                    Liste liste = new Liste();
                    for (Feld f : finde("kiste")) {
                        liste.fuegeSortiertEin(f);
                    }
                    for (Knoten k = liste.kopf; k != null; k = k.next) {
                        geheZu(k.feld);
                        nimm();
                        zurRampe();
                        abliefern();
                    }
                }
            }
        """),
        "warum": "Das Einhängen selbst kostet O(1), aber die richtige Stelle zu finden kostet O(n), weil man vom Kopf aus durchlaufen muss. Für n Kisten sind das zusammen O(n²). Ein Suchbaum findet die Stelle schneller.",
    },
    {
        "title": "Binärer Suchbaum",
        "task": "Wieder nach Nummer aufsteigend liefern, wieder ohne fertige Sammlungen. Diesmal baust du einen binären Suchbaum und läufst ihn inorder ab.",
        "lesson": "Im <b>binären Suchbaum</b> hat jeder Knoten bis zu zwei Kinder: Links hängt alles Kleinere, rechts alles Größere. Beim Einfügen und Suchen entscheidest du an jedem Knoten nur „kleiner oder größer?“ und sparst dir so die Hälfte des Baums."
                  "<pre>class Knoten {\n    int wert;\n    Knoten kleiner, groesser;\n    Knoten(int wert) { this.wert = wert; }\n}\n\nstatic Knoten einfuegen(Knoten k, int wert) {\n    if (k == null) return new Knoten(wert);      // freie Stelle gefunden\n    if (wert &lt; k.wert) k.kleiner = einfuegen(k.kleiner, wert);\n    else k.groesser = einfuegen(k.groesser, wert);\n    return k;\n}</pre>"
                  "Die <b>Inorder-Traversierung</b> besucht erst den linken Teilbaum, dann den Knoten selbst, dann den rechten Teilbaum. Beim Suchbaum kommen die Werte so automatisch sortiert heraus.",
        "tip": "inorder(Knoten k): Ist k == null, dann return. Sonst inorder(k.kleiner); die Kiste von k holen und abliefern; inorder(k.groesser);. In main: wurzel = einfuegen(wurzel, f) für jedes Feld, dann inorder(wurzel).",
        "grid": karte(K=[(5, 0), (8, 1), (2, 2), (6, 4), (3, 5), (8, 6)]),
        "nummern": [25, 60, 11, 42, 7, 18],
        "tragkraft": 1, "ziel": {"folge": [7, 11, 18, 25, 42, 60]}, "belohnung": {"taler": 14}, "needs": [KNOTEN, ZWEI_KINDER, INORDER], "verboten": [OHNE_SAMMLUNG],
        "varianten": [{"text": "andere Nummern auf den Kisten", "nummern": [50, 20, 70, 10, 30, 60], "ziel": {"folge": [10, 20, 30, 50, 60, 70]}},
                      {"text": "die Kisten kommen schon sortiert", "nummern": [1, 2, 3, 4, 5, 6], "ziel": {"folge": [1, 2, 3, 4, 5, 6]}}],
        "braucht": ["hubwagen"],
        "next": "Im nächsten Level räumst du das Regal mit einer Hashfunktion ein.",
        "start": java("""
            class Knoten {
                Feld feld;
                Knoten kleiner, groesser;

                Knoten(Feld feld) {
                    this.feld = feld;
                }
            }

            public class Main {
                static Knoten einfuegen(Knoten k, Feld feld) {
                    if (k == null) {
                        return new Knoten(feld);
                    }
                    return k;
                }

                static void inorder(Knoten k) {
                    if (k == null) {
                        return;
                    }
                    System.out.println(k.feld);
                }

                public static void main(String[] args) {
                    Knoten wurzel = null;
                    for (Feld f : finde("kiste")) {
                        wurzel = einfuegen(wurzel, f);
                    }
                    inorder(wurzel);
                }
            }
        """),
        "solution": java("""
            class Knoten {
                Feld feld;
                Knoten kleiner, groesser;

                Knoten(Feld feld) {
                    this.feld = feld;
                }
            }

            public class Main {
                static Knoten einfuegen(Knoten k, Feld feld) {
                    if (k == null) {
                        return new Knoten(feld);
                    }
                    if (feld.nummer < k.feld.nummer) {
                        k.kleiner = einfuegen(k.kleiner, feld);
                    } else {
                        k.groesser = einfuegen(k.groesser, feld);
                    }
                    return k;
                }

                static void inorder(Knoten k) {
                    if (k == null) {
                        return;
                    }
                    inorder(k.kleiner);
                    geheZu(k.feld);
                    nimm();
                    zurRampe();
                    abliefern();
                    inorder(k.groesser);
                }

                public static void main(String[] args) {
                    Knoten wurzel = null;
                    for (Feld f : finde("kiste")) {
                        wurzel = einfuegen(wurzel, f);
                    }
                    inorder(wurzel);
                }
            }
        """),
        "warum": "In einem ausgeglichenen Baum kostet Einfügen nur O(log n), weil jeder Vergleich die Hälfte ausschließt. Kommen die Werte aber schon sortiert, entartet der Baum zu einer Liste, und es sind wieder O(n) pro Einfügen.",
    },
    {
        "title": "Hashing: Jedes Ding an seinen Platz",
        "task": "Die Lieferung aus lieferung() soll ins leere Regal. Das Fach berechnet sich aus der Nummer: nummer % regalGroesse(). Ist das Fach belegt, nimm das nächste freie (hinter dem letzten Fach geht es bei 0 weiter).",
        "lesson": "Eine <b>Hashtabelle</b> berechnet aus dem Schlüssel direkt den Platz, statt zu suchen. Die <b>Hashfunktion</b> ist hier der Rest beim Teilen durch die Tabellengröße: <code>15 % 7</code> ist 1, also Fach 1. Suchen und Einfügen kosten so im Schnitt nur <b>O(1)</b>."
                  "<pre>int n = 7;\nSystem.out.println(15 % n);        // 1\nSystem.out.println(8 % n);         // auch 1: eine Kollision!\nSystem.out.println((6 + 1) % n);   // 0: nach dem letzten Fach wieder vorne</pre>"
                  "Landen zwei Schlüssel im selben Fach, ist das eine <b>Kollision</b>. Beim <b>linearen Sondieren</b> probierst du einfach das nächste Fach, bis eines frei ist. <code>istFachFrei(i)</code> prüft ein Fach, <code>stelle(i, nummer)</code> stellt die Kiste hinein, <code>lieferung()</code> ist ein <code>int[]</code>.",
        "tip": "Für jede nummer aus lieferung(): fach = nummer % n. Solange !istFachFrei(fach): fach = (fach + 1) % n. Dann stelle(fach, nummer).",
        "grid": regal(7),
        "regal": [0, 0, 0, 0, 0, 0, 0], "lieferung": [15, 8, 22, 3, 10],
        "tragkraft": 1, "ziel": {"regal": [0, 15, 8, 22, 3, 10, 0]}, "belohnung": {"taler": 14}, "needs": [MODULO, WHILE],
        "varianten": [{"text": "alle Kisten wollen ins letzte Fach", "lieferung": [13, 6, 20, 27], "ziel": {"regal": [6, 20, 27, 0, 0, 0, 13]}},
                      {"text": "eine Lieferung ohne Kollision", "lieferung": [7, 22, 16, 11], "ziel": {"regal": [7, 22, 16, 0, 11, 0, 0]}}],
        "braucht": ["terminal"],
        "start": main("""
            int n = regalGroesse();
            for (int nummer : lieferung()) {
                System.out.println(nummer + " gehört in Fach " + (nummer % n));
            }
        """),
        "solution": main("""
            int n = regalGroesse();
            for (int nummer : lieferung()) {
                int fach = nummer % n;
                while (!istFachFrei(fach)) {
                    fach = (fach + 1) % n;
                }
                stelle(fach, nummer);
            }
        """),
        "warum": "Ohne Kollision braucht jede Kiste genau einen Versuch: O(1). Je voller die Tabelle wird, desto länger werden die Ketten beim Sondieren. Deshalb hält man Hashtabellen nur zu einem Teil gefüllt.",
    },
    {
        "title": "Sortieren: Bubblesort",
        "task": "Sortiere das Regal aufsteigend. Du kannst nur Fächer lesen und zwei Fächer tauschen.",
        "lesson": "<b>Bubblesort</b> vergleicht immer zwei Nachbarn und tauscht sie, wenn sie falsch herum stehen. Nach einem Durchgang ist die größte Nummer ganz rechts angekommen, wie eine Luftblase, die aufsteigt. Der nächste Durchgang kann deshalb ein Fach früher aufhören."
                  "<pre>int[] a = { 5, 2, 9, 1 };\nfor (int i = 0; i &lt; a.length - 1; i++) {\n    for (int j = 0; j &lt; a.length - 1 - i; j++) {\n        if (a[j] &gt; a[j + 1]) {\n            int merke = a[j];\n            a[j] = a[j + 1];\n            a[j + 1] = merke;\n        }\n    }\n}</pre>"
                  "Zwei Schleifen ineinander bedeuten rund n · n Vergleiche: <b>O(n²)</b>. Im Regal liest du mit <code>lies(j)</code> und tauschst mit <code>tausche(j, j + 1)</code>.",
        "tip": "Genau wie im Beispiel, nur mit lies und tausche: if (lies(j) > lies(j + 1)) { tausche(j, j + 1); }",
        "grid": regal(6),
        "regal": [34, 12, 51, 7, 28, 19],
        "tragkraft": 1, "ziel": {"regal": [7, 12, 19, 28, 34, 51]}, "belohnung": {"taler": 14}, "needs": [TAUSCHE, FOR],
        "varianten": [{"text": "das Regal steht genau falsch herum", "regal": [60, 50, 40, 30, 20, 10], "ziel": {"regal": [10, 20, 30, 40, 50, 60]}},
                      {"text": "nur zwei Kisten stehen falsch", "regal": [1, 2, 4, 3, 5, 6], "ziel": {"regal": [1, 2, 3, 4, 5, 6]}}],
        "braucht": ["terminal"],
        "next": "Letzter Auftrag: Quicksort, das schnelle Sortierverfahren mit Rekursion.",
        "start": main("""
            int n = regalGroesse();
            if (lies(0) > lies(1)) {
                tausche(0, 1);
            }
        """),
        "solution": main("""
            int n = regalGroesse();
            for (int i = 0; i < n - 1; i++) {
                for (int j = 0; j < n - 1 - i; j++) {
                    if (lies(j) > lies(j + 1)) {
                        tausche(j, j + 1);
                    }
                }
            }
        """),
        "warum": "Bubblesort braucht immer etwa n²/2 Vergleiche, auch wenn das Regal schon fast sortiert ist. Für 6 Kisten ist das egal, für 6000 nicht mehr. Quicksort im nächsten Level kommt mit O(n log n) aus.",
    },
    {
        "title": "Sortieren: Quicksort",
        "task": "Sortiere das Regal mit 8 Kisten aufsteigend, diesmal mit Quicksort: Teile das Regal um ein Pivot-Element und sortiere beide Hälften rekursiv.",
        "lesson": "<b>Quicksort</b> arbeitet nach dem Prinzip <b>Teile und herrsche</b>: Wähle ein <b>Pivot</b> (hier die letzte Kiste des Bereichs). Bringe alle kleineren Kisten nach links, dann das Pivot an die Grenze. Jetzt steht das Pivot endgültig richtig, und links und rechts davon sortierst du rekursiv weiter."
                  "<pre>// Bereich von..bis aufteilen, Pivot ist a[bis]\nint grenze = von;                 // links davon: alles Kleinere\nfor (int j = von; j &lt; bis; j++) {\n    if (a[j] &lt; pivot) {\n        // a[grenze] und a[j] tauschen\n        grenze++;\n    }\n}\n// zum Schluss a[grenze] und a[bis] tauschen</pre>"
                  "Im Schnitt halbiert jeder Schritt das Problem: <b>O(n log n)</b>. Nur wenn das Pivot immer das größte oder kleinste Element ist, wird es O(n²). Basisfall: Ein Bereich mit höchstens einer Kiste ist schon sortiert.",
        "tip": "quicksort(von, bis): if (von >= bis) return;. pivot = lies(bis), grenze = von. Für j von von bis bis - 1: if (lies(j) < pivot) { tausche(grenze, j); grenze++; }. Dann tausche(grenze, bis); quicksort(von, grenze - 1); quicksort(grenze + 1, bis);",
        "grid": regal(8),
        "regal": [45, 12, 78, 33, 9, 60, 21, 38],
        "tragkraft": 1, "ziel": {"regal": [9, 12, 21, 33, 38, 45, 60, 78]}, "belohnung": {"taler": 20}, "needs": [TAUSCHE, REKURSIV2],
        "varianten": [{"text": "andere Kisten im Regal", "regal": [8, 3, 5, 1, 9, 2, 7, 4], "ziel": {"regal": [1, 2, 3, 4, 5, 7, 8, 9]}},
                      {"text": "das Regal ist schon sortiert", "regal": [10, 20, 30, 40, 50, 60, 70, 80], "ziel": {"regal": [10, 20, 30, 40, 50, 60, 70, 80]}}],
        "braucht": ["terminal"],
        "start": main("quicksort(0, regalGroesse() - 1);", vor="""
            static void quicksort(int von, int bis) {
                if (von >= bis) {
                    return;
                }
                int pivot = lies(bis);
                System.out.println("Pivot für " + von + ".." + bis + " ist " + pivot);
            }
        """),
        "solution": main("quicksort(0, regalGroesse() - 1);", vor="""
            static void quicksort(int von, int bis) {
                if (von >= bis) {
                    return;
                }
                int pivot = lies(bis);
                int grenze = von;
                for (int j = von; j < bis; j++) {
                    if (lies(j) < pivot) {
                        tausche(grenze, j);
                        grenze++;
                    }
                }
                tausche(grenze, bis);
                quicksort(von, grenze - 1);
                quicksort(grenze + 1, bis);
            }
        """),
        "warum": "Jede Aufteilung liest den Bereich einmal durch, und im Schnitt gibt es log n Ebenen: O(n log n). Beim schon sortierten Regal ist das letzte Element immer das größte, dann entartet Quicksort zu O(n²). Ein zufälliges Pivot verhindert das.",
    },
]
for lv in WELT2:
    lv["welt"] = 2
LEVELS += WELT2
for lv in LEVELS:
    lv["beste"] = lv["solution"]
    lv.setdefault("verboten", [])
