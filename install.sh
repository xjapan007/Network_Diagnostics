#!/bin/bash
if [ "$EUID" -ne 0 ]; then
  echo "Veuillez lancer ce script avec sudo : sudo ./install.sh"
  exit
fi
echo "Installation de Network Diagnostic Tool..."
echo "Copie du binaire..."
cp dist/main /usr/local/bin/network-diagnostic-tool
echo "Installation de l'icône..."
cp icon.png /usr/share/icons/hicolor/128x128/apps/network-diagnostic-tool.png
echo "Création du raccourci dans le menu Démarrer..."
cp network-diagnostic-tool.desktop /usr/share/applications/
echo "Mise à jour du cache système..."
gtk-update-icon-cache /usr/share/icons/hicolor/ -f || true
update-desktop-database /usr/share/applications/ || true
echo "Installation terminée !"
echo "Vous pouvez trouver 'Network Diagnostic Tool' dans votre menu d'applications."