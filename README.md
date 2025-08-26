# Odontologia no DF — Análise, Comparativos e Dashboard Interativo

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/pandas-2.x-150458.svg)](https://pandas.pydata.org/)
[![Matplotlib](https://img.shields.io/badge/matplotlib-3.x-0b5b8a.svg)](https://matplotlib.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#licença)
[![Made with ❤️ in DF](https://img.shields.io/badge/made%20in-DF-red.svg)](#autor)

> Estudo de dados do CRO (2010–último ano disponível) sobre **profissionais e entidades** da odontologia, com foco no **Distrito Federal (DF)** e comparação com outras UFs do Brasil. O repo traz **código de análise**, **gráficos prontos** e um **dashboard interativo** em HTML para explorar as séries (inclui linha do **Brasil** e seleção de **todas as UFs**).

---

## Sumário

- [Contexto](#contexto)
- [Arquivos e Estrutura](#arquivos-e-estrutura)
- [Como Rodar a Análise (Python)](#como-rodar-a-análise-python)
- [Dashboard Interativo (HTML)](#dashboard-interativo-html)
- [O que Você Vai Encontrar](#o-que-você-vai-encontrar)
- [Dicionário de Dados e Observações](#dicionário-de-dados-e-observações)
- [Metodologia de Métricas](#metodologia-de-métricas)
- [Limitações Importantes](#limitações-importantes)
- [Roadmap](#roadmap)
- [Como Contribuir](#como-contribuir)
- [Licença](#licença)
- [Autor](#autor)

---

## Contexto

Este repositório ajuda a responder: **como evoluiu o mercado odontológico no DF desde 2010?** Quem puxa o crescimento? Como o DF se compara ao Brasil e a outras UFs? O projeto combina:

- **Dataset do CRO** (contagens por UF, ano e categoria);
- **Análises e gráficos** em Python;
- **Dashboard interativo** (HTML + Chart.js) para explorar séries temporais, **composição** (mix de categorias), **YoY** e **CAGR**;
- Ponto de vista prático: recomendações simples para profissionais e gestores, e uma visão do **“paradoxo”** (muita oferta privada × carência na rede pública).

---

## Arquivos e Estrutura

```
.
├─ analysis_odonto_df.py                 # script principal de análise (gera CSVs e PNGs)
├─ dashboard_odonto_df.html              # dashboard interativo (abre no navegador)
├─ Download (1).csv                      # dataset bruto (sem cabeçalho) [uf, ano, sigla, quantidade]
│
├─ resumo_uf_por_ano.csv                 # derivado: totais por UF e ano
├─ resumo_brasil_por_ano.csv             # derivado: total Brasil por ano
├─ resumo_uf_categoria_por_ano.csv       # derivado: totais por UF, categoria e ano
├─ ranking_ufs_2025.csv                  # derivado: ranking do último ano
├─ mix_df_vs_brasil_2025.csv             # derivado: % por categoria — DF vs Brasil (último ano)
├─ yoy_percent_por_uf.csv                # derivado: variação YoY (%) por UF
│
├─ br_total_por_ano.png                  # Figura 1
├─ top_10_ufs_2025.png                   # Figura 2
├─ evolucao_ufs_selecionadas.png         # Figura 3
├─ df_mix_categorias_2025.png            # Figura 4
├─ heatmap_yoy_ufs_selecionadas.png      # Figura 5
├─ cagr_top_10_ufs.png                   # Figura 6
├─ df_vs_brasil_mix_percent_ultimo_ano.png # Figura 7
├─ br_dentistas_cd_por_ano.png           # Figura 8
├─ df_vs_brasil_total_por_ano.png        # Figura 9
├─ posicao_df_no_ranking_por_ano.png     # Figura 10
├─ df_cagr_top_categorias.png            # Figura 11
│
└─ populacao_uf_ano.csv (opcional)       # uf,ano,populacao — se quiser densidades automáticas
```

> Os CSVs “derivados” são gerados pelo script Python. O HTML do dashboard lê esses arquivos para montar os gráficos interativos.

---

## Como Rodar a Análise (Python)

### 1) Requisitos

- **Python 3.10+**
- Bibliotecas: `pandas`, `numpy`, `matplotlib`

Instale com:

```bash
python -m venv .venv
# Windows
.venv\Scripts\pip install -U pip pandas numpy matplotlib
# macOS/Linux
source .venv/bin/activate && pip install -U pip pandas numpy matplotlib
```

### 2) Dataset bruto

- Coloque `Download (1).csv` na raiz do projeto.
- O arquivo **não tem cabeçalho**. Ordem das colunas: `uf, ano, sigla, quantidade`.

### 3) Execute o script

Atualize o caminho do arquivo no topo do script, se necessário:

```python
ARQUIVO = "Download (1).csv"   # ou o caminho completo no seu PC
```

Rode:

```bash
python analysis_odonto_df.py
```

Saídas geradas automaticamente:
- **CSVs** de resumo (ver lista na estrutura acima)
- **PNGs** (gráficos já prontos)

---

## Dashboard Interativo (HTML)

Arquivo: `dashboard_odonto_df.html`

### Como abrir

> **Opção A (recomendada):** servir localmente (evita bloqueios de leitura de arquivo pelo navegador)

```bash
# Python 3
python -m http.server 8000
# Abra: http://localhost:8000/dashboard_odonto_df.html
```

> **Opção B:** abrir o HTML com duplo clique.  
Alguns navegadores podem bloquear `fetch` de CSV local; se isso acontecer, use a opção A.

### O que dá para fazer no dashboard

- **Selecionar TODAS as UFs** (há botões para “Selecionar todas” / “Limpar seleção”).
- **Ativar a linha do Brasil** para contextualizar os volumes.
- Visualizar **ranking**, **posicionamento histórico do DF**, **composição por categoria** (DF x Brasil), **YoY** por UF/ano (heatmap) e **CAGR**.
- **Paradoxo**: blocos visuais de densidade de dentistas (1:xxx) no DF, Brasil e SUS (com defaults editáveis ou cálculo automático se fornecer `populacao_uf_ano.csv`).

---

## O que Você Vai Encontrar

- **Evolução 2010–último ano**: total de profissionais e entidades, Brasil e DF (Fig. 1 e 9).
- **Comparativos regionais**: ranking do último ano e posição histórica do DF (Fig. 2 e 10).
- **Composição (mix)**: participação de Cirurgiões-Dentistas, ASB/TSB, TPD/APD e Laboratórios (Fig. 4 e 7).
- **Quem puxou o crescimento**: **CAGR por UF** e **CAGR por categoria** no DF (Fig. 6 e 11).
- **Ritmo de curto prazo**: heatmap **YoY** com anos de aceleração/desaceleração (Fig. 5).
- **Paradoxo**: alta oferta privada × lacunas no SUS; densidades 1:xxx configuráveis (blocos no dashboard).

---

## Dicionário de Dados e Observações

**Colunas (dataset bruto `Download (1).csv`):**
- `uf` — sigla da Unidade Federativa (ex.: DF, SP, RJ)
- `ano` — ano calendário
- `sigla` — categoria:
  - `CD` = Cirurgião Dentista  
  - `ASB` = Auxiliar em Saúde Bucal  
  - `TSB` = Técnico em Saúde Bucal  
  - `TPD` = Técnico em Prótese Dentária  
  - `APD` = Auxiliar de Prótese Dentária  
  - `LB` = Laboratório de Prótese Dentária  
  - `EPAO` = Entidade Prestadora de Assistência Odontológica  
  - `ECIPO` = Empresa que comercializa e/ou industrializa produto odontológico
- `quantidade` — contagem naquele ano/UF/categoria

> **Atenção**: o dataset mistura **pessoas físicas e jurídicas** (ex.: `LB`, `EPAO`, `ECIPO`). Quando o foco for “quantos **dentistas**”, use apenas a categoria **`CD`**.

---

## Metodologia de Métricas

- **YoY (%)**: variação percentual de um ano para o seguinte.
- **CAGR (% a.a.)**: taxa média de crescimento anual entre o **primeiro** e o **último** ano disponíveis para a série.
- **Mix (%)**: participação de cada categoria no total (DF e Brasil, último ano).
- **Ranking**: ordenação das UFs pelo total no último ano da série.
- **Densidade (1:xxx)** *(opcional no dashboard)*: população por profissional.  
  - Se você fornecer `populacao_uf_ano.csv` (colunas: `uf,ano,populacao`), o dashboard calcula **DF** e **Brasil** automaticamente.
  - Se não houver arquivo, o dashboard usa **valores padrão** editáveis no código.

---

## Limitações Importantes

- **Pessoas × entidades**: parte das categorias não representa profissionais (afeta comparações de “mão de obra”).
- **Sem per capita nativo**: densidades dependem de **dados externos de população** (arquivo opcional).
- **Cobertura SUS**: métricas de rede pública podem exigir apurações específicas (concursos, credenciamentos, equipes).
- **Qualidade de cadastro**: séries administrativas podem ter sub/registros ou revisões.

---

## Roadmap

- [ ] Integrar população IBGE automaticamente (API ou arquivo atualizado).
- [ ] Adicionar **mapa temático** por UF (per capita).
- [ ] Exportação de **PDF** do dashboard.
- [ ] Série por **subcategorias** (quando houver).
- [ ] Camada de **anotações** no gráfico (marcar eventos relevantes).
- [ ] Notebook (`.ipynb`) com passo a passo didático.

---

## Como Contribuir

1. Faça um **fork** e crie um branch: `git checkout -b feat/sua-ideia`
2. Rode o script, gere os CSVs/PNGs e valide o dashboard.
3. Abra um **Pull Request** explicando o que mudou.

Padrão de commit (sugestão):
```
feat: adiciona densidade per capita no dashboard
fix: corrige parse do CSV de yoy
docs: atualiza README com instruções de execução
```

---

## Licença

Este projeto está sob a **Licença MIT**. Sinta-se livre para usar, adaptar e redistribuir com os devidos créditos. Veja o arquivo `LICENSE` (crie um se ainda não existir).

---

## Autor

**Lucas — 4º semestre de Ciência de Dados e IA (Ibmec DF)**  
- GitHub: <https://github.com/lucasrodor>  
- LinkedIn: <https://www.linkedin.com/in/lucasrodor/>

Se este projeto te ajudou, deixe uma ⭐ no repositório! Feedbacks e PRs são muito bem-vindos.
