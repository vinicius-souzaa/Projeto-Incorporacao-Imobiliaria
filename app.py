import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(
    page_title="Portfólio Imobiliário | Analytics SP",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════
#  PALETA NAVY & GOLD — Clássico Corporativo
# ══════════════════════════════════════════════════════════════════
C_NAVY    = "#0D2137"
C_NAVY2   = "#152C47"
C_NAVY3   = "#1A3555"
C_GOLD    = "#C9A84C"
C_GOLD_L  = "#E8C96A"
C_BG      = "#0F1923"   # fundo escuro das páginas
C_CARD    = "#162330"   # cards sobre fundo escuro
C_BORDER  = "#1E3045"   # bordas
C_TEXT    = "#E8EDF2"   # texto principal
C_MUTED   = "#7A93A8"   # texto secundário
C_VERDE   = "#2ECC71"
C_VERM    = "#E74C3C"
C_AZUL    = "#3498DB"
C_PLOT_BG = "#162330"   # fundo dos gráficos (escuro)
C_GRID    = "#1E3045"   # grid dos gráficos

STATUS_LABELS = {
    "entregue":   "Entregue",
    "em_obra":    "Em Obra",
    "lancamento": "Lançamento",
}
STATUS_CORES  = {"Entregue": C_VERDE, "Em Obra": C_AZUL, "Lançamento": C_GOLD}
LINHA_CORES   = {"Premium": C_GOLD, "Alto Padrão": C_AZUL, "Smart": C_MUTED}

# ── CSS ───────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}

/* Fundo geral escuro */
.stApp {{ background-color: {C_BG}; }}
.main .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: {C_NAVY} !important;
    border-right: 1px solid {C_BORDER};
}}
[data-testid="stSidebar"] * {{ color: #B0C4D8 !important; }}
[data-testid="stSidebar"] .stSelectbox > label {{
    color: {C_GOLD} !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: .1em;
}}
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 !important;
    color: #7A93A8 !important;
    font-size: 13px !important;
    text-align: left !important;
    padding: 10px 18px !important;
    width: 100% !important;
    transition: all .15s ease;
    font-weight: 400 !important;
    letter-spacing: .015em;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(201,168,76,.10) !important;
    color: {C_GOLD_L} !important;
    border-left-color: {C_GOLD} !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    color: #F0E6C8 !important;
    border-left-color: {C_GOLD} !important;
    background: rgba(201,168,76,.16) !important;
    font-weight: 600 !important;
}}

/* Selectbox fundo escuro */
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {{
    background: {C_NAVY2} !important;
    border-color: {C_BORDER} !important;
    color: {C_TEXT} !important;
}}

/* Métricas */
[data-testid="stMetric"] {{
    background: {C_CARD} !important;
    border: 1px solid {C_BORDER} !important;
    border-top: 3px solid {C_GOLD} !important;
    border-radius: 8px;
    padding: 16px 20px !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: .07em;
    color: {C_MUTED} !important;
    font-weight: 600 !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 24px !important;
    color: {C_TEXT} !important;
    font-weight: 700 !important;
}}
[data-testid="stMetricDelta"] {{ font-size: 12px !important; }}

/* Títulos */
h1, h2, h3, h4, h5 {{ color: {C_TEXT} !important; }}
h1 {{ font-weight: 700 !important; font-size: 24px !important; letter-spacing: -.3px; }}
h2 {{ font-weight: 600 !important; font-size: 20px !important; }}
p, span, div, label {{ color: {C_TEXT}; }}

/* Caption / subtitle de gráfico */
.chart-title {{
    font-size: 13px;
    font-weight: 600;
    color: {C_TEXT};
    margin-bottom: 2px;
    letter-spacing: .01em;
}}
.chart-desc {{
    font-size: 11px;
    color: {C_MUTED};
    margin-bottom: 8px;
    line-height: 1.5;
    font-style: italic;
}}

/* Cards de insight */
.ins {{
    border-left: 4px solid {C_GOLD};
    background: {C_CARD};
    padding: 11px 15px;
    border-radius: 0 6px 6px 0;
    margin-bottom: 8px;
    font-size: 12.5px;
    color: {C_TEXT};
    line-height: 1.55;
}}
.ins.ok   {{ border-left-color: {C_VERDE}; background: #0E2119; }}
.ins.bad  {{ border-left-color: {C_VERM};  background: #200D0D; }}
.ins.info {{ border-left-color: {C_AZUL};  background: #0C1E2D; }}
.ins.warn {{ border-left-color: {C_GOLD};  background: {C_CARD}; }}

/* Divisor */
hr {{ border-color: {C_BORDER}; margin: 1rem 0; }}

/* Dataframe */
[data-testid="stDataFrame"] {{
    border: 1px solid {C_BORDER} !important;
    border-radius: 8px;
}}

/* Caption */
.stCaption p {{ color: {C_MUTED} !important; font-size: 12px !important; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  DADOS
# ══════════════════════════════════════════════════════════════════
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@st.cache_data
def load_all():
    emp    = pd.read_csv(os.path.join(DATA_DIR, "empreendimentos.csv"), parse_dates=["lancamento","entrega_prevista"])
    vendas = pd.read_csv(os.path.join(DATA_DIR, "vendas_mensais.csv"),  parse_dates=["data"])
    obra   = pd.read_csv(os.path.join(DATA_DIR, "custo_obra.csv"))
    dre    = pd.read_csv(os.path.join(DATA_DIR, "dre_gerencial.csv"))
    return emp, vendas, obra, dre

emp, vendas, obra, dre = load_all()
dre["status_label"] = dre["status"].map(STATUS_LABELS)

# ── HELPERS ───────────────────────────────────────────────────────
def fmt_M(v):
    try:
        v = float(v)
        return f"R$ {v/1_000_000:.1f}M" if abs(v) >= 1_000_000 else f"R$ {v/1_000:.0f}K"
    except:
        return "—"

def ins(txt, tipo="warn"):
    st.markdown(f'<div class="ins {tipo}">{txt}</div>', unsafe_allow_html=True)

def chart_header(titulo, descricao):
    st.markdown(f'<p class="chart-title">{titulo}</p><p class="chart-desc">{descricao}</p>', unsafe_allow_html=True)

def plot_layout(height=300, **kwargs):
    """Retorna dict de layout Plotly com tema escuro Navy & Gold."""
    base = dict(
        height=height,
        plot_bgcolor=C_PLOT_BG,
        paper_bgcolor=C_PLOT_BG,
        font=dict(family="Inter, sans-serif", color=C_TEXT, size=11),
        margin=dict(l=12, r=20, t=10, b=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            bgcolor="rgba(0,0,0,0)", font=dict(size=10, color=C_MUTED),
        ),
    )
    base.update(kwargs)
    return base

def ax(title="", fmt="", rng=None, grid=True, tickangle=0):
    d = dict(
        title=dict(text=title, font=dict(size=10, color=C_MUTED)),
        showgrid=grid, gridcolor=C_GRID, gridwidth=1,
        zeroline=False,
        tickfont=dict(size=10, color=C_MUTED),
        tickangle=tickangle,
        linecolor=C_BORDER, linewidth=1, showline=True,
    )
    if fmt:  d["tickformat"] = fmt
    if rng:  d["range"] = rng
    return d

def axh():
    return dict(showgrid=False, zeroline=False, showline=False,
                tickfont=dict(size=10, color=C_MUTED), title="")

# ══════════════════════════════════════════════════════════════════
#  SIDEBAR — filtros encadeados
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="padding:22px 16px 10px;">
        <div style="font-size:10px;color:{C_GOLD};text-transform:uppercase;
                    letter-spacing:.14em;font-weight:700;">Portfólio Imobiliário</div>
        <div style="font-size:12px;color:{C_MUTED};margin-top:3px;">Analytics · São Paulo SP</div>
    </div>
    <hr style="border-color:{C_BORDER};margin:0 0 6px;">
    """, unsafe_allow_html=True)

    paginas = [
        "🏠  Visão Geral",
        "📈  Comercial & Velocidade de Vendas",
        "🏗️  Obras & % de Conclusão",
        "📊  DRE Gerencial",
    ]
    if "pagina" not in st.session_state:
        st.session_state.pagina = paginas[0]
    for p in paginas:
        ativo = st.session_state.pagina == p
        if st.button(p, key=p, use_container_width=True,
                     type="primary" if ativo else "secondary"):
            st.session_state.pagina = p
            st.rerun()

    st.markdown(f'<hr style="border-color:{C_BORDER};margin:8px 0 4px;">', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:10px;color:{C_GOLD};text-transform:uppercase;'
                f'letter-spacing:.1em;font-weight:700;padding:4px 4px 6px;">Filtros</p>',
                unsafe_allow_html=True)

    # 1) Bairro
    bairros_all = sorted(emp["bairro"].unique())
    filtro_bairro = st.selectbox("Bairro", ["Todos"] + bairros_all, key="fb")

    # 2) Status — depende do bairro
    emp_b = emp if filtro_bairro == "Todos" else emp[emp["bairro"] == filtro_bairro]
    status_raw = sorted(emp_b["status"].unique().tolist())
    status_opts = ["Todos"] + [STATUS_LABELS[s] for s in status_raw if s in STATUS_LABELS]
    if "fs" not in st.session_state or st.session_state.get("_last_bairro") != filtro_bairro:
        st.session_state["fs"] = "Todos"
    st.session_state["_last_bairro"] = filtro_bairro
    filtro_status_lbl = st.selectbox("Status", status_opts, key="fs")
    status_rev = {v: k for k, v in STATUS_LABELS.items()}
    filtro_status = status_rev.get(filtro_status_lbl, "Todos")

    # 3) Linha — depende de bairro + status
    emp_bs = emp_b if filtro_status == "Todos" else emp_b[emp_b["status"] == filtro_status]
    linhas_raw = sorted(emp_bs["linha"].unique().tolist())
    linhas_opts = ["Todas"] + linhas_raw
    if "fl" not in st.session_state or st.session_state.get("_last_status") != filtro_status_lbl:
        st.session_state["fl"] = "Todas"
    st.session_state["_last_status"] = filtro_status_lbl
    filtro_linha = st.selectbox("Linha de Produto", linhas_opts, key="fl")

pagina = st.session_state.pagina

# ── Aplicar filtros ───────────────────────────────────────────────
emp_f = emp.copy()
if filtro_bairro != "Todos":  emp_f = emp_f[emp_f["bairro"]  == filtro_bairro]
if filtro_status != "Todos":  emp_f = emp_f[emp_f["status"]  == filtro_status]
if filtro_linha  != "Todas":  emp_f = emp_f[emp_f["linha"]   == filtro_linha]

ids_f    = emp_f["id"].tolist()
vendas_f = vendas[vendas["id_empreendimento"].isin(ids_f)]
obra_f   = obra[obra["id_empreendimento"].isin(ids_f)]
dre_f    = dre[dre["id_empreendimento"].isin(ids_f)].copy()

if len(dre_f) == 0:
    st.warning("⚠️ Nenhum empreendimento encontrado para os filtros selecionados.")
    st.stop()


# ══════════════════════════════════════════════════════════════════
#  VISÃO GERAL
# ══════════════════════════════════════════════════════════════════
if "Visão Geral" in pagina:

    st.markdown("## Visão Geral do Portfólio")
    st.caption(f"**{len(dre_f)} empreendimentos** selecionados · Alto padrão São Paulo · Dados sintéticos calibrados com Secovi-SP / ABRAINC-FIPE")

    vgv_total   = emp_f["vgv_total"].sum()
    vgv_vendido = dre_f["vgv_vendido"].sum()
    margem_m    = dre_f["margem_bruta_pct"].mean()
    vso_m       = dre_f["vso_acumulado_pct"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Empreendimentos",                       f"{len(dre_f)}")
    c2.metric("Valor Geral de Vendas Total",           fmt_M(vgv_total))
    c3.metric("Valor Geral de Vendas Vendido",         fmt_M(vgv_vendido))
    c4.metric("Velocidade de Vendas Média",            f"{vso_m:.1f}%")
    c5.metric("Margem Bruta Média",                    f"{margem_m:.1f}%")

    st.markdown("---")
    col_a, col_b = st.columns([1.5, 1])

    with col_a:
        chart_header(
            "Valor Geral de Vendas (VGV) por Empreendimento",
            "Potencial máximo de receita de cada projeto ao preço de tabela, segmentado por status atual. "
            "Empreendimentos maiores representam maior exposição financeira e potencial de resultado."
        )
        plot = dre_f.sort_values("vgv_lancado").copy()
        fig = go.Figure()
        for sl, cor in STATUS_CORES.items():
            sub = plot[plot["status_label"] == sl]
            if len(sub):
                fig.add_trace(go.Bar(
                    x=sub["vgv_lancado"], y=sub["nome"],
                    name=sl, orientation="h", marker_color=cor,
                    text=sub["vgv_lancado"].apply(fmt_M),
                    textposition="outside",
                    textfont=dict(size=10, color=C_MUTED),
                    hovertemplate="<b>%{y}</b><br>VGV: %{text}<extra></extra>",
                ))
        fig.update_layout(
            **plot_layout(height=430, barmode="stack"),
            xaxis=ax(fmt=",.0f"),
            yaxis=axh(),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        chart_header(
            "Distribuição por Status",
            "Proporção do portfólio entre empreendimentos entregues, em obra e em lançamento. "
            "Indica o estágio do ciclo de desenvolvimento."
        )
        sc = emp_f["status"].map(STATUS_LABELS).value_counts().reset_index()
        sc.columns = ["status", "qtd"]
        fig2 = go.Figure(go.Pie(
            labels=sc["status"], values=sc["qtd"], hole=0.62,
            marker_colors=[STATUS_CORES.get(s, C_MUTED) for s in sc["status"]],
            textinfo="label+percent",
            textfont=dict(size=10, color=C_TEXT),
            hovertemplate="%{label}: %{value} empreend.<extra></extra>",
        ))
        fig2.update_layout(
            plot_bgcolor=C_PLOT_BG, paper_bgcolor=C_PLOT_BG,
            font=dict(family="Inter, sans-serif", color=C_TEXT, size=11),
            height=190, showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

        chart_header(
            "Distribuição por Linha de Produto",
            "Segmentação entre Premium, Alto Padrão e Smart — cada linha tem perfil de margem e público distintos."
        )
        lc = emp_f["linha"].value_counts().reset_index()
        lc.columns = ["linha", "qtd"]
        fig3 = go.Figure(go.Bar(
            x=lc["linha"], y=lc["qtd"],
            marker_color=[LINHA_CORES.get(l, C_MUTED) for l in lc["linha"]],
            text=lc["qtd"], textposition="outside",
            textfont=dict(size=11, color=C_MUTED),
        ))
        fig3.update_layout(
            **plot_layout(height=175),
            xaxis=ax(grid=False),
            yaxis=dict(visible=False, showgrid=False, zeroline=False),
        )
        st.plotly_chart(fig3, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        chart_header(
            "Evolução do VGV Lançado por Ano",
            "Volume de novos empreendimentos lançados ao longo dos anos, por linha de produto. "
            "Crescimento indica expansão do portfólio; concentração em uma linha indica foco estratégico."
        )
        emp_f2 = emp_f.copy()
        emp_f2["ano"] = emp_f2["lancamento"].dt.year
        vgv_ano = emp_f2.groupby(["ano", "linha"])["vgv_total"].sum().reset_index()
        fig4 = px.bar(vgv_ano, x="ano", y="vgv_total", color="linha",
                      color_discrete_map=LINHA_CORES, barmode="stack",
                      labels={"ano": "Ano", "vgv_total": "VGV (R$)", "linha": "Linha"})
        fig4.update_layout(
            **plot_layout(height=250),
            xaxis=ax(grid=False),
            yaxis=ax(fmt=",.0f"),
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col_d:
        chart_header(
            "VGV Total por Bairro",
            "Concentração geográfica do portfólio. Bairros com maior VGV representam "
            "maior exposição de capital e risco de mercado localizado."
        )
        vgv_b = emp_f.groupby("bairro")["vgv_total"].sum().reset_index().sort_values("vgv_total", ascending=True)
        fig5 = go.Figure(go.Bar(
            x=vgv_b["vgv_total"], y=vgv_b["bairro"], orientation="h",
            marker_color=C_NAVY3,
            marker_line=dict(color=C_GOLD, width=0.5),
            text=vgv_b["vgv_total"].apply(fmt_M),
            textposition="outside",
            textfont=dict(size=10, color=C_MUTED),
        ))
        fig5.update_layout(
            **plot_layout(height=250),
            xaxis=ax(fmt=",.0f"),
            yaxis=axh(),
        )
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")
    st.markdown(f'<p class="chart-title">💡 Análise Executiva do Portfólio</p>', unsafe_allow_html=True)
    melhor      = dre_f.loc[dre_f["margem_bruta_pct"].idxmax()]
    pior_vso    = dre_f.loc[dre_f["vso_acumulado_pct"].idxmin()]
    em_obra_vgv = emp_f[emp_f["status"] == "em_obra"]["vgv_total"].sum()
    lanc_vgv    = emp_f[emp_f["status"] == "lancamento"]["vgv_total"].sum()
    acima_bench = len(dre_f[dre_f["margem_bruta_pct"] >= 30])

    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        ins(f"<strong>{melhor['nome']}</strong> lidera o portfólio com margem bruta de "
            f"<strong>{melhor['margem_bruta_pct']:.1f}%</strong> — "
            f"{melhor['margem_bruta_pct']-30:.1f}pp acima do benchmark de 30% do mercado SP.", "ok")
    with ic2:
        ins(f"<strong>{acima_bench} de {len(dre_f)}</strong> empreendimentos superam o benchmark de 30% "
            f"de margem bruta. Pipeline de lançamentos de <strong>{fmt_M(lanc_vgv)}</strong> "
            f"em VGV garante crescimento nos próximos ciclos.", "info")
    with ic3:
        if pior_vso["vso_acumulado_pct"] < 75:
            ins(f"Atenção: <strong>{pior_vso['nome']}</strong> com Velocidade de Vendas acumulada de "
                f"<strong>{pior_vso['vso_acumulado_pct']:.1f}%</strong>. "
                f"Revisar estratégia comercial ou mix de tipologias.", "bad")
        else:
            ins(f"Velocidade de Vendas média de <strong>{vso_m:.1f}%</strong> alinhada ao mercado SP. "
                f"Lançamentos recentes ainda em fase de aceleração comercial inicial.", "warn")

    st.markdown("---")
    st.markdown(f'<p class="chart-title">Portfólio Completo</p>', unsafe_allow_html=True)
    tab = dre_f[["nome","bairro","linha","status_label","vgv_lancado",
                 "vso_acumulado_pct","avanco_obra_pct","margem_bruta_pct","ebitda_pct"]].copy()
    tab.columns = ["Empreendimento","Bairro","Linha","Status",
                   "Valor Geral de Vendas","VSO (%)","Avanço (%)","Margem Bruta (%)","EBITDA (%)"]
    tab["Valor Geral de Vendas"] = tab["Valor Geral de Vendas"].apply(fmt_M)
    st.dataframe(tab, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════
#  COMERCIAL & VSO
# ══════════════════════════════════════════════════════════════════
elif "Comercial" in pagina:

    st.markdown("## Comercial & Velocidade de Vendas sobre Oferta (VSO)")
    st.caption("Acompanhamento mensal de vendas, distratos e VGV comercializado por empreendimento ou portfólio consolidado")

    sel = st.selectbox("Empreendimento", ["Portfólio Consolidado"] + dre_f["nome"].tolist())
    if sel != "Portfólio Consolidado":
        id_sel = dre_f[dre_f["nome"] == sel]["id_empreendimento"].values[0]
        vp     = vendas_f[vendas_f["id_empreendimento"] == id_sel].copy()
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
    taxa_dist = total_d / total_v * 100 if total_v > 0 else 0
    vso_rec   = vp.sort_values("data").iloc[-1]["vso_pct"] if len(vp) else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Unidades Vendidas",              f"{total_v:,.0f}")
    c2.metric("Distratos (Cancelamentos)",      f"{total_d:,.0f}",
              delta=f"-{taxa_dist:.1f}% da base", delta_color="inverse")
    c3.metric("Valor Geral de Vendas Comercializado", fmt_M(vgv_com))
    c4.metric("Velocidade de Vendas — Último Mês",    f"{vso_rec:.1f}%",
              delta="acima de 10%" if vso_rec >= 10 else "abaixo de 10%",
              delta_color="normal" if vso_rec >= 10 else "inverse")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        chart_header(
            "Velocidade de Vendas sobre Oferta (VSO) — Mensal (%)",
            "Percentual do estoque disponível vendido em cada mês. "
            "O VSO mede a 'saúde' comercial do lançamento: acima de 10%/mês é saudável para o mercado SP (Secovi-SP). "
            "Queda sustentada indica necessidade de ação comercial."
        )
        vp_s = vp.sort_values("data")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=vp_s["data"], y=vp_s["vso_pct"],
            mode="lines+markers", name="VSO",
            line=dict(color=C_GOLD, width=2.5),
            marker=dict(size=4, color=C_GOLD_L),
            fill="tozeroy", fillcolor="rgba(201,168,76,0.10)",
        ))
        fig.add_hline(y=10, line_dash="dash", line_color=C_VERM, line_width=1.2,
                      annotation_text="Mínimo saudável: 10%",
                      annotation_font_size=10, annotation_font_color=C_VERM)
        fig.update_layout(**plot_layout(height=270),
                          xaxis=ax(), yaxis=ax(title="VSO (%)"))
        st.plotly_chart(fig, use_container_width=True)
        cor_v = "bad" if vso_rec < 10 else "ok"
        ins(f"VSO mais recente: <strong>{vso_rec:.1f}%</strong> — "
            f"{'abaixo do mínimo de 10%. Avaliar campanha de incentivo, redução de tabela ou revisão de tipologias.' if vso_rec < 10 else 'acima do benchmark de 10% (Secovi-SP). Ritmo comercial saudável para o segmento de alto padrão.'}", cor_v)

    with col2:
        chart_header(
            "Valor Geral de Vendas (VGV) Comercializado — Mensal",
            "Volume financeiro de vendas efetivadas por mês. "
            "O pico ocorre geralmente no período de lançamento, com desaceleração natural à medida que o estoque é absorvido."
        )
        fig2 = go.Figure(go.Bar(
            x=vp_s["data"], y=vp_s["vgv_mes"],
            marker_color=C_NAVY3,
            marker_line=dict(color=C_GOLD, width=0.4),
            hovertemplate="%{x|%b/%Y}: %{customdata}<extra></extra>",
            customdata=vp_s["vgv_mes"].apply(fmt_M),
        ))
        fig2.update_layout(**plot_layout(height=270),
                           xaxis=ax(), yaxis=ax(fmt=",.0f"))
        st.plotly_chart(fig2, use_container_width=True)
        mes_pico = vp.loc[vp["vgv_mes"].idxmax(), "data"]
        ins(f"Pico de VGV em <strong>{mes_pico.strftime('%b/%Y')}</strong> — "
            f"{fmt_M(vp['vgv_mes'].max())} comercializados. Concentração no lançamento é padrão "
            f"do segmento de alto padrão SP.", "info")

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        chart_header(
            "Unidades Vendidas vs Distratos (Cancelamentos) — Mensal",
            "Comparativo entre novas vendas e cancelamentos de contrato. "
            "Distratos elevados reduzem o VGV líquido e indicam possível inadequação do produto ao público-alvo ou problemas de financiamento."
        )
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=vp_s["data"], y=vp_s["unidades_vendidas"],
                               name="Vendidas",  marker_color=C_GOLD))
        fig3.add_trace(go.Bar(x=vp_s["data"], y=vp_s["distratos"],
                               name="Distratos", marker_color=C_VERM))
        fig3.update_layout(**plot_layout(height=270), barmode="group",
                           xaxis=ax(), yaxis=ax())
        st.plotly_chart(fig3, use_container_width=True)
        cor_d = "bad" if taxa_dist > 5 else "ok"
        ins(f"Taxa de distrato acumulada: <strong>{taxa_dist:.1f}%</strong> — "
            f"{'acima do limite de 5%. Avaliar perfil de crédito dos compradores e canal de vendas.' if taxa_dist > 5 else 'dentro do limite aceitável de 5%. Pipeline de vendas com boa qualidade de compradores.'}", cor_d)

    with col4:
        chart_header(
            "Velocidade de Vendas (VSO) Acumulada por Bairro",
            "Percentual médio do Valor Geral de Vendas vendido por bairro. "
            "Bairros acima de 85% indicam alta absorção pelo mercado; abaixo de 70% sinalizam saturação ou inadequação do produto."
        )
        vso_b = dre_f.groupby("bairro")["vso_acumulado_pct"].mean().reset_index().sort_values("vso_acumulado_pct", ascending=True)
        cores_vso = [C_VERM if v < 70 else (C_GOLD if v < 85 else C_VERDE) for v in vso_b["vso_acumulado_pct"]]
        fig4 = go.Figure(go.Bar(
            x=vso_b["vso_acumulado_pct"], y=vso_b["bairro"],
            orientation="h", marker_color=cores_vso,
            text=[f"{v:.1f}%" for v in vso_b["vso_acumulado_pct"]],
            textposition="outside",
            textfont=dict(size=10, color=C_MUTED),
        ))
        fig4.add_vline(x=85, line_dash="dash", line_color=C_MUTED, line_width=1,
                       annotation_text="Meta: 85%",
                       annotation_font_size=10, annotation_font_color=C_MUTED)
        fig4.update_layout(**plot_layout(height=270),
                           xaxis=ax(rng=[0, 115]), yaxis=axh())
        st.plotly_chart(fig4, use_container_width=True)
        top_b = vso_b.iloc[-1]
        bot_b = vso_b.iloc[0]
        ins(f"<strong>{top_b['bairro']}</strong> lidera com VSO de <strong>{top_b['vso_acumulado_pct']:.1f}%</strong>. "
            f"<strong>{bot_b['bairro']}</strong> apresenta o menor índice ({bot_b['vso_acumulado_pct']:.1f}%) — "
            f"oportunidade de revisão de estratégia comercial local.", "info")


# ══════════════════════════════════════════════════════════════════
#  OBRAS & POC
# ══════════════════════════════════════════════════════════════════
elif "Obras" in pagina:

    st.markdown("## Obras & Percentual de Conclusão (POC)")
    st.caption("Reconhecimento de receita proporcional ao avanço físico da obra · Desvio de orçamento · Curva S de execução")

    opcoes = obra_f["nome_empreendimento"].unique().tolist()
    if not opcoes:
        st.warning("Nenhum dado para os filtros selecionados.")
        st.stop()

    sel_obra = st.selectbox("Empreendimento", opcoes)
    o        = obra_f[obra_f["nome_empreendimento"] == sel_obra]

    av   = o["avanco_fisico_pct"].iloc[0]
    rpoc = o["receita_reconhecida_poc"].iloc[0]
    corc = o["custo_orcado"].sum()
    crea = o["custo_realizado"].sum()
    dmed = o["desvio_pct"].mean()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Avanço Físico — % de Conclusão",   f"{av:.0f}%")
    c2.metric("Receita Reconhecida (POC)",         fmt_M(rpoc), help="Receita proporcional ao avanço físico da obra")
    c3.metric("Custo Realizado vs Orçado",         fmt_M(crea), delta=fmt_M(crea - corc), delta_color="inverse")
    c4.metric("Desvio Médio de Custo",             f"{dmed:+.1f}%", delta_color="inverse")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        chart_header(
            "Custo Orçado vs Realizado por Etapa de Obra",
            "Comparativo entre o orçamento original e o custo efetivamente incorrido em cada fase. "
            "Desvios positivos reduzem diretamente a margem bruta projetada no lançamento."
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=o["etapa_obra"], y=o["custo_orcado"],
            name="Orçado", marker_color=C_BORDER,
            marker_line=dict(color=C_MUTED, width=1),
        ))
        fig.add_trace(go.Bar(
            x=o["etapa_obra"], y=o["custo_realizado"],
            name="Realizado", marker_color=C_NAVY3,
            marker_line=dict(color=C_GOLD, width=0.5),
        ))
        fig.update_layout(**plot_layout(height=290), barmode="group",
                          xaxis=ax(grid=False), yaxis=ax(fmt=",.0f"))
        st.plotly_chart(fig, use_container_width=True)
        etapa_crit = o.loc[o["desvio_pct"].idxmax(), "etapa_obra"]
        dev_crit   = o["desvio_pct"].max()
        cor_e = "bad" if dev_crit > 8 else ("warn" if dev_crit > 3 else "ok")
        ins(f"Maior desvio: etapa <strong>{etapa_crit}</strong> com <strong>{dev_crit:+.1f}%</strong> sobre o orçado. "
            f"{'Requer plano de contenção imediato — impacto direto na margem bruta.' if dev_crit > 8 else 'Dentro da margem tolerável de até +8%.'}",
            cor_e)

    with col2:
        chart_header(
            "Desvio Percentual de Custo por Etapa",
            "Variação do custo realizado em relação ao orçado para cada etapa. "
            "Verde indica economia, dourado indica desvio moderado e vermelho indica desvio crítico (>8%) — "
            "cada ponto percentual de desvio comprime diretamente a margem bruta."
        )
        cores_d = [C_VERM if d > 8 else (C_GOLD if d > 0 else C_VERDE) for d in o["desvio_pct"]]
        fig2 = go.Figure(go.Bar(
            x=o["etapa_obra"], y=o["desvio_pct"],
            marker_color=cores_d,
            text=[f"{d:+.1f}%" for d in o["desvio_pct"]],
            textposition="outside",
            textfont=dict(size=11, color=C_MUTED),
        ))
        fig2.add_hline(y=0,   line_color=C_MUTED, line_width=1)
        fig2.add_hline(y=8,   line_dash="dash", line_color=C_VERM, line_width=1,
                       annotation_text="Limite crítico +8%",
                       annotation_font_size=10, annotation_font_color=C_VERM)
        fig2.update_layout(**plot_layout(height=290),
                           xaxis=ax(grid=False), yaxis=ax(title="Desvio (%)"))
        st.plotly_chart(fig2, use_container_width=True)
        delta_total = crea - corc
        ins(f"Desvio total acumulado: <strong>{fmt_M(abs(delta_total))}</strong> "
            f"{'acima' if delta_total > 0 else 'abaixo'} do orçamento original. "
            f"{'Cada real de desvio reduz diretamente o EBITDA do empreendimento.' if delta_total > 0 else 'Execução abaixo do orçamento preserva a margem bruta projetada no lançamento.'}",
            "bad" if delta_total > 0 else "ok")

    st.markdown("---")
    chart_header(
        "Curva S — Avanço Físico Realizado vs Cronograma Planejado",
        "A Curva S mostra a evolução do progresso físico da obra ao longo do tempo. "
        "A linha tracejada representa o cronograma original; a área preenchida é o avanço real. "
        "Quando a curva real fica abaixo da planejada, há atraso — com risco de impacto no reconhecimento de receita (POC) do trimestre."
    )
    meses = list(range(1, 43))
    plan  = [min(100, (m / 36) ** 1.15 * 100) for m in meses]
    real  = [min(av, min(100, p * (1 + 0.04 * (1 if m < 18 else -0.3)) + (m * 0.25)))
             for m, p in zip(meses, plan)]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=meses, y=plan, name="Cronograma Planejado",
                               line=dict(color=C_BORDER, width=2, dash="dash")))
    fig3.add_trace(go.Scatter(x=meses, y=real, name="Avanço Realizado",
                               line=dict(color=C_GOLD, width=2.5),
                               fill="tonexty", fillcolor="rgba(201,168,76,0.12)"))
    fig3.add_vline(x=av / 100 * 36, line_dash="dot", line_color=C_GOLD_L, line_width=2,
                   annotation_text=f"Hoje: {av:.0f}%",
                   annotation_font_color=C_GOLD_L, annotation_font_size=11)
    fig3.update_layout(**plot_layout(height=300),
                       xaxis=ax(title="Mês de obra"),
                       yaxis=ax(title="Avanço Físico (%)", rng=[0, 110]))
    st.plotly_chart(fig3, use_container_width=True)
    atraso = plan[min(int(av / 100 * 36), len(plan) - 1)] - av if av < 100 else 0
    ins(f"{'Atraso de ' + str(round(atraso, 1)) + 'pp em relação ao cronograma — risco de impacto no reconhecimento de receita POC no próximo trimestre.' if atraso > 5 else 'Avanço de ' + str(round(av, 0)) + '% alinhado ao cronograma. Receita reconhecida via POC de ' + fmt_M(rpoc) + ' reflete corretamente o estágio atual.'}",
        "bad" if atraso > 5 else "ok")

    st.markdown("---")
    chart_header(
        "Percentual de Conclusão (POC) — Todos os Empreendimentos",
        "Visão comparativa do avanço físico de cada obra. Vermelho (<30%): fase inicial, reconhecimento de receita reduzido. "
        "Dourado (30-70%): fase intermediária. Verde (>70%): fase avançada, maior reconhecimento de receita."
    )
    poc = obra_f.groupby("nome_empreendimento").first().reset_index()[
        ["nome_empreendimento","avanco_fisico_pct","receita_reconhecida_poc"]]
    poc = poc.sort_values("avanco_fisico_pct", ascending=True)
    cores_poc = [C_VERM if v < 30 else (C_GOLD if v < 70 else C_VERDE) for v in poc["avanco_fisico_pct"]]
    fig4 = go.Figure(go.Bar(
        x=poc["avanco_fisico_pct"], y=poc["nome_empreendimento"],
        orientation="h", marker_color=cores_poc,
        text=[f"{v:.0f}%" for v in poc["avanco_fisico_pct"]],
        textposition="outside",
        textfont=dict(size=10, color=C_MUTED),
        customdata=poc["receita_reconhecida_poc"].apply(fmt_M),
        hovertemplate="<b>%{y}</b><br>POC: %{x:.0f}%<br>Receita reconhecida: %{customdata}<extra></extra>",
    ))
    fig4.add_vline(x=50, line_dash="dash", line_color=C_MUTED, line_width=1,
                   annotation_text="50%", annotation_font_size=10)
    fig4.update_layout(**plot_layout(height=400),
                       xaxis=ax(rng=[0, 115]), yaxis=axh())
    st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
#  DRE GERENCIAL
# ══════════════════════════════════════════════════════════════════
elif "DRE" in pagina:

    st.markdown("## DRE Gerencial — Demonstrativo de Resultado Econômico")
    st.caption("Resultado por empreendimento pelo método POC · Receita reconhecida proporcional ao avanço físico da obra · Não representa fluxo de caixa")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Receita Total Reconhecida (POC)", fmt_M(dre_f["receita_reconhecida_poc"].sum()))
    c2.metric("Custo Total de Obra (POC)",        fmt_M(dre_f["custo_obra_poc"].sum()))
    c3.metric("Margem Bruta Média do Portfólio",  f"{dre_f['margem_bruta_pct'].mean():.1f}%")
    ebitda_pos = dre_f[dre_f["ebitda"] > 0]["ebitda"].sum()
    c4.metric("EBITDA Acumulado (Positivo)",      fmt_M(ebitda_pos),
              help="Soma apenas dos empreendimentos com EBITDA positivo (obras em fase avançada)")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        chart_header(
            "Margem Bruta por Empreendimento (%)",
            "A margem bruta indica quanto sobra da receita após subtrair os custos diretos de obra. "
            "É o principal indicador de rentabilidade operacional da incorporadora. "
            "Vermelho (<25%): abaixo do aceitável. Dourado (25-33%): margem adequada. Verde (>33%): margem excelente para o mercado SP."
        )
        df_m = dre_f.sort_values("margem_bruta_pct")
        cores_m = [C_VERM if v < 25 else (C_GOLD if v < 33 else C_VERDE) for v in df_m["margem_bruta_pct"]]
        fig = go.Figure(go.Bar(
            x=df_m["margem_bruta_pct"], y=df_m["nome"],
            orientation="h", marker_color=cores_m,
            text=[f"{v:.1f}%" for v in df_m["margem_bruta_pct"]],
            textposition="outside",
            textfont=dict(size=10, color=C_MUTED),
        ))
        fig.add_vline(x=30, line_dash="dash", line_color=C_MUTED, line_width=1,
                      annotation_text="Benchmark mercado SP: 30%",
                      annotation_font_size=10, annotation_font_color=C_MUTED)
        fig.update_layout(**plot_layout(height=460),
                          xaxis=ax(rng=[0, 55]), yaxis=axh())
        st.plotly_chart(fig, use_container_width=True)
        melhor = dre_f.loc[dre_f["margem_bruta_pct"].idxmax()]
        pior   = dre_f.loc[dre_f["margem_bruta_pct"].idxmin()]
        ins(f"<strong>{melhor['nome']}</strong>: melhor margem com <strong>{melhor['margem_bruta_pct']:.1f}%</strong>. "
            f"<strong>{pior['nome']}</strong> ({pior['margem_bruta_pct']:.1f}%) — revisar controle de custos de obra.", "info")

    with col2:
        chart_header(
            "Waterfall do DRE — Demonstrativo de Resultado Consolidado",
            "O gráfico cascata (waterfall) mostra a decomposição do resultado econômico: "
            "parte da Receita Reconhecida (POC), subtrai o Custo de Obra, as Despesas Comerciais (comissões, marketing) "
            "e as Despesas Administrativas, chegando ao EBITDA — resultado operacional antes de juros, impostos e depreciação. "
            "É o principal indicador de eficiência econômica da operação."
        )
        receita = dre_f["receita_reconhecida_poc"].sum()
        custo   = dre_f["custo_obra_poc"].sum()
        desp_c  = dre_f["despesas_comerciais"].sum()
        desp_a  = dre_f["despesas_administrativas"].sum()
        ebitda  = receita - custo - desp_c - desp_a
        fig2 = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute","relative","relative","relative","total"],
            x=["Receita\nPOC","Custo\nde Obra","Despesas\nComerciais","Despesas\nAdm.","EBITDA"],
            y=[receita, -custo, -desp_c, -desp_a, 0],
            text=[fmt_M(v) for v in [receita, custo, desp_c, desp_a, ebitda]],
            textposition="outside",
            textfont=dict(size=10, color=C_TEXT),
            connector={"line": {"color": C_BORDER}},
            increasing={"marker": {"color": C_VERDE}},
            decreasing={"marker": {"color": C_VERM}},
            totals={"marker": {"color": C_GOLD}},
        ))
        fig2.update_layout(
            plot_bgcolor=C_PLOT_BG, paper_bgcolor=C_PLOT_BG,
            font=dict(family="Inter, sans-serif", color=C_TEXT, size=11),
            height=290, showlegend=False,
            margin=dict(l=12, r=20, t=10, b=10),
            xaxis=ax(grid=False),
            yaxis=ax(fmt=",.0f"),
        )
        st.plotly_chart(fig2, use_container_width=True)
        ebitda_pct = ebitda / receita * 100 if receita > 0 else 0
        cor_e = "ok" if ebitda_pct > 15 else ("bad" if ebitda_pct < 8 else "warn")
        ins(f"EBITDA consolidado de <strong>{fmt_M(ebitda)}</strong> — margem EBITDA de <strong>{ebitda_pct:.1f}%</strong>. "
            f"{'Acima da referência de 12-15% do setor imobiliário SP.' if ebitda_pct > 15 else 'Abaixo de 15% — avaliar estrutura de despesas administrativas e comerciais.'}", cor_e)

        chart_header(
            "Margem Bruta Média por Linha de Produto",
            "Comparativo de rentabilidade entre as linhas Premium, Alto Padrão e Smart. "
            "Linhas Premium tendem a ter maior margem absoluta; linhas Smart compensam com volume de unidades."
        )
        ml = dre_f.groupby("linha")["margem_bruta_pct"].mean().reset_index()
        fig3 = go.Figure(go.Bar(
            x=ml["linha"], y=ml["margem_bruta_pct"],
            marker_color=[LINHA_CORES.get(l, C_MUTED) for l in ml["linha"]],
            text=[f"{v:.1f}%" for v in ml["margem_bruta_pct"]],
            textposition="outside",
            textfont=dict(size=11, color=C_MUTED),
        ))
        fig3.add_hline(y=30, line_dash="dash", line_color=C_MUTED, line_width=1,
                       annotation_text="Benchmark: 30%",
                       annotation_font_size=10, annotation_font_color=C_MUTED)
        fig3.update_layout(**plot_layout(height=210),
                           xaxis=ax(grid=False), yaxis=ax(rng=[0, 50]))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    chart_header(
        "Análise Bidimensional: Margem Bruta × Velocidade de Vendas Acumulada",
        "Cada bolha representa um empreendimento — o tamanho é proporcional ao Valor Geral de Vendas lançado. "
        "O quadrante ideal (direita-cima) reúne projetos com alta velocidade de vendas E alta margem. "
        "Bolhas no canto inferior-esquerdo exigem atenção imediata tanto comercial quanto de custos."
    )
    fig4 = go.Figure()
    for sl, cor in STATUS_CORES.items():
        sub = dre_f[dre_f["status_label"] == sl]
        if len(sub):
            fig4.add_trace(go.Scatter(
                x=sub["vso_acumulado_pct"], y=sub["margem_bruta_pct"],
                mode="markers+text", name=sl,
                marker=dict(
                    color=cor, opacity=0.85,
                    size=sub["vgv_lancado"] / 4_000_000 + 8,
                    line=dict(color=C_BORDER, width=1.5),
                ),
                text=sub["nome"], textposition="top center",
                textfont=dict(size=9, color=C_MUTED),
                hovertemplate="<b>%{text}</b><br>VSO: %{x:.1f}%<br>Margem Bruta: %{y:.1f}%<extra></extra>",
            ))
    fig4.add_hline(y=30, line_dash="dash", line_color=C_MUTED, line_width=1,
                   annotation_text="Margem benchmark: 30%",
                   annotation_font_size=10, annotation_font_color=C_MUTED)
    fig4.add_vline(x=80, line_dash="dash", line_color=C_MUTED, line_width=1,
                   annotation_text="VSO meta: 80%",
                   annotation_font_size=10, annotation_font_color=C_MUTED)
    fig4.update_layout(**plot_layout(height=430),
                       xaxis=ax(title="Velocidade de Vendas Acumulada (%)", rng=[0, 105]),
                       yaxis=ax(title="Margem Bruta (%)", rng=[0, 55]))
    st.plotly_chart(fig4, use_container_width=True)
    q_ideal = len(dre_f[(dre_f["vso_acumulado_pct"] >= 80) & (dre_f["margem_bruta_pct"] >= 30)])
    ins(f"<strong>{q_ideal} de {len(dre_f)} empreendimentos</strong> estão no quadrante ideal "
        f"(VSO ≥ 80% e Margem ≥ 30%). O tamanho de cada bolha é proporcional ao Valor Geral de Vendas lançado.",
        "ok" if q_ideal >= len(dre_f) // 2 else "warn")

    st.markdown("---")
    st.markdown(f'<p class="chart-title">DRE Detalhado por Empreendimento</p>', unsafe_allow_html=True)
    st.caption("Resultado econômico individual · Receita reconhecida pelo método POC · Valores em R$")
    cols = ["nome","linha","status_label","vgv_lancado","vso_acumulado_pct",
            "receita_reconhecida_poc","custo_obra_poc","margem_bruta_pct","ebitda","ebitda_pct"]
    tab = dre_f[cols].copy()
    for c in ["vgv_lancado","receita_reconhecida_poc","custo_obra_poc","ebitda"]:
        tab[c] = tab[c].apply(fmt_M)
    tab.columns = [
        "Empreendimento","Linha","Status",
        "Valor Geral de Vendas","VSO (%)","Receita POC","Custo POC",
        "Margem Bruta (%)","EBITDA","EBITDA (%)"
    ]
    st.dataframe(tab, use_container_width=True, hide_index=True)
