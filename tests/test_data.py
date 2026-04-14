"""
Testes de validação dos CSVs de entrada e da sintaxe do app.
Executar com: pytest tests/ -v
"""
import ast
from pathlib import Path
import pandas as pd
import pytest

DATA_DIR  = Path(__file__).parent.parent / "data"
ROOT_DIR  = Path(__file__).parent.parent

VALID_STATUS = {"entregue", "em_obra", "lancamento"}
VALID_LINHAS = {"Premium", "Alto Padrão", "Smart"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def load(filename, **kwargs):
    return pd.read_csv(DATA_DIR / filename, **kwargs)


# ── Empreendimentos ───────────────────────────────────────────────────────────

def test_empreendimentos_colunas_obrigatorias():
    df = load("empreendimentos.csv")
    required = {"id", "nome", "bairro", "vgv_total", "unidades",
                "lancamento", "entrega_prevista", "status", "linha"}
    missing = required - set(df.columns)
    assert not missing, f"Colunas ausentes em empreendimentos.csv: {missing}"


def test_empreendimentos_sem_nulos_em_campos_chave():
    df = load("empreendimentos.csv")
    for col in ["id", "nome", "bairro", "vgv_total", "status", "linha"]:
        assert df[col].notna().all(), f"Valores nulos em empreendimentos.csv['{col}']"


def test_empreendimentos_vgv_positivo():
    df = load("empreendimentos.csv")
    assert (df["vgv_total"] > 0).all(), "vgv_total deve ser positivo em empreendimentos.csv"


def test_empreendimentos_unidades_positivas():
    df = load("empreendimentos.csv")
    assert (df["unidades"] > 0).all(), "unidades deve ser positivo em empreendimentos.csv"


def test_empreendimentos_status_validos():
    df = load("empreendimentos.csv")
    invalidos = set(df["status"].unique()) - VALID_STATUS
    assert not invalidos, f"Status inválidos em empreendimentos.csv: {invalidos}"


def test_empreendimentos_ids_unicos():
    df = load("empreendimentos.csv")
    assert df["id"].nunique() == len(df), "IDs duplicados em empreendimentos.csv"


def test_empreendimentos_datas_parseáveis():
    df = load("empreendimentos.csv", parse_dates=["lancamento", "entrega_prevista"])
    assert pd.api.types.is_datetime64_any_dtype(df["lancamento"]), \
        "lancamento não parseável como data"
    assert pd.api.types.is_datetime64_any_dtype(df["entrega_prevista"]), \
        "entrega_prevista não parseável como data"


def test_empreendimentos_entrega_apos_lancamento():
    df = load("empreendimentos.csv", parse_dates=["lancamento", "entrega_prevista"])
    invalid = df[df["entrega_prevista"] < df["lancamento"]]
    assert len(invalid) == 0, \
        f"entrega_prevista anterior ao lancamento em {invalid['nome'].tolist()}"


# ── Vendas Mensais ────────────────────────────────────────────────────────────

def test_vendas_mensais_colunas_obrigatorias():
    df = load("vendas_mensais.csv")
    required = {"id_empreendimento", "nome", "data", "unidades_vendidas",
                "distratos", "estoque_inicio", "vso_pct", "vgv_mes"}
    missing = required - set(df.columns)
    assert not missing, f"Colunas ausentes em vendas_mensais.csv: {missing}"


def test_vendas_mensais_vso_range():
    df = load("vendas_mensais.csv")
    assert (df["vso_pct"] >= 0).all(), "vso_pct não pode ser negativo"
    assert (df["vso_pct"] <= 100).all(), "vso_pct não pode exceder 100%"


def test_vendas_mensais_distratos_nao_negativos():
    df = load("vendas_mensais.csv")
    assert (df["distratos"] >= 0).all(), "distratos não pode ser negativo"


def test_vendas_mensais_data_parseável():
    df = load("vendas_mensais.csv", parse_dates=["data"])
    assert pd.api.types.is_datetime64_any_dtype(df["data"]), \
        "data não parseável em vendas_mensais.csv"


# ── DRE Gerencial ─────────────────────────────────────────────────────────────

def test_dre_colunas_obrigatorias():
    df = load("dre_gerencial.csv")
    required = {"id_empreendimento", "nome", "status", "linha",
                "vgv_lancado", "vgv_vendido", "margem_bruta_pct",
                "ebitda", "ebitda_pct", "receita_reconhecida_poc",
                "custo_obra_poc", "despesas_comerciais", "despesas_administrativas",
                "vso_acumulado_pct", "avanco_obra_pct"}
    missing = required - set(df.columns)
    assert not missing, f"Colunas ausentes em dre_gerencial.csv: {missing}"


def test_dre_status_validos():
    df = load("dre_gerencial.csv")
    invalidos = set(df["status"].unique()) - VALID_STATUS
    assert not invalidos, f"Status inválidos em dre_gerencial.csv: {invalidos}"


def test_dre_margem_range_plausivel():
    df = load("dre_gerencial.csv")
    assert (df["margem_bruta_pct"] >= -50).all(), "margem_bruta_pct abaixo de -50% parece incorreto"
    assert (df["margem_bruta_pct"] <= 100).all(), "margem_bruta_pct acima de 100% parece incorreto"


def test_dre_avanco_obra_range():
    df = load("dre_gerencial.csv")
    assert (df["avanco_obra_pct"] >= 0).all(),   "avanco_obra_pct não pode ser negativo"
    assert (df["avanco_obra_pct"] <= 100).all(), "avanco_obra_pct não pode exceder 100%"


# ── Custo de Obra ─────────────────────────────────────────────────────────────

def test_custo_obra_colunas_obrigatorias():
    df = load("custo_obra.csv")
    required = {"id_empreendimento", "nome_empreendimento", "etapa_obra",
                "custo_orcado", "custo_realizado", "desvio_pct",
                "avanco_fisico_pct", "receita_reconhecida_poc"}
    missing = required - set(df.columns)
    assert not missing, f"Colunas ausentes em custo_obra.csv: {missing}"


def test_custo_obra_custos_positivos():
    df = load("custo_obra.csv")
    assert (df["custo_orcado"] > 0).all(),   "custo_orcado deve ser positivo"
    assert (df["custo_realizado"] > 0).all(), "custo_realizado deve ser positivo"


# ── Fluxo de Caixa ────────────────────────────────────────────────────────────

def test_fluxo_caixa_colunas_obrigatorias():
    df = load("fluxo_caixa.csv")
    required = {"id_empreendimento", "nome", "data",
                "entradas_total", "saidas_total", "saldo_mes",
                "entradas_vendas", "entradas_financiamento",
                "saidas_obra", "saidas_despesas"}
    missing = required - set(df.columns)
    assert not missing, f"Colunas ausentes em fluxo_caixa.csv: {missing}"


def test_fluxo_caixa_total_consistente():
    """entradas_total deve bater com soma das entradas parciais."""
    df = load("fluxo_caixa.csv")
    diff = (df["entradas_total"] - (df["entradas_vendas"] + df["entradas_financiamento"])).abs()
    assert (diff < 1.0).all(), "entradas_total inconsistente com soma das parcelas"


# ── Budget Realizado ──────────────────────────────────────────────────────────

def test_budget_realizado_colunas_obrigatorias():
    df = load("budget_realizado.csv")
    required = {"id_empreendimento", "nome", "categoria",
                "orcado", "realizado", "variacao_pct", "fase_inicial"}
    missing = required - set(df.columns)
    assert not missing, f"Colunas ausentes em budget_realizado.csv: {missing}"


def test_budget_realizado_fase_inicial_booleano():
    df = load("budget_realizado.csv")
    vals = set(df["fase_inicial"].unique())
    # Aceita True/False ou True/False como strings
    validos = {True, False, "True", "False", 0, 1}
    assert vals.issubset(validos), f"fase_inicial com valores inesperados: {vals - validos}"


# ── Projeções ─────────────────────────────────────────────────────────────────

def test_projecoes_colunas_obrigatorias():
    df = load("projecoes.csv")
    required = {"id_empreendimento", "nome", "data",
                "receita_projetada", "ebitda_projetado", "margem_projetada_pct"}
    missing = required - set(df.columns)
    assert not missing, f"Colunas ausentes em projecoes.csv: {missing}"


# ── Integridade referencial ───────────────────────────────────────────────────

def test_ids_vendas_referenciados_em_empreendimentos():
    emp  = load("empreendimentos.csv")
    vend = load("vendas_mensais.csv")
    orphans = set(vend["id_empreendimento"]) - set(emp["id"])
    assert not orphans, f"IDs em vendas_mensais.csv sem referência em empreendimentos.csv: {orphans}"


def test_ids_dre_referenciados_em_empreendimentos():
    emp = load("empreendimentos.csv")
    dre = load("dre_gerencial.csv")
    orphans = set(dre["id_empreendimento"]) - set(emp["id"])
    assert not orphans, f"IDs em dre_gerencial.csv sem referência em empreendimentos.csv: {orphans}"


def test_ids_fluxo_referenciados_em_empreendimentos():
    emp = load("empreendimentos.csv")
    fc  = load("fluxo_caixa.csv")
    orphans = set(fc["id_empreendimento"]) - set(emp["id"])
    assert not orphans, f"IDs em fluxo_caixa.csv sem referência em empreendimentos.csv: {orphans}"


# ── Sintaxe do app ────────────────────────────────────────────────────────────

def test_app_py_sintaxe_valida():
    """Garante que app.py não tem erros de sintaxe Python."""
    source = (ROOT_DIR / "app.py").read_text(encoding="utf-8")
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"Erro de sintaxe em app.py: {e}")


def test_data_loader_sintaxe_valida():
    """Garante que utils/data_loader.py não tem erros de sintaxe Python."""
    source = (ROOT_DIR / "utils" / "data_loader.py").read_text(encoding="utf-8")
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"Erro de sintaxe em utils/data_loader.py: {e}")


def test_todos_csvs_existem():
    csvs = [
        "empreendimentos.csv", "vendas_mensais.csv", "custo_obra.csv",
        "dre_gerencial.csv", "fluxo_caixa.csv", "budget_realizado.csv", "projecoes.csv",
    ]
    for csv in csvs:
        assert (DATA_DIR / csv).exists(), f"CSV ausente: {csv}"
