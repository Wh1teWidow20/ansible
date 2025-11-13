# Passwort-Authentifizierung mit AD-Benutzer

Dieses Dokument beschreibt die Konfiguration für die Verwendung von **Passwort-Authentifizierung** mit einem **Active Directory (AD) Benutzernamen** anstelle von SSH-Keys.

## Voraussetzungen

### sshpass installieren (optional, aber empfohlen)

`sshpass` ermöglicht es Ansible, SSH-Passwörter automatisch zu verwenden:

```bash
# Arch Linux
sudo pacman -S sshpass

# Falls nicht verfügbar in den Repos
yay -S sshpass
# oder
git clone https://aur.archlinux.org/sshpass.git && cd sshpass && makepkg -si
```

**Ohne sshpass:** Sie müssen `--ask-pass` und `--ask-become-pass` bei jedem Befehl verwenden.

## Konfiguration

### 1. AD-Credentials einrichten

```bash
# Credentials-Datei erstellen
cp ad_credentials.sh.example ad_credentials.sh

# Datei schützen (nur Besitzer kann lesen/schreiben)
chmod 600 ad_credentials.sh

# Datei bearbeiten
nano ad_credentials.sh
```

### 2. AD-Benutzername konfigurieren

Bearbeiten Sie `ad_credentials.sh`:

```bash
# Variante 1: Einfacher Username
export AD_USERNAME="maxmustermann"

# Variante 2: UPN-Format (User Principal Name)
export AD_USERNAME="maxmustermann@dptrzm.de"

# Variante 3: Domain-Format (Windows-Stil)
export AD_USERNAME="DPTRZM\\maxmustermann"
```

### 3. Passwörter konfigurieren

Es gibt **drei Methoden** zur Passwort-Verwaltung:

#### Option A: Interaktive Eingabe (EMPFOHLEN - am sichersten)

Lassen Sie die Passwort-Felder in `ad_credentials.sh` leer:

```bash
export ANSIBLE_PASSWORD=""
export ANSIBLE_BECOME_PASSWORD=""
```

Dann verwenden Sie bei jedem Ansible-Befehl:
```bash
ansible-playbook install_checkmk_agent.yml --ask-pass --ask-become-pass
```

#### Option B: Passwörter in Umgebungsvariablen (praktisch)

Setzen Sie die Passwörter direkt in `ad_credentials.sh`:

```bash
export ANSIBLE_PASSWORD="IhrSSHPasswort"
export ANSIBLE_BECOME_PASSWORD="IhrSudoPasswort"  # Meist identisch
```

**WARNUNG:** Passwörter werden im Klartext gespeichert!

#### Option C: Passwörter aus Dateien (sicherer)

Erstellen Sie geschützte Passwort-Dateien:

```bash
# SSH-Passwort speichern
echo "IhrSSHPasswort" > ~/.ansible_ssh_pass
chmod 600 ~/.ansible_ssh_pass

# Sudo-Passwort speichern
echo "IhrSudoPasswort" > ~/.ansible_become_pass
chmod 600 ~/.ansible_become_pass
```

Dann in `ad_credentials.sh`:
```bash
export ANSIBLE_PASSWORD=$(cat ~/.ansible_ssh_pass)
export ANSIBLE_BECOME_PASSWORD=$(cat ~/.ansible_become_pass)
```

## Verwendung

### Credentials laden

**Vor jedem Ansible-Befehl** müssen Sie sowohl vCenter- als auch AD-Credentials laden:

```bash
# Beide Credentials laden
source vcenter_credentials.sh
source ad_credentials.sh
```

### Verbindung testen

```bash
# Credentials laden
source vcenter_credentials.sh
source ad_credentials.sh

# Mit gespeicherten Passwörtern (Option B oder C)
ansible checkmk_agents -m ping

# Oder mit interaktiver Passwort-Eingabe (Option A)
ansible checkmk_agents -m ping --ask-pass --ask-become-pass
```

### Installation durchführen

#### Mit gespeicherten Passwörtern (Option B/C):

```bash
source vcenter_credentials.sh
source ad_credentials.sh
ansible-playbook install_checkmk_agent.yml
```

#### Mit interaktiver Eingabe (Option A):

```bash
source vcenter_credentials.sh
source ad_credentials.sh
ansible-playbook install_checkmk_agent.yml --ask-pass --ask-become-pass
```

Sie werden dann aufgefordert:
1. **SSH password:** Ihr AD-Passwort für SSH-Login
2. **BECOME password:** Ihr AD-Passwort für sudo (meist identisch)

### Beispiel-Workflow

```bash
# 1. Beide Credentials laden
source vcenter_credentials.sh
source ad_credentials.sh

# 2. Inventory anzeigen
ansible-inventory --graph

# 3. Verbindung testen
ansible checkmk_agents -m ping --ask-pass --ask-become-pass

# 4. Installation durchführen
ansible-playbook install_checkmk_agent.yml --ask-pass --ask-become-pass

# 5. Status überprüfen
ansible checkmk_agents -m shell -a "systemctl status check-mk-agent.socket" --ask-pass --ask-become-pass
```

## Troubleshooting

### "Permission denied" oder "Authentication failed"

```bash
# Prüfen Sie, ob AD_USERNAME korrekt gesetzt ist
echo $AD_USERNAME

# Manuell SSH-Verbindung testen
ssh $AD_USERNAME@<vm-ip>

# Falls Domain erforderlich ist, testen Sie verschiedene Formate:
ssh maxmustermann@vm-ip
ssh maxmustermann@dptrzm.de@vm-ip
ssh DPTRZM\\maxmustermann@vm-ip
```

### "sshpass not found"

Installieren Sie sshpass:
```bash
sudo pacman -S sshpass
```

Oder verwenden Sie immer `--ask-pass`:
```bash
ansible-playbook playbook.yml --ask-pass --ask-become-pass
```

### "Incorrect sudo password"

Stellen Sie sicher, dass:
1. Ihr AD-User sudo-Rechte auf den Zielsystemen hat
2. Das sudo-Passwort korrekt ist (meist identisch mit SSH-Passwort)

```bash
# Manuell testen
ssh $AD_USERNAME@vm-ip
sudo -v  # Fragt nach sudo-Passwort
```

### Passwort wird nicht akzeptiert

```bash
# Prüfen Sie die Umgebungsvariablen
echo $ANSIBLE_PASSWORD | wc -c  # Zeigt Länge (sollte > 1 sein)
echo $ANSIBLE_BECOME_PASSWORD | wc -c

# Neu laden
source ad_credentials.sh

# Mit Debug-Output
ansible checkmk_agents -m ping -vvv --ask-pass
```

## Sicherheitshinweise

### Passwörter schützen

```bash
# ad_credentials.sh nur für Besitzer lesbar
chmod 600 ad_credentials.sh

# Passwort-Dateien schützen
chmod 600 ~/.ansible_ssh_pass
chmod 600 ~/.ansible_become_pass

# Prüfen
ls -la ad_credentials.sh
# Sollte zeigen: -rw------- (nur Owner kann lesen/schreiben)
```

### Git-Schutz

Die `.gitignore` verhindert automatisch, dass folgende Dateien committed werden:
- `ad_credentials.sh`
- `.ansible_ssh_pass`
- `.ansible_become_pass`

**Prüfen Sie trotzdem:**
```bash
git status
# Sollte ad_credentials.sh NICHT auflisten
```

### Ansible Vault (Alternative - höchste Sicherheit)

Für maximale Sicherheit verwenden Sie Ansible Vault:

```bash
# 1. Vault-Passwort erstellen
echo "MeinVaultPasswort" > .vault_pass.txt
chmod 600 .vault_pass.txt

# 2. Vault-Datei mit Credentials erstellen
ansible-vault create group_vars/vault.yml
```

Inhalt von `group_vars/vault.yml`:
```yaml
---
vault_ad_username: "maxmustermann"
vault_ssh_password: "IhrSSHPasswort"
vault_sudo_password: "IhrSudoPasswort"
```

Dann in `group_vars/all.yml`:
```yaml
ansible_user: "{{ vault_ad_username }}"
ansible_ssh_pass: "{{ vault_ssh_password }}"
ansible_become_pass: "{{ vault_sudo_password }}"
```

Verwendung:
```bash
ansible-playbook install_checkmk_agent.yml --vault-password-file .vault_pass.txt
```

## Zusammenfassung

### Schnellstart

```bash
# 1. Setup
cp ad_credentials.sh.example ad_credentials.sh
chmod 600 ad_credentials.sh
nano ad_credentials.sh  # AD_USERNAME eintragen

# 2. Credentials laden
source vcenter_credentials.sh
source ad_credentials.sh

# 3. Verwenden (interaktiv - empfohlen)
ansible-playbook install_checkmk_agent.yml --ask-pass --ask-become-pass
```

### Tägliche Verwendung

```bash
# Immer zuerst Credentials laden
source vcenter_credentials.sh
source ad_credentials.sh

# Dann Ansible-Befehle mit --ask-pass --ask-become-pass
```

## Referenz

### Alle relevanten Ansible-Variablen

```yaml
# In group_vars/all.yml
ansible_user: "{{ lookup('env', 'AD_USERNAME') }}"
ansible_ssh_pass: "{{ lookup('env', 'ANSIBLE_PASSWORD') }}"
ansible_become_pass: "{{ lookup('env', 'ANSIBLE_BECOME_PASSWORD') }}"
ansible_become: yes
ansible_become_method: sudo
ansible_become_user: root
```

### Nützliche Befehle

```bash
# Credentials-Status prüfen
echo "AD User: $AD_USERNAME"
echo "SSH Pass set: $([ -n "$ANSIBLE_PASSWORD" ] && echo 'Yes' || echo 'No')"
echo "Sudo Pass set: $([ -n "$ANSIBLE_BECOME_PASSWORD" ] && echo 'Yes' || echo 'No')"

# Credentials neu laden
source vcenter_credentials.sh && source ad_credentials.sh

# Ansible mit Debug
ansible checkmk_agents -m ping -vvv --ask-pass --ask-become-pass
```
