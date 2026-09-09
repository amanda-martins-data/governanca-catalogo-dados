"""
Testes de lineage.py - 100% offline, sem dependencia de arquivo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from lineage import build_downstream_map, build_lineage_chain, validate_lineage


def test_validate_lineage_detects_broken_reference():
    datasets = [
        {"name": "a", "layer": "Bronze", "upstream": []},
        {"name": "b", "layer": "Silver", "upstream": ["nao_existe"]},
    ]

    issues = validate_lineage(datasets)

    assert len(issues) == 1
    assert issues[0].dataset == "b"
    assert issues[0].kind == "broken_reference"


def test_validate_lineage_detects_missing_upstream_for_non_bronze():
    datasets = [
        {"name": "c", "layer": "Silver", "upstream": []},
    ]

    issues = validate_lineage(datasets)

    assert len(issues) == 1
    assert issues[0].kind == "missing_upstream"


def test_validate_lineage_allows_bronze_without_upstream():
    datasets = [
        {"name": "a", "layer": "Bronze", "upstream": []},
    ]

    issues = validate_lineage(datasets)

    assert issues == []


def test_validate_lineage_clean_graph_has_no_issues():
    datasets = [
        {"name": "a", "layer": "Bronze", "upstream": []},
        {"name": "b", "layer": "Silver", "upstream": ["a"]},
        {"name": "c", "layer": "Gold", "upstream": ["b"]},
    ]

    issues = validate_lineage(datasets)

    assert issues == []


def test_build_downstream_map():
    datasets = [
        {"name": "a", "layer": "Bronze", "upstream": []},
        {"name": "b", "layer": "Silver", "upstream": ["a"]},
        {"name": "c", "layer": "Gold", "upstream": ["b"]},
    ]

    downstream = build_downstream_map(datasets)

    assert downstream["a"] == ["b"]
    assert downstream["b"] == ["c"]
    assert downstream["c"] == []


def test_build_lineage_chain_follows_full_path():
    datasets = [
        {"name": "a", "layer": "Bronze", "upstream": []},
        {"name": "b", "layer": "Silver", "upstream": ["a"]},
        {"name": "c", "layer": "Gold", "upstream": ["b"]},
    ]
    by_name = {d["name"]: d for d in datasets}

    chain = build_lineage_chain("c", by_name)

    assert chain == ["a", "b", "c"]


def test_build_lineage_chain_handles_single_source_dataset():
    datasets = [{"name": "a", "layer": "Bronze", "upstream": []}]
    by_name = {d["name"]: d for d in datasets}

    chain = build_lineage_chain("a", by_name)

    assert chain == ["a"]


def test_build_lineage_chain_does_not_loop_on_cycle():
    """Um grafo com ciclo nao deveria existir na pratica, mas a funcao
    precisa terminar (nao entrar em loop infinito) mesmo assim."""
    datasets = [
        {"name": "a", "layer": "Silver", "upstream": ["b"]},
        {"name": "b", "layer": "Silver", "upstream": ["a"]},
    ]
    by_name = {d["name"]: d for d in datasets}

    chain = build_lineage_chain("a", by_name)

    assert set(chain) == {"a", "b"}
