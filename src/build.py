import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from javarun import ROOT, baue_jar, run_many, zeilen
from levels import LEVELS, SHOP
from book import BOOK

baue_jar()
src = os.path.join(ROOT, "src")
t = open(os.path.join(src, "template.html"), encoding="utf-8").read()

# Referenzwerte für die Bonus-Sterne kommen aus der Musterlösung
alle = [s["id"] for s in SHOP]
for lv, r in zip(LEVELS, run_many([(lv["solution"], dict(lv, owned=alle)) for lv in LEVELS])):
    assert r["won"], (lv["title"], r.get("error"), r.get("hinweis"), r.get("checks"))
    lv["par_steps"] = len(r["events"])
    lv["par_lines"] = zeilen(lv["solution"])


def js(x):
    return json.dumps(x, ensure_ascii=False).replace("</", "<\\/")


for k, v in (("/*LEVELS*/", js(LEVELS)), ("/*SHOP*/", js(SHOP)), ("/*BOOK*/", js(BOOK))):
    assert k in t, k
    t = t.replace(k, v)
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("ok", len(t))
