#!/usr/bin/env python3
"""
xfce-grille-icones.py
----------------------
Petit utilitaire graphique (GTK3) pour régler la grille des icônes du
bureau XFCE (xfdesktop) sans avoir besoin d'ouvrir un terminal :

  - Taille des icônes            -> stockée dans xfconf
                                     (channel xfce4-desktop,
                                      propriété /desktop-icons/icon-size)
  - Espacement entre les icônes  -> propriété de style GTK
    (cell-spacing)                  (pas gérée par xfconf : écrite dans
  - Marge autour de chaque icône    ~/.config/gtk-3.0/gtk.css)
    (cell-padding)
  - Largeur du texte sous l'icône
    (cell-text-width-proportion)

Une fois lancé, tout se fait à la souris : curseurs + bouton "Appliquer".

Dépendances (à installer une seule fois, en terminal, avant la première
utilisation) :
    sudo apt install python3-gi gir1.2-gtk-3.0

Installation d'un lanceur (facultatif) : voir le fichier .desktop fourni
à côté de ce script, à copier dans ~/.local/share/applications/
"""

import os
import re
import subprocess
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

XFCONF_CHANNEL = "xfce4-desktop"
XFCONF_ICON_SIZE_PROP = "/desktop-icons/icon-size"

GTK_CSS_PATH = os.path.expanduser("~/.config/gtk-3.0/gtk.css")
MARK_BEGIN = "/* === XFCE-GRILLE-ICONES BEGIN (ne pas éditer à la main) === */"
MARK_END = "/* === XFCE-GRILLE-ICONES END === */"

DEFAULTS = {
    "icon_size": 48,
    "cell_spacing": 6,
    "cell_padding": 6,
    "cell_text_width": 2.5,
}


def run(cmd):
    """Exécute une commande, renvoie (ok, sortie/erreur)."""
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        if out.returncode != 0:
            return False, (out.stderr or out.stdout).strip()
        return True, out.stdout.strip()
    except FileNotFoundError:
        return False, f"Commande introuvable : {cmd[0]}"
    except Exception as exc:  # sécurité : ne jamais planter l'appli
        return False, str(exc)


def read_icon_size():
    ok, out = run(
        ["xfconf-query", "-c", XFCONF_CHANNEL, "-p", XFCONF_ICON_SIZE_PROP]
    )
    if ok:
        try:
            return int(out)
        except ValueError:
            pass
    return DEFAULTS["icon_size"]


def write_icon_size(value):
    ok, err = run(
        ["xfconf-query", "-c", XFCONF_CHANNEL, "-p", XFCONF_ICON_SIZE_PROP,
         "-s", str(int(value))]
    )
    if ok:
        return True, ""
    # La propriété n'existe peut-être pas encore : on la crée.
    ok2, err2 = run(
        ["xfconf-query", "-c", XFCONF_CHANNEL, "-p", XFCONF_ICON_SIZE_PROP,
         "-n", "-t", "int", "-s", str(int(value))]
    )
    return ok2, ("" if ok2 else (err2 or err))


def read_gtk_css_block():
    """Lit les valeurs actuelles cell-spacing/padding/text-width depuis
    gtk.css si notre bloc y est déjà présent, sinon renvoie les défauts."""
    values = dict(cell_spacing=DEFAULTS["cell_spacing"],
                  cell_padding=DEFAULTS["cell_padding"],
                  cell_text_width=DEFAULTS["cell_text_width"])
    if not os.path.exists(GTK_CSS_PATH):
        return values
    try:
        content = open(GTK_CSS_PATH, encoding="utf-8").read()
    except OSError:
        return values
    block_match = re.search(
        re.escape(MARK_BEGIN) + r"(.*?)" + re.escape(MARK_END),
        content, re.DOTALL,
    )
    if not block_match:
        return values
    block = block_match.group(1)
    for key, css_name in (
        ("cell_spacing", "cell-spacing"),
        ("cell_padding", "cell-padding"),
        ("cell_text_width", "cell-text-width-proportion"),
    ):
        m = re.search(r"-XfdesktopIconView-%s\s*:\s*([0-9.]+)" % re.escape(css_name), block)
        if m:
            values[key] = float(m.group(1)) if "." in m.group(1) else int(m.group(1))
    return values


def write_gtk_css_block(cell_spacing, cell_padding, cell_text_width):
    """Insère/remplace notre bloc dans gtk.css sans toucher au reste du
    fichier (au cas où l'utilisateur y a déjà d'autres réglages)."""
    new_block = (
        f"{MARK_BEGIN}\n"
        "XfdesktopIconView.view {\n"
        f"    -XfdesktopIconView-cell-spacing: {int(cell_spacing)};\n"
        f"    -XfdesktopIconView-cell-padding: {int(cell_padding)};\n"
        f"    -XfdesktopIconView-cell-text-width-proportion: {cell_text_width};\n"
        "}\n"
        f"{MARK_END}\n"
    )

    os.makedirs(os.path.dirname(GTK_CSS_PATH), exist_ok=True)

    content = ""
    if os.path.exists(GTK_CSS_PATH):
        try:
            content = open(GTK_CSS_PATH, encoding="utf-8").read()
        except OSError as exc:
            return False, str(exc)

    pattern = re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END) + r"\n?"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_block, content, flags=re.DOTALL)
    else:
        if content and not content.endswith("\n"):
            content += "\n"
        content += new_block

    try:
        with open(GTK_CSS_PATH, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as exc:
        return False, str(exc)
    return True, ""


def restart_xfdesktop():
    """Relance xfdesktop pour que le nouveau CSS soit pris en compte."""
    run(["pkill", "-x", "xfdesktop"])
    try:
        subprocess.Popen(
            ["xfdesktop"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return True, ""
    except FileNotFoundError:
        return False, "xfdesktop introuvable dans le PATH."


class GrilleWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Grille des icônes du bureau — XFCE")
        self.set_border_width(16)
        self.set_default_size(460, 320)

        current_css = read_gtk_css_block()
        current_icon_size = read_icon_size()

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(root)

        grid = Gtk.Grid(column_spacing=12, row_spacing=14)
        root.pack_start(grid, True, True, 0)

        self.scale_icon = self._add_row(
            grid, 0, "Taille des icônes (px)",
            16, 256, 8, current_icon_size,
        )
        self.scale_spacing = self._add_row(
            grid, 1, "Espacement entre icônes (px)",
            0, 64, 2, current_css["cell_spacing"],
        )
        self.scale_padding = self._add_row(
            grid, 2, "Marge autour de chaque icône (px)",
            0, 64, 2, current_css["cell_padding"],
        )
        self.scale_text_width = self._add_row(
            grid, 3, "Largeur du texte sous l'icône (proportion)",
            1.0, 4.0, 0.1, current_css["cell_text_width"], digits=1,
        )

        self.restart_check = Gtk.CheckButton(
            label="Redémarrer xfdesktop automatiquement après application "
                  "(nécessaire pour voir l'espacement changer)"
        )
        self.restart_check.set_active(True)
        root.pack_start(self.restart_check, False, False, 0)

        self.status_label = Gtk.Label(label="")
        self.status_label.set_xalign(0)
        root.pack_start(self.status_label, False, False, 0)

        button_box = Gtk.Box(spacing=8)
        root.pack_start(button_box, False, False, 0)

        btn_reset = Gtk.Button(label="Valeurs par défaut")
        btn_reset.connect("clicked", self.on_reset)
        button_box.pack_start(btn_reset, False, False, 0)

        btn_quit = Gtk.Button(label="Fermer")
        btn_quit.connect("clicked", lambda w: Gtk.main_quit())
        button_box.pack_end(btn_quit, False, False, 0)

        btn_apply = Gtk.Button(label="Appliquer")
        btn_apply.get_style_context().add_class("suggested-action")
        btn_apply.connect("clicked", self.on_apply)
        button_box.pack_end(btn_apply, False, False, 0)

        self.connect("destroy", lambda w: Gtk.main_quit())

    def _add_row(self, grid, row, label_text, lo, hi, step, value, digits=0):
        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        grid.attach(label, 0, row, 1, 1)

        adj = Gtk.Adjustment(value=value, lower=lo, upper=hi,
                              step_increment=step)
        scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                           adjustment=adj)
        scale.set_digits(digits)
        scale.set_value_pos(Gtk.PositionType.RIGHT)
        scale.set_hexpand(True)
        grid.attach(scale, 1, row, 1, 1)
        return scale

    def on_reset(self, _widget):
        self.scale_icon.set_value(DEFAULTS["icon_size"])
        self.scale_spacing.set_value(DEFAULTS["cell_spacing"])
        self.scale_padding.set_value(DEFAULTS["cell_padding"])
        self.scale_text_width.set_value(DEFAULTS["cell_text_width"])
        self.status_label.set_text(
            "Valeurs par défaut chargées. Cliquez sur \"Appliquer\" pour "
            "les activer."
        )

    def on_apply(self, _widget):
        icon_size = self.scale_icon.get_value()
        cell_spacing = self.scale_spacing.get_value()
        cell_padding = self.scale_padding.get_value()
        cell_text_width = round(self.scale_text_width.get_value(), 1)

        messages = []

        ok, err = write_icon_size(icon_size)
        messages.append(
            "✔ Taille des icônes appliquée." if ok
            else f"✘ Échec taille des icônes : {err}"
        )

        ok, err = write_gtk_css_block(cell_spacing, cell_padding, cell_text_width)
        messages.append(
            "✔ Espacement/marge écrits dans gtk.css." if ok
            else f"✘ Échec écriture gtk.css : {err}"
        )

        if self.restart_check.get_active():
            ok, err = restart_xfdesktop()
            messages.append(
                "✔ xfdesktop redémarré." if ok
                else f"✘ Échec redémarrage xfdesktop : {err}"
            )
        else:
            messages.append(
                "ℹ Pensez à redémarrer xfdesktop (clic droit sur le "
                "bureau > Actions > ou déconnexion/reconnexion) pour voir "
                "l'espacement changer."
            )

        self.status_label.set_text("\n".join(messages))


def main():
    if os.environ.get("XDG_CURRENT_DESKTOP", "").upper().find("XFCE") == -1:
        # On n'empêche pas l'utilisation, juste un avertissement discret.
        pass
    win = GrilleWindow()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
