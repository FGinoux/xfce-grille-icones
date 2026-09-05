# Grille des icônes (bureau) — utilitaire XFCE

This is a small graphical utility for Xfce that allows you to easily adjust the desktop grid layout and icon size without editing files, while also making it easy to revert to the original settings.

Petit utilitaire graphique (GTK3) pour régler la **taille**, l'**espacement**
et la **marge** de la grille d'icônes du bureau XFCE (`xfdesktop`), sans
jamais avoir besoin d'ouvrir un terminal ni d'éditer `gtk.css` à la main.


![XFCE](https://img.shields.io/badge/desktop-XFCE-1e9c4d)
![Python](https://img.shields.io/badge/python-3-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)

## Pourquoi ce projet ?

Sous XFCE, la taille des icônes du bureau se règle via `xfconf`, mais
l'espacement entre les icônes (*cell-spacing*) et la marge autour de
chacune (*cell-padding*) ne sont **pas** exposés dans les paramètres
graphiques standards : il faut normalement éditer à la main
`~/.config/gtk-3.0/gtk.css` et redémarrer `xfdesktop` à chaque essai.

Cet utilitaire regroupe ces réglages dans une seule fenêtre avec des
curseurs, et applique les changements immédiatement (avec redémarrage
automatique de `xfdesktop` en option).

![Capture d'écran] ([/Capture d’écran_2026-09-05_19-23-19.png](https://github.com/FGinoux/xfce-grille-icones/blob/main/Capture%20d%E2%80%99%C3%A9cran_2026-09-05_19-23-19.png?raw=true))

## Fonctionnalités

- Curseur **taille des icônes** (`xfconf`, `/desktop-icons/icon-size`)
- Curseur **espacement entre icônes** (`cell-spacing`, écrit dans `gtk.css`)
- Curseur **marge autour de chaque icône** (`cell-padding`, `gtk.css`)
- Curseur **largeur du texte** sous l'icône (`cell-text-width-proportion`)
- Bouton **valeurs par défaut**
- Redémarrage automatique de `xfdesktop` (optionnel) pour voir le résultat
  tout de suite

## Prérequis

- Un environnement de bureau **XFCE** (testé sur XFCE 4.16/4.18/4.20)
- Python 3
- PyGObject + GTK3 (`python3-gi`, `gir1.2-gtk-3.0` sous Debian/Ubuntu)

## Installation

```bash
git clone https://github.com/FGinoux/xfce-grille-icones.git
cd xfce-grille-icones
./install.sh
```

Le script `install.sh` :
1. vérifie que PyGObject/GTK3 sont installés (et propose de les installer
   sinon, selon votre distribution : `apt`, `dnf`, `pacman`, `zypper`) ;
2. copie `xfce-grille-icones.py` dans `~/.local/bin/` ;
3. copie `xfce-grille-icones.desktop` dans `~/.local/share/applications/` ;
4. rafraîchit le cache des menus.

Aucune commande n'est exécutée avec les droits root, à l'exception de
l'installation des paquets système (avec votre confirmation explicite).

Après installation, l'utilitaire apparaît dans le menu des applications
sous le nom **« Grille des icônes (bureau) »**.

### Installation manuelle

```bash
mkdir -p ~/.local/bin ~/.local/share/applications
cp xfce-grille-icones.py ~/.local/bin/
cp xfce-grille-icones.desktop ~/.local/share/applications/
chmod +x ~/.local/bin/xfce-grille-icones.py
```

## Désinstallation

```bash
./uninstall.sh
```

Retire le script et le lanceur. Propose en option de retirer aussi le
bloc de style ajouté dans `gtk.css` (l'espacement redevient alors celui
par défaut de `xfdesktop`). Les réglages de taille d'icône (`xfconf`)
ne sont pas touchés : ce sont vos préférences, pas des traces de
l'installation.

## Comment ça marche en coulisses

| Réglage | Stocké où | Appliqué comment |
|---|---|---|
| Taille des icônes | `xfconf` (`xfce4-desktop`, `/desktop-icons/icon-size`) | immédiat |
| Espacement / marge / largeur du texte | `~/.config/gtk-3.0/gtk.css`, propriétés de style `XfdesktopIconView` | après redémarrage de `xfdesktop` |

Le bloc écrit dans `gtk.css` est délimité par des marqueurs
(`XFCE-GRILLE-ICONES BEGIN/END`) afin de ne jamais toucher au reste de
votre fichier CSS si vous y avez déjà d'autres personnalisations.

## Contribuer

Les contributions sont bienvenues, en particulier :
- une capture d'écran ou un court GIF pour ce README ;
- test sur d'autres versions de XFCE / distributions ;
- traductions (l'interface est actuellement en français).

Merci d'ouvrir une *issue* avant une *pull request* importante, pour
discuter de l'approche.

## Licence

Distribué sous licence MIT — voir [LICENSE](LICENSE).
