#!/bin/bash
# Setup-Script für Ansible CheckMK-Agent-Installation mit VMware vCenter

set -e

echo "=== Ansible CheckMK Agent Installation - Setup ==="
echo ""

# Betriebssystem erkennen
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ Kann Betriebssystem nicht erkennen!"
    exit 1
fi

# Prüfen ob Ansible installiert ist
if ! command -v ansible &> /dev/null; then
    echo "❌ Ansible ist nicht installiert!"
    case $OS in
        debian|ubuntu)
            echo "   Installation auf Debian/Ubuntu:"
            echo "   sudo apt-get update"
            echo "   sudo apt-get install -y ansible python3 python3-pip sshpass"
            ;;
        arch|manjaro)
            echo "   Installation auf Arch Linux:"
            echo "   sudo pacman -S ansible python python-pip sshpass"
            ;;
        *)
            echo "   Bitte installieren Sie Ansible für Ihr System"
            ;;
    esac
    exit 1
fi
echo "✓ Ansible ist installiert: $(ansible --version | head -n1)"

# Prüfen ob Python3 installiert ist
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 ist nicht installiert!"
    case $OS in
        debian|ubuntu)
            echo "   Installation auf Debian/Ubuntu: sudo apt-get install -y python3 python3-pip"
            ;;
        arch|manjaro)
            echo "   Installation auf Arch Linux: sudo pacman -S python python-pip"
            ;;
        *)
            echo "   Bitte installieren Sie Python3 für Ihr System"
            ;;
    esac
    exit 1
fi
echo "✓ Python3 ist installiert: $(python3 --version)"

# Prüfen ob pip installiert ist
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "⚠ pip3 ist nicht installiert!"
    case $OS in
        debian|ubuntu)
            echo "   Installation auf Debian/Ubuntu: sudo apt-get install -y python3-pip"
            ;;
        arch|manjaro)
            echo "   Installation auf Arch Linux: sudo pacman -S python-pip"
            ;;
        *)
            echo "   Bitte installieren Sie pip für Ihr System"
            ;;
    esac
else
    echo "✓ pip3 ist installiert"
fi

# Prüfen ob sshpass installiert ist (für Passwort-Authentifizierung)
echo ""
echo "=== Prüfe sshpass (für Passwort-Authentifizierung) ==="
if ! command -v sshpass &> /dev/null; then
    echo "⚠ sshpass ist nicht installiert!"
    echo "   sshpass ermöglicht Passwort-Authentifizierung ohne interaktive Eingabe."
    case $OS in
        debian|ubuntu)
            echo "   Installation auf Debian/Ubuntu: sudo apt-get install -y sshpass"
            ;;
        arch|manjaro)
            echo "   Installation auf Arch Linux: sudo pacman -S sshpass"
            ;;
        *)
            echo "   Bitte installieren Sie sshpass für Ihr System"
            ;;
    esac
    echo "   Sie können auch ohne sshpass arbeiten, müssen dann aber --ask-pass verwenden."
else
    echo "✓ sshpass ist installiert"
fi

# Ansible Collections installieren
echo ""
echo "=== Installiere Ansible Collections ==="
ansible-galaxy collection install -r requirements.yml

# PyVmomi installieren (benötigt für VMware)
echo ""
echo "=== Installiere Python-Abhängigkeiten ==="
if ! python3 -c "import pyvmomi" 2>/dev/null; then
    echo "Installiere pyvmomi..."

    case $OS in
        debian|ubuntu)
            # Versuche zuerst Debian-Pakete zu verwenden
            echo "Auf Debian/Ubuntu gibt es mehrere Möglichkeiten:"
            echo ""
            echo "Option 1 (EMPFOHLEN): System-Pakete verwenden"
            echo "   sudo apt-get install -y python3-pyvmomi python3-requests"
            echo ""
            echo "Option 2: pip3 mit --break-system-packages verwenden"
            echo "   pip3 install --user --break-system-packages pyvmomi requests"
            echo ""

            # Versuche automatisch System-Pakete zu installieren
            if command -v apt-cache &> /dev/null && apt-cache show python3-pyvmomi &> /dev/null 2>&1; then
                echo "Versuche automatische Installation mit apt..."
                if sudo apt-get install -y python3-pyvmomi python3-requests 2>/dev/null; then
                    echo "✓ pyvmomi über apt installiert"
                else
                    echo "⚠ Automatische Installation fehlgeschlagen."
                    echo "Bitte führen Sie manuell aus:"
                    echo "   sudo apt-get install -y python3-pyvmomi python3-requests"
                    echo "ODER:"
                    echo "   pip3 install --user --break-system-packages pyvmomi requests"
                    exit 1
                fi
            else
                echo "python3-pyvmomi nicht in apt verfügbar."
                echo "Verwende pip3 mit --break-system-packages..."
                if pip3 install --user --break-system-packages pyvmomi requests; then
                    echo "✓ pyvmomi über pip3 installiert"
                else
                    echo "❌ Installation fehlgeschlagen!"
                    exit 1
                fi
            fi
            ;;
        arch|manjaro)
            pip3 install --user pyvmomi requests
            ;;
        *)
            pip3 install --user pyvmomi requests
            ;;
    esac
else
    echo "✓ pyvmomi ist bereits installiert"
fi

# Requests prüfen
if ! python3 -c "import requests" 2>/dev/null; then
    echo "⚠ Python 'requests' Modul fehlt"
    case $OS in
        debian|ubuntu)
            echo "Installiere mit: sudo apt-get install -y python3-requests"
            echo "ODER: pip3 install --user --break-system-packages requests"
            ;;
    esac
fi

# Prüfen ob Credentials konfiguriert sind
echo ""
echo "=== Prüfe vCenter Credentials ==="
if [ ! -f "vcenter_credentials.sh" ]; then
    echo "❌ vcenter_credentials.sh nicht gefunden!"
    echo "   Bitte erstellen:"
    echo "   cp vcenter_credentials.sh.example vcenter_credentials.sh"
    echo "   Dann die Datei bearbeiten und Ihre Credentials eintragen."
    exit 1
fi
echo "✓ vcenter_credentials.sh gefunden"

# Credentials laden
source vcenter_credentials.sh

# Prüfen ob Credentials gesetzt sind
if [ -z "$VCENTER_USERNAME" ] || [ -z "$VCENTER_PASSWORD" ]; then
    echo "❌ VCENTER_USERNAME oder VCENTER_PASSWORD nicht gesetzt!"
    echo "   Bitte vcenter_credentials.sh bearbeiten."
    exit 1
fi
echo "✓ vCenter Credentials sind gesetzt"

# Prüfen ob AD-Credentials konfiguriert sind
echo ""
echo "=== Prüfe AD-Credentials (für SSH-Zugriff) ==="
if [ ! -f "ad_credentials.sh" ]; then
    echo "⚠ ad_credentials.sh nicht gefunden!"
    echo "   Bitte erstellen:"
    echo "   cp ad_credentials.sh.example ad_credentials.sh"
    echo "   chmod 600 ad_credentials.sh"
    echo "   Dann die Datei bearbeiten und Ihren AD-Benutzernamen eintragen."
    echo ""
    echo "   Sie können auch ohne diese Datei arbeiten und AD_USERNAME manuell setzen:"
    echo "   export AD_USERNAME='ihr-ad-username'"
else
    echo "✓ ad_credentials.sh gefunden"

    # AD Credentials laden
    source ad_credentials.sh

    # Prüfen ob AD_USERNAME gesetzt ist
    if [ -z "$AD_USERNAME" ]; then
        echo "⚠ AD_USERNAME nicht gesetzt in ad_credentials.sh"
        echo "   Bitte ad_credentials.sh bearbeiten und AD_USERNAME eintragen."
    else
        echo "✓ AD-Benutzername ist gesetzt: $AD_USERNAME"
    fi

    # Info über Passwörter
    if [ -z "$ANSIBLE_PASSWORD" ]; then
        echo "ℹ ANSIBLE_PASSWORD nicht gesetzt - Sie müssen --ask-pass verwenden"
    else
        echo "✓ SSH-Passwort ist gesetzt"
    fi

    if [ -z "$ANSIBLE_BECOME_PASSWORD" ]; then
        echo "ℹ ANSIBLE_BECOME_PASSWORD nicht gesetzt - Sie müssen --ask-become-pass verwenden"
    else
        echo "✓ sudo-Passwort ist gesetzt"
    fi
fi

# CheckMK Pakete prüfen
echo ""
echo "=== Prüfe CheckMK Pakete ==="
if [ ! -f "files/check-mk-agent-2.3.0p9-6cc5d32d5bd65f21.noarch.rpm" ]; then
    echo "⚠ RPM-Paket nicht gefunden in files/"
    echo "   Bitte kopieren: cp ~/Downloads/check-mk-agent-*.rpm files/"
fi

if [ ! -f "files/check-mk-agent_2.3.0p9-6cc5d32d5bd65f21_all.deb" ]; then
    echo "⚠ DEB-Paket nicht gefunden in files/"
    echo "   Bitte kopieren: cp ~/Downloads/check-mk-agent_*.deb files/"
fi

# Inventory testen
echo ""
echo "=== Teste VMware Inventory ==="
echo "Lade VMs aus vCenter LTERZTA001.dptrzm.de..."
echo ""

if ansible-inventory -i inventory/vmware.yml --list > /dev/null 2>&1; then
    echo "✓ VMware Inventory erfolgreich geladen"
    echo ""
    echo "Gefundene VMs (mit LTERZTA prefix):"
    ansible-inventory -i inventory/vmware.yml --graph
else
    echo "❌ Fehler beim Laden des VMware Inventory!"
    echo "   Bitte prüfen Sie:"
    echo "   - vCenter Hostname: LTERZTA001.dptrzm.de"
    echo "   - Username und Password"
    echo "   - Netzwerkverbindung zum vCenter"
    exit 1
fi

echo ""
echo "=== Setup abgeschlossen ==="
echo ""
echo "Nächste Schritte:"
echo ""
echo "1. Credentials laden:"
echo "   source vcenter_credentials.sh"
echo "   source ad_credentials.sh"
echo ""
echo "2. Verbindung testen:"
echo "   ansible checkmk_agents -m ping --ask-pass --ask-become-pass"
echo ""
echo "3. Installation starten:"
echo "   ansible-playbook install_checkmk_agent.yml --ask-pass --ask-become-pass"
echo ""
echo "💡 Tipp: Weitere Informationen zur Passwort-Authentifizierung finden Sie in PASSWORD_AUTH.md"
echo ""
