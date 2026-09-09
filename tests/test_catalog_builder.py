"""
Testes de catalog_builder.py - cobrem validacao de dataset, geracao
de HTML, e a carga real dos 8 YAMLs do catalogo deste portfolio.
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from catalog_builder import generate_html_catalog, load_datasets, validate_dataset

VALID_DATASET = {
    "name": "x",
    "layer": "Bronze",
    "project": "p",
    "owner": "o",
    "description": "d",
    "upstream": [],
    "sensitivity": "public",
    "retention_days": 1,
    "pii_fields": [],
    "last_reviewed": "2026-01",
}


def test_validate_dataset_accepts_valid_dataset():
    errors = validate_dataset(VALID_DATASET, "x.yaml")

    assert errors == []


def test_validate_dataset_flags_missing_required_fields():
    errors = validate_dataset({"name": "x"}, "x.yaml")

    assert any("layer" in e for e in errors)
    assert any("owner" in e for e in errors)
    assert len(errors) == 9  # todos os campos obrigatorios menos 'name'


def test_validate_dataset_flags_invalid_layer():
    bad = {**VALID_DATASET, "layer": "Diamond"}

    errors = validate_dataset(bad, "x.yaml")

    assert any("layer" in e for e in errors)


def test_validate_dataset_flags_invalid_sensitivity():
    bad = {**VALID_DATASET, "sensitivity": "top-secret"}

    errors = validate_dataset(bad, "x.yaml")

    assert any("sensitivity" in e for e in errors)


def test_validate_dataset_flags_upstream_not_a_list():
    bad = {**VALID_DATASET, "upstream": "air_quality_bronze"}

    errors = validate_dataset(bad, "x.yaml")

    assert any("upstream" in e for e in errors)


def test_validate_dataset_rejects_non_mapping_content():
    errors = validate_dataset(["nao", "e", "um", "dict"], "x.yaml")

    assert len(errors) == 1
    assert "mapeamento" in errors[0]


def test_load_real_portfolio_datasets():
    """Carrega os 8 YAMLs reais do catalogo deste portfolio e confirma
    que todos passam na validacao, sem nenhum erro."""
    datasets_dir = Path(__file__).resolve().parent.parent / "catalog" / "datasets"

    datasets, errors = load_datasets(datasets_dir)

    assert errors == []
    assert len(datasets) == 8
    names = {d["name"] for d in datasets}
    assert "air_quality_bronze" in names
    assert "rds_air_quality_daily" in names


def test_generate_html_catalog_includes_all_datasets():
    datasets_dir = Path(__file__).resolve().parent.parent / "catalog" / "datasets"
    datasets, errors = load_datasets(datasets_dir)

    html = generate_html_catalog(datasets, errors, generated_at=datetime(2026, 1, 5))

    for d in datasets:
        assert d["name"] in html


def test_generate_html_catalog_shows_lineage_chain():
    datasets_dir = Path(__file__).resolve().parent.parent / "catalog" / "datasets"
    datasets, errors = load_datasets(datasets_dir)

    html = generate_html_catalog(datasets, errors)

    assert "air_quality_bronze -&gt; air_quality_silver" in html or "air_quality_bronze -> air_quality_silver" in html


def test_generate_html_catalog_reports_lineage_issues():
    datasets = [
        {**VALID_DATASET, "name": "a", "layer": "Bronze", "upstream": []},
        {**VALID_DATASET, "name": "b", "layer": "Silver", "upstream": ["nao_existe"]},
    ]

    html = generate_html_catalog(datasets, errors=[])

    assert "broken_reference" not in html  # o texto tecnico nao aparece, so o detalhe legivel
    assert "nao existe no catalogo" in html


def test_generate_html_catalog_contains_no_emoji():
    datasets_dir = Path(__file__).resolve().parent.parent / "catalog" / "datasets"
    datasets, errors = load_datasets(datasets_dir)

    html = generate_html_catalog(datasets, errors)

    assert all(ord(ch) < 0x1F000 for ch in html)
