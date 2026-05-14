# Miljonimäng

AI-põhine ülesande valideerimise rakendus, mis kontrollib õppija arusaamist ülesande lahendusest miljonimängu formaadis.

**Grupp:** TAK25

## Projekti kirjeldus

Rakendus loeb `input/` kaustast ülesandeid (assignment.md + lahendusfailid) ja genereerib nende põhjal AI abil 15 valikvastustega küsimust. Kasutaja mängib miljonimängu, vastates küsimustele, mis kontrollivad tema arusaamist lahendusest – mitte ainult mälu.

Rakendus toetab:
- Mitut ülesannet numbriliste alamkaustadena
- AI-põhist küsimuste genereerimist (OpenAI GPT) või simuleeritud küsimusi kui API-võti puudub
- Miljonimängu reegleid (15 küsimust, turvatasemed, punktid)
- Õlekõrsi: 50:50, Küsi AI-lt, Küsi publikult
- Erineva raskusastmega küsimusi (1–5 lihtsad, 6–10 keskmised, 11–15 rasked)
- Küsimuste vahemällu salvestamist (caching)
- Tulemuste salvestamist ja mänguajalugu
- Markdowni kuvamist ja koodi süntaksivärvimist
- Küsimuste uuesti genereerimist

## Kasutatud tehnoloogiad

- **Python 3** – serveripoolne loogika
- **Flask** – veebiraamistik
- **OpenAI API** (GPT-4o-mini) – küsimuste genereerimine
- **HTML/CSS/JavaScript** – kasutajaliides
- **highlight.js** – koodi süntaksivärvimine
- **marked.js** – Markdowni renderdamine
- **JSON** – andmevahetus kliendi ja serveri vahel, tulemuste salvestamine

## Käivitamise juhend

### Eeldused
- Python 3.7+
- Git

### 1. Klooni repositoorium
```bash
git clone <repo-url>
cd miljonimang
```

### 2. Loo ja aktiveeri virtuaalkeskkond (soovitatav)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Paigalda sõltuvused
```bash
pip install -r requirements.txt
```

### 4. (Valikuline) Sea OpenAI API võti
Kui soovid AI-põhist küsimuste genereerimist, sea keskkonnamuutuja:
```bash
# Windows PowerShell:
$env:OPENAI_API_KEY="sinu-api-voti"
# macOS/Linux:
export OPENAI_API_KEY="sinu-api-voti"
```
Ilma API-võtmeta kasutab rakendus simuleeritud küsimusi.

### 5. Käivita rakendus
```bash
python app.py
```

### 6. Ava brauseris
```
http://localhost:5000
```

## Input-kausta struktuur

```
input/
  001/
    assignment.md      # Ülesande püstitus ja nõuded
    index.html          # Lahenduse failid
    style.css
    script.js

  002/
    assignment.md
    src/
      app.js
      data.json

  003/
    assignment.md
    solution/
      main.py
```

Iga ülesande kaust peab sisaldama vähemalt `assignment.md` faili. Ülejäänud failid on lahenduse osad, mida kasutatakse küsimuste kontekstina.

Kaustade nimed peavad olema numbrilised (001, 002 jne). Ülesande pealkiri võetakse `assignment.md` esimesest `# Pealkiri` reast.

## AI küsimuste genereerimise loogika

1. **Konteksti kogumine**: server loeb valitud ülesande `assignment.md` ja kõik lahenduse failid.
2. **Vahemälu kontroll**: kui samale ülesandele on juba küsimused genereeritud (MD5 räsi alusel), tagastatakse need.
3. **Prompti koostamine**: `prompts/question-generation.md` šabloon täidetakse päris sisuga (ülesande kirjeldus + lahenduse failid).
4. **AI päring**: saadetakse OpenAI GPT-4o-mini-le prompt, mis palub koostada 15 küsimust.
5. **JSON-i parsitakse**: AI vastus (JSON) parsitakse ja salvestatakse vahemällu.
6. **Simuleeritud režiim**: kui API võti puudub, kasutatakse eeldefineeritud küsimuste malli.

Prompt on nähtav failis: [prompts/question-generation.md](prompts/question-generation.md)

### Prompti sisu
- Küsimused peavad põhinema `assignment.md` ja lahendusfailide sisul
- Igal küsimusel 4 vastusevarianti, ainult 1 õige
- Raskusastmed: 1–5 lihtsad (põhimõisted), 6–10 keskmised (loogika), 11–15 rasked (süvaanalüüs)
- Vastus peab sisaldama lühikest selgitust
- Väljund JSON-kujul

## Mängu reeglid

- 15 küsimust, igaühel 4 vastusevarianti
- Ainult üks vastus on õige
- Vale vastuse korral mäng lõpeb ja tulemus langeb viimasele turvatasemele
- Õige vastuse korral liigutakse järgmise küsimuse juurde

### Punktitabel

| Küsimus | Punktid |
|---------|---------|
| 1 | 100 |
| 2 | 200 |
| 3 | 300 |
| 4 | 500 |
| 5 | **1 000** (turvatase) |
| 6 | 2 000 |
| 7 | 4 000 |
| 8 | 8 000 |
| 9 | 16 000 |
| 10 | **32 000** (turvatase) |
| 11 | 64 000 |
| 12 | 125 000 |
| 13 | 250 000 |
| 14 | 500 000 |
| 15 | **1 000 000** (turvatase) |

### Õlekõrred
- **50:50** – eemaldab kaks vale vastusevarianti
- **Küsi AI-lt** – AI annab lühikese vihje (ei ütle otsest vastust)
- **Küsi publikult** – simuleeritud publikuhääletus graafilise vaatega (lihtsamate küsimuste puhul õigem)

## Täiendavad funktsioonid

### Küsimuste vahemällu salvestamine
Küsimused salvestatakse `data/cache/` kausta MD5 räsi alusel (ülesande sisu + failide põhjal). Vahemälu kehtib 1 tund, mis vähendab korduvaid API päringuid.

### Tulemuste salvestamine
Iga mängu tulemus salvestatakse `data/results.json` faili. Salvestatakse: ülesande ID ja pealkiri, punktisumma, küsimuste arv, võit/kaotus, kuupäev.

### Mänguajalugu
Lehel `/history` saab vaadata kõigi salvestatud mängude ajalugu.

### Küsimuste uuesti genereerimine
Mänguvaates on nupp "Uued küsimused", mis genereerib olemasoleva ülesande põhjal uued küsimused (eemaldab vahemälu).

### Ülesande sisu kuvamine
Mänguvaates saab nupuga "Näita ülesannet" avada ülesande kirjelduse ja lahenduse failid Markdowni ja süntaksivärvimisega.

### Markdowni ja koodi kuvamine
- `marked.js` renderdab `assignment.md` sisu ilusa Markdownina
- `highlight.js` värvib koodifailide süntaksi (toetab JavaScript, Python, CSS, HTML, JSON)

## Teadaolevad piirangud

- Simuleeritud küsimused ei ole täielikult dünaamilised – need on eeldefineeritud ja sõltuvad ainult failitüüpidest
- AI genereeritud küsimuste kvaliteet sõltub API võtme olemasolust ja mudeli võimekusest
- Kasutajate süsteem puudub – kõik mängud on anonüümsed (põhinevad sessioonil)
- Alamkaustade sügavus on piiramatu, kuid binaarfaile ignoreeritakse
- Tulemused salvestatakse JSON-faili, mitte andmebaasi (sobib väikese kasutajaskonna jaoks)
- Mänguajalugu kuvab kõigi kasutajate tulemusi koos (sessioonipõhist eraldamist pole)

## Edasiarenduse võimalused

- Päris AI API ühenduse täiustamine (rohkem mudeleid, parem prompt)
- Tulemuste salvestamine andmebaasi (SQLite, PostgreSQL)
- Kasutajate süsteem (registreerimine, sisselogimine)
- Õpetaja vaade – statistika ja tulemuste analüüs
- Veebiliidesest ülesannete lisamine ja haldamine
- Täiendavad õlekõrred (näiteks "vaheta küsimus", "telefonisõber")
- Raskusastmete dünaamilisem jaotus vastavalt kasutaja eelnevatele vastustele
- Responsive disaini parendus mobiilivaate jaoks
- Täiendav küsimuste tüüpide tugi (lünktekst, järjestamine)

## Litsents
Õppe-eesmärkidel projekt.
