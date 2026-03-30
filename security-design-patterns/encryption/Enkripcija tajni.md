## Zadatak: Dizajnirati mehanizam enkripcije sa ciljem da se zaštiti poverljivost (**confidentiality**) korisničkih lozinki, ali tako da je lozinku moguće po potrebi pročitati.

## Algoritmi za generisanje ključa

Istražiti različite algoritme za generisanje ključa za enkripciju/dekripciju na osnovu glavne (master) lozinke i odabrati najbezbedniji.

### PBKDF (Password-Based Key Derivation Function)
- koristi lozinku + salt (random dodatak lozinki) + veliki broj iteracija hash funkcije  
- otporan na brute-force napade jer usporava napadača  

### scrypt
- otporniji na GPU/ASIC napade  
- sporiji i bezbedniji od PBKDF  

### Argon2
- koristi memoriju i paralelizaciju  
- najbezbedniji je od svih algoritama  

---

## Simetrični algoritmi za enkripciju/dekripciju

Simetrični algoritmi koriste isti ključ za enkripciju i dekripciju.

### AES (Advanced Encryption Standard - AES-256)
- podatak se deli u blokove  
- prolazi kroz transformacije:
  - zamena bajtova  
  - permutacija  
  - dodavanje ključa  
- dekripcija je isti proces unazad  

---

## Konfiguracioni parametri

### PBKDF2
- hash: SHA-256  
- salt: minimum 16 bajtova  
- iteracije: 100k-600k  
- dužina ključa: 256-bit  

### Argon2
- memory cost: 64-256MB  
- time cost: 2-4  
- parallelism: 1-4  
- salt: minimum 16 bajtova  
- dužina ključa: 256-bit  

### AES
- ključ: 256-bit (AES-256)  
- IV (initialization vector): nasumičan, jedinstven  
- režim: GCM (autentifikovana enkripcija)  
  - enkriptuje + proverava da li je podatak izmenjen  
  - ima auth tag  

---

## Pouzdani provajderi

- OpenSSL  
- BouncyCastle (Java)  
- JCA  

---

## Ranjivosti

### Heartbleed (OpenSSL)
- omogućavao čitanje memorije servera  
- mogao da otkrije ključeve i lozinke  

### Potencijalni problemi
- slab broj iteracija  
- reuse IV-a  
- zastarele biblioteke  
- neprovereni algoritmi  

---

## Specifikacija mehanizma

### Enkripcija
- korisnik unosi master lozinku  
- generiše se salt (jedinstven za svakog korisnika)  
- iz master lozinke se generiše ključ (Argon2/PBKDF2)  
- generiše se initialization vector (IV)  
- lozinka se enkriptuje (AES-256-GCM)  
- čuvaju se: ciphertext, salt, IV  

---

### Dekripcija
- korisnik ponovo unosi master lozinku  
- iz salta se generiše isti ključ  
- koristi se IV za dekripciju  
- dobija se originalna lozinka  

---

## Dodatno
- koristiti proverene biblioteke  
- redovno ažurirati verzije i proveravati ranjivosti  
- koristiti dovoljno jake parametre (iteracije, memorija)  
- obezbediti integritet podataka (GCM ili dodatni MAC)  
---
