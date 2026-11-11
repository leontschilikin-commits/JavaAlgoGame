"""Baut lager.jar und lässt Java-Code im selben Runner laufen, den auch der Browser benutzt."""
import glob, json, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CP = os.pathsep.join([os.path.join(ROOT, "lager.jar"), os.path.join(ROOT, "ecj.jar")])


def baue_jar():
    out = os.path.join(ROOT, "build", "classes")
    os.makedirs(out, exist_ok=True)
    quellen = sorted(glob.glob(os.path.join(ROOT, "src", "java", "lager", "*.java")))
    subprocess.run(["javac", "--release", "17", "-Xlint:-options", "-nowarn", "-cp", os.path.join(ROOT, "ecj.jar"), "-d", out] + quellen, check=True)
    subprocess.run(["jar", "cf", os.path.join(ROOT, "lager.jar"), "-C", out, "."], check=True)


def run_many(jobs, marken=False):
    """jobs: Liste von (code, level). Liefert die Ergebnisse in derselben Reihenfolge.
    marken=True: Fehlerzeilen wie im Browser nur über die Zeilenmerker bestimmen, nicht über den Stacktrace."""
    p = subprocess.run(["java", "-Xss4m"] + (["-Dlager.marken=1"] if marken else []) + ["-cp", CP, "lager.Runner"], input=json.dumps(jobs).encode(), capture_output=True, check=True)
    return json.loads(p.stdout.decode())


def zeilen(code):
    """Zählt Codezeilen wie das Spiel: ohne Leerzeilen, Kommentare und Zeilen, die nur aus Klammern bestehen."""
    return len([l for l in code.splitlines() if l.strip() and not l.strip().startswith("//") and l.strip() not in ("{", "}")])
