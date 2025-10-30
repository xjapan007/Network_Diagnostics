# Network Diagnostic Tool

Un simple outil graphique pour Windows et Linux permettant de tester la latence (ping) et la vitesse de connexion (speedtest).

![Aperçu de l'application](icon.png)

## Fonctionnalités

* Test de Ping vers un hôte personnalisé.
* Test de vitesse (Download/Upload) via `speedtest-cli`.
* Interface moderne avec thème clair/sombre.
* Historique des tests sauvegardé dans un fichier `network_log.txt`.

## Installation

Allez dans la section **[Releases](https://github.com/VOTRE-NOM/VOTRE-REPO/releases)** de ce dépôt pour télécharger l'installateur.

---

### Pour Windows
1.  Téléchargez `NetworkTool-Setup.exe`.
2.  Lancez l'installateur et suivez les instructions. L'application sera ajoutée à votre menu Démarrer.

---

### Pour Linux (Debian/Ubuntu)
1.  Téléchargez les 4 fichiers de la "Release" Linux :
    * `main` (le binaire)
    * `install.sh` (le script d'installation)
    * `network-diagnostic-tool.desktop`
    * `diag.png`
2.  Placez-les tous dans un même dossier.
3.  Ouvrez un terminal dans ce dossier et lancez :
    ```bash
    # Donne la permission d'exécution au script
    chmod +x install.sh
    
    # Lance l'installation
    sudo ./install.sh
    ```
4.  L'application sera disponible dans votre menu Démarrer.

---
## Pour les développeurs (Code Source)

Ce projet est écrit en Python avec la bibliothèque CustomTkinter.

### Prérequis
* Python 3.x
* `pip install customtkinter speedtest-cli`

### Lancer depuis le code
1.  Clonez ce dépôt.
2.  Lancez : `python3 main.py`