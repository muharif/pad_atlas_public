from pathlib import Path

for file in [
    "pad_atlas_public/__init__.py",
    "pad_atlas_public/utils/__init__.py",
    "pad_atlas_public/pages/__init__.py",
    "pad_atlas_public/components/__init__.py",
]:
    Path(file).touch(exist_ok=True)

print("Package files created.")
