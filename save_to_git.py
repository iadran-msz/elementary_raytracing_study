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

import os
import re
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


def _push_url_with_token(token: str) -> str | None:
    """Construit l'URL du remote courant avec le token GitHub insere dedans,
    sans jamais l'ecrire dans la config git (donc pas de fuite dans .git/config)."""
    remote_name = _run(["git", "remote"]).stdout.strip().splitlines()
    if not remote_name:
        return None
    url = _run(["git", "remote", "get-url", remote_name[0]]).stdout.strip()
    match = re.match(r"https://(?:[^@]+@)?github\.com/(.+)", url)
    if not match:
        return None
    return f"https://{token}@github.com/{match.group(1)}"


def save_to_git(message: str | None = None, github_token: str | None = None) -> None:
    """Ajoute tous les changements, commit et push vers le remote courant.

    Ne fait rien (et le signale) si aucun changement n'est detecte, pour
    eviter les commits vides.

    `github_token` (ou la variable d'environnement GITHUB_TOKEN) est necessaire
    pour le push si le depot est prive, ou si l'environnement (ex: Colab) n'a
    pas d'identifiants git deja enregistres. Un token se cree sur
    https://github.com/settings/tokens (droit "repo" suffit).
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

    token = github_token or os.environ.get("GITHUB_TOKEN")
    push_cmd = ["git", "push"]
    if token:
        auth_url = _push_url_with_token(token)
        if auth_url:
            branch = _run(["git", "branch", "--show-current"]).stdout.strip()
            push_cmd = ["git", "push", auth_url, branch]

    push = _run(push_cmd)
    if push.returncode != 0:
        print(push.stdout, push.stderr)
        raise RuntimeError(
            "Echec de 'git push' : authentification GitHub necessaire. "
            "Passe un token via save_to_git(message, github_token=...) "
            "ou la variable d'environnement GITHUB_TOKEN "
            "(cree un token sur https://github.com/settings/tokens, droit 'repo')."
        )
    print("[save_to_git] Push effectue avec succes.")


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    save_to_git(msg)
