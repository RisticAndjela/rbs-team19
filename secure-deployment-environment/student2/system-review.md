# System Review

U okviru svog dela projekta implementirana je Bash skripta za pregled osnovne bezbednosne konfiguracije Linux sistema.

Implementirane su sledeće provere:

---

# Source code

```bash
#!/bin/bash

echo "=================================="
echo "SYSTEM REVIEW AUDIT"
echo "=================================="

echo
echo "[1] Operating system information..."
if [ -f /etc/os-release ]; then
    cat /etc/os-release
elif command -v lsb_release >/dev/null 2>&1; then
    lsb_release -a 2>/dev/null
else
    uname -a
fi

echo
echo "=================================="

echo
echo "[2] Kernel version and uptime..."
uname -r
uname -m
uptime

echo
echo "=================================="

echo
echo "[3] Time configuration and synchronization..."
if command -v timedatectl >/dev/null 2>&1; then
    timedatectl
else
    date
    cat /etc/timezone 2>/dev/null
fi

systemctl is-active systemd-timesyncd 2>/dev/null
systemctl is-active ntp 2>/dev/null
systemctl is-active chronyd 2>/dev/null

echo
echo "=================================="

echo
echo "[4] Installed packages overview..."
if command -v dpkg >/dev/null 2>&1; then
    dpkg -l | awk '$1=="ii" {print $2, $3}' | head -n 30
elif command -v rpm >/dev/null 2>&1; then
    rpm -qa | head -n 30
fi

echo
echo "=================================="

echo
echo "[5] Logging service and configuration..."
ps -ef | grep -E "rsyslogd|syslog-ng|journald" | grep -v grep
if [ -f /etc/rsyslog.conf ]; then
    grep -Ev '^[[:space:]]*#|^[[:space:]]*$' /etc/rsyslog.conf 2>/dev/null | head -n 40
fi

echo
echo "=================================="

echo
echo "Audit finished."
```

---

# 1. Provera informacija o operativnom sistemu

Korišćene komande:

```bash
cat /etc/os-release
lsb_release -a
uname -a
```

Ova provera služi za identifikaciju distribucije i verzije sistema.

To je važno zato što:
- omogućava da se proveri da li je sistem zastareo
- pomaže pri proveri da li distribucija i dalje dobija bezbednosne ispravke
- olakšava dalje mapiranje poznatih ranjivosti na tačnu platformu

Primer rezultata:

```text
PRETTY_NAME="Ubuntu 22.04.4 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
```

---

# 2. Provera verzije kernela i uptime-a

Korišćene komande:

```bash
uname -r
uname -m
uptime
```

Ovom proverom se dobija verzija kernela, arhitektura sistema i informacija koliko dugo sistem radi bez restarta.

Ovo pomaže da se uoči:
- da li se koristi star kernel
- da li sistem dugo nije restartovan nakon ažuriranja
- da li možda nisu primenjene novije kernel zakrpe

Primer rezultata:

```text
5.15.0-107-generic
x86_64
10:52:11 up 34 days,  2:41,  2 users,  load average: 0.08, 0.11, 0.09
```

---

# 3. Provera vremena i sinhronizacije

Korišćene komande:

```bash
timedatectl
date
cat /etc/timezone
systemctl is-active systemd-timesyncd
systemctl is-active ntp
systemctl is-active chronyd
```

Ova provera služi za proveru vremenske zone i da li je sistem pravilno sinhronizovan sa izvorom vremena.

To je bitno zato što:
- netačno vreme otežava analizu logova
- može praviti problem pri validaciji sertifikata
- može narušiti rad autentikacionih i audit mehanizama

Primer rezultata:

```text
Time zone: Europe/Belgrade (CEST, +0200)
System clock synchronized: yes
NTP service: active
```

---

# 4. Pregled instaliranih paketa

Korišćene komande:

```bash
dpkg -l | awk '$1=="ii" {print $2, $3}' | head -n 30
rpm -qa | head -n 30
```

Ova provera daje pregled instaliranog softvera na sistemu.

Cilj je da se uoči:
- da li je instalirano više paketa nego što je potrebno
- da li postoje nepotrebni servisi ili alati
- da li sistem sadrži dodatni softver koji povećava napadnu površinu

Primer rezultata:

```text
apache2 2.4.52
openssh-server 1:8.9p1
rsyslog 8.2112.0
```

---

# 5. Provera logovanja i log servisa

Korišćene komande:

```bash
ps -ef | grep -E "rsyslogd|syslog-ng|journald" | grep -v grep
grep -Ev '^[[:space:]]*#|^[[:space:]]*$' /etc/rsyslog.conf | head -n 40
```

Ovom proverom se utvrđuje da li je servis za logovanje aktivan i kako izgleda osnovna konfiguracija logovanja.

To je važno zato što:
- bez logova je teže otkriti incidente
- loša konfiguracija može značiti da se važni događaji ne beleže
- centralizovano i uredno logovanje je važan deo hardening procesa

Primer rezultata:

```text
root      742     1  0 09:10 ?        00:00:00 /usr/sbin/rsyslogd -n
$FileOwner root
$FileGroup adm
$FileCreateMode 0640
```

---

# Pokretanje skripte

Skripta se pokreće komandom:

```bash
chmod +x audit-system-review.sh
./audit-system-review.sh
```
