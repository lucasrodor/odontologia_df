# -*- coding: utf-8 -*-
"""
Análise exploratória (Brasil + DF) com comparações entre UFs
Entrada esperada (sem cabeçalho): Download (1).csv com colunas:
[uf, ano, sigla, quantidade]
- uf: sigla do estado (ex: DF, SP, RJ...)
- ano: 2010..2025 (ou faixa disponível)
- sigla: categoria (CD, EPAO, TPD, LB, TSB, ASB, APD, ECIPO)
- quantidade: contagem naquele ano/UF/categoria

Saídas: CSVs de resumo e PNGs de gráficos no diretório atual.
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============== PARÂMETROS ==============
ARQUIVO = "C:\\Users\\lucas\\Downloads\\Download (1).csv"   # ajuste o caminho se necessário
TOP_N = 10                      # Top UFs para ranking
COMPARAR_UFS = []               # Ex.: ["DF","SP","MG","GO"]; se vazio, usa DF + 3 maiores
UF_REFERENCIA = "DF"            # UF âncora para algumas comparações

# ============== 1) Leitura e preparação ==============
# Lê SEM cabeçalho, pois a 1ª linha é dado
df = pd.read_csv(ARQUIVO, header=None, names=["uf", "ano", "sigla", "quantidade"])
df = df.dropna(how="all").copy()

# Limpeza e tipos
df["uf"] = df["uf"].astype(str).str.strip().str.upper()
df["sigla"] = df["sigla"].astype(str).str.strip().str.upper()
df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")

# Remove linhas inválidas
df = df.dropna(subset=["ano", "quantidade"]).copy()
# Mantém apenas UFs com 2 letras (evita linhas acidentais)
df = df[df["uf"].str.match(r"^[A-Z]{2}$", na=False)].copy()

# Tradução de categorias
TRADUTOR = {
    "CD": "Cirurgião Dentista",
    "EPAO": "Entidade Prestadora de Assistência Odontológica",
    "TPD": "Técnico em Prótese Dentária",
    "LB": "Laboratório de Prótese Dentária",
    "TSB": "Técnico em Saúde Bucal",
    "ASB": "Auxiliar em Saúde Bucal",
    "APD": "Auxiliar de Prótese Dentária",
    "ECIPO": "Empresa que comercializa e/ou industrializa produto odontológico",
}
df["categoria"] = df["sigla"].map(TRADUTOR).fillna(df["sigla"])
df
# ============== 2) Visão geral ==============
anos = sorted(df["ano"].dropna().unique().tolist())
ufs = sorted(df["uf"].dropna().unique().tolist())
cats = sorted(df["categoria"].dropna().unique().tolist())

print("==== VISÃO GERAL ====")
print(f"- Linhas totais: {len(df)}")
print(f"- Anos: {min(anos)} → {max(anos)}")
print(f"- UFs: {len(ufs)} -> {', '.join(ufs[:15])}{'...' if len(ufs)>15 else ''}")
print(f"- Categorias: {', '.join(cats)}")

# ============== 3) Agregações base ==============
# Totais por UF e ano
uf_ano = (
    df.groupby(["uf", "ano"], as_index=False)["quantidade"]
      .sum()
      .sort_values(["uf", "ano"])
)

# Totais por UF, categoria e ano
uf_cat_ano = (
    df.groupby(["uf", "categoria", "ano"], as_index=False)["quantidade"]
      .sum()
      .sort_values(["uf", "categoria", "ano"])
)

# Totais Brasil por ano ( Dentistas no Brasil por ANO )
br_ano = (
    df.groupby("ano", as_index=False)["quantidade"]
      .sum()
      .sort_values("ano")
)

# Ano mais recente
ultimo_ano = int(br_ano["ano"].max())
print(f"\nAno mais recente no dataset: {ultimo_ano}")

# Ranking UFs no último ano
rank_ultimo_ano = (
    uf_ano[uf_ano["ano"] == ultimo_ano]
    .sort_values("quantidade", ascending=False)
    .reset_index(drop=True)
)

# Posição do DF
pos_df = None
if UF_REFERENCIA in rank_ultimo_ano["uf"].values:
    pos_df = int(rank_ultimo_ano.index[rank_ultimo_ano["uf"] == UF_REFERENCIA][0]) + 1
print(f"Posição do {UF_REFERENCIA} no ano {ultimo_ano}: {pos_df}")

# ============== 4) Métricas extras (CAGR e YoY) ==============
def cagr(v0: float, v1: float, n_years: int) -> float:
    """CAGR entre primeiro e último ano (retorna fração, ex: 0.12 = 12%)."""
    if v0 <= 0 or n_years <= 0:
        return np.nan
    return (v1 / v0) ** (1 / n_years) - 1

# CAGR por UF (1º ano disponível vs último)
cagr_rows = []
for uf in ufs:
    serie = uf_ano[uf_ano["uf"] == uf].sort_values("ano")
    if serie.empty: 
        continue
    y0, y1 = int(serie["ano"].min()), int(serie["ano"].max())
    v0 = float(serie.loc[serie["ano"] == y0, "quantidade"].sum())
    v1 = float(serie.loc[serie["ano"] == y1, "quantidade"].sum())
    cagr_val = cagr(v0, v1, y1 - y0)
    cagr_rows.append({"uf": uf, "ano_inicial": y0, "ano_final": y1, "v0": v0, "v1": v1, "cagr": cagr_val})

cagr_por_uf = pd.DataFrame(cagr_rows).sort_values("cagr", ascending=False)

# YoY por UF (variação % ano a ano)
def yoy_percent(series: pd.Series) -> pd.Series:
    return series.pct_change() * 100.0

yoy_list = []
for uf in ufs:
    serie = uf_ano[uf_ano["uf"] == uf].sort_values("ano")
    if serie.empty:
        continue
    serie = serie.set_index("ano")["quantidade"]
    yoy = yoy_percent(serie).rename(uf)
    yoy_list.append(yoy)

yoy_por_uf = pd.concat(yoy_list, axis=1) if yoy_list else pd.DataFrame()

# ============== 5) Comparações específicas (DF vs maiores ou lista fixa) ==============
if COMPARAR_UFS:
    sel_ufs = [u for u in COMPARAR_UFS if u in ufs]
else:
    # DF + 3 maiores UFs (pelo último ano), se DF existir; caso contrário, 4 maiores UFs
    maiores = rank_ultimo_ano["uf"].tolist()
    if UF_REFERENCIA in ufs:
        outros = [u for u in maiores if u != UF_REFERENCIA][:5]
        sel_ufs = [UF_REFERENCIA] + outros
    else:
        sel_ufs = maiores[:4]

print(f"\nUFs selecionadas para séries comparativas: {', '.join(sel_ufs)}")

# Composição (mix) por categoria: DF x Brasil, no último ano
mix_df_ultimo = (
    uf_cat_ano[(uf_cat_ano["uf"] == UF_REFERENCIA) & (uf_cat_ano["ano"] == ultimo_ano)]
    .groupby("categoria", as_index=False)["quantidade"].sum()
)
if not mix_df_ultimo.empty:
    mix_df_ultimo["% DF"] = 100 * mix_df_ultimo["quantidade"] / mix_df_ultimo["quantidade"].sum()

mix_br_ultimo = (
    df[df["ano"] == ultimo_ano]
    .groupby("categoria", as_index=False)["quantidade"].sum()
)
mix_br_ultimo["% Brasil"] = 100 * mix_br_ultimo["quantidade"] / mix_br_ultimo["quantidade"].sum()

comparativo_mix = pd.merge(
    mix_df_ultimo[["categoria", "% DF"]] if not mix_df_ultimo.empty else pd.DataFrame(columns=["categoria","% DF"]),
    mix_br_ultimo[["categoria", "% Brasil"]],
    on="categoria", how="outer"
).fillna(0).sort_values("% Brasil", ascending=False)

# # ============== 6) Salva CSVs de resumo ==============
# uf_ano.to_csv("data\\resumo_uf_por_ano.csv", index=False)
# uf_cat_ano.to_csv("data\\resumo_uf_categoria_por_ano.csv", index=False)
# br_ano.to_csv("data\\resumo_brasil_por_ano.csv", index=False)
# rank_ultimo_ano.to_csv(f"data\\ranking_ufs_{ultimo_ano}.csv", index=False)
# comparativo_mix.to_csv(f"data\\mix_df_vs_brasil_{ultimo_ano}.csv", index=False)
# cagr_por_uf.to_csv("data\\cagr_por_uf.csv", index=False)
# if not yoy_por_uf.empty:
#     yoy_por_uf.to_csv("data\\yoy_percent_por_uf.csv")

# print("\nArquivos CSV gerados:")
# print("- resumo_uf_por_ano.csv")
# print("- resumo_uf_categoria_por_ano.csv")
# print("- resumo_brasil_por_ano.csv")
# print(f"- ranking_ufs_{ultimo_ano}.csv")
# print(f"- mix_df_vs_brasil_{ultimo_ano}.csv")
# print("- cagr_por_uf.csv")
# if not yoy_por_uf.empty:
#     print("- yoy_percent_por_uf.csv")

# ============== 7) Gráficos (matplotlib puro) ==============
def savefig(fname: str):
    plt.tight_layout()
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Gerado: {fname}")

# (G1) Brasil — total por ano (todas as categorias)
plt.figure(figsize=(9,5))
plt.plot(br_ano["ano"], br_ano["quantidade"], marker="o")
plt.title("Brasil — total por ano (todas as categorias)")
plt.xlabel("Ano"); plt.ylabel("Quantidade")
plt.grid(True)
savefig("br_total_por_ano.png")

# (G2) Ranking UFs no último ano (Top N)
top_ufs = rank_ultimo_ano.head(TOP_N)
plt.figure(figsize=(10,5))
x = np.arange(len(top_ufs))
plt.bar(x, top_ufs["quantidade"])
plt.xticks(x, top_ufs["uf"])
plt.title(f"Top {TOP_N} UFs por quantidade — {ultimo_ano}")
plt.xlabel("UF"); plt.ylabel("Quantidade")
savefig(f"top_{TOP_N}_ufs_{ultimo_ano}.png")

# (G3) Evolução temporal — UFs selecionadas
plt.figure(figsize=(11,6))
for uf in sel_ufs:
    serie = uf_ano[uf_ano["uf"] == uf].sort_values("ano")
    if not serie.empty:
        plt.plot(serie["ano"], serie["quantidade"], marker="o", label=uf)
plt.title("Evolução por UF — comparação selecionada")
plt.xlabel("Ano"); plt.ylabel("Quantidade")
plt.grid(True); plt.legend(title="UF", ncol=2)
savefig("evolucao_ufs_selecionadas.png")

# (G4) Mix de categorias do DF no último ano (se DF existir)
if not mix_df_ultimo.empty:
    tmp = mix_df_ultimo.sort_values("quantidade", ascending=False)
    plt.figure(figsize=(12,5))
    x = np.arange(len(tmp))
    plt.bar(x, tmp["quantidade"])
    plt.xticks(x, tmp["categoria"], rotation=45, ha="right")
    plt.title(f"{UF_REFERENCIA} — distribuição por categoria em {ultimo_ano}")
    plt.xlabel("Categoria"); plt.ylabel("Quantidade")
    savefig(f"{UF_REFERENCIA.lower()}_mix_categorias_{ultimo_ano}.png")

# ================== NOVOS GRÁFICOS ==================

# (G5) Heatmap de YoY por UF (selecionadas)
# Usa yoy_por_uf já calculado; restringe às sel_ufs e anos disponíveis
if not yoy_por_uf.empty:
    yoy_sel = yoy_por_uf[sel_ufs].copy() if all(u in yoy_por_uf.columns for u in sel_ufs) else yoy_por_uf
    yoy_sel = yoy_sel.sort_index()  # anos em ordem
    data = yoy_sel.values
    # mascara NaNs para não "sujar" o heatmap
    data_masked = np.ma.masked_invalid(data)

    plt.figure(figsize=(12, max(5, len(yoy_sel.index)*0.4)))
    im = plt.imshow(data_masked, aspect="auto", interpolation="nearest")
    plt.colorbar(im, label="% YoY")
    plt.yticks(ticks=np.arange(len(yoy_sel.index)), labels=yoy_sel.index.tolist())
    plt.xticks(ticks=np.arange(len(yoy_sel.columns)), labels=yoy_sel.columns.tolist(), rotation=0)
    plt.title("Variação YoY (%) — UFs selecionadas")
    plt.xlabel("UF"); plt.ylabel("Ano")
    savefig("heatmap_yoy_ufs_selecionadas.png")

# (G6) Barras — CAGR por UF (Top N)
cagr_plot = cagr_por_uf.dropna(subset=["cagr"]).head(TOP_N)
if not cagr_plot.empty:
    plt.figure(figsize=(10,6))
    x = np.arange(len(cagr_plot))
    plt.bar(x, (cagr_plot["cagr"]*100.0))
    plt.xticks(x, cagr_plot["uf"])
    plt.title(f"CAGR por UF (Top {TOP_N}) — período disponível em cada UF")
    plt.xlabel("UF"); plt.ylabel("CAGR (% a.a.)")
    # opcional: rótulo numérico no topo
    for i, v in enumerate(cagr_plot["cagr"]*100.0):
        plt.text(i, v, f"{v:.1f}%", ha="center", va="bottom", fontsize=8)
    savefig(f"cagr_top_{TOP_N}_ufs.png")

# (G7) Barras lado a lado — DF vs Brasil (mix por categoria, % no último ano)
if not mix_df_ultimo.empty:
    comp = comparativo_mix.copy()
    categorias = comp["categoria"].tolist()
    ind = np.arange(len(categorias))
    width = 0.4

    plt.figure(figsize=(12,6))
    plt.bar(ind - width/2, comp["% DF"], width)
    plt.bar(ind + width/2, comp["% Brasil"], width)
    plt.xticks(ind, categorias, rotation=45, ha="right")
    plt.title(f"Mix por categoria — DF vs Brasil ({ultimo_ano})")
    plt.xlabel("Categoria"); plt.ylabel("Participação (%)")
    plt.legend(["DF", "Brasil"], title="Região")
    savefig("df_vs_brasil_mix_percent_ultimo_ano.png")

# (G8) Brasil — somente dentistas (CD) por ano
df_cd = df[df["sigla"] == "CD"].copy()
if not df_cd.empty:
    br_ano_cd = (
        df_cd.groupby("ano", as_index=False)["quantidade"].sum()
             .sort_values("ano")
    )
    plt.figure(figsize=(9,5))
    plt.plot(br_ano_cd["ano"], br_ano_cd["quantidade"], marker="o")
    plt.title("Brasil — Cirurgiões-Dentistas (CD) por ano")
    plt.xlabel("Ano"); plt.ylabel("Quantidade")
    plt.grid(True)
    savefig("br_dentistas_cd_por_ano.png")

# (G9) DF vs Brasil — total por ano
plt.figure(figsize=(10,6))
plt.plot(br_ano["ano"], br_ano["quantidade"], marker="o", label="Brasil (Total)")
df_total_ano = uf_ano[uf_ano["uf"] == UF_REFERENCIA]
if not df_total_ano.empty:
    plt.plot(df_total_ano["ano"], df_total_ano["quantidade"], marker="o", label=f"{UF_REFERENCIA} (Total)")
plt.title(f"{UF_REFERENCIA} vs Brasil — total por ano")
plt.xlabel("Ano"); plt.ylabel("Quantidade")
plt.grid(True); plt.legend()
savefig(f"{UF_REFERENCIA.lower()}_vs_brasil_total_por_ano.png")

# (G10) Posição do DF no ranking ao longo dos anos
ranks = []
for ano in sorted(uf_ano["ano"].unique()):
    sub = uf_ano[uf_ano["ano"] == ano].sort_values("quantidade", ascending=False).reset_index(drop=True)
    if UF_REFERENCIA in sub["uf"].values:
        pos = int(sub.index[sub["uf"] == UF_REFERENCIA][0]) + 1
        ranks.append((ano, pos))
rank_df = pd.DataFrame(ranks, columns=["ano", "posicao"])
if not rank_df.empty:
    plt.figure(figsize=(9,5))
    plt.plot(rank_df["ano"], rank_df["posicao"], marker="o")
    plt.gca().invert_yaxis()  # 1º lugar no topo
    plt.title(f"Posição do {UF_REFERENCIA} no ranking de UFs (por ano)")
    plt.xlabel("Ano"); plt.ylabel("Posição (1 = topo)")
    plt.grid(True)
    savefig(f"posicao_{UF_REFERENCIA.lower()}_no_ranking_por_ano.png")

# (G11) CAGR por categoria dentro do DF (top crescimentos)
df_df_cat = uf_cat_ano[uf_cat_ano["uf"] == UF_REFERENCIA].copy()
cagr_cat_rows = []
if not df_df_cat.empty:
    for cat in sorted(df_df_cat["categoria"].unique()):
        serie = df_df_cat[df_df_cat["categoria"] == cat].sort_values("ano")
        y0, y1 = int(serie["ano"].min()), int(serie["ano"].max())
        v0 = float(serie.loc[serie["ano"] == y0, "quantidade"].sum())
        v1 = float(serie.loc[serie["ano"] == y1, "quantidade"].sum())
        cagr_val = cagr(v0, v1, y1 - y0)
        if not np.isnan(cagr_val):
            cagr_cat_rows.append({"categoria": cat, "cagr": cagr_val})
    cagr_cat_df = pd.DataFrame(cagr_cat_rows).sort_values("cagr", ascending=False).head(10)
    if not cagr_cat_df.empty:
        plt.figure(figsize=(10,6))
        x = np.arange(len(cagr_cat_df))
        plt.bar(x, (cagr_cat_df["cagr"]*100.0))
        plt.xticks(x, cagr_cat_df["categoria"], rotation=45, ha="right")
        plt.title(f"{UF_REFERENCIA} — CAGR por categoria (Top 10)")
        plt.xlabel("Categoria"); plt.ylabel("CAGR (% a.a.)")
        for i, v in enumerate(cagr_cat_df["cagr"]*100.0):
            plt.text(i, v, f"{v:.1f}%", ha="center", va="bottom", fontsize=8)
        savefig(f"{UF_REFERENCIA.lower()}_cagr_top_categorias.png")

print("\nConcluído.")
