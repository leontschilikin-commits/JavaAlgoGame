# Lager-Quest

Lernspiel für Java sowie Algorithmen und Datenstrukturen, nach dem Vorbild von Rohstoff-Quest (Python).
Dein Code steuert einen Lageristen. Er wird im Browser mit einem echten Java-17-Compiler übersetzt.

- Welt 1 (Vertiefung Softwareentwicklung): Methoden, Klassen, Vererbung, Interfaces, Generics, Collections, Lambdas, Streams
- Welt 2 (Algorithmen und Datenstrukturen): lineare und binäre Suche, Rekursion, Backtracking, verkettete Liste, Suchbaum, Hashing, Bubblesort, Quicksort

## Starten

Das Spiel braucht einen Webserver (ein Doppelklick auf `index.html` reicht nicht) und Internet für CheerpJ und CodeMirror.

```bash
python3 src/serve.py 8766 .
```

Dann http://localhost:8766 öffnen. Der erste Start dauert einige Sekunden, bis der Compiler warm ist.
Für GitHub Pages gehören `index.html`, `lager.jar` und `ecj.jar` in denselben Ordner.

## Bauen und testen

Braucht Python 3 und ein JDK ab Version 17.

```bash
python3 src/build.py
```

```bash
python3 src/test.py && python3 src/test_book.py && python3 src/test_sprache.py
```

| Datei | Inhalt |
| --- | --- |
| `src/levels.py` | Level, Shop, Musterlösungen |
| `src/book.py` | Java-Handbuch |
| `src/template.html` | Oberfläche, Grafik, Editor |
| `src/java/lager/` | Simulator: `Welt` (Halle), `Befehle` (Spielbefehle), `Runner` (Compiler und Ausführung) |
| `ecj.jar` | Eclipse-Compiler für Java 3.33 (EPL 2.0), läuft im Browser über CheerpJ |

CheerpJ ist für private und nicht kommerzielle Nutzung kostenlos.
