# CheckMK Agent Installation mit Ansible und VMware vCenter

Dieses Ansible-Projekt installiert den CheckMK-Agenten automatisch auf VMs aus einem VMware vCenter Server. Es werden nur VMs berücksichtigt, deren Name mit "LTERZTA" beginnt.

**🔐 WICHTIG:** Dieses Setup verwendet **Passwort-Authentifizierung mit AD-Benutzern** (keine SSH-Keys). Siehe [PASSWORD_AUTH.md](PASSWORD_AUTH.md) für Details.

## Voraussetzungen

### Auf dem Control Node (Arch Linux)

```bash
# Ansible und sshpass installieren
sudo pacman -S ansible python python-pip sshpass

# Python VMware-Bibliothek installieren
pip install --user pyvmomi requests
```

### CheckMK-Pakete

Die CheckMK-Agent-Pakete müssen im `files/` Verzeichnis abgelegt werden:

```bash
# Pakete von ~/Downloads ins files/ Verzeichnis kopieren
cp ~/Downloads/check-mk-agent-2.3.0p9-6cc5d32d5bd65f21.noarch.rpm files/
cp ~/Downloads/check-mk-agent_2.3.0p9-6cc5d32d5bd65f21_all.deb files/
```

## Schnellstart

### 1. Automatisches Setup (empfohlen)

```bash
# 1. vCenter Credentials konfigurieren
cp vcenter_credentials.sh.example vcenter_credentials.sh
nano vcenter_credentials.sh  # vCenter Username und Password eintragen

# 2. AD-Credentials konfigurieren (für SSH-Zugriff auf VMs)
cp ad_credentials.sh.example ad_credentials.sh
chmod 600 ad_credentials.sh
nano ad_credentials.sh  # Ihren AD-Benutzernamen eintragen

# 3. Automatisches Setup ausführen
./setup.sh

# 4. Installation starten
source vcenter_credentials.sh
source ad_credentials.sh
ansible-playbook install_checkmk_agent.yml --ask-pass --ask-become-pass
```

**Hinweis:** Sie werden nach Ihrem SSH- und sudo-Passwort gefragt.

### 2. Manuelles Setup

```bash
# 1. Ansible Collections installieren
ansible-galaxy collection install -r requirements.yml

# 2. Python-Abhängigkeiten installieren
pip install --user pyvmomi requests

# 3. vCenter Credentials setzen
export VCENTER_USERNAME="ihr-username@vsphere.local"
export VCENTER_PASSWORD="ihr-passwort"

# 4. AD-Benutzernamen setzen
export AD_USERNAME="ihr-ad-username"

# 5. Inventory testen
ansible-inventory -i inventory/vmware.yml --graph

# 6. Installation durchführen (mit Passwort-Abfrage)
ansible-playbook install_checkmk_agent.yml --ask-pass --ask-become-pass
```

## Verzeichnisstruktur

```
ansible/
├── ansible.cfg                           # Ansible-Konfiguration mit Inventory-Plugin
├── requirements.yml                      # Ansible Collections (VMware)
├── setup.sh                              # Automatisches Setup-Script
├── vcenter_credentials.sh.example        # Vorlage für vCenter Credentials
├── ad_credentials.sh.example             # Vorlage für AD-User Credentials (SSH)
├── install_checkmk_agent.yml             # Hauptplaybook für Installation
├── uninstall_checkmk_agent.yml           # Playbook für Deinstallation
├── README.md                             # Diese Datei
├── PASSWORD_AUTH.md                      # Anleitung für Passwort-Authentifizierung
├── inventory/
│   ├── hosts                             # Statisches Inventory (optional)
│   └── vmware.yml                        # Dynamisches VMware Inventory Plugin
├── group_vars/
│   └── all.yml                           # Globale Variablen (inkl. AD-User)
└── files/
    ├── check-mk-agent-*.rpm              # RPM-Paket
    └── check-mk-agent_*.deb              # DEB-Paket
```

## vCenter Konfiguration

### Dynamisches Inventory

Das System verwendet das `community.vmware.vmware_vm_inventory` Plugin, um automatisch VMs aus dem vCenter zu laden.

**Konfiguration:** `inventory/vmware.yml`

- **vCenter Server:** LTERZTA001.dptrzm.de
- **Filter:** Nur VMs die mit "LTERZTA" beginnen
- **Gruppierung:** Automatisch nach Betriebssystem (rhel_based, debian_based, suse_based)

### Credentials konfigurieren

```bash
# Credentials-Datei erstellen
cp vcenter_credentials.sh.example vcenter_credentials.sh

# Bearbeiten und Ihre Zugangsdaten eintragen
nano vcenter_credentials.sh
```

Inhalt von `vcenter_credentials.sh`:
```bash
export VCENTER_USERNAME="ihr-username@vsphere.local"
export VCENTER_PASSWORD="ihr-passwort"
```

**Wichtig:** Diese Datei wird NICHT in Git eingecheckt!

### Credentials laden

Vor jedem Ansible-Befehl BEIDE Credentials laden:
```bash
source vcenter_credentials.sh  # Für vCenter-Zugriff
source ad_credentials.sh        # Für SSH-Zugriff auf VMs
```

## Verwendung

### Inventory anzeigen

```bash
# Credentials laden
source vcenter_credentials.sh
source ad_credentials.sh

# Alle VMs aus vCenter anzeigen (mit LTERZTA prefix)
ansible-inventory -i inventory/vmware.yml --graph

# Detaillierte Liste als JSON
ansible-inventory -i inventory/vmware.yml --list

# Nur bestimmte Gruppen anzeigen
ansible-inventory --graph rhel_based
ansible-inventory --graph debian_based
```

### Verbindung testen

```bash
# Credentials laden
source vcenter_credentials.sh
source ad_credentials.sh

# Alle gefundenen VMs testen (Passwort wird abgefragt)
ansible checkmk_agents -m ping --ask-pass --ask-become-pass

# Nur RHEL-basierte Systeme testen
ansible rhel_based -m ping --ask-pass --ask-become-pass

# Nur Debian-basierte Systeme testen
ansible debian_based -m ping --ask-pass --ask-become-pass
```

### CheckMK-Agent installieren

```bash
# Credentials laden
source vcenter_credentials.sh
source ad_credentials.sh

# Auf allen VMs installieren (Passwort wird abgefragt)
ansible-playbook install_checkmk_agent.yml --ask-pass --ask-become-pass

# Nur auf RHEL-basierten Systemen
ansible-playbook install_checkmk_agent.yml --limit rhel_based --ask-pass --ask-become-pass

# Nur auf Debian-basierten Systemen
ansible-playbook install_checkmk_agent.yml --limit debian_based --ask-pass --ask-become-pass

# Nur auf einer spezifischen VM
ansible-playbook install_checkmk_agent.yml --limit LTERZTA-SERVER-01 --ask-pass --ask-become-pass

# Dry-Run (Test-Modus ohne Änderungen)
ansible-playbook install_checkmk_agent.yml --check --ask-pass --ask-become-pass

# Mit erhöhter Verbosity (für Debugging)
ansible-playbook install_checkmk_agent.yml -vvv --ask-pass --ask-become-pass
```

**💡 Tipp:** Siehe [PASSWORD_AUTH.md](PASSWORD_AUTH.md) für Möglichkeiten, Passwörter zu speichern und nicht jedes Mal eingeben zu müssen.

### Installation überprüfen

```bash
# Credentials laden
source vcenter_credentials.sh
source ad_credentials.sh

# Agent-Status auf allen Hosts prüfen
ansible checkmk_agents -m shell -a "systemctl status check-mk-agent.socket || service xinetd status" --ask-pass --ask-become-pass

# Agent-Output direkt testen
ansible checkmk_agents -m shell -a "check_mk_agent | head -20" --ask-pass --ask-become-pass

# Port-Status prüfen
ansible checkmk_agents -m shell -a "ss -tlnp | grep 6556" --ask-pass --ask-become-pass
```

### Deinstallation

```bash
# Credentials laden
source vcenter_credentials.sh
source ad_credentials.sh

# Deinstallation durchführen
ansible-playbook uninstall_checkmk_agent.yml --ask-pass --ask-become-pass
```

## Konfiguration anpassen

### CheckMK-Server IP ändern

Bearbeiten Sie `group_vars/all.yml`:
```yaml
checkmk_server: "192.168.1.100"  # Ihre CheckMK-Server IP
```

### Inventory-Filter anpassen

Bearbeiten Sie `inventory/vmware.yml` um den Filter zu ändern:

```yaml
# Aktuell: Nur VMs die mit "LTERZTA" beginnen
filters:
  - name is match("LTERZTA.*")

# Beispiele für andere Filter:
# - name is match("PROD.*")           # VMs die mit PROD beginnen
# - name contains "WEB"               # VMs die WEB enthalten
# - runtime.powerState == "poweredOn" # Nur eingeschaltete VMs
```

## Unterstützte Distributionen

Das Playbook erkennt automatisch die Distribution und verwendet das richtige Paket:

- **RHEL-basiert** (RPM): RHEL 7/8/9, CentOS, Rocky Linux, AlmaLinux
- **SUSE-basiert** (RPM): SLES 12/15
- **Debian-basiert** (DEB): Ubuntu 18.04/20.04/22.04/24.04, Debian 10/11/12

## Funktionen

Das Playbook führt automatisch folgende Aktionen durch:

1. Erkennt die Linux-Distribution der Ziel-VM
2. Kopiert das entsprechende Paket (RPM oder DEB)
3. Installiert den CheckMK-Agenten
4. Installiert und konfiguriert xinetd (falls benötigt)
5. Aktiviert systemd socket (falls verfügbar)
6. Konfiguriert die Firewall (firewalld oder ufw)
7. Öffnet Port 6556/TCP
8. Überprüft die Installation
9. Räumt temporäre Dateien auf

## Firewall-Ports

Der CheckMK-Agent verwendet standardmäßig **TCP Port 6556**.
Dieser Port wird automatisch in der Firewall geöffnet.

## Troubleshooting

### vCenter-Verbindungsprobleme

```bash
# Credentials prüfen
echo $VCENTER_USERNAME
echo $VCENTER_PASSWORD

# vCenter Erreichbarkeit testen
ping LTERZTA001.dptrzm.de
curl -k https://LTERZTA001.dptrzm.de

# Inventory manuell laden
ansible-inventory -i inventory/vmware.yml --list -vvv
```

### Keine VMs gefunden

```bash
# Prüfen ob VMs mit "LTERZTA" prefix existieren
# Filter in inventory/vmware.yml überprüfen

# Manuell im vCenter nachsehen ob VMs:
# - mit "LTERZTA" beginnen
# - eingeschaltet sind (poweredOn)
# - Linux-VMs sind
```

### SSL-Zertifikat-Fehler

In `inventory/vmware.yml` ist bereits konfiguriert:
```yaml
validate_certs: no  # Deaktiviert SSL-Zertifikat-Prüfung
```

### SSH-Verbindungsprobleme

```bash
# SSH-Zugriff manuell testen mit AD-User
ssh $AD_USERNAME@<vm-ip>

# Verschiedene Username-Formate testen
ssh maxmustermann@<vm-ip>
ssh maxmustermann@dptrzm.de@<vm-ip>

# Passwort-Authentifizierung ist aktiviert (keine SSH-Keys erforderlich)
```

**Hinweis:** Dieses Setup verwendet Passwort-Authentifizierung, daher sind keine SSH-Keys erforderlich. Siehe [PASSWORD_AUTH.md](PASSWORD_AUTH.md) für Details.

### Agent antwortet nicht

```bash
# Service-Status prüfen
ansible checkmk_agents -m shell -a "systemctl status check-mk-agent.socket"

# Logs prüfen
ansible checkmk_agents -m shell -a "journalctl -u check-mk-agent.socket -n 50"

# Port prüfen
ansible checkmk_agents -m shell -a "netstat -tlnp | grep 6556"
```

### Firewall blockiert

```bash
# Firewall-Status prüfen (RHEL)
ansible rhel_based -m shell -a "firewall-cmd --list-all"

# Firewall-Status prüfen (Ubuntu/Debian)
ansible debian_based -m shell -a "ufw status verbose"

# Port manuell öffnen (RHEL)
ansible rhel_based -m shell -a "firewall-cmd --permanent --add-port=6556/tcp && firewall-cmd --reload"

# Port manuell öffnen (Ubuntu/Debian)
ansible debian_based -m shell -a "ufw allow 6556/tcp"
```

## Weitere nützliche Befehle

### Ad-hoc Befehle auf allen VMs

```bash
# Credentials laden
source vcenter_credentials.sh
source ad_credentials.sh

# Uptime aller VMs
ansible checkmk_agents -m shell -a "uptime" --ask-pass --ask-become-pass

# Disk-Space prüfen
ansible checkmk_agents -m shell -a "df -h" --ask-pass --ask-become-pass

# Memory-Usage prüfen
ansible checkmk_agents -m shell -a "free -h" --ask-pass --ask-become-pass

# Kernel-Version
ansible checkmk_agents -m shell -a "uname -r" --ask-pass --ask-become-pass

# OS-Version
ansible checkmk_agents -m shell -a "cat /etc/os-release" --ask-pass --ask-become-pass
```

### Inventory Cache

Das Inventory wird gecacht (1 Stunde), um wiederholte Anfragen zu beschleunigen.

```bash
# Cache löschen
rm -rf .ansible_cache/

# Cache-Timeout in ansible.cfg anpassen:
# fact_caching_timeout = 3600  # Sekunden
```

### Performance-Optimierung

Für große Umgebungen mit vielen VMs:

```bash
# Parallelität erhöhen in ansible.cfg
forks = 20  # Statt 10

# Pipelining aktiviert (bereits konfiguriert)
pipelining = True
```

## Sicherheitshinweise

- **SSH-Keys verwenden:** Verwenden Sie SSH-Keys statt Passwörter
- **Zugriffsbeschränkung:** Beschränken Sie den Zugriff auf Port 6556 auf den CheckMK-Server
- **Credentials schützen:** Die Datei `vcenter_credentials.sh` wird nicht in Git eingecheckt
- **Ansible Vault:** Für zusätzliche Sicherheit können Sie Ansible Vault verwenden:

```bash
# Vault-Datei erstellen
ansible-vault create group_vars/vault.yml

# Credentials in Vault speichern
vcenter_username: "user@vsphere.local"
vcenter_password: "password"

# In inventory/vmware.yml referenzieren:
username: "{{ vcenter_username }}"
password: "{{ vcenter_password }}"
```

## Automatisierung

### Cronjob für regelmäßige Installation

```bash
# Crontab bearbeiten
crontab -e

# Jeden Tag um 2 Uhr morgens ausführen
0 2 * * * cd /pfad/zu/ansible && source vcenter_credentials.sh && ansible-playbook install_checkmk_agent.yml >> /var/log/checkmk-deployment.log 2>&1
```

## Support und Dokumentation

- Ansible VMware Guide: https://docs.ansible.com/ansible/latest/collections/community/vmware/
- CheckMK Dokumentation: https://docs.checkmk.com/
- Ansible Best Practices: https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html

## Lizenz

Dieses Projekt dient zur internen Verwendung für die automatisierte CheckMK-Agent-Installation via Ansible und VMware vCenter.
