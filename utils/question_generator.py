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
                {"role": "system", "content": "Sa oled haridustehnoloog, kes koostab valikvastustega küsimusi."},
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


def generate_simulated_questions(assignment_data):
    title = assignment_data["id"]
    content = assignment_data["content"]
    files = list(assignment_data["solution_files"].keys())

    has_html = any(f.endswith(".html") for f in files)
    has_css = any(f.endswith(".css") for f in files)
    has_js = any(f.endswith(".js") for f in files)
    has_py = any(f.endswith(".py") for f in files)
    has_json_file = any(f.endswith(".json") for f in files)

    questions = [
        {
            "level": 1,
            "question": f"Mis on ülesande {title} põhieesmärk?",
            "options": [
                f"Lahendada ülesanne {title} vastavalt assignment.md nõuetele",
                "Luua uus programmeerimiskeel",
                "Testida andmebaasi ühendust",
                "Kirjutada dokumentatsioon",
            ],
            "correctIndex": 0,
            "explanation": f"Ülesande {title} eesmärk on täita assignment.md failis toodud nõudeid.",
        },
        {
            "level": 2,
            "question": "Milliseid faile kasutatakse selles lahenduses?",
            "options": [
                ", ".join(files[:3]) if files else "Puuduvad failid",
                "ainult .exe failid",
                "mingid pildifailid",
                "puuduvad failid, lahendus on ainult mälus",
            ],
            "correctIndex": 0,
            "explanation": "Lahendus koosneb failidest: " + ", ".join(files),
        },
        {
            "level": 3,
            "question": "Millist programmeerimiskeelt selle ülesande lahendus peamiselt kasutab?",
            "options": [
                "Python" if has_py else "JavaScript",
                "C++",
                "Java",
                "Ruby",
            ],
            "correctIndex": 0,
            "explanation": "Lahendus kasutab " + ("Pythonit" if has_py else "JavaScripti") + " põhiloogika jaoks.",
        },
        {
            "level": 4,
            "question": "Miks on oluline lugeda assignment.md faili enne lahendamist?",
            "options": [
                "Et mõista ülesande nõudeid ja hindamiskriteeriume",
                "Sest ilma selleta ei tööta kood",
                "See on ainult ilu pärast",
                "Et teada saada, millist värvi nuppe kasutada",
            ],
            "correctIndex": 0,
            "explanation": "assignment.md sisaldab ülesande püstitust, nõudeid ja hindamiskriteeriume.",
        },
        {
            "level": 5,
            "question": "Kuidas on lahenduse failid omavahel seotud?",
            "options": [
                "HTML viitab CSS-ile ja JavaScriptile, mis töötlevad kasutaja sisendit",
                "Failid ei ole üksteisega seotud",
                "Kõik failid on koopiaid üksteisest",
                "CSS fail käivitab JavaScripti",
            ],
            "correctIndex": 0,
            "explanation": "Tüüpiliselt HTML laeb CSS-i stiilideks ja JavaScripti funktsionaalsuseks.",
        },
        {
            "level": 6,
            "question": "Miks tuleb kasutaja sisend enne töötlemist valideerida?",
            "options": [
                "Et vältida vigaseid andmeid ja turvariske",
                "Sest muidu läheb andmebaas katki",
                "See pole vajalik, kui kasutaja on usaldusväärne",
                "Et programm ilusti välja näeks",
            ],
            "correctIndex": 0,
            "explanation": "Sisendi valideerimine hoiab ära vead ja turvaprobleemid nagu XSS.",
        },
        {
            "level": 7,
            "question": "Mis juhtub, kui üks vajalikest failidest puudub?",
            "options": [
                "Rakendus võib töötada osaliselt või mitte üldse",
                "Rakendus töötab alati, sõltumata failidest",
                "See ei oma tähtsust, sest failid laaditakse serverist",
                "Tekib automaatselt uus fail",
            ],
            "correctIndex": 0,
            "explanation": "Puuduv fail võib põhjustada veateateid või funktsionaalsuse puudumist.",
        },
        {
            "level": 8,
            "question": "Kuidas toimub andmevahetus erinevate lahenduse osade vahel?",
            "options": [
                "Funktsioonid kutsuvad üksteist välja ja edastavad parameetreid",
                "Andmeid hoitakse paberkandjal",
                "Andmeid saadetakse e-mailiga",
                "Andmevahetust ei toimu, iga osa töötab iseseisvalt",
            ],
            "correctIndex": 0,
            "explanation": "Funktsioonid ja moodulid vahetavad andmeid parameetrite ja tagastusväärtuste kaudu.",
        },
        {
            "level": 9,
            "question": "Millist sündmuste töötlemise meetodit lahenduses kasutatakse?",
            "options": [
                "addEventListener või sarnast sündmuste kuulamise mehhanismi",
                "Tsükli abil pidevat kontrolli",
                "Funktsiooni setTimeout",
                "Sündmusi ei töödelda üldse",
            ],
            "correctIndex": 0,
            "explanation": "addEventListener võimaldab reageerida kasutaja tegevustele (klikk, submit jne).",
        },
        {
            "level": 10,
            "question": "Kuidas lahendus käsitleb erijuhtumeid (näiteks tühja sisendit)?",
            "options": [
                "Kontrollitakse tingimuslausega ja kuvatakse veateade",
                "Erijuhtumeid ignoreeritakse",
                "Programm lõpetab töö veateatega",
                "Kasutajalt küsitakse uuesti ilma kontrollita",
            ],
            "correctIndex": 0,
            "explanation": "Korralik lahendus kontrollib sisendit ja teavitab kasutajat vigadest.",
        },
        {
            "level": 11,
            "question": "Milline turvarisk võib kaasneda innerHTML kasutamisega?",
            "options": [
                "XSS (Cross-Site Scripting) rünnak",
                "Andmebaasi kustutamine",
                "Serveri ülekoormus",
                "Paroolide lekkimine",
            ],
            "correctIndex": 0,
            "explanation": "innerHTML võimaldab pahatahtliku koodi sisestamist lehele (XSS).",
        },
        {
            "level": 12,
            "question": "Kuidas saaks seda lahendust skaleeritavamaks muuta?",
            "options": [
                "Eraldada loogika väiksemateks funktsioonideks ja mooduliteks",
                "Lisada rohkem CSS-animatsioone",
                "Kasutada rohkem globaalseid muutujaid",
                "Kirjutada kogu kood ühte faili",
            ],
            "correctIndex": 0,
            "explanation": "Modulaarne struktuur võimaldab lahendust hõlpsamini laiendada ja hooldada.",
        },
        {
            "level": 13,
            "question": "Milline lahenduse osa vajaks täiendamist, kui andmeid tuleks juurde palju?",
            "options": [
                "Andmete töötlemise ja kuvamise loogika vajaks optimeerimist",
                "CSS-faili tuleks suurendada",
                "HTML-faili tuleks lisada rohkem div-elemente",
                "Midagi ei muutuks, sest kood töötab alati ühtemoodi",
            ],
            "correctIndex": 0,
            "explanation": "Suure hulga andmete korral võib optimeerimata kood olla aeglane või mittetöötav.",
        },
        {
            "level": 14,
            "question": "Kuidas parandada lahenduse struktuuri, et seda oleks lihtsam testida?",
            "options": [
                "Eraldada loogika väikesteks unittestidega testitavateks funktsioonideks",
                "Lisada rohkem HTML-lehti",
                "Eemaldada kõik funktsioonid",
                "Kirjutada kood ühe reana",
            ],
            "correctIndex": 0,
            "explanation": "Väikesed üksikfunktsioonid on kergesti testitavad ühiktestidega.",
        },
        {
            "level": 15,
            "question": "Kuidas tagada, et lahendus järgib häid tavasid ja on edasiarendatav?",
            "options": [
                "Kasutada puhta koodi põhimõtteid, versioonihaldust ja dokumentatsiooni",
                "Kirjutada kogu loogika ühte suurde funktsiooni",
                "Ignoreerida veahaldust",
                "Kasutada ainult ühte muutujat kogu programmis",
            ],
            "correctIndex": 0,
            "explanation": "Hea kood on loetav, testitav ja dokumenteeritud, mis võimaldab lihtsat edasiarendust.",
        },
    ]
    return questions


def generate_questions(assignment_data, api_key=None):
    if OPENAI_AVAILABLE and (api_key or os.environ.get("OPENAI_API_KEY")):
        questions = generate_questions_with_ai(assignment_data, api_key)
        if questions and len(questions) == 15:
            return questions

    return generate_simulated_questions(assignment_data)
