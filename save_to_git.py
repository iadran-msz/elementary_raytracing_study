"""Sauvegarde (add + commit + push) de tout le dossier du projet vers GitHub.

Fonctionne de la meme facon sur le PC Linux, dans Colab, ou en ligne de
commande sur n'importe quelle machine ou le depot est clone.

Utilisation en ligne de commande :
    python save_to_git.py "message de commit"
    python save_to_git.py               # message genere automatiquement

Utilisation depuis un notebook :
    from save_to_git import save_to_git
    save_to_git("message de commit")
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent

# Identite utilisee pour les commits si le depot n'en a pas deja une
# configuree (ex: conteneur Colab, neuf a chaque session). N'est jamais
# ecrite en configuration globale, uniquement locale a ce depot.
DEFAULT_NAME = "Adrian Marszalek"
DEFAULT_EMAIL = "adr.mrzk@gmail.com"


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=REPO_DIR, capture_output=True, text=True
    )


def _ensure_git_identity() -> None:
    for key, value in (("user.name", DEFAULT_NAME), ("user.email", DEFAULT_EMAIL)):
        current = _run(["git", "config", key])
        if not current.stdout.strip():
            _run(["git", "config", key, value])


def save_to_git(message: str | None = None) -> None:
    """Ajoute tous les changements, commit et push vers le remote courant.

    Ne fait rien (et le signale) si aucun changement n'est detecte, pour
    eviter les commits vides.
    """
    if message is None:
        message = f"Sauvegarde automatique du {datetime.now():%Y-%m-%d %H:%M}"

    _ensure_git_identity()

    status = _run(["git", "status", "--porcelain"])
    if not status.stdout.strip():
        print("[save_to_git] Rien a sauvegarder, aucun changement detecte.")
        return

    add = _run(["git", "add", "-A"])
    if add.returncode != 0:
        print(add.stderr)
        raise RuntimeError("Echec de 'git add'")

    commit = _run(["git", "commit", "-m", message])
    if commit.returncode != 0:
        print(commit.stdout, commit.stderr)
        raise RuntimeError("Echec de 'git commit'")
    print(commit.stdout)

    push = _run(["git", "push"])
    if push.returncode != 0:
        print(push.stdout, push.stderr)
        raise RuntimeError(
            "Echec de 'git push' (verifie l'authentification GitHub)"
        )
    print("[save_to_git] Push effectue avec succes.")


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    save_to_git(msg)
