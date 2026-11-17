# cv08: CRUD aplikácia

Stránka týždňa: https://beata.stehlikova.website.tuke.sk/ti/09.html
Prijať zadanie: https://classroom50.org/tuke-fberg-stehlikova/technologie-internetu-5k/assignments/cv08/accept?k=tcc8jmx0

Výsledkom je hotová aplikácia: files majú názvy podľa tabuľky rolí a lookup tables aj main entity majú každú operáciu CRUD. `ENTITY` je názov table svojej main entity, `LOOKUP` názov svojej lookup table.

**Odovzdávaš** (v repository a vo svojom webovom priestore na sigma.tuke.sk v `ti/cv08/`, obsah `web/` aj v `ti/projekt/`):

- aplikáciu z cv07 s názvami files podľa tabuľky rolí, každý file s komentárom `// ROLA:` na začiatku
- `web/edit-LOOKUP.php` + `web/content/edit-LOOKUP.php` a `web/delete-LOOKUP.php` pre každú lookup table
- `web/edit-ENTITY.php` + `web/content/edit-ENTITY.php` a `web/delete-ENTITY.php` pre main entity
- `web/content/data.php` a `web/content/detail.php` s odkazom Upraviť a buttonom Zmazať
- `web/template.php` s array `$messages` a výpisom správy pod `<h1>`
- `README.md` s mapou aplikácie (zapíše ju `unify.py`), `unify.py` a `unify.txt`

**Hodnotenie:** 1 bod. Aplikácia s názvami files podľa tabuľky rolí, s úpravou a zmazaním record v lookup tables aj v main entity s pivot table a so správou po každej operácii funguje vo svojom webovom priestore na sigma.tuke.sk, kód je v repository. Po push sa spustia testy (25 kontrol); zelený výsledok znamená, že files a požadované časti kódu sú na mieste, body udeľuje učiteľka.

Ak v Kubeflow chýbajú rozšírenia, príkaz na obnovu je v návode 04 Odovzdávanie.

## Tabuľka rolí a pravidlo názvov

Názov file je daný rolou. Píše sa anglicky, malými písmenami, bez diakritiky, slová spája pomlčka. `ENTITY` je názov table main entity, `LOOKUP` názov lookup table. Files `add-`, `edit-` a `delete-` majú názov v jednotnom čísle.

| Rola | File | CRUD | Lezecká stena | Knižnica |
|---|---|---|---|---|
| main entity, zoznam s filtrom | `ENTITY.php` | Read | `routes.php` | `books.php` |
| main entity, detail jedného record | `detail.php` | Read | `detail.php` | `detail.php` |
| main entity, formulár na nový record | `add-ENTITY.php` | Create | `add-route.php` | `add-book.php` |
| main entity, formulár na úpravu jedného record | `edit-ENTITY.php` | Update | `edit-route.php` | `edit-book.php` |
| main entity, zmazanie jedného record | `delete-ENTITY.php` | Delete | `delete-route.php` | `delete-book.php` |
| lookup tables, formuláre na nový record a výpis tables | `data.php` | Create, Read | `data.php` | `data.php` |
| lookup table, formulár na úpravu jedného record | `edit-LOOKUP.php` | Update | `edit-grade.php`, `edit-style.php` | `edit-genre.php`, `edit-tag.php` |
| lookup table, zmazanie jedného record | `delete-LOOKUP.php` | Delete | `delete-grade.php`, `delete-style.php` | `delete-genre.php`, `delete-tag.php` |
| prehľad, výpisy s JOIN a GROUP BY | `stats.php` | Read | `stats.php` | `stats.php` |
| úvodná stránka | `index.php` | | `index.php` | `index.php` |
| stránka s kontaktom | `contact.php` | | `contact.php` | `contact.php` |
| pripojenie k databáze | `db.php` | | `db.php` | `db.php` |
| template | `template.php` | | `template.php` | `template.php` |

## Unifikácia

Script `unify.py` sa spúšťa v termináli Kubeflow v priečinku repository cv08.

| Príkaz | Čo spraví |
|---|---|
| `python3 unify.py --init` | vytvorí `unify.txt`: tables zo `sql/schema.sql` a zoznam files vo `web/` s návrhom nového názvu |
| `python3 unify.py` | vypíše plán podľa `unify.txt`, files nemení |
| `python3 unify.py --run` | vykoná plán |
| `python3 unify.py --check` | skontroluje odkazy a dvojice file stránky a content file, files nemení |

## Prompty

Prompt U pomáha s `unify.txt`. Prikladá sa `unify.txt`, `sql/schema.sql` a tabuľka rolí z časti Z čoho sa aplikácia skladá.

```text
Prikladám unify.txt z predmetu Technológie internetu, sql/schema.sql a tabuľku rolí s pravidlom názvov files. V unify.txt skontroluj riadky entity a lookup podľa schema.sql. Každý otáznik nahraď novým názvom file podľa tabuľky rolí alebo slovom zmazat. Riadky bez otáznika nemeň. Vráť celý unify.txt a pod ním pri každom zmenenom riadku jednou vetou, akú rolu má file a prečo.
```

Prompt A, UPDATE a DELETE pre lookup table. Prikladá sa `sql/schema.sql`, `web/template.php`, `web/content/data.php` a files, ktoré vytvoril `unify.py`: `web/edit-LOOKUP.php`, `web/content/edit-LOOKUP.php`, `web/delete-LOOKUP.php`.

```text
PHP aplikácia: stránku tvorí file stránky web/X.php ($title, $active, $content, include 'template.php') a content file web/content/X.php. $pdo je pripravené v db.php. Pre lookup table LOOKUP zo schema.sql doplň priložené files, komentár s rolou na začiatku každého file nechaj. 1. content/data.php: v tabuľke lookup table pridaj column akcia s odkazom Upraviť (edit-LOOKUP.php?id=...) a formulárom method POST action delete-LOOKUP.php s hidden input id a buttonom Zmazať. 2. content/edit-LOOKUP.php: id z $_GET; po POST hodnoty z $_POST do premenných, kontrola povinných, SELECT ... WHERE name = ? AND id <> ? s fetch na kontrolu duplicity, UPDATE ... WHERE id = ? cez prepare a execute, správa do $message; potom SELECT record podľa id, keď neexistuje správa a return; správa v alert a Bootstrap formulár method POST bez action s hodnotami z databázy vo value. 3. delete-LOOKUP.php bez content file a bez template: require 'db.php'; keď request nie je POST, header('Location: data.php') a exit; id z $_POST; SELECT COUNT(*) na table, ktorá na LOOKUP ukazuje cez foreign key; keď je počet väčší ako 0, redirect na data.php?msg=used; inak DELETE cez prepare a execute a redirect na data.php?msg=deleted; po každom header exit. 4. template.php: na začiatok array $messages s keys deleted a used, pod <h1> výpis správy podľa $_GET['msg'] v alert. Bez funkcií a tried, komentár pri každom riadku po slovensky. Text správ nechaj ako // DOPLŇ.
```

Prompt B, UPDATE a DELETE pre main entity. Prikladá sa `sql/schema.sql`, `web/content/add-ENTITY.php`, `web/content/detail.php` a files, ktoré vytvoril `unify.py`: `web/edit-ENTITY.php`, `web/content/edit-ENTITY.php`, `web/delete-ENTITY.php`.

```text
Pre tú istú aplikáciu doplň priložené files pre main entity ENTITY, komentár s rolou na začiatku každého file nechaj. 1. content/detail.php: SELECT nech vracia aj id; pod výpis odkaz Upraviť (edit-ENTITY.php?id=...) a formulár method POST action delete-ENTITY.php s hidden input id a buttonom Zmazať. 2. content/edit-ENTITY.php: formulár z priloženého content/add-ENTITY.php zachovaj, zmeň len to, čo píšem. id z $_GET; najprv SELECT, či record existuje, inak správa a return. Po POST: hodnoty z $_POST do premenných, kontrola povinných, UPDATE ... WHERE id = ?, potom DELETE dvojíc tohto record v pivot table a INSERT zaškrtnutých vo foreach cez jeden pripravený príkaz, správa do $message. Potom SELECT record a SELECT jeho dvojíc, array_column na array id. Vo formulári hodnoty z databázy: value pri input, text medzi tagmi textarea, selected pri option, checked cez in_array pri checkbox. 3. delete-ENTITY.php bez content file a bez template: require 'db.php'; keď request nie je POST, redirect na ENTITY.php; id z $_POST; DELETE cez prepare a execute; header('Location: ENTITY.php?msg=deleted') a exit. Bez funkcií a tried, komentár pri každom riadku po slovensky. Validačné pravidlá nechaj ako // DOPLŇ.
```

Prečo sú prompty napísané práve takto:

- priložené files namiesto opisu: AI vidí presné názvy tables, columns a files a dopĺňa do nich,
- „komentár s rolou nechaj": mapa aplikácie v `README.md` a komentáre vo files zostanú rovnaké,
- „formulár zachovaj, zmeň len to, čo píšem" bráni AI prerobiť formulár z cv07,
- „bez content file a bez template" pri delete: AI nevloží do file HTML a `header()` bude fungovať,
- „po každom header exit": bez `exit` by sa po kontrole vykonal aj DELETE,
- `// DOPLŇ` necháva texty správ a validačné pravidlá na autorovi aplikácie,
- prompt U mení len riadky s otáznikom: premenovanie robí `unify.py`, AI len navrhne názvy.

## Úlohy

**9.1** Kubeflow: skontroluj rozšírenia (SFTP, Five Server, Intelephense). Ak chýbajú, spusti v termináli príkaz na obnovu z návodu [04 Odovzdávanie](https://beata.stehlikova.website.tuke.sk/navody/04-odovzdavanie.html).

**9.2** `git clone` repository cv08. V repository je `README.md` a `unify.py`. Prekopíruj aplikáciu z cv07:

```bash
rsync -a --exclude .git --exclude README.md cv07/ cv08/
```

V Adminer spusti `schema.sql` a potom `seed.sql`, aby aplikácia začínala z čistých dát. Commit.

**9.3** Unifikácia (ukážka 1). V priečinku cv08 spusti `python3 unify.py --init`. Otvor `unify.txt`, skontroluj riadky `entity` a `lookup` a nahraď každý otáznik názvom podľa tabuľky rolí alebo slovom `zmazat` (pomôže prompt U). Spusti `python3 unify.py`, prečítaj plán a potom `python3 unify.py --run`.

**9.4** Dokonči, čo script vypísal pod „Treba dokončiť". Menu v `template.php` má odkazy na `index.php`, `ENTITY.php`, `add-ENTITY.php`, `data.php`, `stats.php` a `contact.php`. Spusti `python3 unify.py --check`. V prehliadači otvor každú položku menu. Commit.

**9.5** Lookup table, UPDATE (ukážky 3 a 4, prompt A). V `content/data.php` má každý record lookup table odkaz Upraviť. `edit-LOOKUP.php` s `content/edit-LOOKUP.php`: formulár s hodnotami z databázy, UPDATE cez prepare a execute, kontrola duplicity s `AND id <> ?`, správa nad formulárom. Over: uloženie bez zmeny, uloženie so zmenou, `name`, ktorý už má iný record.

**9.6** Lookup table, DELETE (ukážky 2 a 5, prompt A). V `content/data.php` má každý record lookup table button Zmazať vo formulári `method="post"`. `delete-LOOKUP.php`: kontrola použitia cez `SELECT COUNT(*)`, DELETE, redirect. V `template.php` array `$messages` a výpis správy pod `<h1>`. Over: zmazanie použitého record, zmazanie record, ktorý použitý nie je. Commit.

**9.7** To isté ako 9.5 a 9.6 pre každú ďalšiu lookup table (vo vzore `edit-style.php` a `delete-style.php`). Pri lookup table s reláciou M:N kontrola počíta dvojice v pivot table.

**9.8** Main entity, odkaz Upraviť a button Zmazať v `content/detail.php` (ukážka 6, prompt B).

**9.9** Main entity, UPDATE (ukážka 7, prompt B). `edit-ENTITY.php` s `content/edit-ENTITY.php`: formulár z `content/add-ENTITY.php` s hodnotami z databázy, UPDATE, DELETE dvojíc v pivot table, INSERT zaškrtnutých, správa nad formulárom. Over v `data.php`, že dvojice v pivot table sedia so zaškrtnutými checkboxmi. Commit.

**9.10** Main entity, DELETE (ukážka 8, prompt B). `delete-ENTITY.php`: DELETE a redirect na `ENTITY.php?msg=deleted`. Over v `data.php`, že so zmazaným record zmizli aj jeho dvojice v pivot table. Do komentára v `delete-ENTITY.php` napíš, ktorý riadok v `schema.sql` to zabezpečil.

**9.11** Spusti `python3 unify.py --check` a over, že mapa aplikácie v `README.md` sedí s files vo `web/`. Commit a push, aspoň 4 commity v rôznych krokoch (napr. po 9.2, 9.4, 9.6, 9.9).

**9.12** Upload Folder: `cv08` do `ti/cv08/` a obsah `web/` do `ti/projekt/`. Over vo svojom webovom priestore na sigma.tuke.sk: každá položka menu funguje, úprava a zmazanie fungujú pre lookup tables aj main entity, po každej operácii je správa.

---

# cv08: CRUD application

Week page: https://beata.stehlikova.website.tuke.sk/ti/09.html
Accept the assignment: https://classroom50.org/tuke-fberg-stehlikova/technologie-internetu-5k/assignments/cv08/accept?k=tcc8jmx0

The result is a complete application: the files are named according to the table of roles and the lookup tables and the main entity have every CRUD operation. `ENTITY` is the name of the table of your main entity, `LOOKUP` the name of your lookup table.

**You submit** (in the repository and in your web space on sigma.tuke.sk in `ti/cv08/`, the content of `web/` also in `ti/projekt/`):

- the application from cv07 with file names according to the table of roles, every file with the comment `// ROLA:` at the beginning
- `web/edit-LOOKUP.php` + `web/content/edit-LOOKUP.php` and `web/delete-LOOKUP.php` for every lookup table
- `web/edit-ENTITY.php` + `web/content/edit-ENTITY.php` and `web/delete-ENTITY.php` for the main entity
- `web/content/data.php` and `web/content/detail.php` with the link Upraviť and the button Zmazať
- `web/template.php` with the array `$messages` and the message printed below `<h1>`
- `README.md` with the map of the application (written by `unify.py`), `unify.py` and `unify.txt`

**Grading:** 1 point. The application with file names according to the table of roles, with editing and deleting of a record in the lookup tables and in the main entity with the pivot table and with a message after every operation works in your web space on sigma.tuke.sk, and the code is in the repository. Tests run after the push (25 checks); a green result means the files and the required parts of the code are in place, points are awarded by the teacher.

If extensions are missing in Kubeflow, the restore command is in the guide 04 Submitting.

## Table of roles and the naming rule

The name of a file is given by its role. It is written in English, in lowercase, without diacritics, words joined by a hyphen. `ENTITY` is the name of the main entity table, `LOOKUP` the name of a lookup table. The files `add-`, `edit-` and `delete-` use the singular.

| Role | File | CRUD | Climbing wall | Library |
|---|---|---|---|---|
| main entity, list with a filter | `ENTITY.php` | Read | `routes.php` | `books.php` |
| main entity, detail of one record | `detail.php` | Read | `detail.php` | `detail.php` |
| main entity, form for a new record | `add-ENTITY.php` | Create | `add-route.php` | `add-book.php` |
| main entity, form to edit one record | `edit-ENTITY.php` | Update | `edit-route.php` | `edit-book.php` |
| main entity, deleting one record | `delete-ENTITY.php` | Delete | `delete-route.php` | `delete-book.php` |
| lookup tables, forms for a new record and listing of tables | `data.php` | Create, Read | `data.php` | `data.php` |
| lookup table, form to edit one record | `edit-LOOKUP.php` | Update | `edit-grade.php`, `edit-style.php` | `edit-genre.php`, `edit-tag.php` |
| lookup table, deleting one record | `delete-LOOKUP.php` | Delete | `delete-grade.php`, `delete-style.php` | `delete-genre.php`, `delete-tag.php` |
| overview, listings with JOIN and GROUP BY | `stats.php` | Read | `stats.php` | `stats.php` |
| home page | `index.php` | | `index.php` | `index.php` |
| contact page | `contact.php` | | `contact.php` | `contact.php` |
| database connection | `db.php` | | `db.php` | `db.php` |
| template | `template.php` | | `template.php` | `template.php` |

## Unification

The script `unify.py` is run in the Kubeflow terminal in the folder of the repository cv08. Its output is in Slovak.

| Command | What it does |
|---|---|
| `python3 unify.py --init` | creates `unify.txt`: the tables from `sql/schema.sql` and the list of files in `web/` with a proposed new name |
| `python3 unify.py` | prints the plan from `unify.txt`, changes no files |
| `python3 unify.py --run` | carries out the plan |
| `python3 unify.py --check` | checks the links and the pairs of page file and content file, changes no files |

## Prompts

Prompt U helps with `unify.txt`. Attach `unify.txt`, `sql/schema.sql` and the table of roles from the part What the application consists of.

```text
I attach unify.txt from the course Internet Technologies, sql/schema.sql and the table of roles with the file naming rule. In unify.txt check the lines entity and lookup against schema.sql. Replace every question mark with a new file name according to the table of roles or with the word zmazat. Do not change lines without a question mark. Return the whole unify.txt and below it, for every changed line, one sentence saying which role the file has and why.
```

Prompt A, UPDATE and DELETE for a lookup table. Attach `sql/schema.sql`, `web/template.php`, `web/content/data.php` and the files created by `unify.py`: `web/edit-LOOKUP.php`, `web/content/edit-LOOKUP.php`, `web/delete-LOOKUP.php`.

```text
A PHP application: a page consists of the page file web/X.php ($title, $active, $content, include 'template.php') and the content file web/content/X.php. $pdo is ready in db.php. For the lookup table LOOKUP from schema.sql complete the attached files; keep the comment with the role at the beginning of every file. 1. content/data.php: in the table of the lookup table add a column akcia with the link Upraviť (edit-LOOKUP.php?id=...) and a form method POST action delete-LOOKUP.php with a hidden input id and the button Zmazať. 2. content/edit-LOOKUP.php: id from $_GET; after POST values from $_POST into variables, check of required values, SELECT ... WHERE name = ? AND id <> ? with fetch as a duplicate check, UPDATE ... WHERE id = ? with prepare and execute, a message into $message; then SELECT the record by id, when it does not exist a message and return; the message in an alert and a Bootstrap form method POST without action with the values from the database in value. 3. delete-LOOKUP.php without a content file and without the template: require 'db.php'; when the request is not POST, header('Location: data.php') and exit; id from $_POST; SELECT COUNT(*) on the table that points to LOOKUP with a foreign key; when the count is greater than 0, redirect to data.php?msg=used; otherwise DELETE with prepare and execute and redirect to data.php?msg=deleted; exit after every header. 4. template.php: at the beginning the array $messages with the keys deleted and used, below <h1> the message for $_GET['msg'] in an alert. No functions or classes, a comment on every line in Slovak. Leave the texts of the messages as // DOPLŇ.
```

Prompt B, UPDATE and DELETE for the main entity. Attach `sql/schema.sql`, `web/content/add-ENTITY.php`, `web/content/detail.php` and the files created by `unify.py`: `web/edit-ENTITY.php`, `web/content/edit-ENTITY.php`, `web/delete-ENTITY.php`.

```text
For the same application complete the attached files for the main entity ENTITY; keep the comment with the role at the beginning of every file. 1. content/detail.php: the SELECT should also return id; below the output the link Upraviť (edit-ENTITY.php?id=...) and a form method POST action delete-ENTITY.php with a hidden input id and the button Zmazať. 2. content/edit-ENTITY.php: keep the form from the attached content/add-ENTITY.php, change only what I write. id from $_GET; first SELECT whether the record exists, otherwise a message and return. After POST: values from $_POST into variables, check of required values, UPDATE ... WHERE id = ?, then DELETE of the pairs of this record in the pivot table and INSERT of the checked ones in a foreach with one prepared statement, a message into $message. Then SELECT the record and SELECT its pairs, array_column to get an array of ids. In the form the values from the database: value for input, text between the textarea tags, selected for option, checked with in_array for checkbox. 3. delete-ENTITY.php without a content file and without the template: require 'db.php'; when the request is not POST, redirect to ENTITY.php; id from $_POST; DELETE with prepare and execute; header('Location: ENTITY.php?msg=deleted') and exit. No functions or classes, a comment on every line in Slovak. Leave the validation rules as // DOPLŇ.
```

Why the prompts are written this way:

- attached files instead of a description: the AI sees the exact names of tables, columns and files and completes them,
- "keep the comment with the role": the map of the application in `README.md` and the comments in the files stay the same,
- "keep the form, change only what I write" stops the AI from rewriting the form from cv07,
- "without a content file and without the template" for delete: the AI puts no HTML into the file and `header()` works,
- "exit after every header": without `exit` DELETE would be executed even after the check,
- `// DOPLŇ` leaves the texts of the messages and the validation rules to the author of the application,
- prompt U changes only the lines with a question mark: renaming is done by `unify.py`, the AI only proposes names.

## Tasks

**9.1** Kubeflow: check the extensions (SFTP, Five Server, Intelephense). If they are missing, run the restore command from the guide [04 Submitting](https://beata.stehlikova.website.tuke.sk/navody/04-odovzdavanie.html) in the terminal.

**9.2** `git clone` the repository cv08. It contains `README.md` and `unify.py`. Copy the application from cv07:

```bash
rsync -a --exclude .git --exclude README.md cv07/ cv08/
```

In Adminer run `schema.sql` and then `seed.sql` so that the application starts from clean data. Commit.

**9.3** Unification (example 1). In the folder cv08 run `python3 unify.py --init`. Open `unify.txt`, check the lines `entity` and `lookup` and replace every question mark with a name from the table of roles or with the word `zmazat` (prompt U helps). Run `python3 unify.py`, read the plan and then run `python3 unify.py --run`.

**9.4** Finish what the script printed under „Treba dokončiť" (to be finished). The menu in `template.php` has links to `index.php`, `ENTITY.php`, `add-ENTITY.php`, `data.php`, `stats.php` and `contact.php`. Run `python3 unify.py --check`. Open every menu item in the browser. Commit.

**9.5** Lookup table, UPDATE (examples 3 and 4, prompt A). In `content/data.php` every record of a lookup table has the link Upraviť. `edit-LOOKUP.php` with `content/edit-LOOKUP.php`: a form with the values from the database, UPDATE with prepare and execute, a duplicate check with `AND id <> ?`, a message above the form. Verify: saving without a change, saving with a change, a `name` that another record already has.

**9.6** Lookup table, DELETE (examples 2 and 5, prompt A). In `content/data.php` every record of a lookup table has the button Zmazať in a form with `method="post"`. `delete-LOOKUP.php`: a check of use with `SELECT COUNT(*)`, DELETE, redirect. In `template.php` the array `$messages` and the message printed below `<h1>`. Verify: deleting a used record, deleting a record that is not used. Commit.

**9.7** The same as 9.5 and 9.6 for every other lookup table (in the sample `edit-style.php` and `delete-style.php`). For a lookup table with an M:N relation the check counts the pairs in the pivot table.

**9.8** Main entity, the link Upraviť and the button Zmazať in `content/detail.php` (example 6, prompt B).

**9.9** Main entity, UPDATE (example 7, prompt B). `edit-ENTITY.php` with `content/edit-ENTITY.php`: the form from `content/add-ENTITY.php` with the values from the database, UPDATE, DELETE of the pairs in the pivot table, INSERT of the checked ones, a message above the form. Verify in `data.php` that the pairs in the pivot table match the checked checkboxes. Commit.

**9.10** Main entity, DELETE (example 8, prompt B). `delete-ENTITY.php`: DELETE and a redirect to `ENTITY.php?msg=deleted`. Verify in `data.php` that the pairs of the deleted record disappeared from the pivot table. In a comment in `delete-ENTITY.php` write which line of `schema.sql` ensured that.

**9.11** Run `python3 unify.py --check` and verify that the map of the application in `README.md` matches the files in `web/`. Commit and push, at least 4 commits at different steps (e.g. after 9.2, 9.4, 9.6, 9.9).

**9.12** Upload Folder: `cv08` to `ti/cv08/` and the content of `web/` to `ti/projekt/`. Verify in your web space on sigma.tuke.sk: every menu item works, editing and deleting work for the lookup tables and the main entity, there is a message after every operation.
