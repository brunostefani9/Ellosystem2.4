import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ellosystem Open Bar", layout="wide")

st.sidebar.title("🍸 Ellosystem")
aba = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Produtos", "Drinks", "Orçamento", "Estoque", "Financeiro"]
)

# ----------------------------
# Bancos de dados simples
# ----------------------------

if "produtos" not in st.session_state:
    st.session_state.produtos = pd.DataFrame(
        columns=["Produto", "Preço", "Unidade"]
    )

if "drinks" not in st.session_state:
    st.session_state.drinks = []

if "financeiro" not in st.session_state:
    st.session_state.financeiro = []

# ----------------------------
# DASHBOARD
# ----------------------------

if aba == "Dashboard":

    st.title("📊 Painel do Sistema")

    col1, col2, col3 = st.columns(3)

    col1.metric("Produtos cadastrados", len(st.session_state.produtos))
    col2.metric("Drinks cadastrados", len(st.session_state.drinks))
    col3.metric("Movimentações financeiras", len(st.session_state.financeiro))

# ----------------------------
# PRODUTOS
# ----------------------------

elif aba == "Produtos":

    st.title("📦 Cadastro de Produtos")

    nome = st.text_input("Nome do produto")
    preco = st.number_input("Preço", min_value=0.0)
    unidade = st.text_input("Unidade (ml, g, unidade, garrafa)")

    if st.button("Cadastrar produto"):

        novo = pd.DataFrame(
            [[nome, preco, unidade]],
            columns=["Produto", "Preço", "Unidade"]
        )

        st.session_state.produtos = pd.concat(
            [st.session_state.produtos, novo],
            ignore_index=True
        )

        st.success("Produto cadastrado!")

    if not st.session_state.produtos.empty:
        st.subheader("Produtos cadastrados")
        st.dataframe(st.session_state.produtos)

# ----------------------------
# DRINKS
# ----------------------------

elif aba == "Drinks":

    st.title("🍸 Cadastro de Drinks")

    nome_drink = st.text_input("Nome do drink")

    ingrediente = st.selectbox(
        "Ingrediente",
        st.session_state.produtos["Produto"]
        if not st.session_state.produtos.empty else []
    )

    quantidade = st.number_input("Quantidade usada")

    if st.button("Adicionar receita"):

        receita = {
            "Drink": nome_drink,
            "Ingrediente": ingrediente,
            "Quantidade": quantidade
        }

        st.session_state.drinks.append(receita)

        st.success("Ingrediente adicionado ao drink!")

    if st.session_state.drinks:
        st.subheader("Receitas cadastradas")
        st.table(pd.DataFrame(st.session_state.drinks))

# ----------------------------
# ORÇAMENTO
# ----------------------------

elif aba == "Orçamento":

    st.title("📋 Orçamento de Evento")

    pessoas = st.number_input("Número de pessoas", min_value=1)
    horas = st.number_input("Horas de evento", min_value=1)

    lista_drinks = list(
        set([d["Drink"] for d in st.session_state.drinks])
    )

    drinks_escolhidos = st.multiselect(
        "Drinks do evento",
        lista_drinks
    )

    if st.button("Calcular consumo estimado"):

        consumo_medio = 3
        total = pessoas * horas * consumo_medio

        st.subheader("Resultado")

        st.write("Pessoas:", pessoas)
        st.write("Horas:", horas)
        st.write("Drinks escolhidos:", drinks_escolhidos)
        st.write("Total estimado de drinks:", total)

# ----------------------------
# ESTOQUE
# ----------------------------

elif aba == "Estoque":

    st.title("📦 Controle de Estoque")

    if not st.session_state.produtos.empty:
        estoque = st.data_editor(st.session_state.produtos)
        st.session_state.produtos = estoque

# ----------------------------
# FINANCEIRO
# ----------------------------

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
        st.subheader("Histórico financeiro")
        st.table(pd.DataFrame(st.session_state.financeiro))