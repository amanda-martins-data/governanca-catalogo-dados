"""
lineage.py
-----------
Monta o grafo de linhagem entre datasets do catalogo (quem depende de
quem) e valida esse grafo, procurando dois tipos de problema:

1. Referencia quebrada: um dataset declara um upstream que nao existe
   no catalogo (typo, dataset removido, etc.).
2. Upstream ausente indevido: um dataset de camada Silver, Gold ou
   Report sem nenhum upstream declarado - camadas derivadas deveriam
   sempre apontar de onde vieram. Bronze e a unica camada em que uma
   lista de upstream vazia e esperada (e a fonte primaria).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LineageIssue:
    dataset: str
    kind: str  # "broken_reference" ou "missing_upstream"
    detail: str


def build_downstream_map(datasets: list[dict]) -> dict[str, list[str]]:
    """Inverte a relacao upstream -> devolve, para cada dataset, a
    lista de datasets que dependem dele (downstream)."""
    downstream: dict[str, list[str]] = {d["name"]: [] for d in datasets}

    for dataset in datasets:
        for upstream_name in dataset.get("upstream", []):
            if upstream_name in downstream:
                downstream[upstream_name].append(dataset["name"])

    return downstream


def validate_lineage(datasets: list[dict]) -> list[LineageIssue]:
    """Roda as duas checagens de consistencia do grafo de linhagem."""
    issues: list[LineageIssue] = []
    known_names = {d["name"] for d in datasets}

    for dataset in datasets:
        name = dataset["name"]
        layer = dataset.get("layer")
        upstream = dataset.get("upstream", [])

        for upstream_name in upstream:
            if upstream_name not in known_names:
                issues.append(
                    LineageIssue(
                        dataset=name,
                        kind="broken_reference",
                        detail=f"upstream '{upstream_name}' nao existe no catalogo",
                    )
                )

        if layer != "Bronze" and not upstream:
            issues.append(
                LineageIssue(
                    dataset=name,
                    kind="missing_upstream",
                    detail=f"camada '{layer}' sem nenhum upstream declarado",
                )
            )

    return issues


def build_lineage_chain(dataset_name: str, datasets_by_name: dict[str, dict]) -> list[str]:
    """Retorna a cadeia completa de upstream de um dataset, da fonte
    primaria ate o dataset informado (inclusive), na ordem em que os
    dados fluem. Detecta ciclos para nao entrar em loop infinito."""
    chain: list[str] = []
    visited: set[str] = set()

    def walk(name: str) -> None:
        if name in visited:
            return  # protege contra ciclo no grafo
        visited.add(name)

        dataset = datasets_by_name.get(name)
        if dataset is None:
            return

        for upstream_name in dataset.get("upstream", []):
            walk(upstream_name)

        if name not in chain:
            chain.append(name)

    walk(dataset_name)
    return chain
