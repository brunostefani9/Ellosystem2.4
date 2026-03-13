import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema Open Bar", layout="wide")

st.sidebar.title("Navegação")
aba = st.sidebar.radio("Ir para:", ["Dashboard", "Fichas Técnicas", "Estoque", "Financeiro"])

# Banco inicial
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame({
        'Produto': ['Rum', 'Gin', 'Limão'],
        'Quantidade': [10, 5, 50],
        'Preço_Unit': [120.0, 150.0, 0.5]
    })

if 'receitas' not in st.session_state:
    st.session_state.receitas = []

if 'financeiro' not in st.session_state:
    st.session_state.financeiro = []

# DASHBOARD
if aba == "Dashboard":

    st.title("📊 Ellosystem - Painel de Controle")

    col1, col2, col3 = st.columns(3)

    col1.metric("Produtos em estoque", len(st.session_state.estoque))
    col2.metric("Receitas cadastradas", len(st.session_state.receitas))
    col3.metric("Movimentações financeiras", len(st.session_state.financeiro))

# FICHAS TECNICAS
elif aba == "Fichas Técnicas":

    st.title("🍸 Cadastro de Receitas")

    nome = st.text_input("Nome do Drink")
    ingrediente = st.text_input("Ingrediente")
    quantidade = st.number_input("Quantidade (ml ou g)", min_value=0)

    if st.button("Adicionar Receita"):

        receita = {
            "Drink": nome,
            "Ingrediente": ingrediente,
            "Quantidade": quantidade
        }

        st.session_state.receitas.append(receita)
        st.success("Receita cadastrada!")

    if st.session_state.receitas:
        st.write("Receitas cadastradas:")
        st.table(pd.DataFrame(st.session_state.receitas))

# ESTOQUE
elif aba == "Estoque":

    st.title("📦 Gestão de Estoque")

    st.session_state.estoque = st.data_editor(st.session_state.estoque)

# FINANCEIRO
elif aba == "Financeiro":

    st.title("💰 Controle Financeiro")

    entrada = st.number_input("Entrada (R$)", min_value=0.0)
    saida = st.number_input("Saída (R$)", min_value=0.0)

    if st.button("Registrar movimentação"):

        registro = {
            "Entrada": entrada,
            "Saída": saida
        }

        st.session_state.financeiro.append(registro)

        st.success("Movimentação registrada!")

    if st.session_state.financeiro:
        st.write("Histórico financeiro")
        st.table(pd.DataFrame(st.session_state.financeiro))