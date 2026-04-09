# Portfólio Imobiliário Analytics SP

Dashboard gerencial para acompanhamento de portfólio de incorporação imobiliária de alto padrão em São Paulo. Desenvolvido com Python, Streamlit e Plotly.

**Paleta:** Navy & Gold — Clássico Corporativo (`#0D2137` · `#C9A84C`)

---

## Páginas e Insights

### 🏠 Visão Geral

Painel consolidado do portfólio com KPIs executivos e distribuição por bairro, status e linha de produto.

**Insights gerados automaticamente:**
- Empreendimento com maior margem bruta e distância ao benchmark de 30%
- Quantidade de empreendimentos acima do benchmark de margem e VGV total em pipeline de lançamentos
- Alerta de VSO acumulado abaixo de 75% com recomendação de revisão comercial

**Métricas exibidas:** Total de empreendimentos · VGV Total Lançado · VGV Vendido · VSO Médio · Margem Bruta Média

---

### 📈 Comercial & VSO

Análise de velocidade de vendas, distratos e VGV mensal. Filtrável por empreendimento individual ou visão consolidada do portfólio.

**Insights gerados automaticamente:**
- VSO mais recente vs benchmark de 10% (mínimo saudável do mercado SP) com alerta colorido
- Mês de pico de VGV comercializado com contexto de fase do lançamento
- Taxa de distrato acumulada vs limite de 5% com avaliação de qualidade do pipeline
- Bairros com melhor e pior VSO acumulado com recomendação de ação

**Métricas exibidas:** Unidades Vendidas · Distratos · VGV Comercializado · VSO Último Mês

**Benchmarks aplicados:**
- VSO mensal saudável: ≥ 10% (Secovi-SP)
- Taxa de distrato aceitável: ≤ 5%
- Meta de VSO acumulado: ≥ 85%

---

### 🏗️ Obras & POC

Controle de avanço físico pelo método POC (Percentage of Completion), curva S e desvio de orçamento por etapa de obra.

**Insights gerados automaticamente:**
- Etapa de maior desvio de custo com classificação de criticidade (até +3%: ok, até +8%: atenção, acima: crítico)
- Desvio total orçado vs realizado com impacto na margem bruta projetada
- Posição na curva S com detecção de atraso em relação ao cronograma planejado
- Alerta de risco de impacto no reconhecimento de receita POC quando atraso > 5pp

**Métricas exibidas:** Avanço Físico (POC) · Receita Reconhecida · Custo Realizado vs Desvio · Desvio Médio por Etapa

**Sobre o método POC:**
A receita é reconhecida proporcionalmente ao avanço físico da obra, não no momento da venda ou recebimento. Assim, uma obra com 60% de avanço e R$ 100M de VGV vendido reconhece R$ 60M de receita no DRE gerencial.

---

### 📊 DRE Gerencial

Demonstrativo de Resultado Econômico por empreendimento e consolidado, com waterfall, análise bidimensional Margem × VSO e comparativo por linha de produto.

**Insights gerados automaticamente:**
- Melhor e pior margem bruta do portfólio com recomendação de ação para o pior
- Margem EBITDA consolidada vs referência de 12-15% do setor imobiliário SP
- Quantidade de empreendimentos no quadrante ideal (VSO ≥ 80% e Margem ≥ 30%)
- Margem por linha de produto (Premium · Alto Padrão · Smart) vs benchmark

**Métricas exibidas:** Receita Total POC · Custo Total POC · Margem Bruta Média · EBITDA Acumulado

**Benchmarks aplicados:**
- Margem bruta saudável: ≥ 30%
- Margem bruta excelente: ≥ 33%
- Margem EBITDA referência setor: 12–15%
- VSO acumulado meta: ≥ 80%

---

## Filtros Inteligentes

Os filtros da sidebar são encadeados e dinâmicos:

1. **Bairro** → atualiza as opções de Status disponíveis para aquele bairro
2. **Status** → atualiza as opções de Linha de Produto disponíveis
3. **Linha** → filtra todos os gráficos e insights

Se um bairro tem apenas empreendimentos "Em Obra", o filtro de status só mostrará essa opção — evitando combinações inválidas que resultariam em tela vazia.

---

## Conceitos do Setor Imobiliário

| Termo | Definição |
|-------|-----------|
| **VGV** | Valor Geral de Vendas — potencial máximo de receita do empreendimento |
| **VSO** | Velocidade de Vendas sobre Oferta — % do estoque vendido no período |
| **POC** | Percentage of Completion — reconhecimento de receita proporcional ao avanço físico |
| **Distrato** | Cancelamento de contrato de compra pelo comprador |
| **Curva S** | Comparativo entre avanço físico planejado e realizado ao longo da obra |
| **DRE Gerencial** | Resultado por empreendimento — diferente do DRE societário obrigatório |
| **Permuta** | Pagamento do terreno com unidades do empreendimento |

---

## Dados

Dataset sintético com **20 empreendimentos** gerado com parâmetros calibrados com dados públicos do mercado imobiliário de São Paulo (Secovi-SP / ABRAINC-FIPE):

- VSO mensal de mercado: 10–16%/mês nos primeiros meses
- Margem bruta alto padrão SP: 30–45%
- Taxa de distrato saudável: até 5%
- Bairros reais: Brooklin, Pinheiros, Campo Belo, Chácara Klabin, Mooca, Santana, Aclimação, Alto da Lapa, Perdizes, Itaim Bibi, Vila Olímpia, Moema, Jundiaí, Chácara Sto. Antônio
- Linhas de produto: Premium · Alto Padrão · Smart
- Período: 2018–2028 (histórico + projeção)

---

## Stack

| Tecnologia | Uso |
|------------|-----|
| Python 3.11+ | Linguagem principal |
| Streamlit | Interface e deploy |
| Plotly | Visualizações interativas |
| Pandas | Manipulação de dados |

---

## Como rodar localmente

```bash
git clone https://github.com/vinicius-souzaa/Projeto-Incorporacao-Imobiliaria
cd Projeto-Incorporacao-Imobiliaria
pip install -r requirements.txt
streamlit run app.py
```

---

*Desenvolvido por Vinicius · Portfólio Data Analytics · 2026*
