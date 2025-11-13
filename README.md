# CheckMK Agent Installation mit Ansible

Dieses Ansible-Projekt installiert den CheckMK-Agenten auf verschiedenen Linux-Distributionen (RHEL, SLES, Ubuntu, Debian).

## Voraussetzungen

### Auf dem Control Node (Arch Linux)
```bash
# Ansible installieren
sudo pacman -S ansible

# SSH-Zugriff auf die Zielsysteme einrichten
ssh-keygen -t rsa -b 4096
ssh-copy-id user@zielhost
```

### CheckMK-Pakete
Die CheckMK-Agent-Pakete müssen im `files/` Verzeichnis abgelegt werden:

```bash
# Pakete von ~/Downloads ins files/ Verzeichnis kopieren
cp ~/Downloads/check-mk-agent-2.3.0p9-6cc5d32d5bd65f21.noarch.rpm files/
cp ~/Downloads/check-mk-agent_2.3.0p9-6cc5d32d5bd65f21_all.deb files/
```

## Verzeichnisstruktur

```
ansible/
├── ansible.cfg                    # Ansible-Konfiguration
├── inventory/
│   └── hosts                      # Inventory-Datei mit Zielhosts
├── files/
│   ├── check-mk-agent-2.3.0p9-6cc5d32d5bd65f21.noarch.rpm
│   └── check-mk-agent_2.3.0p9-6cc5d32d5bd65f21_all.deb
├── install_checkmk_agent.yml      # Hauptplaybook für Installation
├── uninstall_checkmk_agent.yml    # Playbook für Deinstallation
└── README.md                      # Diese Datei
```

## Konfiguration

### 1. Inventory anpassen
Bearbeiten Sie `inventory/hosts` und fügen Sie Ihre Zielhosts hinzu:

```ini
[rhel_based]
rhel-server-01 ansible_host=192.168.1.10
sles-server-01 ansible_host=192.168.1.11

[debian_based]
ubuntu-server-01 ansible_host=192.168.1.20
debian-server-01 ansible_host=192.168.1.21
```

### 2. CheckMK-Server-IP anpassen
Bearbeiten Sie `install_checkmk_agent.yml` und passen Sie die Variable an:
```yaml
vars:
  checkmk_server: "192.168.1.100"  # IP Ihres CheckMK-Servers
```

## Verwendung

### Installation durchführen

```bash
# Verbindung zu allen Hosts testen
ansible checkmk_agents -m ping

# Playbook auf allen Hosts ausführen
ansible-playbook install_checkmk_agent.yml

# Nur auf RHEL-basierten Systemen ausführen
ansible-playbook install_checkmk_agent.yml --limit rhel_based

# Nur auf Debian-basierten Systemen ausführen
ansible-playbook install_checkmk_agent.yml --limit debian_based

# Nur auf einem spezifischen Host ausführen
ansible-playbook install_checkmk_agent.yml --limit rhel-server-01

# Dry-Run (Test-Modus)
ansible-playbook install_checkmk_agent.yml --check

# Mit erhöhter Verbosity (für Debugging)
ansible-playbook install_checkmk_agent.yml -vvv
```

### Installation überprüfen

```bash
# Agent-Status auf allen Hosts prüfen
ansible checkmk_agents -m shell -a "systemctl status check-mk-agent.socket || service xinetd status"

# Agent-Output direkt testen
ansible checkmk_agents -m shell -a "check_mk_agent | head -20"

# Port-Status prüfen
ansible checkmk_agents -m shell -a "netstat -tlnp | grep 6556 || ss -tlnp | grep 6556"
```

### Deinstallation

```bash
# CheckMK-Agent entfernen
ansible-playbook uninstall_checkmk_agent.yml
```

## Unterstützte Distributionen

- Red Hat Enterprise Linux (RHEL) 7, 8, 9
- CentOS 7, 8
- Rocky Linux 8, 9
- AlmaLinux 8, 9
- SUSE Linux Enterprise Server (SLES) 12, 15
- Ubuntu 18.04, 20.04, 22.04, 24.04
- Debian 10, 11, 12

## Funktionen

Das Playbook führt folgende Aktionen durch:

1. Erkennt automatisch die Linux-Distribution
2. Kopiert das entsprechende Paket (RPM oder DEB)
3. Installiert den CheckMK-Agenten
4. Installiert und konfiguriert xinetd (falls benötigt)
5. Aktiviert systemd socket (falls verfügbar)
6. Konfiguriert die Firewall (firewalld oder ufw)
7. Öffnet Port 6556/TCP
8. Überprüft die Installation
9. Räumt temporäre Dateien auf

## Firewall-Ports

Der CheckMK-Agent verwendet standardmäßig:
- TCP Port 6556

Dieser Port wird automatisch in der Firewall geöffnet.

## Troubleshooting

### SSH-Verbindungsprobleme
```bash
# SSH-Verbindung manuell testen
ssh user@zielhost

# SSH mit Ansible testen
ansible checkmk_agents -m ping
```

### Agent antwortet nicht
```bash
# Service-Status prüfen
ansible checkmk_agents -m shell -a "systemctl status check-mk-agent.socket"

# Manuell auf dem Zielhost testen
ssh zielhost
check_mk_agent
```

### Firewall blockiert
```bash
# Firewall-Status prüfen (RHEL)
ansible rhel_based -m shell -a "firewall-cmd --list-all"

# Firewall-Status prüfen (Ubuntu/Debian)
ansible debian_based -m shell -a "ufw status verbose"
```

### Logs überprüfen
```bash
# Ansible-Log auf Control Node
tail -f ansible.log

# System-Logs auf Zielhost
ansible checkmk_agents -m shell -a "journalctl -u check-mk-agent.socket -n 50"
```

## Weitere Befehle

### Alle Hosts auflisten
```bash
ansible-inventory --list
ansible-inventory --graph
```

### Ad-hoc Befehle ausführen
```bash
# Uptime aller Hosts
ansible checkmk_agents -m shell -a "uptime"

# Disk-Space prüfen
ansible checkmk_agents -m shell -a "df -h"

# Memory-Usage prüfen
ansible checkmk_agents -m shell -a "free -h"
```

## Sicherheitshinweise

- Verwenden Sie SSH-Keys statt Passwörter
- Beschränken Sie den Zugriff auf Port 6556 auf den CheckMK-Server
- Halten Sie die CheckMK-Pakete aktuell
- Überprüfen Sie regelmäßig die Ansible-Logs

## Lizenz

Dieses Projekt dient zur internen Verwendung für die CheckMK-Agent-Installation.

## Autor

Erstellt für die automatisierte CheckMK-Agent-Installation via Ansible.
