"""Point unique de configuration de la variante Mitsuba pour tout le projet.

A importer en tout premier, avant tout autre usage de mitsuba :

    import mitsuba_config  # active automatiquement la meilleure variante
    import mitsuba as mi

La variante est choisie automatiquement selon ce qui est reellement
utilisable sur la machine (comme `torch.cuda.is_available()` avec PyTorch) :
CUDA si un GPU compatible est detecte (typiquement Colab), sinon LLVM (CPU,
typiquement le PC Linux), sinon la variante generique scalar_rgb (fonctionne
toujours, sans acceleration).
"""

import mitsuba as mi

_available = mi.variants()


def _try_variant(name: str) -> bool:
    """Essaie d'activer une variante et de creer un objet dessus (test reel,
    pas juste la presence dans mi.variants()). Retourne True si ca marche."""
    if name not in _available:
        return False
    try:
        mi.set_variant(name)
        mi.Float(0.0)  # force l'initialisation du backend (CUDA/LLVM)
        return True
    except Exception:
        return False


if _try_variant("cuda_ad_rgb"):
    variant = "cuda_ad_rgb"
elif _try_variant("llvm_ad_rgb"):
    variant = "llvm_ad_rgb"
else:
    variant = "scalar_rgb"
    mi.set_variant(variant)

print(f"[mitsuba_config] variante activee : {variant}")
