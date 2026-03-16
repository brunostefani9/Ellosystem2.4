import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Ellosystem", layout="wide")

# -------------------------
# DATABASE
# -------------------------

conn = sqlite3.connect("ellosystem.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS produtos(
nome TEXT,
tipo TEXT,
unidade TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS precos(
produto TEXT,
marca TEXT,
volume REAL,
preco REAL,
custo_unit REAL
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS receitas(
drink TEXT,
ingrediente TEXT,
quantidade REAL,
unidade TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS vendas(
evento TEXT,
valor REAL,
data TEXT
)""")

conn.commit()

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("🍸 Ellosystem")

menu = st.sidebar.radio(
"Menu",
[
"Relatórios",
"Estoque",
"Precificação",
"Receitas",
"Orçamentos",
"Vendas"
]
)

# -------------------------
# RELATÓRIOS
# -------------------------

if menu == "Relatórios":

    st.title("Relatórios")

    vendas = pd.read_sql("SELECT * FROM vendas", conn)

    if not vendas.empty:

        vendas["data"] = pd.to_datetime(vendas["data"])
        vendas["mes"] = vendas["data"].dt.to_period("M")

        vendas_mes = vendas.groupby("mes")["valor"].sum()

        media = vendas_mes.mean()

        mes_atual = datetime.now().strftime("%Y-%m")

        vendas_mes_atual = vendas[vendas["mes"] == mes_atual]["valor"].sum()

        eventos_mes = len(vendas[vendas["mes"] == mes_atual])

        meta = media

        perc = (vendas_mes_atual / meta) * 100 if meta > 0 else 0

        c1,c2,c3,c4 = st.columns(4)

        c1.metric("Vendas no mês", f"R$ {round(vendas_mes_atual,2)}")
        c2.metric("Eventos no mês", eventos_mes)
        c3.metric("Meta média", f"R$ {round(meta,2)}")
        c4.metric("% meta atingida", f"{round(perc,1)}%")

        st.subheader("Comparativo mês a mês")

        st.line_chart(vendas_mes)

    else:

        st.info("Sem dados de vendas ainda.")

# -------------------------
# ESTOQUE
# -------------------------

elif menu == "Estoque":

    st.title("Estoque")

    tab1,tab2 = st.tabs(["Cadastro de produtos","Lista"])

    with tab1:

        nome = st.text_input("Produto")
        tipo = st.text_input("Tipo")
        unidade = st.selectbox("Unidade",["ml","g","kg","un"])

        if st.button("Cadastrar"):

            cursor.execute(
            "INSERT INTO produtos VALUES (?,?,?)",
            (nome,tipo,unidade)
            )

            conn.commit()

            st.success("Produto cadastrado")

    with tab2:

        df = pd.read_sql("SELECT * FROM produtos", conn)

        st.dataframe(df)

# -------------------------
# PRECIFICAÇÃO
# -------------------------

elif menu == "Precificação":

    st.title("Precificação")

    produtos = pd.read_sql("SELECT * FROM produtos", conn)

    if produtos.empty:

        st.warning("Cadastre produtos primeiro.")

    else:

        produto = st.selectbox("Produto", produtos["nome"])

        marca = st.text_input("Marca")

        volume = st.number_input("Volume")

        preco = st.number_input("Preço de compra")

        if st.button("Cadastrar preço"):

            custo = preco / volume if volume > 0 else 0

            cursor.execute(
            "INSERT INTO precos VALUES (?,?,?,?,?)",
            (produto,marca,volume,preco,custo)
            )

            conn.commit()

            st.success("Preço cadastrado")

        st.subheader("Lista")

        df = pd.read_sql("SELECT * FROM precos", conn)

        if not df.empty:

            for categoria in df["produto"].unique():

                st.subheader(categoria)

                st.dataframe(df[df["produto"]==categoria])

# -------------------------
# RECEITAS
# -------------------------

elif menu == "Receitas":

    tab1,tab2 = st.tabs(["Criar receita","Visualizar"])

    with tab1:

        st.title("Nova receita")

        drink = st.text_input("Nome do drink")

        produtos = pd.read_sql("SELECT nome FROM produtos", conn)

        ingrediente = st.selectbox("Ingrediente", produtos)

        qtd = st.number_input("Quantidade")

        unidade = st.selectbox("Unidade",["ml","g","un","fatia","gota"])

        if st.button("Adicionar ingrediente"):

            cursor.execute(
            "INSERT INTO receitas VALUES (?,?,?,?)",
            (drink,ingrediente,qtd,unidade)
            )

            conn.commit()

            st.success("Ingrediente adicionado")

    with tab2:

        df = pd.read_sql("SELECT * FROM receitas", conn)

        for drink in df["drink"].unique():

            with st.expander(drink):

                st.dataframe(df[df["drink"]==drink])

# -------------------------
# ORÇAMENTOS
# -------------------------

elif menu == "Orçamentos":

    st.title("Orçamento de Evento")

    pessoas = st.number_input("Número de pessoas")

    horas = st.number_input("Horas de evento")

    drinks_pessoa = st.number_input("Drinks por pessoa",value=6)

    total_drinks = pessoas * drinks_pessoa

    st.metric("Total estimado de drinks", total_drinks)

    receitas = pd.read_sql("SELECT * FROM receitas", conn)

    drinks = receitas["drink"].unique()

    selecionados = st.multiselect("Selecionar drinks",drinks)

    if st.button("Calcular"):

        ingredientes = {}

        precos = pd.read_sql("SELECT * FROM precos", conn)

        custo_total = 0

        for drink in selecionados:

            receita = receitas[receitas["drink"]==drink]

            for _,row in receita.iterrows():

                ing = row["ingrediente"]

                qtd = row["quantidade"] * total_drinks

                ingredientes[ing] = ingredientes.get(ing,0)+qtd

                preco = precos[precos["produto"]==ing]

                if not preco.empty:

                    custo = preco.iloc[0]["custo_unit"]

                    custo_total += qtd * custo

        df = pd.DataFrame(
        ingredientes.items(),
        columns=["Ingrediente","Quantidade"]
        )

        st.subheader("Checklist")

        st.dataframe(df)

        st.metric("Custo total", f"R$ {round(custo_total,2)}")

# -------------------------
# VENDAS
# -------------------------

elif menu == "Vendas":

    tab1,tab2 = st.tabs(["Novo evento","Eventos realizados"])

    with tab1:

        evento = st.text_input("Nome do evento")

        valor = st.number_input("Valor de venda")

        if st.button("Registrar venda"):

            cursor.execute(
            "INSERT INTO vendas VALUES (?,?,?)",
            (evento,valor,str(datetime.now()))
            )

            conn.commit()

            st.success("Venda registrada")

    with tab2:

        df = pd.read_sql("SELECT * FROM vendas", conn)

        st.dataframe(df)