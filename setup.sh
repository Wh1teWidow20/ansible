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
echo "1. Inventory testen: ansible checkmk_agents -m ping"
echo "2. Installation starten: ansible-playbook install_checkmk_agent.yml"
echo ""
