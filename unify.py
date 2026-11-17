#!/usr/bin/env python3
"""unify.py: unifikácia názvov files v aplikácii (Technológie internetu, cv08).

Spúšťa sa v termináli v priečinku repository (tam, kde je priečinok web/):

  python3 unify.py --init    vytvorí unify.txt: zoznam súčasných files a návrh nových názvov
  python3 unify.py           vypíše plán, nič nemení
  python3 unify.py --run     premenuje files, opraví odkazy, doplní chýbajúce files a mapu v README.md

Script mení len názvy files, odkazy na ne a komentár na začiatku file. Ostatný kód nechá tak, ako je.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")
PLAN = os.path.join(ROOT, "unify.txt")
README = os.path.join(ROOT, "README.md")
MAP_START = "<!-- MAPA-START -->"
MAP_END = "<!-- MAPA-END -->"
DELETE = "zmazat"
TOKEN = re.compile(r"(?<![\w/.\-])((?:[\w\-]+/)*[\w\-]+\.php)\b")


# ---------------------------------------------------------------- pomocné funkcie

def say(text=""):
    print(text)


def stop(text):
    print("CHYBA: " + text)
    sys.exit(1)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def php_files():
    """Všetky .php files pod web/, cesty od priečinka web/ (napr. content/routes.php)."""
    found = []
    for folder, _dirs, names in os.walk(WEB):
        for name in names:
            if name.endswith(".php"):
                found.append(os.path.relpath(os.path.join(folder, name), WEB).replace(os.sep, "/"))
    return sorted(found, key=lambda p: (p.count("/"), p))


def without_comments(text):
    """Kód bez komentárov, aby sa názov file v komentári nepočítal ako odkaz."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"(^|[^:'\"])//.*$", r"\1", text, flags=re.M)
    text = re.sub(r"^\s*#.*$", "", text, flags=re.M)
    return text


def is_git():
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=ROOT, check=True,
                       capture_output=True)
        return True
    except Exception:
        return False


def tracked(rel):
    r = subprocess.run(["git", "ls-files", "--error-unmatch", os.path.join("web", rel)], cwd=ROOT,
                       capture_output=True)
    return r.returncode == 0


def move(old, new, git):
    """Premenuje web/old na web/new. V git repository cez git mv, aby zostala história."""
    src, dst = os.path.join(WEB, old), os.path.join(WEB, new)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if git and tracked(old):
        subprocess.run(["git", "mv", os.path.join("web", old), os.path.join("web", new)], cwd=ROOT, check=True)
    else:
        os.rename(src, dst)


def remove(old, git):
    if git and tracked(old):
        subprocess.run(["git", "rm", "-q", "-f", os.path.join("web", old)], cwd=ROOT, check=True)
    else:
        os.remove(os.path.join(WEB, old))
    folder = os.path.dirname(os.path.join(WEB, old))
    while folder != WEB and os.path.isdir(folder) and not os.listdir(folder):   # prázdny priečinok preč
        os.rmdir(folder)
        folder = os.path.dirname(folder)


# ---------------------------------------------------------------- roly a pravidlo názvov

def roles(entity, lookups):
    """Vráti dict: file (cesta od web/) -> (rola, CRUD, odkiaľ sa otvára, úloha).
    entity = (table, slovo), napr. ('routes', 'route'); lookups = zoznam takých dvojíc."""
    table, one = entity
    r = {}

    def page(name, role, crud, opened, task=""):
        r[name] = (role + " (file stránky)", crud, opened, task)
        r["content/" + name] = (role + " (content file)", crud,
                                "vkladá ho template.php, keď sa otvorí " + name, task)

    r["db.php"] = ("pripojenie k databáze, spoločný file", "žiadna",
                   "v prehliadači sa neotvára; file stránky ho pripája cez require", "")
    r["template.php"] = ("template, spoločný file každej stránky", "žiadna",
                         "v prehliadači sa neotvára; file stránky ho pripája cez include", "")
    page("index.php", "úvodná stránka", "žiadna", "z menu")
    page("contact.php", "stránka s kontaktom", "žiadna", "z menu")
    page(f"{table}.php", f"main entity {table}, zoznam", "Read", "z menu", "cv07")
    page("detail.php", f"main entity {table}, detail jedného record", "Read",
         f"z {table}.php, odkaz s id: detail.php?id=...", "cv07")
    page(f"add-{one}.php", f"main entity {table}, formulár na nový record", "Create", "z menu", "cv07")
    page(f"edit-{one}.php", f"main entity {table}, formulár na úpravu jedného record", "Update",
         f"z detail.php, odkaz Upraviť: edit-{one}.php?id=...", "9.9")
    r[f"delete-{one}.php"] = (f"main entity {table}, zmazanie jedného record (file bez stránky)", "Delete",
                              "z detail.php, button Zmazať (formulár POST s hidden input id)", "9.10")
    page("data.php", "lookup tables, formuláre na nový record a výpis tables", "Create, Read", "z menu", "cv07")
    for ltable, lone in lookups:
        page(f"edit-{lone}.php", f"lookup table {ltable}, formulár na úpravu jedného record", "Update",
             f"z data.php, odkaz Upraviť: edit-{lone}.php?id=...", "9.5")
        r[f"delete-{lone}.php"] = (f"lookup table {ltable}, zmazanie jedného record (file bez stránky)", "Delete",
                                   "z data.php, button Zmazať (formulár POST s hidden input id)", "9.6")
    page("stats.php", "prehľad, výpisy s JOIN a GROUP BY", "Read", "z menu", "cv07")
    return r


def header(role, crud, opened):
    return f"// ROLA: {role}\n// CRUD: {crud}\n// OTVÁRA SA: {opened}\n"


def add_header(rel, info):
    """Doplní komentár s rolou na začiatok file, ak tam ešte nie je."""
    path = os.path.join(WEB, rel)
    text = read(path)
    if "// ROLA:" in text:
        return False
    h = header(info[0], info[1], info[2])
    if text.startswith("<?php\n"):
        text = "<?php\n" + h + text[6:]
    elif text.startswith("<?php"):
        text = "<?php\n" + h + text[5:].lstrip(" ")
    else:
        text = "<?php\n" + h + "?>\n" + text
    write(path, text)
    return True


def skeleton(rel, info, entity):
    """Obsah file, ktorý v aplikácii chýba."""
    role, crud, opened, task = info
    h = "<?php\n" + header(role, crud, opened)
    name = os.path.basename(rel)
    todo = f"DOPLŇ v úlohe {task}" if task.startswith("9.") else "DOPLŇ: táto časť je z cvičenia cv07"
    if rel == "content/index.php":
        return h + "?>\n<p>Úvodná stránka aplikácie. Sem patrí krátky text o tom, čo aplikácia eviduje.</p>\n"
    if rel == "content/contact.php":
        return h + "?>\n<p>Kontakt: meno autora aplikácie a študijná skupina.</p>\n"
    if rel.startswith("content/"):
        return h + f"// {todo}\n?>\n<p>{todo}.</p>\n"
    if name.startswith("delete-"):
        back = "data.php" if "lookup table" in role else entity[0] + ".php"
        return (h + f"// {todo}: kontrola, DELETE, redirect so správou\n"
                + f"header('Location: {back}');   // zatiaľ len redirect späť\nexit;\n")
    if name == "index.php":
        title, active, db = "Domov", "index", False
    elif name == "contact.php":
        title, active, db = "Kontakt", "contact", False
    elif name.startswith("edit-"):
        title, db = "Upraviť", True
        active = "data" if "lookup table" in role else entity[0]
    else:
        title, active, db = name[:-4].capitalize(), name[:-4], True
    body = h
    if db:
        body += "require 'db.php';\n"
    body += f"$title = '{title}';\n$active = '{active}';\n$content = 'content/{name}';\ninclude 'template.php';\n"
    return body


CSS = """/* ROLA: vlastné CSS k Bootstrap. Pripája ho template.php, platí pre každú stránku. */

body {
  padding-top: 4.5rem;          /* menu je fixed-top, obsah začína pod ním */
}
"""


# ---------------------------------------------------------------- unify.txt

def guess_schema():
    """Zo sql/schema.sql odhadne main entity a lookup tables. Je to len návrh, treba ho skontrolovať."""
    path = os.path.join(ROOT, "sql", "schema.sql")
    if not os.path.isfile(path):
        return None, []
    text = re.sub(r"--.*$", "", read(path), flags=re.M)
    tables = {}
    for m in re.finditer(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\(([^;]*);", text, flags=re.I):
        tables[m.group(1)] = [x.lower() for x in re.findall(r"REFERENCES\s+`?(\w+)`?", m.group(2), flags=re.I)]
    lower = {t.lower(): t for t in tables}
    pivots = [t for t, refs in tables.items() if len(set(refs)) >= 2]
    entity = None
    for pv in pivots:                                   # main entity: table z pivot table, ktorá má vlastný foreign key
        for ref in tables[pv]:
            if ref in lower and tables[lower[ref]]:
                entity = lower[ref]
    if entity is None:                                  # inak prvá table s foreign key, ktorá nie je pivot table
        for t, refs in tables.items():
            if refs and t not in pivots:
                entity = t
                break
    lookups = [t for t in tables if t != entity and t not in pivots]
    return entity, lookups


def one(table):
    """Slovo do názvu file: názov table v jednotnom čísle (odhad pre anglické názvy)."""
    if table.endswith("ies"):
        return table[:-3] + "y"
    if table.endswith("s"):
        return table[:-1]
    return table


def init():
    if not os.path.isdir(WEB):
        stop("v tomto priečinku nie je priečinok web/. Spusti script v priečinku repository.")
    if os.path.exists(PLAN):
        stop("unify.txt už existuje. Uprav ho, alebo ho zmaž a spusti --init znova.")
    entity, lookups = guess_schema()
    lines = ["# unify.txt: plán unifikácie. Riadky so znakom # na začiatku sú komentáre.",
             "#",
             "# 1. Skontroluj tables. Za názvom table je slovo do názvu file (názov v jednotnom čísle).",
             "#    Z entity: routes route vzniknú názvy routes.php, add-route.php, edit-route.php, delete-route.php."]
    lines.append(f"entity: {entity} {one(entity)}" if entity else "entity: TABLE SLOVO")
    for t in lookups:
        lines.append(f"lookup: {t} {one(t)}")
    if not lookups:
        lines.append("lookup: TABLE SLOVO")
    ent = (entity or "TABLE", one(entity) if entity else "SLOVO")
    expected = roles(ent, [(t, one(t)) for t in lookups])
    lines += ["",
              "# 2. Pri každom file napíš za šípku nový názov podľa pravidla. Namiesto názvu môže byť: " + DELETE,
              "#    Otáznik: script nový názov neurčil. Nahraď ho názvom zo zoznamu na konci alebo slovom " + DELETE + ".",
              "#    Cesty sú od priečinka web/."]
    current = php_files()
    used = set()
    for rel in current:
        base = os.path.basename(rel)
        if rel in expected:
            new = rel
        elif rel == "content/home.php":
            new = "content/index.php"
        elif base in ("form.php", "register.php") or rel.startswith("practice/") or "/practice/" in rel:
            new = DELETE
        else:
            new = "?"
        used.add(new)
        lines.append(f"{rel} -> {new}")
    free = [f for f in expected if f not in used]
    lines += ["", "# Názvy podľa pravidla, ktoré zatiaľ nemá žiadny file. Čo zostane voľné, vytvorí script ako nový file."]
    for f in free:
        lines.append(f"#   {f:<28} {expected[f][0]}")
    write(PLAN, "\n".join(lines) + "\n")
    say("Vytvorený unify.txt. Otvor ho, skontroluj tables a nahraď každý otáznik.")
    say("Potom spusti: python3 unify.py")


def load_plan():
    if not os.path.exists(PLAN):
        stop("chýba unify.txt. Najprv spusti: python3 unify.py --init")
    entity, lookups, mapping, problems = None, [], {}, []
    for n, raw in enumerate(read(PLAN).split("\n"), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(entity|lookup)\s*:\s*(\S+)\s+(\S+)$", line)
        if m:
            if m.group(2) == "TABLE":
                problems.append(f"riadok {n}: namiesto TABLE SLOVO napíš názov table a slovo do názvu file")
            elif m.group(1) == "entity":
                entity = (m.group(2), m.group(3))
            else:
                lookups.append((m.group(2), m.group(3)))
            continue
        m = re.match(r"^(\S+)\s*->\s*(\S+)$", line)
        if not m:
            problems.append(f"riadok {n}: nerozumiem riadku: {line}")
            continue
        old, new = m.group(1), m.group(2)
        if new == "?":
            problems.append(f"riadok {n}: {old} má stále otáznik")
        elif new != DELETE and not new.endswith(".php"):
            problems.append(f"riadok {n}: nový názov {new} nekončí na .php")
        if old in mapping:
            problems.append(f"riadok {n}: {old} je v unify.txt viackrát")
        mapping[old] = new
    if entity is None:
        problems.append("chýba riadok entity: TABLE SLOVO")
    current = set(php_files())
    for old in mapping:
        if old not in current:
            problems.append(f"{old}: taký file vo web/ nie je")
    for rel in sorted(current - set(mapping)):
        problems.append(f"{rel}: file je vo web/, ale nie je v unify.txt (doplň riadok alebo spusti --init nanovo)")
    targets = [new for new in mapping.values() if new not in (DELETE, "?")]
    for t in sorted(set(targets)):
        if targets.count(t) > 1:
            problems.append(f"{t}: tento nový názov majú viaceré files")
    if problems:
        say("unify.txt treba opraviť:")
        for p in problems:
            say("  - " + p)
        sys.exit(1)
    return entity, lookups, mapping


# ---------------------------------------------------------------- kontrola po unifikácii

def check(entity, lookups):
    """Vráti zoznam vecí, ktoré po unifikácii nesedia."""
    expected = roles(entity, lookups)
    current = set(php_files())
    notes = []
    for rel in sorted(current):
        code = without_comments(read(os.path.join(WEB, rel)))
        for token in sorted(set(TOKEN.findall(code))):
            if token not in current:
                notes.append(f"{rel}: odkaz na {token}, taký file vo web/ nie je")
    for rel in sorted(current):
        if "/" in rel or rel in ("db.php", "template.php") or rel.startswith("delete-"):
            continue
        if "content/" + rel not in current:
            notes.append(f"{rel}: chýba content file content/{rel}")
        elif f"content/{rel}" not in without_comments(read(os.path.join(WEB, rel))):
            notes.append(f"{rel}: $content nemá hodnotu 'content/{rel}'")
    if "template.php" in current:
        menu = without_comments(read(os.path.join(WEB, "template.php")))
        for item in ("index.php", f"{entity[0]}.php", f"add-{entity[1]}.php", "data.php", "stats.php", "contact.php"):
            if item not in menu:
                notes.append(f"template.php: v menu chýba odkaz na {item}")
    for rel in sorted(current - set(expected)):
        notes.append(f"{rel}: názov nie je podľa pravidla (ak file do aplikácie patrí, nechaj ho)")
    return notes


def app_map(entity, lookups):
    expected = roles(entity, lookups)
    current = set(php_files())
    rows = ["| file | rola | CRUD |", "|---|---|---|"]
    for rel, info in expected.items():
        if rel in current:
            rows.append(f"| `web/{rel}` | {info[0]} | {info[1]} |")
    for rel in sorted(current - set(expected)):
        rows.append(f"| `web/{rel}` | iné | |")
    return "\n".join(rows)


def write_map(entity, lookups):
    block = (MAP_START + "\n## Mapa aplikácie\n\n"
             + f"Main entity: `{entity[0]}`. Lookup tables: " + ", ".join(f"`{t}`" for t, _ in lookups) + ".\n\n"
             + app_map(entity, lookups) + "\n" + MAP_END)
    text = read(README) if os.path.exists(README) else ""
    if MAP_START in text and MAP_END in text:
        text = text[:text.index(MAP_START)] + block + text[text.index(MAP_END) + len(MAP_END):]
    else:
        text = text.rstrip("\n") + ("\n\n" if text.strip() else "") + block + "\n"
    write(README, text)


# ---------------------------------------------------------------- plán a spustenie

def plan(entity, lookups, mapping):
    expected = roles(entity, lookups)
    renames = {o: n for o, n in mapping.items() if n not in (DELETE, o)}
    deletes = [o for o, n in mapping.items() if n == DELETE]
    final = {(n if n != DELETE else None) for n in mapping.values()} - {None}
    missing = [f for f in expected if f not in final]
    return renames, deletes, missing, expected


def show_plan(entity, lookups, mapping):
    renames, deletes, missing, expected = plan(entity, lookups, mapping)
    say(f"Main entity: {entity[0]} (slovo do názvu file: {entity[1]})")
    say("Lookup tables: " + ", ".join(f"{t} ({w})" for t, w in lookups))
    say()
    say("Premenovať:")
    for o, n in renames.items():
        say(f"  {o} -> {n}")
    if not renames:
        say("  nič")
    say("Zmazať:")
    for o in deletes:
        say(f"  {o}")
    if not deletes:
        say("  nič")
    say("Vytvoriť (v aplikácii chýba):")
    for f in missing:
        say(f"  {f:<28} {expected[f][0]}")
    if not missing:
        say("  nič")
    other = sorted(n for n in mapping.values() if n != DELETE and n not in expected)
    if other:
        say("Názvy mimo pravidla (zostanú, ak ich tak chceš):")
        for f in other:
            say(f"  {f}")


def run(entity, lookups, mapping):
    git = is_git()
    renames, deletes, missing, expected = plan(entity, lookups, mapping)
    changes = []

    # 1. premenovanie v dvoch krokoch cez dočasné názvy, aby si files navzájom neprekážali
    for i, old in enumerate(renames):
        move(old, f"__unify_{i}.tmp", git)
    for i, (old, new) in enumerate(renames.items()):
        move(f"__unify_{i}.tmp", new, git)
        changes.append(f"premenovaný: {old} -> {new}")

    # 2. zmazanie
    for old in deletes:
        remove(old, git)
        changes.append(f"zmazaný: {old}")

    # 3. odkazy: každý starý názov v kóde sa nahradí novým
    deleted = set(deletes)
    lost = []
    for rel in php_files():
        path = os.path.join(WEB, rel)
        text = read(path)
        fixed = []

        def swap(m):
            token = m.group(1)
            if token in renames:
                fixed.append(f"{token} -> {renames[token]}")
                return renames[token]
            if token in deleted:
                lost.append(f"{rel}: odkaz na zmazaný file {token}")
            return token

        new_text = TOKEN.sub(swap, text)
        if new_text != text:
            write(path, new_text)
            for f in sorted(set(fixed)):
                changes.append(f"odkaz opravený v {rel}: {f}")

    # 4. chýbajúce files
    for rel in missing:
        write(os.path.join(WEB, rel), skeleton(rel, expected[rel], entity))
        changes.append(f"vytvorený: {rel}")
    css = os.path.join(WEB, "css", "style.css")
    if not os.path.exists(css) and os.path.exists(os.path.join(WEB, "template.php")) \
            and "css/style.css" in read(os.path.join(WEB, "template.php")):
        write(css, CSS)
        changes.append("vytvorený: css/style.css")

    # 5. komentár s rolou na začiatok každého file
    for rel in php_files():
        if rel in expected and add_header(rel, expected[rel]):
            changes.append(f"komentár s rolou doplnený: {rel}")

    # 6. mapa aplikácie do README.md
    write_map(entity, lookups)
    changes.append("mapa aplikácie zapísaná do README.md")

    say("Zmeny:")
    for c in changes:
        say("  " + c)
    notes = lost + check(entity, lookups)
    say()
    if notes:
        say("Treba dokončiť:")
        for n in notes:
            say("  - " + n)
    else:
        say("Kontrola: každý odkaz vedie na existujúci file, každá stránka má content file.")
    say()
    say("Ďalej: otvor aplikáciu v prehliadači, prejdi každú položku menu a potom:")
    say('  git add -A && git commit -m "unifikácia názvov files"')


def main():
    args = sys.argv[1:]
    if args == ["--init"]:
        init()
        return
    if args not in ([], ["--run"], ["--check"]):
        print(__doc__)
        sys.exit(1)
    if not os.path.isdir(WEB):
        stop("v tomto priečinku nie je priečinok web/. Spusti script v priečinku repository.")
    entity, lookups, mapping = load_plan()
    if args == ["--check"]:
        notes = check(entity, lookups)
        for n in notes:
            say("  - " + n)
        if not notes:
            say("Kontrola: každý odkaz vedie na existujúci file, každá stránka má content file.")
        return
    if args == ["--run"]:
        run(entity, lookups, mapping)
        keep = [l for l in read(PLAN).split("\n") if not re.match(r"^\S+\s*->\s*\S+$", l.strip())]
        while keep and not keep[-1].strip():
            keep.pop()
        cut = next((i for i, l in enumerate(keep) if l.startswith("# Názvy podľa pravidla")), len(keep))
        keep = keep[:cut] + [f"{rel} -> {rel}" for rel in php_files()]     # unify.txt po unifikácii: súčasný stav
        write(PLAN, "\n".join(keep) + "\n")
    else:
        show_plan(entity, lookups, mapping)
        say()
        say("Zatiaľ sa nič nezmenilo. Ak plán sedí, spusti: python3 unify.py --run")


if __name__ == "__main__":
    main()
