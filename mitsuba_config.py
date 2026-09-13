"""Point unique de configuration de la variante Mitsuba pour tout le projet.

A importer en tout premier, avant tout autre usage de mitsuba :

    import mitsuba_config  # active la bonne variante
    import mitsuba as mi

Pour changer de machine : commente/decommente la ligne correspondante
ci-dessous, une seule fois, ici. Tous les scripts et notebooks du projet
qui font `import mitsuba_config` recuperent automatiquement le changement.
"""

import mitsuba as mi

# mi.set_variant("scalar_rgb")     # generique, sans acceleration (fonctionne partout)
mi.set_variant("llvm_ad_rgb")      # PC Linux (CPU, avec autodiff)
# mi.set_variant("cuda_ad_rgb")    # Google Colab (GPU, avec autodiff)
