import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from financial_analysis import FinancialAnalyzer
import io
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Análise de Precificação e Lucratividade",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-card {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .info-card {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

# Função para gerar relatório em PDF
def generate_report(analyzer, cvp_analysis, contribution_analysis):
    """Gera relatório em formato texto para download"""
    report = f"""
RELATÓRIO DE ANÁLISE FINANCEIRA - CAFETERIA
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
{'='*60}

RESUMO EXECUTIVO
{'='*60}
• Receita Total: R$ {cvp_analysis['total_revenue']:,.2f}
• Margem de Contribuição Total: R$ {cvp_analysis['total_contribution']:,.2f}
• Custos Fixos: R$ {cvp_analysis['fixed_costs']:,.2f}
• Lucro Líquido: R$ {cvp_analysis['net_profit']:,.2f}
• Margem de Contribuição (%): {cvp_analysis['contribution_margin_ratio']:.1f}%

ANÁLISE POR PRODUTO
{'='*60}
"""
    
    for _, product in contribution_analysis.iterrows():
        report += f"""
{product['name']}:
  - Preço: R$ {product['price']:.2f}
  - Custo Variável: R$ {product['cost']:.2f}
  - Margem de Contribuição: R$ {product['contribution_margin']:.2f} ({product['contribution_margin_percent']:.1f}%)
  - Quantidade Vendida: {product['quantity']} unidades
  - Contribuição Total: R$ {product['total_contribution']:.2f}
  - Participação na Receita: {product['revenue_participation']:.1f}%
  - Participação na Contribuição: {product['contribution_participation']:.1f}%
"""

    report += f"""

ANÁLISE CUSTO-VOLUME-LUCRO
{'='*60}
• Ponto de Equilíbrio (unidades): {cvp_analysis['breakeven_units']:,.0f}
• Ponto de Equilíbrio (receita): R$ {cvp_analysis['breakeven_revenue']:,.2f}
• Margem de Segurança (unidades): {cvp_analysis['safety_margin_units']:,.0f}
• Margem de Segurança (%): {cvp_analysis['safety_margin_percent']:.1f}%
• Alavancagem Operacional: {cvp_analysis['operating_leverage']:.2f}
• Razão Margem de Contribuição: {cvp_analysis['contribution_margin_ratio']:.1f}%

RECOMENDAÇÕES ESTRATÉGICAS
{'='*60}
"""
    
    optimization = analyzer.analyze_product_mix_optimization()
    
    report += "\nPRODUTOS COM MAIOR MARGEM:\n"
    for product in optimization['high_margin_products']:
        report += f"• {product['name']}: {product['contribution_margin_percent']:.1f}% de margem\n"
    
    report += "\nPRODUTOS COM MENOR MARGEM:\n"
    for product in optimization['low_margin_products']:
        report += f"• {product['name']}: {product['contribution_margin_percent']:.1f}% de margem\n"
    
    report += "\nMAIORES CONTRIBUIDORES:\n"
    for product in optimization['high_contribution_products']:
        report += f"• {product['name']}: R$ {product['total_contribution']:.2f}\n"
    
    report += f"""

CONCLUSÕES E PRÓXIMOS PASSOS
{'='*60}
1. Foque nos produtos de maior margem para aumentar lucratividade
2. Revise preços ou custos dos produtos de menor margem
3. Considere criar combos estratégicos
4. Monitore regularmente o ponto de equilíbrio
5. Analise oportunidades de aumento de volume nos produtos mais lucrativos

Relatório gerado automaticamente pelo Sistema de Análise de Precificação e Lucratividade
"""
    
    return report

# Título principal
st.title("☕ Análise de Precificação e Lucratividade da Cafeteria")
st.markdown("**Sistema completo para otimização de lucratividade e análise de combos**")
st.markdown("---")

# Sidebar para entrada de dados
# Logo da cafeteria
st.sidebar.image(
    "https://github.com/cesarvalentimjr/custovolumelucro/blob/main/dicelestelogo.jpg?raw=true",
    use_container_width=True
)
st.sidebar.header("📊 Configurações e Dados de Entrada")

# Seção para upload de planilha
st.sidebar.subheader("📁 Upload de Dados")

# Botão para download do template
#with open('/home/ubuntu/streamlit_app/template_planilha.xlsx', 'rb') as template_file:
   # st.sidebar.download_button(
       # label="📥 Baixar Planilha Template",
       # data=template_file.read(),
       # file_name="template_cafeteria.xlsx",
      #  mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
   # )

# Upload de arquivo
uploaded_file = st.sidebar.file_uploader(
    "Faça upload da planilha com dados dos produtos",
    type=['xlsx', 'xls', 'csv'],
    help="Use a planilha template baixada acima"
)

# Campo para alíquota do SIMPLES
st.sidebar.subheader("💸 Tributação SIMPLES")
tax_rate = st.sidebar.number_input(
    "% Alíquota Efetiva (SIMPLES)",
    min_value=0.0, max_value=30.0, value=0.0, step=0.1,
    help="Percentual efetivo de tributação sobre a receita"
)

# Seção para dados de produtos
st.sidebar.subheader("🍰 Dados dos Produtos")

# Opção para carregar dados de exemplo
if st.sidebar.button("📋 Carregar Dados de Exemplo"):
    st.session_state.example_data = True

# Processar dados do upload ou usar entrada manual
product_data = []
use_uploaded_data = False

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_upload = pd.read_csv(uploaded_file)
        else:
            df_upload = pd.read_excel(uploaded_file)
        
        # Verificar se as colunas necessárias existem
        required_columns = ['Nome do Produto', 'Preço de Venda (R$)', 'Custo Variável (R$)', 'Quantidade Vendida (mês)']
        if all(col in df_upload.columns for col in required_columns):
            for _, row in df_upload.iterrows():
                product_data.append({
                    "name": row['Nome do Produto'],
                    "price": float(row['Preço de Venda (R$)']),
                    "cost": float(row['Custo Variável (R$)']),
                    "quantity": int(row['Quantidade Vendida (mês)'])
                })
            use_uploaded_data = True
            st.sidebar.success(f"✅ Planilha carregada com {len(product_data)} produtos!")
        else:
            st.sidebar.error("❌ Planilha não possui as colunas necessárias. Use o template fornecido.")
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao processar planilha: {str(e)}")

# Se não há upload válido, usar entrada manual
if not use_uploaded_data:
    # Inicializar com dados de exemplo se solicitado
    if st.session_state.get('example_data', False):
        example_products = [
            {"name": "Café Expresso", "price": 4.50, "cost": 1.20, "quantity": 300},
            {"name": "Cappuccino", "price": 6.00, "cost": 2.00, "quantity": 200},
            {"name": "Croissant", "price": 8.00, "cost": 3.50, "quantity": 150},
            {"name": "Pão de Açúcar", "price": 5.50, "cost": 2.20, "quantity": 180},
            {"name": "Sanduíche Natural", "price": 12.00, "cost": 6.00, "quantity": 100},
            {"name": "Suco Natural", "price": 7.00, "cost": 2.50, "quantity": 120}
        ]
        num_products = len(example_products)
        st.session_state.example_data = False
    else:
        example_products = []
        num_products = st.sidebar.number_input("Quantos produtos você deseja analisar?", min_value=1, max_value=20, value=3, step=1)

    # Coletar dados dos produtos
    for i in range(int(num_products)):
        with st.sidebar.expander(f"Produto {i+1}", expanded=i < 3):
            if example_products and i < len(example_products):
                default_name = example_products[i]["name"]
                default_price = example_products[i]["price"]
                default_cost = example_products[i]["cost"]
                default_quantity = example_products[i]["quantity"]
            else:
                default_name = f"Produto {i+1}"
                default_price = 10.0
                default_cost = 5.0
                default_quantity = 100
            
            name = st.text_input(f"Nome do Produto", value=default_name, key=f"name_{i}")
            price = st.number_input(f"Preço de Venda (R$)", min_value=0.0, value=default_price, format="%.2f", key=f"price_{i}")
            cost = st.number_input(f"Custo Variável (R$)", min_value=0.0, value=default_cost, format="%.2f", key=f"cost_{i}")
            quantity = st.number_input(f"Quantidade Vendida (mês)", min_value=0, value=default_quantity, step=1, key=f"quantity_{i}")
            
            product_data.append({
                "name": name, 
                "price": price, 
                "cost": cost, 
                "quantity": quantity
            })

# Seção para custos fixos
st.sidebar.subheader("🏢 Custos Fixos")
fixed_costs = st.sidebar.number_input("Custos Fixos Totais (R$/mês)", min_value=0.0, value=8000.0, format="%.2f")

# Inicializar analisador financeiro
if product_data:
    analyzer = FinancialAnalyzer(product_data, fixed_costs, tax_rate)
    cvp_analysis = analyzer.get_cost_volume_profit_analysis()
    contribution_analysis = analyzer.get_contribution_margin_analysis()

# Seção principal de resultados
if product_data and not contribution_analysis.empty:
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Receita Total", f"R$ {cvp_analysis['total_revenue']:,.2f}")
    
    with col2:
        # Margem de contribuição com percentual
        contribution_percent = cvp_analysis['contribution_margin_ratio']
        st.metric("📈 Margem de Contribuição", 
                 f"R$ {cvp_analysis['total_contribution']:,.2f}",
                 delta=f"{contribution_percent:.1f}%")
    
    with col3:
        st.metric("🏢 Custos Fixos", f"R$ {cvp_analysis['fixed_costs']:,.2f}")
    
    with col4:
        profit_percent = (cvp_analysis['net_profit']/cvp_analysis['total_revenue']*100) if cvp_analysis['total_revenue'] > 0 else 0
        st.metric("💵 Lucro Líquido", 
                 f"R$ {cvp_analysis['net_profit']:,.2f}",
                 delta=f"{profit_percent:.1f}%")

    st.markdown("---")

    # Análise por produto
    st.subheader("📊 Análise Detalhada por Produto")
    
    # Tabela de análise
    display_df = contribution_analysis[['name', 'price', 'cost', 'contribution_margin', 'contribution_margin_percent', 
                                      'quantity', 'total_contribution', 'revenue_participation', 'contribution_participation']].copy()
    display_df.columns = ['Produto', 'Preço (R$)', 'Custo Var. (R$)', 'Margem Contr. (R$)', 'Margem Contr. (%)', 
                         'Qtd Vendida', 'Contr. Total (R$)', 'Part. Receita (%)', 'Part. Contribuição (%)']
    
    # Formatação da tabela
    st.dataframe(
        display_df.style.format({
            'Preço (R$)': 'R$ {:.2f}',
            'Custo Var. (R$)': 'R$ {:.2f}',
            'Margem Contr. (R$)': 'R$ {:.2f}',
            'Margem Contr. (%)': '{:.1f}%',
            'Contr. Total (R$)': 'R$ {:.2f}',
            'Part. Receita (%)': '{:.1f}%',
            'Part. Contribuição (%)': '{:.1f}%'
        }),
        use_container_width=True
    )
    
    # Gráficos de análise
    col1, col2 = st.columns(2)
    
    with col1:
        fig_margin = px.bar(contribution_analysis, x='name', y='contribution_margin_percent', 
                           title='Margem de Contribuição por Produto (%)',
                           labels={'contribution_margin_percent': 'Margem (%)', 'name': 'Produto'},
                           color='contribution_margin_percent',
                           color_continuous_scale='RdYlGn')
        fig_margin.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_margin, use_container_width=True)
    
    with col2:
        fig_contribution = px.pie(contribution_analysis, values='total_contribution', names='name', 
                                 title='Participação na Margem de Contribuição Total')
        st.plotly_chart(fig_contribution, use_container_width=True)

    st.markdown("---")

    # Análise de ponto de equilíbrio com legendas e alertas
    st.subheader("⚖️ Análise Custo-Volume-Lucro")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🎯 Ponto de Equilíbrio**")
        st.metric("Unidades", f"{cvp_analysis['breakeven_units']:,.0f}")
        st.metric("Receita", f"R$ {cvp_analysis['breakeven_revenue']:,.2f}")
        
        # Legenda do ponto de equilíbrio
        current_units = sum([p["quantity"] for p in product_data])
        if current_units > cvp_analysis['breakeven_units']:
            st.markdown('<div class="success-card">✅ <strong>Situação:</strong> Acima do ponto de equilíbrio</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="danger-card">⚠️ <strong>Situação:</strong> Abaixo do ponto de equilíbrio</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("**🛡️ Margem de Segurança**")
        st.metric("Unidades", f"{cvp_analysis['safety_margin_units']:,.0f}")
        st.metric("Percentual", f"{cvp_analysis['safety_margin_percent']:.1f}%")
        
        # Legenda da margem de segurança
        if cvp_analysis['safety_margin_percent'] > 30:
            st.markdown('<div class="success-card">✅ <strong>Risco:</strong> Baixo - Margem confortável</div>', unsafe_allow_html=True)
        elif cvp_analysis['safety_margin_percent'] > 15:
            st.markdown('<div class="warning-card">⚠️ <strong>Risco:</strong> Moderado - Atenção necessária</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="danger-card">🚨 <strong>Risco:</strong> Alto - Situação crítica</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("**⚡ Alavancagem Operacional**")
        leverage_value = cvp_analysis['operating_leverage']
        leverage_display = f"{leverage_value:.2f}" if leverage_value != float('inf') else "∞"
        st.metric("Alavancagem", leverage_display)
        st.metric("Razão Margem Contr.", f"{cvp_analysis['contribution_margin_ratio']:.1f}%")
        
        # Legenda da alavancagem operacional
        if leverage_value < 2:
            st.markdown('<div class="success-card">✅ <strong>Sensibilidade:</strong> Baixa - Estável</div>', unsafe_allow_html=True)
        elif leverage_value < 5:
            st.markdown('<div class="warning-card">⚠️ <strong>Sensibilidade:</strong> Moderada</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="danger-card">🚨 <strong>Sensibilidade:</strong> Alta - Volátil</div>', unsafe_allow_html=True)

    # Gráfico de ponto de equilíbrio
    st.subheader("📈 Gráfico de Ponto de Equilíbrio")
    
    # Criar dados para o gráfico
    max_units = int(cvp_analysis['breakeven_units'] * 2) if cvp_analysis['breakeven_units'] > 0 else 1000
    units_range = np.linspace(0, max_units, 100)
    
    avg_price = cvp_analysis['weighted_avg_price']
    avg_variable_cost = avg_price - cvp_analysis['weighted_avg_contribution_margin']
    
    revenue_line = units_range * avg_price
    total_cost_line = fixed_costs + (units_range * avg_variable_cost)
    
    fig_breakeven = go.Figure()
    
    fig_breakeven.add_trace(go.Scatter(x=units_range, y=revenue_line, mode='lines', name='Receita Total', line=dict(color='green')))
    fig_breakeven.add_trace(go.Scatter(x=units_range, y=total_cost_line, mode='lines', name='Custo Total', line=dict(color='red')))
    fig_breakeven.add_trace(go.Scatter(x=[cvp_analysis['breakeven_units']], y=[cvp_analysis['breakeven_revenue']], 
                                      mode='markers', name='Ponto de Equilíbrio', marker=dict(size=12, color='blue')))
    
    fig_breakeven.update_layout(
        title='Análise de Ponto de Equilíbrio',
        xaxis_title='Quantidade (unidades)',
        yaxis_title='Valor (R$)',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_breakeven, use_container_width=True)

    st.markdown("---")

    # Otimização do mix de produtos
    st.subheader("🎯 Otimização do Mix de Produtos")
    
    optimization = analyzer.analyze_product_mix_optimization()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔥 Produtos com Maior Margem**")
        for product in optimization['high_margin_products']:
            st.success(f"**{product['name']}**: {product['contribution_margin_percent']:.1f}% de margem")
        
        st.info("**💡 Estratégias:**")
        st.write("• Promover mais estes produtos")
        st.write("• Aumentar o estoque")
        st.write("• Usar como âncora em combos")
    
    with col2:
        st.markdown("**⚠️ Produtos com Menor Margem**")
        for product in optimization['low_margin_products']:
            st.warning(f"**{product['name']}**: {product['contribution_margin_percent']:.1f}% de margem")
        
        st.info("**🔧 Ações Sugeridas:**")
        st.write("• Revisar custos ou preços")
        st.write("• Combinar com produtos de alta margem")
        st.write("• Avaliar descontinuação")
    
    with col3:
        st.markdown("**💰 Maiores Contribuidores**")
        for product in optimization['high_contribution_products']:
            st.success(f"**{product['name']}**: R$ {product['total_contribution']:.2f}")
        
        st.info("**📈 Oportunidades:**")
        st.write("• Manter foco nestes produtos")
        st.write("• Analisar capacidade de aumento")
        st.write("• Proteger participação de mercado")

    st.markdown("---")

    # Simulador de combos avançado
    st.subheader("🎁 Simulador Avançado de Combos")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Criar Novo Combo:**")
        combo_name = st.text_input("Nome do Combo", value="Combo Especial")
        
        selected_products = st.multiselect(
            "Selecione os produtos para o combo:",
            options=contribution_analysis['name'].tolist(),
            default=contribution_analysis['name'].tolist()[:2] if len(contribution_analysis) >= 2 else []
        )
        
        combo_discount = st.slider("Desconto do Combo (%)", 0, 50, 10)
        
        if st.button("🔍 Analisar Combo Avançado"):
            if selected_products:
                # Usar a quantidade do produto que mais vende como base
                combo_products = contribution_analysis[contribution_analysis['name'].isin(selected_products)]
                max_quantity = combo_products['quantity'].max()
                
                # Calcular impacto na margem total da empresa
                combo_original_price = combo_products['price'].sum()
                combo_discounted_price = combo_original_price * (1 - combo_discount/100)
                combo_total_cost = combo_products['cost'].sum()
                combo_margin = combo_discounted_price - combo_total_cost
                combo_margin_percent = (combo_margin / combo_discounted_price * 100) if combo_discounted_price > 0 else 0
                
                # Calcular contribuição do combo vs produtos individuais
                individual_contribution = combo_products['total_contribution'].sum()
                combo_contribution = combo_margin * max_quantity
                
                # Impacto na margem total da empresa
                new_total_contribution = cvp_analysis['total_contribution'] - individual_contribution + combo_contribution
                margin_impact = new_total_contribution - cvp_analysis['total_contribution']
                
                combo_analysis = {
                    'products': selected_products,
                    'original_price': combo_original_price,
                    'discounted_price': combo_discounted_price,
                    'total_cost': combo_total_cost,
                    'combo_margin': combo_margin,
                    'combo_margin_percent': combo_margin_percent,
                    'estimated_quantity': max_quantity,
                    'individual_contribution': individual_contribution,
                    'combo_contribution': combo_contribution,
                    'margin_impact': margin_impact,
                    'viability': 'Viável' if margin_impact > 0 else 'Não recomendado'
                }
                
                st.session_state.combo_analysis = combo_analysis
    
    with col2:
        if 'combo_analysis' in st.session_state and st.session_state.combo_analysis:
            combo = st.session_state.combo_analysis
            
            st.markdown("**📊 Análise Avançada do Combo:**")
            
            col2a, col2b = st.columns(2)
            with col2a:
                st.metric("Preço Original", f"R$ {combo['original_price']:.2f}")
                st.metric("Preço com Desconto", f"R$ {combo['discounted_price']:.2f}")
                st.metric("Quantidade Estimada", f"{combo['estimated_quantity']} unidades/mês")
            
            with col2b:
                st.metric("Margem do Combo", f"R$ {combo['combo_margin']:.2f}")
                st.metric("Margem do Combo (%)", f"{combo['combo_margin_percent']:.1f}%")
                st.metric("Impacto na Margem Total", f"R$ {combo['margin_impact']:+,.2f}")
            
            # Comparação detalhada
            st.markdown("**📈 Comparação Financeira:**")
            st.write(f"• Contribuição Individual: R$ {combo['individual_contribution']:,.2f}")
            st.write(f"• Contribuição do Combo: R$ {combo['combo_contribution']:,.2f}")
            st.write(f"• Diferença: R$ {combo['margin_impact']:+,.2f}")
            
            # Avaliação da viabilidade baseada no impacto total
            if combo['viability'] == 'Viável':
                st.markdown('<div class="success-card">✅ <strong>Combo Viável!</strong> Aumenta a margem total da empresa.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="danger-card">❌ <strong>Combo Não Recomendado!</strong> Reduz a margem total da empresa.</div>', unsafe_allow_html=True)

    # Simulador de mudança de preços com elasticidade
    st.markdown("---")
    st.subheader("💲 Simulador de Mudança de Preços com Elasticidade")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Simular Mudança de Preço:**")
        product_to_change = st.selectbox(
            "Selecione o produto:",
            options=contribution_analysis['name'].tolist()
        )
        
        current_price = contribution_analysis[contribution_analysis['name'] == product_to_change]['price'].iloc[0]
        current_quantity = contribution_analysis[contribution_analysis['name'] == product_to_change]['quantity'].iloc[0]
        
        new_price = st.number_input(
            f"Novo preço (atual: R$ {current_price:.2f})",
            min_value=0.0,
            value=current_price,
            format="%.2f"
        )
        
        # Estimativa de elasticidade
        price_change_percent = ((new_price - current_price) / current_price * 100) if current_price > 0 else 0
        
        st.markdown("**📊 Estimativa de Elasticidade:**")
        elasticity = st.slider(
            "Elasticidade da demanda (quanto % a quantidade muda para cada 1% de mudança no preço)",
            min_value=-3.0, max_value=0.0, value=-1.2, step=0.1,
            help="Valores negativos indicam que aumento de preço reduz quantidade"
        )
        
        # Calcular nova quantidade estimada
        quantity_change_percent = elasticity * price_change_percent
        new_quantity = max(0, current_quantity * (1 + quantity_change_percent/100))
        
        st.write(f"**Mudança de preço:** {price_change_percent:+.1f}%")
        st.write(f"**Mudança estimada na quantidade:** {quantity_change_percent:+.1f}%")
        st.write(f"**Nova quantidade estimada:** {new_quantity:.0f} unidades")
        
        if st.button("📊 Simular Impacto com Elasticidade"):
            # Simular com nova quantidade
            product_idx = contribution_analysis[contribution_analysis['name'] == product_to_change].index[0]
            
            # Criar dados simulados
            simulated_data = product_data.copy()
            for i, product in enumerate(simulated_data):
                if product['name'] == product_to_change:
                    simulated_data[i]['price'] = new_price
                    simulated_data[i]['quantity'] = int(new_quantity)
                    break
            
            # Analisar cenário simulado
            sim_analyzer = FinancialAnalyzer(simulated_data, fixed_costs)
            sim_cvp = sim_analyzer.get_cost_volume_profit_analysis()
            
            price_simulation = {
                'current_profit': cvp_analysis['net_profit'],
                'new_profit': sim_cvp['net_profit'],
                'profit_change': sim_cvp['net_profit'] - cvp_analysis['net_profit'],
                'current_revenue': cvp_analysis['total_revenue'],
                'new_revenue': sim_cvp['total_revenue'],
                'revenue_change': sim_cvp['total_revenue'] - cvp_analysis['total_revenue'],
                'current_contribution_ratio': cvp_analysis['contribution_margin_ratio'],
                'new_contribution_ratio': sim_cvp['contribution_margin_ratio'],
                'price_change_percent': price_change_percent,
                'quantity_change_percent': quantity_change_percent
            }
            
            st.session_state.price_simulation = price_simulation
    
    with col2:
        if 'price_simulation' in st.session_state and st.session_state.price_simulation:
            sim = st.session_state.price_simulation
            
            st.markdown("**📈 Impacto da Mudança com Elasticidade:**")
            
            col2a, col2b = st.columns(2)
            with col2a:
                st.metric("Lucro Atual", f"R$ {sim['current_profit']:,.2f}")
                st.metric("Novo Lucro", f"R$ {sim['new_profit']:,.2f}")
                st.metric("Mudança no Lucro", f"R$ {sim['profit_change']:+,.2f}")
            
            with col2b:
                st.metric("Receita Atual", f"R$ {sim['current_revenue']:,.2f}")
                st.metric("Nova Receita", f"R$ {sim['new_revenue']:,.2f}")
                st.metric("Mudança na Receita", f"R$ {sim['revenue_change']:+,.2f}")
            
            # Análise detalhada
            st.markdown("**🔍 Análise Detalhada:**")
            st.write(f"• Mudança no preço: {sim['price_change_percent']:+.1f}%")
            st.write(f"• Mudança na quantidade: {sim['quantity_change_percent']:+.1f}%")
            st.write(f"• Mudança na razão MC: {sim['new_contribution_ratio'] - sim['current_contribution_ratio']:+.1f} p.p.")
            
            # Recomendação
            if sim['profit_change'] > 0:
                st.markdown('<div class="success-card">✅ <strong>Mudança Recomendada!</strong> Aumenta a lucratividade considerando elasticidade.</div>', unsafe_allow_html=True)
            elif sim['profit_change'] == 0:
                st.markdown('<div class="info-card">➖ <strong>Mudança Neutra</strong> - Sem impacto significativo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-card">⚠️ <strong>Cuidado!</strong> Reduz a lucratividade considerando elasticidade.</div>', unsafe_allow_html=True)

    # Seção de download do relatório
    st.markdown("---")
    st.subheader("📄 Download do Relatório de Análise")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("📊 Gerar Relatório Completo", use_container_width=True):
            report_content = generate_report(analyzer, cvp_analysis, contribution_analysis)
            
            # Criar arquivo para download
            report_bytes = report_content.encode('utf-8')
            
            st.download_button(
                label="📥 Baixar Relatório (TXT)",
                data=report_bytes,
                file_name=f"relatorio_analise_cafeteria_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.success("✅ Relatório gerado com sucesso! Clique no botão acima para baixar.")

# Footer
st.markdown("---")
st.markdown("**💡 Desenvolvido para otimização de lucratividade de cafeterias** ☕")
st.markdown("*Use as análises para tomar decisões estratégicas baseadas em dados!*")



