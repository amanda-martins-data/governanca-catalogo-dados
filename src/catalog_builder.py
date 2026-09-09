"""
catalog_builder.py
--------------------
Le os arquivos YAML em catalog/datasets/, valida cada um contra o
contrato definido em catalog/schema.yaml, e gera uma pagina HTML
estatica e autocontida com o catalogo completo - agrupado por
projeto, com badge de sensibilidade e a cadeia de linhagem de cada
dataset.

Nao usa nenhum emoji: sensibilidade e comunicada por texto e cor,
seguindo a mesma decisao de design do Projeto 06.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

from lineage import build_lineage_chain, validate_lineage

REQUIRED_FIELDS = [
    "name",
    "layer",
    "project",
    "owner",
    "description",
    "upstream",
    "sensitivity",
    "retention_days",
    "pii_fields",
    "last_reviewed",
]

VALID_LAYERS = {"Bronze", "Silver", "Gold", "Report"}
VALID_SENSITIVITY = {"public", "internal", "confidential", "personal"}


@dataclass
class ValidationError:
    dataset_file: str
    message: str


def load_datasets(datasets_dir: Path) -> tuple[list[dict], list[ValidationError]]:
    """Le todos os .yaml de datasets_dir, retornando os datasets
    validos e a lista de erros de validacao encontrados. Um dataset
    com erro nao entra na lista de datasets validos."""
    datasets: list[dict] = []
    errors: list[ValidationError] = []

    for path in sorted(datasets_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        file_errors = validate_dataset(data, path.name)

        if file_errors:
            errors.extend(ValidationError(dataset_file=path.name, message=m) for m in file_errors)
        else:
            datasets.append(data)

    return datasets, errors


def validate_dataset(data: dict, filename: str) -> list[str]:
    """Valida um dataset contra o contrato. Retorna a lista de erros
    encontrados (lista vazia = dataset valido)."""
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["conteudo do arquivo nao e um mapeamento YAML valido"]

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"campo obrigatorio ausente: '{field}'")

    if "layer" in data and data["layer"] not in VALID_LAYERS:
        errors.append(f"layer '{data['layer']}' invalida - deve ser uma de {sorted(VALID_LAYERS)}")

    if "sensitivity" in data and data["sensitivity"] not in VALID_SENSITIVITY:
        errors.append(f"sensitivity '{data['sensitivity']}' invalida - deve ser uma de {sorted(VALID_SENSITIVITY)}")

    if "upstream" in data and not isinstance(data["upstream"], list):
        errors.append("campo 'upstream' deve ser uma lista (mesmo que vazia)")

    return errors


_STYLE = """
body { font-family: -apple-system, Segoe UI, Arial, sans-serif; margin: 2rem; background: #0f1115; color: #e6e6e6; }
h1 { font-size: 1.4rem; margin-bottom: 0.25rem; }
h2 { font-size: 1.1rem; margin-top: 2rem; border-bottom: 1px solid #2a2d34; padding-bottom: 0.4rem; }
.subtitle { color: #9aa0a6; margin-bottom: 1.5rem; font-size: 0.9rem; }
.dataset { border: 1px solid #2a2d34; border-radius: 8px; padding: 1rem; margin: 0.8rem 0; }
.dataset-name { font-size: 1rem; font-weight: 600; }
.dataset-desc { color: #c7c9cc; font-size: 0.9rem; margin: 0.4rem 0; }
.meta-row { font-size: 0.8rem; color: #9aa0a6; margin-top: 0.5rem; }
.badge { font-weight: 600; padding: 0.1rem 0.5rem; border-radius: 4px; display: inline-block; font-size: 0.75rem; }
.badge.public { color: #4caf50; background: rgba(76, 175, 80, 0.12); }
.badge.internal { color: #e0a952; background: rgba(224, 169, 82, 0.12); }
.badge.confidential { color: #e0725a; background: rgba(224, 114, 90, 0.12); }
.badge.personal { color: #e05252; background: rgba(224, 82, 82, 0.15); }
.layer-tag { color: #7aa2f7; font-size: 0.75rem; text-transform: uppercase; }
.lineage { font-size: 0.8rem; color: #9aa0a6; margin-top: 0.5rem; }
.lineage code { color: #c7c9cc; }
.errors { border: 1px solid #e05252; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; }
.errors h2 { border: none; margin-top: 0; color: #e05252; }
"""


def generate_html_catalog(
    datasets: list[dict],
    errors: list[ValidationError],
    generated_at: datetime | None = None,
) -> str:
    generated_at = generated_at or datetime.now()
    datasets_by_name = {d["name"]: d for d in datasets}
    lineage_issues = validate_lineage(datasets)

    projects = sorted({d["project"] for d in datasets})

    sections = []
    for project in projects:
        project_datasets = [d for d in datasets if d["project"] == project]
        cards = []
        for d in project_datasets:
            chain = build_lineage_chain(d["name"], datasets_by_name)
            lineage_str = " -> ".join(chain) if len(chain) > 1 else "(fonte primaria)"
            cards.append(
                f"""
                <div class="dataset">
                    <div class="layer-tag">{d['layer']}</div>
                    <div class="dataset-name">{d['name']}</div>
                    <div class="dataset-desc">{d['description']}</div>
                    <div class="meta-row">
                        <span class="badge {d['sensitivity']}">{d['sensitivity']}</span>
                        &nbsp;retencao: {d['retention_days']} dias
                        &nbsp;dono: {d['owner']}
                        &nbsp;revisado: {d['last_reviewed']}
                    </div>
                    <div class="lineage">linhagem: <code>{lineage_str}</code></div>
                </div>
                """
            )
        sections.append(f"<h2>{project}</h2>{''.join(cards)}")

    error_block = ""
    all_problems = [f"{e.dataset_file}: {e.message}" for e in errors] + [
        f"{i.dataset}: {i.detail}" for i in lineage_issues
    ]
    if all_problems:
        items = "".join(f"<li>{p}</li>" for p in all_problems)
        error_block = f'<div class="errors"><h2>Problemas encontrados ({len(all_problems)})</h2><ul>{items}</ul></div>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<title>Catalogo de Dados</title>
<style>{_STYLE}</style>
</head>
<body>
<h1>Catalogo de Dados - Portfolio</h1>
<div class="subtitle">Gerado em {generated_at.strftime('%Y-%m-%d %H:%M:%S')} - {len(datasets)} datasets catalogados</div>
{error_block}
{''.join(sections)}
</body>
</html>
"""


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    datasets_dir = root / "catalog" / "datasets"
    out_dir = root / "out"
    out_dir.mkdir(exist_ok=True)

    datasets, errors = load_datasets(datasets_dir)
    html = generate_html_catalog(datasets, errors)

    out_path = out_dir / "catalog.html"
    out_path.write_text(html, encoding="utf-8")

    print(f"Catalogados: {len(datasets)} datasets validos, {len(errors)} com erro de validacao.")
    print(f"Catalogo escrito em {out_path}")


if __name__ == "__main__":
    main()
