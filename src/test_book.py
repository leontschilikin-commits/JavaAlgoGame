import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from javarun import baue_jar, run_many
from book import BOOK

IMPORTS = "import java.util.*; import java.util.function.*; import java.util.stream.*;\n"
LEVEL = {"grid": ["L"], "tragkraft": 1, "ziel": {}}


def programm(code):
    """Baut aus einem Handbuch-Beispiel ein ganzes Programm: Klassen nach außen, static-Methoden in Main, der Rest in main."""
    aussen, innen, body, ziel = [], [], [], None
    for z in code.split("\n"):
        if ziel is None:
            if z.startswith(("class ", "interface ", "abstract class ", "enum ")):
                ziel = aussen
            elif z.startswith("static "):
                ziel = innen
            else:
                body.append(z)
                continue
            ziel.append(z)
            if z.rstrip().endswith("}"):
                ziel = None
        else:
            ziel.append(z)
            if z == "}":
                ziel = None
    return IMPORTS + "\n".join(aussen) + "\npublic class Main {\n" + "\n".join(innen) + "\npublic static void main(String[] args) {\n" + "\n".join(body) + "\n}\n}\n"


baue_jar()
items = [it for sec in BOOK for it in sec["items"] if "code" in it]
bad = 0
for it, r in zip(items, run_many([(programm(it["code"]), LEVEL) for it in items])):
    if r["error"] or r["output"] != it["out"]:
        bad += 1
        print("FEHLER", it["name"], "|", r["error"], "| bekommen:", repr(r["output"]), "erwartet:", repr(it["out"]))
print(len(items), "Beispiele geprüft, Fehler:", bad)
sys.exit(1 if bad else 0)
