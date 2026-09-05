#!/usr/bin/env bash
#
# uninstall.sh — désinstalle « Grille des icônes (bureau) »
#
# Retire le script et le lanceur .desktop. Propose en option de retirer
# également le bloc de style que l'utilitaire a écrit dans
# ~/.config/gtk-3.0/gtk.css (l'espacement des icônes reviendra alors au
# comportement par défaut de xfdesktop). Les réglages xfconf (taille des
# icônes) ne sont volontairement pas touchés : ce sont des préférences
# système normales, pas des traces de l'installation.
#
set -euo pipefail

BIN_DIR="$HOME/.local/bin"
APPS_DIR="$HOME/.local/share/applications"
APP_NAME="xfce-grille-icones"
GTK_CSS="$HOME/.config/gtk-3.0/gtk.css"
MARK_BEGIN="/* === XFCE-GRILLE-ICONES BEGIN (ne pas éditer à la main) === */"
MARK_END="/* === XFCE-GRILLE-ICONES END === */"

info()  { printf '\033[1;34m[info]\033[0m %s\n' "$1"; }
ok()    { printf '\033[1;32m[ok]\033[0m %s\n' "$1"; }

rm -f "$BIN_DIR/$APP_NAME.py" && ok "Script retiré."
rm -f "$APPS_DIR/$APP_NAME.desktop" && ok "Lanceur retiré."

command -v update-desktop-database >/dev/null 2>&1 && \
    update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true

if [[ -f "$GTK_CSS" ]] && grep -qF "$MARK_BEGIN" "$GTK_CSS"; then
    read -r -p "Retirer aussi le réglage d'espacement dans gtk.css ? [o/N] " reponse
    if [[ "$reponse" =~ ^[oOyY]$ ]]; then
        sed -i "\|$MARK_BEGIN|,\|$MARK_END|d" "$GTK_CSS"
        ok "Bloc retiré de $GTK_CSS."
        pkill -x xfdesktop 2>/dev/null || true
        (xfdesktop >/dev/null 2>&1 &) || true
        ok "xfdesktop redémarré pour appliquer le changement."
    fi
fi

ok "Désinstallation terminée."
