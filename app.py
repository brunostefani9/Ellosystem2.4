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

def criar_tabela(nome):

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {nome}(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    nome TEXT,
    quantidade REAL,
    preco REAL,
    uso REAL,
    rendimento REAL,
    custo REAL
    )
    """)

criar_tabela("precos_bebidas")
criar_tabela("precos_insumos")
criar_tabela("precos_artesanais")

cursor.execute("""
CREATE TABLE IF NOT EXISTS estoque(
produto TEXT,
marca TEXT,
quantidade REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS movimentacoes(
data TEXT,
produto TEXT,
marca TEXT,
tipo TEXT,
quantidade REAL,
status TEXT
)
""")

# Nova tabela para Receitas
cursor.execute("""
CREATE TABLE IF NOT EXISTS receitas(
id INTEGER PRIMARY KEY AUTOINCREMENT,
drink TEXT,
ingrediente TEXT,
quantidade REAL,
unidade TEXT
)
""")

conn.commit()

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("🍸 Ellosystem")

menu = st.sidebar.radio(
"Menu",
[
"Relatórios",
"Precificação",
"Estoque",
"Receitas",
"Orçamentos",
"Vendas"
]
)

# -------------------------
# FUNÇÃO DE PRECIFICAÇÃO
# -------------------------

def tela_precificacao(nome_tabela):

    tab1,tab2 = st.tabs(["Cadastrar","Lista"])

    with tab1:

        with st.form(f"form_{nome_tabela}",clear_on_submit=True):

            tipo = st.text_input(
                "Tipo do item",
                key=f"tipo_{nome_tabela}"
            )

            nome = st.text_input(
                "Nome / Marca",
                key=f"nome_{nome_tabela}"
            )

            quantidade = st.number_input(
                "Quantidade total (ml, g, un)",
                min_value=0.0,
                key=f"quant_{nome_tabela}"
            )

            preco = st.number_input(
                "Preço",
                min_value=0.0,
                key=f"preco_{nome_tabela}"
            )

            uso = st.number_input(
                "Quantidade usada no drink",
                min_value=0.0,
                key=f"uso_{nome_tabela}"
            )

            if st.form_submit_button("Cadastrar"):

                if uso == 0:
                    st.error("Uso não pode ser zero")
                else:

                    rendimento = quantidade / uso
                    custo = preco / rendimento

                    cursor.execute(f"""
                    INSERT INTO {nome_tabela}
                    VALUES(NULL,?,?,?,?,?,?,?)
                    """,(tipo,nome,quantidade,preco,uso,rendimento,custo))

                    conn.commit()

                    st.success("Item cadastrado!")

    with tab2:

        df = pd.read_sql(f"SELECT * FROM {nome_tabela}",conn)

        busca = st.text_input(
            "Pesquisar",
            key=f"busca_{nome_tabela}"
        )

        if busca:

            df = df[
                df["nome"].str.contains(busca,case=False) |
                df["tipo"].str.contains(busca,case=False)
            ]

        st.dataframe(df,use_container_width=True)

# -------------------------
# PRECIFICAÇÃO
# -------------------------

if menu == "Precificação":

    st.title("Precificação")

    aba1,aba2,aba3 = st.tabs(
        ["Bebidas","Frutas e Insumos","Artesanais"]
    )

    with aba1:

        tela_precificacao("precos_bebidas")

    with aba2:

        tela_precificacao("precos_insumos")

    with aba3:

        tela_precificacao("precos_artesanais")

# -------------------------
# ESTOQUE
# -------------------------

elif menu == "Estoque":

    st.title("Controle de Estoque")

    bebidas = pd.read_sql(
        "SELECT tipo FROM precos_bebidas",
        conn
    )

    tab1,tab2,tab3,tab4 = st.tabs(
        ["Entrada","Saída","Estoque físico","Registros"]
    )

# -------------------------
# ENTRADA
# -------------------------

    with tab1:

        with st.form("entrada_estoque",clear_on_submit=True):

            produto = st.selectbox(
                "Tipo",
                bebidas["tipo"].unique()
            )

            marca = st.text_input("Marca")

            qtd = st.number_input(
                "Quantidade",
                min_value=0.0
            )

            status = st.selectbox(
                "Status",
                ["Compra","Volta evento"]
            )

            if st.form_submit_button("Registrar entrada"):

                atual = pd.read_sql(
                "SELECT * FROM estoque WHERE produto=? AND marca=?",
                conn,
                params=(produto,marca)
                )

                if atual.empty:

                    cursor.execute(
                    "INSERT INTO estoque VALUES(?,?,?)",
                    (produto,marca,qtd)
                    )

                else:

                    nova = atual.iloc[0]["quantidade"] + qtd

                    cursor.execute("""
                    UPDATE estoque
                    SET quantidade=?
                    WHERE produto=? AND marca=?
                    """,(nova,produto,marca))

                cursor.execute("""
                INSERT INTO movimentacoes
                VALUES(?,?,?,?,?,?)
                """,
                (
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                produto,
                marca,
                "Entrada",
                qtd,
                status
                )
                )

                conn.commit()

                st.success("Entrada registrada!")

# -------------------------
# SAÍDA
# -------------------------

    with tab2:

        estoque = pd.read_sql("SELECT * FROM estoque",conn)

        if estoque.empty:

            st.info("Estoque vazio")

        else:

            with st.form("saida_estoque",clear_on_submit=True):

                produto = st.selectbox(
                    "Produto",
                    estoque["produto"].unique()
                )

                marca = st.text_input("Marca")

                qtd = st.number_input(
                    "Quantidade",
                    min_value=0.0
                )

                if st.form_submit_button("Registrar saída"):

                    atual = pd.read_sql(
                    "SELECT * FROM estoque WHERE produto=? AND marca=?",
                    conn,
                    params=(produto,marca)
                    )

                    if atual.empty:

                        st.error("Item não encontrado no estoque")

                    else:

                        nova = atual.iloc[0]["quantidade"] - qtd

                        if nova < 0:

                            st.error("Estoque insuficiente")

                        else:

                            cursor.execute("""
                            UPDATE estoque
                            SET quantidade=?
                            WHERE produto=? AND marca=?
                            """,(nova,produto,marca))

                            cursor.execute("""
                            INSERT INTO movimentacoes
                            VALUES(?,?,?,?,?,?)
                            """,
                            (
                            datetime.now().strftime("%Y-%m-%d %H:%M"),
                            produto,
                            marca,
                            "Saída",
                            qtd,
                            "Evento"
                            )
                            )

                            conn.commit()

                            st.success("Saída registrada!")

# -------------------------
# ESTOQUE FÍSICO
# -------------------------

    with tab3:

        df = pd.read_sql(
        "SELECT * FROM estoque ORDER BY produto",
        conn
        )

        busca = st.text_input("Pesquisar item")

        if busca:

            df = df[
            df["marca"].str.contains(busca,case=False)
            ]

        st.dataframe(df,use_container_width=True)

# -------------------------
# REGISTROS
# -------------------------

    with tab4:

        df = pd.read_sql(
        "SELECT * FROM movimentacoes ORDER BY data DESC",
        conn
        )

        st.dataframe(df,use_container_width=True)

# -------------------------
# OUTRAS ABAS
# -------------------------

elif menu == "Relatórios":

    st.title("Relatórios")
    st.info("Indicadores virão na próxima etapa")

elif menu == "Receitas":

    st.title("Receitas")

    # -------------------------
    # ABA DE RECEITAS
    # -------------------------
    aba1, aba2 = st.tabs(["Cadastro de Drinks", "Lista de Drinks"])

    with aba1:

        with st.form("form_receitas", clear_on_submit=True):

            drink = st.text_input("Nome do drink", key="nome_drink")
            ingrediente = st.text_input("Ingrediente", key="ingrediente")
            quantidade = st.number_input("Quantidade", min_value=0.0, key="qtd_ingrediente")
            unidade = st.selectbox("Unidade", ["ml","g","un","gota","fatia","guarnição"], key="unidade_ingrediente")

            if st.form_submit_button("Adicionar ingrediente"):

                if not drink or not ingrediente or quantidade <= 0:
                    st.error("Preencha todos os campos corretamente")
                else:
                    cursor.execute("""
                    INSERT INTO receitas(drink, ingrediente, quantidade, unidade)
                    VALUES(?,?,?,?)
                    """, (drink, ingrediente, quantidade, unidade))
                    conn.commit()
                    st.success("Ingrediente adicionado ao drink!")

    with aba2:

        df = pd.read_sql("SELECT * FROM receitas", conn)

        busca = st.text_input("Pesquisar drink", key="busca_drink")
        if busca:
            df = df[df["drink"].str.contains(busca, case=False)]

        # Botão de exclusão
        for index, row in df.iterrows():
            cols = st.columns([3,3,2,2,1])
            cols[0].write(row["drink"])
            cols[1].write(f"{row['ingrediente']} - {row['quantidade']} {row['unidade']}")
            if cols[4].button("🗑️", key=f"del_{row['id']}"):
                cursor.execute("DELETE FROM receitas WHERE id=?", (row["id"],))
                conn.commit()
                st.experimental_rerun()  # Atualiza a lista

elif menu == "Orçamentos":

    st.title("Orçamentos")
    st.info("Criação de eventos em breve")

elif menu == "Vendas":

    st.title("Vendas")
    st.info("Histórico de eventos em breve")