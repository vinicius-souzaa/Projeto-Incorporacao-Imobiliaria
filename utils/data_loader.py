import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

@st.cache_data if False else lambda f: f
def _noop(f): return f

def load_all():
    emp    = pd.read_csv(os.path.join(DATA_DIR, "empreendimentos.csv"), parse_dates=["lancamento", "entrega_prevista"])
    vendas = pd.read_csv(os.path.join(DATA_DIR, "vendas_mensais.csv"),  parse_dates=["data"])
    obra   = pd.read_csv(os.path.join(DATA_DIR, "custo_obra.csv"))
    dre    = pd.read_csv(os.path.join(DATA_DIR, "dre_gerencial.csv"))
    return emp, vendas, obra, dre
