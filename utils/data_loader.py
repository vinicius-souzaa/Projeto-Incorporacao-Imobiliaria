from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data
def load_all():
    emp  = pd.read_csv(DATA_DIR / "empreendimentos.csv",  parse_dates=["lancamento", "entrega_prevista"])
    vend = pd.read_csv(DATA_DIR / "vendas_mensais.csv",   parse_dates=["data"])
    obra = pd.read_csv(DATA_DIR / "custo_obra.csv")
    dre  = pd.read_csv(DATA_DIR / "dre_gerencial.csv")
    fc   = pd.read_csv(DATA_DIR / "fluxo_caixa.csv",      parse_dates=["data"])
    bud  = pd.read_csv(DATA_DIR / "budget_realizado.csv")
    proj = pd.read_csv(DATA_DIR / "projecoes.csv",         parse_dates=["data"])
    return emp, vend, obra, dre, fc, bud, proj
