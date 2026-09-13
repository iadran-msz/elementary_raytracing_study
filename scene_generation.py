"""Generation d'une scene Mitsuba 3 simple sous forme de dictionnaire Python.

Ce module ne fait aucun rendu : il construit uniquement le scene dict,
pour que le notebook `results.ipynb` (ou tout autre script) puisse
l'importer, le charger avec `mitsuba.load_dict(...)` et faire le rendu.
"""

import mitsuba_config  # noqa: F401  (active la variante Mitsuba configuree pour cette machine)
import mitsuba as mi


def make_simple_scene(sphere_radius: float = 1.0, resolution: int = 256) -> dict:
    """Construit une scene simple : une sphere sur un plan, eclairee par un point light.

    Parameters
    ----------
    sphere_radius : rayon de la sphere centrale.
    resolution : resolution (carree) du film de la camera.

    Returns
    -------
    dict compatible avec mitsuba.load_dict().
    """
    scene = {
        "type": "scene",
        "integrator": {"type": "path"},
        "sensor": {
            "type": "perspective",
            "fov": 39.3,
            "to_world": mi.ScalarTransform4f().look_at(
                origin=[0, 0, 4],
                target=[0, 0, 0],
                up=[0, 1, 0],
            ),
            "sampler": {
                "type": "independent",
                "sample_count": 64,
            },
            "film": {
                "type": "hdrfilm",
                "width": resolution,
                "height": resolution,
                "rfilter": {"type": "gaussian"},
            },
        },
        "light": {
            "type": "point",
            "position": [3, 3, 3],
            "intensity": {"type": "spectrum", "value": 30.0},
        },
        "floor": {
            "type": "rectangle",
            "to_world": mi.ScalarTransform4f().translate([0, -sphere_radius, 0])
            .rotate(axis=[1, 0, 0], angle=-90)
            .scale(5.0),
            "bsdf": {
                "type": "diffuse",
                "reflectance": {"type": "rgb", "value": [0.8, 0.8, 0.8]},
            },
        },
        "sphere": {
            "type": "sphere",
            "radius": sphere_radius,
            "bsdf": {
                "type": "diffuse",
                "reflectance": {"type": "rgb", "value": [0.9, 0.2, 0.2]},
            },
        },
    }
    return scene


def render_scene(scene_dict: dict):
    """Charge un scene dict et effectue le rendu. Retourne un mitsuba.Bitmap."""
    scene = mi.load_dict(scene_dict)
    return mi.render(scene)


if __name__ == "__main__":
    scene_dict = make_simple_scene()
    image = render_scene(scene_dict)
    mi.util.write_bitmap("render_output.png", image)
    print("Rendu enregistre dans render_output.png")
