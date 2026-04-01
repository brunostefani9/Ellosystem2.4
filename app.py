import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

def definir_categoria_global(produto):

    produto = str(produto).lower()

    if any(p in produto for p in [
        "vodka", "gin", "rum", "whisky", "whiskey",
        "tequila", "licor", "cachaça", "bacardi",
        "absolut", "smirnoff", "jack", "campari"
    ]):
        return "Bebidas"

    elif any(p in produto for p in [
        "xarope", "açucar", "acucar", "grenadine"
    ]):
        return "Insumos"

    elif any(p in produto for p in [
        "limão", "limao", "laranja", "abacaxi", "morango"
    ]):
        return "Frutas"

    else:
        return "Outros"

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

cursor.execute("""
CREATE TABLE IF NOT EXISTS evento_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evento_id INTEGER,
    produto TEXT,
    quantidade REAL,
    unidade TEXT
)
""")

conn.commit()

# adiciona categoria sem quebrar
try:
    cursor.execute("ALTER TABLE evento_itens ADD COLUMN categoria TEXT")
    conn.commit()
except:
    pass

# -------------------------
# FUNÇÃO AUXILIAR
# -------------------------
def normalizar_nome(nome):
    if not nome:
        return ""
    return nome.strip().lower()

try:
    cursor.execute("ALTER TABLE eventos ADD COLUMN telefone TEXT")
    cursor.execute("ALTER TABLE eventos ADD COLUMN endereco TEXT")
    cursor.execute("ALTER TABLE eventos ADD COLUMN tipo_evento TEXT")
    cursor.execute("ALTER TABLE eventos ADD COLUMN hora_chegada TEXT")
    cursor.execute("ALTER TABLE eventos ADD COLUMN hora_inicio TEXT")
    cursor.execute("ALTER TABLE eventos ADD COLUMN hora_convidados TEXT")
    cursor.execute("ALTER TABLE eventos ADD COLUMN convidados INTEGER")
    conn.commit()
except:
    pass

try:
    cursor.execute("ALTER TABLE eventos ADD COLUMN custo_por_convidado REAL")
    conn.commit()
except:
    pass

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
                step=1.0,
                format="%.0f"
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
                step=1.0,
                format="%.0f"
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

                    custo = (preco / quantidade) * uso
                
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

            produto = st.text_input("Tipo do Produto").lower().strip()

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
    aba_cadastro, aba_lista = st.tabs(
        ["Cadastro de Drinks", "Lista de Drinks"]
    )

    # =========================
    # ABA 1 - CADASTRO
    # =========================
    with aba_cadastro:

        drink = st.text_input("Nome do drink", value=st.session_state["drink_nome"])

        col1, col2, col3, col4 = st.columns(4)

        ingrediente = normalizar_nome(col1.text_input("Ingrediente"))
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
                    cursor.execute("DELETE FROM receitas WHERE drink=?", (st.session_state["drink_nome"],))

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
                        uso_padrao = 1  # valor padrão pra evitar erro

                        for tabela in ["precos_bebidas","precos_insumos","precos_artesanais"]:
                            result = pd.read_sql(
                                f"SELECT custo, uso FROM {tabela} WHERE nome=?",
                                conn,
                                params=(ingrediente,)
                            )
                        
                            if not result.empty:
                                custo_unitario = result.iloc[0]["custo"]
                                uso_padrao = result.iloc[0]["uso"] if result.iloc[0]["uso"] > 0 else 1
                                break
                        
                        custo_total += (quantidade / uso_padrao) * custo_unitario

                        st.write(f"- {ingrediente} ({quantidade} {unidade})")

                with col2:
                    st.markdown(f"### 💰\nR$ {custo_total:,.2f}")
                    if st.button("🗑️", key=f"del_{drink}"):
                        cursor.execute("DELETE FROM receitas WHERE drink=?", (drink,))
                        conn.commit()
                        st.rerun()

                st.divider()

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

        telefone = st.text_input("📞 Telefone")

        endereco = st.text_input("📍 Endereço do evento")
        
        tipo_evento = st.selectbox("🎉 Tipo de evento", [
            "Casamento", "Aniversário", "Corporativo", "Festa privada", "Outro"
        ])
        
        col1, col2 = st.columns(2)
        
        hora_chegada = col1.time_input("🕒 Chegada da equipe")
        hora_inicio = col2.time_input("🍸 Início do serviço")
        
        hora_convidados = st.time_input("👥 Chegada dos convidados")
        
        num_convidados = st.number_input("👥 Número de convidados", min_value=1)
        
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
                    # Primeiro, busca exata pelo nome
                    resultado = df_bebidas[
                        df_bebidas["nome"].str.lower().str.strip() == item.lower()
                    ]
                
                    # Se não encontrar pelo nome, busca pelo tipo
                    if resultado.empty:
                        resultado = df_bebidas[
                            df_bebidas["tipo"].str.lower().str.contains(item.lower())
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
                
                    # Mostra todas as bebidas do mesmo tipo para escolha de marca
                    opcoes = df_bebidas[df_bebidas["tipo"].str.lower() == tipo.lower()]
                
                    # Caso não encontre, mostra todas as bebidas
                    if opcoes.empty:
                        opcoes = df_bebidas
                
                    escolha = st.selectbox(
                        f"{item} - Escolha a marca",
                        opcoes["nome"],
                        key=f"marca_{item}"
                    )
                    escolhas_marcas[item] = escolha
                
                # =========================
                # Cálculo do custo das bebidas
                # =========================
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
                        custo_total = custo_bebidas + custo_frutas

                        st.write(f"✔ {fruta.capitalize()} → {qtd_gramas:.0f} g | 💰 R$ {custo_item:,.2f}")

            # =========================
            # TOTAL (CORREÇÃO AQUI)
            # =========================
            st.divider()
            
            # Garantimos que custo_total exista mesmo se o cálculo acima falhar
            if 'custo_total' not in locals():
                custo_total = 0
            
            st.metric("💰 Custo Total do Evento (Bruto)", f"R$ {custo_total:,.2f}")
            
            # ✅ PREÇO DE VENDA (Com margem de lucro)
            margem = st.slider("Margem de lucro (%)", 0, 300, 100)
            preco_venda = custo_total * (1 + margem / 100)
            
            st.metric("💰 Preço Final Sugerido", f"R$ {preco_venda:,.2f}")
            
            # ✅ VALOR POR CONVIDADO (O cálculo que você pediu)
            # Usamos o preco_venda dividido pelo número de convidados do início do formulário
            if num_convidados > 0:
                valor_por_convidado = preco_venda / num_convidados
            else:
                valor_por_convidado = 0
                
            st.metric("💰 Valor cobrado por convidado", f"R$ {valor_por_convidado:,.2f}")
            
            
            # 💾 SALVAR ORÇAMENTO
            if st.button("💾 Salvar orçamento"):
            
                cursor.execute("""
                    INSERT INTO eventos (
                        cliente, data, cidade,
                        telefone, endereco, tipo_evento,
                        hora_chegada, hora_inicio, hora_convidados,
                        convidados,
                        custo, venda, status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    nome_cliente,
                    str(data_evento),
                    cidade_evento,
                    telefone,
                    endereco,
                    tipo_evento,
                    str(hora_chegada),
                    str(hora_inicio),
                    str(hora_convidados),
                    num_convidados,
                    custo_total,
                    preco_venda,
                    "pendente"
                ))
            
                conn.commit()
                evento_id = cursor.lastrowid
            
                # =========================
                # SALVAR BEBIDAS
                # =========================
                for item, dados in ingredientes_bebidas.items():
                    marca = escolhas_marcas[item]
                    qtd_ml = dados["qtd"]
            
                    result = df_bebidas[df_bebidas["nome"] == marca]
            
                    if not result.empty:
                        volume = result.iloc[0]["quantidade"]
            
                        if volume > 0:
                            qtd_real = qtd_ml / volume
                            qtd_garrafas = int(qtd_real) + (1 if qtd_real % 1 > 0 else 0)
            
                            cursor.execute("""
                                INSERT INTO evento_itens (evento_id, produto, quantidade, unidade, categoria)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                evento_id,
                                marca,
                                qtd_garrafas,
                                "garrafas",
                                "Bebidas"
                            ))
            
                    conn.commit()
                    st.success("✅ Orçamento salvo com sucesso!")
                    # =========================
                    # SALVAR FRUTAS / INSUMOS
                    # =========================
                    for fruta, qtd_gramas in ingredientes_insumos.items():
                    
                        cursor.execute("""
                            INSERT INTO evento_itens (evento_id, produto, quantidade, unidade, categoria)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            evento_id,
                            fruta.capitalize(),
                            qtd_gramas,
                            "g",
                            "Insumos"  # ou "Frutas" se quiser separar depois
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
    
                # =========================
                # CONTROLE DE ABERTURA
                # =========================
                if f"abrir_{row['id']}" not in st.session_state:
                    st.session_state[f"abrir_{row['id']}"] = False
    
                # =========================
                # BOTÃO CHECKLIST
                # =========================
                if st.button(f"📋 Checklist {row['id']}", key=f"check_{row['id']}"):
                    st.session_state[f"abrir_{row['id']}"] = True
    
                # =========================
                # CHECKLIST
                # =========================
                if st.session_state[f"abrir_{row['id']}"]:
    
                    itens = pd.read_sql("""
                        SELECT * FROM evento_itens WHERE evento_id=?
                    """, conn, params=(row["id"],))
    
                    st.subheader("📋 Checklist do Evento")
    
                    st.markdown(f"""
                    ### 📍 Informações do Evento
                    
                    **👤 Cliente:** {row['cliente']}  
                    📞 {row['telefone']}  
                    
                    📅 {row['data']}  
                    📍 {row['cidade']} - {row['endereco']}  
                    
                    🎉 Tipo: {row['tipo_evento']}  
                    
                    🕒 Chegada equipe: {row['hora_chegada']}  
                    🍸 Início serviço: {row['hora_inicio']}  
                    👥 Convidados chegam: {row['hora_convidados']}  
                    
                    👥 Nº convidados: {row['convidados']}  
                    
                    💰 Valor: R$ {row['venda']:,.2f}
                    """)
    
                    if itens.empty:
                        st.warning("Nenhum item encontrado")
                    else:
                        df_checklist = itens.copy()
    
                        # =========================
                        # CATEGORIA INTELIGENTE
                        # =========================
                        def definir_categoria(produto):
    
                            produto = produto.lower()
    
                            if any(p in produto for p in ["vodka", "gin", "rum", "whisky", "tequila", "licor", "cachaça"]):
                                return "Bebidas"
    
                            elif any(p in produto for p in ["limão", "limao", "laranja", "abacaxi", "morango"]):
                                return "Frutas"
    
                            elif any(p in produto for p in ["xarope", "açucar", "acucar", "grenadine"]):
                                return "Insumos"
    
                            else:
                                return "Outros"
    
                        df_checklist["Categoria"] = df_checklist["produto"].apply(definir_categoria_global)
    
                        # =========================
                        # COLUNAS OPERACIONAIS
                        # =========================
                        df_checklist["Início"] = ""
                        df_checklist["Fim"] = ""
    
                        # =========================
                        # EDITOR
                        # =========================
                        df_editado = st.data_editor(
                            df_checklist[["Categoria", "produto", "quantidade", "Início", "Fim"]],
                            num_rows="dynamic",
                            use_container_width=True,
                            key=f"editor_{row['id']}"
                        )
    
                        # =========================
                        # SALVAR EDIÇÃO
                        # =========================
                        if st.button(f"💾 Salvar edição {row['id']}", key=f"save_{row['id']}"):
    
                            cursor.execute("DELETE FROM evento_itens WHERE evento_id=?", (row["id"],))
    
                            for _, item in df_editado.iterrows():
                                cursor.execute("""
                                    INSERT INTO evento_itens (evento_id, produto, quantidade, unidade, categoria)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (
                                    row["id"],
                                    item["produto"],
                                    item["quantidade"],
                                    item.get("unidade", "un"),
                                    item["Categoria"]
                                ))
    
                            conn.commit()
                            st.success("Checklist atualizado!")
    
                # =========================
                # VALOR
                # =========================
                st.write(f"💰 Venda: R$ {row['venda']:,.2f}")
    
                # =========================
                # AÇÕES
                # =========================
                col1, col2 = st.columns(2)
    
                if col1.button(f"✅ Aprovar {row['id']}", key=f"aprovar_{row['id']}"):
                    cursor.execute("UPDATE eventos SET status='aprovado' WHERE id=?", (row["id"],))
                    conn.commit()
                    st.rerun()
    
                if col2.button(f"🗑 Excluir {row['id']}", key=f"excluir_{row['id']}"):
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
    
                # CHECKLIST (igual ao anterior)
                if st.button(f"📋 Checklist aprovado {row['id']}"):
    
                    itens = pd.read_sql("""
                        SELECT * FROM evento_itens WHERE evento_id=?
                    """, conn, params=(row["id"],))
    
                    st.subheader("📋 Checklist do Evento")
    
                    st.markdown(f"""
                    **Cliente:** {row['cliente']}  
                    **Data:** {row['data']}  
                    **Cidade:** {row['cidade']}  
                    """)
    
                    if not itens.empty:
                        df_checklist = itens.copy()
    
                        def definir_categoria(unidade):
                            if unidade == "garrafas":
                                return "Bebidas"
                            elif unidade == "g":
                                return "Frutas"
                            else:
                                return "Outros"
    
                        df_checklist = itens.copy()

                        df_checklist["Categoria"] = df_checklist["produto"].apply(definir_categoria_global)
                        
                        df_checklist["Início"] = ""
                        df_checklist["Fim"] = ""
                        
                        st.dataframe(
                            df_checklist[["Categoria", "produto", "quantidade", "Início", "Fim"]]
                            .rename(columns={
                                "produto": "Produto",
                                "quantidade": "Qtde"
                            })
                        )
    
                if st.button(f"✔ Finalizar {row['id']}"):
                    cursor.execute(
                        "UPDATE eventos SET status='finalizado' WHERE id=?",
                        (row["id"],)
                    )
                    conn.commit()
                    st.rerun()
    
                st.divider()
        
elif menu == "Vendas":

    st.title("💰 Vendas")

    tab_vendas, tab_registro = st.tabs(["📊 Resumo", "📁 Registro"])

    # =========================
    # 📊 RESUMO (FATURAMENTO)
    # =========================
    with tab_vendas:

        df_vendas = pd.read_sql("""
            SELECT * FROM eventos 
            WHERE status IN ('aprovado', 'finalizado')
        """, conn)

        if df_vendas.empty:
            st.info("Nenhuma venda registrada")
        else:
            df_vendas["data"] = pd.to_datetime(df_vendas["data"], errors="coerce")

            # filtro por mês
            meses = df_vendas["data"].dt.to_period("M").astype(str).unique()
            mes_selecionado = st.selectbox("Selecionar mês", sorted(meses))

            df_filtrado = df_vendas[
                df_vendas["data"].dt.to_period("M").astype(str) == mes_selecionado
            ]

            faturamento = df_filtrado["venda"].sum()

            st.metric("💰 Faturamento do mês", f"R$ {faturamento:,.2f}")

            st.dataframe(df_filtrado[["cliente", "data", "cidade", "venda"]])

    # =========================
    # 📁 REGISTRO COMPLETO
    # =========================
    with tab_registro:

        st.subheader("📁 Histórico de Eventos")

        df_todos = pd.read_sql("""
            SELECT * FROM eventos 
            WHERE status IN ('aprovado', 'finalizado')
            ORDER BY data DESC
        """, conn)

        if df_todos.empty:
            st.info("Nenhum evento registrado")
        else:
            for _, row in df_todos.iterrows():

                st.write(f"""
                **👤 {row['cliente']}**  
                📅 {row['data']} | 📍 {row['cidade']}  
                💰 R$ {row['venda']:,.2f}
                """)

                # botão checklist
                if st.button(f"📋 Ver Checklist {row['id']}", key=f"check_venda_{row['id']}"):

                    itens = pd.read_sql("""
                        SELECT * FROM evento_itens WHERE evento_id=?
                    """, conn, params=(row["id"],))

                    if itens.empty:
                        st.warning("Sem itens")
                    else:
                        st.dataframe(itens[["produto", "quantidade", "unidade"]])

                st.divider()
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
