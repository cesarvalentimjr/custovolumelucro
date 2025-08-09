import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from financial_analysis import FinancialAnalyzer

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
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("☕ Análise de Precificação e Lucratividade da Cafeteria")
st.markdown("**Sistema completo para otimização de lucratividade e análise de combos**")
st.markdown("---")

# Sidebar para entrada de dados
st.sidebar.image(
    "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPOSITORIO/refs/heads/main/dicelestelogo.jpg",
    use_container_width=True
)
st.sidebar.header("📊 Configurações e Dados de Entrada")

# Seção para dados de produtos
st.sidebar.subheader("🍰 Dados dos Produtos")

# Opção para carregar dados de exemplo
if st.sidebar.button("📋 Carregar Dados de Exemplo"):
    st.session_state.example_data = True

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
product_data = []
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
    analyzer = FinancialAnalyzer(product_data, fixed_costs)
    cvp_analysis = analyzer.get_cost_volume_profit_analysis()
    contribution_analysis = analyzer.get_contribution_margin_analysis()

# Seção principal de resultados
if product_data and not contribution_analysis.empty:
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Receita Total", f"R$ {cvp_analysis['total_revenue']:,.2f}")
    
    with col2:
        st.metric("📈 Margem de Contribuição", f"R$ {cvp_analysis['total_contribution']:,.2f}")
    
    with col3:
        st.metric("🏢 Custos Fixos", f"R$ {cvp_analysis['fixed_costs']:,.2f}")
    
    with col4:
        profit_color = "normal" if cvp_analysis['net_profit'] >= 0 else "inverse"
        st.metric("💵 Lucro Líquido", f"R$ {cvp_analysis['net_profit']:,.2f}", 
                 delta=f"{(cvp_analysis['net_profit']/cvp_analysis['total_revenue']*100):.1f}%" if cvp_analysis['total_revenue'] > 0 else "0%")

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

    # Análise de ponto de equilíbrio
    st.subheader("⚖️ Análise Custo-Volume-Lucro")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🎯 Ponto de Equilíbrio**")
        st.metric("Unidades", f"{cvp_analysis['breakeven_units']:,.0f}")
        st.metric("Receita", f"R$ {cvp_analysis['breakeven_revenue']:,.2f}")
    
    with col2:
        st.markdown("**🛡️ Margem de Segurança**")
        safety_color = "normal" if cvp_analysis['safety_margin_percent'] > 20 else "inverse"
        st.metric("Unidades", f"{cvp_analysis['safety_margin_units']:,.0f}")
        st.metric("Percentual", f"{cvp_analysis['safety_margin_percent']:.1f}%")
    
    with col3:
        st.markdown("**⚡ Alavancagem Operacional**")
        leverage_value = cvp_analysis['operating_leverage']
        leverage_display = f"{leverage_value:.2f}" if leverage_value != float('inf') else "∞"
        st.metric("Alavancagem", leverage_display)
        st.metric("Razão Margem Contr.", f"{cvp_analysis['contribution_margin_ratio']:.1f}%")

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
        
        if st.button("🔍 Analisar Combo"):
            if selected_products:
                combo_analysis = analyzer.calculate_combo_analysis(selected_products, combo_discount)
                st.session_state.combo_analysis = combo_analysis
    
    with col2:
        if 'combo_analysis' in st.session_state and st.session_state.combo_analysis:
            combo = st.session_state.combo_analysis
            
            if 'error' not in combo:
                st.markdown("**📊 Análise do Combo:**")
                
                col2a, col2b = st.columns(2)
                with col2a:
                    st.metric("Preço Original", f"R$ {combo['original_price']:.2f}")
                    st.metric("Preço com Desconto", f"R$ {combo['discounted_price']:.2f}")
                
                with col2b:
                    st.metric("Margem do Combo", f"R$ {combo['combo_margin']:.2f}")
                    st.metric("Margem do Combo (%)", f"{combo['combo_margin_percent']:.1f}%")
                
                # Comparação com margem individual
                st.metric("Impacto na Margem", f"{combo['margin_impact']:+.1f} p.p.", 
                         delta=f"vs {combo['avg_individual_margin_percent']:.1f}% individual")
                
                # Avaliação da viabilidade
                if combo['viability'] == 'Viável':
                    st.success(f"✅ **{combo['viability']}** - Combo recomendado!")
                elif combo['viability'] == 'Revisar':
                    st.warning(f"⚠️ **{combo['viability']}** - Considere ajustar o desconto.")
                else:
                    st.error(f"❌ **{combo['viability']}** - Margem muito baixa.")
            else:
                st.error(combo['error'])

    # Simulador de mudança de preços
    st.markdown("---")
    st.subheader("💲 Simulador de Mudança de Preços")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Simular Mudança de Preço:**")
        product_to_change = st.selectbox(
            "Selecione o produto:",
            options=contribution_analysis['name'].tolist()
        )
        
        current_price = contribution_analysis[contribution_analysis['name'] == product_to_change]['price'].iloc[0]
        new_price = st.number_input(
            f"Novo preço (atual: R$ {current_price:.2f})",
            min_value=0.0,
            value=current_price,
            format="%.2f"
        )
        
        if st.button("📊 Simular Impacto"):
            price_simulation = analyzer.simulate_price_changes(product_to_change, new_price)
            st.session_state.price_simulation = price_simulation
    
    with col2:
        if 'price_simulation' in st.session_state and st.session_state.price_simulation:
            sim = st.session_state.price_simulation
            
            if 'error' not in sim:
                st.markdown("**📈 Impacto da Mudança:**")
                
                col2a, col2b = st.columns(2)
                with col2a:
                    st.metric("Lucro Atual", f"R$ {sim['current_profit']:,.2f}")
                    st.metric("Novo Lucro", f"R$ {sim['new_profit']:,.2f}")
                
                with col2b:
                    profit_change = sim['profit_change']
                    change_color = "normal" if profit_change >= 0 else "inverse"
                    st.metric("Mudança no Lucro", f"R$ {profit_change:+,.2f}")
                    
                    ratio_change = sim['new_contribution_ratio'] - sim['current_contribution_ratio']
                    st.metric("Mudança na Razão MC", f"{ratio_change:+.1f} p.p.")
                
                # Recomendação
                if profit_change > 0:
                    st.success("✅ Mudança recomendada - Aumenta a lucratividade!")
                elif profit_change == 0:
                    st.info("➖ Mudança neutra - Sem impacto significativo.")
                else:
                    st.warning("⚠️ Cuidado - Reduz a lucratividade!")

# Footer
st.markdown("---")
st.markdown("**💡 Desenvolvido para otimização de lucratividade de cafeterias** ☕")
st.markdown("*Use as análises para tomar decisões estratégicas baseadas em dados!*")

