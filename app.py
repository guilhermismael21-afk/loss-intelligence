
import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Loss Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent

COLUMN_ALIASES = {
    "area": ["Área LI", "Area LI", "Área", "Area"],
    "macro": ["Macrotema LI", "Macrotema"],
    "theme": ["Tema específico", "Tema especifico", "Tema"],
    "voice": ["Voz do problema", "Voz"],
    "status": ["Status"],
    "owner": ["Responsável", "Responsavel"],
    "overdue": ["Atrasada?", "Atrasada"],
    "confidence": ["Confiança", "Confianca"],
    "reference": ["Referência técnica", "Referencia tecnica"],
    "exposure": ["Exposição / perda potencial", "Exposicao / perda potencial"],
    "title": ["Título", "Titulo"],
    "description": ["Descrição", "Descricao"],
    "created": ["Data de Criação", "Data de Criacao"],
    "target": ["Data Alvo"],
    "closed": ["Data Conclusão", "Data Conclusao"],
    "days": ["Dias em Aberto"],
    "priority": ["Prioridade"],
    "id": ["PublishedRecordId", "ID"],
}

def resolve_column(df, logical_name):
    for candidate in COLUMN_ALIASES[logical_name]:
        if candidate in df.columns:
            return candidate
    return None

@st.cache_data(show_spinner=False)
def read_csv_bytes(content):
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return pd.read_csv(io.BytesIO(content), encoding=encoding)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(io.BytesIO(content))

@st.cache_data(show_spinner=False)
def read_default():
    return pd.read_csv(BASE_DIR / "data.csv", encoding="utf-8-sig")

def normalize(df):
    df = df.copy()
    for logical in ("created", "target", "closed"):
        col = resolve_column(df, logical)
        if col:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    days = resolve_column(df, "days")
    if days:
        df[days] = pd.to_numeric(df[days], errors="coerce").fillna(0)
    return df

def safe_value(row, logical):
    col = resolve_column(row.to_frame().T, logical)
    return row.get(col, "") if col else ""

def counts(df, col, top=15):
    if not col:
        return pd.DataFrame({"Categoria": [], "Quantidade": []})
    result = (
        df[col].fillna("Não informado").astype(str)
        .value_counts()
        .head(top)
        .rename_axis("Categoria")
        .reset_index(name="Quantidade")
    )
    return result

def download_csv(df):
    return df.to_csv(index=False).encode("utf-8-sig")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background: #f4f7f9;}
[data-testid="stSidebar"] {background: #102a43;}
[data-testid="stSidebar"] * {color: #f5f8fa;}
.block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
.li-header {
    padding: 1.25rem 1.4rem;
    border-radius: 16px;
    color: white;
    background: linear-gradient(115deg, #102a43, #2166a5);
    margin-bottom: 1rem;
}
.li-header h1 {margin: 0; font-size: 2rem;}
.li-header p {margin: .35rem 0 0; opacity: .9;}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e3eaf0;
    border-top: 4px solid #2166a5;
    padding: .8rem 1rem;
    border-radius: 12px;
}
.insight {
    background: #e8f2fa;
    border-left: 5px solid #2166a5;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: .4rem 0 1rem;
}
.small-note {color: #607d8b; font-size: .88rem;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    """<div class="li-header">
    <h1>Loss Intelligence</h1>
    <p>Da contagem de ações para a inteligência sobre mecanismos de perda.</p>
    </div>""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Base de dados")
    uploaded = st.file_uploader(
        "Carregar nova base CSV",
        type=["csv"],
        help="A base deve manter as colunas de Loss Intelligence.",
    )
    if uploaded:
        df = read_csv_bytes(uploaded.getvalue())
        st.success("Base carregada para esta sessão.")
    else:
        df = read_default()
        st.caption("Usando a base padrão incluída no projeto.")

df = normalize(df)

COL = {name: resolve_column(df, name) for name in COLUMN_ALIASES}

with st.sidebar:
    st.markdown("---")
    st.markdown("## Filtros")
    def multiselect_for(label, col):
        if not col:
            return []
        options = sorted(df[col].dropna().astype(str).unique().tolist())
        return st.multiselect(label, options)

    f_area = multiselect_for("Área", COL["area"])
    f_macro = multiselect_for("Macrotema", COL["macro"])
    f_theme = multiselect_for("Tema específico", COL["theme"])
    f_status = multiselect_for("Status", COL["status"])
    f_owner = multiselect_for("Responsável", COL["owner"])
    search = st.text_input("Pesquisar texto")
    st.markdown("---")
    st.caption("Os filtros afetam todas as páginas.")

filtered = df.copy()
for selected, col in [
    (f_area, COL["area"]),
    (f_macro, COL["macro"]),
    (f_theme, COL["theme"]),
    (f_status, COL["status"]),
    (f_owner, COL["owner"]),
]:
    if selected and col:
        filtered = filtered[filtered[col].astype(str).isin(selected)]

if search:
    searchable = [
        c for c in [
            COL["title"], COL["description"], COL["voice"],
            COL["theme"], COL["exposure"], COL["reference"]
        ] if c
    ]
    if searchable:
        mask = filtered[searchable].fillna("").astype(str).agg(" ".join, axis=1).str.contains(
            search, case=False, na=False, regex=False
        )
        filtered = filtered[mask]

total = len(filtered)
status_col = COL["status"]
overdue_col = COL["overdue"]
confidence_col = COL["confidence"]

open_count = (
    int((filtered[status_col].astype(str).str.lower() != "closed").sum())
    if status_col else 0
)
overdue_count = (
    int(filtered[overdue_col].astype(str).str.upper().eq("SIM").sum())
    if overdue_col else 0
)
review_count = (
    int(filtered[confidence_col].astype(str).str.contains("revis", case=False, na=False).sum())
    if confidence_col else 0
)
areas_count = filtered[COL["area"]].nunique() if COL["area"] else 0
themes_count = filtered[COL["theme"]].nunique() if COL["theme"] else 0
closed_count = total - open_count
closure_rate = closed_count / total if total else 0

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Ações analisadas", f"{total:,}".replace(",", "."))
k2.metric("Abertas", f"{open_count:,}".replace(",", "."))
k3.metric("Atrasadas", f"{overdue_count:,}".replace(",", "."))
k4.metric("Fechamento", f"{closure_rate:.1%}".replace(".", ","))
k5.metric("Áreas", areas_count)
k6.metric("Revisão especializada", review_count)

macro_counts = counts(filtered, COL["macro"])
area_counts = counts(filtered, COL["area"])
theme_counts = counts(filtered, COL["theme"])

top_macro = macro_counts.iloc[0].to_dict() if len(macro_counts) else {"Categoria": "Sem dados", "Quantidade": 0}
top_area = area_counts.iloc[0].to_dict() if len(area_counts) else {"Categoria": "Sem dados", "Quantidade": 0}
top_theme = theme_counts.iloc[0].to_dict() if len(theme_counts) else {"Categoria": "Sem dados", "Quantidade": 0}

st.markdown(
    f"""<div class="insight"><b>Leitura automática:</b>
    o principal mecanismo no recorte é <b>{top_macro['Categoria']}</b>
    ({top_macro['Quantidade']} registros). A maior concentração está em
    <b>{top_area['Categoria']}</b> ({top_area['Quantidade']}). O tema específico
    mais recorrente é <b>{top_theme['Categoria']}</b>
    ({top_theme['Quantidade']}). Há <b>{overdue_count}</b> ações atrasadas.
    </div>""",
    unsafe_allow_html=True,
)

tab_exec, tab_voices, tab_areas, tab_nr, tab_5s, tab_people, tab_data = st.tabs(
    ["Executivo", "Vozes", "Áreas", "NR Intelligence", "5S Intelligence", "Responsáveis", "Ações"]
)

def horizontal_bar(data, title, color):
    fig = px.bar(
        data.sort_values("Quantidade"),
        x="Quantidade",
        y="Categoria",
        orientation="h",
        title=title,
        text="Quantidade",
        color_discrete_sequence=[color],
    )
    fig.update_layout(height=430, margin=dict(l=10, r=20, t=55, b=20), showlegend=False)
    fig.update_traces(textposition="outside")
    return fig

with tab_exec:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            horizontal_bar(macro_counts, "Pareto de macrotemas", "#2166a5"),
            use_container_width=True,
        )
    with c2:
        st.plotly_chart(
            horizontal_bar(area_counts, "Concentração por área", "#2e8b57"),
            use_container_width=True,
        )

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(
            horizontal_bar(theme_counts, "O que existe dentro dos temas", "#d97706"),
            use_container_width=True,
        )
    with c4:
        if COL["created"]:
            trend = (
                filtered.dropna(subset=[COL["created"]])
                .assign(Mês=lambda x: x[COL["created"]].dt.to_period("M").astype(str))
                .groupby("Mês")
                .size()
                .reset_index(name="Quantidade")
            )
            fig = px.line(trend, x="Mês", y="Quantidade", markers=True, title="Tendência de criação")
            fig.update_layout(height=430, margin=dict(l=10, r=20, t=55, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna de data de criação não encontrada.")

with tab_voices:
    voice_counts = counts(filtered, COL["voice"], top=20)
    ref_counts = counts(filtered, COL["reference"], top=20)
    c1, c2 = st.columns(2)
    c1.plotly_chart(horizontal_bar(voice_counts, "Maiores vozes recorrentes", "#7c3aed"), use_container_width=True)
    c2.plotly_chart(horizontal_bar(ref_counts, "Referências técnicas", "#0f766e"), use_container_width=True)

with tab_areas:
    st.subheader("Área × mecanismo de perda")
    if COL["area"] and COL["macro"]:
        cross = pd.crosstab(
            filtered[COL["area"]].fillna("Não informado"),
            filtered[COL["macro"]].fillna("Não informado"),
        )
        fig = px.imshow(cross, aspect="auto", text_auto=True, color_continuous_scale="Blues")
        fig.update_layout(height=max(450, len(cross) * 28), coloraxis_colorbar_title="Ações")
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(area_counts, use_container_width=True, hide_index=True)

with tab_nr:
    nr_mask = pd.Series(False, index=filtered.index)
    for col in [COL["macro"], COL["theme"], COL["reference"], COL["title"], COL["description"]]:
        if col:
            nr_mask |= filtered[col].fillna("").astype(str).str.contains(r"\bNR[\s-]?\d+", case=False, regex=True)
    nr_df = filtered[nr_mask]
    st.metric("Registros relacionados a NR", len(nr_df))
    c1, c2 = st.columns(2)
    c1.plotly_chart(horizontal_bar(counts(nr_df, COL["reference"]), "NR / referência", "#b91c1c"), use_container_width=True)
    c2.plotly_chart(horizontal_bar(counts(nr_df, COL["theme"]), "Problema específico", "#d97706"), use_container_width=True)
    st.dataframe(nr_df, use_container_width=True, hide_index=True, height=420)

with tab_5s:
    five_mask = pd.Series(False, index=filtered.index)
    for col in [COL["macro"], COL["theme"], COL["title"], COL["description"], COL["voice"]]:
        if col:
            five_mask |= filtered[col].fillna("").astype(str).str.contains("5S|organiza|limpeza|demarca|identifica|armazen", case=False, regex=True)
    five_df = filtered[five_mask]
    st.metric("Registros relacionados a 5S", len(five_df))
    c1, c2 = st.columns(2)
    c1.plotly_chart(horizontal_bar(counts(five_df, COL["theme"]), "Tipo de 5S", "#2e8b57"), use_container_width=True)
    c2.plotly_chart(horizontal_bar(counts(five_df, COL["area"]), "Áreas com maior recorrência", "#2166a5"), use_container_width=True)
    st.dataframe(five_df, use_container_width=True, hide_index=True, height=420)

with tab_people:
    if COL["owner"]:
        people = filtered.groupby(COL["owner"], dropna=False).size().reset_index(name="Total")
        people[COL["owner"]] = people[COL["owner"]].fillna("Não informado")
        if overdue_col:
            late = (
                filtered.assign(_late=filtered[overdue_col].astype(str).str.upper().eq("SIM").astype(int))
                .groupby(COL["owner"], dropna=False)["_late"].sum()
                .reset_index(name="Atrasadas")
            )
            people = people.merge(late, on=COL["owner"], how="left")
        people = people.sort_values("Total", ascending=False)
        st.plotly_chart(
            horizontal_bar(
                people.rename(columns={COL["owner"]: "Categoria", "Total": "Quantidade"}),
                "Ações por responsável",
                "#2166a5",
            ),
            use_container_width=True,
        )
        st.dataframe(people, use_container_width=True, hide_index=True)
    else:
        st.info("Coluna de responsável não encontrada.")

with tab_data:
    st.subheader("Consulta até a ação individual")
    st.caption(f"Exibindo {len(filtered)} registros após os filtros.")
    st.download_button(
        "Baixar recorte em CSV",
        data=download_csv(filtered),
        file_name="loss_intelligence_filtrado.csv",
        mime="text/csv",
    )
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=650)
