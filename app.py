import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from pathlib import Path

st.set_page_config(
    page_title="Portfólio Imobiliário | Analytics SP",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  PALETA NAVY & GOLD
# ══════════════════════════════════════════════════════════════
C_NAVY   = "#0D2137"
C_NAVY2  = "#152C47"
C_NAVY3  = "#1A3555"
C_GOLD   = "#C9A84C"
C_GOLD_L = "#E8C96A"
C_BG     = "#0F1923"
C_CARD   = "#162330"
C_BORDER = "#1E3045"
C_TEXT   = "#E8EDF2"
C_MUTED  = "#7A93A8"
C_VERDE  = "#2ECC71"
C_VERM   = "#E74C3C"
C_AZUL   = "#3498DB"
C_PLOT   = "#162330"
C_GRID   = "#1E3045"

STATUS_LABELS = {"entregue":"Entregue","em_obra":"Em Obra","lancamento":"Lançamento"}
STATUS_CORES  = {"Entregue":C_VERDE,"Em Obra":C_AZUL,"Lançamento":C_GOLD}
LINHA_CORES   = {"Premium":C_GOLD,"Alto Padrão":C_AZUL,"Smart":C_MUTED}

# ── CSS ───────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif!important;}}
.stApp{{background:{C_BG};}}
.main .block-container{{padding-top:1.2rem;padding-bottom:2rem;}}
[data-testid="stSidebar"]{{background:{C_NAVY}!important;border-right:1px solid {C_BORDER};}}
[data-testid="stSidebar"] *{{color:#B0C4D8!important;}}
[data-testid="stSidebar"] .stSelectbox>label{{color:{C_GOLD}!important;font-size:10px!important;font-weight:700!important;text-transform:uppercase;letter-spacing:.1em;}}
[data-testid="stSidebar"] .stButton>button{{background:transparent!important;border:none!important;border-left:3px solid transparent!important;border-radius:0!important;color:#7A93A8!important;font-size:13px!important;text-align:left!important;padding:9px 18px!important;width:100%!important;transition:all .15s;font-weight:400!important;}}
[data-testid="stSidebar"] .stButton>button:hover{{background:rgba(201,168,76,.10)!important;color:{C_GOLD_L}!important;border-left-color:{C_GOLD}!important;}}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{{color:#F0E6C8!important;border-left-color:{C_GOLD}!important;background:rgba(201,168,76,.16)!important;font-weight:600!important;}}
[data-testid="stMetric"]{{background:{C_CARD}!important;border:1px solid {C_BORDER}!important;border-top:3px solid {C_GOLD}!important;border-radius:8px;padding:16px 18px!important;}}
[data-testid="stMetricLabel"]{{font-size:10px!important;text-transform:uppercase;letter-spacing:.07em;color:{C_MUTED}!important;font-weight:600!important;}}
[data-testid="stMetricValue"]{{font-size:22px!important;color:{C_TEXT}!important;font-weight:700!important;}}
[data-testid="stMetricDelta"]{{font-size:11px!important;}}
h1,h2,h3,h4,h5{{color:{C_TEXT}!important;}}
h1{{font-weight:700!important;font-size:23px!important;letter-spacing:-.3px;}}
p,span,div,label{{color:{C_TEXT};}}
.ct{{font-size:13px;font-weight:600;color:{C_TEXT};margin-bottom:1px;letter-spacing:.01em;}}
.cd{{font-size:11px;color:{C_MUTED};margin-bottom:6px;line-height:1.5;font-style:italic;}}
.ins{{border-left:4px solid {C_GOLD};background:{C_CARD};padding:10px 14px;border-radius:0 6px 6px 0;margin-bottom:7px;font-size:12.5px;color:{C_TEXT};line-height:1.55;}}
.ins.ok {{border-left-color:{C_VERDE};background:#0E2119;}}
.ins.bad{{border-left-color:{C_VERM};background:#200D0D;}}
.ins.info{{border-left-color:{C_AZUL};background:#0C1E2D;}}
.ins.warn{{border-left-color:{C_GOLD};background:{C_CARD};}}
.rag-ok  {{background:#0E2119;border:1px solid {C_VERDE};border-radius:8px;padding:10px 14px;}}
.rag-warn{{background:#1A1408;border:1px solid {C_GOLD};border-radius:8px;padding:10px 14px;}}
.rag-bad {{background:#200D0D;border:1px solid {C_VERM};border-radius:8px;padding:10px 14px;}}
hr{{border-color:{C_BORDER};margin:.8rem 0;}}
[data-testid="stDataFrame"]{{border:1px solid {C_BORDER}!important;border-radius:8px;}}
.stCaption p{{color:{C_MUTED}!important;font-size:11px!important;}}
</style>
""", unsafe_allow_html=True)

# ── DADOS ─────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_all():
    emp  = pd.read_csv(DATA_DIR / "empreendimentos.csv",  parse_dates=["lancamento","entrega_prevista"])
    vend = pd.read_csv(DATA_DIR / "vendas_mensais.csv",   parse_dates=["data"])
    obra = pd.read_csv(DATA_DIR / "custo_obra.csv")
    dre  = pd.read_csv(DATA_DIR / "dre_gerencial.csv")
    fc   = pd.read_csv(DATA_DIR / "fluxo_caixa.csv",      parse_dates=["data"])
    bud  = pd.read_csv(DATA_DIR / "budget_realizado.csv")
    proj = pd.read_csv(DATA_DIR / "projecoes.csv",         parse_dates=["data"])
    return emp, vend, obra, dre, fc, bud, proj

emp, vendas, obra, dre, fc, bud, proj = load_all()
dre["status_label"] = dre["status"].map(STATUS_LABELS).fillna(dre["status"])

# ── HELPERS ───────────────────────────────────────────────────
def fM(v):
    try:
        v=float(v)
        if abs(v)>=1_000_000_000: return f"R$ {v/1_000_000_000:.1f}B"
        if abs(v)>=1_000_000:     return f"R$ {v/1_000_000:.1f}M"
        return f"R$ {v/1_000:.0f}K"
    except: return "—"

def ins(t,tp="warn"):
    st.markdown(f'<div class="ins {tp}">{t}</div>', unsafe_allow_html=True)

def hdr(title, desc):
    st.markdown(f'<p class="ct">{title}</p><p class="cd">{desc}</p>', unsafe_allow_html=True)

def rag_card(nome, score, motivo, cls):
    dot = {"ok":"🟢","warn":"🟡","bad":"🔴"}[cls]
    st.markdown(f'<div class="rag-{cls}"><strong style="font-size:12px;">{dot} {nome}</strong>'
                f'<br><span style="font-size:11px;color:{C_MUTED};">{motivo}</span></div>',
                unsafe_allow_html=True)

def L(h=280, **kw):
    d = dict(height=h, plot_bgcolor=C_PLOT, paper_bgcolor=C_PLOT,
             font=dict(family="Inter,sans-serif",color=C_TEXT,size=11),
             margin=dict(l=12,r=20,t=10,b=10),
             legend=dict(orientation="h",yanchor="bottom",y=1.02,
                         bgcolor="rgba(0,0,0,0)",font=dict(size=10,color=C_MUTED)))
    d.update(kw)
    return d

def AX(title="",fmt="",rng=None,grid=True,ang=0,vis=True):
    d = dict(title=dict(text=title,font=dict(size=10,color=C_MUTED)),
             showgrid=grid,gridcolor=C_GRID,gridwidth=1,zeroline=False,
             tickfont=dict(size=10,color=C_MUTED),tickangle=ang,
             linecolor=C_BORDER,linewidth=1,showline=True,visible=vis)
    if fmt: d["tickformat"]=fmt
    if rng: d["range"]=rng
    return d

def AXH():
    return dict(showgrid=False,zeroline=False,showline=False,
                tickfont=dict(size=10,color=C_MUTED),title="")

# ══════════════════════════════════════════════════════════════
#  SIDEBAR — filtros encadeados
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""<div style="padding:20px 16px 10px;">
        <div style="font-size:10px;color:{C_GOLD};text-transform:uppercase;letter-spacing:.14em;font-weight:700;">Portfólio Imobiliário</div>
        <div style="font-size:12px;color:{C_MUTED};margin-top:2px;">Analytics · São Paulo SP</div>
    </div><hr style="border-color:{C_BORDER};margin:0 0 6px;">""", unsafe_allow_html=True)

    PAGES = ["⚡  Executive Summary","🏠  Visão Geral","📈  Comercial & VSO",
             "🏗️  Obras & POC","📊  DRE Gerencial","💰  Fluxo de Caixa",
             "🎯  FP&A & Projeções","🔬  Cohort de Lançamentos"]
    if "pg" not in st.session_state: st.session_state.pg = PAGES[0]
    for p in PAGES:
        ativo = st.session_state.pg == p
        if st.button(p, key=p, use_container_width=True,
                     type="primary" if ativo else "secondary"):
            st.session_state.pg = p
            st.rerun()

    st.markdown(f'<hr style="border-color:{C_BORDER};margin:8px 0 4px;">', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:10px;color:{C_GOLD};text-transform:uppercase;letter-spacing:.1em;font-weight:700;padding:2px 4px 5px;">Filtros</p>', unsafe_allow_html=True)

    bairros_all = sorted(emp["bairro"].unique())
    filtro_bairro = st.selectbox("Bairro", ["Todos"] + bairros_all, key="fb")

    emp_b = emp if filtro_bairro=="Todos" else emp[emp["bairro"]==filtro_bairro]
    s_raw = sorted(emp_b["status"].unique())
    s_opts = ["Todos"] + [STATUS_LABELS[s] for s in s_raw if s in STATUS_LABELS]
    if st.session_state.get("_lb") != filtro_bairro:
        st.session_state["fs"] = "Todos"
    st.session_state["_lb"] = filtro_bairro
    filtro_status_lbl = st.selectbox("Status", s_opts, key="fs")
    s_rev = {v:k for k,v in STATUS_LABELS.items()}
    filtro_status = s_rev.get(filtro_status_lbl,"Todos")

    emp_bs = emp_b if filtro_status=="Todos" else emp_b[emp_b["status"]==filtro_status]
    l_raw = sorted(emp_bs["linha"].unique())
    l_opts = ["Todos"] + l_raw
    if st.session_state.get("_ls") != filtro_status_lbl:
        st.session_state["fl"] = "Todos"
    st.session_state["_ls"] = filtro_status_lbl
    filtro_linha = st.selectbox("Linha de Produto", l_opts, key="fl")

    st.markdown(f'<hr style="border-color:{C_BORDER};margin:8px 0 4px;">', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:10px;color:{C_GOLD};text-transform:uppercase;letter-spacing:.1em;font-weight:700;padding:2px 4px 5px;">Período</p>', unsafe_allow_html=True)
    _min_d = vendas["data"].min().date()
    _max_d = vendas["data"].max().date()
    date_range = st.date_input("Intervalo de análise", value=(_min_d, _max_d),
                               min_value=_min_d, max_value=_max_d, key="dr")
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        dt_ini = pd.Timestamp(date_range[0])
        dt_fim = pd.Timestamp(date_range[1])
    else:
        dt_ini = pd.Timestamp(_min_d)
        dt_fim = pd.Timestamp(_max_d)

pg = st.session_state.pg

# ── Aplicar filtros ───────────────────────────────────────────
emp_f = emp.copy()
if filtro_bairro!="Todos": emp_f=emp_f[emp_f["bairro"]==filtro_bairro]
if filtro_status!="Todos": emp_f=emp_f[emp_f["status"]==filtro_status]
if filtro_linha !="Todos": emp_f=emp_f[emp_f["linha"]==filtro_linha]

ids_f  = emp_f["id"].tolist()
vend_f = vendas[vendas["id_empreendimento"].isin(ids_f)]
obra_f = obra[obra["id_empreendimento"].isin(ids_f)]
dre_f  = dre[dre["id_empreendimento"].isin(ids_f)].copy()
fc_f   = fc[fc["id_empreendimento"].isin(ids_f)]
bud_f  = bud[bud["id_empreendimento"].isin(ids_f)]
proj_f = proj[proj["id_empreendimento"].isin(ids_f)]

# Aplicar filtro de período nos datasets temporais
vend_f = vend_f[(vend_f["data"] >= dt_ini) & (vend_f["data"] <= dt_fim)]
fc_f   = fc_f[(fc_f["data"] >= dt_ini) & (fc_f["data"] <= dt_fim)]
proj_f = proj_f[(proj_f["data"] >= dt_ini) & (proj_f["data"] <= dt_fim)]

if len(dre_f)==0:
    st.warning("⚠️ Nenhum empreendimento encontrado para os filtros selecionados.")
    st.stop()

# ══════════════════════════════════════════════════════════════
#  EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════
if "Executive" in pg:
    st.markdown("## Executive Summary")
    st.caption("Visão consolidada para diretoria · Semáforo de performance · Alertas automáticos de risco")

    # KPIs executivos
    vgv_t  = emp_f["vgv_total"].sum()
    vgv_v  = dre_f["vgv_vendido"].sum()
    mg_m   = dre_f["margem_bruta_pct"].mean()
    vso_m  = dre_f["vso_acumulado_pct"].mean()
    ebitda = dre_f[dre_f["ebitda"]>0]["ebitda"].sum()
    rec_poc= dre_f["receita_reconhecida_poc"].sum()
    fc_sal = fc_f["saldo_mes"].sum()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Empreendimentos",            f"{len(dre_f)}")
    c2.metric("VGV Total Lançado",          fM(vgv_t))
    c3.metric("VGV Vendido",                fM(vgv_v),
              delta=f"{vgv_v/vgv_t*100:.1f}% do total")
    c4.metric("Margem Bruta Média",         f"{mg_m:.1f}%",
              delta="▲ vs bench 30%" if mg_m>=30 else "▼ vs bench 30%",
              delta_color="normal" if mg_m>=30 else "inverse")
    c5.metric("Receita Reconhecida (POC)",  fM(rec_poc))
    c6.metric("EBITDA Acumulado",           fM(ebitda))

    st.markdown("---")

    # Semáforo RAG
    st.markdown(f'<p class="ct">🚦 Semáforo de Performance — Todos os Empreendimentos</p>'
                f'<p class="cd">Classificação automática por margem bruta, VSO e avanço de obra. '
                f'Verde: todos os indicadores saudáveis. Amarelo: atenção em pelo menos um. Vermelho: risco alto.</p>',
                unsafe_allow_html=True)

    def rag_score(row):
        pts = 0
        motivos = []
        if row["margem_bruta_pct"] < 25:
            pts += 2; motivos.append(f"Margem {row['margem_bruta_pct']:.1f}% < 25%")
        elif row["margem_bruta_pct"] < 30:
            pts += 1; motivos.append(f"Margem {row['margem_bruta_pct']:.1f}% < 30%")
        if row["vso_acumulado_pct"] < 70:
            pts += 2; motivos.append(f"VSO {row['vso_acumulado_pct']:.1f}% < 70%")
        elif row["vso_acumulado_pct"] < 80:
            pts += 1; motivos.append(f"VSO {row['vso_acumulado_pct']:.1f}% < 80%")
        if row["ebitda_pct"] < 0:
            pts += 2; motivos.append("EBITDA negativo")
        elif row["ebitda_pct"] < 8:
            pts += 1; motivos.append(f"EBITDA {row['ebitda_pct']:.1f}% < 8%")
        cls = "bad" if pts>=3 else ("warn" if pts>=1 else "ok")
        mot = " · ".join(motivos) if motivos else "Todos os indicadores saudáveis"
        return cls, mot

    # Agrupar em 3 colunas
    dre_rag = dre_f.sort_values("nome").reset_index(drop=True)
    cols_rag = st.columns(3)
    for i, row in dre_rag.iterrows():
        cls, mot = rag_score(row)
        with cols_rag[i % 3]:
            rag_card(row["nome"], 0, mot, cls)

    st.markdown("---")

    # Ranking de performance
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        hdr("Ranking de Desempenho — Margem Bruta (%)",
            "Empreendimentos ordenados por margem bruta. "
            "Permite identificar rapidamente quais projetos estão entregando melhor resultado operacional.")
        rk = dre_f.sort_values("margem_bruta_pct", ascending=True)
        cores_rk = [C_VERM if v<25 else (C_GOLD if v<33 else C_VERDE) for v in rk["margem_bruta_pct"]]
        fig = go.Figure(go.Bar(
            x=rk["margem_bruta_pct"], y=rk["nome"], orientation="h",
            marker_color=cores_rk,
            text=[f"{v:.1f}%" for v in rk["margem_bruta_pct"]],
            textposition="outside", textfont=dict(size=10,color=C_MUTED),
        ))
        fig.add_vline(x=30, line_dash="dash", line_color=C_MUTED, line_width=1,
                      annotation_text="Benchmark: 30%", annotation_font_size=9)
        fig.update_layout(**L(h=420), xaxis=AX(rng=[0,55]), yaxis=AXH())
        st.plotly_chart(fig, use_container_width=True)

    with col_r2:
        hdr("Mapa de Calor — Margem Bruta por Bairro × Linha de Produto",
            "Cruzamento estratégico: identifica quais combinações de localização e produto "
            "entregam melhor margem bruta. Ferramenta central para decisão de novos lançamentos.")
        heat = dre_f.groupby(["bairro","linha"])["margem_bruta_pct"].mean().reset_index()
        pivot = heat.pivot(index="bairro", columns="linha", values="margem_bruta_pct").fillna(0)
        fig2 = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0,C_VERM],[0.4,C_GOLD],[1,C_VERDE]],
            text=[[f"{v:.1f}%" if v>0 else "—" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            textfont=dict(size=11, color=C_TEXT),
            hovertemplate="Bairro: %{y}<br>Linha: %{x}<br>Margem: %{text}<extra></extra>",
            colorbar=dict(
                tickfont=dict(color=C_MUTED,size=10),
                title=dict(text="%",font=dict(color=C_MUTED,size=10)),
                bgcolor=C_CARD, bordercolor=C_BORDER,
            ),
        ))
        fig2.update_layout(**L(h=420), xaxis=AX(grid=False), yaxis=AX(grid=False))
        st.plotly_chart(fig2, use_container_width=True)

    # Alertas automáticos
    st.markdown("---")
    st.markdown(f'<p class="ct">⚠️ Alertas Automáticos de Risco</p>'
                f'<p class="cd">Itens que requerem atenção imediata da diretoria.</p>',
                unsafe_allow_html=True)
    alertas = []
    for _, row in dre_f.iterrows():
        if row["margem_bruta_pct"] < 25:
            alertas.append(("bad", f"<strong>{row['nome']}</strong>: Margem bruta crítica de {row['margem_bruta_pct']:.1f}% — abaixo do mínimo aceitável de 25%."))
        if row["vso_acumulado_pct"] < 70 and row["status"] not in ["lancamento"]:
            alertas.append(("bad", f"<strong>{row['nome']}</strong>: VSO de {row['vso_acumulado_pct']:.1f}% — estoque com baixa absorção. Risco de fluxo de caixa."))
        if row["ebitda_pct"] < 0:
            alertas.append(("bad", f"<strong>{row['nome']}</strong>: EBITDA negativo ({row['ebitda_pct']:.1f}%) — despesas superiores à receita reconhecida no período."))
    for _, row in dre_f.iterrows():
        if 25 <= row["margem_bruta_pct"] < 30:
            alertas.append(("warn", f"<strong>{row['nome']}</strong>: Margem bruta de {row['margem_bruta_pct']:.1f}% — abaixo do benchmark de 30%. Monitorar."))
        if 70 <= row["vso_acumulado_pct"] < 80:
            alertas.append(("warn", f"<strong>{row['nome']}</strong>: VSO de {row['vso_acumulado_pct']:.1f}% — abaixo da meta de 80%. Intensificar ações comerciais."))
    if not alertas:
        ins("Nenhum alerta crítico identificado. Todos os empreendimentos dentro dos parâmetros aceitáveis.", "ok")
    else:
        a1, a2 = st.columns(2)
        for i, (tp, txt) in enumerate(alertas[:10]):
            with (a1 if i%2==0 else a2):
                ins(txt, tp)


# ══════════════════════════════════════════════════════════════
#  VISÃO GERAL
# ══════════════════════════════════════════════════════════════
elif "Visão Geral" in pg:
    st.markdown("## Visão Geral do Portfólio")
    st.caption(f"**{len(dre_f)} empreendimentos** · Alto padrão São Paulo · Dados sintéticos calibrados Secovi-SP / ABRAINC-FIPE")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Empreendimentos",                    f"{len(dre_f)}")
    c2.metric("Valor Geral de Vendas Total",         fM(emp_f["vgv_total"].sum()))
    c3.metric("Valor Geral de Vendas Vendido",       fM(dre_f["vgv_vendido"].sum()))
    c4.metric("Velocidade de Vendas Média (VSO)",    f"{dre_f['vso_acumulado_pct'].mean():.1f}%")
    c5.metric("Margem Bruta Média",                  f"{dre_f['margem_bruta_pct'].mean():.1f}%")

    st.markdown("---")
    col_a, col_b = st.columns([1.5, 1])
    with col_a:
        hdr("Valor Geral de Vendas (VGV) por Empreendimento",
            "Potencial máximo de receita de cada projeto ao preço de tabela, segmentado por status. "
            "Empreendimentos maiores representam maior exposição financeira e potencial de resultado.")
        plot = dre_f.sort_values("vgv_lancado").copy()
        fig = go.Figure()
        for sl, cor in STATUS_CORES.items():
            sub = plot[plot["status_label"]==sl]
            if len(sub):
                fig.add_trace(go.Bar(
                    x=sub["vgv_lancado"], y=sub["nome"],
                    name=sl, orientation="h", marker_color=cor,
                    text=sub["vgv_lancado"].apply(fM), textposition="outside",
                    textfont=dict(size=10,color=C_MUTED),
                    hovertemplate="<b>%{y}</b><br>VGV: %{text}<extra></extra>",
                ))
        fig.update_layout(**L(h=430,barmode="stack"), xaxis=AX(fmt=",.0f"), yaxis=AXH())
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        hdr("Status do Portfólio", "Proporção entre empreendimentos entregues, em obra e em lançamento.")
        sc = emp_f["status"].map(STATUS_LABELS).value_counts().reset_index()
        sc.columns = ["status","qtd"]
        fig2 = go.Figure(go.Pie(
            labels=sc["status"], values=sc["qtd"], hole=0.62,
            marker_colors=[STATUS_CORES.get(s,C_MUTED) for s in sc["status"]],
            textinfo="label+percent", textfont=dict(size=10,color=C_TEXT),
        ))
        fig2.update_layout(plot_bgcolor=C_PLOT,paper_bgcolor=C_PLOT,
                           font=dict(family="Inter,sans-serif",color=C_TEXT,size=11),
                           height=190,showlegend=False,margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True)

        hdr("Linha de Produto", "Segmentação entre Premium, Alto Padrão e Smart.")
        lc = emp_f["linha"].value_counts().reset_index(); lc.columns=["linha","qtd"]
        fig3 = go.Figure(go.Bar(
            x=lc["linha"], y=lc["qtd"],
            marker_color=[LINHA_CORES.get(l,C_MUTED) for l in lc["linha"]],
            text=lc["qtd"], textposition="outside", textfont=dict(size=11,color=C_MUTED),
        ))
        fig3.update_layout(**L(h=175), xaxis=AX(grid=False), yaxis=dict(visible=False,showgrid=False,zeroline=False))
        st.plotly_chart(fig3, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        hdr("VGV Lançado por Ano e Linha de Produto",
            "Evolução do volume de lançamentos. Crescimento indica expansão; concentração em uma linha indica foco estratégico.")
        emp_f2 = emp_f.copy(); emp_f2["ano"]=emp_f2["lancamento"].dt.year
        vgv_ano = emp_f2.groupby(["ano","linha"])["vgv_total"].sum().reset_index()
        fig4 = px.bar(vgv_ano, x="ano", y="vgv_total", color="linha",
                      color_discrete_map=LINHA_CORES, barmode="stack",
                      labels={"ano":"Ano","vgv_total":"VGV (R$)","linha":"Linha"})
        fig4.update_layout(**L(h=250), xaxis=AX(grid=False), yaxis=AX(fmt=",.0f"))
        st.plotly_chart(fig4, use_container_width=True)

    with col_d:
        hdr("VGV Total por Bairro",
            "Concentração geográfica do portfólio. Bairros com maior VGV têm maior exposição de capital.")
        vgv_b = emp_f.groupby("bairro")["vgv_total"].sum().reset_index().sort_values("vgv_total",ascending=True)
        fig5 = go.Figure(go.Bar(
            x=vgv_b["vgv_total"], y=vgv_b["bairro"], orientation="h",
            marker_color=C_NAVY3, marker_line=dict(color=C_GOLD,width=0.5),
            text=vgv_b["vgv_total"].apply(fM), textposition="outside",
            textfont=dict(size=10,color=C_MUTED),
        ))
        fig5.update_layout(**L(h=250), xaxis=AX(fmt=",.0f"), yaxis=AXH())
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")
    st.markdown(f'<p class="ct">💡 Análise Executiva</p>', unsafe_allow_html=True)
    melhor   = dre_f.loc[dre_f["margem_bruta_pct"].idxmax()]
    pior_vso = dre_f.loc[dre_f["vso_acumulado_pct"].idxmin()]
    lanc_vgv = emp_f[emp_f["status"]=="lancamento"]["vgv_total"].sum()
    acima    = len(dre_f[dre_f["margem_bruta_pct"]>=30])
    i1,i2,i3 = st.columns(3)
    with i1:
        ins(f"<strong>{melhor['nome']}</strong> lidera com margem bruta de <strong>{melhor['margem_bruta_pct']:.1f}%</strong> — {melhor['margem_bruta_pct']-30:.1f}pp acima do benchmark de 30% do mercado SP.", "ok")
    with i2:
        ins(f"<strong>{acima} de {len(dre_f)}</strong> empreendimentos superam o benchmark de 30%. Pipeline de lançamentos de <strong>{fM(lanc_vgv)}</strong> garante crescimento nos próximos ciclos.", "info")
    with i3:
        tp = "bad" if pior_vso["vso_acumulado_pct"]<75 else "warn"
        ins(f"Atenção: <strong>{pior_vso['nome']}</strong> com VSO acumulado de <strong>{pior_vso['vso_acumulado_pct']:.1f}%</strong>. {'Revisar estratégia comercial urgente.' if pior_vso['vso_acumulado_pct']<70 else 'Abaixo da meta de 80%.'}", tp)


# ══════════════════════════════════════════════════════════════
#  COMERCIAL & VSO
# ══════════════════════════════════════════════════════════════
elif "Comercial" in pg:
    st.markdown("## Comercial & Velocidade de Vendas sobre Oferta (VSO)")
    st.caption("Acompanhamento mensal de vendas, distratos e VGV comercializado")

    sel = st.selectbox("Empreendimento", ["Portfólio Consolidado"]+dre_f["nome"].tolist())
    if sel!="Portfólio Consolidado":
        id_s = dre_f[dre_f["nome"]==sel]["id_empreendimento"].values[0]
        vp   = vend_f[vend_f["id_empreendimento"]==id_s].copy()
    else:
        vp = vend_f.groupby("data").agg(
            unidades_vendidas=("unidades_vendidas","sum"),
            distratos=("distratos","sum"),
            vgv_mes=("vgv_mes","sum"),
            vso_pct=("vso_pct","mean"),
        ).reset_index()

    tv   = vp["unidades_vendidas"].sum()
    td   = vp["distratos"].sum()
    vgvc = vp["vgv_mes"].sum()
    txd  = td/tv*100 if tv>0 else 0
    vp_ord = vp.sort_values("data")
    vrec = vp_ord.iloc[-1]["vso_pct"] if len(vp) else 0
    vso_3m = vp_ord.tail(3)["vso_pct"].mean() if len(vp)>=3 else vrec

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Unidades Vendidas",                    f"{tv:,.0f}")
    c2.metric("Distratos (Cancelamentos)",             f"{td:,.0f}", delta=f"-{txd:.1f}% da base", delta_color="inverse")
    c3.metric("Valor Geral de Vendas Comercializado",  fM(vgvc))
    c4.metric("VSO — Último Mês",                     f"{vrec:.1f}%",
              delta="acima de 10%" if vrec>=10 else "abaixo de 10%",
              delta_color="normal" if vrec>=10 else "inverse")
    c5.metric("Absorção Média — Últimos 3M",           f"{vso_3m:.1f}%",
              delta="acima de 10%" if vso_3m>=10 else "abaixo de 10%",
              delta_color="normal" if vso_3m>=10 else "inverse")

    st.markdown("---")
    vp_s = vp.sort_values("data")
    col1,col2 = st.columns(2)
    with col1:
        hdr("Velocidade de Vendas sobre Oferta (VSO) — Mensal (%)",
            "% do estoque disponível vendido por mês. Acima de 10%/mês é saudável (Secovi-SP). "
            "Queda sustentada indica necessidade de ação comercial ou revisão de preços.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=vp_s["data"],y=vp_s["vso_pct"],mode="lines+markers",
                                  line=dict(color=C_GOLD,width=2.5),
                                  marker=dict(size=4,color=C_GOLD_L),
                                  fill="tozeroy",fillcolor="rgba(201,168,76,0.10)"))
        fig.add_hline(y=10,line_dash="dash",line_color=C_VERM,line_width=1.2,
                      annotation_text="Mínimo saudável: 10%",
                      annotation_font_size=10,annotation_font_color=C_VERM)
        fig.update_layout(**L(h=265), xaxis=AX(), yaxis=AX(title="VSO (%)"))
        st.plotly_chart(fig, use_container_width=True)
        ins(f"VSO mais recente: <strong>{vrec:.1f}%</strong> — {'abaixo do mínimo de 10%. Ação comercial recomendada.' if vrec<10 else 'acima do benchmark de 10% (Secovi-SP).'}", "bad" if vrec<10 else "ok")

    with col2:
        hdr("Valor Geral de Vendas (VGV) Comercializado — Mensal",
            "Volume financeiro de vendas efetivadas por mês. O pico ocorre no lançamento "
            "com desaceleração natural à medida que o estoque é absorvido pelo mercado.")
        fig2 = go.Figure(go.Bar(
            x=vp_s["data"],y=vp_s["vgv_mes"],
            marker_color=C_NAVY3,marker_line=dict(color=C_GOLD,width=0.4),
            hovertemplate="%{x|%b/%Y}: %{customdata}<extra></extra>",
            customdata=vp_s["vgv_mes"].apply(fM),
        ))
        fig2.update_layout(**L(h=265), xaxis=AX(), yaxis=AX(fmt=",.0f"))
        st.plotly_chart(fig2, use_container_width=True)
        mp = vp.loc[vp["vgv_mes"].idxmax(),"data"]
        ins(f"Pico de VGV em <strong>{mp.strftime('%b/%Y')}</strong> — {fM(vp['vgv_mes'].max())} comercializados.", "info")

    st.markdown("---")
    col3,col4 = st.columns(2)
    with col3:
        hdr("Unidades Vendidas vs Distratos (Cancelamentos) — Mensal",
            "Distratos elevados reduzem o VGV líquido e indicam problemas de financiamento ou inadequação do produto.")
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=vp_s["data"],y=vp_s["unidades_vendidas"],name="Vendidas",marker_color=C_GOLD))
        fig3.add_trace(go.Bar(x=vp_s["data"],y=vp_s["distratos"],name="Distratos",marker_color=C_VERM))
        fig3.update_layout(**L(h=265),barmode="group",xaxis=AX(),yaxis=AX())
        st.plotly_chart(fig3, use_container_width=True)
        ins(f"Taxa de distrato acumulada: <strong>{txd:.1f}%</strong> — {'acima do limite de 5%. Revisar canal de vendas e perfil de crédito.' if txd>5 else 'dentro do limite aceitável de 5%.'}", "bad" if txd>5 else "ok")

    with col4:
        hdr("Velocidade de Vendas (VSO) Acumulada por Bairro",
            "VSO médio por bairro. Acima de 85%: alta absorção. Abaixo de 70%: saturação ou inadequação do produto.")
        vso_b = dre_f.groupby("bairro")["vso_acumulado_pct"].mean().reset_index().sort_values("vso_acumulado_pct",ascending=True)
        cv = [C_VERM if v<70 else (C_GOLD if v<85 else C_VERDE) for v in vso_b["vso_acumulado_pct"]]
        fig4 = go.Figure(go.Bar(
            x=vso_b["vso_acumulado_pct"],y=vso_b["bairro"],orientation="h",
            marker_color=cv,
            text=[f"{v:.1f}%" for v in vso_b["vso_acumulado_pct"]],
            textposition="outside",textfont=dict(size=10,color=C_MUTED),
        ))
        fig4.add_vline(x=85,line_dash="dash",line_color=C_MUTED,line_width=1,
                       annotation_text="Meta: 85%",annotation_font_size=10)
        fig4.update_layout(**L(h=265), xaxis=AX(rng=[0,115]), yaxis=AXH())
        st.plotly_chart(fig4, use_container_width=True)
        top_b=vso_b.iloc[-1]; bot_b=vso_b.iloc[0]
        ins(f"<strong>{top_b['bairro']}</strong> lidera com {top_b['vso_acumulado_pct']:.1f}%. "
            f"<strong>{bot_b['bairro']}</strong> ({bot_b['vso_acumulado_pct']:.1f}%) — oportunidade de revisão comercial.", "info")


# ══════════════════════════════════════════════════════════════
#  OBRAS & POC
# ══════════════════════════════════════════════════════════════
elif "Obras" in pg:
    st.markdown("## Obras & Percentual de Conclusão (POC)")
    st.caption("Reconhecimento de receita proporcional ao avanço físico · Desvio de orçamento · Curva S")

    opcoes = obra_f["nome_empreendimento"].unique().tolist()
    if not opcoes: st.warning("Sem dados para os filtros."); st.stop()
    sel_o = st.selectbox("Empreendimento", opcoes)
    o = obra_f[obra_f["nome_empreendimento"]==sel_o]

    av=o["avanco_fisico_pct"].iloc[0]; rpoc=o["receita_reconhecida_poc"].iloc[0]
    corc=o["custo_orcado"].sum(); crea=o["custo_realizado"].sum(); dmed=o["desvio_pct"].mean()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Avanço Físico — % de Conclusão", f"{av:.0f}%")
    c2.metric("Receita Reconhecida (POC)",       fM(rpoc))
    c3.metric("Custo Realizado vs Orçado",       fM(crea), delta=fM(crea-corc), delta_color="inverse")
    c4.metric("Desvio Médio de Custo",           f"{dmed:+.1f}%", delta_color="inverse")

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        hdr("Custo Orçado vs Realizado por Etapa",
            "Comparativo entre orçamento original e custo incorrido por fase. "
            "Desvios positivos reduzem diretamente a margem bruta projetada no lançamento.")
        fig=go.Figure()
        fig.add_trace(go.Bar(x=o["etapa_obra"],y=o["custo_orcado"],name="Orçado",
                             marker_color=C_BORDER,marker_line=dict(color=C_MUTED,width=1)))
        fig.add_trace(go.Bar(x=o["etapa_obra"],y=o["custo_realizado"],name="Realizado",
                             marker_color=C_NAVY3,marker_line=dict(color=C_GOLD,width=0.5)))
        fig.update_layout(**L(h=285),barmode="group",xaxis=AX(grid=False),yaxis=AX(fmt=",.0f"))
        st.plotly_chart(fig, use_container_width=True)
        ec=o.loc[o["desvio_pct"].idxmax(),"etapa_obra"]; dc=o["desvio_pct"].max()
        ins(f"Maior desvio: etapa <strong>{ec}</strong> com <strong>{dc:+.1f}%</strong> sobre o orçado. "
            f"{'Requer plano de contenção.' if dc>8 else 'Dentro da margem tolerável de até +8%.'}", "bad" if dc>8 else "warn" if dc>3 else "ok")

    with col2:
        hdr("Desvio Percentual de Custo por Etapa",
            "Verde: economia. Dourado: desvio moderado. Vermelho: desvio crítico (>8%). "
            "Cada ponto percentual de desvio comprime diretamente a margem bruta.")
        cd=[C_VERM if d>8 else (C_GOLD if d>0 else C_VERDE) for d in o["desvio_pct"]]
        fig2=go.Figure(go.Bar(x=o["etapa_obra"],y=o["desvio_pct"],marker_color=cd,
                               text=[f"{d:+.1f}%" for d in o["desvio_pct"]],
                               textposition="outside",textfont=dict(size=11,color=C_MUTED)))
        fig2.add_hline(y=0,line_color=C_MUTED,line_width=1)
        fig2.add_hline(y=8,line_dash="dash",line_color=C_VERM,line_width=1,
                       annotation_text="Limite crítico +8%",annotation_font_size=10,annotation_font_color=C_VERM)
        fig2.update_layout(**L(h=285),xaxis=AX(grid=False),yaxis=AX(title="Desvio (%)"))
        st.plotly_chart(fig2, use_container_width=True)
        dt=crea-corc
        ins(f"Desvio total: <strong>{fM(abs(dt))}</strong> {'acima' if dt>0 else 'abaixo'} do orçamento. "
            f"{'Impacto direto na margem bruta.' if dt>0 else 'Execução preservando a margem projetada.'}", "bad" if dt>0 else "ok")

    st.markdown("---")
    hdr("Curva S — Avanço Físico Realizado vs Cronograma Planejado",
        "A Curva S mostra a evolução do progresso físico da obra. Quando a curva real fica abaixo "
        "da planejada há atraso — com risco de impacto no reconhecimento de receita (POC) do trimestre.")
    meses=list(range(1,43))
    plan=[min(100,(m/36)**1.15*100) for m in meses]
    # Estimar mês atual na linha do tempo de 36 meses; para obras entregues (av=100) usa mês 36
    mes_atual=int(av/100*36) if av<100 else 36
    # Curva realizada cresce naturalmente até o mês atual — sem cap artificial em av%
    real=[min(100,p*(1+0.04*(1 if m<18 else -0.3))+(m*0.25)) if m<=mes_atual else None
          for m,p in zip(meses,plan)]
    fig3=go.Figure()
    fig3.add_trace(go.Scatter(x=meses,y=plan,name="Cronograma Planejado",
                               line=dict(color=C_BORDER,width=2,dash="dash")))
    fig3.add_trace(go.Scatter(x=meses,y=real,name="Avanço Realizado",
                               line=dict(color=C_GOLD,width=2.5),
                               fill="tonexty",fillcolor="rgba(201,168,76,0.12)"))
    fig3.add_vline(x=av/100*36,line_dash="dot",line_color=C_GOLD_L,line_width=2,
                   annotation_text=f"Hoje: {av:.0f}%",annotation_font_color=C_GOLD_L,annotation_font_size=11)
    fig3.update_layout(**L(h=295),xaxis=AX(title="Mês de obra"),yaxis=AX(title="Avanço Físico (%)",rng=[0,110]))
    st.plotly_chart(fig3, use_container_width=True)
    atraso=plan[min(int(av/100*36),len(plan)-1)]-av if av<100 else 0
    ins(f"{'Atraso de '+str(round(atraso,1))+'pp — risco de impacto no reconhecimento POC do próximo trimestre.' if atraso>5 else 'Avanço de '+str(round(av,0))+'% alinhado ao cronograma. Receita POC de '+fM(rpoc)+' reflete o estágio atual.'}", "bad" if atraso>5 else "ok")

    st.markdown("---")
    hdr("Percentual de Conclusão (POC) — Portfólio Completo",
        "Comparativo do avanço físico de todas as obras. Cor indica fase: vermelho=inicial, dourado=intermediária, verde=avançada.")
    poc=obra_f.groupby("nome_empreendimento").first().reset_index()[["nome_empreendimento","avanco_fisico_pct","receita_reconhecida_poc"]]
    poc=poc.sort_values("avanco_fisico_pct",ascending=True)
    cp=[C_VERM if v<30 else (C_GOLD if v<70 else C_VERDE) for v in poc["avanco_fisico_pct"]]
    fig4=go.Figure(go.Bar(
        x=poc["avanco_fisico_pct"],y=poc["nome_empreendimento"],orientation="h",
        marker_color=cp,text=[f"{v:.0f}%" for v in poc["avanco_fisico_pct"]],
        textposition="outside",textfont=dict(size=10,color=C_MUTED),
        customdata=poc["receita_reconhecida_poc"].apply(fM),
        hovertemplate="<b>%{y}</b><br>POC: %{x:.0f}%<br>Receita: %{customdata}<extra></extra>",
    ))
    fig4.add_vline(x=50,line_dash="dash",line_color=C_MUTED,line_width=1,
                   annotation_text="50%",annotation_font_size=10)
    fig4.update_layout(**L(h=400), xaxis=AX(rng=[0,115]), yaxis=AXH())
    st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════
#  DRE GERENCIAL
# ══════════════════════════════════════════════════════════════
elif "DRE" in pg:
    st.markdown("## DRE Gerencial — Demonstrativo de Resultado Econômico")
    st.caption("Resultado pelo método POC · Receita reconhecida proporcional ao avanço físico · Não representa fluxo de caixa")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Receita Total Reconhecida (POC)", fM(dre_f["receita_reconhecida_poc"].sum()))
    c2.metric("Custo Total de Obra (POC)",        fM(dre_f["custo_obra_poc"].sum()))
    c3.metric("Margem Bruta Média",               f"{dre_f['margem_bruta_pct'].mean():.1f}%")
    c4.metric("EBITDA Acumulado",                 fM(dre_f[dre_f["ebitda"]>0]["ebitda"].sum()))

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        hdr("Margem Bruta por Empreendimento (%)",
            "% da receita que sobra após subtrair custos diretos de obra. Principal indicador de rentabilidade. "
            "Vermelho <25%: crítico. Dourado 25-33%: adequado. Verde >33%: excelente para mercado SP.")
        dm=dre_f.sort_values("margem_bruta_pct")
        cm=[C_VERM if v<25 else (C_GOLD if v<33 else C_VERDE) for v in dm["margem_bruta_pct"]]
        fig=go.Figure(go.Bar(x=dm["margem_bruta_pct"],y=dm["nome"],orientation="h",
                             marker_color=cm,text=[f"{v:.1f}%" for v in dm["margem_bruta_pct"]],
                             textposition="outside",textfont=dict(size=10,color=C_MUTED)))
        fig.add_vline(x=30,line_dash="dash",line_color=C_MUTED,line_width=1,
                      annotation_text="Benchmark SP: 30%",annotation_font_size=9)
        fig.update_layout(**L(h=460), xaxis=AX(rng=[0,55]), yaxis=AXH())
        st.plotly_chart(fig, use_container_width=True)
        m=dre_f.loc[dre_f["margem_bruta_pct"].idxmax()]; p=dre_f.loc[dre_f["margem_bruta_pct"].idxmin()]
        ins(f"<strong>{m['nome']}</strong>: melhor margem com <strong>{m['margem_bruta_pct']:.1f}%</strong>. "
            f"<strong>{p['nome']}</strong> ({p['margem_bruta_pct']:.1f}%) — revisar custos de obra.", "info")

    with col2:
        hdr("Waterfall do DRE — Decomposição do Resultado Consolidado",
            "Parte da Receita Reconhecida (POC), subtrai Custo de Obra, Despesas Comerciais e Administrativas, "
            "chegando ao EBITDA. Permite identificar onde estão as principais perdas de margem.")
        receita=dre_f["receita_reconhecida_poc"].sum(); custo=dre_f["custo_obra_poc"].sum()
        desp_c=dre_f["despesas_comerciais"].sum(); desp_a=dre_f["despesas_administrativas"].sum()
        ebitda=receita-custo-desp_c-desp_a
        fig2=go.Figure(go.Waterfall(
            orientation="v",measure=["absolute","relative","relative","relative","total"],
            x=["Receita\nPOC","Custo\nde Obra","Despesas\nComerciais","Despesas\nAdm.","EBITDA"],
            y=[receita,-custo,-desp_c,-desp_a,0],
            text=[fM(v) for v in [receita,custo,desp_c,desp_a,ebitda]],
            textposition="outside",textfont=dict(size=10,color=C_TEXT),
            connector={"line":{"color":C_BORDER}},
            increasing={"marker":{"color":C_VERDE}},
            decreasing={"marker":{"color":C_VERM}},
            totals={"marker":{"color":C_GOLD}},
        ))
        fig2.update_layout(plot_bgcolor=C_PLOT,paper_bgcolor=C_PLOT,
                           font=dict(family="Inter,sans-serif",color=C_TEXT,size=11),
                           height=285,showlegend=False,margin=dict(l=12,r=20,t=10,b=10),
                           xaxis=AX(grid=False),yaxis=AX(fmt=",.0f"))
        st.plotly_chart(fig2, use_container_width=True)
        ep=ebitda/receita*100 if receita>0 else 0
        ins(f"EBITDA de <strong>{fM(ebitda)}</strong> — margem EBITDA de <strong>{ep:.1f}%</strong>. "
            f"{'Acima da referência de 12-15% do setor SP.' if ep>15 else 'Abaixo de 15% — avaliar despesas administrativas e comerciais.'}", "ok" if ep>15 else "bad" if ep<8 else "warn")

        hdr("Margem Bruta Média por Linha de Produto",
            "Comparativo de rentabilidade entre Premium, Alto Padrão e Smart. "
            "Premium tende a ter maior margem absoluta; Smart compensa com volume.")
        ml=dre_f.groupby("linha")["margem_bruta_pct"].mean().reset_index()
        fig3=go.Figure(go.Bar(x=ml["linha"],y=ml["margem_bruta_pct"],
                               marker_color=[LINHA_CORES.get(l,C_MUTED) for l in ml["linha"]],
                               text=[f"{v:.1f}%" for v in ml["margem_bruta_pct"]],
                               textposition="outside",textfont=dict(size=11,color=C_MUTED)))
        fig3.add_hline(y=30,line_dash="dash",line_color=C_MUTED,line_width=1)
        fig3.update_layout(**L(h=210),xaxis=AX(grid=False),yaxis=AX(rng=[0,50]))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    hdr("Análise Bidimensional: Margem Bruta × Velocidade de Vendas Acumulada",
        "Cada bolha é um empreendimento; o tamanho é proporcional ao VGV lançado. "
        "Quadrante ideal (direita-cima): alto VSO + alta margem. "
        "Bolhas no canto inferior-esquerdo requerem atenção simultânea comercial e de custos.")
    fig4=go.Figure()
    for sl,cor in STATUS_CORES.items():
        sub=dre_f[dre_f["status_label"]==sl]
        if len(sub):
            fig4.add_trace(go.Scatter(
                x=sub["vso_acumulado_pct"],y=sub["margem_bruta_pct"],
                mode="markers+text",name=sl,
                marker=dict(color=cor,opacity=0.85,size=sub["vgv_lancado"]/4_000_000+8,
                            line=dict(color=C_BORDER,width=1.5)),
                text=sub["nome"],textposition="top center",
                textfont=dict(size=9,color=C_MUTED),
                hovertemplate="<b>%{text}</b><br>VSO: %{x:.1f}%<br>Margem: %{y:.1f}%<extra></extra>",
            ))
    fig4.add_hline(y=30,line_dash="dash",line_color=C_MUTED,line_width=1,
                   annotation_text="Margem benchmark: 30%",annotation_font_size=9)
    fig4.add_vline(x=80,line_dash="dash",line_color=C_MUTED,line_width=1,
                   annotation_text="VSO meta: 80%",annotation_font_size=9)
    fig4.update_layout(**L(h=430),
                       xaxis=AX(title="Velocidade de Vendas Acumulada (%)",rng=[0,105]),
                       yaxis=AX(title="Margem Bruta (%)",rng=[0,55]))
    st.plotly_chart(fig4, use_container_width=True)
    qi=len(dre_f[(dre_f["vso_acumulado_pct"]>=80)&(dre_f["margem_bruta_pct"]>=30)])
    ins(f"<strong>{qi} de {len(dre_f)} empreendimentos</strong> estão no quadrante ideal (VSO ≥ 80% e Margem ≥ 30%).", "ok" if qi>=len(dre_f)//2 else "warn")


# ══════════════════════════════════════════════════════════════
#  FLUXO DE CAIXA
# ══════════════════════════════════════════════════════════════
elif "Fluxo" in pg:
    st.markdown("## Fluxo de Caixa")
    st.caption("Entradas e saídas mensais de caixa · Saldo acumulado projetado · Necessidade de capital por empreendimento · Diferente do DRE — representa movimentação real de dinheiro")

    sel = st.selectbox("Empreendimento", ["Portfólio Consolidado"]+dre_f["nome"].tolist())
    if sel!="Portfólio Consolidado":
        id_s=dre_f[dre_f["nome"]==sel]["id_empreendimento"].values[0]
        fp=fc_f[fc_f["id_empreendimento"]==id_s].copy()
    else:
        fp=fc_f.groupby("data").agg(
            entradas_vendas=("entradas_vendas","sum"),
            entradas_financiamento=("entradas_financiamento","sum"),
            saidas_obra=("saidas_obra","sum"),
            saidas_despesas=("saidas_despesas","sum"),
            entradas_total=("entradas_total","sum"),
            saidas_total=("saidas_total","sum"),
            saldo_mes=("saldo_mes","sum"),
        ).reset_index()

    fp_s=fp.sort_values("data")
    fp_s["saldo_acum"]=fp_s["saldo_mes"].cumsum()

    total_ent=fp_s["entradas_total"].sum(); total_sai=fp_s["saidas_total"].sum()
    saldo_tot=fp_s["saldo_acum"].iloc[-1] if len(fp_s) else 0
    meses_neg=len(fp_s[fp_s["saldo_mes"]<0])

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total de Entradas de Caixa",   fM(total_ent))
    c2.metric("Total de Saídas de Caixa",     fM(total_sai))
    c3.metric("Saldo de Caixa Acumulado",     fM(saldo_tot),
              delta_color="normal" if saldo_tot>=0 else "inverse")
    c4.metric("Meses com Saldo Negativo",     f"{meses_neg}",
              delta="risco de capital" if meses_neg>0 else "sem necessidade",
              delta_color="inverse" if meses_neg>0 else "normal")

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        hdr("Entradas vs Saídas de Caixa — Mensal",
            "Comparativo mensal entre recebimentos (parcelas de compradores + financiamento bancário) "
            "e desembolsos (custo de obra + despesas). Meses com saídas > entradas indicam necessidade de capital.")
        fig=go.Figure()
        fig.add_trace(go.Bar(x=fp_s["data"],y=fp_s["entradas_total"],name="Entradas",marker_color=C_VERDE,opacity=0.85))
        fig.add_trace(go.Bar(x=fp_s["data"],y=-fp_s["saidas_total"],name="Saídas",marker_color=C_VERM,opacity=0.85))
        fig.update_layout(**L(h=280),barmode="relative",xaxis=AX(),yaxis=AX(fmt=",.0f"))
        st.plotly_chart(fig, use_container_width=True)
        ins(f"Total de entradas: <strong>{fM(total_ent)}</strong> | Total de saídas: <strong>{fM(total_sai)}</strong>. "
            f"{'Saldo positivo — operação auto-sustentável.' if saldo_tot>=0 else 'Saldo negativo — avaliar necessidade de aporte ou financiamento.'}",
            "ok" if saldo_tot>=0 else "bad")

    with col2:
        hdr("Saldo de Caixa Acumulado",
            "Posição de caixa acumulada ao longo do ciclo do empreendimento. "
            "Períodos abaixo de zero indicam necessidade de capital de giro ou financiamento bancário.")
        cores_sal=[C_VERDE if v>=0 else C_VERM for v in fp_s["saldo_acum"]]
        fig2=go.Figure()
        fig2.add_trace(go.Scatter(x=fp_s["data"],y=fp_s["saldo_acum"],
                                   mode="lines",name="Saldo Acumulado",
                                   line=dict(color=C_GOLD,width=2.5),
                                   fill="tozeroy",fillcolor="rgba(201,168,76,0.10)"))
        fig2.add_hline(y=0,line_color=C_VERM,line_width=1.5,line_dash="dash",
                       annotation_text="Linha de necessidade de capital",annotation_font_size=9)
        fig2.update_layout(**L(h=280),xaxis=AX(),yaxis=AX(fmt=",.0f"))
        st.plotly_chart(fig2, use_container_width=True)
        if meses_neg>0:
            ins(f"<strong>{meses_neg} meses</strong> com saldo negativo — revisar cronograma de recebimentos ou acionar financiamento bancário (SFH/SFI).", "bad")
        else:
            ins("Saldo acumulado positivo em todos os meses — empreendimento auto-financiado pelo fluxo de vendas.", "ok")

    st.markdown("---")
    col3,col4 = st.columns(2)
    with col3:
        hdr("Composição das Entradas de Caixa",
            "Parcelas de compradores vs financiamento bancário. A dependência elevada de financiamento "
            "bancário aumenta o custo financeiro e o risco operacional do projeto.")
        fig3=go.Figure()
        fig3.add_trace(go.Bar(x=fp_s["data"],y=fp_s["entradas_vendas"],name="Recebimentos de Compradores",marker_color=C_GOLD))
        fig3.add_trace(go.Bar(x=fp_s["data"],y=fp_s["entradas_financiamento"],name="Financiamento Bancário",marker_color=C_AZUL))
        fig3.update_layout(**L(h=265),barmode="stack",xaxis=AX(),yaxis=AX(fmt=",.0f"))
        st.plotly_chart(fig3, use_container_width=True)
        pct_fin=fp_s["entradas_financiamento"].sum()/total_ent*100 if total_ent>0 else 0
        ins(f"Financiamento bancário representa <strong>{pct_fin:.1f}%</strong> das entradas totais. "
            f"{'Dependência elevada — monitorar custo financeiro.' if pct_fin>40 else 'Proporção saudável — majoritariamente financiado por vendas.'}", "warn" if pct_fin>40 else "ok")

    with col4:
        hdr("Necessidade de Capital por Empreendimento",
            "Saldo de caixa acumulado mínimo de cada projeto — indica o pico de exposição financeira "
            "que a incorporadora precisou aportar ou financiar para viabilizar a obra.")
        fc_emp=(
            fc_f.sort_values("data")
            .groupby(["id_empreendimento","nome"])["saldo_mes"]
            .apply(lambda x: x.cumsum().min())
            .reset_index(name="exposicao_maxima")
        )
        fc_emp=fc_emp.sort_values("exposicao_maxima",ascending=True)
        cores_exp=[C_VERM if v<0 else C_VERDE for v in fc_emp["exposicao_maxima"]]
        fig4=go.Figure(go.Bar(
            x=fc_emp["exposicao_maxima"],y=fc_emp["nome"],orientation="h",
            marker_color=cores_exp,
            text=fc_emp["exposicao_maxima"].apply(fM),
            textposition="outside",textfont=dict(size=10,color=C_MUTED),
        ))
        fig4.add_vline(x=0,line_color=C_MUTED,line_width=1)
        fig4.update_layout(**L(h=265), xaxis=AX(fmt=",.0f"), yaxis=AXH())
        st.plotly_chart(fig4, use_container_width=True)
        maior_exp=fc_emp.loc[fc_emp["exposicao_maxima"].idxmin()]
        ins(f"Maior exposição de capital: <strong>{maior_exp['nome']}</strong> com necessidade mínima de {fM(abs(maior_exp['exposicao_maxima']))}. "
            f"Monitorar prazo de recebimento das parcelas dos compradores.", "warn")


# ══════════════════════════════════════════════════════════════
#  FP&A & PROJEÇÕES
# ══════════════════════════════════════════════════════════════
elif "FP&A" in pg:
    st.markdown("## FP&A — Planejamento Financeiro, Análise & Projeções")
    st.caption("Budget vs Realizado · Variação orçamentária · Forecast 12 meses · Análise comparativa entre empreendimentos")

    # Budget vs Realizado consolidado
    st.markdown("---")
    hdr("Budget vs Realizado — Visão Consolidada por Categoria",
        "Comparativo entre o resultado orçado no lançamento e o resultado efetivamente realizado até o momento. "
        "Variação positiva na receita é favorável; variação positiva em custos é desfavorável.")

    bud_cons=bud_f.groupby("categoria").agg(
        orcado=("orcado","sum"), realizado=("realizado","sum")).reset_index()
    bud_cons["variacao_pct"]=(bud_cons["realizado"]-bud_cons["orcado"])/bud_cons["orcado"].abs()*100

    col1,col2 = st.columns(2)
    with col1:
        fig=go.Figure()
        ordem=["Receita (POC)","Custo de Obra","Despesas Comerciais","Despesas Adm.","EBITDA"]
        bud_o=bud_cons.set_index("categoria").reindex(ordem).reset_index()
        fig.add_trace(go.Bar(x=bud_o["categoria"],y=bud_o["orcado"],name="Orçado",
                             marker_color=C_BORDER,marker_line=dict(color=C_MUTED,width=1)))
        fig.add_trace(go.Bar(x=bud_o["categoria"],y=bud_o["realizado"],name="Realizado",
                             marker_color=C_GOLD,marker_line=dict(color=C_GOLD_L,width=0.5)))
        fig.update_layout(**L(h=280),barmode="group",xaxis=AX(grid=False),yaxis=AX(fmt=",.0f"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        hdr("Variação Orçamentária por Categoria (%)",
            "Percentual de desvio entre realizado e orçado. Verde: favorável. Vermelho: desfavorável. "
            "A variação do EBITDA resume o impacto líquido de todos os desvios.")
        cores_var=[]
        for i,row in bud_o.iterrows():
            fav = (row["categoria"]=="Receita (POC)" and row["variacao_pct"]>0) or \
                  (row["categoria"] not in ["Receita (POC)","EBITDA"] and row["variacao_pct"]<0) or \
                  (row["categoria"]=="EBITDA" and row["variacao_pct"]>0)
            cores_var.append(C_VERDE if fav else C_VERM)
        fig3=go.Figure(go.Bar(
            x=bud_o["categoria"],y=bud_o["variacao_pct"],
            marker_color=cores_var,
            text=[f"{v:+.1f}%" for v in bud_o["variacao_pct"]],
            textposition="outside",textfont=dict(size=11,color=C_MUTED),
        ))
        fig3.add_hline(y=0,line_color=C_MUTED,line_width=1)
        fig3.update_layout(**L(h=280),xaxis=AX(grid=False),yaxis=AX(title="Variação (%)"))
        st.plotly_chart(fig3, use_container_width=True)

    # Variação por empreendimento
    st.markdown("---")
    hdr("Variação de EBITDA: Budget vs Realizado — por Empreendimento",
        "Quais empreendimentos estão performando acima ou abaixo do orçamento. "
        "Empreendimentos em fase inicial de obra (<10% POC) são excluídos: o EBITDA é estruturalmente "
        "negativo nessa fase (despesas já correm, receita POC ainda mínima) — comparação orçamentária não é válida.")

    bud_emp_all = bud_f[bud_f["categoria"]=="EBITDA"].copy()

    # Derivar fase_inicial do status se coluna não existir no CSV
    if "fase_inicial" not in bud_emp_all.columns:
        bud_emp_all["fase_inicial"] = bud_emp_all["status"] == "lancamento"

    # Garantir que variacao_pct existe; recalcular para lançamentos se necessário
    if "variacao_pct" not in bud_emp_all.columns:
        bud_emp_all["variacao_pct"] = None

    # Separar comparáveis (excluir fase inicial e variações inválidas)
    bud_comp = bud_emp_all[
        (bud_emp_all["fase_inicial"] == False) &
        (bud_emp_all["variacao_pct"].notna())
    ].copy()
    bud_fase = bud_emp_all[bud_emp_all["fase_inicial"] == True]
    bud_comp = bud_comp.sort_values("variacao_pct", ascending=True)

    cv = [C_VERDE if v>=0 else C_VERM for v in bud_comp["variacao_pct"]]
    fig5 = go.Figure(go.Bar(
        x=bud_comp["variacao_pct"], y=bud_comp["nome"], orientation="h",
        marker_color=cv,
        text=[f"{v:+.1f}%" for v in bud_comp["variacao_pct"]],
        textposition="outside", textfont=dict(size=10, color=C_MUTED),
        hovertemplate="<b>%{y}</b><br>Variação EBITDA: %{x:+.1f}%<br>Orçado: %{customdata[0]}<br>Realizado: %{customdata[1]}<extra></extra>",
        customdata=list(zip(bud_comp["orcado"].apply(fM), bud_comp["realizado"].apply(fM))),
    ))
    fig5.add_vline(x=0, line_color=C_MUTED, line_width=1)
    fig5.add_vline(x=-20, line_dash="dash", line_color=C_VERM, line_width=1,
                   annotation_text="Alerta: -20%", annotation_font_size=9, annotation_font_color=C_VERM)
    fig5.add_vline(x=20, line_dash="dash", line_color=C_VERDE, line_width=1,
                   annotation_text="Destaque: +20%", annotation_font_size=9, annotation_font_color=C_VERDE)
    fig5.update_layout(**L(h=max(300, len(bud_comp)*28)),
                       xaxis=AX(title="Variação EBITDA vs Orçado (%)", rng=[-65, 65]),
                       yaxis=AXH())
    st.plotly_chart(fig5, use_container_width=True)

    if len(bud_fase) > 0:
        nomes_fase = ", ".join(bud_fase["nome"].tolist())
        ins(f"<strong>{len(bud_fase)} empreendimentos excluídos da comparação orçamentária</strong> por estarem em fase inicial de obra (POC < 10%): {nomes_fase}. "
            f"Nessa fase, o EBITDA negativo é estrutural — despesas comerciais e administrativas já correm enquanto a receita POC ainda é mínima. "
            f"A comparação orçamentária passa a ser válida a partir de ~15% de avanço físico.", "info")

    if len(bud_comp) > 0:
        melhor_bud = bud_comp.iloc[-1]
        pior_bud   = bud_comp.iloc[0]
        n_acima = len(bud_comp[bud_comp["variacao_pct"] >= 0])
        n_abaixo= len(bud_comp[bud_comp["variacao_pct"] < 0])
        ins(f"<strong>{n_acima} empreendimentos</strong> acima do orçamento. Destaque: <strong>{melhor_bud['nome']}</strong> com EBITDA <strong>{melhor_bud['variacao_pct']:+.1f}%</strong> acima do planejado.", "ok")
        if n_abaixo > 0:
            ins(f"<strong>{n_abaixo} empreendimentos</strong> abaixo do orçamento. Maior desvio: <strong>{pior_bud['nome']}</strong> com <strong>{pior_bud['variacao_pct']:+.1f}%</strong> vs orçado — revisar estrutura de custos de obra e despesas.", "bad")

    # Projeção 12 meses
    st.markdown("---")
    hdr("Projeção de Receita Reconhecida (POC) — Próximos 12 Meses",
        "Forecast da receita a ser reconhecida nos próximos 12 meses com base no avanço físico projetado "
        "e no VGV vendido atual. Permite antecipar o resultado econômico futuro e planejar o fluxo financeiro.")
    proj_cons=proj_f.groupby("data").agg(
        receita_projetada=("receita_projetada","sum"),
        ebitda_projetado=("ebitda_projetado","sum"),
    ).reset_index()

    col_p1,col_p2 = st.columns(2)
    with col_p1:
        fig6=go.Figure()
        fig6.add_trace(go.Bar(x=proj_cons["data"],y=proj_cons["receita_projetada"],
                               name="Receita Projetada",marker_color=C_GOLD,opacity=0.85))
        fig6.update_layout(**L(h=270),xaxis=AX(),yaxis=AX(fmt=",.0f",title="Receita (R$)"))
        st.plotly_chart(fig6, use_container_width=True)
        total_proj=proj_cons["receita_projetada"].sum()
        ins(f"Receita projetada para os próximos 12 meses: <strong>{fM(total_proj)}</strong>. "
            f"Baseada no ritmo atual de avanço físico e VSO acumulado de cada empreendimento.", "info")

    with col_p2:
        hdr("Projeção de EBITDA — Próximos 12 Meses",
            "Resultado operacional projetado. Meses com EBITDA negativo indicam fase inicial "
            "de obras com baixo POC acumulado — esperado para empreendimentos em lançamento.")
        cores_ebitda=[C_VERDE if v>=0 else C_VERM for v in proj_cons["ebitda_projetado"]]
        fig7=go.Figure(go.Bar(
            x=proj_cons["data"],y=proj_cons["ebitda_projetado"],
            marker_color=cores_ebitda,
            hovertemplate="%{x|%b/%Y}: %{customdata}<extra></extra>",
            customdata=proj_cons["ebitda_projetado"].apply(fM),
        ))
        fig7.add_hline(y=0,line_color=C_MUTED,line_width=1)
        fig7.update_layout(**L(h=270),xaxis=AX(),yaxis=AX(fmt=",.0f",title="EBITDA (R$)"))
        st.plotly_chart(fig7, use_container_width=True)
        meses_pos=len(proj_cons[proj_cons["ebitda_projetado"]>0])
        ins(f"<strong>{meses_pos} de 12 meses</strong> com EBITDA positivo projetado. "
            f"{'Trajetória favorável de resultado nos próximos trimestres.' if meses_pos>=8 else 'Maioria dos meses com EBITDA negativo — obras em fase inicial. Resultado se intensifica conforme POC avança.'}", "ok" if meses_pos>=8 else "warn")

    # Análise comparativa de margens
    st.markdown("---")
    hdr("Análise Comparativa de Margens por Empreendimento",
        "Visão lado a lado das principais margens de cada projeto: bruta, EBITDA e percentual de conclusão (POC). "
        "Permite identificar quais empreendimentos entregam mais resultado por fase de obra.")
    comp=dre_f[["nome","margem_bruta_pct","ebitda_pct","avanco_obra_pct"]].sort_values("margem_bruta_pct",ascending=False)
    fig8=go.Figure()
    fig8.add_trace(go.Bar(name="Margem Bruta (%)",x=comp["nome"],y=comp["margem_bruta_pct"],
                           marker_color=C_GOLD,text=[f"{v:.1f}%" for v in comp["margem_bruta_pct"]],
                           textposition="outside",textfont=dict(size=9,color=C_MUTED)))
    fig8.add_trace(go.Bar(name="EBITDA (%)",x=comp["nome"],y=comp["ebitda_pct"],
                           marker_color=C_AZUL,text=[f"{v:.1f}%" for v in comp["ebitda_pct"]],
                           textposition="outside",textfont=dict(size=9,color=C_MUTED)))
    fig8.add_trace(go.Scatter(name="POC (%)",x=comp["nome"],y=comp["avanco_obra_pct"],
                               mode="lines+markers",yaxis="y2",
                               line=dict(color=C_VERDE,width=2),marker=dict(size=6,color=C_VERDE)))
    fig8.update_layout(**L(h=360),barmode="group",
                       xaxis=AX(grid=False,ang=-30),
                       yaxis=AX(title="Margem (%)",rng=[-30,60]),
                       yaxis2=dict(title=dict(text="POC (%)",font=dict(size=10,color=C_VERDE)),
                                   overlaying="y",side="right",range=[0,120],
                                   showgrid=False,zeroline=False,
                                   tickfont=dict(size=10,color=C_VERDE)))
    st.plotly_chart(fig8, use_container_width=True)
    ins("A linha verde (POC) sobreposta às barras permite avaliar se a margem está sendo entregue de forma consistente com o avanço da obra — desvios entre POC alto e margem baixa indicam estouro de custo.", "info")


# ══════════════════════════════════════════════════════════════
#  COHORT DE LANÇAMENTOS
# ══════════════════════════════════════════════════════════════
elif "Cohort" in pg:
    st.markdown("## Análise de Cohort — Velocidade de Absorção por Safra")
    st.caption("Compara empreendimentos lançados no mesmo ano · Identifica tendências de absorção de mercado · Benchmark entre gerações")

    # Preparar dados de cohort: merge vendas com data de lançamento
    cohort = vend_f.merge(
        emp_f[["id","lancamento"]].rename(columns={"id":"id_empreendimento"}),
        on="id_empreendimento", how="left"
    )
    cohort["meses"] = (
        (cohort["data"].dt.year  - cohort["lancamento"].dt.year ) * 12 +
        (cohort["data"].dt.month - cohort["lancamento"].dt.month)
    ).clip(lower=0)
    cohort["safra"] = cohort["lancamento"].dt.year.astype(str)

    if len(cohort) == 0:
        st.warning("Sem dados suficientes para análise de cohort com os filtros selecionados.")
        st.stop()

    safras = sorted(cohort["safra"].unique())
    SAFRA_CORES = [C_GOLD, C_AZUL, C_VERDE, C_VERM, C_MUTED, C_GOLD_L, C_NAVY3]

    # KPIs por safra
    cols_ks = st.columns(min(len(safras), 4))
    for i, safra in enumerate(safras[:4]):
        sub = cohort[cohort["safra"]==safra]
        vso_rec = sub.sort_values("data").tail(3)["vso_pct"].mean()
        n = sub["nome"].nunique()
        cols_ks[i].metric(
            f"Safra {safra}",
            f"{n} empreend.",
            delta=f"VSO rec: {vso_rec:.1f}%",
            delta_color="normal" if vso_rec>=10 else "inverse"
        )

    st.markdown("---")

    # Agregar VSO médio por safra × meses desde lançamento
    cg = cohort.groupby(["safra","meses"]).agg(
        vso_medio=("vso_pct","mean"),
        unidades=("unidades_vendidas","sum"),
    ).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        hdr("Velocidade de Absorção (VSO) por Meses desde o Lançamento",
            "Cada linha é uma safra (ano de lançamento). Curvas mais altas indicam maior demanda "
            "de mercado. Média móvel de 3 meses para suavizar sazonalidade.")
        fig = go.Figure()
        for i, safra in enumerate(safras):
            sub = cg[cg["safra"]==safra].sort_values("meses")
            sub = sub.copy()
            sub["vso_suav"] = sub["vso_medio"].rolling(3, min_periods=1).mean()
            cor = SAFRA_CORES[i % len(SAFRA_CORES)]
            fig.add_trace(go.Scatter(
                x=sub["meses"], y=sub["vso_suav"],
                mode="lines", name=f"Safra {safra}",
                line=dict(color=cor, width=2),
                hovertemplate=f"Safra {safra} · Mês %{{x}}: %{{y:.1f}}%<extra></extra>",
            ))
        fig.add_hline(y=10, line_dash="dash", line_color=C_MUTED, line_width=1,
                      annotation_text="Mínimo saudável: 10%", annotation_font_size=9)
        fig.update_layout(**L(h=310),
                          xaxis=AX(title="Meses desde o lançamento"),
                          yaxis=AX(title="VSO médio (%)"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        hdr("Heatmap de Absorção — Safra × Meses desde o Lançamento",
            "Intensidade da cor indica VSO. Colunas à esquerda = início do ciclo. "
            "Permite comparar velocidade entre gerações de lançamentos no mesmo estágio do ciclo.")
        pivot = cg.pivot(index="safra", columns="meses", values="vso_medio")
        cols_36 = [c for c in pivot.columns if c <= 36]
        pivot = pivot[cols_36]
        fig2 = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[f"M{int(c)}" for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[[0,C_VERM],[0.3,C_GOLD],[1,C_VERDE]],
            text=[[f"{v:.1f}%" if not pd.isna(v) else "—" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            textfont=dict(size=9, color=C_TEXT),
            hovertemplate="Safra %{y}<br>%{x}: %{text}<extra></extra>",
            colorbar=dict(
                tickfont=dict(color=C_MUTED, size=10),
                title=dict(text="VSO%", font=dict(color=C_MUTED, size=10)),
                bgcolor=C_CARD, bordercolor=C_BORDER,
            ),
        ))
        fig2.update_layout(**L(h=310), xaxis=AX(grid=False, ang=-45), yaxis=AX(grid=False))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Unidades acumuladas por safra
    hdr("Volume de Vendas Acumulado por Safra",
        "Unidades acumuladas vendidas por meses desde o lançamento. "
        "Inclinação mais íngreme = maior velocidade de absorção inicial.")
    cumul = cohort.sort_values(["safra","meses"]).copy()
    cumul_agg = cumul.groupby(["safra","meses"])["unidades_vendidas"].sum().reset_index()
    cumul_agg["acum"] = cumul_agg.groupby("safra")["unidades_vendidas"].cumsum()

    fig3 = go.Figure()
    for i, safra in enumerate(safras):
        sub = cumul_agg[cumul_agg["safra"]==safra].sort_values("meses")
        cor = SAFRA_CORES[i % len(SAFRA_CORES)]
        fig3.add_trace(go.Scatter(
            x=sub["meses"], y=sub["acum"],
            mode="lines+markers", name=f"Safra {safra}",
            line=dict(color=cor, width=2),
            marker=dict(size=4, color=cor),
            hovertemplate=f"Safra {safra} · Mês %{{x}}: %{{y:.0f}} un.<extra></extra>",
        ))
    fig3.update_layout(**L(h=280),
                       xaxis=AX(title="Meses desde o lançamento"),
                       yaxis=AX(title="Unidades acumuladas"))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # VGV por safra (barras agrupadas por linha de produto)
    hdr("VGV Total por Safra e Linha de Produto",
        "Volume financeiro lançado por geração. Permite identificar quais safras concentraram "
        "mais investimento e se houve mudança de mix de produto ao longo do tempo.")
    vgv_safra = emp_f.copy()
    vgv_safra["safra"] = vgv_safra["lancamento"].dt.year.astype(str)
    vgv_sg = vgv_safra.groupby(["safra","linha"])["vgv_total"].sum().reset_index()
    fig4 = px.bar(vgv_sg, x="safra", y="vgv_total", color="linha",
                  color_discrete_map=LINHA_CORES, barmode="group",
                  labels={"safra":"Safra","vgv_total":"VGV (R$)","linha":"Linha"})
    fig4.update_layout(**L(h=260), xaxis=AX(grid=False), yaxis=AX(fmt=",.0f"))
    st.plotly_chart(fig4, use_container_width=True)

    # Insights
    best_safra = cg.groupby("safra")["vso_medio"].mean().idxmax()
    worst_safra= cg.groupby("safra")["vso_medio"].mean().idxmin()
    i1, i2 = st.columns(2)
    with i1:
        ins(f"Safra com maior VSO médio: <strong>{best_safra}</strong>. "
            f"Empreendimentos lançados nesse ano tiveram a melhor velocidade de absorção do portfólio.", "ok")
    with i2:
        ins(f"Safra <strong>{worst_safra}</strong> apresentou menor velocidade de absorção. "
            f"Analisar contexto macroeconômico e perfil de produto para orientar decisões de novos lançamentos.", "warn")
