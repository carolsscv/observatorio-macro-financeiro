from pathlib import Path
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.etl import run_etl, PROCESSED_DIR, SERIES, START_DATE, END_DATE

st.set_page_config(page_title="Observatório Macro-Financeiro", page_icon="📊",
                   layout="wide")
st.title("📊 Observatório Macro-Financeiro do Brasil")
st.caption("Indicadores públicos do Banco Central | Período-base: 2020 a 2023")

@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    path = PROCESSED_DIR / "indicadores_macro.csv"
    if path.exists():
        try:
            local = pd.read_csv(path, parse_dates=["date"])
            if not local.empty:
                return local
        except Exception:
            pass
    # Contingência: consulta API pública do BACEN e salva cópia tratada.
    return run_etl()

with st.sidebar:
    st.header("Filtros")
    if st.button("↻ Atualizar dados / redefinir filtros", use_container_width=True):
        st.cache_data.clear()
        st.session_state.pop("periodo", None)
        st.rerun()
    st.caption("Os dados são consultados na API pública do SGS/BCB.")
    try:
        df_all = load_data()
    except Exception as exc:
        st.error("Não foi possível consultar o Banco Central. Verifique a conexão.")
        st.code(str(exc))
        st.stop()
    min_date = pd.to_datetime(df_all["date"]).min().date()
    max_date = pd.to_datetime(df_all["date"]).max().date()
    periodo = st.date_input("Período", value=(min_date, max_date),
                            min_value=min_date, max_value=max_date,
                            key="periodo")

if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
    df = df_all[(df_all["date"].dt.date >= periodo[0]) &
                (df_all["date"].dt.date <= periodo[1])].copy()
else:
    df = df_all.copy()

if df.empty:
    st.warning("Não há observações para o período selecionado.")
    st.stop()


# Indicadores: médias do período selecionado
selic_media = df["selic_meta"].mean()
ipca_media = df["ipca_12m"].mean()
juro_real_medio = df["juro_real_ex_post"].mean()
dolar_medio = df["dolar_ptax"].mean()

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Selic Meta média (%)",
    f"{selic_media:.2f}"
)

k2.metric(
    "IPCA 12 meses médio (%)",
    f"{ipca_media:.2f}"
)

k3.metric(
    "Juro real ex-post médio (%)",
    f"{juro_real_medio:.2f}"
)

k4.metric(
    "Dólar PTAX médio (R$)",
    f"{dolar_medio:.2f}"
)


tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Visão geral", "Política monetária", "Câmbio", "Atividade econômica", "Correlação e dados"
])

with tab1:
    st.subheader("Panorama macroeconômico")
    st.markdown("**Pergunta de negócio:** como Selic, inflação e câmbio evoluíram entre 2020 e 2023?")
    fig = go.Figure()
    for col, label in [("selic_meta", "Selic Meta (%)"),
                       ("ipca_12m", "IPCA 12 meses (%)")]:
        fig.add_trace(go.Scatter(x=df["date"], y=df[col], name=label, mode="lines"))
    fig.update_layout(title="Selic Meta e IPCA acumulado em 12 meses",
                      xaxis_title="Data", yaxis_title="Percentual (%)",
                      hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    st.info("Leitura: compare a trajetória dos juros com a inflação. A proximidade temporal entre as séries não comprova, isoladamente, causalidade.")

with tab2:
    st.subheader("Política monetária e juro real")
    st.markdown("**Pergunta de negócio:** em quais momentos o juro real ex-post foi mais elevado?")
    fig = px.line(df, x="date", y="juro_real_ex_post",
                  title="Juro real ex-post estimado (%)",
                  labels={"date": "Data", "juro_real_ex_post": "Juro real (%)"})
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("Cálculo utilizado: `((1 + Selic/100) / (1 + IPCA 12m/100) - 1) × 100`. É uma aproximação ex-post construída com as séries selecionadas.")

with tab3:
    st.subheader("Câmbio")
    st.markdown("**Pergunta de negócio:** quando o dólar ficou acima da média do período?")
    media = df["dolar_ptax"].mean()
    fig = px.line(df, x="date", y="dolar_ptax", title="Dólar PTAX (R$/US$)",
                  labels={"date": "Data", "dolar_ptax": "R$/US$"})
    fig.add_hline(y=media, line_dash="dash",
                  annotation_text=f"Média do período: R$ {media:.2f}")
    st.plotly_chart(fig, use_container_width=True)
    acima = int((df["dolar_ptax"] > media).sum())
    st.write(f"No recorte selecionado, **{acima} meses** ficaram acima da média cambial do próprio período.")

with tab4:
    st.subheader("Atividade econômica")
    st.markdown("**Pergunta de negócio:** como o IBC-Br se comportou no período analisado?")
    fig = px.line(df, x="date", y="ibc_br", markers=True,
                  title="IBC-Br dessazonalizado",
                  labels={"date": "Data", "ibc_br": "Índice"})
    st.plotly_chart(fig, use_container_width=True)
    valid = df.dropna(subset=["ibc_br"])
    if len(valid) >= 2:
        variation = (valid["ibc_br"].iloc[-1] / valid["ibc_br"].iloc[0] - 1) * 100
        st.write(f"Entre a primeira e a última observação disponível, a variação acumulada do índice foi de **{variation:.2f}%**.")
    st.caption("O IBC-Br é proxy da atividade econômica e não substitui o PIB oficial.")

with tab5:
    st.subheader("Correlação e base tratada")
    st.markdown("**Pergunta de negócio:** quais pares de indicadores apresentaram maior correlação linear?")
    cols = ["selic_meta", "ipca_mensal", "ipca_12m", "dolar_ptax", "ibc_br"]
    corr = df[cols].corr(method="pearson")
    fig = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu",
                    title="Matriz de correlação de Pearson")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Correlação mede associação linear e não demonstra relação de causa e efeito.")
    st.subheader("Dados filtrados")
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇️ Baixar dados filtrados (CSV)",
                       data=df.to_csv(index=False).encode("utf-8-sig"),
                       file_name="indicadores_macro_filtrados.csv",
                       mime="text/csv")

st.divider()
st.caption("Fontes: Banco Central do Brasil, Sistema Gerenciador de Séries Temporais (SGS). "
           "Séries: 432, 433, 13522, 1 e 24364. Análise descritiva, sem inferência causal.")
