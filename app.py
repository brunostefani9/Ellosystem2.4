import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Sistema Open Bar", layout="wide")

st.sidebar.title("Navegação")
aba = st.sidebar.radio("Ir para:", ["Dashboard", "Fichas Técnicas", "Estoque", "Financeiro"])

# Banco de dados inicial (simulado)
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame({
        'Produto': ['Rum', 'Gin', 'Limão'],
        'Quantidade': [10, 5, 50],
        'Preço_Unit': [120.0, 150.0, 0.5]
    })

# --- ABA DASHBOARD ---
if aba == "Dashboard":
    st.title("📊 Painel de Controle")
    st.write("Visão geral do seu faturamento e próximos eventos.")

# --- ABA FICHAS TÉCNICAS ---
elif aba == "Fichas Técnicas":
    st.title("🍸 Cadastro de Receitas")
    nome_drink = st.text_input("Nome do Drink")
    st.write("Adicione ingredientes para calcular o custo automático.")

# --- ABA ESTOQUE ---
elif aba == "Estoque":
    st.title("📦 Gestão de Estoque")
    st.write("Edite seu estoque atual:")
    st.session_state.estoque = st.data_editor(st.session_state.estoque)

# --- ABA FINANCEIRO ---
elif aba == "Financeiro":
    st.title("💰 Controle Financeiro")
    st.write("Lançamentos de Entradas e Saídas.")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Valor de Entrada (R$)", min_value=0.0)
    with col2:
        st.number_input("Valor de Saída (R$)", min_value=0.0)