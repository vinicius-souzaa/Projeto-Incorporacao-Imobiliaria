import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Portos do BI — TDRE Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@st.cache_data
def load_all():
    emp    = pd.read_csv(os.path.join(DATA_DIR, "empreendimentos.csv"),  parse_dates=["lancamento", "entrega_prevista"])
    vendas = pd.read_csv(os.path.join(DATA_DIR, "vendas_mensais.csv"),   parse_dates=["data"])
    obra   = pd.read_csv(os.path.join(DATA_DIR, "custo_obra.csv"))
    dre    = pd.read_csv(os.path.join(DATA_DIR, "dre_gerencial.csv"))
    return emp, vendas, obra, dre

emp, vendas, obra, dre = load_all()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏙️ TDRE Dashboard")
    st.caption("Incorporadora · Alto Padrão SP")
    st.markdown("---")
    paginas = {
        "🏠  Visão Geral":       "geral",
        "📈  Comercial & VSO":   "comercial",
        "🏗️  Obras & POC":       "obras",
        "📊  DRE Gerencial":     "dre",
    }
    pagina = st.radio("Navegação", list(paginas.keys()), label_visibility="collapsed")
    st.markdown("---")
    bairros_disponiveis = ["Todos"] + sorted(emp["bairro"].unique().tolist())
    filtro_bairro = st.selectbox("Filtrar por bairro", bairros_disponiveis)
    status_disponiveis = ["Todos", "entregue", "em_obra", "lancamento"]
    filtro_status = st.selectbox("Filtrar por status", status_disponiveis)

# Aplicar filtros
emp_f = emp.copy()
if filtro_bairro != "Todos":
    emp_f = emp_f[emp_f["bairro"] == filtro_bairro]
if filtro_status != "Todos":
    emp_f = emp_f[emp_f["status"] == filtro_status]

ids_filtrados = emp_f["id"].tolist()
vendas_f = vendas[vendas["id_empreendimento"].isin(ids_filtrados)]
obra_f   = obra[obra["id_empreendimento"].isin(ids_filtrados)]
dre_f    = dre[dre["id_empreendimento"].isin(ids_filtrados)]

# ── CORES ─────────────────────────────────────────────────────────────────────
COR_PRIMARIA  = "#1B4F72"
COR_SECUNDARIA = "#2E86C1"
COR_DESTAQUE  = "#F39C12"
COR_SUCESSO   = "#1E8449"
COR_PERIGO    = "#C0392B"
COR_NEUTRO    = "#7F8C8D"

STATUS_LABELS = {"entregue": "Entregue", "em_obra": "Em Obra", "lancamento": "Lançamento"}
STATUS_CORES  = {"entregue": COR_SUCESSO, "em_obra": COR_SECUNDARIA, "lancamento": COR_DESTAQUE}

def fmt_milhoes(v):
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.1f}M"
    return f"R$ {v/1_000:.0f}K"

def metrica(col, label, valor, delta=None, ajuda=None):
    with col:
        st.metric(label=label, value=valor, delta=delta, help=ajuda)

# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA: VISÃO GERAL
# ═══════════════════════════════════════════════════════════════════════════════
if paginas[pagina] == "geral":
    st.title("Visão Geral do Portfólio")
    st.caption("Consolidado de todos os empreendimentos · Dados sintéticos baseados no mercado SP")

    # KPIs
    vgv_total      = emp_f["vgv_total"].sum()
    vgv_vendido    = dre_f["vgv_vendido"].sum()
    unidades_total = emp_f["unidades"].sum()
    n_emp          = len(emp_f)
    margem_media   = dre_f["margem_bruta_pct"].mean()
    vso_medio      = dre_f["vso_acumulado_pct"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    metrica(c1, "Empreendimentos",  f"{n_emp}")
    metrica(c2, "VGV Total Lançado", fmt_milhoes(vgv_total))
    metrica(c3, "VGV Vendido",       fmt_milhoes(vgv_vendido), ajuda="Soma do VGV comercializado")
    metrica(c4, "VSO Acumulado",     f"{vso_medio:.1f}%",      ajuda="Velocidade de vendas média do portfólio")
    metrica(c5, "Margem Bruta Média",f"{margem_media:.1f}%",   ajuda="Margem bruta média via método POC")

    st.markdown("---")

    col_a, col_b = st.columns([1.4, 1])

    with col_a:
        st.subheader("VGV por Empreendimento")
        dre_plot = dre_f.merge(emp_f[["id","status"]], left_on="id_empreendimento", right_on="id", how="left")
        dre_plot["status_label"] = dre_plot["status"].map(STATUS_LABELS)
        fig = px.bar(
            dre_plot.sort_values("vgv_lancado", ascending=True),
            x="vgv_lancado", y="nome",
            color="status_label",
            color_discrete_map={v: STATUS_CORES[k] for k,v in STATUS_LABELS.items()},
            orientation="h",
            labels={"vgv_lancado": "VGV Lançado (R$)", "nome": "", "status_label": "Status"},
            text=dre_plot.sort_values("vgv_lancado", ascending=True)["vgv_lancado"].apply(fmt_milhoes),
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=340, margin=dict(l=0, r=20, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis_tickformat=",.0f",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Portfólio por Status")
        status_count = emp_f["status"].value_counts().reset_index()
        status_count.columns = ["status", "qtd"]
        status_count["label"] = status_count["status"].map(STATUS_LABELS)
        fig2 = px.pie(
            status_count, values="qtd", names="label",
            color="label",
            color_discrete_map={v: STATUS_CORES[k] for k,v in STATUS_LABELS.items()},
            hole=0.55,
        )
        fig2.update_traces(textinfo="label+percent", hovertemplate="%{label}: %{value} empreendimentos")
        fig2.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=10), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Tabela resumo
    st.subheader("Resumo do Portfólio")
    tabela = dre_f.merge(emp_f[["id","bairro","status","lancamento","entrega_prevista"]], left_on="id_empreendimento", right_on="id", how="left")
    tabela = tabela[["nome","bairro","status","vgv_lancado","vso_acumulado_pct","avanco_obra_pct","margem_bruta_pct","ebitda_pct"]].copy()
    tabela.columns = ["Empreendimento","Bairro","Status","VGV Lançado","VSO Acum. %","Avanço Obra %","Margem Bruta %","EBITDA %"]
    tabela["VGV Lançado"] = tabela["VGV Lançado"].apply(fmt_milhoes)
    tabela["Status"] = tabela["Status"].map(STATUS_LABELS)
    st.dataframe(tabela, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA: COMERCIAL & VSO
# ═══════════════════════════════════════════════════════════════════════════════
elif paginas[pagina] == "comercial":
    st.title("Comercial & VSO")
    st.caption("Velocidade de Vendas · Distratos · VGV mensal")

    # Seletor de empreendimento
    emp_opcoes = ["Todos"] + dre_f["nome"].tolist()
    sel_emp = st.selectbox("Empreendimento", emp_opcoes)

    if sel_emp != "Todos":
        id_sel = dre_f[dre_f["nome"] == sel_emp]["id_empreendimento"].values[0]
        vendas_plot = vendas_f[vendas_f["id_empreendimento"] == id_sel]
    else:
        vendas_plot = vendas_f.groupby("data").agg(
            unidades_vendidas=("unidades_vendidas","sum"),
            distratos=("distratos","sum"),
            vgv_mes=("vgv_mes","sum"),
            vso_pct=("vso_pct","mean"),
        ).reset_index()

    c1, c2, c3 = st.columns(3)
    metrica(c1, "Total Unidades Vendidas", f"{vendas_plot['unidades_vendidas'].sum():,.0f}")
    metrica(c2, "Total Distratos",         f"{vendas_plot['distratos'].sum():,.0f}",
            ajuda="Unidades distratadas no período")
    metrica(c3, "VGV Comercializado",      fmt_milhoes(vendas_plot["vgv_mes"].sum()))

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("VSO Mensal (%)")
        fig = px.line(
            vendas_plot.sort_values("data"), x="data", y="vso_pct",
            labels={"data": "", "vso_pct": "VSO (%)"},
            color_discrete_sequence=[COR_SECUNDARIA],
        )
        fig.add_hline(y=10, line_dash="dash", line_color=COR_PERIGO,
                      annotation_text="Mínimo saudável (10%)", annotation_position="top left")
        fig.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("VGV Mensal Comercializado")
        fig2 = px.bar(
            vendas_plot.sort_values("data"), x="data", y="vgv_mes",
            labels={"data": "", "vgv_mes": "VGV (R$)"},
            color_discrete_sequence=[COR_PRIMARIA],
        )
        fig2.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=10), yaxis_tickformat=",.0f")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Unidades Vendidas vs Distratos")
    fig3 = go.Figure()
    vd = vendas_plot.sort_values("data")
    fig3.add_trace(go.Bar(x=vd["data"], y=vd["unidades_vendidas"], name="Vendidas", marker_color=COR_SUCESSO))
    fig3.add_trace(go.Bar(x=vd["data"], y=vd["distratos"],         name="Distratos", marker_color=COR_PERIGO))
    fig3.update_layout(barmode="group", height=280, margin=dict(l=0,r=0,t=10,b=10),
                       legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig3, use_container_width=True)

    # VSO acumulado por bairro
    st.subheader("VSO Acumulado por Bairro")
    vso_bairro = dre_f.merge(emp_f[["id","bairro"]], left_on="id_empreendimento", right_on="id")
    vso_bairro = vso_bairro.groupby("bairro")["vso_acumulado_pct"].mean().reset_index()
    fig4 = px.bar(
        vso_bairro.sort_values("vso_acumulado_pct", ascending=False),
        x="bairro", y="vso_acumulado_pct",
        labels={"bairro":"Bairro","vso_acumulado_pct":"VSO Acumulado (%)"},
        color="vso_acumulado_pct",
        color_continuous_scale=[[0, COR_PERIGO],[0.5, COR_DESTAQUE],[1, COR_SUCESSO]],
        text_auto=".1f",
    )
    fig4.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=10), coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA: OBRAS & POC
# ═══════════════════════════════════════════════════════════════════════════════
elif paginas[pagina] == "obras":
    st.title("Obras & POC")
    st.caption("Percentage of Completion · Curva S · Desvio de Orçamento")

    emp_obra_opcoes = obra_f["nome_empreendimento"].unique().tolist()
    sel_obra = st.selectbox("Selecionar empreendimento", emp_obra_opcoes)
    obra_sel = obra_f[obra_f["nome_empreendimento"] == sel_obra]

    avanco = obra_sel["avanco_fisico_pct"].iloc[0]
    receita_poc = obra_sel["receita_reconhecida_poc"].iloc[0]
    desvio_medio = obra_sel["desvio_pct"].mean()

    c1, c2, c3, c4 = st.columns(4)
    metrica(c1, "Avanço Físico (POC)", f"{avanco:.0f}%")
    metrica(c2, "Receita Reconhecida", fmt_milhoes(receita_poc), ajuda="Receita pelo método POC")
    metrica(c3, "Desvio Médio de Custo", f"{desvio_medio:+.1f}%",
            delta=f"{desvio_medio:+.1f}%",
            ajuda="Positivo = acima do orçado")
    custo_total_orcado = obra_sel["custo_orcado"].sum()
    custo_total_real   = obra_sel["custo_realizado"].sum()
    metrica(c4, "Custo Realizado vs Orçado",
            fmt_milhoes(custo_total_real),
            delta=fmt_milhoes(custo_total_real - custo_total_orcado))

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Orçado vs Realizado por Etapa")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=obra_sel["etapa_obra"], y=obra_sel["custo_orcado"],
            name="Orçado", marker_color=COR_NEUTRO,
        ))
        fig.add_trace(go.Bar(
            x=obra_sel["etapa_obra"], y=obra_sel["custo_realizado"],
            name="Realizado", marker_color=COR_SECUNDARIA,
        ))
        fig.update_layout(barmode="group", height=300, margin=dict(l=0,r=0,t=10,b=10),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02),
                          yaxis_tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Desvio de Custo por Etapa (%)")
        cores_desvio = [COR_PERIGO if d > 5 else (COR_DESTAQUE if d > 0 else COR_SUCESSO)
                        for d in obra_sel["desvio_pct"]]
        fig2 = go.Figure(go.Bar(
            x=obra_sel["etapa_obra"], y=obra_sel["desvio_pct"],
            marker_color=cores_desvio,
            text=[f"{d:+.1f}%" for d in obra_sel["desvio_pct"]],
            textposition="outside",
        ))
        fig2.add_hline(y=0, line_color="gray", line_width=1)
        fig2.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=10),
                           yaxis_title="Desvio (%)")
        st.plotly_chart(fig2, use_container_width=True)

    # Curva S simulada
    st.subheader("Curva S — Avanço Físico-Financeiro")
    meses = list(range(1, 37))
    ritmo_planejado = [min(100, (m / 30) ** 1.2 * 100) for m in meses]
    ritmo_real      = [min(100, p * (1 + 0.05 * (1 if m < 20 else -0.5)) + (m * 0.3))
                       for m, p in zip(meses, ritmo_planejado)]
    ritmo_real      = [min(avanco, r) for r in ritmo_real]

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=meses, y=ritmo_planejado, name="Planejado",
                               line=dict(color=COR_NEUTRO, dash="dash")))
    fig3.add_trace(go.Scatter(x=meses, y=ritmo_real, name="Realizado",
                               line=dict(color=COR_SECUNDARIA), fill="tonexty",
                               fillcolor="rgba(46,134,193,0.1)"))
    fig3.add_vline(x=avanco / 100 * 30, line_dash="dot", line_color=COR_DESTAQUE,
                   annotation_text=f"Hoje ({avanco:.0f}%)")
    fig3.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=10),
                       xaxis_title="Mês de obra", yaxis_title="Avanço (%)",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig3, use_container_width=True)

    # Todos os empreendimentos — comparativo POC
    st.subheader("POC por Empreendimento — Comparativo")
    poc_comp = obra_f.groupby("nome_empreendimento").first().reset_index()[["nome_empreendimento","avanco_fisico_pct"]]
    fig4 = px.bar(
        poc_comp.sort_values("avanco_fisico_pct", ascending=True),
        x="avanco_fisico_pct", y="nome_empreendimento", orientation="h",
        color="avanco_fisico_pct",
        color_continuous_scale=[[0, COR_PERIGO],[0.5, COR_DESTAQUE],[1, COR_SUCESSO]],
        labels={"avanco_fisico_pct": "Avanço (%)", "nome_empreendimento": ""},
        text_auto=".0f",
    )
    fig4.update_layout(height=300, margin=dict(l=0,r=20,t=10,b=10), coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA: DRE GERENCIAL
# ═══════════════════════════════════════════════════════════════════════════════
elif paginas[pagina] == "dre":
    st.title("DRE Gerencial")
    st.caption("Resultado econômico pelo método POC · Por empreendimento")

    c1, c2, c3, c4 = st.columns(4)
    metrica(c1, "Receita Total POC",    fmt_milhoes(dre_f["receita_reconhecida_poc"].sum()))
    metrica(c2, "Custo Total POC",      fmt_milhoes(dre_f["custo_obra_poc"].sum()))
    metrica(c3, "Margem Bruta Média",   f"{dre_f['margem_bruta_pct'].mean():.1f}%")
    ebitda_pos = dre_f[dre_f["ebitda"] > 0]["ebitda"].sum()
    metrica(c4, "EBITDA Consolidado",   fmt_milhoes(ebitda_pos),
            ajuda="Apenas empreendimentos com EBITDA positivo (obras avançadas)")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Margem Bruta por Empreendimento (%)")
        fig = px.bar(
            dre_f.sort_values("margem_bruta_pct", ascending=True),
            x="margem_bruta_pct", y="nome", orientation="h",
            color="margem_bruta_pct",
            color_continuous_scale=[[0, COR_PERIGO],[0.4, COR_DESTAQUE],[1, COR_SUCESSO]],
            text_auto=".1f",
            labels={"margem_bruta_pct": "Margem Bruta (%)", "nome": ""},
        )
        fig.add_vline(x=30, line_dash="dash", line_color=COR_NEUTRO,
                      annotation_text="Benchmark 30%")
        fig.update_layout(height=320, margin=dict(l=0,r=20,t=10,b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Waterfall DRE — Consolidado")
        receita = dre_f["receita_reconhecida_poc"].sum()
        custo   = dre_f["custo_obra_poc"].sum()
        desp_c  = dre_f["despesas_comerciais"].sum()
        desp_a  = dre_f["despesas_administrativas"].sum()
        ebitda  = receita - custo - desp_c - desp_a

        fig2 = go.Figure(go.Waterfall(
            name="DRE",
            orientation="v",
            measure=["absolute","relative","relative","relative","total"],
            x=["Receita POC","(-) Custo Obra","(-) Desp. Comercial","(-) Desp. Adm.","EBITDA"],
            y=[receita, -custo, -desp_c, -desp_a, 0],
            text=[fmt_milhoes(v) for v in [receita, custo, desp_c, desp_a, ebitda]],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": COR_SUCESSO}},
            decreasing={"marker": {"color": COR_PERIGO}},
            totals={"marker": {"color": COR_PRIMARIA}},
        ))
        fig2.update_layout(height=320, margin=dict(l=0,r=0,t=10,b=10),
                           showlegend=False, yaxis_tickformat=",.0f")
        st.plotly_chart(fig2, use_container_width=True)

    # Scatter margem vs VSO
    st.subheader("Margem Bruta × VSO Acumulado — Portfólio")
    dre_scatter = dre_f.merge(emp_f[["id","status"]], left_on="id_empreendimento", right_on="id")
    dre_scatter["status_label"] = dre_scatter["status"].map(STATUS_LABELS)
    fig3 = px.scatter(
        dre_scatter,
        x="vso_acumulado_pct", y="margem_bruta_pct",
        size="vgv_lancado", color="status_label",
        text="nome",
        color_discrete_map={v: STATUS_CORES[k] for k,v in STATUS_LABELS.items()},
        labels={"vso_acumulado_pct":"VSO Acumulado (%)","margem_bruta_pct":"Margem Bruta (%)","status_label":"Status"},
    )
    fig3.update_traces(textposition="top center")
    fig3.add_hline(y=30, line_dash="dash", line_color=COR_NEUTRO, annotation_text="Benchmark margem 30%")
    fig3.add_vline(x=80, line_dash="dash", line_color=COR_NEUTRO, annotation_text="VSO 80%")
    fig3.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=10))
    st.plotly_chart(fig3, use_container_width=True)

    # Tabela detalhada
    st.subheader("DRE Detalhado por Empreendimento")
    dre_tabela = dre_f[[
        "nome","vgv_lancado","vgv_vendido","vso_acumulado_pct",
        "receita_reconhecida_poc","custo_obra_poc","margem_bruta","margem_bruta_pct",
        "despesas_comerciais","ebitda","ebitda_pct"
    ]].copy()
    for col in ["vgv_lancado","vgv_vendido","receita_reconhecida_poc","custo_obra_poc","margem_bruta","despesas_comerciais","ebitda"]:
        dre_tabela[col] = dre_tabela[col].apply(fmt_milhoes)
    dre_tabela.columns = [
        "Empreendimento","VGV Lançado","VGV Vendido","VSO %",
        "Receita POC","Custo POC","Margem Bruta","Margem %",
        "Desp. Comercial","EBITDA","EBITDA %"
    ]
    st.dataframe(dre_tabela, use_container_width=True, hide_index=True)
