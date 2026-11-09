#!/usr/bin/env python3
"""
Découpeur de vidéo : coupe une grosse vidéo en plusieurs parties
de 30 Mo maximum, automatiquement, sans perte de qualité.

Utilisation :
  - Double-clic (ou `python decoupeur.py`) : ouvre la fenêtre, choisis ta vidéo.
  - Glisser la vidéo sur decoupeur.py / Lancer.bat : découpe directement.
  - Ligne de commande : python decoupeur.py ma_video.mp4 [--taille 30]

Prérequis : ffmpeg et ffprobe installés (https://ffmpeg.org/download.html).
Les parties sont créées dans un dossier "<nom>_parties" à côté de la vidéo.
"""

import argparse
import os
import shutil
import subprocess
import sys
import threading

MO = 1_000_000  # 1 Mo = 1 000 000 octets (valeur la plus stricte, sûre partout)
TAILLE_DEFAUT_MO = 30

# Sous Windows, évite l'ouverture d'une fenêtre console pour chaque appel ffmpeg
CREATIONFLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class ErreurDecoupe(Exception):
    pass


def trouver_outil(nom):
    chemin = shutil.which(nom)
    if chemin:
        return chemin
    # ffmpeg posé à côté du script (pratique sous Windows)
    dossier = os.path.dirname(os.path.abspath(__file__))
    for candidat in (nom, nom + ".exe"):
        p = os.path.join(dossier, candidat)
        if os.path.isfile(p):
            return p
    raise ErreurDecoupe(
        f"'{nom}' est introuvable. Installe ffmpeg (https://ffmpeg.org/download.html) "
        f"ou place {nom}.exe dans le même dossier que ce programme."
    )


def lancer(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace",
                       creationflags=CREATIONFLAGS)
    if r.returncode != 0:
        raise ErreurDecoupe("Erreur ffmpeg/ffprobe :\n" + r.stderr[-2000:])
    return r.stdout


def lire_paquets(ffprobe, video):
    """Liste (index_flux, temps, taille, est_image_cle) de tous les paquets,
    dans l'ordre du fichier. Lecture rapide : aucun décodage."""
    sortie = lancer([
        ffprobe, "-v", "error",
        "-show_entries", "packet=stream_index,pts_time,dts_time,size,flags",
        "-of", "csv=p=0", video,
    ])
    paquets = []
    for ligne in sortie.splitlines():
        champs = ligne.strip().split(",")
        if len(champs) < 5:
            continue
        idx, pts, dts, taille, flags = champs[:5]
        t = pts if pts not in ("", "N/A") else dts
        try:
            paquets.append((int(idx), float(t), int(taille), "K" in flags))
        except ValueError:
            continue
    return paquets


def infos_flux(ffprobe, video):
    sortie = lancer([
        ffprobe, "-v", "error",
        "-show_entries", "stream=index,codec_type:format=duration",
        "-of", "csv=p=0", video,
    ])
    flux_video, duree = None, 0.0
    for ligne in sortie.splitlines():
        champs = ligne.strip().split(",")
        if len(champs) >= 2 and champs[1] == "video" and flux_video is None:
            flux_video = int(champs[0])
        elif len(champs) == 1:
            try:
                duree = float(champs[0])
            except ValueError:
                pass
    if flux_video is None:
        raise ErreurDecoupe("Aucune piste vidéo trouvée dans ce fichier.")
    return flux_video, duree


def planifier_coupes(paquets, flux_video, budget):
    """Choisit les instants de coupe (sur des images clés) pour que chaque
    partie pèse au plus `budget` octets. Renvoie (temps_de_coupe, trop_gros)."""
    coupes = []
    octets = 0              # octets de la partie en cours
    derniere_cle = None     # (temps, octets accumulés avant cette image clé)
    trop_gros = False
    debut_partie = None
    for idx, t, taille, cle in paquets:
        if idx == flux_video and cle:
            if debut_partie is None:
                debut_partie = t
            elif t > debut_partie:
                derniere_cle = (t, octets)
        if octets + taille > budget:
            if derniere_cle is not None:
                t_coupe, octets_avant = derniere_cle
                coupes.append(t_coupe)
                octets -= octets_avant
                debut_partie = t_coupe
                derniere_cle = None
            else:
                trop_gros = True  # un seul bloc entre 2 images clés > budget
        octets += taille
    return coupes, trop_gros


def decouper(video, taille_max_mo=TAILLE_DEFAUT_MO, log=print, progression=None):
    video = os.path.abspath(video)
    if not os.path.isfile(video):
        raise ErreurDecoupe(f"Fichier introuvable : {video}")
    ffmpeg, ffprobe = trouver_outil("ffmpeg"), trouver_outil("ffprobe")
    limite = int(taille_max_mo * MO)

    nom, ext = os.path.splitext(os.path.basename(video))
    ext = ext.lower() or ".mp4"
    dossier = os.path.join(os.path.dirname(video), f"{nom}_parties")
    os.makedirs(dossier, exist_ok=True)

    taille_totale = os.path.getsize(video)
    log(f"Vidéo : {os.path.basename(video)} ({taille_totale / MO:.1f} Mo)")
    if taille_totale <= limite:
        dest = os.path.join(dossier, f"{nom}_partie01{ext}")
        shutil.copy2(video, dest)
        log("La vidéo fait déjà moins de la limite : copiée telle quelle.")
        return [dest]

    log("Analyse de la vidéo…")
    flux_video, duree = infos_flux(ffprobe, video)
    paquets = lire_paquets(ffprobe, video)
    if not paquets:
        raise ErreurDecoupe("Impossible de lire le contenu de la vidéo.")

    marge = 0.97  # garde de la place pour l'en-tête du fichier
    for essai in range(6):
        budget = int(limite * marge) - 200_000
        coupes, trop_gros = planifier_coupes(paquets, flux_video, budget)
        log(f"Découpage en {len(coupes) + 1} parties…")

        for f in os.listdir(dossier):
            if f.startswith(f"{nom}_partie"):
                os.remove(os.path.join(dossier, f))
        modele = os.path.join(dossier, f"{nom}_partie%02d{ext}")
        cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
               "-i", video, "-map", "0:v:0", "-map", "0:a?",
               "-c", "copy", "-f", "segment", "-reset_timestamps", "1",
               "-segment_start_number", "1"]
        if coupes:
            cmd += ["-segment_times", ",".join(f"{t:.6f}" for t in coupes)]
        else:
            cmd += ["-segment_time", "999999"]
        if ext in (".mp4", ".mov", ".m4v"):
            cmd += ["-movflags", "+faststart"]
        cmd += ["-progress", "pipe:1", "-nostats", modele]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, errors="replace", creationflags=CREATIONFLAGS)
        for ligne in proc.stdout:
            if ligne.startswith("out_time_us=") and progression and duree > 0:
                try:
                    progression(min(1.0, int(ligne.split("=")[1]) / 1e6 / duree))
                except ValueError:
                    pass
        erreur = proc.stderr.read()
        if proc.wait() != 0:
            raise ErreurDecoupe("Erreur ffmpeg :\n" + erreur[-2000:])

        parties = sorted(os.path.join(dossier, f) for f in os.listdir(dossier)
                         if f.startswith(f"{nom}_partie"))
        trop = [p for p in parties if os.path.getsize(p) > limite]
        if not trop or trop_gros:
            break
        marge -= 0.04
        log("Une partie dépasse légèrement, nouvel essai avec plus de marge…")

    if progression:
        progression(1.0)
    for p in parties:
        log(f"  ✔ {os.path.basename(p)} : {os.path.getsize(p) / MO:.2f} Mo")
    trop = [p for p in parties if os.path.getsize(p) > limite]
    if trop:
        log("⚠ Certaines parties dépassent la limite : la vidéo a des images clés "
            "trop espacées pour être coupée sans réencodage.")
    log(f"Terminé ! {len(parties)} parties dans : {dossier}")
    return parties


# ---------------------------------------------------------------- Interface --

def interface(video_initiale=None):
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    fen = tk.Tk()
    fen.title("Découpeur vidéo – parties de 30 Mo")
    fen.geometry("560x420")

    tk.Label(fen, text="Découpe ta vidéo en parties de", font=("Segoe UI", 12)).pack(pady=(16, 4))
    ligne = tk.Frame(fen)
    ligne.pack()
    taille = tk.StringVar(value=str(TAILLE_DEFAUT_MO))
    tk.Entry(ligne, textvariable=taille, width=5, justify="center",
             font=("Segoe UI", 12)).pack(side="left")
    tk.Label(ligne, text=" Mo maximum", font=("Segoe UI", 12)).pack(side="left")

    bouton = tk.Button(fen, text="📂  Choisir une vidéo…", font=("Segoe UI", 13, "bold"),
                       padx=20, pady=10)
    bouton.pack(pady=14)
    barre = ttk.Progressbar(fen, length=480, maximum=1.0)
    barre.pack()
    journal = tk.Text(fen, height=12, width=68, state="disabled", font=("Consolas", 9))
    journal.pack(pady=10, padx=10, fill="both", expand=True)

    def log(msg):
        def ecrire():
            journal.configure(state="normal")
            journal.insert("end", msg + "\n")
            journal.see("end")
            journal.configure(state="disabled")
        fen.after(0, ecrire)

    def progression(x):
        fen.after(0, lambda: barre.configure(value=x))

    def traiter(chemin):
        try:
            mo = float(taille.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Taille invalide.")
            return
        bouton.configure(state="disabled")
        barre.configure(value=0)

        def travail():
            try:
                parties = decouper(chemin, mo, log, progression)
                dossier = os.path.dirname(parties[0])
                fen.after(0, lambda: ouvrir_dossier(dossier))
            except Exception as e:  # noqa: BLE001
                log(f"❌ {e}")
            finally:
                fen.after(0, lambda: bouton.configure(state="normal"))
        threading.Thread(target=travail, daemon=True).start()

    def choisir():
        chemin = filedialog.askopenfilename(
            title="Choisis la vidéo à découper",
            filetypes=[("Vidéos", "*.mp4 *.mov *.m4v *.mkv *.avi *.webm *.ts"), ("Tous", "*.*")])
        if chemin:
            traiter(chemin)

    bouton.configure(command=choisir)
    if video_initiale:
        fen.after(300, lambda: traiter(video_initiale))
    fen.mainloop()


def ouvrir_dossier(dossier):
    try:
        if sys.platform.startswith("win"):
            os.startfile(dossier)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", dossier])
        else:
            subprocess.Popen(["xdg-open", dossier])
    except Exception:  # noqa: BLE001
        pass


def main():
    p = argparse.ArgumentParser(description="Coupe une vidéo en parties de 30 Mo maximum.")
    p.add_argument("video", nargs="?", help="vidéo à découper (sinon, ouvre la fenêtre)")
    p.add_argument("--taille", type=float, default=TAILLE_DEFAUT_MO,
                   help="taille max d'une partie en Mo (défaut : 30)")
    p.add_argument("--console", action="store_true", help="pas de fenêtre, tout en console")
    a = p.parse_args()

    if a.video and a.console:
        try:
            decouper(a.video, a.taille)
        except ErreurDecoupe as e:
            sys.exit(f"❌ {e}")
        return
    try:
        interface(a.video)
    except ImportError:
        if not a.video:
            sys.exit("Interface indisponible (tkinter manquant). "
                     "Utilise : python decoupeur.py ma_video.mp4")
        try:
            decouper(a.video, a.taille)
        except ErreurDecoupe as e:
            sys.exit(f"❌ {e}")


if __name__ == "__main__":
    main()
