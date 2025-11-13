#!/bin/bash
# Setup-Script für Ansible CheckMK-Agent-Installation mit VMware vCenter

set -e

echo "=== Ansible CheckMK Agent Installation - Setup ==="
echo ""

# Prüfen ob Ansible installiert ist
if ! command -v ansible &> /dev/null; then
    echo "❌ Ansible ist nicht installiert!"
    echo "   Installation auf Arch Linux: sudo pacman -S ansible"
    exit 1
fi
echo "✓ Ansible ist installiert: $(ansible --version | head -n1)"

# Prüfen ob Python3 installiert ist
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 ist nicht installiert!"
    echo "   Installation auf Arch Linux: sudo pacman -S python"
    exit 1
fi
echo "✓ Python3 ist installiert: $(python3 --version)"

# Prüfen ob sshpass installiert ist (für Passwort-Authentifizierung)
echo ""
echo "=== Prüfe sshpass (für Passwort-Authentifizierung) ==="
if ! command -v sshpass &> /dev/null; then
    echo "⚠ sshpass ist nicht installiert!"
    echo "   sshpass ermöglicht Passwort-Authentifizierung ohne interaktive Eingabe."
    echo "   Installation auf Arch Linux: sudo pacman -S sshpass"
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
    pip3 install --user pyvmomi requests
else
    echo "✓ pyvmomi ist bereits installiert"
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
