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

cursor.execute("""
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT,
    data TEXT,
    cidade TEXT,
    custo REAL,
    venda REAL,
    status TEXT
)
""")

conn.commit()

# -------------------------
# FUNÇÃO AUXILIAR
# -------------------------
def normalizar_nome(nome):
    if not nome:
        return ""
    return nome.strip().lower()

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
"Vendas",
"Pacotes"
]
)

# -------------------------
# FUNÇÃO DE PRECIFICAÇÃO
# -------------------------

def tela_precificacao(nome_tabela):

    tab1, tab2 = st.tabs(["Cadastrar", "Lista"])

    # =========================
    # CADASTRO
    # =========================
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
                    rendimento = quantidade / uso if uso > 0 else 0
                    custo = preco / rendimento if rendimento > 0 else 0
        
                    cursor.execute(f"""
                    INSERT INTO {nome_tabela}
                    (tipo, nome, quantidade, preco, uso, rendimento, custo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                    tipo,
                    normalizar_nome(nome),
                    quantidade,
                    preco,
                    uso,
                    rendimento,
                    custo
                    ))
        
                    conn.commit()
                    st.success("Item cadastrado!")

    # =========================
    # LISTA / EDIÇÃO
    # =========================
    with tab2:

        df = pd.read_sql(f"SELECT * FROM {nome_tabela}", conn)

        busca = st.text_input("Pesquisar", key=f"busca_{nome_tabela}")

        if busca:
            df = df[
                df["nome"].fillna("").str.contains(busca, case=False) |
                df["tipo"].fillna("").str.contains(busca, case=False)
            ]

        if not df.empty:

            df_editado = st.data_editor(
                df,
                use_container_width=True,
                column_config={
                    "preco": st.column_config.NumberColumn(
                        "💰 Preço",
                        format="R$ %.2f"
                    ),
                    "custo": st.column_config.NumberColumn(
                        "💰 Custo",
                        format="R$ %.2f"
                    ),
                }
            )

            # =========================
            # SALVAR ALTERAÇÕES (SEGURO)
            # =========================
            if st.button("💾 Salvar alterações", key=f"save_{nome_tabela}"):

                try:
                    for _, row in df_editado.iterrows():
                        cursor.execute(f"""
                        UPDATE {nome_tabela}
                        SET tipo=?, nome=?, quantidade=?, preco=?, uso=?, rendimento=?, custo=?
                        WHERE id=?
                        """, (
                            row["tipo"],
                            row["nome"],
                            row["quantidade"],
                            row["preco"],
                            row["uso"],
                            row["rendimento"],
                            row["custo"],
                            row["id"]
                        ))

                    conn.commit()
                    st.success("Alterações salvas!")

                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

            # =========================
            # EXCLUIR ITEM
            # =========================
            item = st.selectbox("Excluir item", df["id"], key=f"del_{nome_tabela}")

            if st.button("🗑 Excluir selecionado", key=f"btn_{nome_tabela}"):

                cursor.execute(f"DELETE FROM {nome_tabela} WHERE id = ?", (item,))
                conn.commit()
                st.rerun()

        else:
            st.info("Nenhum item cadastrado.")

# -------------------------
# FUNÇÃO INSUMOS (FRUTAS)
# -------------------------

def tela_insumos():

    tab1, tab2 = st.tabs(["Cadastrar","Lista"])

    # -------------------------
    # CADASTRO
    # -------------------------
    with tab1:

        with st.form("form_insumos", clear_on_submit=True):

            nome = st.text_input("Nome do insumo")

            quantidade = st.number_input(
                "Quantidade total (g ou ml)",
                min_value=0.0,
                format="%.2f"
            )

            preco = st.number_input(
                "Preço",
                min_value=0.0,
                format="%.2f"
            )

            uso = st.number_input(
                "Uso por receita (g ou ml)",
                min_value=1.0,
                value=25.0,
                format="%.2f"
            )
            
            if st.form_submit_button("Cadastrar"):

                if quantidade == 0:
                    st.error("Quantidade não pode ser zero")
                else:

                    quantidade_gramas = quantidade * 1000
                    custo_por_grama = preco / quantidade_gramas
                    custo = uso * custo_por_grama
                
                    cursor.execute("""
                    INSERT INTO precos_insumos
                    VALUES(NULL,?,?,?,?,?,?,?)
                    """,(
                        "insumo",
                        normalizar_nome(nome),
                        quantidade,
                        preco,
                        uso,
                        quantidade_gramas / uso if uso != 0 else 0,
                        custo
                    ))
                
                    conn.commit()
                    st.success("Insumo cadastrado!")

    # -------------------------
    # LISTA / EDIÇÃO
    # -------------------------
    with tab2:

        df = pd.read_sql("SELECT * FROM precos_insumos", conn)

        # ✏️ EDITÁVEL + FORMATADO EM R$
        df_editado = st.data_editor(
            df,
            use_container_width=True,
            column_config={
                "preco": st.column_config.NumberColumn(
                    "💰 Preço",
                    format="R$ %.2f"
                ),
                "custo": st.column_config.NumberColumn(
                    "💰 Custo (por unidade)",
                    format="R$ %.4f"
                ),
            }
        )

        # 💾 SALVAR ALTERAÇÕES
        if st.button("💾 Salvar alterações insumos"):

            try:
                df_editado.to_sql("precos_insumos", conn, if_exists="replace", index=False)
                st.success("Alterações salvas!")
            except:
                st.error("Erro ao salvar alterações")

        # 🗑 EXCLUIR
        if not df.empty:
            item = st.selectbox("Excluir item", df["id"])

            if st.button("🗑 Excluir"):
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

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Entrada", "Saída", "Estoque físico", "Registros"]
    )

    # -------------------------
    # ENTRADA
    # -------------------------

    with tab1:

        with st.form("entrada_estoque", clear_on_submit=True):

            st.subheader("Tipo do Produto")

            tipos_existentes = bebidas["tipo"].dropna().unique().tolist()

            produto = st.text_input("Tipo do Produto")

            if not produto:
                produto = st.selectbox(
                    "Ou selecione um tipo existente",
                    tipos_existentes
                )

            novo_tipo = st.text_input("Ou digite um novo tipo")

            produto = novo_tipo.lower().strip() if novo_tipo else produto_existente

            marca = st.text_input("Marca")

            qtd = st.number_input(
                "Quantidade",
                min_value=0.0
            )

            status = st.selectbox(
                "Status",
                ["Compra", "Volta evento"]
            )

            if st.form_submit_button("Registrar entrada"):

                atual = pd.read_sql(
                    "SELECT * FROM estoque WHERE produto=? AND marca=?",
                    conn,
                    params=(produto, marca)
                )

                if atual.empty:

                    cursor.execute(
                        "INSERT INTO estoque VALUES(?,?,?)",
                        (produto, marca, qtd)
                    )

                else:

                    nova = atual.iloc[0]["quantidade"] + qtd

                    cursor.execute("""
                        UPDATE estoque
                        SET quantidade=?
                        WHERE produto=? AND marca=?
                    """, (nova, produto, marca))

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

        estoque = pd.read_sql("SELECT * FROM estoque", conn)

        if estoque.empty:

            st.info("Estoque vazio")

        else:

            with st.form("saida_estoque", clear_on_submit=True):

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
                        params=(produto, marca)
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
                            """, (nova, produto, marca))

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
            df["marca"].str.contains(busca, case=False)
        ]

    if df.empty:
        st.info("Estoque vazio")
    else:
        st.dataframe(df, use_container_width=True)

        st.subheader("Remover item")

        item = st.selectbox(
            "Selecione o item para excluir",
            df["produto"] + " | " + df["marca"]
        )

        if st.button("🗑 Excluir item"):

            produto_sel, marca_sel = item.split(" | ")

            row = df[
                (df["produto"] == produto_sel) &
                (df["marca"] == marca_sel)
            ].iloc[0]

            cursor.execute("""
                INSERT INTO movimentacoes
                VALUES(?,?,?,?,?,?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                produto_sel,
                marca_sel,
                "Exclusão",
                row["quantidade"],
                "Manual"
            )
            )

            cursor.execute(
                "DELETE FROM estoque WHERE produto=? AND marca=?",
                (produto_sel, marca_sel)
            )

            conn.commit()

            st.success("Item removido do estoque")
            st.rerun()

    # -------------------------
    # REGISTROS
    # -------------------------

    with tab4:

        df = pd.read_sql(
            "SELECT * FROM movimentacoes ORDER BY data DESC",
            conn
        )

        st.dataframe(df, use_container_width=True)

# -------------------------
# OUTRAS ABAS
# -------------------------

elif menu == "Relatórios":

    st.title("Relatórios")
    st.info("Indicadores virão na próxima etapa")

elif menu == "Receitas":

    st.title("Receitas")

    # Controle de estado
    if "ingredientes_temp" not in st.session_state:
        st.session_state["ingredientes_temp"] = []

    if "drink_nome" not in st.session_state:
        st.session_state["drink_nome"] = ""

    if "msg" not in st.session_state:
        st.session_state["msg"] = ""

    # Mostra mensagem (se existir)
    if st.session_state["msg"]:
        st.success(st.session_state["msg"])
        st.session_state["msg"] = ""

    # ------------------------
    # SUB-ABAS
    # ------------------------
    aba_cadastro, aba_lista, aba_edicao = st.tabs(
        ["Cadastro de Drinks", "Lista de Drinks", "Edição de Receitas"]
    )

    # =========================
    # ABA 1 - CADASTRO
    # =========================
    with aba_cadastro:

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
    with aba_lista:

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

                        # Busca custo nas tabelas
                        custo_unitario = 0
                        for tabela in ["precos_bebidas","precos_insumos","precos_artesanais"]:
                            result = pd.read_sql(f"SELECT custo FROM {tabela} WHERE nome=?", conn, params=(ingrediente,))
                            if not result.empty:
                                custo_unitario = result.iloc[0]["custo"]
                                break
                        custo_total += custo_unitario * quantidade

                        st.write(f"- {ingrediente} ({quantidade} {unidade})")

                with col2:
                    st.markdown(f"### 💰\nR$ {custo_total:,.2f}")
                    if st.button("🗑️", key=f"del_{drink}"):
                        cursor.execute("DELETE FROM receitas WHERE drink=?", (drink,))
                        conn.commit()
                        st.rerun()

                st.divider()

    # =========================
    # ABA 3 - EDIÇÃO DE RECEITAS
    # =========================
    with aba_edicao:

        df = pd.read_sql("SELECT * FROM receitas", conn)

        if df.empty:
            st.info("Nenhum drink cadastrado")
        else:

            drinks = df["drink"].unique()
            drink_sel = st.selectbox("Selecione o drink para editar", drinks)

            receita = df[df["drink"] == drink_sel].copy()

            # Data editor para edição
            df_editado = st.data_editor(
                receita,
                use_container_width=True,
                column_config={
                    "drink": st.column_config.TextColumn("Drink"),
                    "ingrediente": st.column_config.TextColumn("Ingrediente"),
                    "quantidade": st.column_config.NumberColumn("Quantidade"),
                    "unidade": st.column_config.TextColumn("Unidade")
                }
            )

            # Botão para salvar alterações
            if st.button("💾 Salvar alterações da receita"):

                try:
                    # Deleta entradas antigas
                    cursor.execute("DELETE FROM receitas WHERE drink=?", (drink_sel,))

                    # Insere os dados editados
                    for _, row in df_editado.iterrows():
                        cursor.execute("""
                        INSERT INTO receitas(drink, ingrediente, quantidade, unidade)
                        VALUES(?,?,?,?)
                        """, (row["drink"], row["ingrediente"], row["quantidade"], row["unidade"]))

                    conn.commit()
                    st.success("Receita atualizada com sucesso!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

elif menu == "Orçamentos":

    st.title("Orçamentos")

    tab1, tab2, tab3 = st.tabs([
        "🧾 Novo Orçamento",
        "⏳ Pendentes",
        "✅ Aprovados"
    ])

    # =========================
    # ABA 1 - NOVO ORÇAMENTO
    # =========================
    with tab1:

        # ✅ DADOS CLIENTE
        st.subheader("Dados do Cliente")

        col1, col2, col3 = st.columns(3)

        nome_cliente = col1.text_input("Nome do cliente")
        data_evento = col2.date_input("Data do evento")
        cidade_evento = col3.text_input("Cidade / Local")

        modo_calculo = st.radio(
            "Modo de cálculo",
            ["Evento inteiro", "Por hora"]
        )

        # =========================
        # CONFIG EVENTO
        # =========================
        st.subheader("Configuração do Evento")

        col1, col2, col3 = st.columns(3)

        convidados = col1.number_input("Convidados", min_value=1, value=50)
        horas = col2.number_input("Horas de evento", min_value=1, value=4)
        drinks_por_hora = col3.number_input("Drinks por pessoa/hora", min_value=0.5, value=2.0)

        if modo_calculo == "Evento inteiro":
            total_drinks = convidados * drinks_por_hora
        else:
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

                pesos = {}
                total_peso = 0

                for drink in selecao:
                    peso = st.number_input(drink, min_value=1, value=1, key=f"peso_{drink}")
                    pesos[drink] = peso
                    total_peso += peso

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
                # DADOS
                # =========================
                df_bebidas = pd.read_sql("SELECT * FROM precos_bebidas", conn)
                df_insumos = pd.read_sql("SELECT * FROM precos_insumos", conn)

                ingredientes_bebidas = {}
                ingredientes_insumos = {}

                for item, qtd in ingredientes_totais.items():

                    resultado = df_bebidas[
                        df_bebidas["tipo"].str.lower().str.contains(item.lower(), na=False)
                    ]

                    if not resultado.empty:
                        ingredientes_bebidas[item] = {
                            "qtd": qtd,
                            "tipo": resultado.iloc[0]["tipo"]
                        }
                    else:
                        ingredientes_insumos[item] = qtd

                # =========================
                # BEBIDAS
                # =========================
                st.subheader("🍸 Bebidas")

                custo_bebidas = 0
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

                for item, dados in ingredientes_bebidas.items():

                    qtd_ml = dados["qtd"]
                    marca = escolhas_marcas[item]

                    result = df_bebidas[df_bebidas["nome"] == marca]

                    if not result.empty:

                        preco = result.iloc[0]["preco"]
                        volume = result.iloc[0]["quantidade"]

                        if volume > 0:

                            qtd_real = qtd_ml / volume
                            qtd_garrafas = int(qtd_real) + (1 if qtd_real % 1 > 0 else 0)

                            custo_item = qtd_garrafas * preco
                            custo_bebidas += custo_item

                            st.write(f"✔ {marca} → {qtd_garrafas} garrafas | 💰 R$ {custo_item:,.2f}")

                st.markdown(f"### 💰 Subtotal Bebidas: R$ {custo_bebidas:,.2f}")

                # =========================
                # FRUTAS
                # =========================
                st.subheader("🍋 Frutas")

                custo_frutas = 0

                for fruta, qtd_gramas in ingredientes_insumos.items():

                    encontrado = df_insumos[
                        df_insumos["nome"].str.lower() == fruta
                    ]

                    if not encontrado.empty:

                        preco_kg = encontrado.iloc[0]["preco"]
                        custo_por_grama = preco_kg / 1000

                        custo_item = qtd_gramas * custo_por_grama
                        custo_frutas += custo_item

                        st.write(f"✔ {fruta.capitalize()} → {qtd_gramas:.0f} g | 💰 R$ {custo_item:,.2f}")

                # =========================
                # TOTAL
                # =========================
                st.divider()

                custo_total = custo_bebidas + custo_frutas

                st.metric("💰 Custo Total do Evento", f"R$ {custo_total:,.2f}")

                # ✅ PREÇO DE VENDA
                margem = st.slider("Margem de lucro (%)", 0, 300, 100)
                preco_venda = custo_total * (1 + margem / 100)

                st.metric("💰 Preço sugerido", f"R$ {preco_venda:,.2f}")

                if st.button("💾 Salvar orçamento"):

                    cursor.execute("""
                        INSERT INTO eventos (cliente, data, cidade, custo, venda, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        nome_cliente,
                        str(data_evento),
                        cidade_evento,
                        custo_total,
                        preco_venda,
                        "pendente"
                    ))

                    conn.commit()

                    st.success("Orçamento salvo com sucesso!")

    # =========================
    # ABA 2 - PENDENTES
    # =========================
    with tab2:

        st.subheader("📋 Orçamentos Pendentes")

        df_eventos = pd.read_sql("SELECT * FROM eventos WHERE status='pendente'", conn)

        if df_eventos.empty:
            st.info("Nenhum orçamento pendente")
        else:
            for _, row in df_eventos.iterrows():

                st.write(f"👤 {row['cliente']} | 📅 {row['data']} | 📍 {row['cidade']}")
                st.write(f"💰 Venda: R$ {row['venda']:,.2f}")

                col1, col2 = st.columns(2)

                if col1.button(f"✅ Aprovar {row['id']}"):
                    cursor.execute("UPDATE eventos SET status='aprovado' WHERE id=?", (row["id"],))
                    conn.commit()
                    st.rerun()

                if col2.button(f"🗑 Excluir {row['id']}"):
                    cursor.execute("DELETE FROM eventos WHERE id=?", (row["id"],))
                    conn.commit()
                    st.rerun()

                st.divider()

    # =========================
    # ABA 3 - APROVADOS
    # =========================
    with tab3:

        st.subheader("✅ Eventos Aprovados")

        df_eventos = pd.read_sql("SELECT * FROM eventos WHERE status='aprovado'", conn)

        if df_eventos.empty:
            st.info("Nenhum evento aprovado")
        else:
            for _, row in df_eventos.iterrows():

                st.write(f"👤 {row['cliente']} | 📅 {row['data']} | 📍 {row['cidade']}")
                st.write(f"💰 Venda: R$ {row['venda']:,.2f}")

                if st.button(f"✔ Finalizar {row['id']}"):
                    cursor.execute(
                        "UPDATE eventos SET status='finalizado' WHERE id=?",
                        (row["id"],)
                    )
                    conn.commit()
                    st.rerun()

                st.divider()
        
elif menu == "Vendas":

    st.title("Vendas")
    st.info("Histórico de eventos em breve")

elif menu == "Pacotes":

    st.title("📦 Pacotes / Serviços")

    import json

    tab1, tab2 = st.tabs(["Cadastrar","Lista"])

    # -------------------------
    # CADASTRAR PACOTE
    # -------------------------
    with tab1:

        nome = st.text_input("Nome do pacote")

        tipo = st.selectbox(
            "Tipo do serviço",
            ["Bar Principal","Whisky","Gin","Spritz","Shots","Outro"]
        )

        itens = st.text_area(
            "Itens (um por linha)",
            placeholder="jack daniels\nred label\ngelo"
        )

        extras = st.text_area(
            "Extras opcionais",
            placeholder="gelo saborizado\ncopo especial"
        )

        if st.button("💾 Salvar pacote"):

            dados = json.dumps({
                "itens": itens.split("\n"),
                "extras": extras.split("\n")
            })

            cursor.execute("""
            INSERT INTO pacotes (nome, tipo, dados)
            VALUES (?,?,?)
            """,(nome, tipo, dados))

            conn.commit()

            st.success("Pacote salvo!")

    # -------------------------
    # LISTA
    # -------------------------
    with tab2:

        df = pd.read_sql("SELECT * FROM pacotes", conn)

        if df.empty:
            st.info("Nenhum pacote cadastrado")
        else:

            id_sel = st.selectbox("Selecionar pacote", df["id"])

            pacote = df[df["id"] == id_sel].iloc[0]

            dados = json.loads(pacote["dados"])

            st.subheader(pacote["nome"])

            st.write("📦 Itens:")
            for i in dados["itens"]:
                if i:
                    st.write(f"✔ {i}")

            st.write("✨ Extras:")
            for e in dados["extras"]:
                if e:
                    st.write(f"+ {e}")

            if st.button("🗑 Excluir pacote"):
                cursor.execute("DELETE FROM pacotes WHERE id = ?", (id_sel,))
                conn.commit()
                st.rerun()
