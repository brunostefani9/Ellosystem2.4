import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ellosystem Open Bar", layout="wide")

st.sidebar.title("🍸 Ellosystem")

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Base de Produtos",
        "Marcas / Insumos",
        "Drinks",
        "Orçamentos",
        "Estoque"
    ]
)

# -------------------------
# BANCOS DE DADOS
# -------------------------

if "produtos_base" not in st.session_state:
    st.session_state.produtos_base = pd.DataFrame(
        columns=["Produto", "Categoria"]
    )

if "insumos" not in st.session_state:
    st.session_state.insumos = pd.DataFrame(
        columns=[
            "Produto",
            "Marca",
            "Embalagem",
            "Quantidade",
            "Unidade",
            "Preço",
            "Custo_unitario"
        ]
    )

if "receitas" not in st.session_state:
    st.session_state.receitas = pd.DataFrame(
        columns=[
            "Drink",
            "Ingrediente",
            "Quantidade",
            "Unidade"
        ]
    )

# -------------------------
# DASHBOARD
# -------------------------

if menu == "Dashboard":

    st.title("📊 Ellosystem")

    col1, col2, col3 = st.columns(3)

    col1.metric("Produtos base", len(st.session_state.produtos_base))
    col2.metric("Insumos cadastrados", len(st.session_state.insumos))
    col3.metric("Receitas cadastradas", len(st.session_state.receitas))

# -------------------------
# BASE DE PRODUTOS
# -------------------------

elif menu == "Base de Produtos":

    st.title("📦 Base de Produtos")

    tab1, tab2 = st.tabs(["Cadastrar", "Produtos cadastrados"])

    with tab1:

        with st.form("form_produto", clear_on_submit=True):

            produto = st.text_input("Nome do produto")

            categoria = st.selectbox(
                "Categoria",
                [
                    "Destilado",
                    "Licor",
                    "Fruta",
                    "Refrigerante",
                    "Xarope",
                    "Insumo"
                ]
            )

            submit = st.form_submit_button("Cadastrar produto")

            if submit:

                novo = pd.DataFrame(
                    [[produto, categoria]],
                    columns=["Produto", "Categoria"]
                )

                st.session_state.produtos_base = pd.concat(
                    [st.session_state.produtos_base, novo],
                    ignore_index=True
                )

                st.success("Produto cadastrado!")

    with tab2:

        st.data_editor(
            st.session_state.produtos_base,
            use_container_width=True
        )

# -------------------------
# MARCAS / INSUMOS
# -------------------------

elif menu == "Marcas / Insumos":

    st.title("🏷️ Banco de Insumos")

    tab1, tab2 = st.tabs(["Cadastrar insumo", "Lista de insumos"])

    with tab1:

        if not st.session_state.produtos_base.empty:

            with st.form("form_insumo", clear_on_submit=True):

                produto = st.selectbox(
                    "Produto",
                    st.session_state.produtos_base["Produto"]
                )

                marca = st.text_input("Marca")

                embalagem = st.selectbox(
                    "Embalagem",
                    ["Garrafa", "Kg", "Pacote", "Unidade"]
                )

                quantidade = st.number_input(
                    "Quantidade da embalagem",
                    min_value=0.0
                )

                unidade = st.selectbox(
                    "Unidade",
                    ["ml", "g", "unidade"]
                )

                preco = st.number_input(
                    "Preço da embalagem (R$)",
                    min_value=0.0
                )

                submit = st.form_submit_button("Cadastrar insumo")

                if submit:

                    custo = 0

                    if quantidade > 0:
                        custo = preco / quantidade

                    novo = pd.DataFrame(
                        [[
                            produto,
                            marca,
                            embalagem,
                            quantidade,
                            unidade,
                            preco,
                            custo
                        ]],
                        columns=st.session_state.insumos.columns
                    )

                    st.session_state.insumos = pd.concat(
                        [st.session_state.insumos, novo],
                        ignore_index=True
                    )

                    st.success("Insumo cadastrado!")

        else:

            st.warning("Cadastre produtos primeiro.")

    with tab2:

        st.data_editor(
            st.session_state.insumos,
            use_container_width=True
        )

# -------------------------
# DRINKS
# -------------------------

elif menu == "Drinks":

    st.title("🍸 Ficha Técnica dos Drinks")

    if "ingredientes_temp" not in st.session_state:
        st.session_state.ingredientes_temp = []

    tab1, tab2 = st.tabs(["Criar receita", "Receitas cadastradas"])

    with tab1:

        nome_drink = st.text_input("Nome do drink")

        if not st.session_state.produtos_base.empty:

            ingrediente = st.selectbox(
                "Ingrediente",
                st.session_state.produtos_base["Produto"]
            )

            quantidade = st.number_input(
                "Quantidade usada",
                min_value=0.0
            )

            unidade = st.selectbox(
                "Unidade",
                ["ml", "g", "unidade"]
            )

            if st.button("Adicionar ingrediente"):

                st.session_state.ingredientes_temp.append({
                    "Ingrediente": ingrediente,
                    "Quantidade": quantidade,
                    "Unidade": unidade
                })

        if st.session_state.ingredientes_temp:

            st.subheader("Ingredientes do drink")

            df_temp = pd.DataFrame(st.session_state.ingredientes_temp)

            st.table(df_temp)

        if st.button("Salvar receita"):

            for item in st.session_state.ingredientes_temp:

                novo = pd.DataFrame(
                    [[
                        nome_drink,
                        item["Ingrediente"],
                        item["Quantidade"],
                        item["Unidade"]
                    ]],
                    columns=st.session_state.receitas.columns
                )

                st.session_state.receitas = pd.concat(
                    [st.session_state.receitas, novo],
                    ignore_index=True
                )

            st.session_state.ingredientes_temp = []

            st.success("Receita salva!")

    with tab2:

        if not st.session_state.receitas.empty:

            drinks = st.session_state.receitas["Drink"].unique()

            for drink in drinks:

                with st.expander(drink):

                    df = st.session_state.receitas[
                        st.session_state.receitas["Drink"] == drink
                    ]

                    st.table(df[["Ingrediente", "Quantidade", "Unidade"]])

        else:

            st.info("Nenhuma receita cadastrada.")

# -------------------------
# ORÇAMENTOS
# -------------------------

elif menu == "Orçamentos":

    st.title("📋 Orçamento de Evento")

    pessoas = st.number_input("Número de pessoas", min_value=1)

    modo = st.radio(
        "Modo de cálculo",
        [
            "Drinks por pessoa no evento",
            "Drinks por pessoa por hora"
        ]
    )

    if modo == "Drinks por pessoa no evento":

        drinks_pessoa = st.number_input(
            "Drinks por pessoa",
            min_value=1,
            value=6
        )

        total_drinks = pessoas * drinks_pessoa

    else:

        horas = st.number_input(
            "Horas de evento",
            min_value=1
        )

        drinks_hora = st.number_input(
            "Drinks por pessoa por hora",
            min_value=1,
            value=3
        )

        total_drinks = pessoas * horas * drinks_hora

    st.divider()

    st.subheader("Resultado estimado")

    st.metric(
        "Total de drinks estimado",
        total_drinks
    )

    drinks_disponiveis = st.session_state.receitas["Drink"].unique()

    drinks = st.multiselect(
        "Drinks do evento",
        drinks_disponiveis
    )

# -------------------------
# ESTOQUE
# -------------------------

elif menu == "Estoque":

    st.title("📦 Controle de Estoque")

    if not st.session_state.insumos.empty:

        st.data_editor(
            st.session_state.insumos,
            use_container_width=True
        )

    else:

        st.info("Cadastre insumos primeiro.")