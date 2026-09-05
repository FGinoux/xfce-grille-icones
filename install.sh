#!/usr/bin/env bash
#
# install.sh — installe « Grille des icônes (bureau) » pour XFCE
#
# Ce script :
#   1. vérifie (et propose d'installer) les dépendances (python3-gi, GTK3)
#   2. copie le script et le lanceur .desktop aux emplacements XDG standards
#      (~/.local/bin et ~/.local/share/applications), sans sudo
#   3. rafraîchit le cache des menus si possible
#
# Usage :
#   ./install.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
APPS_DIR="$HOME/.local/share/applications"

APP_NAME="xfce-grille-icones"
PY_FILE="$APP_NAME.py"
DESKTOP_FILE="$APP_NAME.desktop"

info()  { printf '\033[1;34m[info]\033[0m %s\n' "$1"; }
ok()    { printf '\033[1;32m[ok]\033[0m %s\n' "$1"; }
warn()  { printf '\033[1;33m[attention]\033[0m %s\n' "$1"; }
err()   { printf '\033[1;31m[erreur]\033[0m %s\n' "$1" >&2; }

# --- 1. Vérifications de base -------------------------------------------

if [[ ! -f "$SCRIPT_DIR/$PY_FILE" || ! -f "$SCRIPT_DIR/$DESKTOP_FILE" ]]; then
    err "Ce script doit être lancé depuis le dossier contenant"
    err "  $PY_FILE et $DESKTOP_FILE"
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    err "python3 n'est pas installé. Installez-le d'abord avec votre gestionnaire de paquets."
    exit 1
fi

# --- 2. Dépendance PyGObject / GTK3 --------------------------------------

if ! python3 -c "import gi; gi.require_version('Gtk','3.0'); from gi.repository import Gtk" >/dev/null 2>&1; then
    warn "Le module Python GTK3 (PyGObject) n'est pas détecté."
    PKG=""
    if command -v apt >/dev/null 2>&1; then
        PKG="sudo apt install -y python3-gi gir1.2-gtk-3.0"
    elif command -v dnf >/dev/null 2>&1; then
        PKG="sudo dnf install -y python3-gobject gtk3"
    elif command -v pacman >/dev/null 2>&1; then
        PKG="sudo pacman -S --needed python-gobject gtk3"
    elif command -v zypper >/dev/null 2>&1; then
        PKG="sudo zypper install -y python3-gobject gtk3"
    fi

    if [[ -n "$PKG" ]]; then
        read -r -p "Installer maintenant avec : '$PKG' ? [o/N] " reponse
        if [[ "$reponse" =~ ^[oOyY]$ ]]; then
            eval "$PKG"
        else
            warn "Installation des dépendances ignorée : l'utilitaire ne pourra pas se lancer tant qu'elles ne sont pas installées."
        fi
    else
        warn "Gestionnaire de paquets non reconnu. Installez manuellement PyGObject + GTK3 pour Python 3."
    fi
else
    ok "Dépendances Python GTK3 déjà présentes."
fi

# --- 3. Copie des fichiers aux emplacements XDG --------------------------

mkdir -p "$BIN_DIR" "$APPS_DIR"

install -m 755 "$SCRIPT_DIR/$PY_FILE" "$BIN_DIR/$PY_FILE"
ok "Script installé : $BIN_DIR/$PY_FILE"

install -m 644 "$SCRIPT_DIR/$DESKTOP_FILE" "$APPS_DIR/$DESKTOP_FILE"
ok "Lanceur installé : $APPS_DIR/$DESKTOP_FILE"

# --- 4. Rafraîchir le cache des menus si l'outil existe ------------------

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
    ok "Cache des menus mis à jour."
fi

echo
ok "Installation terminée !"
echo "Vous trouverez « Grille des icônes (bureau) » dans le menu des applications."
echo "Vous pouvez aussi le lancer directement avec :"
echo "    python3 \"$BIN_DIR/$PY_FILE\""
