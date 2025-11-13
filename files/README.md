# CheckMK Agent Pakete

Bitte legen Sie die CheckMK-Agent-Pakete in diesem Verzeichnis ab:

## Benötigte Dateien

1. **RPM-Paket** (für RHEL, CentOS, Rocky, AlmaLinux, SLES):
   ```
   check-mk-agent-2.3.0p9-6cc5d32d5bd65f21.noarch.rpm
   ```

2. **DEB-Paket** (für Ubuntu, Debian):
   ```
   check-mk-agent_2.3.0p9-6cc5d32d5bd65f21_all.deb
   ```

## Pakete kopieren

Kopieren Sie die Pakete aus Ihrem Downloads-Ordner:

```bash
cp ~/Downloads/check-mk-agent-2.3.0p9-6cc5d32d5bd65f21.noarch.rpm ./files/
cp ~/Downloads/check-mk-agent_2.3.0p9-6cc5d32d5bd65f21_all.deb ./files/
```

## Überprüfung

Nach dem Kopieren sollten die Dateien hier vorhanden sein:

```bash
ls -lh files/
```

Erwartete Ausgabe:
```
-rw-r--r-- 1 user user  XXX check-mk-agent-2.3.0p9-6cc5d32d5bd65f21.noarch.rpm
-rw-r--r-- 1 user user  XXX check-mk-agent_2.3.0p9-6cc5d32d5bd65f21_all.deb
```

## Hinweis

Diese Pakete werden NICHT in das Git-Repository eingecheckt, da sie zu groß sind. Jeder Benutzer muss sie separat von der CheckMK-Website herunterladen.
