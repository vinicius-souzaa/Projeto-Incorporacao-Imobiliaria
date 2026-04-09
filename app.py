import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Portfólio Imobiliário | Analytics SP",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── NAVY & GOLD ───────────────────────────────────────────────────────────────
C_NAVY    = "#0D2137"   # sidebar / elementos escuros
C_NAVY2   = "#152C47"   # hover sidebar
C_GOLD    = "#C9A84C"   # acento principal
C_GOLD2   = "#E8C96A"   # acento claro
C_FUNDO   = "#F5F6FA"   # background geral
C_BRANCO  = "#FFFFFF"   # cards
C_BORDA   = "#E2E6ED"   # bordas
C_TEXTO   = "#1A2433"   # texto principal
C_MUTED   = "#6B7A90"   # texto secundário
C_VERDE   = "#1A7A4A"   # sucesso
C_VERM    = "#B03A2E"   # alerta
C_AZUL    = "#2471A3"   # info

STATUS_LABELS = {"entregue":"Entregue","em_obra":"Em Obra","lancamento":"Lançamento"}
STATUS_CORES  = {"Entregue": C_VERDE, "Em Obra": C_AZUL, "Lançamento": C_GOLD}
LINHA_CORES   = {"Premium": C_NAVY, "Alto Padrão": C_GOLD, "Smart": C_MUTED}

# Configuração base de gráficos — SEM xaxis/yaxis para evitar conflito no update_layout
PLOT_BASE = dict(
    plot_bgcolor=C_BRANCO,
    paper_bgcolor=C_BRANCO,
    font=dict(family="Inter, Segoe UI, sans-serif", color=C_TEXTO, size=12),
    margin=dict(l=10, r=20, t=30, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)

GRID = dict(showgrid=True, gridcolor=C_BORDA, zeroline=False)
NOGRID = dict(showgrid=False, zeroline=False)

st.markdown(f"""
<style>
html, body, [class*="css"] {{ font-family: 'Inter', 'Segoe UI', sans-serif; }}
.stApp {{ background-color: {C_FUNDO}; }}

[data-testid="stSidebar"] {{
    background: {C_NAVY};
    border-right: 1px solid {C_NAVY2};
}}
[data-testid="stSidebar"] * {{ color: #C8D4E0 !important; }}
[data-testid="stSidebar"] .stSelectbox label {{
    color: {C_GOLD} !important;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 600;
}}
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 !important;
    color: #8FA8C0 !important;
    font-size: 13px !important;
    text-align: left !important;
    padding: 10px 16px !important;
    width: 100% !important;
    transition: all .15s;
    font-weight: 400 !important;
    letter-spacing: .01em;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(201,168,76,0.08) !important;
    color: {C_GOLD2} !important;
    border-left-color: {C_GOLD} !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    color: #F0E6C8 !important;
    border-left-color: {C_GOLD} !important;
    background: rgba(201,168,76,0.14) !important;
    font-weight: 600 !important;
}}
[data-testid="stMetric"] {{
    background: {C_BRANCO};
    border: 1px solid {C_BORDA};
    border-top: 3px solid {C_GOLD};
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
    color: {C_NAVY} !important;
    font-weight: 700 !important;
}}
.insight-card {{
    background: {C_BRANCO};
    border-left: 4px solid {C_GOLD};
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 13px;
    color: {C_TEXTO};
    line-height: 1.55;
    border-radius: 0 6px 6px 0;
}}
.insight-card.alerta  {{ border-left-color:{C_VERM};  background:#FDF3F2; }}
.insight-card.positivo{{ border-left-color:{C_VERDE}; background:#F2FAF5; }}
.insight-card.info    {{ border-left-color:{C_AZUL};  background:#F0F5FB; }}
.insight-card.neutro  {{ border-left-color:{C_MUTED}; background:#F8F9FB; }}
h1 {{ color:{C_NAVY} !important; font-weight:700 !important; letter-spacing:-.3px; }}
h2, h3 {{ color:{C_NAVY} !important; font-weight:600 !important; }}
hr {{ border-color:{C_BORDA}; margin:1rem 0; }}
[data-testid="stDataFrame"] {{ border:1px solid {C_BORDA}; border-radius:8px; }}
</style>
""", unsafe_allow_html=True)

# ── DADOS ─────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@st.cache_data
def load_all():
    emp    = pd.read_csv(os.path.join(DATA_DIR,"empreendimentos.csv"), parse_dates=["lancamento","entrega_prevista"])
    vendas = pd.read_csv(os.path.join(DATA_DIR,"vendas_mensais.csv"),  parse_dates=["data"])
    obra   = pd.read_csv(os.path.join(DATA_DIR,"custo_obra.csv"))
    dre    = pd.read_csv(os.path.join(DATA_DIR,"dre_gerencial.csv"))
    return emp, vendas, obra, dre

emp, vendas, obra, dre = load_all()
dre["status_label"] = dre["status"].map(STATUS_LABELS)

def fmt_M(v):
    try:
        v = float(v)
        return f"R$ {v/1_000_000:.1f}M" if abs(v)>=1_000_000 else f"R$ {v/1_000:.0f}K"
    except: return "—"

def insight(texto, tipo="neutro"):
    st.markdown(f'<div class="insight-card {tipo}">{texto}</div>', unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:24px 16px 12px;">
        <div style="font-size:11px;color:{C_GOLD};text-transform:uppercase;letter-spacing:.14em;font-weight:600;">Portfólio Imobiliário</div>
        <div style="font-size:13px;color:#8FA8C0;margin-top:4px;letter-spacing:.02em;">Analytics · São Paulo SP</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<hr style="border-color:{C_NAVY2};margin:0 0 6px;">', unsafe_allow_html=True)

    paginas = ["🏠  Visão Geral","📈  Comercial & VSO","🏗️  Obras & POC","📊  DRE Gerencial"]
    if "pagina" not in st.session_state:
        st.session_state.pagina = paginas[0]
    for p in paginas:
        ativo = st.session_state.pagina == p
        if st.button(p, key=p, use_container_width=True, type="primary" if ativo else "secondary"):
            st.session_state.pagina = p
            st.rerun()

    st.markdown(f'<hr style="border-color:{C_NAVY2};margin:8px 0 4px;">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:10px;color:{C_GOLD};text-transform:uppercase;letter-spacing:.1em;padding:4px 4px 6px;font-weight:600;">Filtros</div>', unsafe_allow_html=True)

    bairros_disp = ["Todos"] + sorted(emp["bairro"].unique())
    filtro_bairro = st.selectbox("Bairro", bairros_disp, key="fb")

    # Status dinâmico
    emp_tmp = emp if filtro_bairro=="Todos" else emp[emp["bairro"]==filtro_bairro]
    status_raw = sorted(emp_tmp["status"].unique().tolist())
    status_opts = ["Todos"] + [STATUS_LABELS[s] for s in status_raw if s in STATUS_LABELS]
    filtro_status_lbl = st.selectbox("Status", status_opts, key="fs")
    status_rev = {v:k for k,v in STATUS_LABELS.items()}
    filtro_status = status_rev.get(filtro_status_lbl,"Todos")

    # Linha dinâmica
    emp_tmp2 = emp_tmp if filtro_status=="Todos" else emp_tmp[emp_tmp["status"]==filtro_status]
    linhas_disp = sorted(emp_tmp2["linha"].unique().tolist())
    filtro_linha = st.selectbox("Linha", ["Todas"] + linhas_disp, key="fl")

pagina = st.session_state.pagina

# ── FILTROS ───────────────────────────────────────────────────────────────────
emp_f = emp.copy()
if filtro_bairro != "Todos":   emp_f = emp_f[emp_f["bairro"]==filtro_bairro]
if filtro_status != "Todos":   emp_f = emp_f[emp_f["status"]==filtro_status]
if filtro_linha  != "Todas":   emp_f = emp_f[emp_f["linha"]==filtro_linha]

ids_f    = emp_f["id"].tolist()
vendas_f = vendas[vendas["id_empreendimento"].isin(ids_f)]
obra_f   = obra[obra["id_empreendimento"].isin(ids_f)]
dre_f    = dre[dre["id_empreendimento"].isin(ids_f)].copy()

if len(dre_f)==0:
    st.warning("⚠️ Nenhum empreendimento encontrado para os filtros selecionados.")
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
#  VISÃO GERAL
# ═══════════════════════════════════════════════════════════════════════════════
if "Visão Geral" in pagina:
    st.markdown("## Visão Geral do Portfólio")
    st.caption(f"**{len(dre_f)} empreendimentos** · Alto padrão São Paulo · Dados sintéticos calibrados Secovi-SP / ABRAINC-FIPE")

    vgv_total   = emp_f["vgv_total"].sum()
    vgv_vendido = dre_f["vgv_vendido"].sum()
    margem_m    = dre_f["margem_bruta_pct"].mean()
    vso_m       = dre_f["vso_acumulado_pct"].mean()

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Empreendimentos",    f"{len(dre_f)}")
    c2.metric("VGV Total Lançado",  fmt_M(vgv_total))
    c3.metric("VGV Vendido",        fmt_M(vgv_vendido))
    c4.metric("VSO Médio",          f"{vso_m:.1f}%")
    c5.metric("Margem Bruta Média", f"{margem_m:.1f}%")

    st.markdown("---")
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
                    name=sl, orientation="h", marker_color=cor,
                    text=sub["vgv_lancado"].apply(fmt_M),
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>VGV: %{text}<extra></extra>",
                ))
        fig.update_layout(**PLOT_BASE, height=420, barmode="stack",
                          xaxis=dict(**GRID, tickformat=",.0f"),
                          yaxis=dict(**NOGRID))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("##### Status do Portfólio")
        sc = emp_f["status"].map(STATUS_LABELS).value_counts().reset_index()
        sc.columns = ["status","qtd"]
        fig2 = go.Figure(go.Pie(
            labels=sc["status"], values=sc["qtd"], hole=0.6,
            marker_colors=[STATUS_CORES.get(s,C_MUTED) for s in sc["status"]],
            textinfo="label+percent",
            hovertemplate="%{label}: %{value}<extra></extra>",
        ))
        fig2.update_layout(**PLOT_BASE, height=210, showlegend=False,
                           margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("##### Linha de Produto")
        lc = emp_f["linha"].value_counts().reset_index()
        lc.columns = ["linha","qtd"]
        fig3 = go.Figure(go.Bar(
            x=lc["linha"], y=lc["qtd"],
            marker_color=[LINHA_CORES.get(l,C_MUTED) for l in lc["linha"]],
            text=lc["qtd"], textposition="outside",
        ))
        fig3.update_layout(**PLOT_BASE, height=185,
                           xaxis=dict(**NOGRID),
                           yaxis=dict(**NOGRID, visible=False))
        st.plotly_chart(fig3, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("##### VGV Lançado por Ano")
        emp_f2 = emp_f.copy()
        emp_f2["ano"] = emp_f2["lancamento"].dt.year
        vgv_ano = emp_f2.groupby(["ano","linha"])["vgv_total"].sum().reset_index()
        fig4 = px.bar(vgv_ano, x="ano", y="vgv_total", color="linha",
                      color_discrete_map=LINHA_CORES, barmode="stack",
                      labels={"ano":"Ano","vgv_total":"VGV (R$)","linha":"Linha"})
        fig4.update_layout(**PLOT_BASE, height=260,
                           xaxis=dict(**NOGRID),
                           yaxis=dict(**GRID, tickformat=",.0f"))
        st.plotly_chart(fig4, use_container_width=True)

    with col_d:
        st.markdown("##### VGV Consolidado por Bairro")
        vgv_b = emp_f.groupby("bairro")["vgv_total"].sum().reset_index().sort_values("vgv_total", ascending=True)
        fig5 = go.Figure(go.Bar(
            x=vgv_b["vgv_total"], y=vgv_b["bairro"], orientation="h",
            marker_color=C_NAVY,
            text=vgv_b["vgv_total"].apply(fmt_M), textposition="outside",
        ))
        fig5.update_layout(**PLOT_BASE, height=260,
                           xaxis=dict(**GRID, tickformat=",.0f"),
                           yaxis=dict(**NOGRID))
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 💡 Análise do Portfólio")
    melhor   = dre_f.loc[dre_f["margem_bruta_pct"].idxmax()]
    pior_vso = dre_f.loc[dre_f["vso_acumulado_pct"].idxmin()]
    em_obra_vgv = emp_f[emp_f["status"]=="em_obra"]["vgv_total"].sum()
    lanc_vgv    = emp_f[emp_f["status"]=="lancamento"]["vgv_total"].sum()
    acima_bench = len(dre_f[dre_f["margem_bruta_pct"]>=30])

    ic1,ic2,ic3 = st.columns(3)
    with ic1:
        insight(f"<strong>{melhor['nome']}</strong> lidera com margem bruta de <strong>{melhor['margem_bruta_pct']:.1f}%</strong> — {melhor['margem_bruta_pct']-30:.1f}pp acima do benchmark de 30% do mercado SP.", "positivo")
    with ic2:
        insight(f"<strong>{acima_bench} de {len(dre_f)}</strong> empreendimentos acima do benchmark de 30% de margem. Pipeline de <strong>{fmt_M(lanc_vgv)}</strong> em lançamentos garante crescimento nos próximos ciclos.", "info")
    with ic3:
        if pior_vso["vso_acumulado_pct"] < 75:
            insight(f"Atenção: <strong>{pior_vso['nome']}</strong> com VSO acumulado de <strong>{pior_vso['vso_acumulado_pct']:.1f}%</strong>. Revisar estratégia comercial ou mix de tipologias.", "alerta")
        else:
            insight(f"VSO médio de <strong>{vso_m:.1f}%</strong> em linha com o mercado SP. Lançamentos recentes ainda em fase de aceleração comercial inicial.", "neutro")

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
    st.caption("Velocidade de Vendas · Distratos · VGV mensal por empreendimento")

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
    vso_rec   = vp.sort_values("data").iloc[-1]["vso_pct"] if len(vp) else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Unidades Vendidas",  f"{total_v:,.0f}")
    c2.metric("Distratos",          f"{total_d:,.0f}", delta=f"-{taxa_dist:.1f}% da base", delta_color="inverse")
    c3.metric("VGV Comercializado", fmt_M(vgv_com))
    c4.metric("VSO Último Mês",     f"{vso_rec:.1f}%",
              delta="acima de 10%" if vso_rec>=10 else "abaixo de 10%",
              delta_color="normal" if vso_rec>=10 else "inverse")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### VSO Mensal (%)")
        vp_s = vp.sort_values("data")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=vp_s["data"], y=vp_s["vso_pct"],
            mode="lines+markers", name="VSO",
            line=dict(color=C_NAVY, width=2.5),
            marker=dict(size=4, color=C_GOLD),
            fill="tozeroy", fillcolor="rgba(13,33,55,0.07)",
        ))
        fig.add_hline(y=10, line_dash="dash", line_color=C_VERM, line_width=1,
                      annotation_text="Mínimo saudável 10%",
                      annotation_font_size=10, annotation_font_color=C_VERM)
        fig.update_layout(**PLOT_BASE, height=270,
                          xaxis=dict(**GRID),
                          yaxis=dict(**GRID, title="VSO (%)"))
        st.plotly_chart(fig, use_container_width=True)
        cor_v = "alerta" if vso_rec<10 else "positivo"
        insight(f"VSO mais recente: <strong>{vso_rec:.1f}%</strong> — {'abaixo do mínimo saudável de 10%. Considerar ação comercial.' if vso_rec<10 else 'acima do benchmark de 10% do mercado SP. Ritmo comercial saudável.'}", cor_v)

    with col2:
        st.markdown("##### VGV Mensal Comercializado")
        fig2 = go.Figure(go.Bar(
            x=vp_s["data"], y=vp_s["vgv_mes"],
            marker_color=C_NAVY,
            hovertemplate="%{x|%b/%Y}: %{customdata}<extra></extra>",
            customdata=vp_s["vgv_mes"].apply(fmt_M),
        ))
        fig2.update_layout(**PLOT_BASE, height=270,
                           xaxis=dict(**GRID),
                           yaxis=dict(**GRID, tickformat=",.0f"))
        st.plotly_chart(fig2, use_container_width=True)
        mes_pico = vp.loc[vp["vgv_mes"].idxmax(),"data"]
        insight(f"Pico de comercialização em <strong>{mes_pico.strftime('%b/%Y')}</strong> com {fmt_M(vp['vgv_mes'].max())} — concentrado no período de lançamento, padrão típico do segmento de alto padrão.", "info")

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("##### Vendas vs Distratos (mensal)")
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=vp_s["data"], y=vp_s["unidades_vendidas"], name="Vendidas",  marker_color=C_NAVY))
        fig3.add_trace(go.Bar(x=vp_s["data"], y=vp_s["distratos"],         name="Distratos", marker_color=C_GOLD))
        fig3.update_layout(**PLOT_BASE, height=270, barmode="group",
                           xaxis=dict(**GRID),
                           yaxis=dict(**GRID))
        st.plotly_chart(fig3, use_container_width=True)
        cor_d = "alerta" if taxa_dist>5 else "positivo"
        insight(f"Taxa de distrato acumulada: <strong>{taxa_dist:.1f}%</strong> — {'acima do limite aceitável de 5%. Avaliar perfil de crédito dos compradores.' if taxa_dist>5 else 'dentro do limite aceitável de 5%. Indicativo de qualidade do pipeline de vendas.'}", cor_d)

    with col4:
        st.markdown("##### VSO Acumulado por Bairro")
        vso_b = dre_f.groupby("bairro")["vso_acumulado_pct"].mean().reset_index().sort_values("vso_acumulado_pct", ascending=True)
        cores_vso = [C_VERM if v<70 else (C_GOLD if v<85 else C_VERDE) for v in vso_b["vso_acumulado_pct"]]
        fig4 = go.Figure(go.Bar(
            x=vso_b["vso_acumulado_pct"], y=vso_b["bairro"],
            orientation="h", marker_color=cores_vso,
            text=[f"{v:.1f}%" for v in vso_b["vso_acumulado_pct"]],
            textposition="outside",
        ))
        fig4.add_vline(x=85, line_dash="dash", line_color=C_MUTED, line_width=1,
                       annotation_text="Meta 85%", annotation_font_size=10)
        fig4.update_layout(**PLOT_BASE, height=270,
                           xaxis=dict(**GRID, range=[0,115]),
                           yaxis=dict(**NOGRID))
        st.plotly_chart(fig4, use_container_width=True)
        top_b = vso_b.iloc[-1]
        bot_b = vso_b.iloc[0]
        insight(f"<strong>{top_b['bairro']}</strong> lidera com VSO de <strong>{top_b['vso_acumulado_pct']:.1f}%</strong>. <strong>{bot_b['bairro']}</strong> apresenta o menor índice ({bot_b['vso_acumulado_pct']:.1f}%) — oportunidade de revisão da estratégia local.", "info")


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
    c1.metric("Avanço Físico (POC)",  f"{av:.0f}%")
    c2.metric("Receita Reconhecida",  fmt_M(rpoc), help="Receita proporcional ao avanço físico")
    c3.metric("Custo Realizado",      fmt_M(crea),  delta=fmt_M(crea-corc), delta_color="inverse")
    c4.metric("Desvio Médio de Custo",f"{dmed:+.1f}%", delta_color="inverse")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Orçado vs Realizado por Etapa")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=o["etapa_obra"], y=o["custo_orcado"],
                             name="Orçado",    marker_color=C_BORDA,
                             marker_line=dict(color=C_MUTED, width=1)))
        fig.add_trace(go.Bar(x=o["etapa_obra"], y=o["custo_realizado"],
                             name="Realizado", marker_color=C_NAVY))
        fig.update_layout(**PLOT_BASE, height=290, barmode="group",
                          xaxis=dict(**NOGRID),
                          yaxis=dict(**GRID, tickformat=",.0f"))
        st.plotly_chart(fig, use_container_width=True)
        etapa_crit = o.loc[o["desvio_pct"].idxmax(),"etapa_obra"]
        dev_crit   = o["desvio_pct"].max()
        cor_e = "alerta" if dev_crit>8 else ("neutro" if dev_crit>3 else "positivo")
        insight(f"Maior desvio: etapa <strong>{etapa_crit}</strong> com <strong>{dev_crit:+.1f}%</strong> sobre o orçado. {'Requer plano de contenção imediato.' if dev_crit>8 else 'Dentro da margem tolerável de obra (até +8%).'}", cor_e)

    with col2:
        st.markdown("##### Desvio de Custo por Etapa (%)")
        cores_d = [C_VERM if d>8 else (C_GOLD if d>0 else C_VERDE) for d in o["desvio_pct"]]
        fig2 = go.Figure(go.Bar(
            x=o["etapa_obra"], y=o["desvio_pct"],
            marker_color=cores_d,
            text=[f"{d:+.1f}%" for d in o["desvio_pct"]],
            textposition="outside",
        ))
        fig2.add_hline(y=0, line_color=C_MUTED, line_width=1)
        fig2.add_hline(y=8, line_dash="dash", line_color=C_VERM, line_width=1,
                       annotation_text="Limite crítico +8%",
                       annotation_font_size=10, annotation_font_color=C_VERM)
        fig2.update_layout(**PLOT_BASE, height=290,
                           xaxis=dict(**NOGRID),
                           yaxis=dict(**GRID, title="Desvio (%)"))
        st.plotly_chart(fig2, use_container_width=True)
        delta_total = crea - corc
        cor_dt = "alerta" if delta_total>0 else "positivo"
        insight(f"Desvio total acumulado: <strong>{fmt_M(abs(delta_total))}</strong> {'acima' if delta_total>0 else 'abaixo'} do orçamento original. {'Cada ponto percentual acima impacta diretamente a margem bruta.' if delta_total>0 else 'Execução dentro do orçamento preserva a margem bruta projetada.'}", cor_dt)

    st.markdown("---")
    st.markdown("##### Curva S — Avanço Físico vs Cronograma Planejado")
    meses = list(range(1,43))
    plan  = [min(100,(m/36)**1.15*100) for m in meses]
    real  = [min(av, min(100, p*(1+0.04*(1 if m<18 else -0.3))+(m*0.25))) for m,p in zip(meses,plan)]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=meses, y=plan, name="Cronograma Planejado",
                               line=dict(color=C_BORDA, width=2, dash="dash")))
    fig3.add_trace(go.Scatter(x=meses, y=real, name="Avanço Realizado",
                               line=dict(color=C_NAVY, width=2.5),
                               fill="tonexty", fillcolor="rgba(201,168,76,0.12)"))
    fig3.add_vline(x=av/100*36, line_dash="dot", line_color=C_GOLD, line_width=2,
                   annotation_text=f"Hoje: {av:.0f}%",
                   annotation_font_color=C_GOLD, annotation_font_size=11)
    fig3.update_layout(**PLOT_BASE, height=300,
                       xaxis=dict(**GRID, title="Mês de obra"),
                       yaxis=dict(**GRID, title="Avanço Físico (%)", range=[0,110]))
    st.plotly_chart(fig3, use_container_width=True)
    atraso = plan[min(int(av/100*36), len(plan)-1)] - av if av<100 else 0
    cor_a = "alerta" if atraso>5 else "positivo"
    insight(f"{'Atraso de ' + str(round(atraso,1)) + 'pp em relação ao cronograma — risco de impacto no reconhecimento de receita (POC) no próximo trimestre.' if atraso>5 else 'Avanço de ' + str(round(av,0)) + '% alinhado ao cronograma. Receita reconhecida via POC de ' + fmt_M(rpoc) + ' reflete o estágio atual.'}", cor_a)

    st.markdown("---")
    st.markdown("##### POC Consolidado — Todos os Empreendimentos")
    poc = obra_f.groupby("nome_empreendimento").first().reset_index()[["nome_empreendimento","avanco_fisico_pct","receita_reconhecida_poc"]]
    poc = poc.sort_values("avanco_fisico_pct", ascending=True)
    cores_poc = [C_VERM if v<30 else (C_GOLD if v<70 else C_VERDE) for v in poc["avanco_fisico_pct"]]
    fig4 = go.Figure(go.Bar(
        x=poc["avanco_fisico_pct"], y=poc["nome_empreendimento"],
        orientation="h", marker_color=cores_poc,
        text=[f"{v:.0f}%" for v in poc["avanco_fisico_pct"]],
        textposition="outside",
        customdata=poc["receita_reconhecida_poc"].apply(fmt_M),
        hovertemplate="<b>%{y}</b><br>POC: %{x:.0f}%<br>Receita reconhecida: %{customdata}<extra></extra>",
    ))
    fig4.add_vline(x=50, line_dash="dash", line_color=C_MUTED, line_width=1,
                   annotation_text="50%", annotation_font_size=10)
    fig4.update_layout(**PLOT_BASE, height=400,
                       xaxis=dict(**GRID, range=[0,115]),
                       yaxis=dict(**NOGRID))
    st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  DRE GERENCIAL
# ═══════════════════════════════════════════════════════════════════════════════
elif "DRE" in pagina:
    st.markdown("## DRE Gerencial")
    st.caption("Resultado econômico pelo método POC · Receita reconhecida proporcional ao avanço físico da obra")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Receita Total POC",   fmt_M(dre_f["receita_reconhecida_poc"].sum()))
    c2.metric("Custo Total POC",     fmt_M(dre_f["custo_obra_poc"].sum()))
    c3.metric("Margem Bruta Média",  f"{dre_f['margem_bruta_pct'].mean():.1f}%")
    ebitda_pos = dre_f[dre_f["ebitda"]>0]["ebitda"].sum()
    c4.metric("EBITDA Acumulado",    fmt_M(ebitda_pos), help="Soma dos empreendimentos com EBITDA positivo")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Margem Bruta por Empreendimento (%)")
        df_m = dre_f.sort_values("margem_bruta_pct")
        cores_m = [C_VERM if v<25 else (C_GOLD if v<33 else C_VERDE) for v in df_m["margem_bruta_pct"]]
        fig = go.Figure(go.Bar(
            x=df_m["margem_bruta_pct"], y=df_m["nome"],
            orientation="h", marker_color=cores_m,
            text=[f"{v:.1f}%" for v in df_m["margem_bruta_pct"]],
            textposition="outside",
        ))
        fig.add_vline(x=30, line_dash="dash", line_color=C_MUTED, line_width=1,
                      annotation_text="Benchmark 30%", annotation_font_size=10)
        fig.update_layout(**PLOT_BASE, height=460,
                          xaxis=dict(**GRID, range=[0,55]),
                          yaxis=dict(**NOGRID))
        st.plotly_chart(fig, use_container_width=True)
        melhor = dre_f.loc[dre_f["margem_bruta_pct"].idxmax()]
        pior   = dre_f.loc[dre_f["margem_bruta_pct"].idxmin()]
        insight(f"<strong>{melhor['nome']}</strong>: melhor margem do portfólio com <strong>{melhor['margem_bruta_pct']:.1f}%</strong>. <strong>{pior['nome']}</strong> ({pior['margem_bruta_pct']:.1f}%) — revisar controle de custos de obra.", "info")

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
            connector={"line":{"color":C_BORDA}},
            increasing={"marker":{"color":C_VERDE}},
            decreasing={"marker":{"color":C_VERM}},
            totals={"marker":{"color":C_NAVY}},
        ))
        fig2.update_layout(**PLOT_BASE, height=290, showlegend=False,
                           xaxis=dict(**NOGRID),
                           yaxis=dict(**GRID, tickformat=",.0f"))
        st.plotly_chart(fig2, use_container_width=True)
        ebitda_pct = ebitda/receita*100 if receita>0 else 0
        cor_e = "positivo" if ebitda_pct>15 else ("alerta" if ebitda_pct<8 else "neutro")
        insight(f"EBITDA consolidado de <strong>{fmt_M(ebitda)}</strong> — margem EBITDA de <strong>{ebitda_pct:.1f}%</strong>. {'Desempenho acima da média do setor imobiliário SP (referência: 12-15%).' if ebitda_pct>15 else 'Margem EBITDA abaixo de 15% — avaliar estrutura de despesas administrativas.'}", cor_e)

        st.markdown("##### Margem por Linha de Produto")
        ml = dre_f.groupby("linha")["margem_bruta_pct"].mean().reset_index()
        fig3 = go.Figure(go.Bar(
            x=ml["linha"], y=ml["margem_bruta_pct"],
            marker_color=[LINHA_CORES.get(l,C_MUTED) for l in ml["linha"]],
            text=[f"{v:.1f}%" for v in ml["margem_bruta_pct"]],
            textposition="outside",
        ))
        fig3.add_hline(y=30, line_dash="dash", line_color=C_MUTED, line_width=1)
        fig3.update_layout(**PLOT_BASE, height=210,
                           xaxis=dict(**NOGRID),
                           yaxis=dict(**GRID, range=[0,50]))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.markdown("##### Análise Bidimensional: Margem Bruta × VSO Acumulado")
    fig4 = go.Figure()
    for sl, cor in STATUS_CORES.items():
        sub = dre_f[dre_f["status_label"]==sl]
        if len(sub):
            fig4.add_trace(go.Scatter(
                x=sub["vso_acumulado_pct"], y=sub["margem_bruta_pct"],
                mode="markers+text", name=sl,
                marker=dict(color=cor, size=sub["vgv_lancado"]/4_000_000+8,
                            opacity=0.85, line=dict(color=C_BRANCO, width=1.5)),
                text=sub["nome"], textposition="top center",
                textfont=dict(size=9, color=C_MUTED),
                hovertemplate="<b>%{text}</b><br>VSO: %{x:.1f}%<br>Margem: %{y:.1f}%<extra></extra>",
            ))
    fig4.add_hline(y=30, line_dash="dash", line_color=C_MUTED, line_width=1,
                   annotation_text="Margem benchmark 30%", annotation_font_size=10)
    fig4.add_vline(x=80, line_dash="dash", line_color=C_MUTED, line_width=1,
                   annotation_text="VSO meta 80%", annotation_font_size=10)
    fig4.update_layout(**PLOT_BASE, height=430,
                       xaxis=dict(**GRID, title="VSO Acumulado (%)", range=[0,105]),
                       yaxis=dict(**GRID, title="Margem Bruta (%)", range=[0,55]))
    st.plotly_chart(fig4, use_container_width=True)
    q_ideal = len(dre_f[(dre_f["vso_acumulado_pct"]>=80)&(dre_f["margem_bruta_pct"]>=30)])
    cor_q = "positivo" if q_ideal>=len(dre_f)//2 else "neutro"
    insight(f"<strong>{q_ideal} de {len(dre_f)} empreendimentos</strong> atingem simultaneamente VSO ≥ 80% e margem ≥ 30% (quadrante ideal). O tamanho de cada bolha representa o VGV lançado.", cor_q)

    st.markdown("---")
    st.markdown("##### DRE Detalhado por Empreendimento")
    cols = ["nome","linha","status_label","vgv_lancado","vso_acumulado_pct",
            "receita_reconhecida_poc","custo_obra_poc","margem_bruta_pct","ebitda","ebitda_pct"]
    tab = dre_f[cols].copy()
    for c in ["vgv_lancado","receita_reconhecida_poc","custo_obra_poc","ebitda"]:
        tab[c] = tab[c].apply(fmt_M)
    tab.columns = ["Empreendimento","Linha","Status","VGV","VSO %","Receita POC","Custo POC","Margem %","EBITDA","EBITDA %"]
    st.dataframe(tab, use_container_width=True, hide_index=True)
