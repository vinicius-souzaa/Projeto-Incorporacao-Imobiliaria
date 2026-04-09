# 🏙️ Portfólio Imobiliário — Analytics SP

> Dashboard gerencial para acompanhamento de portfólio de incorporação imobiliária de alto padrão em São Paulo. Cobre FP&A, DRE Gerencial, Fluxo de Caixa, Budget vs Realizado, projeções de 12 meses, semáforo RAG automático e mapa de calor estratégico — 91% de cobertura dos KPIs exigidos em controladoria de incorporadoras.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://projeto-incorporacao-imobiliaria.streamlit.app)

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-green)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-purple)](https://plotly.com)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-yellow)](https://pandas.pydata.org)

---

## 📌 Sobre o projeto

O mercado imobiliário de alto padrão em São Paulo movimenta mais de R$ 59 bilhões em VGV por ano (Secovi-SP, out/2024–set/2025). Uma incorporadora com 8–20 empreendimentos simultâneos precisa acompanhar resultado econômico (POC), fluxo de caixa, desvio de orçamento de obra e velocidade de vendas — tudo ao mesmo tempo, por projeto. Este dashboard simula exatamente esse ambiente de controladoria, com 7 páginas e 29 seções analíticas cobrindo os indicadores que um Analista de BI Sênior entrega para o diretor financeiro.

**Design:** Navy & Gold — Fundo `#0F1923` + Acento `#C9A84C` — estética executiva para apresentações de diretoria.

---

## 📊 Dados

### Fontes e volumes

| Dataset | Origem | Arquivo | Registros | Período |
|---------|--------|---------|-----------|---------|
| Empreendimentos | Sintético (TDRE-inspired) | `empreendimentos.csv` | 20 | 2018–2028 |
| Vendas Mensais | Sintético (Secovi-SP calibrado) | `vendas_mensais.csv` | 602 | 2018–2028 |
| Custo de Obra | Sintético (etapas reais) | `custo_obra.csv` | 120 | — |
| DRE Gerencial | Calculado (método POC) | `dre_gerencial.csv` | 20 | — |
| Fluxo de Caixa | Sintético (SFH/SFI modelado) | `fluxo_caixa.csv` | 602 | 2018–2028 |
| Budget vs Realizado | Calculado (variação orçamentária) | `budget_realizado.csv` | 100 | — |
| Projeções | Calculado (forecast 12 meses) | `projecoes.csv` | 240 | 2025–2026 |

> Dados sintéticos calibrados com parâmetros reais do mercado imobiliário SP: VSO médio 13,6%/mês (Secovi-SP jun/2025), margem bruta alto padrão 30–42%, taxa de distrato aceitável ≤5%, custo de obra 55–60% do VGV.

### Dataset empreendimentos

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | string | Identificador único (EMP001–EMP020) |
| `nome` | string | Nome do empreendimento |
| `bairro` | string | Bairro em São Paulo (14 bairros) |
| `vgv_total` | float | Valor Geral de Vendas lançado (R$) |
| `unidades` | int | Número total de unidades |
| `lancamento` | date | Data de lançamento |
| `entrega_prevista` | date | Previsão de entrega |
| `status` | string | `entregue` / `em_obra` / `lancamento` |
| `linha` | string | `Premium` / `Alto Padrão` / `Smart` |

### Key stats do portfólio

| Métrica | Valor |
|---------|-------|
| Empreendimentos | 20 |
| VGV Total Lançado | ~R$ 2,3B |
| Bairros cobertos | 14 (Brooklin, Perdizes, Pinheiros, Itaim Bibi, Campo Belo, Moema e outros) |
| Linhas de produto | 3 (Premium, Alto Padrão, Smart) |
| Status: Entregues / Em Obra / Lançamento | 8 / 7 / 5 |
| Margem bruta média | 32–38% |
| VSO médio acumulado | ~85% |
| Período coberto | 2018–2028 |

---

## 🗂️ Estrutura do projeto

```
Projeto-Incorporacao-Imobiliaria/
├── app.py                        # Aplicação principal — 7 páginas, sidebar com filtros encadeados
├── requirements.txt
├── README.md
├── .gitignore
│
└── data/
    ├── empreendimentos.csv       # Cadastro dos 20 empreendimentos
    ├── vendas_mensais.csv        # 602 linhas — VSO, VGV, distratos por mês/empreendimento
    ├── custo_obra.csv            # 120 linhas — orçado vs realizado por etapa de obra
    ├── dre_gerencial.csv         # 20 linhas — DRE consolidado por empreendimento (método POC)
    ├── fluxo_caixa.csv           # 602 linhas — entradas e saídas mensais de caixa
    ├── budget_realizado.csv      # 100 linhas — budget vs realizado por categoria e empreendimento
    └── projecoes.csv             # 240 linhas — forecast de receita e EBITDA para 12 meses
```

---

## 🔍 Páginas e análises

### ⚡ Executive Summary

Primeira tela para o diretor. Seis KPIs executivos no topo: empreendimentos, VGV total, VGV vendido (com % do total), margem bruta média (com delta vs benchmark), receita POC e EBITDA. Semáforo RAG automático — cada empreendimento recebe verde/amarelo/vermelho com base em três critérios combinados: margem bruta, VSO acumulado e EBITDA %. Ranking de desempenho por margem bruta com codificação de cores semântica. Mapa de calor estratégico cruzando bairro × linha de produto — principal ferramenta de decisão de novos lançamentos. Alertas automáticos de risco com hierarquia crítico/atenção e texto contextual por empreendimento.

### 🏠 Visão Geral do Portfólio

Panorama completo. VGV por empreendimento em barras empilhadas por status (entregue/em obra/lançamento). Donut de distribuição por status. Barras de linha de produto (Premium/Alto Padrão/Smart). VGV lançado por ano com empilhamento por linha — permite identificar pivôs estratégicos. VGV total por bairro revelando concentração geográfica de risco. Três insights automáticos: líder de margem, quantidade acima do benchmark e alerta de VSO.

### 📈 Comercial & Velocidade de Vendas sobre Oferta (VSO)

Análise de desempenho comercial mensal. VSO mensal em gráfico de área com linha de benchmark de 10% (Secovi-SP). VGV comercializado mensal com identificação do pico de lançamento. Vendas vs Distratos agrupados com cálculo automático de taxa de distrato vs limite de 5%. VSO acumulado por bairro com codificação verde/dourado/vermelho e meta de 85%. Quatro insights automáticos com texto condicional baseado nos valores reais.

### 🏗️ Obras & Percentual de Conclusão (POC)

Controle operacional de obra. Custo orçado vs realizado por etapa (Fundação → Estrutura → Alvenaria → Instalações → Acabamento → Entrega). Desvio percentual por etapa com limite crítico de +8% marcado. Curva S — comparativo entre cronograma planejado e avanço físico realizado ao longo dos 36 meses de obra, com detecção automática de atraso. POC consolidado de todos os empreendimentos com hover mostrando receita reconhecida em R$.

### 📊 DRE Gerencial

Demonstrativo de Resultado Econômico pelo método POC. Margem bruta por empreendimento com codificação <25% / 25–33% / >33% e benchmark de 30%. Waterfall do DRE decompondo Receita POC → Custo de Obra → Despesas Comerciais → Despesas Adm. → EBITDA com cálculo de margem EBITDA vs referência de 12–15% do setor. Margem por linha de produto. Análise bidimensional Margem × VSO em bubble chart — os quatro quadrantes de performance do portfólio com tamanho de bolha proporcional ao VGV.

### 💰 Fluxo de Caixa

Movimentação real de dinheiro — diferente do DRE (POC). Entradas vs saídas em barras divergentes mensais. Saldo de caixa acumulado ao longo do ciclo com detecção de meses negativos. Composição das entradas separando recebimentos de compradores de financiamento bancário (SFH/SFI). Necessidade de capital por empreendimento — pico de exposição financeira que cada projeto exigiu da incorporadora. Quatro insights automáticos incluindo análise de dependência de financiamento bancário.

### 🎯 FP&A — Planejamento Financeiro, Análise & Projeções

Budget vs Realizado consolidado por categoria (Receita POC, Custo de Obra, Despesas Comerciais, Despesas Adm., EBITDA) com barras agrupadas orçado/realizado. Variação orçamentária % com semântica de cor correta — custo abaixo do orçado é verde mesmo sendo valor negativo. Variação de EBITDA por empreendimento excluindo automaticamente projetos em fase inicial (<10% POC) com nota explicativa. Projeção de receita POC para os próximos 12 meses baseada no ritmo atual de avanço físico. Projeção de EBITDA mensal com identificação de meses negativos estruturais. Análise comparativa de margens com eixo duplo — Margem Bruta + EBITDA (barras) e POC (linha) sobrepostos por empreendimento.

---

## 🏗️ Conceitos do setor imobiliário implementados

| Conceito | Implementação |
|----------|--------------|
| **VGV** (Valor Geral de Vendas) | Todas as páginas — potencial máximo de receita ao preço de tabela |
| **VSO** (Velocidade de Vendas sobre Oferta) | Página Comercial — % do estoque vendido por mês |
| **POC** (Percentage of Completion) | Páginas Obras e DRE — reconhecimento de receita proporcional ao avanço físico |
| **Distrato** | Página Comercial — cancelamentos com taxa vs limite de 5% |
| **Curva S** | Página Obras — avanço físico planejado vs realizado |
| **DRE Gerencial** | Página DRE — resultado econômico ≠ resultado de caixa |
| **Fluxo de Caixa** | Página FC — movimentação real de dinheiro, independente do POC |
| **Budget vs Realizado** | Página FP&A — variação orçamentária por categoria e projeto |
| **Semáforo RAG** | Executive Summary — Red/Amber/Green automático por projeto |
| **Mapa de calor** | Executive Summary — margem bruta por bairro × linha de produto |

---

## 🎯 Benchmarks de mercado aplicados

| Indicador | Benchmark | Fonte |
|-----------|-----------|-------|
| VSO mensal saudável | ≥ 10%/mês | Secovi-SP (jun/2025: 13,6%) |
| VSO acumulado meta | ≥ 85% | Prática de mercado SP |
| Taxa de distrato | ≤ 5% | Prática de mercado incorporadoras SP |
| Margem bruta adequada | ≥ 30% | Secovi-SP / alto padrão SP |
| Margem bruta excelente | ≥ 33% | Alto padrão SP |
| Margem EBITDA referência | 12–15% | Setor imobiliário SP |
| Desvio de custo de obra crítico | > +8% por etapa | Prática de mercado |
| Dependência de financiamento bancário | < 30% das entradas | Prática saudável |

---

## 🔧 Filtros encadeados

Os três filtros da sidebar são dependentes em cascata:

1. **Bairro** → atualiza dinamicamente os status disponíveis
2. **Status** → atualiza dinamicamente as linhas de produto disponíveis
3. **Linha de Produto** → filtra todos os gráficos e insights simultaneamente

Se um bairro tem apenas empreendimentos "Em Obra", o filtro de status exibirá somente essa opção — eliminando combinações inválidas.

---

## 🚀 Como rodar localmente

```bash
git clone https://github.com/vinicius-souzaa/Projeto-Incorporacao-Imobiliaria
cd Projeto-Incorporacao-Imobiliaria
pip install -r requirements.txt
streamlit run app.py
```

---

## 📦 Stack

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.11+ | Linguagem principal |
| Streamlit | 1.32+ | Interface web e deploy |
| Plotly | 5.18+ | Visualizações interativas (29 gráficos) |
| Pandas | 2.0+ | Manipulação e cálculo dos datasets |

---

*Desenvolvido por Vinicius Souza · Portfólio Data Analytics · 2026*
*Dados sintéticos calibrados com Secovi-SP / ABRAINC-FIPE — não representam dados reais de nenhuma incorporadora.*
