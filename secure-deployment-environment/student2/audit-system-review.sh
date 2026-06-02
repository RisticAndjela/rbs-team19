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
