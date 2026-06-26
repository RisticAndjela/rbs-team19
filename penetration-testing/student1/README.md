# Dodatni zadatak - demonstracija CVE-2007-4559

U okviru dodatnog zadatka pripremljena je bezbedna lokalna demonstracija ranjivosti `CVE-2007-4559`, poznate i kroz problem nebezbedne upotrebe Python `tarfile` modula.

Primer je smesten u fajlu `slippy_demo.py` i ne napada stvaran sistem. Sve se izvrsava unutar foldera `sandbox` koji se automatski pravi u okviru ovog studentskog direktorijuma.

## Sta pokazuje skripta

Skripta simulira dve situacije:

1. `vulnerable_extract(...)`
   koristi `tarfile.extractall(...)` bez provere putanja iz arhive

2. `safe_extract(...)`
   proverava da li svaki fajl ostaje unutar ciljnog direktorijuma pre raspakivanja

U arhivi se namerno nalazi unos `../outside/owned.txt`, sto predstavlja klasicni `path traversal` scenario.

Ako aplikacija bez provere raspakuje takvu arhivu, fajl moze da zavrsi van predvidjenog foldera.

## Pokretanje

Iz ovog direktorijuma pokrenuti:

```powershell
python .\slippy_demo.py
```

## Ocekivani rezultat

Kod nebezbedne ekstrakcije vidi se da je fajl napravljen u:

```text
sandbox/outside/owned.txt
```

To znaci da je unos iz arhive uspeo da "izadje" iz ciljnog foldera za raspakivanje.

Kod bezbedne ekstrakcije skripta prijavljuje gresku i blokira takav unos pre raspakivanja.

## Zasto je ovo bitno

Ova ranjivost je opasna zato sto zlonamerna `.tar` arhiva moze da:

- prepise postojece fajlove
- ubaci nove fajlove na neocekivane lokacije
- dovede do daljeg kompromitovanja aplikacije ako se raspakuju konfiguracije, skripte ili kljucevi

Najvaznija mera zastite je validacija svake putanje iz arhive pre ekstrakcije.

## Sta sam uradila

Uradila sam lokalni proof-of-concept za `CVE-2007-4559` u Python-u.
Napravila sam arhivu sa namerno zlonamernom putanjom `../outside/owned.txt` kako bih pokazala kako dolazi do `path traversal` problema.
Zatim sam implementirala i nebezbednu i bezbednu verziju ekstrakcije da se jasno vidi razlika izmedju ranjivog i zasticenog pristupa.
Sve sam ogranicila na lokalni `sandbox` direktorijum, tako da demonstracija ostane edukativna i bezbedna.
