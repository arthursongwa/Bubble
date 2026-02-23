"""Lance ce fichier pour diagnostiquer le registry et le drag & drop."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== 1. Contenu du dossier blocks/ ===")
import pkgutil, blocks
for finder, name, ispkg in pkgutil.iter_modules(blocks.__path__):
    print(f"  fichier trouvé : {name}")

print("\n=== 2. Import manuel de chaque bloc ===")
for finder, name, ispkg in pkgutil.iter_modules(blocks.__path__):
    if name.startswith("_"):
        print(f"  {name} → ignoré (commence par _)")
        continue
    try:
        import importlib
        module = importlib.import_module(f"blocks.{name}")
        print(f"  blocks.{name} → importé OK")
        for attr_name in dir(module):
            cls = getattr(module, attr_name)
            if isinstance(cls, type):
                print(f"    classe trouvée : {attr_name} | __module__={getattr(cls,'__module__','?')} | module attendu=blocks.{name}")
    except Exception as e:
        print(f"  blocks.{name} → ERREUR : {e}")

print("\n=== 3. Version Python ===")
print(f"  {sys.version}")