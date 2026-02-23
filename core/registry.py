"""
Registry des blocs - decouverte automatique.
Tous les fichiers dans /blocks/ sont scannes.
Les fichiers commencant par _ sont ignores.
"""

import importlib
import pkgutil
import blocks
from core.base_block import BaseBlock

_registry = {}


def discover():
    print("[Registry] Scan du dossier blocks/...")
    
    modules_found = list(pkgutil.iter_modules(blocks.__path__))
    print(f"[Registry] {len(modules_found)} fichier(s) detecte(s) : {[m.name for m in modules_found]}")

    for finder, name, ispkg in modules_found:
        # Ignore templates et fichiers prives
        if name.startswith("_"):
            print(f"[Registry] Ignore : {name} (commence par _)")
            continue

        try:
            module = importlib.import_module(f"blocks.{name}")
            print(f"[Registry] Module charge : blocks.{name}")
        except Exception as e:
            print(f"[Registry] ERREUR import blocks.{name} : {e}")
            import traceback; traceback.print_exc()
            continue

        registered = 0
        for attr_name in dir(module):
            try:
                cls = getattr(module, attr_name)
            except Exception:
                continue

            if not isinstance(cls, type):
                continue
            if cls is BaseBlock:
                continue
            if not issubclass(cls, BaseBlock):
                continue

            # Evite d'enregistrer deux fois le meme BLOCK_ID
            bid = getattr(cls, "BLOCK_ID", None)
            if not bid:
                continue
            if bid in _registry:
                print(f"[Registry] Doublon ignore : '{bid}' (deja enregistre par {_registry[bid].__name__})")
                continue

            _registry[bid] = cls
            print(f"[Registry] OK enregistre : '{bid}' -> {cls.__name__}")
            registered += 1

        if registered == 0:
            print(f"[Registry] Aucune classe BaseBlock trouvee dans blocks.{name}")

    print(f"[Registry] Total : {len(_registry)} bloc(s) -> {list(_registry.keys())}")
    return _registry


def get(block_id):
    return _registry.get(block_id)


def all_blocks():
    return dict(_registry)