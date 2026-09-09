# Framework de Governanca de Dados

Este documento define os papeis, responsabilidades e politicas que
regem os datasets catalogados neste repositorio - aplicados
retroativamente aos Projetos 01-06 do portfolio.

## Papeis

| Papel | Responsabilidade |
|---|---|
| **Data Owner** | Responsavel final pelo dataset: aprova mudancas de schema, decide classificacao de sensibilidade, autoriza exclusao. |
| **Data Steward** | Garante qualidade e documentacao: mantem o YAML do dataset atualizado, roda e acompanha as checagens de qualidade (Projeto 06). |
| **Data Consumer** | Consome o dataset (dashboards, relatorios, outros pipelines) - reporta problemas de qualidade ao Steward, nao tem permissao de alterar schema. |

Neste portfolio, uma unica pessoa acumula os tres papeis - isso e
documentado explicitamente, nao escondido. Em um time real, a
separacao entre Owner e Steward evita que a mesma pessoa que decide
"o que o dado deveria ser" seja a unica verificando "o dado esta
correto".

## Matriz RACI por tipo de decisao

R = Responsavel (executa) · A = Aprova (autoridade final) · C = Consultado · I = Informado

| Decisao | Data Owner | Data Steward | Data Consumer |
|---|---|---|---|
| Mudanca de schema (nova coluna) | A | R | I |
| Mudanca de schema (remocao/tipo) | A | R | C |
| Exclusao de dataset | A | C | I |
| Alteracao de classificacao de sensibilidade | A | R | I |
| Alteracao de politica de retencao | A | R | I |
| Reporte de problema de qualidade | I | R | R |

Mudancas destrutivas de schema (remocao, troca de tipo) tem o
Consumer como Consultado, nao apenas Informado - e exatamente o tipo
de mudanca que quebra pipelines downstream sem aviso, o mesmo
raciocinio documentado no ADR 0009 do repositorio de arquitetura
deste portfolio.

## Politica de retencao

A retencao e definida por camada, nao por dataset individual, com
justificativa proporcional ao papel de cada camada:

| Camada | Retencao padrao | Justificativa |
|---|---|---|
| Bronze | 5 anos (1825 dias) | E a trilha de auditoria - "o que recebemos e quando". Reter mais tempo permite reprocessamento completo se uma regra de transformacao mudar (ver ADR 0002). |
| Silver | 2 anos (730 dias) | Dado ja validado e deduplicado; retencao menor que Bronze porque pode ser reconstruido a partir dela se necessario. |
| Gold | 1 ano (365 dias) | Camada de consumo direto - retencao alinhada ao ciclo de reporting mais comum (anual). |
| Report | 30 a 90 dias | Relatorios de qualidade e narrativas de IA sao artefatos operacionais, nao historicos - tem valor decrescente rapido apos a checagem que os gerou ser revisada. |

Estes numeros sao os aplicados nos YAMLs de `catalog/datasets/` e
podem ser consultados por dataset especifico la.

## Fluxo de revisao

Cada dataset tem um campo `last_reviewed` (formato AAAA-MM). A
expectativa e que datasets Gold e Report sejam revisados a cada
trimestre (maior exposicao a consumidores), e datasets Bronze/Silver
a cada semestre - refletindo que mudancas na fonte (OpenAQ) tendem a
se propagar e ficar visiveis primeiro nas camadas de consumo.
