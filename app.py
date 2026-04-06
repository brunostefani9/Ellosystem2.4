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

cursor.execute("""
CREATE TABLE IF NOT EXISTS pagamentos_equipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evento TEXT,
    nome TEXT,
    funcao TEXT,
    valor REAL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evento_id INTEGER,
    cliente TEXT,
    data TEXT,
    valor_venda REAL,
    custo REAL,
    lucro REAL
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS financeiro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    tipo TEXT,
    categoria TEXT,
    forma_pagamento TEXT,
    descricao TEXT,
    valor REAL
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pacotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    tipo TEXT,
    dados TEXT
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

# adiciona categoria sem quebrar
try:
    cursor.execute("ALTER TABLE evento_itens ADD COLUMN categoria TEXT")
    conn.commit()
except:
    pass

try:
    cursor.execute("ALTER TABLE pacotes ADD COLUMN preco_por_pessoa REAL")
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
"Cachês",
"Vendas",
"Financeiro",
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

                        quantidade = row["quantidade"]
                        uso = row["uso"]
                        preco = row["preco"]
                    
                        if uso == 0 or quantidade == 0:
                            rendimento = 0
                            custo = 0
                        else:
                            quantidade_gramas = quantidade * 1000
                            rendimento = quantidade_gramas / uso
                            custo = preco / rendimento
                    
                        cursor.execute("""
                            UPDATE precos_insumos
                            SET tipo=?, nome=?, quantidade=?, preco=?, uso=?, rendimento=?, custo=?
                            WHERE id=?
                        """, (
                            row["tipo"],
                            row["nome"],
                            quantidade,
                            preco,
                            uso,
                            rendimento,
                            custo,
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

        st.info("📌 Cadastro de frutas:\n- Quantidade sempre em KG\n- Uso sempre em GRAMAS")
    
        with st.form("form_insumos", clear_on_submit=True):
    
            nome = st.text_input("Nome do insumo")
    
            quantidade = st.number_input(
                "Quantidade (KG)",  # ✅ corrigido
                min_value=0.0,
                format="%.2f"
            )
    
            preco = st.number_input(
                "Preço (por KG)",  # 🔥 já melhora também
                min_value=0.0,
                format="%.2f"
            )
    
            uso = st.number_input(
                "Uso por receita (GRAMAS)",  # ✅ corrigido
                min_value=1.0,
                value=25.0,
                format="%.2f"
            )
            
            if st.form_submit_button("Cadastrar"):

                if quantidade == 0:
                    st.error("Quantidade não pode ser zero")
                elif uso == 0:
                    st.error("Uso não pode ser zero")
                else:
            
                    # 🔹 converter KG → GRAMAS
                    quantidade_gramas = quantidade * 1000
            
                    # 🔹 cálculo correto
                    rendimento = quantidade_gramas / uso
                    custo = preco / rendimento
            
                    cursor.execute("""
                    INSERT INTO precos_insumos
                    VALUES(NULL,?,?,?,?,?,?,?)
                    """,(
                        "fruta",
                        normalizar_nome(nome),
                        quantidade,   # continua salvando em KG
                        preco,
                        uso,
                        rendimento,
                        custo
                    ))
            
                    conn.commit()
                    st.success("Fruta cadastrada corretamente!")
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
        
                "id": st.column_config.NumberColumn(
                    "ID",
                    disabled=True  # 🔒 não pode editar
                ),
        
                "tipo": "Tipo",
        
                "nome": "Nome",
        
                "quantidade": st.column_config.NumberColumn(
                    "Quantidade (KG)"
                ),
        
                "preco": st.column_config.NumberColumn(
                    "💰 Preço (KG)",
                    format="R$ %.2f"
                ),
        
                "uso": st.column_config.NumberColumn(
                    "Uso (g)"
                ),
        
                "rendimento": st.column_config.NumberColumn(
                    "Rendimento",
                    disabled=True  # 🔒 calculado
                ),
        
                "custo": st.column_config.NumberColumn(
                    "💰 Custo por uso",
                    format="R$ %.2f",
                    disabled=True  # 🔒 calculado
                ),
            }
        )

        # 💾 SALVAR ALTERAÇÕES
        if st.button("💾 Salvar alterações insumos"):

            try:
                for _, row in df_editado.iterrows():
                    cursor.execute("""
                        UPDATE precos_insumos
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

    st.title("📦 Controle de Estoque")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Entrada", "Saída", "Estoque físico", "Registros"]
    )

    # =========================
    # ENTRADA
    # =========================
    with tab1:

        with st.form("entrada_estoque", clear_on_submit=True):

            st.subheader("➕ Entrada de Produto")

            produto = st.text_input("Tipo do Produto").lower().strip()
            marca = st.text_input("Marca")

            tamanho = st.selectbox(
                "Tamanho",
                ["1L", "750ml", "700ml", "600ml"]
            )

            qtd = st.number_input("Quantidade", min_value=1.0)

            status = st.selectbox(
                "Tipo",
                ["Compra", "Volta evento"]
            )

            preco = 0.0

            if status == "Compra":
                preco = st.number_input("Preço por garrafa", min_value=0.0)

            else:
                st.info("🔁 Retorno de evento: será somado ao estoque existente")

            if st.form_submit_button("Registrar entrada"):

                atual = pd.read_sql(
                    "SELECT * FROM estoque WHERE produto=? AND marca=? AND tamanho=?",
                    conn,
                    params=(produto, marca, tamanho)
                )

                if atual.empty:

                    cursor.execute("""
                        INSERT INTO estoque (produto, marca, tamanho, quantidade, preco)
                        VALUES (?, ?, ?, ?, ?)
                    """, (produto, marca, tamanho, qtd, preco))

                else:
                    qtd_atual = atual.iloc[0]["quantidade"]
                    preco_atual = atual.iloc[0]["preco"]

                    nova_qtd = qtd_atual + qtd

                    if status == "Compra":
                        novo_preco = preco
                    else:
                        novo_preco = preco_atual

                    cursor.execute("""
                        UPDATE estoque
                        SET quantidade=?, preco=?
                        WHERE produto=? AND marca=? AND tamanho=?
                    """, (nova_qtd, novo_preco, produto, marca, tamanho))

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
                st.success("✅ Entrada registrada!")
                st.rerun()

    # =========================
    # SAÍDA
    # =========================
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

                marca = st.selectbox(
                    "Marca",
                    estoque[estoque["produto"] == produto]["marca"].unique()
                )

                tamanho = st.selectbox(
                    "Tamanho",
                    estoque[
                        (estoque["produto"] == produto) &
                        (estoque["marca"] == marca)
                    ]["tamanho"].unique()
                )

                qtd = st.number_input("Quantidade", min_value=1.0)

                if st.form_submit_button("Registrar saída"):

                    atual = pd.read_sql(
                        "SELECT * FROM estoque WHERE produto=? AND marca=? AND tamanho=?",
                        conn,
                        params=(produto, marca, tamanho)
                    )

                    if atual.empty:
                        st.error("Item não encontrado")

                    else:
                        qtd_atual = atual.iloc[0]["quantidade"]
                        nova = qtd_atual - qtd

                        if nova < 0:
                            st.error("Estoque insuficiente")

                        else:
                            cursor.execute("""
                                UPDATE estoque
                                SET quantidade=?
                                WHERE produto=? AND marca=? AND tamanho=?
                            """, (nova, produto, marca, tamanho))

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
                            st.success("✅ Saída registrada!")
                            st.rerun()

    # =========================
    # ESTOQUE FÍSICO
    # =========================
    with tab3:

        df = pd.read_sql(
            "SELECT * FROM estoque ORDER BY produto",
            conn
        )

        busca = st.text_input("🔍 Buscar")

        if busca:
            df = df[df["marca"].str.contains(busca, case=False)]

        if df.empty:
            st.info("Estoque vazio")

        else:

            # 💰 cálculo automático
            df["valor_total"] = df["quantidade"] * df["preco"]

            total_estoque = df["valor_total"].sum()
            total_itens = df["quantidade"].sum()

            col1, col2 = st.columns(2)
            col1.metric("📦 Total de itens", int(total_itens))
            col2.metric("💰 Valor total em estoque", f"R$ {total_estoque:,.2f}")

            st.divider()

            st.dataframe(
                df[
                    ["produto", "marca", "tamanho", "quantidade", "preco", "valor_total"]
                ],
                use_container_width=True,
                column_config={
                    "preco": st.column_config.NumberColumn("💰 Unitário", format="R$ %.2f"),
                    "valor_total": st.column_config.NumberColumn("💎 Total", format="R$ %.2f")
                }
            )

            # 🔥 ranking financeiro
            st.subheader("💸 Onde está seu dinheiro")

            ranking = df.sort_values(by="valor_total", ascending=False)
            st.bar_chart(ranking.set_index("marca")["valor_total"])

            # 🔥 alerta
            baixo = df[df["quantidade"] <= 2]

            if not baixo.empty:
                st.warning("⚠️ Estoque baixo")
                st.dataframe(baixo[["produto", "marca", "quantidade"]])

    # =========================
    # REGISTROS
    # =========================
    with tab4:

        df = pd.read_sql(
            "SELECT * FROM movimentacoes ORDER BY data DESC",
            conn
        )

        st.dataframe(df, use_container_width=True)

elif menu == "Relatórios":

    st.title("📊 Dashboard Geral")

    # =========================
    # FILTRO GLOBAL
    # =========================
    col1, col2 = st.columns(2)
    data_inicio = col1.date_input("📅 Data inicial")
    data_fim = col2.date_input("📅 Data final")

    # =========================
    # CARREGAR DADOS
    # =========================
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
    df_fin = pd.read_sql("SELECT * FROM financeiro", conn)
    df_itens = pd.read_sql("SELECT * FROM evento_itens", conn)

    # converter datas
    if not df_vendas.empty:
        df_vendas["data"] = pd.to_datetime(df_vendas["data"])

    if not df_fin.empty:
        df_fin["data"] = pd.to_datetime(df_fin["data"])

    # aplicar filtro
    if data_inicio and data_fim:
        if not df_vendas.empty:
            df_vendas = df_vendas[
                (df_vendas["data"] >= pd.to_datetime(data_inicio)) &
                (df_vendas["data"] <= pd.to_datetime(data_fim))
            ]

        if not df_fin.empty:
            df_fin = df_fin[
                (df_fin["data"] >= pd.to_datetime(data_inicio)) &
                (df_fin["data"] <= pd.to_datetime(data_fim))
            ]

    # =========================
    # ABAS
    # =========================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral",
        "💰 Financeiro",
        "📈 Vendas",
        "🎯 Metas",
        "📦 Produtos"
    ])

    # =========================
    # 📊 VISÃO GERAL
    # =========================
    with tab1:

        total_vendas = df_vendas["valor_venda"].sum() if not df_vendas.empty else 0
        total_custo = df_vendas["custo"].sum() if not df_vendas.empty else 0
        total_lucro = df_vendas["lucro"].sum() if not df_vendas.empty else 0

        margem = (total_lucro / total_vendas * 100) if total_vendas > 0 else 0

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("💰 Faturamento", f"R$ {total_vendas:,.2f}")
        col2.metric("💸 Custos", f"R$ {total_custo:,.2f}")
        col3.metric("📈 Lucro", f"R$ {total_lucro:,.2f}")
        col4.metric("📊 Margem", f"{margem:.1f}%")

        st.divider()

        if not df_vendas.empty:
            vendas_dia = df_vendas.groupby(df_vendas["data"].dt.date)["valor_venda"].sum()
            st.line_chart(vendas_dia)

    # =========================
    # 💰 FINANCEIRO
    # =========================
    with tab2:

        entradas = df_fin[df_fin["tipo"] == "Entrada"]["valor"].sum() if not df_fin.empty else 0
        saidas = df_fin[df_fin["tipo"] == "Saída"]["valor"].sum() if not df_fin.empty else 0

        saldo = entradas - saidas

        col1, col2, col3 = st.columns(3)

        col1.metric("💵 Entradas", f"R$ {entradas:,.2f}")
        col2.metric("💸 Saídas", f"R$ {saidas:,.2f}")
        col3.metric("🏦 Saldo", f"R$ {saldo:,.2f}")

        st.divider()

        if not df_fin.empty:
            fluxo = df_fin.groupby(["data", "tipo"])["valor"].sum().unstack().fillna(0)
            st.line_chart(fluxo)

    # =========================
    # 📈 VENDAS
    # =========================
    with tab3:

        if not df_vendas.empty:

            vendas_mes = df_vendas.groupby(
                df_vendas["data"].dt.to_period("M")
            )["valor_venda"].sum()

            st.subheader("📅 Vendas por mês")
            st.bar_chart(vendas_mes)

            st.divider()

            top_clientes = df_vendas.groupby("cliente")["valor_venda"].sum() \
                                    .sort_values(ascending=False).head(5)

            st.subheader("🏆 Top Clientes")
            st.dataframe(top_clientes)

            ticket_medio = df_vendas["valor_venda"].mean()
            st.metric("🎟 Ticket Médio", f"R$ {ticket_medio:,.2f}")

        else:
            st.info("Sem dados de vendas")

    # =========================
    # 🎯 METAS
    # =========================
    with tab4:

        meta_mensal = st.number_input("Meta mensal (R$)", value=10000.0)

        if not df_vendas.empty:

            mes_atual = pd.Timestamp.now().to_period("M")

            vendas_mes = df_vendas[
                df_vendas["data"].dt.to_period("M") == mes_atual
            ]["valor_venda"].sum()

            progresso = (vendas_mes / meta_mensal * 100) if meta_mensal > 0 else 0

            st.metric("📊 Vendas no mês", f"R$ {vendas_mes:,.2f}")
            st.progress(min(progresso / 100, 1.0))
            st.write(f"{progresso:.1f}% da meta")

        else:
            st.info("Sem vendas no mês")

    # =========================
    # 📦 PRODUTOS
    # =========================
    with tab5:

        if not df_itens.empty:

            ranking = df_itens.groupby("produto")["quantidade"].sum() \
                              .sort_values(ascending=False).head(10)

            st.subheader("🔥 Produtos mais utilizados")
            st.bar_chart(ranking)

            st.divider()

            categorias = df_itens.groupby("categoria")["quantidade"].sum()
            st.subheader("📊 Consumo por categoria")
            st.bar_chart(categorias)

        else:
            st.info("Sem dados de produtos")
    

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

                # 🔥 Apaga receita antiga
                cursor.execute(
                    "DELETE FROM receitas WHERE drink=?",
                    (st.session_state["drink_nome"],)
                )
                
                # 🔥 Insere novos ingredientes
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

                # limpa
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

                        custo_unitario = 0
                        uso_padrao = 1

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

                st.divider()

            # =========================
            # 🔥 EXCLUSÃO CENTRALIZADA
            # =========================
            st.markdown("---")
            st.subheader("🗑 Excluir drink")

            drink_excluir = st.selectbox("Selecione o drink", drinks)

            if st.button("Excluir drink"):
                cursor.execute(
                    "DELETE FROM receitas WHERE drink=?",
                    (drink_excluir,)
                )
                conn.commit()
                st.success(f"{drink_excluir} excluído com sucesso!")
                st.rerun()

elif menu == "Orçamentos":

    if "orcamento_bebidas" not in st.session_state:
        st.session_state["orcamento_bebidas"] = {}

    if "orcamento_frutas" not in st.session_state:
        st.session_state["orcamento_frutas"] = {}
    
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

        # =========================
        # EQUIPE DO EVENTO
        # =========================
        st.subheader("👥 Equipe")
        
        nomes_equipe = st.text_area(
            "Nomes da equipe (um por linha)",
            placeholder="Ex:\nJoão\nPedro\nLucas"
        )
        
        col1, col2 = st.columns(2)
        
        hora_chegada = col1.time_input("🕒 Chegada da equipe")
        hora_inicio = col2.time_input("🍸 Início do serviço")
        
        hora_convidados = st.time_input("👥 Chegada dos convidados")
        
        modo_calculo = st.radio(
            "Modo de cálculo",
            ["Evento inteiro", "Por hora"]
        )

        # =========================
        # CONFIG EVENTO
        # =========================
        st.subheader("Configuração do Evento")

        col1, col2, col3 = st.columns(3)

        num_convidados = col1.number_input("Convidados", min_value=1, value=50)
        horas = col2.number_input("Horas de evento", min_value=1, value=4)
        drinks_por_hora = col3.number_input("Drinks por pessoa/hora", min_value=0.5, value=2.0)

        if modo_calculo == "Evento inteiro":
            total_drinks = num_convidados * drinks_por_hora
        else:
            total_drinks = num_convidados * horas * drinks_por_hora
            
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
                            qtd_garrafas = int(qtd_real) + (1 if qtd_real % 1 > 0 else 0)
                
                            # 🔥 INTERFACE EDITÁVEL
                            col1, col2, col3 = st.columns([4,2,2])
                
                            with col1:
                                st.write(f"✔ {marca}")
                
                            with col2:
                                key_qtd = f"qtd_{marca}"

                            # se ainda não existe, cria valor inicial
                            if key_qtd not in st.session_state:
                                st.session_state[key_qtd] = qtd_garrafas
                            
                            qtd_editavel = st.number_input(
                                "Garrafas",
                                min_value=0,
                                key=key_qtd
                            )
                
                            with col3:
                                custo_item = qtd_editavel * preco
                                st.write(f"💰 R$ {custo_item:,.2f}")
                
                            # salva estado
                            st.session_state["orcamento_bebidas"][marca] = {
                                "quantidade": qtd_editavel,
                                "preco": preco
                            }
                
                            custo_bebidas += custo_item
                
                st.markdown(f"### 💰 Subtotal Bebidas: R$ {custo_bebidas:,.2f}")
                                
                # =========================
                # 📋 RESUMO BEBIDAS
                # =========================
                st.markdown("### 📋 Resumo Bebidas")
                
                for marca, dados in st.session_state["orcamento_bebidas"].items():
                    qtd = dados["quantidade"]
                    preco = dados["preco"]
                
                    total = qtd * preco
                
                    st.write(f"✔ {marca} → {qtd} garrafas | 💰 R$ {total:,.2f}")

                # =========================
                # FRUTAS
                # =========================
                st.subheader("🍋 Frutas")
                
                if "orcamento_frutas" not in st.session_state:
                    st.session_state["orcamento_frutas"] = {}
                
                custo_frutas = 0
                
                for fruta, qtd_gramas in ingredientes_insumos.items():
                
                    encontrado = df_insumos[
                        df_insumos["nome"].str.lower() == fruta
                    ]
                
                    if not encontrado.empty:
                
                        preco_kg = encontrado.iloc[0]["preco"]
                        custo_por_grama = preco_kg / 1000
                
                        col1, col2, col3 = st.columns([4,2,2])
                
                        with col1:
                            st.write(f"✔ {fruta.capitalize()}")
                
                        with col2:
                            key_qtd = f"qtd_fruta_{fruta.lower().strip()}"
                
                            if key_qtd not in st.session_state:
                                st.session_state[key_qtd] = float(qtd_gramas)
                
                            qtd_editavel = st.number_input(
                                "Gramas",
                                min_value=0.0,
                                key=key_qtd
                            )
                
                        with col3:
                            custo_item = qtd_editavel * custo_por_grama
                            st.write(f"💰 R$ {custo_item:,.2f}")
                
                        st.session_state["orcamento_frutas"][fruta] = {
                            "quantidade": qtd_editavel,
                            "preco_grama": custo_por_grama
                        }
                
                        custo_frutas += custo_item
                        
                # =========================
                # 📋 RESUMO FRUTAS
                # =========================
                st.markdown("### 📋 Resumo Frutas")
                
                for fruta, dados in st.session_state["orcamento_frutas"].items():
                    qtd = dados["quantidade"]
                    preco = dados["preco_grama"]
                
                    total = qtd * preco
                
                    st.write(f"✔ {fruta.capitalize()} → {qtd:.0f} g | 💰 R$ {total:,.2f}")
                
                # =========================
                # CUSTOS EXTRAS
                # =========================
                st.subheader("💸 Custos Extras")
                
                col1, col2, col3, col4 = st.columns(4)
                
                custo_gelo = col1.number_input("🧊 Gelo", min_value=0.0, format="%.2f")
                custo_transporte = col2.number_input("🚚 Transporte", min_value=0.0, format="%.2f")
                custo_viagem = col3.number_input("🛣️ Viagem / Km", min_value=0.0, format="%.2f")
                custo_caches = col4.number_input("👥 Cachês equipe", min_value=0.0, format="%.2f")
                
                custo_outros = st.number_input("📦 Outros custos", min_value=0.0, format="%.2f")
                
                custo_extras = (
                    custo_gelo +
                    custo_transporte +
                    custo_viagem +
                    custo_caches +
                    custo_outros
                )
                                
                # =========================
                # 📦 PACOTES / SERVIÇOS ADICIONAIS
                # =========================
                st.subheader("📦 Serviços Adicionais")
                
                df_pacotes = pd.read_sql("SELECT * FROM pacotes", conn)
                
                total_pacotes = 0
                
                if not df_pacotes.empty:
                
                    nomes_pacotes = df_pacotes["nome"].tolist()
                
                    pacotes_selecionados = st.multiselect(
                        "Selecione pacotes adicionais",
                        nomes_pacotes
                    )
                
                    for nome in pacotes_selecionados:
                
                        pacote = df_pacotes[df_pacotes["nome"] == nome].iloc[0]
                
                        preco_fixo = pacote["preco"] if "preco" in pacote else 0
                        preco_por_pessoa = pacote["preco_por_pessoa"] if "preco_por_pessoa" in pacote else 0
                
                        if preco_por_pessoa and preco_por_pessoa > 0:
                            total = preco_por_pessoa * num_convidados
                            st.write(f"✔ {nome} ({num_convidados} pessoas) → R$ {total:,.2f}")
                        else:
                            total = preco_fixo
                            st.write(f"✔ {nome} → R$ {total:,.2f}")
                
                        total_pacotes += total
                
                else:
                    st.info("Nenhum pacote cadastrado")
                
                st.markdown(f"### 💰 Total Pacotes: R$ {total_pacotes:,.2f}")
                
                # =========================
                # TOTAL
                # =========================
                custo_total = custo_bebidas + custo_frutas + custo_extras + total_pacotes
                
                st.divider()
                
                st.metric("💰 Custo Total do Evento (Bruto)", f"R$ {custo_total:,.2f}")
                st.markdown(f"### 💸 Extras: R$ {custo_extras:,.2f}")
                
                
                # =========================
                # MARGEM
                # =========================
                margem = st.slider("Margem de lucro (%)", 0, 300, 100)
                preco_venda = custo_total * (1 + margem / 100)
                
                st.metric("💰 Preço Final Sugerido", f"R$ {preco_venda:,.2f}")
                
                
                # =========================
                # DESCONTO
                # =========================
                st.subheader("💰 Desconto")
                
                desconto = st.slider("Desconto (%)", 0, 100, 0)
                
                preco_com_desconto = preco_venda * (1 - desconto / 100)
                
                st.metric("💸 Preço com desconto", f"R$ {preco_com_desconto:,.2f}")
                valor_desconto = preco_venda - preco_com_desconto

                st.metric(
                    "🔻 Desconto",
                    f"R$ {valor_desconto:,.2f}",
                    f"{desconto}%"
                )
                
                # =========================
                # LUCRO
                # =========================
                lucro = preco_com_desconto - custo_total
                
                if lucro < 0:
                    st.error("⚠️ Atenção: esse desconto gera PREJUÍZO!")
                else:
                    st.success(f"✅ Lucro estimado: R$ {lucro:,.2f}")
                
                
                # =========================
                # INDICADORES
                # =========================
                valor_por_convidado = preco_com_desconto / num_convidados if num_convidados > 0 else 0
                st.metric("💰 Valor cobrado por convidado", f"R$ {valor_por_convidado:,.2f}")
                
                valor_por_hora = preco_com_desconto / horas if horas > 0 else 0
                st.metric("⏱️ Valor por hora", f"R$ {valor_por_hora:,.2f}")
                
                
                # =========================
                # 💾 SALVAR ORÇAMENTO (RESTAURADO)
                # =========================
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
                        preco_com_desconto,  # ✅ agora salva com desconto
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
                
                    # =========================
                    # INFORMAÇÕES DO EVENTO
                    # =========================
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
                
                    # =========================
                    # 👥 EQUIPE (NOVO)
                    # =========================
                    st.markdown("### 👥 Equipe")
                
                    if "equipe" in row and row["equipe"]:
                        nomes = [n.strip() for n in row["equipe"].split("\n") if n.strip()]
                        
                        for nome in nomes:
                            st.write(f"✔ {nome}")
                    else:
                        st.write("Sem equipe definida")
                
                    # =========================
                    # ITENS DO EVENTO
                    # =========================
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

                    # Atualiza status
                    cursor.execute(
                        "UPDATE eventos SET status='aprovado' WHERE id=?",
                        (row["id"],)
                    )
                
                    # 🔥 PEGAR VALORES DO EVENTO
                    valor_venda = row["venda"] if "venda" in row else 0
                    custo = row["custo"] if "custo" in row else 0
                    lucro = valor_venda - custo
                
                    # 🔥 SALVAR NA TABELA VENDAS
                    cursor.execute("""
                    INSERT INTO vendas (evento_id, cliente, data, valor_venda, custo, lucro)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["id"],
                        row["cliente"],
                        row["data"],
                        valor_venda,
                        custo,
                        lucro
                    ))
                
                    # 🔥 LANÇAR NO FINANCEIRO (AUTOMÁTICO)
                    cursor.execute("""
                    INSERT INTO financeiro (data, tipo, descricao, valor)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        datetime.now().strftime("%Y-%m-%d"),
                        "Entrada",
                        f"Evento {row['cliente']}",
                        valor_venda
                    ))
                
                    conn.commit()
                    st.success("Evento aprovado e venda registrada!")
                    st.rerun()
                    alertas = []

                    # 🔥 baixa estoque
                    for marca, dados in st.session_state.get("orcamento_bebidas", {}).items():
                    
                        qtd_necessaria = dados["quantidade"]
                    
                        atual = pd.read_sql(
                            "SELECT * FROM estoque WHERE marca=?",
                            conn,
                            params=(marca,)
                        )
                    
                        if atual.empty:
                            alertas.append(f"❌ {marca} não existe no estoque")
                    
                        else:
                            qtd_atual = atual.iloc[0]["quantidade"]
                    
                            if qtd_atual < qtd_necessaria:
                                alertas.append(
                                    f"⚠️ {marca}: precisa {qtd_necessaria}, tem {qtd_atual}"
                                )
                    
                            nova_qtd = max(0, qtd_atual - qtd_necessaria)
                    
                            cursor.execute("""
                                UPDATE estoque
                                SET quantidade=?
                                WHERE marca=?
                            """, (nova_qtd, marca))
                    
                            cursor.execute("""
                                INSERT INTO movimentacoes
                                VALUES(?,?,?,?,?,?)
                            """,
                            (
                                datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "bebida",
                                marca,
                                "Saída (orçamento aprovado)",
                                qtd_necessaria,
                                "Reserva"
                            )
                            )
                    
                    # 🔥 atualiza status
                    cursor.execute(
                        "UPDATE eventos SET status='aprovado' WHERE id=?",
                        (row["id"],)
                    )
                    
                    conn.commit()
                    
                    # feedback
                    if alertas:
                        st.warning("⚠️ Problemas no estoque:")
                        for a in alertas:
                            st.write(a)
                    else:
                        st.success("✅ Evento aprovado e estoque atualizado!")
                    
                    # limpa memória
                    st.session_state["orcamento_bebidas"] = {}
                    
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
    
                if st.button(f"📋 Checklist aprovado {row['id']}", key=f"check_aprov_{row['id']}"):
    
                    itens = pd.read_sql("""
                        SELECT * FROM evento_itens WHERE evento_id=?
                    """, conn, params=(row["id"],))
    
                    st.subheader("📋 Checklist do Evento")
    
                    # =========================
                    # INFO DO EVENTO (SEM VALOR)
                    # =========================
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
                    """)
    
                    # =========================
                    # 👥 EQUIPE
                    # =========================
                    st.markdown("### 👥 Equipe")
    
                    if "equipe" in row and row["equipe"]:
                        nomes = [n.strip() for n in row["equipe"].split("\n") if n.strip()]
                        for nome in nomes:
                            st.write(f"✔ {nome}")
                    else:
                        st.write("Sem equipe definida")
    
                    # =========================
                    # ITENS
                    # =========================
                    if not itens.empty:
    
                        df_checklist = itens.copy()
    
                        def definir_categoria(unidade):
                            if unidade == "garrafas":
                                return "Bebidas"
                            elif unidade == "g":
                                return "Frutas"
                            else:
                                return "Outros"
    
                        df_checklist["Categoria"] = df_checklist["unidade"].apply(definir_categoria)
    
                        df_checklist["Início"] = ""
                        df_checklist["Fim"] = ""
    
                        st.dataframe(
                            df_checklist[["Categoria", "produto", "quantidade", "Início", "Fim"]]
                            .rename(columns={
                                "produto": "Produto",
                                "quantidade": "Qtde"
                            })
                        )
                    else:
                        st.warning("Nenhum item encontrado")
    
                # =========================
                # FINALIZAR EVENTO
                # =========================
                if st.button(f"✔ Finalizar {row['id']}", key=f"fin_{row['id']}"):
                    cursor.execute(
                        "UPDATE eventos SET status='finalizado' WHERE id=?",
                        (row["id"],)
                    )
                    conn.commit()
                    st.rerun()
    
                st.divider()

elif menu == "Cachês":

    st.title("👥 Cálculo de Cachês")

    # =========================
    # SUB ABAS
    # =========================
    subaba = st.radio("Escolha a visão", ["Resumo", "Por pessoa", "Histórico"])

    # =========================
    # VALORES BASE (GLOBAL)
    # =========================
    st.subheader("💰 Valores base")

    col1, col2, col3 = st.columns(3)

    valor_bartender = col1.number_input("Bartender", value=250.0)
    valor_barback = col2.number_input("Barback", value=180.0)
    valor_lider = col3.number_input("Líder", value=300.0)

    limite_horas = st.number_input("Horas inclusas", value=7.0)
    valor_hora_extra = st.number_input("💰 Hora extra", value=40.0)

    # =========================
    # 🔹 RESUMO
    # =========================
    if subaba == "Resumo":

        st.subheader("Equipe")

        col1, col2, col3 = st.columns(3)

        qtd_bartenders = col1.number_input("🍸 Bartenders", min_value=0, value=2)
        qtd_barbacks = col2.number_input("🧰 Barbacks", min_value=0, value=1)
        qtd_lider = col3.number_input("👑 Líder", min_value=0, max_value=1, value=1)

        st.subheader("Extras")

        col1, col2 = st.columns(2)

        qtd_carro = col1.number_input("🚗 Pessoas com carro", min_value=0, value=1)
        valor_carro = col2.number_input("💰 Ajuda carro", value=100.0)

        horas = st.number_input("⏱️ Horas totais", value=7.0)

        total_base = (
            qtd_bartenders * valor_bartender +
            qtd_barbacks * valor_barback +
            qtd_lider * valor_lider
        )

        horas_extra = max(0, horas - limite_horas)
        custo_horas_extra = horas_extra * valor_hora_extra * (
            qtd_bartenders + qtd_barbacks + qtd_lider
        )

        custo_carro = qtd_carro * valor_carro

        total_final = total_base + custo_horas_extra + custo_carro

        st.divider()

        st.metric("👥 Base", f"R$ {total_base:,.2f}")
        st.metric("⏱️ Extras", f"R$ {custo_horas_extra:,.2f}")
        st.metric("🚗 Transporte", f"R$ {custo_carro:,.2f}")
        st.metric("💸 Total", f"R$ {total_final:,.2f}")

    # =========================
    # 🔹 POR PESSOA
    # =========================
    elif subaba == "Por pessoa":

        st.subheader("👤 Pagamento individual")

        evento_nome = st.text_input("Nome do evento")

        qtd_pessoas = st.number_input(
            "Quantidade de pessoas",
            min_value=1,
            max_value=20,
            value=3
        )

        total_geral = 0
        dados_pagamento = []

        for i in range(qtd_pessoas):

            st.markdown(f"### 👤 Profissional {i+1}")

            col1, col2, col3 = st.columns(3)

            nome = col1.text_input("Nome", key=f"nome_{i}")

            funcao = col2.selectbox(
                "Função",
                ["Bartender", "Barback", "Líder"],
                key=f"funcao_{i}"
            )

            horas = col3.number_input(
                "Horas",
                value=7.0,
                key=f"horas_{i}"
            )

            if funcao == "Bartender":
                valor_base = valor_bartender
            elif funcao == "Barback":
                valor_base = valor_barback
            else:
                valor_base = valor_lider

            horas_extra = max(0, horas - limite_horas)
            pagamento = valor_base + (horas_extra * valor_hora_extra)

            st.metric(
                f"💰 {nome if nome else f'Pessoa {i+1}'}",
                f"R$ {pagamento:,.2f}"
            )

            total_geral += pagamento

            dados_pagamento.append((evento_nome, nome, funcao, pagamento))

        st.divider()
        st.metric("💸 Total equipe", f"R$ {total_geral:,.2f}")

        # SALVAR
        if st.button("💾 Salvar pagamentos"):

            for dados in dados_pagamento:

                cursor.execute("""
                    INSERT INTO pagamentos_equipe (evento, nome, funcao, valor)
                    VALUES (?, ?, ?, ?)
                """, dados)

            conn.commit()
            st.success("✅ Pagamentos salvos!")

    # =========================
    # 🔹 HISTÓRICO
    # =========================
    elif subaba == "Histórico":

        st.subheader("📊 Histórico de pagamentos")

        df_pagamentos = pd.read_sql(
            "SELECT * FROM pagamentos_equipe ORDER BY data DESC",
            conn
        )

        st.dataframe(df_pagamentos)


elif menu == "Vendas":

    st.title("📊 Vendas")

    df = pd.read_sql("SELECT * FROM vendas", conn)

    # estrutura vazia
    if df.empty:
        df = pd.DataFrame(columns=[
            "evento_id",
            "cliente",
            "data",
            "valor_venda",
            "custo",
            "lucro"
        ])

    # KPIs
    total_vendas = df["valor_venda"].sum()
    total_custo = df["custo"].sum()
    total_lucro = df["lucro"].sum()

    margem = (total_lucro / total_vendas * 100) if total_vendas > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Receita", f"R$ {total_vendas:,.2f}")
    col2.metric("💸 Custo", f"R$ {total_custo:,.2f}")
    col3.metric("📈 Lucro", f"R$ {total_lucro:,.2f}")
    col4.metric("📊 Margem", f"{margem:.1f}%")

    st.markdown("---")

    # filtro
    cliente = st.text_input("Buscar cliente")

    if cliente:
        df = df[df["cliente"].str.contains(cliente, case=False)]

    # tabela
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "valor_venda": st.column_config.NumberColumn("💰 Venda", format="R$ %.2f"),
            "custo": st.column_config.NumberColumn("💸 Custo", format="R$ %.2f"),
            "lucro": st.column_config.NumberColumn("📈 Lucro", format="R$ %.2f"),
        }
    )

    # gráfico
    st.markdown("---")
    st.subheader("📊 Evolução das vendas")

    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
        vendas_por_data = df.groupby("data")["valor_venda"].sum()
        st.line_chart(vendas_por_data)
    else:
        st.info("Sem dados ainda")

    if df.empty:
        st.warning("Nenhuma venda registrada ainda — aparecerá ao aprovar eventos.")

elif menu == "Financeiro":

    st.title("💰 Financeiro")

    tab1, tab2, tab3 = st.tabs([
        "📊 Resumo",
        "➕ Lançamentos",
        "📄 Extrato"
    ])

    # =========================
    # 📊 RESUMO
    # =========================
    with tab1:

        df = pd.read_sql("SELECT * FROM financeiro", conn)

        if df.empty:
            entrada = 0
            saida = 0
        else:
            entrada = df[df["tipo"] == "Entrada"]["valor"].sum()
            saida = df[df["tipo"] == "Saída"]["valor"].sum()

        saldo = entrada - saida

        # KPIs
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("💰 Entradas", f"R$ {entrada:,.2f}")
        col2.metric("💸 Saídas", f"R$ {saida:,.2f}")
        col3.metric("🏦 Saldo", f"R$ {saldo:,.2f}")
        col4.metric("📈 Resultado", f"R$ {saldo:,.2f}")

        st.markdown("---")

        if not df.empty:

            df["data"] = pd.to_datetime(df["data"])

            # 📊 mensal
            df["mes"] = df["data"].dt.to_period("M")
            mensal = df.groupby(["mes", "tipo"])["valor"].sum().unstack().fillna(0)

            st.subheader("📊 Resultado mensal")
            st.bar_chart(mensal)

            # 💸 gastos
            st.subheader("💸 Gastos por categoria")
            gastos = df[df["tipo"] == "Saída"].groupby("categoria")["valor"].sum()
            st.dataframe(gastos)

            # 💳 entradas por forma
            st.subheader("💳 Entradas por forma")
            formas = df[df["tipo"] == "Entrada"].groupby("forma_pagamento")["valor"].sum()
            st.dataframe(formas)

            # 🏦 saldo acumulado
            df_ordenado = df.sort_values("data")

            df_ordenado["fluxo"] = df_ordenado.apply(
                lambda x: x["valor"] if x["tipo"] == "Entrada" else -x["valor"],
                axis=1
            )

            df_ordenado["saldo_acumulado"] = df_ordenado["fluxo"].cumsum()

            st.subheader("🏦 Evolução do caixa")
            st.line_chart(df_ordenado.set_index("data")["saldo_acumulado"])

            # alerta
            if saida > entrada:
                st.error("⚠️ Você está gastando mais do que ganha!")

    # =========================
    # ➕ LANÇAMENTOS
    # =========================
    with tab2:

        with st.form("novo_lancamento", clear_on_submit=True):

            tipo = st.selectbox("Tipo", ["Entrada", "Saída"])

            valor = st.number_input("Valor", min_value=0.0)

            categoria = st.selectbox(
                "Categoria",
                ["Evento", "Bebidas", "Equipe", "Transporte", "Marketing", "Outros"]
            )

            forma = st.selectbox(
                "Forma de pagamento",
                ["Dinheiro", "Pix", "Cartão", "Transferência"]
            )

            descricao = st.text_input("Descrição")

            if st.form_submit_button("Salvar lançamento"):

                cursor.execute("""
                INSERT INTO financeiro 
                (data, tipo, categoria, forma_pagamento, descricao, valor)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().strftime("%Y-%m-%d"),
                    tipo,
                    categoria,
                    forma,
                    descricao,
                    valor
                ))

                conn.commit()
                st.success("Lançamento registrado!")

    # =========================
    # 📄 EXTRATO
    # =========================
    with tab3:

        df = pd.read_sql(
            "SELECT * FROM financeiro ORDER BY data DESC",
            conn
        )

        if df.empty:
            st.info("Nenhum lançamento ainda")
        else:

            filtro = st.selectbox(
                "Filtrar tipo",
                ["Todos", "Entrada", "Saída"]
            )

            if filtro != "Todos":
                df = df[df["tipo"] == filtro]

            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "valor": st.column_config.NumberColumn(
                        "💰 Valor",
                        format="R$ %.2f"
                    )
                }
            )

elif menu == "Pacotes":

    st.title("📦 Pacotes / Serviços")

    import json

    tab1, tab2 = st.tabs(["Cadastrar","Lista"])

    # -------------------------
    # CADASTRAR PACOTE
    # -------------------------
    with tab1:

        nome = st.text_input("Nome do pacote")

        tipo = st.text_input("Tipo do serviço (livre)")

        st.markdown("### 🍸 Bebidas do pacote")

        df_bebidas = pd.read_sql("SELECT * FROM precos_bebidas", conn)
        
        itens_pacote = []
        
        custo_total_pacote = 0
        
        if not df_bebidas.empty:
        
            bebidas_selecionadas = st.multiselect(
                "Selecione as bebidas",
                df_bebidas["nome"]
            )
        
            for bebida in bebidas_selecionadas:
        
                dados = df_bebidas[df_bebidas["nome"] == bebida].iloc[0]
        
                preco = dados["preco"]
                volume = dados["quantidade"]
        
                col1, col2, col3 = st.columns([4,2,2])
        
                with col1:
                    st.write(f"✔ {bebida}")
        
                with col2:
                    qtd = st.number_input(
                        "Qtd",
                        min_value=0,
                        key=f"pac_{bebida}"
                    )
        
                with col3:
                    total_item = qtd * preco
                    st.write(f"💰 R$ {total_item:,.2f}")
        
                custo_total_pacote += total_item
        
                itens_pacote.append({
                    "nome": bebida,
                    "quantidade": qtd,
                    "preco": preco
                })
        
        st.markdown(f"### 💸 Custo total das bebidas: R$ {custo_total_pacote:,.2f}")

        st.markdown("### 🧊 Extras do pacote")

        # -------------------------
        # ESTADO
        # -------------------------
        if "extras_lista" not in st.session_state:
            st.session_state["extras_lista"] = []
        
        # -------------------------
        # INPUTS
        # -------------------------
        col1, col2, col3 = st.columns([4,2,1])
        
        with col1:
            nome_extra = st.text_input("Nome do extra", placeholder="Ex: 45 esferas de gelo translúcido")
        
        with col2:
            valor_extra = st.number_input("Valor", min_value=0.0, format="%.2f")
        
        with col3:
            if st.button("➕"):
                if nome_extra:
                    st.session_state["extras_lista"].append({
                        "nome": nome_extra,
                        "valor": valor_extra
                    })
        
        # -------------------------
        # LISTA
        # -------------------------
        total_extras = 0
        
        if st.session_state["extras_lista"]:
        
            st.markdown("### 📋 Extras adicionados")
        
            for i, extra in enumerate(st.session_state["extras_lista"]):
        
                col1, col2, col3 = st.columns([4,2,1])
        
                with col1:
                    st.write(f"✔ {extra['nome']}")
        
                with col2:
                    st.write(f"R$ {extra['valor']:,.2f}")
        
                with col3:
                    if st.button("❌", key=f"del_extra_{i}"):
                        st.session_state["extras_lista"].pop(i)
                        st.rerun()
        
                total_extras += extra["valor"]
        
        st.markdown(f"### 💰 Total Extras: R$ {total_extras:,.2f}")
        
        st.markdown("### 💰 Precificação")

        custo = custo_total_pacote + total_extras
        
        st.info(f"Custo automático: R$ {custo:,.2f}")
        
        # -------------------------
        # MARGEM
        # -------------------------
        margem = st.slider("Margem de lucro (%)", 0, 300, 100)
        
        preco_sugerido = custo * (1 + margem / 100)
        
        st.metric("💡 Preço sugerido", f"R$ {preco_sugerido:,.2f}")
        
        # -------------------------
        # PREÇO FINAL (EDITÁVEL)
        # -------------------------
        preco = st.number_input(
            "Preço de venda final",
            min_value=0.0,
            value=float(preco_sugerido)
        )
        
        # -------------------------
        # LUCRO
        # -------------------------
        lucro_preview = preco - custo
        
        if lucro_preview < 0:
            st.error(f"⚠️ Prejuízo: R$ {lucro_preview:,.2f}")
        else:
            st.success(f"✅ Lucro estimado: R$ {lucro_preview:,.2f}")
        
        st.info(f"Lucro estimado: R$ {lucro_preview:,.2f}")

        if st.button("💾 Salvar pacote"):

            dados = json.dumps({
                "bebidas": itens_pacote,
                "extras": st.session_state["extras_lista"]
            })

            cursor.execute("""
            INSERT INTO pacotes (nome, tipo, dados, preco, custo)
            VALUES (?,?,?,?,?)
            """,(nome, tipo, dados, preco, custo))

            conn.commit()

            st.success("Pacote salvo!")
            st.session_state["extras_lista"] = []

        # -------------------------
        # MARKUP (AQUI)
        # -------------------------
        if custo > 0:
            markup = preco / custo
            st.metric("📊 Markup", f"{markup:.2f}x")

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

            for b in dados.get("bebidas", []):
                st.write(f"✔ {b['nome']} - {b['quantidade']} un")

            st.subheader(pacote["nome"])

            lucro = (pacote["preco"] or 0) - (pacote["custo"] or 0)

            st.write(f"💰 Preço: R$ {pacote['preco']}")
            st.write(f"💸 Custo: R$ {pacote['custo']}")
            st.write(f"📈 Lucro: R$ {lucro}")

            st.write("📦 Itens:")
            for i in dados["itens"]:
                if i:
                    st.write(f"✔ {i}")

            st.write("✨ Extras:")

            for e in dados.get("extras", []):
                st.write(f"+ {e['nome']} → R$ {e['valor']:,.2f}")

            if st.button("🗑 Excluir pacote"):
                cursor.execute("DELETE FROM pacotes WHERE id = ?", (id_sel,))
                conn.commit()
                st.rerun()
