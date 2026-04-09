import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="TDRE Analytics | Portfólio Imobiliário SP",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS CUSTOMIZADO — identidade TDRE Brasil ──────────────────────────────────
# Site teixeiraduarte.com.br: logo preto, fundo branco, estética limpa e premium
# Paleta: preto #1A1A1A, areia/bege #D4B896, cinza frio #6B7280, offwhite #F7F6F4
st.markdown("""
<style>
/* Fonte e fundo geral */
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }
.stApp { background-color: #F7F6F4; }

/* Sidebar premium */
[data-testid="stSidebar"] {
    background: #1A1A1A;
    border-right: 1px solid #2D2D2D;
}
[data-testid="stSidebar"] * { color: #E8E4DF !important; }
[data-testid="stSidebar"] .stSelectbox label { color: #A09080 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: .06em; }

/* Botões de navegação na sidebar */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 !important;
    color: #A09080 !important;
    font-size: 13px !important;
    text-align: left !important;
    padding: 10px 16px !important;
    width: 100% !important;
    transition: all .2s;
    font-weight: 400 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(212,184,150,0.1) !important;
    color: #D4B896 !important;
    border-left-color: #D4B896 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    color: #F7F6F4 !important;
    border-left-color: #D4B896 !important;
    background: rgba(212,184,150,0.12) !important;
    font-weight: 600 !important;
}

/* Métricas */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E8E4DF;
    border-radius: 8px;
    padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] { font-size: 11px !important; text-transform: uppercase; letter-spacing: .05em; color: #6B7280 !important; }
[data-testid="stMetricValue"] { font-size: 22px !important; color: #1A1A1A !important; font-weight: 600 !important; }

/* Cards de insight */
.insight-card {
    background: #FFFFFF;
    border-left: 4px solid #D4B896;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #1A1A1A;
    line-height: 1.5;
}
.insight-card.alerta { border-left-color: #C0392B; background: #FDF2F2; }
.insight-card.positivo { border-left-color: #1E6B3A; background: #F2FDF6; }
.insight-card.info { border-left-color: #2563A8; background: #F2F6FD; }
.insight-card.neutro { border-left-color: #6B7280; background: #F9F9F9; }

/* Divisor */
hr { border-color: #E8E4DF; margin: 1rem 0; }

/* Títulos de seção */
h1 { color: #1A1A1A !important; font-weight: 700 !important; font-size: 26px !important; }
h2, h3 { color: #1A1A1A !important; font-weight: 600 !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #E8E4DF; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@st.cache_data
def load_all():
    emp    = pd.read_csv(os.path.join(DATA_DIR, "empreendimentos.csv"),  parse_dates=["lancamento","entrega_prevista"])
    vendas = pd.read_csv(os.path.join(DATA_DIR, "vendas_mensais.csv"),   parse_dates=["data"])
    obra   = pd.read_csv(os.path.join(DATA_DIR, "custo_obra.csv"))
    dre    = pd.read_csv(os.path.join(DATA_DIR, "dre_gerencial.csv"))
    return emp, vendas, obra, dre

emp, vendas, obra, dre = load_all()

STATUS_LABELS = {"entregue":"Entregue","em_obra":"Em Obra","lancamento":"Lançamento"}
dre["status_label"] = dre["status"].map(STATUS_LABELS)

# ── PALETA TDRE Brasil (site teixeiraduarte.com.br) ───────────────────────────
C_PRETO   = "#1A1A1A"   # cor dominante da marca
C_AREIA   = "#D4B896"   # bege/dourado presente no site
C_CINZA   = "#6B7280"   # cinza secundário
C_OFF     = "#F7F6F4"   # fundo offwhite
C_VERDE   = "#1E6B3A"   # sucesso
C_VERM    = "#C0392B"   # alerta
C_AZUL    = "#2563A8"   # informação
C_CLARO   = "#E8E4DF"   # bordas

STATUS_CORES = {"Entregue": C_VERDE, "Em Obra": C_AZUL, "Lançamento": C_AREIA}
LINHA_CORES  = {"Premium": C_PRETO, "Alto Padrão": C_AREIA, "Smart": C_CINZA}

LAYOUT_BASE = dict(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(family="Inter, Segoe UI, sans-serif", color=C_PRETO, size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
    xaxis=dict(showgrid=True, gridcolor=C_CLARO, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor=C_CLARO, zeroline=False),
)

def fmt_M(v):
    try:
        v = float(v)
        return f"R$ {v/1_000_000:.1f}M" if abs(v) >= 1_000_000 else f"R$ {v/1_000:.0f}K"
    except: return "—"

def insight(texto, tipo="neutro"):
    st.markdown(f'<div class="insight-card {tipo}">{texto}</div>', unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 16px 8px;">
        <div style="font-size:18px;font-weight:700;letter-spacing:-.5px;color:#F7F6F4;">TDRE</div>
        <div style="font-size:10px;color:#A09080;text-transform:uppercase;letter-spacing:.12em;margin-top:2px;">Analytics · Portfólio SP</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#2D2D2D;margin:0 0 8px;">', unsafe_allow_html=True)

    paginas = ["🏠  Visão Geral","📈  Comercial & VSO","🏗️  Obras & POC","📊  DRE Gerencial"]
    if "pagina" not in st.session_state:
        st.session_state.pagina = paginas[0]
    for p in paginas:
        ativo = st.session_state.pagina == p
        if st.button(p, key=p, use_container_width=True, type="primary" if ativo else "secondary"):
            st.session_state.pagina = p
            st.rerun()

    st.markdown('<hr style="border-color:#2D2D2D;margin:8px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px;color:#A09080;text-transform:uppercase;letter-spacing:.1em;padding:0 4px 6px;">Filtros</div>', unsafe_allow_html=True)

    # Filtro bairro
    bairros_disp = ["Todos"] + sorted(emp["bairro"].unique())
    filtro_bairro = st.selectbox("Bairro", bairros_disp, key="fb")

    # Filtro status — dinâmico conforme bairro selecionado
    if filtro_bairro != "Todos":
        status_disponiveis = emp[emp["bairro"] == filtro_bairro]["status"].unique().tolist()
    else:
        status_disponiveis = emp["status"].unique().tolist()

    status_labels_disp = ["Todos"] + [STATUS_LABELS[s] for s in status_disponiveis if s in STATUS_LABELS]
    filtro_status_label = st.selectbox("Status", status_labels_disp, key="fs")
    status_map_rev = {v:k for k,v in STATUS_LABELS.items()}
    filtro_status = status_map_rev.get(filtro_status_label, "Todos")

    # Filtro linha
    if filtro_bairro != "Todos":
        linhas_disp = emp[emp["bairro"] == filtro_bairro]["linha"].unique().tolist()
    else:
        linhas_disp = emp["linha"].unique().tolist()
    filtro_linha_opts = ["Todas"] + sorted(linhas_disp)
    filtro_linha = st.selectbox("Linha", filtro_linha_opts, key="fl")

pagina = st.session_state.pagina

# ── APLICAR FILTROS ───────────────────────────────────────────────────────────
emp_f = emp.copy()
if filtro_bairro != "Todos":
    emp_f = emp_f[emp_f["bairro"] == filtro_bairro]
if filtro_status != "Todos":
    emp_f = emp_f[emp_f["status"] == filtro_status]
if filtro_linha != "Todas":
    emp_f = emp_f[emp_f["linha"] == filtro_linha]

ids_f    = emp_f["id"].tolist()
vendas_f = vendas[vendas["id_empreendimento"].isin(ids_f)]
obra_f   = obra[obra["id_empreendimento"].isin(ids_f)]
dre_f    = dre[dre["id_empreendimento"].isin(ids_f)].copy()

if len(dre_f) == 0:
    st.warning("⚠️ Nenhum empreendimento encontrado para os filtros selecionados.")
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
#  VISÃO GERAL
# ═══════════════════════════════════════════════════════════════════════════════
if "Visão Geral" in pagina:
    st.markdown("## Visão Geral do Portfólio")
    st.caption(f"**{len(dre_f)} empreendimentos** selecionados · Alto padrão São Paulo · Dados sintéticos calibrados com Secovi-SP")

    # KPIs
    vgv_total   = emp_f["vgv_total"].sum()
    vgv_vendido = dre_f["vgv_vendido"].sum()
    margem_m    = dre_f["margem_bruta_pct"].mean()
    vso_m       = dre_f["vso_acumulado_pct"].mean()
    unidades_t  = emp_f["unidades"].sum()

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Empreendimentos",   f"{len(dre_f)}")
    c2.metric("VGV Total Lançado", fmt_M(vgv_total))
    c3.metric("VGV Vendido",       fmt_M(vgv_vendido), help="Soma do VGV comercializado")
    c4.metric("VSO Médio",         f"{vso_m:.1f}%",    help="Velocidade de vendas acumulada média")
    c5.metric("Margem Bruta Média",f"{margem_m:.1f}%", help="Margem bruta via método POC")

    st.markdown("---")

    # Linha 1: VGV bar + donut status
    col_a, col_b = st.columns([1.5, 1])
    with col_a:
        st.markdown("##### VGV Lançado por Empreendimento")
        plot = dre_f.sort_values("vgv_lancado").copy()
        fig = go.Figure()
        for sl, cor in STATUS_CORES.items():
            sub = plot[plot["status_label"]==sl]
            if len(sub):
                fig.add_trace(go.Bar(
                    x=sub["vgv_lancado"], y=sub["nome"],
                    name=sl, orientation="h",
                    marker_color=cor,
                    text=sub["vgv_lancado"].apply(fmt_M),
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>VGV: %{text}<extra></extra>",
                ))
        fig.update_layout(**LAYOUT_BASE, height=420,
                          barmode="stack", xaxis_tickformat=",.0f",
                          yaxis=dict(showgrid=False, gridcolor=C_CLARO))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("##### Status do Portfólio")
        sc = emp_f["status"].map(STATUS_LABELS).value_counts().reset_index()
        sc.columns = ["status","qtd"]
        fig2 = go.Figure(go.Pie(
            labels=sc["status"], values=sc["qtd"],
            hole=0.6,
            marker_colors=[STATUS_CORES.get(s, C_CINZA) for s in sc["status"]],
            textinfo="label+percent",
            hovertemplate="%{label}: %{value} empreend.<extra></extra>",
        ))
        fig2.update_layout(**{**LAYOUT_BASE,"margin":dict(l=0,r=0,t=30,b=0)},
                           height=200, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("##### Linha de Produto")
        lc = emp_f["linha"].value_counts().reset_index()
        lc.columns = ["linha","qtd"]
        fig3 = go.Figure(go.Bar(
            x=lc["linha"], y=lc["qtd"],
            marker_color=[LINHA_CORES.get(l, C_CINZA) for l in lc["linha"]],
            text=lc["qtd"], textposition="outside",
        ))
        fig3.update_layout(**LAYOUT_BASE, height=180,
                           xaxis=dict(showgrid=False), yaxis=dict(showgrid=False,visible=False))
        st.plotly_chart(fig3, use_container_width=True)

    # Linha 2: VGV evolução + mapa de bairros
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("##### VGV Lançado por Ano")
        emp_f["ano"] = emp_f["lancamento"].dt.year
        vgv_ano = emp_f.groupby(["ano","linha"])["vgv_total"].sum().reset_index()
        fig4 = px.bar(vgv_ano, x="ano", y="vgv_total", color="linha",
                      color_discrete_map=LINHA_CORES,
                      labels={"ano":"Ano","vgv_total":"VGV (R$)","linha":"Linha"},
                      barmode="stack")
        fig4.update_layout(**LAYOUT_BASE, height=260, yaxis_tickformat=",.0f")
        st.plotly_chart(fig4, use_container_width=True)

    with col_d:
        st.markdown("##### VGV por Bairro")
        vgv_b = emp_f.groupby("bairro")["vgv_total"].sum().reset_index().sort_values("vgv_total",ascending=True)
        fig5 = go.Figure(go.Bar(
            x=vgv_b["vgv_total"], y=vgv_b["bairro"], orientation="h",
            marker_color=C_AREIA,
            text=vgv_b["vgv_total"].apply(fmt_M), textposition="outside",
        ))
        fig5.update_layout(**LAYOUT_BASE, height=260, xaxis_tickformat=",.0f",
                           yaxis=dict(showgrid=False))
        st.plotly_chart(fig5, use_container_width=True)

    # Insights
    st.markdown("---")
    st.markdown("##### 💡 Análise do Portfólio")
    ic1, ic2, ic3 = st.columns(3)
    melhor = dre_f.loc[dre_f["margem_bruta_pct"].idxmax()]
    pior_vso = dre_f.loc[dre_f["vso_acumulado_pct"].idxmin()]
    em_obra_vgv = emp_f[emp_f["status"]=="em_obra"]["vgv_total"].sum()
    lanc_vgv    = emp_f[emp_f["status"]=="lancamento"]["vgv_total"].sum()
    with ic1:
        insight(f"<strong>{melhor['nome']}</strong> lidera com margem bruta de <strong>{melhor['margem_bruta_pct']:.1f}%</strong> — {melhor['margem_bruta_pct']-30:.1f}pp acima do benchmark de 30% do mercado SP.", "positivo")
    with ic2:
        insight(f"<strong>{fmt_M(em_obra_vgv)}</strong> em VGV atualmente em obra. Pipeline de lançamentos de <strong>{fmt_M(lanc_vgv)}</strong> garantem crescimento nos próximos ciclos.", "info")
    with ic3:
        if pior_vso["vso_acumulado_pct"] < 75:
            insight(f"Atenção: <strong>{pior_vso['nome']}</strong> com VSO acumulado de <strong>{pior_vso['vso_acumulado_pct']:.1f}%</strong>. Revisar estratégia comercial ou mix de tipologias.", "alerta")
        else:
            insight(f"VSO acumulado médio de <strong>{vso_m:.1f}%</strong> em linha com o mercado SP. Lançamentos recentes ainda em aceleração comercial.", "neutro")

    # Tabela resumo
    st.markdown("---")
    st.markdown("##### Portfólio Completo")
    tab = dre_f[["nome","bairro","linha","status_label","vgv_lancado","vso_acumulado_pct",
                 "avanco_obra_pct","margem_bruta_pct","ebitda_pct"]].copy()
    tab.columns = ["Empreendimento","Bairro","Linha","Status","VGV Lançado","VSO %","Avanço %","Margem %","EBITDA %"]
    tab["VGV Lançado"] = tab["VGV Lançado"].apply(fmt_M)
    st.dataframe(tab, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  COMERCIAL & VSO
# ═══════════════════════════════════════════════════════════════════════════════
elif "Comercial" in pagina:
    st.markdown("## Comercial & VSO")
    st.caption("Velocidade de Vendas · Distratos · VGV mensal")

    sel = st.selectbox("Empreendimento", ["Portfólio Consolidado"] + dre_f["nome"].tolist())

    if sel != "Portfólio Consolidado":
        id_sel = dre_f[dre_f["nome"]==sel]["id_empreendimento"].values[0]
        vp = vendas_f[vendas_f["id_empreendimento"]==id_sel].copy()
    else:
        vp = vendas_f.groupby("data").agg(
            unidades_vendidas=("unidades_vendidas","sum"),
            distratos=("distratos","sum"),
            vgv_mes=("vgv_mes","sum"),
            vso_pct=("vso_pct","mean"),
        ).reset_index()

    total_v   = vp["unidades_vendidas"].sum()
    total_d   = vp["distratos"].sum()
    vgv_com   = vp["vgv_mes"].sum()
    taxa_dist = total_d/total_v*100 if total_v>0 else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Unidades Vendidas",  f"{total_v:,.0f}")
    c2.metric("Distratos",          f"{total_d:,.0f}", delta=f"-{taxa_dist:.1f}% da base", delta_color="inverse")
    c3.metric("VGV Comercializado", fmt_M(vgv_com))
    vso_rec = vp.sort_values("data").iloc[-1]["vso_pct"] if len(vp) else 0
    c4.metric("VSO Último Mês",     f"{vso_rec:.1f}%", delta="acima de 10%" if vso_rec>=10 else "abaixo de 10%", delta_color="normal" if vso_rec>=10 else "inverse")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### VSO Mensal (%)")
        vp_s = vp.sort_values("data")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=vp_s["data"], y=vp_s["vso_pct"],
                                  mode="lines+markers", line=dict(color=C_PRETO, width=2),
                                  marker=dict(size=4, color=C_AREIA),
                                  fill="tozeroy", fillcolor="rgba(212,184,150,0.12)",
                                  name="VSO"))
        fig.add_hline(y=10, line_dash="dash", line_color=C_VERM, line_width=1,
                      annotation_text="Mínimo saudável 10%", annotation_font_size=10)
        fig.update_layout(**LAYOUT_BASE, height=260)
        st.plotly_chart(fig, use_container_width=True)
        if vso_rec < 10:
            insight(f"VSO mais recente de <strong>{vso_rec:.1f}%</strong> está abaixo do mínimo saudável de 10% para o mercado SP. Avaliar campanhas de incentivo ou revisão de preços.", "alerta")
        else:
            insight(f"VSO de <strong>{vso_rec:.1f}%</strong> acima do benchmark de 10% — ritmo comercial saudável.", "positivo")

    with col2:
        st.markdown("##### VGV Mensal Comercializado")
        fig2 = go.Figure(go.Bar(
            x=vp_s["data"], y=vp_s["vgv_mes"],
            marker_color=C_PRETO,
            hovertemplate="%{x|%b/%Y}: %{customdata}<extra></extra>",
            customdata=vp_s["vgv_mes"].apply(fmt_M),
        ))
        fig2.update_layout(**LAYOUT_BASE, height=260, yaxis_tickformat=",.0f")
        st.plotly_chart(fig2, use_container_width=True)
        mes_pico = vp.loc[vp["vgv_mes"].idxmax(),"data"]
        insight(f"Pico de comercialização em <strong>{mes_pico.strftime('%b/%Y')}</strong> com {fmt_M(vp['vgv_mes'].max())} — tipicamente associado ao lançamento.", "info")

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("##### Vendas vs Distratos (mensal)")
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=vp_s["data"], y=vp_s["unidades_vendidas"],
                               name="Vendidas", marker_color=C_PRETO))
        fig3.add_trace(go.Bar(x=vp_s["data"], y=vp_s["distratos"],
                               name="Distratos", marker_color=C_AREIA))
        fig3.update_layout(**LAYOUT_BASE, height=260, barmode="group")
        st.plotly_chart(fig3, use_container_width=True)
        cor_d = "alerta" if taxa_dist>5 else "positivo"
        insight(f"Taxa de distrato acumulada: <strong>{taxa_dist:.1f}%</strong> — {'acima' if taxa_dist>5 else 'dentro'} do limite aceitável de 5% do setor.", cor_d)

    with col4:
        st.markdown("##### VSO Acumulado por Bairro")
        vso_b = dre_f.groupby("bairro")["vso_acumulado_pct"].mean().reset_index().sort_values("vso_acumulado_pct",ascending=True)
        cores_vso = [C_VERM if v<70 else (C_AREIA if v<85 else C_VERDE) for v in vso_b["vso_acumulado_pct"]]
        fig4 = go.Figure(go.Bar(
            x=vso_b["vso_acumulado_pct"], y=vso_b["bairro"],
            orientation="h", marker_color=cores_vso,
            text=[f"{v:.1f}%" for v in vso_b["vso_acumulado_pct"]],
            textposition="outside",
        ))
        fig4.update_layout(**LAYOUT_BASE, height=260,
                           xaxis=dict(range=[0,110], showgrid=True, gridcolor=C_CLARO))
        fig4.add_vline(x=85, line_dash="dash", line_color=C_CINZA, line_width=1,
                       annotation_text="Meta 85%", annotation_font_size=10)
        st.plotly_chart(fig4, use_container_width=True)
        top_bairro = vso_b.iloc[-1]
        insight(f"<strong>{top_bairro['bairro']}</strong> lidera o VSO acumulado com <strong>{top_bairro['vso_acumulado_pct']:.1f}%</strong> — reflete alta demanda por imóveis de alto padrão na região.", "positivo")


# ═══════════════════════════════════════════════════════════════════════════════
#  OBRAS & POC
# ═══════════════════════════════════════════════════════════════════════════════
elif "Obras" in pagina:
    st.markdown("## Obras & POC")
    st.caption("Percentage of Completion · Curva S · Controle de Orçamento")

    opcoes = obra_f["nome_empreendimento"].unique().tolist()
    if not opcoes:
        st.warning("Nenhum dado para os filtros selecionados.")
        st.stop()

    sel_obra = st.selectbox("Empreendimento", opcoes)
    o = obra_f[obra_f["nome_empreendimento"]==sel_obra]

    av   = o["avanco_fisico_pct"].iloc[0]
    rpoc = o["receita_reconhecida_poc"].iloc[0]
    corc = o["custo_orcado"].sum()
    crea = o["custo_realizado"].sum()
    dmed = o["desvio_pct"].mean()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Avanço Físico (POC)", f"{av:.0f}%")
    c2.metric("Receita Reconhecida", fmt_M(rpoc), help="Receita pelo método POC")
    c3.metric("Custo Realizado",     fmt_M(crea),  delta=fmt_M(crea-corc), delta_color="inverse")
    c4.metric("Desvio Médio",        f"{dmed:+.1f}%", delta_color="inverse")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Orçado vs Realizado por Etapa")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=o["etapa_obra"], y=o["custo_orcado"],
                             name="Orçado", marker_color=C_CLARO,
                             marker_line=dict(color=C_CINZA, width=1)))
        fig.add_trace(go.Bar(x=o["etapa_obra"], y=o["custo_realizado"],
                             name="Realizado", marker_color=C_PRETO))
        fig.update_layout(**LAYOUT_BASE, height=280, barmode="group", yaxis_tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)

        etapa_crit = o.loc[o["desvio_pct"].idxmax(),"etapa_obra"]
        dev_crit   = o["desvio_pct"].max()
        cor_e = "alerta" if dev_crit>8 else ("neutro" if dev_crit>3 else "positivo")
        insight(f"Etapa de maior desvio: <strong>{etapa_crit}</strong> com <strong>{dev_crit:+.1f}%</strong> sobre o orçado. {'Requer atenção imediata.' if dev_crit>8 else 'Dentro da margem tolerável de obra.'}", cor_e)

    with col2:
        st.markdown("##### Desvio de Custo por Etapa (%)")
        cores_d = [C_VERM if d>8 else (C_AREIA if d>0 else C_VERDE) for d in o["desvio_pct"]]
        fig2 = go.Figure(go.Bar(
            x=o["etapa_obra"], y=o["desvio_pct"],
            marker_color=cores_d,
            text=[f"{d:+.1f}%" for d in o["desvio_pct"]],
            textposition="outside",
        ))
        fig2.add_hline(y=0, line_color=C_CINZA, line_width=1)
        fig2.add_hline(y=8, line_dash="dash", line_color=C_VERM, line_width=1,
                       annotation_text="Limite crítico +8%", annotation_font_size=10)
        fig2.update_layout(**LAYOUT_BASE, height=280, yaxis_title="Desvio (%)")
        st.plotly_chart(fig2, use_container_width=True)
        delta_total = crea - corc
        cor_dt = "alerta" if delta_total>0 else "positivo"
        insight(f"Desvio total de custo: <strong>{fmt_M(abs(delta_total))}</strong> {'acima' if delta_total>0 else 'abaixo'} do orçamento original. Impacto direto na margem bruta projetada.", cor_dt)

    # Curva S
    st.markdown("---")
    st.markdown("##### Curva S — Avanço Físico vs Planejado")
    meses = list(range(1,43))
    plan  = [min(100,(m/36)**1.15*100) for m in meses]
    real  = [min(av, min(100, p*(1+0.04*(1 if m<18 else -0.3))+(m*0.25))) for m,p in zip(meses,plan)]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=meses, y=plan, name="Cronograma Planejado",
                               line=dict(color=C_CLARO, width=2, dash="dash")))
    fig3.add_trace(go.Scatter(x=meses, y=real, name="Avanço Realizado",
                               line=dict(color=C_PRETO, width=2.5),
                               fill="tonexty", fillcolor="rgba(212,184,150,0.15)"))
    fig3.add_vline(x=av/100*36, line_dash="dot", line_color=C_AREIA, line_width=2,
                   annotation_text=f"Posição atual: {av:.0f}%",
                   annotation_font_color=C_AREIA, annotation_font_size=11)
    fig3.update_layout(**LAYOUT_BASE, height=300,
                       xaxis_title="Mês de obra", yaxis_title="Avanço Físico (%)",
                       yaxis=dict(range=[0,110], showgrid=True, gridcolor=C_CLARO))
    st.plotly_chart(fig3, use_container_width=True)

    atraso = plan[int(av/100*36)-1] - av if av < 100 else 0
    if atraso > 5:
        insight(f"A obra apresenta atraso de <strong>{atraso:.1f}pp</strong> em relação ao cronograma planejado. Risco de impacto no reconhecimento de receita (POC) do próximo trimestre.", "alerta")
    else:
        insight(f"Avanço de <strong>{av:.0f}%</strong> alinhado ao cronograma. Receita reconhecida via POC de <strong>{fmt_M(rpoc)}</strong> reflete o estágio atual da obra.", "positivo")

    # Comparativo POC
    st.markdown("---")
    st.markdown("##### POC Consolidado — Todos os Empreendimentos")
    poc = obra_f.groupby("nome_empreendimento").first().reset_index()[["nome_empreendimento","avanco_fisico_pct","receita_reconhecida_poc"]]
    poc = poc.sort_values("avanco_fisico_pct", ascending=True)
    cores_poc = [C_VERM if v<30 else (C_AREIA if v<70 else C_VERDE) for v in poc["avanco_fisico_pct"]]
    fig4 = go.Figure(go.Bar(
        x=poc["avanco_fisico_pct"], y=poc["nome_empreendimento"],
        orientation="h", marker_color=cores_poc,
        text=[f"{v:.0f}%" for v in poc["avanco_fisico_pct"]],
        textposition="outside",
        customdata=poc["receita_reconhecida_poc"].apply(fmt_M),
        hovertemplate="<b>%{y}</b><br>POC: %{x:.0f}%<br>Receita reconhecida: %{customdata}<extra></extra>",
    ))
    fig4.add_vline(x=50, line_dash="dash", line_color=C_CINZA, line_width=1,
                   annotation_text="50%", annotation_font_size=10)
    fig4.update_layout(**LAYOUT_BASE, height=380,
                       xaxis=dict(range=[0,115], showgrid=True, gridcolor=C_CLARO),
                       yaxis=dict(showgrid=False))
    st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  DRE GERENCIAL
# ═══════════════════════════════════════════════════════════════════════════════
elif "DRE" in pagina:
    st.markdown("## DRE Gerencial")
    st.caption("Resultado econômico pelo método POC · Por empreendimento · Receita proporcional ao avanço físico")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Receita Total POC",  fmt_M(dre_f["receita_reconhecida_poc"].sum()))
    c2.metric("Custo Total POC",    fmt_M(dre_f["custo_obra_poc"].sum()))
    c3.metric("Margem Bruta Média", f"{dre_f['margem_bruta_pct'].mean():.1f}%")
    ebitda_pos = dre_f[dre_f["ebitda"]>0]["ebitda"].sum()
    c4.metric("EBITDA Positivo",    fmt_M(ebitda_pos), help="Obras com avanço > 30%")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Margem Bruta por Empreendimento (%)")
        df_m = dre_f.sort_values("margem_bruta_pct")
        cores_m = [C_VERM if v<25 else (C_AREIA if v<33 else C_VERDE) for v in df_m["margem_bruta_pct"]]
        fig = go.Figure(go.Bar(
            x=df_m["margem_bruta_pct"], y=df_m["nome"],
            orientation="h", marker_color=cores_m,
            text=[f"{v:.1f}%" for v in df_m["margem_bruta_pct"]],
            textposition="outside",
        ))
        fig.add_vline(x=30, line_dash="dash", line_color=C_CINZA, line_width=1,
                      annotation_text="Benchmark 30%", annotation_font_size=10)
        fig.update_layout(**LAYOUT_BASE, height=440,
                          xaxis=dict(range=[0,55], showgrid=True, gridcolor=C_CLARO),
                          yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)
        melhor = dre_f.loc[dre_f["margem_bruta_pct"].idxmax()]
        pior   = dre_f.loc[dre_f["margem_bruta_pct"].idxmin()]
        insight(f"<strong>{melhor['nome']}</strong>: margem de {melhor['margem_bruta_pct']:.1f}% — melhor resultado do portfólio. <strong>{pior['nome']}</strong>: {pior['margem_bruta_pct']:.1f}% — monitorar evolução de custos.", "info")

    with col2:
        st.markdown("##### Waterfall DRE — Consolidado")
        receita = dre_f["receita_reconhecida_poc"].sum()
        custo   = dre_f["custo_obra_poc"].sum()
        desp_c  = dre_f["despesas_comerciais"].sum()
        desp_a  = dre_f["despesas_administrativas"].sum()
        ebitda  = receita-custo-desp_c-desp_a
        fig2 = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute","relative","relative","relative","total"],
            x=["Receita\nPOC","Custo\nde Obra","Desp.\nComercial","Desp.\nAdm.","EBITDA"],
            y=[receita,-custo,-desp_c,-desp_a,0],
            text=[fmt_M(v) for v in [receita,custo,desp_c,desp_a,ebitda]],
            textposition="outside",
            connector={"line":{"color":C_CLARO}},
            increasing={"marker":{"color":C_VERDE}},
            decreasing={"marker":{"color":C_VERM}},
            totals={"marker":{"color":C_PRETO}},
        ))
        fig2.update_layout(**{**LAYOUT_BASE,"xaxis":dict(showgrid=False)},
                           height=280, showlegend=False, yaxis_tickformat=",.0f")
        st.plotly_chart(fig2, use_container_width=True)
        margem_ebitda = ebitda/receita*100 if receita>0 else 0
        cor_e = "positivo" if margem_ebitda>15 else ("alerta" if margem_ebitda<8 else "neutro")
        insight(f"EBITDA consolidado de <strong>{fmt_M(ebitda)}</strong> ({margem_ebitda:.1f}% de margem EBITDA). {'Desempenho acima da média do setor.' if margem_ebitda>15 else 'Margem EBITDA abaixo de 15% — atenção ao controle de despesas.'}", cor_e)

        # Margem por linha
        st.markdown("##### Margem Bruta por Linha de Produto")
        ml = dre_f.groupby("linha")["margem_bruta_pct"].mean().reset_index()
        fig3 = go.Figure(go.Bar(
            x=ml["linha"], y=ml["margem_bruta_pct"],
            marker_color=[LINHA_CORES.get(l,C_CINZA) for l in ml["linha"]],
            text=[f"{v:.1f}%" for v in ml["margem_bruta_pct"]],
            textposition="outside",
        ))
        fig3.add_hline(y=30, line_dash="dash", line_color=C_CINZA, line_width=1)
        fig3.update_layout(**LAYOUT_BASE, height=200,
                           yaxis=dict(range=[0,50], showgrid=True, gridcolor=C_CLARO),
                           xaxis=dict(showgrid=False))
        st.plotly_chart(fig3, use_container_width=True)

    # Scatter margem x VSO
    st.markdown("---")
    st.markdown("##### Análise Bidimensional: Margem Bruta × VSO Acumulado")
    fig4 = go.Figure()
    for sl, cor in STATUS_CORES.items():
        sub = dre_f[dre_f["status_label"]==sl]
        if len(sub):
            fig4.add_trace(go.Scatter(
                x=sub["vso_acumulado_pct"], y=sub["margem_bruta_pct"],
                mode="markers+text",
                name=sl, marker=dict(color=cor, size=sub["vgv_lancado"]/4_000_000+8, opacity=0.85,
                                      line=dict(color="#FFFFFF", width=1)),
                text=sub["nome"], textposition="top center",
                textfont=dict(size=9, color=C_CINZA),
                hovertemplate="<b>%{text}</b><br>VSO: %{x:.1f}%<br>Margem: %{y:.1f}%<extra></extra>",
            ))
    fig4.add_hline(y=30, line_dash="dash", line_color=C_CINZA, line_width=1,
                   annotation_text="Margem benchmark 30%", annotation_font_size=10)
    fig4.add_vline(x=80, line_dash="dash", line_color=C_CINZA, line_width=1,
                   annotation_text="VSO meta 80%", annotation_font_size=10)
    fig4.update_layout(**LAYOUT_BASE, height=420,
                       xaxis=dict(title="VSO Acumulado (%)", range=[0,105], showgrid=True, gridcolor=C_CLARO),
                       yaxis=dict(title="Margem Bruta (%)", range=[0,55], showgrid=True, gridcolor=C_CLARO))
    st.plotly_chart(fig4, use_container_width=True)
    q_ideal = len(dre_f[(dre_f["vso_acumulado_pct"]>=80)&(dre_f["margem_bruta_pct"]>=30)])
    insight(f"<strong>{q_ideal} de {len(dre_f)} empreendimentos</strong> atingem simultaneamente VSO ≥ 80% e margem ≥ 30% — quadrante ideal de desempenho do portfólio.", "positivo" if q_ideal>len(dre_f)//2 else "neutro")

    # Tabela DRE
    st.markdown("---")
    st.markdown("##### DRE Detalhado")
    cols = ["nome","linha","status_label","vgv_lancado","vso_acumulado_pct",
            "receita_reconhecida_poc","custo_obra_poc","margem_bruta_pct","ebitda","ebitda_pct"]
    tab = dre_f[cols].copy()
    for c in ["vgv_lancado","receita_reconhecida_poc","custo_obra_poc","ebitda"]:
        tab[c] = tab[c].apply(fmt_M)
    tab.columns = ["Empreendimento","Linha","Status","VGV","VSO %","Receita POC","Custo POC","Margem %","EBITDA","EBITDA %"]
    st.dataframe(tab, use_container_width=True, hide_index=True)
