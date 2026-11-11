import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from javarun import baue_jar, run_many
from levels import LEVELS, SHOP

baue_jar()
ALLE = [s["id"] for s in SHOP]
bad = 0

print("--- Lösungen, nur mit den für das Level nötigen Käufen; der Startcode darf nicht gewinnen und muss übersetzbar sein")
noetig = [[s["id"] for s in SHOP if s["level"] is not None and s["level"] <= i] for i in range(len(LEVELS))]
loes = run_many([(lv["solution"], dict(lv, owned=noetig[i])) for i, lv in enumerate(LEVELS)])
start = run_many([(lv["start"], dict(lv, owned=noetig[i])) for i, lv in enumerate(LEVELS)])
for i, (lv, r, s) in enumerate(zip(LEVELS, loes, start)):
    syntax = bool(s["error"]) and s["error"]["kind"] == "syntax"
    ok = r["won"] and not s["won"] and not syntax
    print(i + 1, lv["title"], "OK" if ok else "FEHLER", "| aktionen=", len(r.get("events", [])), "err=", r["error"], r.get("hinweis"),
          [c for c in r.get("checks", []) if not c["ok"]], "| start:", s["won"], s["error"])
    bad += not ok

print("--- Gesperrt ohne Kauf: jedes Level mit braucht muss ohne den Kauf scheitern")
jobs = [(i, f) for i, lv in enumerate(LEVELS) for f in lv.get("braucht", [])]
res = run_many([(LEVELS[i]["solution"], dict(LEVELS[i], owned=[x for x in ALLE if x != f])) for i, f in jobs])
for (i, f), r in zip(jobs, res):
    ok = not r["won"]
    print(i + 1, "ohne", f, "->", "gesperrt" if ok else "GEWINNT TROTZDEM", "|", (r["error"] or {}).get("msg"))
    bad += not ok

print("--- Wirtschaft: Pflichtkäufe müssen vor ihrem Level bezahlbar sein")
taler = 0
kaeufe = {s["level"]: s for s in SHOP if s["level"] is not None}
for i, lv in enumerate(LEVELS):
    if i in kaeufe:
        taler -= kaeufe[i]["preis"]["taler"]
        print("vor Level", i + 1, "Kauf", kaeufe[i]["name"], "-> Rest", taler)
        bad += taler < 0
    taler += lv["belohnung"]["taler"]
print("am Ende übrig:", taler, "| optionale Käufe kosten", sum(s["preis"]["taler"] for s in SHOP if s["level"] is None))

print("--- Falsche Lösungen müssen scheitern")
falsch = [
    (3, LEVELS[3]["solution"].replace('if (wasIstHier().equals("kiste")) {', 'if (!wasIstHier().equals("leer")) {'), "nimmt auch Fässer"),
    (12, LEVELS[11]["solution"], "lineare Suche statt binärer"),
    (13, LEVELS[13]["solution"].replace("return 0;", "return 1;"), "falsche Summe"),
    (17, LEVELS[17]["solution"].replace("fach = (fach + 1) % n;", "fach = fach + 1;"), "Sondieren ohne Umlauf"),
    (18, LEVELS[18]["solution"].replace("lies(j) > lies(j + 1)", "lies(j) < lies(j + 1)"), "absteigend sortiert"),
    (6, LEVELS[9]["solution"], "Lambda im Comparable-Level"),
]
for (i, code, was), r in zip(falsch, run_many([(c, dict(LEVELS[i], owned=ALLE)) for i, c, _ in falsch])):
    print(i + 1, was, "->", "scheitert" if not r["won"] else "GEWINNT", "|", (r["error"] or {}).get("msg"), r.get("hinweis"), [c["label"] for c in r.get("checks", []) if not c["ok"]])
    bad += r["won"]

print("FEHLER:", bad)
sys.exit(1 if bad else 0)
