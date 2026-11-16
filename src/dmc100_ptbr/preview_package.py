"""Package only allowlisted authorial browser assets; never read private files."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ASSETS = (
    "index.html", "lab.html", "gallery.html", "reference-gallery.html",
    "app.js", "catalog.js", "model.js", "navigation.js", "navigation-catalog.js",
    "navigator-app.js", "reference-renderer.js", "gallery.js", "reference-gallery.js",
    "style.css", "navigator.css", "gallery.css",
)
START = """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DMC100-PTBR — versão testável no computador</title>
<h1>DMC100-PTBR · alfa offline 1</h1>
<p>Protótipo visual autoral de 240 × 320 pixels. Leituras fictícias.
Não contém firmware, não emula o aparelho e não acessa USB.</p>
<p><a href="simulator/index.html">Abrir simulador e comparar inglês/PT-BR</a></p>
<p><a href="simulator/lab.html">Testar fontes, abreviações e acentos</a></p>
<p><a href="simulator/reference-gallery.html">Ver quatro telas lado a lado</a></p>
<h2>Roteiro de teste</h2><ol>
<li>Extraia todo o ZIP antes de abrir esta página.</li>
<li>No simulador, abra Configurações → Idioma → Português (BR) → Confirmar.</li>
<li>Use “Seguir idioma escolhido no menu” para conferir a troca.</li>
<li>Repita a seleção e cancele: o idioma ativo deve permanecer.</li>
<li>Volte ao inglês; compare Medição, Histórico, Configurações e Sobre.</li>
<li>Na bancada, experimente 12/16/24/32 px e as variantes com/sem acentos.</li>
<li>Recarregue: o estado é volátil e volta ao inglês.</li></ol>
<p>Setas navegam, Enter confirma, Esc volta. Compare com o aparelho apenas
visualmente, sem conectá-lo ao computador. Anote tela, ação, idioma,
tamanho da fonte, esperado e observado ao relatar um problema.</p>
<h2>Limites</h2><p>Fontes são do computador. Acentos no navegador não provam
suporte no firmware. A CPU virtual ARM é um ensaio de desenvolvimento separado;
esta página não executa ARM. Não há instalação no multímetro.</p></html>
"""


def build(repository: Path, destination: Path) -> dict:
    sources = {name: repository / "simulator" / name for name in ASSETS}
    sources["LICENSE"] = repository / "LICENSE"
    # Validate all inputs before creating an archive. No recursive enumeration.
    contents = {}
    root = repository.resolve()
    for name, path in sources.items():
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            raise ValueError("Package source escapes repository or is a symlink")
        target = name if name == "LICENSE" else "simulator/" + name
        contents[target] = path.read_bytes()
    contents["ABRIR.html"] = START.encode("utf-8")
    manifest = {"version": "offline-alpha-1", "scope": "Authorial browser prototype",
                "firmware_included": False, "device_access": False,
                "files": {name: hashlib.sha256(data).hexdigest()
                          for name, data in sorted(contents.items())}}
    contents["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    if destination.suffix.lower() != ".zip":
        raise ValueError("Output must be a ZIP archive")
    if destination.resolve().is_relative_to(root):
        raise ValueError("Write deliverables outside the source repository")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(contents.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 11, 16, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    build(Path(__file__).resolve().parents[2], args.destination)
    print(str(args.destination.resolve()))


if __name__ == "__main__":
    main()
