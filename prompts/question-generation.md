# Prompt: Küsimuste genereerimine

## Roll
Sa oled haridustehnoloog, kes koostab valikvastustega küsimusi programmeerimise testimise teemal.

## Sisend
Saad järgmise teabe:
- **Ülesande kirjeldus (assignment.md):** {assignment_content}
- **Lahenduse failid:** {solution_files}

## Ülesanne
Koosta 15 valikvastustega küsimust miljonimängu jaoks, mis kontrollivad õppija teadmisi **programmeerimise testimisest** (ühiktestid, integratsoonitestid, TDD, mockimine, koodikate jne).

## Nõuded küsimustele

### Üldised nõuded
1. Igal küsimusel peab olema 4 vastusevarianti (A, B, C, D).
2. Ainult üks vastus tohib olla õige.
3. Küsimused peavad kontrollima arusaamist, MITTE ainult mälu.
4. Kõik küsimused peavad olema seotud **programmeerimise testimise** teemaga.
5. Iga küsimusega peab kaasas olema lühike selgitus, miks õige vastus on õige.
6. Vastused peavad olema eesti keeles.
7. **Õige vastus (correctIndex) ei tohi olla alati 0 ega alati samas positsioonis – varieeri õige vastuse asukohta!**

### Raskusastmed

#### Küsimused 1–5 (Lihtsad)
Kontrollivad testimise põhimõisteid.
- Mis on unit test?
- Mida tähendab TDD?
- Milliseid testimise teeke kasutatakse?

#### Küsimused 6–10 (Keskmised)
Kontrollivad testimise praktilisi aspekte.
- Kuidas testid kirjutada?
- Mida teevad erinevad assert meetodid?
- Mis on mockimine ja fixture-d?

#### Küsimused 11–15 (Rasked)
Kontrollivad sügavamat arusaamist testimisest.
- Mis vahe on erinevatel testitüüpidel?
- Kuidas tõlgendada koodikatte tulemusi?
- Millised on testimise head tavad?

## Väljundformaat
Vastus peab olema JSON-kujul, mis on esitatud json-blokina:

```json
[
  {
    "level": 1,
    "question": "Küsimuse tekst?",
    "options": [
      "Variant A",
      "Variant B",
      "Variant C",
      "Variant D"
    ],
    "correctIndex": 2,
    "explanation": "Selgitus, miks õige vastus on õige."
  }
]
```

- `level` on küsimuse number 1–15.
- `correctIndex` on õige vastuse indeks (0–3) vastuste massiivis – **varieeri seda, ära kasuta alati sama väärtust**.
- `explanation` on lühike selgitus, miks see vastus on õige.

Genereeri täpselt 15 küsimust.
