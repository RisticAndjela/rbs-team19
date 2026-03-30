**Zadatak: Dizajnirati mehanizam enkripcije sa ciljem da se zaštiti poverljivost (confidentiality) korisničkih lozinki, ali tako da je lozinku moguće po potrebi pročitati.**

**- Istražiti različite algoritme za generisanje ključa za enkripciju/dekripciju na osnovu glavne (master) lozinke i odabrati najbezbedniji. Primer: PBKDF;**

PBKDF - password-based key derivation function:
    koristi lozinku + salt (random dodatak lozinki) + veliki broj iteracija hash funkcije
    otporan na brute-force napade jer usporava napadaca

scrypt:
    otporniji na GPU/ASIC napade
    sporiji i bezbedniji od PBKDF

Argon2:
    koristi memoriju i paralelizaciju
    najbezbedniji je od svih algoritama

**- Istražiti različite simetrične algoritme za enkripciju/dekripciju i odabrati najbezbedniji;**

Simetricni algoritmi koriste isti kljuc za enkripciju i dekripciju.

AES - advanced encryption standard (AES-256):
    podatak se deli u blokove, prolazi kroz transformacije (zamena bajtova, permutacija, dodavanje kljuca...), a dekripcija je isti proces unazad.

**- Ispitati konfiguracione parametre odabranih algoritama, i otkriti koje bi to bile preporučene praksa za konfiguraciju;**

preporuke za PBKDF2:
    hash: SHA-256
    salt: minimum 16 bajtova
    iteracije: 100k-600k
    duzina kljuca: 256-bit

preporuke za Argon2:
    memory cost: 64-256MB
    time cost: 2-4
    parallelism: 1-4
    salt: min 16 bajtova
    duzina kljuca: 256-bit

za AES:
    kljuc: 256-bit (AES-256)
    IV (initialization vector): nasumican, jedinstven
    rezim: GCM (autentifikovana enkripcija) - enkriptuje + proverava da li je podatak izmenjen, ima auth tag

**- Odabrati pouzdane provajdere;**

pouzdani provajderi: OpenSSL, BouncyCastle (java), JCA...

**- Istražiti da li poslednje verzije za implementaciju imaju ozbiljnijih ranjivosti;**

Heartbleed (OpenSSL) - omogucavao citanje memorije servera, mogao da otkrije kljuceve i lozinke
potencijalni problemi: slab broj iteracija, reuse IV-a, zastarele biblioteke, neprovereni algoritmi

**- Specificirati zahteve za bezbednu implementaciju mehanizama za kreiranje ključa i enkripciju koristeći sve do sada nabrojano.**

Enkripcija:
korisnik unosi master lozinku
generise se salt (jedinstven za svakog korisnika)
iz master lozinke se generise kljuc (Argon2/PBKDF2)
generise se initialization vector (IV)
lozinka se enkriptuje (AES-256-GCM)
cuvaju se: ciphertext, salt, IV

Dekripcija:
korisnik ponovo unosi master lozinku
iz salta se generise isti kljuc
koristi se IV za dekripciju
dobija se originalna lozinka

dodatno:
koristiti proverene biblioteke
redovno azurirati verzije i proveravati ranjivosti
koristiti dovoljno jake parametre (iteracije, memorija)
obezbediti integritet podataka (GCM ili dodatni MAC)
