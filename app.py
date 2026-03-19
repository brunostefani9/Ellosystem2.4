import streamlit as st
import pandas as pd
import sqlite3

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

conn.commit()

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("🍸 Ellosystem")

menu = st.sidebar.radio(
    "Menu",
    ["Precificação"]
)

# -------------------------
# FUNÇÃO PADRÃO
# -------------------------

def tela_precificacao(nome_tabela):

    tab1, tab2 = st.tabs(["Cadastrar","Lista"])

    with tab1:

        with st.form(f"form_{nome_tabela}", clear_on_submit=True):

            tipo = st.text_input("Tipo do item", key=f"tipo_{nome_tabela}")
            nome = st.text_input("Nome / Marca", key=f"nome_{nome_tabela}")

            quantidade = st.number_input(
                "Quantidade total (ml, g, un)",
                min_value=0.0,
                format="%.2f",
                key=f"quant_{nome_tabela}"
            )

            preco = st.number_input(
                "Preço (R$)",
                min_value=0.0,
                format="%.2f",
                key=f"preco_{nome_tabela}"
            )

            uso = st.number_input(
                "Quantidade usada no drink",
                min_value=0.0,
                format="%.2f",
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

        df = pd.read_sql(f"SELECT * FROM {nome_tabela}", conn)

        busca = st.text_input("Pesquisar", key=f"busca_{nome_tabela}")

        if busca:
            df = df[
                df["nome"].str.contains(busca, case=False) |
                df["tipo"].str.contains(busca, case=False)
            ]

        df["preco"] = df["preco"].map(lambda x: f"R$ {x:.2f}")
        df["custo"] = df["custo"].map(lambda x: f"R$ {x:.2f}")

        st.dataframe(df, use_container_width=True)

        # 🗑 EXCLUIR
        if not df.empty:
            item = st.selectbox("Excluir item", df["id"], key=f"del_{nome_tabela}")

            if st.button("🗑 Excluir selecionado", key=f"btn_{nome_tabela}"):
                cursor.execute(f"DELETE FROM {nome_tabela} WHERE id = ?", (item,))
                conn.commit()
                st.rerun()

# -------------------------
# INSUMOS (FRUTAS)
# -------------------------

def tela_insumos():

    tab1, tab2 = st.tabs(["Cadastrar","Lista"])

    with tab1:

        with st.form("form_insumos", clear_on_submit=True):

            tipo = st.text_input("Tipo do item", key="tipo_insumos")
            nome = st.text_input("Nome / Marca", key="nome_insumos")

            quantidade = st.number_input(
                "Quantidade total",
                min_value=0.0,
                format="%.2f",
                key="quant_insumos"
            )

            unidade = st.selectbox(
                "Unidade de compra",
                ["kg","g","un","maço"],
                key="unidade_insumos"
            )

            # mensagens inteligentes
            if unidade == "kg":
                st.info("Cálculo feito automaticamente por gramas (g)")

            elif unidade == "maço":
                st.info("Maço será tratado como unidade (cálculo simples)")

            preco = st.number_input(
                "Preço (R$)",
                min_value=0.0,
                format="%.2f",
                key="preco_insumos"
            )

            uso = st.number_input(
                "Quantidade usada no drink",
                min_value=0.0,
                format="%.2f",
                key="uso_insumos"
            )

            if st.form_submit_button("Cadastrar"):

                if quantidade <= 0 or preco <= 0 or uso <= 0:
                    st.error("Preencha valores válidos")
                else:

                    if unidade == "kg":
                        quantidade_g = quantidade * 1000
                        custo_unitario = preco / quantidade_g
                        custo = round(custo_unitario * uso, 2)

                    elif unidade == "maço":
                        custo_unitario = preco / quantidade
                        custo = round(custo_unitario * uso, 2)

                    else:
                        custo_unitario = preco / quantidade
                        custo = round(custo_unitario * uso, 2)

                    rendimento = round(quantidade / uso, 2)

                    nome_final = f"{nome} ({unidade})"

                    cursor.execute("""
                    INSERT INTO precos_insumos
                    VALUES(NULL,?,?,?,?,?,?,?)
                    """,(tipo,nome_final,quantidade,preco,uso,rendimento,custo))

                    conn.commit()

                    st.success(f"{nome} cadastrado! Custo: R$ {custo:.2f}")

    with tab2:

        df = pd.read_sql("SELECT * FROM precos_insumos", conn)

        busca = st.text_input("Pesquisar", key="busca_insumos")

        if busca:
            df = df[
                df["nome"].fillna("").str.contains(busca, case=False) |
                df["tipo"].fillna("").str.contains(busca, case=False)
            ]

        df["preco"] = df["preco"].map(lambda x: f"R$ {x:.2f}")
        df["custo"] = df["custo"].map(lambda x: f"R$ {x:.2f}")

        st.dataframe(df, use_container_width=True)

        # 🗑 EXCLUIR
        if not df.empty:
            item = st.selectbox("Excluir item", df["id"], key="del_insumos")

            if st.button("🗑 Excluir selecionado", key="btn_insumos"):
                cursor.execute("DELETE FROM precos_insumos WHERE id = ?", (item,))
                conn.commit()
                st.rerun()

# -------------------------
# TELA PRINCIPAL
# -------------------------

if menu == "Precificação":

    st.title("Precificação")

    aba1, aba2, aba3 = st.tabs(
        ["Bebidas","Frutas e Insumos","Artesanais"]
    )

    with aba1:
        tela_precificacao("precos_bebidas")

    with aba2:
        tela_insumos()

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

    # controle de estado
    if "ingredientes_temp" not in st.session_state:
        st.session_state["ingredientes_temp"] = []

    if "drink_nome" not in st.session_state:
        st.session_state["drink_nome"] = ""

    if "msg" not in st.session_state:
        st.session_state["msg"] = ""

    # mostra mensagem (se existir)
    if st.session_state["msg"]:
        st.success(st.session_state["msg"])
        st.session_state["msg"] = ""

    aba1, aba2 = st.tabs(["Cadastro de Drinks", "Lista de Drinks"])

    # =========================
    # ABA 1 - CADASTRO
    # =========================
    with aba1:

        drink = st.text_input("Nome do drink", value=st.session_state["drink_nome"])

        col1, col2, col3, col4 = st.columns(4)

        ingrediente = col1.text_input("Ingrediente")
        quantidade = col2.number_input("Quantidade", min_value=0.0)
        unidade = col3.selectbox("Unidade", ["ml","g","un","gota","fatia","guarnição"])

        if col4.button("➕ Adicionar"):

            if drink and ingrediente and quantidade > 0:

                st.session_state["drink_nome"] = drink

                st.session_state["ingredientes_temp"].append({
                    "ingrediente": ingrediente,
                    "quantidade": quantidade,
                    "unidade": unidade
                })

                st.session_state["msg"] = "Ingrediente adicionado!"

                st.rerun()

            else:
                st.warning("Preencha tudo corretamente")

        if st.button("💾 Salvar Drink"):

            if not st.session_state["drink_nome"]:
                st.error("Digite o nome do drink")

            elif not st.session_state["ingredientes_temp"]:
                st.error("Adicione pelo menos um ingrediente")

            else:

                for item in st.session_state["ingredientes_temp"]:
                    cursor.execute("""
                    INSERT INTO receitas(drink, ingrediente, quantidade, unidade)
                    VALUES(?,?,?,?)
                    """, (
                        st.session_state["drink_nome"],
                        item["ingrediente"],
                        item["quantidade"],
                        item["unidade"]
                    ))

                conn.commit()

                st.session_state["msg"] = "🍹 Drink cadastrado com sucesso!"

                # limpa tudo
                st.session_state["ingredientes_temp"] = []
                st.session_state["drink_nome"] = ""

                st.rerun()

    # =========================
    # ABA 2 - LISTA
    # =========================
    with aba2:

        df = pd.read_sql("SELECT * FROM receitas", conn)

        if df.empty:
            st.info("Nenhum drink cadastrado")

        else:

            drinks = df["drink"].unique()

            for drink in drinks:

                receita = df[df["drink"] == drink]

                custo_total = 0

                col1, col2 = st.columns([5,1])

                with col1:
                    st.markdown(f"### 🍹 {drink}")

                    for _, row in receita.iterrows():

                        ingrediente = row["ingrediente"]
                        quantidade = row["quantidade"]
                        unidade = row["unidade"]

                        custo_unitario = 0

                        for tabela in ["precos_bebidas","precos_insumos","precos_artesanais"]:

                            result = pd.read_sql(f"""
                            SELECT custo FROM {tabela}
                            WHERE nome=?
                            """, conn, params=(ingrediente,))

                            if not result.empty:
                                custo_unitario = result.iloc[0]["custo"]
                                break

                        custo_total += custo_unitario * quantidade

                        st.write(f"- {ingrediente} ({quantidade} {unidade})")

                with col2:
                    st.markdown(f"### 💰\nR$ {custo_total:.2f}")

                    if st.button("🗑️", key=f"del_{drink}"):
                        cursor.execute("DELETE FROM receitas WHERE drink=?", (drink,))
                        conn.commit()
                        st.rerun()

                st.divider()

elif menu == "Orçamentos":

    st.title("Orçamentos")
    st.info("Criação de eventos em breve")

elif menu == "Vendas":

    st.title("Vendas")
    st.info("Histórico de eventos em breve")