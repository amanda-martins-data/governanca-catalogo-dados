# Classificacao de Dados e LGPD

## Categorias de sensibilidade

Cada dataset catalogado declara um campo `sensitivity`, com quatro
valores possiveis:

| Categoria | Definicao | Exemplo neste portfolio |
|---|---|---|
| `public` | Pode ser divulgado sem restricao - nenhum dado que identifique pessoas ou exponha informacao competitiva. | Dados de qualidade do ar por cidade (Bronze, Silver, Gold) |
| `internal` | Uso interno da organizacao - nao e secreto, mas nao deveria ser publicado externamente sem revisao. | Relatorios de qualidade de dados, narrativas geradas por IA |
| `confidential` | Informacao sensivel para o negocio (ex.: contratos, precos negociados, credenciais). | Nao existe neste portfolio - categoria documentada por completude |
| `personal` | Dado pessoal na definicao da LGPD (Lei 13.709/2018) - qualquer informacao relacionada a pessoa natural identificada ou identificavel. | Nao existe neste portfolio - dados sao agregados por cidade/poluente, nunca por individuo |

Nenhum dataset deste portfolio contem dado pessoal - os dados de
qualidade do ar sao inerentemente agregados (cidade, poluente, dia),
sem qualquer vinculo a uma pessoa fisica. A categoria `personal`
esta documentada mesmo assim, porque uma classificacao de
sensibilidade que so lista as categorias que o projeto atual usa nao
serve como framework reutilizavel para um proximo projeto que venha
a ter dado pessoal de verdade.

## Por que declarar isso explicitamente importa

E comum um portfolio de dados nunca mencionar sensibilidade ou LGPD
simplesmente porque os dados de exemplo sao publicos - o que faz
parecer que o autor nunca pensou no assunto, nao que o assunto nao
se aplica. Declarar `sensitivity: public` e `pii_fields: []`
explicitamente em cada YAML (em vez de simplesmente omitir o campo)
e a diferenca entre "essa pessoa nunca considerou LGPD" e "essa
pessoa considerou e concluiu, de forma documentada, que nao se
aplica aqui".

## Campo `pii_fields`

Cada dataset tambem declara `pii_fields`, uma lista dos campos que
seriam dado pessoal (LGPD) se existissem no dataset. Em todos os
datasets deste portfolio a lista esta vazia - mas o campo existe
propositalmente no contrato (`catalog/schema.yaml`) como um lembrete
estrutural: ao adicionar um dataset novo, quem preenche o YAML e
forcado a parar e responder "isso tem dado pessoal?" em vez de essa
pergunta nunca ser feita.

Se um dataset futuro deste portfolio viesse a conter, por exemplo,
o e-mail de quem se inscreve para receber alertas de qualidade do
ar, o YAML correspondente declararia:

```yaml
sensitivity: personal
pii_fields: ["email", "nome_completo"]
retention_days: 180  # LGPD: retencao deve ser proporcional a finalidade
```

## Bases legais da LGPD relevantes para um pipeline de dados ambientais

Ainda que este portfolio nao processe dado pessoal, o raciocinio de
base legal e o mesmo exigido em qualquer projeto de dados no Brasil.
As bases mais aplicaveis a um cenario futuro de alertas
personalizados seriam:

- **Legitimo interesse** (Art. 7º, IX): para o processamento minimo
  necessario a operacao de um alerta que o proprio titular solicitou.
- **Consentimento** (Art. 7º, I): para qualquer uso que va alem da
  finalidade original (ex.: usar o e-mail de alerta para outra
  comunicacao).
- **Cumprimento de obrigacao legal ou regulatoria** (Art. 7º, II):
  relevante se o dado de qualidade do ar viesse a alimentar um
  relatorio ambiental obrigatorio (paralelo direto aos relatorios
  GRI e disclosures ESG ja produzidos profissionalmente fora deste
  portfolio).
