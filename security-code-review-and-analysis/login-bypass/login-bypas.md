Problem je **blind SQL injection u `forgotusername.php`**. Korisnicki unos (`username`) se direktno ubacuje u SQL upit bez parametrizacije, sto omogucava ubacivanje malicioznih SQL uslova. Aplikacija vraca razlicite odgovore (“User exists” i “User doesnt exist”), sto formira tzv. boolean oracle i omogucava napadacu da postepeno izvlaci podatke iz baze (UID i reset token) bit po bit. Eksploatacija se odvija tako sto se prvo pokrece zahtev za reset lozinke, zatim se kroz SQL injection izvlace podaci iz baze, nakon cega se dobijeni token koristi za postavljanje nove lozinke i pristup nalogu.

Kao validacija, razvijena je PoC skripta za ovaj problem. Skripta demonstrira da je napad prakticno izvodljiv i da se moze automatizovati za izvlacenje reset tokena i preuzimanje naloga.

Pokretanje PoC-a:

```bash id="k2m9qp"
python blind_sqli_reset.py http://localhost:8000 user1 Hacked123!
```

Nakon uspesnog izvrsavanja, moguce je prijaviti se kroz `http://localhost:8000/login.php` sa:

* username: `user1` ili `user2`
* password: lozinka postavljena kroz exploit

Analiza je zapoceta fokusiranjem na delove aplikacije koji obradjuju autentifikaciju i password recovery, jer predstavljaju najcesce attack surface tacke. Koriscenjem staticke CLI pretrage koda identifikovane su funkcije koje direktno komuniciraju sa bazom podataka. Daljom analizom uoceno je da se korisnicki unos koristi u SQL upitu bez parametrizacije, sto je ukazivalo na potencijalnu SQL injection ranjivost, kasnije potvrdjenu manuelnom analizom i eksploatacijom.
