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

# -------------------------
# FUNÇÃO DE PRECIFICAÇÃO
# -------------------------

def tela_precificacao(nome_tabela):

    tab1,tab2 = st.tabs(["Cadastrar","Lista"])

    with tab1:

        with st.form(f"form_{nome_tabela}",clear_on_submit=True):

            tipo = st.text_input("Tipo do item", key=f"tipo_{nome_tabela}")

            nome = st.text_input("Nome / Marca", key=f"nome_{nome_tabela}")

            quantidade = st.number_input(
                "Quantidade total (ml, g, un)",
                min_value=0.0,
                format="%.2f",
                key=f"quant_{nome_tabela}"
            )

            preco = st.number_input(
                "Preço",
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

        df = pd.read_sql(f"SELECT * FROM {nome_tabela}",conn)

        busca = st.text_input("Pesquisar", key=f"busca_{nome_tabela}")

        if busca:
            df = df[
                df["nome"].str.contains(busca,case=False) |
                df["tipo"].str.contains(busca,case=False)
            ]

        st.dataframe(df,use_container_width=True)

        # 🗑 excluir
        if not df.empty:
            item = st.selectbox("Excluir item", df["id"], key=f"del_{nome_tabela}")

            if st.button("🗑 Excluir selecionado", key=f"btn_{nome_tabela}"):
                cursor.execute(f"DELETE FROM {nome_tabela} WHERE id = ?", (item,))
                conn.commit()
                st.rerun()

# -------------------------
# FUNÇÃO INSUMOS (FRUTAS)
# -------------------------

def tela_insumos():

    tab1,tab2 = st.tabs(["Cadastrar","Lista"])

    with tab1:

        with st.form("form_insumos",clear_on_submit=True):

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

            if unidade == "kg":
                st.info("Cálculo convertido para ml (suco)")

            elif unidade == "maço":
                st.info("Maço tratado como unidade (cálculo simples)")

            # 🔥 NOVO CAMPO
            rendimento_ml = st.number_input(
                "Rendimento em ml (suco total)",
                min_value=0.0,
                format="%.2f",
                key="rendimento_ml"
            )

            preco = st.number_input(
                "Preço",
                min_value=0.0,
                format="%.2f",
                key="preco_insumos"
            )

            uso = st.number_input(
                "Quantidade usada no drink (ml ou unidade)",
                min_value=0.0,
                format="%.2f",
                key="uso_insumos"
            )

            if st.form_submit_button("Cadastrar"):

                if quantidade <= 0 or preco <= 0 or uso <= 0:
                    st.error("Preencha valores válidos")
                else:

                    if unidade == "kg":

                        if rendimento_ml <= 0:
                            st.error("Informe o rendimento em ml")
                        else:
                            custo_por_ml = preco / rendimento_ml
                            custo = round(custo_por_ml * uso, 2)
                            rendimento = round(rendimento_ml / uso, 2)

                    else:
                        custo_unitario = preco / quantidade
                        custo = round(custo_unitario * uso, 2)
                        rendimento = round(quantidade / uso, 2)

                    nome_final = f"{nome}"

                    cursor.execute("""
                    INSERT INTO precos_insumos
                    VALUES(NULL,?,?,?,?,?,?,?)
                    """,(tipo,nome_final,quantidade,preco,uso,rendimento,custo))

                    conn.commit()

                    st.success(f"Custo por uso: R$ {custo:.2f}")

    with tab2:

        df = pd.read_sql("SELECT * FROM precos_insumos",conn)

        busca = st.text_input("Pesquisar", key="busca_insumos")

        if busca:
            df = df[
                df["nome"].fillna("").str.contains(busca,case=False) |
                df["tipo"].fillna("").str.contains(busca,case=False)
            ]

        st.dataframe(df,use_container_width=True)

        if not df.empty:
            item = st.selectbox("Excluir item", df["id"], key="del_insumos")

            if st.button("🗑 Excluir selecionado", key="btn_insumos"):
                cursor.execute("DELETE FROM precos_insumos WHERE id = ?", (item,))
                conn.commit()
                st.rerun()

# -------------------------
# BLOCO DE PRECIFICAÇÃO
# -------------------------

if menu == "Precificação":

    st.title("Precificação")

    aba1,aba2,aba3 = st.tabs(
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

    st.title("Orçamento de Evento")

    mapa_bebidas = {
        "rum": "rum",
        "vodka": "vodka",
        "gin": "gin",
        "whisky": "whisky",
        "whiskey": "whisky",
        "cachaça": "cachaça",
        "tequila": "tequila",
        "aperol": "aperol",
        "campari": "campari",
        "espumante": "espumante",
        "vinho": "vinho"
    }

    def definir_unidade(item, qtd):
        item_lower = item.lower()

        if any(x in item_lower for x in ["suco", "agua", "xarope"]):
            if qtd >= 1000:
                return round(qtd / 1000, 2), "L"
            else:
                return round(qtd, 2), "ml"

        elif any(x in item_lower for x in ["acucar", "hortela", "limao", "limão"]):
            if qtd >= 1000:
                return round(qtd / 1000, 2), "kg"
            else:
                return round(qtd, 2), "g"

        else:
            return round(qtd, 2), "un"

    def normalizar_nome(nome):
        return nome.strip().lower()

    # =========================
    # CONFIG EVENTO
    # =========================
    st.subheader("Configuração do Evento")

    col1, col2, col3 = st.columns(3)

    convidados = col1.number_input("Convidados", min_value=1, value=50)
    horas = col2.number_input("Horas de evento", min_value=1, value=4)
    drinks_por_hora = col3.number_input("Drinks por pessoa/hora", min_value=0.5, value=2.0)

    total_drinks = convidados * horas * drinks_por_hora
    st.info(f"Total estimado de drinks: {int(total_drinks)}")

    # =========================
    # RECEITAS
    # =========================
    df_receitas = pd.read_sql("SELECT * FROM receitas", conn)

    if df_receitas.empty:
        st.warning("Cadastre receitas primeiro")

    else:

        drinks = df_receitas["drink"].unique()
        selecao = st.multiselect("Selecione os drinks", drinks)

        if selecao:

            st.subheader("Peso de Consumo")

            pesos = {}
            total_peso = 0

            for drink in selecao:
                peso = st.number_input(drink, min_value=1, value=1, key=f"peso_{drink}")
                pesos[drink] = peso
                total_peso += peso

            # =========================
            # CALCULO INGREDIENTES
            # =========================
            ingredientes_totais = {}

            for drink in selecao:

                proporcao = pesos[drink] / total_peso
                qtd_drinks = total_drinks * proporcao

                receita = df_receitas[df_receitas["drink"] == drink]

                for _, row in receita.iterrows():

                    ingrediente = normalizar_nome(row["ingrediente"])
                    qtd = row["quantidade"]

                    total_ingrediente = qtd * qtd_drinks

                    if ingrediente in ingredientes_totais:
                        ingredientes_totais[ingrediente] += total_ingrediente
                    else:
                        ingredientes_totais[ingrediente] = total_ingrediente

            # =========================
            # CARREGAR DADOS
            # =========================
            df_bebidas = pd.read_sql("SELECT * FROM precos_bebidas", conn)
            df_insumos = pd.read_sql("SELECT * FROM precos_insumos", conn)

            ingredientes_bebidas = {}
            ingredientes_insumos = {}

            for item, qtd in ingredientes_totais.items():

                tipo_encontrado = None

                for chave in mapa_bebidas:
                    if chave in item:
                        tipo_encontrado = mapa_bebidas[chave]
                        break

                if tipo_encontrado:
                    ingredientes_bebidas[item] = {"qtd": qtd, "tipo": tipo_encontrado}
                else:
                    ingredientes_insumos[item] = qtd

            # =========================
            # ESCOLHA BEBIDAS
            # =========================
            st.subheader("🍸 Escolha das Bebidas")

            escolhas_marcas = {}

            for item, dados in ingredientes_bebidas.items():

                tipo = dados["tipo"]

                opcoes = df_bebidas[
                    df_bebidas["tipo"].str.lower().str.contains(tipo)
                ]

                if opcoes.empty:
                    opcoes = df_bebidas

                escolha = st.selectbox(
                    f"{item}",
                    opcoes["nome"],
                    key=f"marca_{item}"
                )

                escolhas_marcas[item] = escolha

            # =========================
            # BEBIDAS
            # =========================
            st.subheader("🛒 Bebidas")

            custo_bebidas = 0

            for item, dados in ingredientes_bebidas.items():

                qtd_ml = dados["qtd"]
                marca = escolhas_marcas[item]

                result = df_bebidas[df_bebidas["nome"] == marca]

                if not result.empty:

                    preco = result.iloc[0]["preco"]
                    volume = result.iloc[0]["quantidade"]

                    if volume > 0:

                        qtd_real = qtd_ml / volume

                        qtd_garrafas = int(qtd_real)
                        if qtd_real > qtd_garrafas:
                            qtd_garrafas += 1

                        custo_item = qtd_garrafas * preco
                        custo_bebidas += custo_item

                        valor = f"R$ {custo_item:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                        st.write(f"✔ {marca} → {qtd_garrafas} garrafas | 💰 {valor}")

            subtotal_bebidas = f"R$ {custo_bebidas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f"### 💰 Subtotal Bebidas: {subtotal_bebidas}")

            # =========================
            # INSUMOS (100% CORRIGIDO)
            # =========================
            st.subheader("🍋 Insumos")

            custo_insumos = 0

            for item, qtd in ingredientes_insumos.items():

                qtd_exibicao, unidade = definir_unidade(item, qtd)

                encontrado = None

                for _, row in df_insumos.iterrows():
                    if row["nome"].strip().lower() == item:
                        encontrado = row
                        break

                if encontrado is not None:

                    preco = encontrado["preco"]
                    quantidade_base = encontrado["quantidade"]

                    # 🔥 CONVERSÃO AUTOMÁTICA
                    if any(x in item for x in ["limao", "limão", "acucar", "hortela"]):
                        if quantidade_base <= 10:
                            quantidade_base *= 1000

                    if any(x in item for x in ["agua", "xarope"]):
                        if quantidade_base <= 10:
                            quantidade_base *= 1000

                    if quantidade_base > 0:

                        custo_unitario = preco / quantidade_base
                        custo_item = qtd * custo_unitario
                        custo_insumos += custo_item

                        valor = f"R$ {custo_item:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                        st.write(f"✔ {item.capitalize()} → {qtd_exibicao} {unidade} | 💰 {valor}")

                else:
                    st.write(f"✔ {item.capitalize()} → {qtd_exibicao} {unidade}")

            subtotal_insumos = f"R$ {custo_insumos:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f"### 💰 Subtotal Insumos: {subtotal_insumos}")

            # =========================
            # TOTAL FINAL
            # =========================
            st.divider()

            custo_total = custo_bebidas + custo_insumos

            total_formatado = f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.metric("💰 Custo Total do Evento", total_formatado)
elif menu == "Vendas":

    st.title("Vendas")
    st.info("Histórico de eventos em breve")