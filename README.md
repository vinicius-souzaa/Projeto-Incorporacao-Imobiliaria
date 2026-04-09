# 🏙️ TDRE Dashboard — Incorporadora · Alto Padrão SP

Dashboard gerencial para acompanhamento de portfólio de incorporação imobiliária de alto padrão em São Paulo. Desenvolvido com Python, Streamlit e Plotly.

## Páginas

| Página | Descrição |
|--------|-----------|
| 🏠 Visão Geral | KPIs consolidados, VGV por empreendimento, status do portfólio |
| 📈 Comercial & VSO | Velocidade de Vendas (VSO), distratos, VGV mensal |
| 🏗️ Obras & POC | Curva S, desvio de orçamento, Percentage of Completion |
| 📊 DRE Gerencial | Resultado econômico por empreendimento, waterfall, scatter margem × VSO |

## Conceitos implementados

- **VGV** (Valor Geral de Vendas): potencial máximo de receita do empreendimento
- **VSO** (Velocidade de Vendas sobre Oferta): % do estoque vendido no período
- **POC** (Percentage of Completion): método de reconhecimento de receita proporcional ao avanço físico da obra
- **Curva S**: comparativo entre avanço físico planejado e realizado ao longo da obra
- **DRE Gerencial**: resultado econômico por empreendimento (Receita POC → Margem Bruta → EBITDA)

## Como rodar localmente

```bash
git clone https://github.com/seu-usuario/incorporadora-dashboard
cd incorporadora-dashboard
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Streamlit Cloud

1. Faça push deste repositório para o GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Clique em **New app**
4. Selecione o repositório, branch `main` e arquivo `app.py`
5. Clique em **Deploy**

## Dados

Dataset sintético gerado com base em parâmetros reais do mercado imobiliário de São Paulo (Secovi-SP / ABRAINC-FIPE):
- VSO médio de mercado: 10–15%/mês
- Margem bruta alto padrão SP: 30–42%
- 8 empreendimentos fictícios em bairros reais (Brooklin, Pinheiros, Campo Belo, Chácara Klabin, Mooca, Santana, Aclimação)

## Stack

- **Python 3.11+**
- **Streamlit** — interface e deploy
- **Plotly** — visualizações interativas
- **Pandas** — manipulação de dados

---
Desenvolvido por Vinicius · Portfólio Data Analytics
