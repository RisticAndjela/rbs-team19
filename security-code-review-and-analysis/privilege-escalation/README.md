# Privilege Escalation i Stored XSS

Ovaj direktorijum sadrži eksploataciju privilege escalation ranjivosti u aplikaciji TUDO zasnovanu na Stored XSS-u u opisu korisnika.

## Opis ranjivosti

- Stored XSS ranjivost u polju `description` korisnika.
- Kada se opis korisnika prikaže na admin dashboard-u, JavaScript koji je unet od strane napadača može da se izvrši u kontekstu admin browser-a.
- Napadač može da ukrade admin kolačić (`PHPSESSID`) i time preuzme admin sesiju.

## Kako radi napad

1. Napadač se prijavi kao običan korisnik (`user1`).
2. Unese zlonamerni XSS payload u svoje polje `description`.
3. Admin se kasnije loguje i posećuje dashboard na kojem su svi opisi vidljivi.
4. XSS payload se izvršava u browser-u admina i šalje njegov `PHPSESSID` kolačić na napadačev server.
5. Napadač koristi ukradeni kolačić da se prijavi kao admin bez lozinke.

## Skripta `xss.py`

- Skripta automatski:
  - loguje se kao zadati korisnik,
  - postavlja XSS payload u `description`,
  - simulira admin login,
  - posećuje admin stranicu da bi payload bio okinut,
  - čeka da se ukradeni cookie pojavi iz zahteva.

### Pokretanje

```bash
python privilege-escalation/xss.py http://localhost:8000 user1 user1
```
(gde je drugi argument username korisnika, a treći argument lozinka korisnika)

Ili preko glavne skripte `script.py`:

```bash
python script.py priv-esc user1 user1
```

(python script.py priv-esc user1 user1 - gde je prvi argument username korisnika, a drugi argument lozinka korisnika)

## Šta se dobija

- Ako je napad uspešan, izlaz će sadržati admin cookie u formatu:
  - `PHPSESSID=<session_id>`
- Skripta zatim koristi ovaj kolačić da verifikuje admin pristup.

## Generalno o privilege escalation

- Privilege escalation je situacija kada napadač stekne veći nivo privilegija nego što bi trebalo da ima.
- U ovoj aplikaciji, admin privilegije se mogu dobiti bez validnog admin naloga kroz:
  - XSS u `description` polju,
  - slabosti u prikazu admin dashboard-a,
  - krađu sesijskih kolačića.

## Preporuke za ispravku

- Sanitizovati i enkodovati sve korisničke unose pre prikaza u admin delu.
- Koristiti `Content Security Policy (CSP)` i `HttpOnly`/`Secure` za kolačiće.
- Ograničiti prikaz korisničkih opisa u admin dashboard-u i izbegavati nefiltrirani HTML.
- Implementirati validaciju i autorizaciju pre nego što dozvoliš prikaz sadržaja adminu.


