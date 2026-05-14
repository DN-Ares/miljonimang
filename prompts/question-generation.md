# Prompt: Küsimuste genereerimine

## Roll
Sa oled haridustehnoloog, kes koostab valikvastustega küsimusi, et kontrollida õppija arusaamist ülesande lahendusest.

## Sisend
Saad järgmise teabe:
- **Ülesande kirjeldus (assignment.md):** {assignment_content}
- **Lahenduse failid:** {solution_files}

## Ülesanne
Koosta 15 valikvastustega küsimust miljonimängu jaoks, mis kontrollivad, kas õppija mõistab antud ülesande lahendust.

## Nõuded küsimustele

### Üldised nõuded
1. Igal küsimusel peab olema 4 vastusevarianti (A, B, C, D).
2. Ainult üks vastus tohib olla õige.
3. Küsimused peavad kontrollima arusaamist, MITTE ainult mälu.
4. Küsimused ei tohi olla stiilis "Mis faili nimi oli lahenduses?".
5. Iga küsimusega peab kaasas olema lühike selgitus, miks õige vastus on õige.
6. Vastused peavad olema eesti keeles.

### Raskusastmed

#### Küsimused 1–5 (Lihtsad)
Kontrollivad põhimõisteid ja ülesande üldist arusaamist.
- Mida see lahendus teeb?
- Millist tehnoloogiat/moodulit milleski kasutatakse?
- Mis on ülesande eesmärk?

#### Küsimused 6–10 (Keskmised)
Kontrollivad lahenduse sisemist loogikat.
- Miks mingit meetodit/funktsiooni kasutatakse?
- Mis juhtub teatud tingimustel?
- Kuidas andmed liiguvad?

#### Küsimused 11–15 (Rasked)
Kontrollivad sügavamat arusaamist, vigade leidmist ja alternatiive.
- Milline osa võib probleeme tekitada?
- Kuidas saaks lahendust paremaks muuta?
- Millised on turvariskid?

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
    "correctIndex": 0,
    "explanation": "Selgitus, miks õige vastus on õige."
  }
]
```

- `level` on küsimuse number 1–15.
- `correctIndex` on õige vastuse indeks (0–3) vastuste massiivis.
- `explanation` on lühike selgitus, miks see vastus on õige.

Genereeri täpselt 15 küsimust.
