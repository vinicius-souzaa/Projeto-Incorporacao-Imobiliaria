"""
Geração de dados sintéticos realistas — Portfólio Imobiliário SP
Calibrado com benchmarks Secovi-SP / ABRAINC-FIPE 2018-2026.

Executar: python generate_data.py
"""
import numpy as np
import pandas as pd
from pathlib import Path
from dateutil.relativedelta import relativedelta

np.random.seed(42)
DATA_DIR = Path("data")

# ── Parâmetros por segmento ────────────────────────────────────────────────
# Fonte: Secovi-SP, ABRAINC, pesquisa de mercado SP 2018-2026
SEG = {
    "Premium": {
        "margem_bruta":     (0.34, 0.42),   # % sobre receita
        "desp_comercial":   (0.050, 0.065),  # % sobre VGV vendido (comissão + mktg)
        "desp_admin":       (0.018, 0.026),  # % sobre VGV total × POC
        "vso_burst":        (0.18, 0.28),    # VSO mês de lançamento
        "vso_decay":        0.88,            # fator de decaimento mensal
        "dist_rate":        (0.02, 0.04),    # taxa de distrato acumulada
    },
    "Alto Padrão": {
        "margem_bruta":     (0.29, 0.37),
        "desp_comercial":   (0.055, 0.070),
        "desp_admin":       (0.020, 0.028),
        "vso_burst":        (0.15, 0.24),
        "vso_decay":        0.86,
        "dist_rate":        (0.03, 0.06),
    },
    "Smart": {
        "margem_bruta":     (0.26, 0.33),
        "desp_comercial":   (0.060, 0.075),
        "desp_admin":       (0.022, 0.032),
        "vso_burst":        (0.20, 0.30),
        "vso_decay":        0.90,
        "dist_rate":        (0.04, 0.08),
    },
}

# Proporção de custo por etapa de obra (soma = 1.0)
ETAPAS_PROP = {
    "Fundação":    0.10,
    "Estrutura":   0.26,
    "Alvenaria":   0.20,
    "Instalações": 0.23,
    "Acabamento":  0.15,
    "Entrega":     0.06,
}

# Limite acumulado de conclusão ao fim de cada etapa
ETAPA_LIM = {
    "Fundação":    0.12,
    "Estrutura":   0.38,
    "Alvenaria":   0.58,
    "Instalações": 0.78,
    "Acabamento":  0.93,
    "Entrega":     1.00,
}


def rnd(lo, hi):
    return np.random.uniform(lo, hi)


def etapa_completion(avanco, lim_ant, lim):
    """Fração de conclusão de uma etapa dado o avanço físico total."""
    if avanco <= lim_ant:
        return 0.0
    if avanco >= lim:
        return 1.0
    return (avanco - lim_ant) / (lim - lim_ant)


# ── Carregar empreendimentos (estrutura mantida) ───────────────────────────
emp = pd.read_csv(DATA_DIR / "empreendimentos.csv",
                  parse_dates=["lancamento", "entrega_prevista"])

# ── 1. DRE Gerencial ───────────────────────────────────────────────────────
dre_rows = []
emp_params = {}  # guarda parâmetros para reutilizar nos outros CSVs

# VSO acumulado realista por status
VSO_STATUS = {
    "entregue":   (0.90, 0.99),
    "em_obra":    (0.62, 0.84),
    "lancamento": (0.22, 0.48),
}

# Avanço físico por status
AVANCO_STATUS = {
    "entregue":   1.00,
    "em_obra":    {"EMP009": 0.58, "EMP010": 0.54, "EMP011": 0.62, "EMP012": 0.68,
                   "EMP013": 0.52, "EMP014": 0.45, "EMP015": 0.38},
    "lancamento": {"EMP016": 0.08, "EMP017": 0.06, "EMP018": 0.04, "EMP019": 0.03, "EMP020": 0.02},
}

for _, row in emp.iterrows():
    linha = row["linha"]
    p = SEG[linha]
    eid = row["id"]

    margem_bruta_pct = rnd(*p["margem_bruta"])
    desp_com_rate    = rnd(*p["desp_comercial"])
    desp_adm_rate    = rnd(*p["desp_admin"])

    status = row["status"]
    vso    = rnd(*VSO_STATUS[status])

    if status == "entregue":
        avanco = 1.00
    elif status == "em_obra":
        avanco = AVANCO_STATUS["em_obra"].get(eid, 0.55)
    else:
        avanco = AVANCO_STATUS["lancamento"].get(eid, 0.05)

    vgv_total   = row["vgv_total"]
    vgv_vendido = vgv_total * vso
    poc         = avanco

    # Receita reconhecida pelo método POC
    receita_poc = vgv_vendido * poc

    # Custo de obra reconhecido (proporcional ao POC)
    custo_obra_poc = receita_poc * (1 - margem_bruta_pct)
    margem_bruta   = receita_poc * margem_bruta_pct

    # Despesas reconhecidas proporcionalmente ao POC (método consistente)
    desp_comerciais = vgv_vendido * desp_com_rate * poc
    desp_admin      = vgv_total   * desp_adm_rate  * poc

    ebitda     = margem_bruta - desp_comerciais - desp_admin
    ebitda_pct = (ebitda / receita_poc * 100) if receita_poc > 0 else 0.0

    # Guardar parâmetros para reuso
    emp_params[eid] = {
        "margem_bruta_pct": margem_bruta_pct,
        "desp_com_rate":    desp_com_rate,
        "desp_adm_rate":    desp_adm_rate,
        "vso":              vso,
        "avanco":           avanco,
        "vgv_total":        vgv_total,
        "vgv_vendido":      vgv_vendido,
        "linha":            linha,
        "status":           status,
        "dist_rate":        rnd(*p["dist_rate"]),
    }

    dre_rows.append({
        "id_empreendimento":        eid,
        "nome":                     row["nome"],
        "bairro":                   row["bairro"],
        "status":                   status,
        "linha":                    linha,
        "vgv_lancado":              round(vgv_total, 0),
        "vgv_vendido":              round(vgv_vendido, 0),
        "vso_acumulado_pct":        round(vso * 100, 1),
        "avanco_obra_pct":          round(avanco * 100, 1),
        "receita_reconhecida_poc":  round(receita_poc, 0),
        "custo_obra_poc":           round(custo_obra_poc, 0),
        "margem_bruta":             round(margem_bruta, 0),
        "margem_bruta_pct":         round(margem_bruta_pct * 100, 1),
        "despesas_comerciais":      round(desp_comerciais, 0),
        "despesas_administrativas": round(desp_admin, 0),
        "ebitda":                   round(ebitda, 0),
        "ebitda_pct":               round(ebitda_pct, 1),
    })

dre_df = pd.DataFrame(dre_rows)
dre_df.to_csv(DATA_DIR / "dre_gerencial.csv", index=False)
print(f"dre_gerencial.csv: {len(dre_df)} linhas")
print(dre_df[["nome", "status", "avanco_obra_pct", "margem_bruta_pct", "ebitda_pct"]].to_string())


# ── 2. Custo de Obra ───────────────────────────────────────────────────────
obra_rows = []

for _, row in emp.iterrows():
    eid  = row["id"]
    prm  = emp_params[eid]
    avanco = prm["avanco"]

    # Custo total de construção = VGV total × (1 - margem bruta) × fator de custo
    # O custo orçado é calculado sobre o VGV vendido esperado (100% VSO)
    # Custo direto de construção ≈ VGV_total × 0.60-0.65 (custo/m²)
    custo_total_orc = prm["vgv_total"] * (1 - prm["margem_bruta_pct"]) * 0.92

    lim_ant = 0.0
    for etapa, prop in ETAPAS_PROP.items():
        lim = ETAPA_LIM[etapa]
        compl = etapa_completion(avanco, lim_ant, lim)

        custo_orc  = custo_total_orc * prop
        # Desvio realista: negativo (economia) nas fases iniciais,
        # leve desvio positivo nas intermediárias e finais
        if compl == 0:
            # Etapa não iniciada: custo realizado = 0, desvio = 0
            custo_real = 0.0
            desvio     = 0.0
        elif compl < 1.0:
            # Etapa em andamento: desvio pequeno e realizado proporcional
            desvio_base = rnd(-0.03, 0.08)
            custo_real  = custo_orc * compl * (1 + desvio_base)
            desvio      = round(desvio_base * 100, 1)
        else:
            # Etapa concluída: desvio representativo
            if etapa in ("Fundação", "Estrutura"):
                desvio_base = rnd(-0.02, 0.06)
            elif etapa in ("Alvenaria", "Instalações"):
                desvio_base = rnd(0.01, 0.10)
            else:
                desvio_base = rnd(-0.03, 0.07)
            custo_real  = custo_orc * (1 + desvio_base)
            desvio      = round(desvio_base * 100, 1)

        # receita POC desta etapa (proporcional)
        receita_etapa = prm["vgv_vendido"] * prop * compl

        obra_rows.append({
            "id_empreendimento":      eid,
            "nome_empreendimento":    row["nome"],
            "bairro":                 row["bairro"],
            "linha":                  prm["linha"],
            "etapa_obra":             etapa,
            "custo_orcado":           round(custo_orc, 0),
            "custo_realizado":        round(custo_real, 0),
            "desvio_pct":             desvio,
            "avanco_fisico_pct":      round(avanco * 100, 1),
            "poc_pct":                round(avanco * 100, 1),
            "receita_reconhecida_poc": round(receita_etapa, 0),
        })

        lim_ant = lim

obra_df = pd.DataFrame(obra_rows)
obra_df.to_csv(DATA_DIR / "custo_obra.csv", index=False)
print(f"\ncusto_obra.csv: {len(obra_df)} linhas")


# ── 3. Vendas Mensais ──────────────────────────────────────────────────────
vend_rows = []
HOJE = pd.Timestamp("2026-04-01")

for _, row in emp.iterrows():
    eid    = row["id"]
    prm    = emp_params[eid]
    p      = SEG[prm["linha"]]
    lancamento = row["lancamento"]

    # Série de meses: do lançamento até hoje (ou entrega + 6 meses)
    fim = min(HOJE, row["entrega_prevista"] + pd.DateOffset(months=6))
    meses = pd.date_range(lancamento, fim, freq="MS")
    if len(meses) == 0:
        continue

    unidades_total = row["unidades"]
    vso_burst   = rnd(*p["vso_burst"])
    decay       = p["vso_decay"]
    ticket_base = prm["vgv_total"] / unidades_total
    # Pequena variação de ticket ao longo do tempo (+0.5%/mês valorização)
    dist_total = prm["dist_rate"] * unidades_total

    estoque = unidades_total
    acum_vendidas = 0
    acum_distratos = 0

    for i, mes in enumerate(meses):
        # VSO calculado: burst decaindo
        if estoque <= 0:
            vso_m = 0.0
        else:
            vso_raw = vso_burst * (decay ** i) + rnd(-0.005, 0.010)
            vso_m   = max(0.005, min(vso_raw, 0.35))

        uv = round(estoque * vso_m)
        uv = max(0, min(uv, estoque))

        # Distratos distribuídos gradualmente
        dist_m = round(min(acum_vendidas * 0.004, dist_total - acum_distratos))
        dist_m = max(0, dist_m)

        estoque_ini = estoque
        estoque = estoque - uv + dist_m

        ticket_m = ticket_base * (1 + 0.005 * i)   # valorização 0.5%/mês
        vgv_m    = uv * ticket_m

        acum_vendidas  += uv
        acum_distratos += dist_m

        vend_rows.append({
            "id_empreendimento": eid,
            "nome":              row["nome"],
            "bairro":            row["bairro"],
            "linha":             prm["linha"],
            "data":              mes,
            "unidades_vendidas": int(uv),
            "distratos":         int(dist_m),
            "estoque_inicio":    int(estoque_ini),
            "vso_pct":           round(vso_m * 100, 2),
            "ticket_medio":      round(ticket_m, 0),
            "vgv_mes":           round(vgv_m, 0),
        })

vend_df = pd.DataFrame(vend_rows)
vend_df.to_csv(DATA_DIR / "vendas_mensais.csv", index=False)
print(f"vendas_mensais.csv: {len(vend_df)} linhas")


# ── 4. Fluxo de Caixa ─────────────────────────────────────────────────────
# Modelo realista de fluxo para incorporadora:
#   Entradas de vendas  = parcelas mensais dos compradores ao longo da obra
#                         (calculadas sobre VSO FINAL esperado ~90%, não o atual)
#   Entradas financiam. = crédito bancário (CEF/SFH) liberado em tranches na obra
#   Saídas obra         = desembolso de construção em curva S (lento→acelerado→lento)
#   Saídas despesas     = comissões + admin, concentradas no lançamento depois lineares
#
# Princípio: total entradas ≈ total saídas + margem → projeto viável por construção.
fc_rows = []

for _, row in emp.iterrows():
    eid    = row["id"]
    prm    = emp_params[eid]
    lancamento = row["lancamento"]
    # Série vai até entrega + 9 meses para capturar recebimentos pós-entrega
    fim    = row["entrega_prevista"] + pd.DateOffset(months=9)
    meses  = pd.date_range(lancamento, fim, freq="MS")
    n      = len(meses)
    if n == 0:
        continue

    vgv_total  = prm["vgv_total"]

    # VSO final esperado ao término da obra
    vso_final  = rnd(0.88, 0.97)
    vgv_final  = vgv_total * vso_final

    # Custo total de construção
    custo_total = vgv_total * (1 - prm["margem_bruta_pct"]) * 0.90

    t = np.arange(n)

    # ── Entradas de vendas ─────────────────────────────────────────────────
    # 30% em parcelas mensais durante obra (distribuídas uniformemente)
    # + entrada (sinal) de 5% concentrada no lançamento
    parcela_total = vgv_final * 0.30
    ent_vendas    = np.ones(n) * (parcela_total / n)
    n_launch      = max(1, int(n * 0.08))
    ent_vendas[:n_launch] += (vgv_final * 0.05) / n_launch  # sinal de lançamento

    # ── Entradas de financiamento ──────────────────────────────────────────
    # Crédito de produção (SFH/CEF): ~25-35% do custo, 4 tranches na fase de obra
    cred_producao = custo_total * rnd(0.25, 0.35)
    fin_obra = np.zeros(n)
    for tranche in [0.20, 0.40, 0.60, 0.78]:
        idx = min(int(n * tranche), n - 1)
        fin_obra[idx] += cred_producao / 4

    # Repasse bancário do comprador (~60% do VGV): distribuído suavemente
    # nos 6 meses próximos à entrega (entregas escalonadas por unidade)
    cred_entrega   = vgv_final * 0.60
    n_repasse      = max(6, int(n * 0.18))   # ≥ 6 meses para diluir
    idx_ini_rep    = max(0, n - n_repasse)
    fin_entrega    = np.zeros(n)
    # Curva crescente → pico na entrega → queda nos meses finais
    repasse_w      = np.linspace(0.5, 1.0, n_repasse // 2 + 1)
    repasse_w      = np.concatenate([repasse_w, np.linspace(1.0, 0.3, n_repasse - len(repasse_w) + 1)[1:]])
    repasse_w      = repasse_w[:n_repasse] / repasse_w[:n_repasse].sum()
    fin_entrega[idx_ini_rep:idx_ini_rep + n_repasse] = repasse_w * cred_entrega

    ent_fin = fin_obra + fin_entrega

    ent_fin = fin_obra + fin_entrega

    # ── Saídas de obra ────────────────────────────────────────────────────
    # Curva S realista: aceleração no início/meio, desaceleração no final
    # Fundação+Estrutura (0-38%): ~36% do custo
    # Alvenaria+Instalações (38-78%): ~43% do custo → fase mais intensa
    # Acabamento+Entrega (78-100%): ~21% do custo
    s_curve = np.zeros(n)
    for i, tv in enumerate(t):
        frac = tv / max(n - 1, 1)
        # Densidade: trapézio com pico entre 30-70% do ciclo
        if frac < 0.15:
            densidade = frac / 0.15 * 0.8
        elif frac < 0.70:
            densidade = 0.8 + (frac - 0.15) / 0.55 * 0.4
        elif frac < 0.85:
            densidade = 1.2 - (frac - 0.70) / 0.15 * 0.4
        else:
            densidade = 0.8 * (1 - (frac - 0.85) / 0.15)
        s_curve[i] = max(densidade, 0.05)

    s_curve = s_curve / s_curve.sum()
    sai_obra = s_curve * custo_total

    # ── Saídas de despesas ────────────────────────────────────────────────
    # Comissões: 60% no lançamento, 40% distribuídas ao longo das vendas
    total_desp  = vgv_total * (prm["desp_com_rate"] + prm["desp_adm_rate"])
    sai_desp    = np.ones(n) * (total_desp * 0.40 / n)
    n_launch    = max(1, int(n * 0.08))
    sai_desp[:n_launch] += (total_desp * 0.60) / n_launch

    for i, mes in enumerate(meses):
        et      = ent_vendas[i]
        ef      = ent_fin[i]
        so      = sai_obra[i]
        sd      = sai_desp[i]
        ent_tot = et + ef
        sai_tot = so + sd
        saldo   = ent_tot - sai_tot

        fc_rows.append({
            "id_empreendimento":      eid,
            "nome":                   row["nome"],
            "bairro":                 row["bairro"],
            "status":                 prm["status"],
            "linha":                  prm["linha"],
            "data":                   mes,
            "entradas_vendas":        round(et, 0),
            "entradas_financiamento": round(ef, 0),
            "saidas_obra":            round(so, 0),
            "saidas_despesas":        round(sd, 0),
            "entradas_total":         round(ent_tot, 0),
            "saidas_total":           round(sai_tot, 0),
            "saldo_mes":              round(saldo, 0),
        })

fc_df = pd.DataFrame(fc_rows)
fc_df.to_csv(DATA_DIR / "fluxo_caixa.csv", index=False)
print(f"fluxo_caixa.csv: {len(fc_df)} linhas")


# ── 5. Budget vs Realizado ─────────────────────────────────────────────────
bud_rows = []
CATS = ["Receita (POC)", "Custo de Obra", "Despesas Comerciais", "Despesas Adm.", "EBITDA"]

for _, row in emp.iterrows():
    eid  = row["id"]
    prm  = emp_params[eid]
    p    = emp_params[eid]
    status = prm["status"]

    # Fase inicial = projetos em lançamento ou em_obra com POC < 20%
    fase_ini = status == "lancamento" or (status == "em_obra" and prm["avanco"] < 0.20)

    vgv  = prm["vgv_total"]
    vso  = prm["vso"]
    poc  = prm["avanco"]
    mb   = prm["margem_bruta_pct"]
    dc   = prm["desp_com_rate"]
    da   = prm["desp_adm_rate"]

    rec_orc  = vgv * vso * poc
    rec_real = rec_orc * rnd(0.96, 1.06)

    custo_orc  = rec_orc  * (1 - mb)
    custo_real = custo_orc * rnd(0.97, 1.08)

    dcm_orc  = vgv * vso * dc * poc
    dcm_real = dcm_orc * rnd(0.94, 1.09)

    dam_orc  = vgv * da * poc
    dam_real = dam_orc * rnd(0.95, 1.07)

    ebitda_orc  = rec_orc  - custo_orc  - dcm_orc  - dam_orc
    ebitda_real = rec_real - custo_real - dcm_real - dam_real

    vals = [
        ("Receita (POC)",         rec_orc,    rec_real),
        ("Custo de Obra",         custo_orc,  custo_real),
        ("Despesas Comerciais",   dcm_orc,    dcm_real),
        ("Despesas Adm.",         dam_orc,    dam_real),
        ("EBITDA",                ebitda_orc, ebitda_real),
    ]

    for cat, orc, real in vals:
        var_abs = real - orc
        var_pct = (var_abs / abs(orc) * 100) if abs(orc) > 1 else 0.0
        bud_rows.append({
            "id_empreendimento": eid,
            "nome":              row["nome"],
            "bairro":            row["bairro"],
            "status":            status,
            "linha":             prm["linha"],
            "categoria":         cat,
            "orcado":            round(orc, 0),
            "realizado":         round(real, 0),
            "variacao_abs":      round(var_abs, 0),
            "variacao_pct":      round(var_pct, 1),
            "fase_inicial":      fase_ini,
        })

bud_df = pd.DataFrame(bud_rows)
bud_df.to_csv(DATA_DIR / "budget_realizado.csv", index=False)
print(f"budget_realizado.csv: {len(bud_df)} linhas")


# ── 6. Projeções 12 meses ──────────────────────────────────────────────────
proj_rows = []
HOJE_TS = pd.Timestamp("2026-04-01")
MESES_PROJ = pd.date_range(HOJE_TS, periods=12, freq="MS")

for _, row in emp.iterrows():
    eid  = row["id"]
    prm  = emp_params[eid]

    # Apenas empreendimentos ainda gerando receita futura
    if prm["status"] == "entregue" and prm["avanco"] >= 1.0:
        continue

    vgv      = prm["vgv_total"]
    vso      = prm["vso"]
    poc_ini  = prm["avanco"]
    mb       = prm["margem_bruta_pct"]
    dc       = prm["desp_com_rate"]
    da       = prm["desp_adm_rate"]

    # Velocidade de avanço projetada por mês (~2-4% por mês)
    avanco_mensal = rnd(0.018, 0.038)

    for i, mes in enumerate(MESES_PROJ):
        poc_proj   = min(1.0, poc_ini + avanco_mensal * (i + 1))
        poc_delta  = avanco_mensal   # avanço incremental neste mês

        receita_proj  = vgv * vso * poc_delta
        custo_proj    = receita_proj * (1 - mb)
        desp_com_proj = vgv * vso * dc * poc_delta
        desp_adm_proj = vgv * da * poc_delta
        ebitda_proj   = receita_proj - custo_proj - desp_com_proj - desp_adm_proj
        margem_proj   = (ebitda_proj / receita_proj * 100) if receita_proj > 0 else 0.0

        proj_rows.append({
            "id_empreendimento":   eid,
            "nome":                row["nome"],
            "bairro":              row["bairro"],
            "status":              prm["status"],
            "linha":               prm["linha"],
            "data":                mes,
            "avanco_projetado_pct": round(poc_proj * 100, 1),
            "receita_projetada":   round(receita_proj, 0),
            "custo_projetado":     round(custo_proj, 0),
            "ebitda_projetado":    round(ebitda_proj, 0),
            "margem_projetada_pct": round(margem_proj, 1),
        })

proj_df = pd.DataFrame(proj_rows)
proj_df.to_csv(DATA_DIR / "projecoes.csv", index=False)
print(f"projecoes.csv: {len(proj_df)} linhas")

print("\n✅ Todos os CSVs regenerados com sucesso!")
print("\n=== Verificação DRE ===")
dre_check = pd.read_csv(DATA_DIR / "dre_gerencial.csv")
print(dre_check[["nome","status","avanco_obra_pct","margem_bruta_pct","ebitda_pct"]].to_string())
