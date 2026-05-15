import json
import os
import random

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

PROMPT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "question-generation.md")


def load_prompt_template():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(assignment_data):
    template = load_prompt_template()
    solution_text = ""
    for path, content in assignment_data["solution_files"].items():
        solution_text += f"\n--- Fail: {path} ---\n{content}\n"
    prompt = template.replace("{assignment_content}", assignment_data["content"])
    prompt = prompt.replace("{solution_files}", solution_text)
    return prompt


def generate_questions_with_ai(assignment_data, api_key=None):
    if not OPENAI_AVAILABLE:
        return None

    client = openai.OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    prompt = build_prompt(assignment_data)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sa oled haridustehnoloog, kes koostab valikvastustega küsimusi programmeerimise testimise teemal. Õige vastuse indeks peab olema varieeruv (mitte alati 0)."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=4000,
        )
        content = response.choices[0].message.content

        json_match = content.strip()
        if "```json" in json_match:
            json_match = json_match.split("```json")[1].split("```")[0].strip()
        elif "```" in json_match:
            json_match = json_match.split("```")[1].split("```")[0].strip()

        questions = json.loads(json_match)
        return questions
    except Exception as e:
        print(f"AI viga: {e}")
        return None


def _shuffle_options(question):
    options = question["options"]
    correct = options[question["correctIndex"]]
    random.shuffle(options)
    question["correctIndex"] = options.index(correct)
    return question


def generate_simulated_questions(assignment_data):
    title = assignment_data["id"]
    files = list(assignment_data["solution_files"].keys())

    has_html = any(f.endswith(".html") for f in files)
    has_css = any(f.endswith(".css") for f in files)
    has_js = any(f.endswith(".js") for f in files)
    has_py = any(f.endswith(".py") for f in files)

    questions = [
        _shuffle_options({
            "level": 1,
            "question": "Mis on ühiktesti (unit test) peamine eesmärk?",
            "options": [
                "Kontrollida ühe väikse funktsiooni või meetodi korrektsust eraldiseisvalt",
                "Testida kogu süsteemi tervikuna",
                "Kontrollida kasutajaliidese välimust",
                "Testida andmebaasi jõudlust",
            ],
            "correctIndex": 0,
            "explanation": "Ühiktestid testivad väikseimaid koodiühikuid (funktsioone/meetodeid) isoleeritult.",
        }),
        _shuffle_options({
            "level": 2,
            "question": "Mida tähendab TDD (Test-Driven Development)?",
            "options": [
                "Kõigepealt kirjutatakse testid, seejärel realiseeritakse funktsionaalsus",
                "Kõigepealt kirjutatakse kood, seejärel testid",
                "Testid kirjutatakse alles pärast seda, kui kood on tootmisse viidud",
                "Testide kirjutamine ei ole TDD-s oluline",
            ],
            "correctIndex": 0,
            "explanation": "TDD puhul kirjutatakse esmalt testid, mis ebaõnnestuvad, seejärel realiseeritakse piisavalt koodi testide läbimiseks.",
        }),
        _shuffle_options({
            "level": 3,
            "question": "Millist Pythoni teeki kasutatakse enim unit-testide kirjutamiseks?",
            "options": [
                "unittest",
                "numpy",
                "flask",
                "matplotlib",
            ],
            "correctIndex": 0,
            "explanation": "Pythoni sisseehitatud unittest teek on kõige levinum valik ühiktestide kirjutamiseks.",
        }),
        _shuffle_options({
            "level": 4,
            "question": "Mida tähendab mockimine (mocking) testide kontekstis?",
            "options": [
                "Päris objektide asendamine simuleeritud objektidega, et isoleerida testitavat koodi",
                "Testide naeruvääristamine",
                "Testide automaatne genereerimine",
                "Koodi koopia loomine enne testimist",
            ],
            "correctIndex": 0,
            "explanation": "Mockid asendavad sõltuvused (nt API kutsed, andmebaas) simuleeritud objektidega, et testida ainult ühte koodi osa.",
        }),
        _shuffle_options({
            "level": 5,
            "question": "Milline on õige järjekord testi kirjutamisel TDD-s?",
            "options": [
                "Kirjuta ebaõnnestuv test -> kirjuta minimaalne kood testi läbimiseks -> refaktoreeri",
                "Kirjuta kood -> kirjuta test -> refaktoreeri",
                "Kirjuta test ja kood korraga",
                "Refaktoreeri -> kirjuta test -> kirjuta kood",
            ],
            "correctIndex": 0,
            "explanation": "TDD tsükkel on: Red (kirjuta ebaõnnestuv test) -> Green (kirjuta piisavalt koodi) -> Refactor (paranda koodi struktuuri).",
        }),
        _shuffle_options({
            "level": 6,
            "question": "Mida mõõdab testide koodikatte (code coverage) protsent?",
            "options": [
                "Kui suur osa lähtekoodist käivitatakse testide käigus",
                "Kui palju teste on koodi kohta kirjutatud",
                "Kui kiiresti testid jooksevad",
                "Kui palju vigu testid leiavad",
            ],
            "correctIndex": 0,
            "explanation": "Koodikatteprotsent näitab, kui suur osa koodiridadest/testitavatest harudest testidega kaetud on.",
        }),
        _shuffle_options({
            "level": 7,
            "question": "Mis on integratsoonitestide (integration tests) eesmärk?",
            "options": [
                "Kontrollida, kas erinevad süsteemi osad töötavad koos õigesti",
                "Testida ainult ühte funktsiooni",
                "Testida kasutajaliidese disaini",
                "Kontrollida koodi stiili",
            ],
            "correctIndex": 0,
            "explanation": "Integratsioonitestid kontrollivad, kas erinevad moodulid, teenused või komponendid koos töötades annavad õige tulemuse.",
        }),
        _shuffle_options({
            "level": 8,
            "question": "Mida teeb assertEqual(a, b) unittestis?",
            "options": [
                "Kontrollib, kas a ja b on võrdsed; kui ei ole, siis test ebaõnnestub",
                "Omistab muutujale a väärtuse b",
                "Kontrollib, kas a ja b on erinevad",
                "Loob uue testi",
            ],
            "correctIndex": 0,
            "explanation": "assertEqual kontrollib, et a == b. Kui võrdus ei kehti, visatakse AssertionError ja test loetakse ebaõnnestunuks.",
        }),
        _shuffle_options({
            "level": 9,
            "question": "Millist käsku kasutatakse pytest-is testide käivitamiseks?",
            "options": [
                "pytest",
                "python test",
                "run test",
                "pytest-run",
            ],
            "correctIndex": 0,
            "explanation": "pytest on nii teegi nimi kui ka CLI käsk testide käivitamiseks.",
        }),
        _shuffle_options({
            "level": 10,
            "question": "Milleks kasutatakse setUp() meetodit unittestis?",
            "options": [
                "Ettevalmistavate toimingute tegemiseks enne iga testi käivitamist",
                "Testide tulemuste kokkuvõtte tegemiseks",
                "Testitava koodi seadistamiseks tootmiskeskkonnas",
                "Testide automaatseks käivitamiseks",
            ],
            "correctIndex": 0,
            "explanation": "setUp() käivitatakse enne iga testimeetodit ja seda kasutatakse testide jaoks vajaliku keskkonna ettevalmistamiseks.",
        }),
        _shuffle_options({
            "level": 11,
            "question": "Mida tähendab testide puhul 'false positive'?",
            "options": [
                "Test näitab viga, aga tegelikult on kood korrektne",
                "Test läbitakse, aga kood on vigane",
                "Testi tulemus on tundmatu",
                "Testi ei käivitata üldse",
            ],
            "correctIndex": 0,
            "explanation": "False positive (valepositiivne) tähendab, et test ebaõnnestub (näitab viga), kuigi testitav kood on tegelikult korrektne.",
        }),
        _shuffle_options({
            "level": 12,
            "question": "Miks on oluline testide puhul kasutada fixture-id?",
            "options": [
                "Et luua testide jaoks korduvkasutatav ja ühtne algseisund",
                "Et testid ilusamad välja näeks",
                "Et vähendada testide arvu",
                "Et testid kiiremini jookseks",
            ],
            "correctIndex": 0,
            "explanation": "Fixture-d võimaldavad defineerida testide jaoks vajaliku keskkonna ja andmed ühes kohas ning neid korduvalt kasutada.",
        }),
        _shuffle_options({
            "level": 13,
            "question": "Mida testib regressioonitest (regression test)?",
            "options": [
                "Kas uued muudatused rikuvad olemasolevat funktsionaalsust",
                "Kas koodi jõudlus on piisav",
                "Kas kasutajaliides on ilus",
                "Kas andmebaas on optimeeritud",
            ],
            "correctIndex": 0,
            "explanation": "Regressioonitestid veenduvad, et uued koodimuudatused ei tekitanud vigu juba töötavates osades.",
        }),
        _shuffle_options({
            "level": 14,
            "question": "Mille poolest erineb pytest standardsest unittest moodulist?",
            "options": [
                "pytest toetab lihtsamat süntaksit (assert ilma erimeetoditeta) ja paremat vearaportit",
                "pytest ei toeta testide paralleelset käivitamist",
                "pytest nõuab klasside kasutamist",
                "pytest on aeglasem kui unittest",
            ],
            "correctIndex": 0,
            "explanation": "Pytest võimaldab kasutada tavalist Pythoni assert lauset ning annab paluge informatiivsemaid veateateid kui unittest.",
        }),
        _shuffle_options({
            "level": 15,
            "question": "Milline on hea testi omadus?",
            "options": [
                "Test trükib konsooli palju väljundeid, mida tuleb käsitsi kontrollida",
                "Test on isoleeritud, korratav, kiire ja kontrollib ühte kindlat käitumist",
                "Test sõltub teistest testidest ja nende tulemustest",
                "Test kasutab päris andmebaasi ja võrguühendust",
                
            ],
            "correctIndex": 1,
            "explanation": "Hea test on isoleeritud (ei sõltu teistest testidest), korratav (sama tulemus alati), kiire ja testib ühte kindlat omadust.",
        }),
    ]
    return questions


def generate_questions(assignment_data, api_key=None):
    if OPENAI_AVAILABLE and (api_key or os.environ.get("OPENAI_API_KEY")):
        questions = generate_questions_with_ai(assignment_data, api_key)
        if questions and len(questions) == 15:
            return questions

    return generate_simulated_questions(assignment_data)
