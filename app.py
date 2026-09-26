import os
import streamlit as st
def normalizar_nome(nome):
    return str(nome).strip().lower()
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta, date
from servicos import SERVICOS

SUPABASE_URL = "https://tkidpoirwnolgzknsohj.supabase.co"
SUPABASE_KEY = "sb_publishable_m4uQvOAi0D10f8Wj8GyqMQ_vZKa5GeM"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="Ellosystem",
    layout="wide"
)

# =========================================================
# FUNÇÕES GERAIS
# =========================================================

def carregar_tabela(nome):
    """
    Carrega uma tabela do Supabase e retorna um DataFrame.
    """

    try:

        response = (
            supabase
            .table(nome)
            .select("*")
            .execute()
        )

        if response.data:

            return pd.DataFrame(response.data)

        return pd.DataFrame()

    except Exception as e:

        st.error(
            f"Erro ao carregar a tabela '{nome}': {e}"
        )

        return pd.DataFrame()


# =========================================================
# CUSTO DE DRINK
# =========================================================

def calcular_custo_drink(
    drink,
    df_receitas,
    df_bebidas,
    df_insumos
):

    if df_receitas.empty:

        return 0

    receita = df_receitas[
        df_receitas["drink"] == drink
    ]

    custo_total = 0

    for _, row in receita.iterrows():

        ingrediente = normalizar_nome(
            row.get("ingrediente", "")
        )

        quantidade = float(
            row.get("quantidade", 0) or 0
        )

        if not ingrediente or quantidade <= 0:

            continue

        # -------------------------------------------------
        # PROCURAR NAS BEBIDAS
        # -------------------------------------------------

        if not df_bebidas.empty:

            bebida = df_bebidas[
                df_bebidas["nome"]
                .astype(str)
                .str.strip()
                .str.lower()
                ==
                ingrediente.lower()
            ]

            if not bebida.empty:

                preco = float(
                    bebida.iloc[0].get(
                        "preco",
                        0
                    ) or 0
                )

                volume = float(
                    bebida.iloc[0].get(
                        "quantidade",
                        0
                    ) or 0
                )

                if volume > 0:

                    custo_total += (
                        quantidade / volume
                    ) * preco

                    continue

        # -------------------------------------------------
        # PROCURAR NOS INSUMOS
        # -------------------------------------------------

        if not df_insumos.empty:

            insumo = df_insumos[
                df_insumos["nome"]
                .astype(str)
                .str.strip()
                .str.lower()
                ==
                ingrediente.lower()
            ]

            if not insumo.empty:

                preco = float(
                    insumo.iloc[0].get(
                        "preco",
                        0
                    ) or 0
                )

                custo_total += (
                    quantidade / 1000
                ) * preco

    return round(custo_total, 2)


# =========================================================
# INGREDIENTES DO DRINK
# =========================================================

def ingredientes_do_drink(
    drink,
    df_receitas
):

    if df_receitas.empty:

        return []

    receita = df_receitas[
        df_receitas["drink"] == drink
    ]

    ingredientes = []

    for _, row in receita.iterrows():

        ingrediente = normalizar_nome(
            row.get("ingrediente", "")
        )

        if ingrediente:

            ingredientes.append(
                ingrediente
            )

    return ingredientes


# =========================================================
# CUSTO DE UM INGREDIENTE
# =========================================================

def calcular_custo_ingrediente(
    ingrediente,
    quantidade,
    unidade
):

    ingrediente = normalizar_nome(
        ingrediente
    )

    if not ingrediente:

        return 0

    # -----------------------------------------------------
    # BEBIDAS
    # -----------------------------------------------------

    if not df_bebidas_global.empty:

        item = df_bebidas_global[
            df_bebidas_global["nome"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            ingrediente.lower()
        ]

        if not item.empty:

            custo_unitario = float(
                item.iloc[0].get(
                    "custo",
                    0
                ) or 0
            )

            # O campo "custo" representa
            # o custo da quantidade de uso cadastrada.
            uso_cadastrado = float(
                item.iloc[0].get(
                    "uso",
                    0
                ) or 0
            )

            if uso_cadastrado > 0:

                return (
                    custo_unitario
                    *
                    quantidade
                    /
                    uso_cadastrado
                )

            return custo_unitario

    # -----------------------------------------------------
    # INSUMOS
    # -----------------------------------------------------

    if not df_insumos_global.empty:

        item = df_insumos_global[
            df_insumos_global["nome"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            ingrediente.lower()
        ]

        if not item.empty:

            custo_unitario = float(
                item.iloc[0].get(
                    "custo",
                    0
                ) or 0
            )

            uso_cadastrado = float(
                item.iloc[0].get(
                    "uso",
                    0
                ) or 0
            )

            if uso_cadastrado > 0:

                return (
                    custo_unitario
                    *
                    quantidade
                    /
                    uso_cadastrado
                )

            return custo_unitario

    return 0


# =========================================================
# SERVIÇO PERSONALIZADO
# =========================================================

def tela_servico_personalizado():

    st.subheader(
        "👷 Serviço Personalizado"
    )

    st.info(
        "Orçamento para eventos onde "
        "o cliente fornece as bebidas."
    )


# =========================================================
# CARREGAMENTO GLOBAL
# =========================================================

df_bebidas_global = carregar_tabela(
    "precos_bebidas"
)

df_insumos_global = carregar_tabela(
    "precos_insumos"
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "🍸 Ellosystem"
)

menu = st.sidebar.radio(
    "Menu",
    [
        "Relatórios",
        "Eventos",
        "Copos, Taças e Decor",
        "Materiais e Utensílios de Bar",
        "Precificação",
        "Estoque",
        "Receitas",
        "Orçamentos",
        "Cachês",
        "Vendas",
        "CMV",
        "Financeiro",
        "Pacotes"
    ]
)

# =========================================================
# TELA — COPOS, TAÇAS E DECOR
# =========================================================

def tela_copos_tacas_decor():

    st.title("🥂 Copos, Taças e Decor")

    st.caption(
        "Cadastro dos materiais utilizados nos eventos. "
        "Copos e taças serão utilizados posteriormente "
        "para identificar o recipiente de cada drink."
    )

    # =====================================================
    # ABAS
    # =====================================================

    aba_copos, aba_decor = st.tabs(
        [
            "🥂 Copos e Taças",
            "🎀 Materiais Decorativos"
        ]
    )

    # =====================================================
    # ABA — COPOS E TAÇAS
    # =====================================================

    with aba_copos:

        st.subheader("🥂 Copos e Taças")

        st.info(
            "Cadastre aqui os copos e taças disponíveis "
            "para utilização nos eventos."
        )

        # -------------------------------------------------
        # CADASTRO
        # -------------------------------------------------

        st.markdown("### ➕ Cadastrar Copo ou Taça")

        with st.form(
            "form_copos_tacas",
            clear_on_submit=True
        ):

            col1, col2 = st.columns(2)

            with col1:

                tipo = st.selectbox(
                    "Tipo",
                    [
                        "Copo",
                        "Taça"
                    ],
                    key="tipo_copo_taca"
                )

                nome = st.text_input(
                    "Nome",
                    placeholder="Ex.: Long Drink",
                    key="nome_copo_taca"
                )

                modelo = st.text_input(
                    "Modelo",
                    placeholder="Ex.: Cristal",
                    key="modelo_copo_taca"
                )

            with col2:

                capacidade = st.number_input(
                    "Capacidade (ml)",
                    min_value=0.0,
                    step=10.0,
                    format="%.0f",
                    key="capacidade_copo_taca"
                )

                quantidade = st.number_input(
                    "Quantidade disponível",
                    min_value=0,
                    step=1,
                    format="%d",
                    key="quantidade_copo_taca"
                )

                observacao = st.text_input(
                    "Observação",
                    placeholder="Ex.: Guardado no estoque principal",
                    key="observacao_copo_taca"
                )

            cadastrar = st.form_submit_button(
                "💾 Cadastrar"
            )

        if cadastrar:

            if not nome.strip():

                st.error(
                    "Informe o nome do copo ou taça."
                )

            elif quantidade <= 0:

                st.error(
                    "A quantidade deve ser maior que zero."
                )

            else:

                st.success(
                    "✅ Cadastro preparado com sucesso!"
                )

                st.info(
                    "A gravação no Supabase será ativada "
                    "assim que criarmos a tabela."
                )


        st.divider()

        # -------------------------------------------------
        # LISTA
        # -------------------------------------------------

        st.markdown("### 📋 Lista de Copos e Taças")

        st.info(
            "A lista será carregada do Supabase "
            "quando a tabela for criada."
        )


    # =====================================================
    # ABA — MATERIAIS DECORATIVOS
    # =====================================================

    with aba_decor:

        st.subheader("🎀 Materiais Decorativos")

        st.info(
            "Cadastre aqui os materiais utilizados "
            "na decoração dos eventos."
        )

        # -------------------------------------------------
        # CADASTRO
        # -------------------------------------------------

        st.markdown("### ➕ Cadastrar Material Decorativo")

        with st.form(
            "form_materiais_decorativos",
            clear_on_submit=True
        ):

            col1, col2 = st.columns(2)

            with col1:

                nome_decor = st.text_input(
                    "Nome do material",
                    placeholder="Ex.: Vaso de mesa",
                    key="nome_material_decorativo"
                )

                categoria = st.selectbox(
                    "Categoria",
                    [
                        "Mesa",
                        "Bar",
                        "Ambientação",
                        "Iluminação",
                        "Identificação",
                        "Outros"
                    ],
                    key="categoria_material_decorativo"
                )

            with col2:

                quantidade_decor = st.number_input(
                    "Quantidade disponível",
                    min_value=0,
                    step=1,
                    format="%d",
                    key="quantidade_material_decorativo"
                )

                observacao_decor = st.text_input(
                    "Observação",
                    placeholder="Ex.: Material frágil",
                    key="observacao_material_decorativo"
                )

            cadastrar_decor = st.form_submit_button(
                "💾 Cadastrar"
            )

        if cadastrar_decor:

            if not nome_decor.strip():

                st.error(
                    "Informe o nome do material."
                )

            elif quantidade_decor <= 0:

                st.error(
                    "A quantidade deve ser maior que zero."
                )

            else:

                st.success(
                    "✅ Cadastro preparado com sucesso!"
                )

                st.info(
                    "A gravação no Supabase será ativada "
                    "assim que criarmos a tabela."
                )


        st.divider()

        # -------------------------------------------------
        # LISTA
        # -------------------------------------------------

        st.markdown(
            "### 📋 Lista de Materiais Decorativos"
        )

        st.info(
            "A lista será carregada do Supabase "
            "quando a tabela for criada."
        )

# =========================================================
# TELA DE PRECIFICAÇÃO
# =========================================================

def tela_precificacao(
    nome_tabela
):

    aba_cadastro, aba_lista = st.tabs(
        [
            "Cadastrar",
            "Lista"
        ]
    )


    # =====================================================
    # CADASTRO
    # =====================================================

    with aba_cadastro:

        with st.form(
            f"form_{nome_tabela}",
            clear_on_submit=True
        ):

            tipo = st.text_input(
                "Tipo do item",
                key=f"tipo_{nome_tabela}"
            )

            nome = st.text_input(
                "Nome / Marca",
                key=f"nome_{nome_tabela}"
            )

            quantidade = st.number_input(
                "Quantidade total",
                min_value=0.0,
                step=1.0,
                format="%.2f",
                key=f"quantidade_{nome_tabela}"
            )

            preco = st.number_input(
                "Preço",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key=f"preco_{nome_tabela}"
            )

            uso = st.number_input(
                "Quantidade usada no drink",
                min_value=0.0,
                step=1.0,
                format="%.2f",
                key=f"uso_{nome_tabela}"
            )

            cadastrar = st.form_submit_button(
                "💾 Cadastrar"
            )


        if cadastrar:

            if not nome.strip():

                st.error(
                    "Informe o nome do item."
                )

            elif quantidade <= 0:

                st.error(
                    "A quantidade total deve ser maior que zero."
                )

            elif preco <= 0:

                st.error(
                    "O preço deve ser maior que zero."
                )

            elif uso <= 0:

                st.error(
                    "A quantidade de uso deve ser maior que zero."
                )

            else:

                # -----------------------------------------
                # BEBIDAS E ARTESANAIS
                # -----------------------------------------

                quantidade_real = quantidade

                # -----------------------------------------
                # INSUMOS
                # -----------------------------------------

                if nome_tabela == "precos_insumos":

                    quantidade_real = (
                        quantidade * 1000
                    )

                rendimento = (
                    quantidade_real / uso
                )

                custo = (
                    preco / rendimento
                    if rendimento > 0
                    else 0
                )

                try:

                    supabase.table(
                        nome_tabela
                    ).insert({

                        "tipo":
                            tipo.strip(),

                        "nome":
                            normalizar_nome(nome),

                        "quantidade":
                            quantidade,

                        "preco":
                            preco,

                        "uso":
                            uso,

                        "rendimento":
                            rendimento,

                        "custo":
                            custo

                    }).execute()

                    st.success(
                        "✅ Item cadastrado com sucesso!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Erro ao cadastrar: {e}"
                    )


    # =====================================================
    # LISTA
    # =====================================================

    with aba_lista:

        dados = (
            supabase
            .table(nome_tabela)
            .select("*")
            .execute()
        )

        df = pd.DataFrame(
            dados.data
            if dados.data
            else []
        )

        if df.empty:

            st.info(
                "Nenhum item cadastrado."
            )

            return


        busca = st.text_input(
            "🔎 Pesquisar",
            key=f"busca_{nome_tabela}"
        )


        if busca:

            busca = busca.strip()

            filtro_nome = (
                df["nome"]
                .fillna("")
                .astype(str)
                .str.contains(
                    busca,
                    case=False,
                    na=False
                )
            )

            filtro_tipo = (
                df["tipo"]
                .fillna("")
                .astype(str)
                .str.contains(
                    busca,
                    case=False,
                    na=False
                )
            )

            df = df[
                filtro_nome
                |
                filtro_tipo
            ]


        if df.empty:

            st.info(
                "Nenhum item encontrado."
            )

            return


        # -------------------------------------------------
        # EDITOR
        # -------------------------------------------------

        df_editado = st.data_editor(

            df,

            use_container_width=True,

            hide_index=True,

            column_config={

                "id":
                    st.column_config.NumberColumn(
                        "ID",
                        disabled=True
                    ),

                "tipo":
                    st.column_config.TextColumn(
                        "Tipo"
                    ),

                "nome":
                    st.column_config.TextColumn(
                        "Nome / Marca"
                    ),

                "quantidade":
                    st.column_config.NumberColumn(
                        "Quantidade"
                    ),

                "preco":
                    st.column_config.NumberColumn(
                        "💰 Preço",
                        format="R$ %.2f"
                    ),

                "uso":
                    st.column_config.NumberColumn(
                        "Uso"
                    ),

                "rendimento":
                    st.column_config.NumberColumn(
                        "Rendimento",
                        disabled=True
                    ),

                "custo":
                    st.column_config.NumberColumn(
                        "💰 Custo por uso",
                        format="R$ %.2f",
                        disabled=True
                    )
            }
        )


        # =================================================
        # SALVAR ALTERAÇÕES
        # =================================================

        if st.button(
            "💾 Salvar alterações",
            key=f"save_{nome_tabela}"
        ):

            try:

                for _, row in df_editado.iterrows():

                    quantidade = float(
                        row["quantidade"]
                        or 0
                    )

                    uso = float(
                        row["uso"]
                        or 0
                    )

                    preco = float(
                        row["preco"]
                        or 0
                    )

                    # -------------------------------------
                    # RECALCULAR
                    # -------------------------------------

                    if (
                        quantidade <= 0
                        or uso <= 0
                        or preco < 0
                    ):

                        rendimento = 0
                        custo = 0

                    else:

                        quantidade_real = quantidade

                        if (
                            nome_tabela
                            ==
                            "precos_insumos"
                        ):

                            quantidade_real = (
                                quantidade * 1000
                            )

                        rendimento = (
                            quantidade_real / uso
                        )

                        custo = (
                            preco / rendimento
                            if rendimento > 0
                            else 0
                        )


                    # -------------------------------------
                    # ATUALIZAR
                    # -------------------------------------

                    supabase.table(
                        nome_tabela
                    ).update({

                        "tipo":
                            str(
                                row["tipo"]
                            ).strip(),

                        "nome":
                            normalizar_nome(
                                row["nome"]
                            ),

                        "quantidade":
                            quantidade,

                        "preco":
                            preco,

                        "uso":
                            uso,

                        "rendimento":
                            rendimento,

                        "custo":
                            custo

                    }).eq(
                        "id",
                        row["id"]
                    ).execute()


                st.success(
                    "✅ Alterações salvas!"
                )

                st.rerun()


            except Exception as e:

                st.error(
                    f"Erro ao salvar: {e}"
                )


        # =================================================
        # EXCLUIR
        # =================================================

        st.divider()

        item = st.selectbox(
            "Selecionar item para excluir",
            df["id"].tolist(),
            key=f"del_{nome_tabela}"
        )

        if st.button(
            "🗑️ Excluir selecionado",
            key=f"btn_delete_{nome_tabela}"
        ):

            try:

                supabase.table(
                    nome_tabela
                ).delete().eq(
                    "id",
                    item
                ).execute()

                st.success(
                    "Item excluído."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Erro ao excluir: {e}"
                )


# =========================================================
# TELA DE INSUMOS / FRUTAS
# =========================================================

def tela_insumos():

    aba_cadastro, aba_lista = st.tabs(
        [
            "Cadastrar",
            "Lista"
        ]
    )


    # =====================================================
    # CADASTRO
    # =====================================================

    with aba_cadastro:

        st.info(
            "📌 Cadastro de frutas:\n"
            "- Quantidade sempre em KG\n"
            "- Preço por KG\n"
            "- Uso sempre em GRAMAS"
        )


        with st.form(
            "form_insumos",
            clear_on_submit=True
        ):

            nome = st.text_input(
                "Nome da fruta"
            )

            quantidade = st.number_input(
                "Quantidade (KG)",
                min_value=0.0,
                step=0.01,
                format="%.2f"
            )

            preco = st.number_input(
                "Preço (por KG)",
                min_value=0.0,
                step=0.01,
                format="%.2f"
            )

            uso = st.number_input(
                "Uso por receita (GRAMAS)",
                min_value=1.0,
                value=25.0,
                step=1.0,
                format="%.2f"
            )

            cadastrar = st.form_submit_button(
                "💾 Cadastrar"
            )


        if cadastrar:

            if not nome.strip():

                st.error(
                    "Informe o nome da fruta."
                )

            elif quantidade <= 0:

                st.error(
                    "Quantidade deve ser maior que zero."
                )

            elif preco <= 0:

                st.error(
                    "Preço deve ser maior que zero."
                )

            elif uso <= 0:

                st.error(
                    "Uso deve ser maior que zero."
                )

            else:

                quantidade_gramas = (
                    quantidade * 1000
                )

                rendimento = (
                    quantidade_gramas / uso
                )

                custo = (
                    preco / rendimento
                )

                try:

                    supabase.table(
                        "precos_insumos"
                    ).insert({

                        "tipo":
                            "fruta",

                        "nome":
                            normalizar_nome(nome),

                        "quantidade":
                            quantidade,

                        "preco":
                            preco,

                        "uso":
                            uso,

                        "rendimento":
                            rendimento,

                        "custo":
                            custo

                    }).execute()

                    st.success(
                        "✅ Fruta cadastrada corretamente!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Erro ao cadastrar: {e}"
                    )


    # =====================================================
    # LISTA
    # =====================================================

    with aba_lista:

        dados = (
            supabase
            .table("precos_insumos")
            .select("*")
            .execute()
        )

        df = pd.DataFrame(
            dados.data
            if dados.data
            else []
        )


        if df.empty:

            st.info(
                "Nenhuma fruta cadastrada."
            )

            return


        df_editado = st.data_editor(

            df,

            use_container_width=True,

            hide_index=True,

            column_config={

                "id":
                    st.column_config.NumberColumn(
                        "ID",
                        disabled=True
                    ),

                "tipo":
                    st.column_config.TextColumn(
                        "Tipo"
                    ),

                "nome":
                    st.column_config.TextColumn(
                        "Nome"
                    ),

                "quantidade":
                    st.column_config.NumberColumn(
                        "Quantidade (KG)"
                    ),

                "preco":
                    st.column_config.NumberColumn(
                        "💰 Preço (KG)",
                        format="R$ %.2f"
                    ),

                "uso":
                    st.column_config.NumberColumn(
                        "Uso (g)"
                    ),

                "rendimento":
                    st.column_config.NumberColumn(
                        "Rendimento",
                        disabled=True
                    ),

                "custo":
                    st.column_config.NumberColumn(
                        "💰 Custo por uso",
                        format="R$ %.2f",
                        disabled=True
                    )
            }
        )


        # =================================================
        # SALVAR
        # =================================================

        if st.button(
            "💾 Salvar alterações insumos"
        ):

            try:

                for _, row in df_editado.iterrows():

                    quantidade = float(
                        row["quantidade"]
                        or 0
                    )

                    preco = float(
                        row["preco"]
                        or 0
                    )

                    uso = float(
                        row["uso"]
                        or 0
                    )


                    if (
                        quantidade <= 0
                        or preco < 0
                        or uso <= 0
                    ):

                        rendimento = 0
                        custo = 0

                    else:

                        quantidade_gramas = (
                            quantidade * 1000
                        )

                        rendimento = (
                            quantidade_gramas / uso
                        )

                        custo = (
                            preco / rendimento
                        )


                    supabase.table(
                        "precos_insumos"
                    ).update({

                        "tipo":
                            str(
                                row["tipo"]
                            ).strip(),

                        "nome":
                            normalizar_nome(
                                row["nome"]
                            ),

                        "quantidade":
                            quantidade,

                        "preco":
                            preco,

                        "uso":
                            uso,

                        "rendimento":
                            rendimento,

                        "custo":
                            custo

                    }).eq(
                        "id",
                        row["id"]
                    ).execute()


                st.success(
                    "✅ Alterações salvas!"
                )

                st.rerun()


            except Exception as e:

                st.error(
                    f"Erro ao salvar: {e}"
                )


        # =================================================
        # EXCLUIR
        # =================================================

        st.divider()

        item = st.selectbox(
            "Selecionar fruta para excluir",
            df["id"].tolist(),
            key="delete_insumo"
        )

        if st.button(
            "🗑️ Excluir selecionado",
            key="delete_insumo_btn"
        ):

            supabase.table(
                "precos_insumos"
            ).delete().eq(
                "id",
                item
            ).execute()

            st.success(
                "Fruta excluída."
            )

            st.rerun()


# =========================================================
# MENU — PRECIFICAÇÃO
# =========================================================

if menu == "Precificação":

    st.title(
        "💰 Precificação"
    )

    aba_bebidas, aba_insumos, aba_artesanais = st.tabs(
        [
            "🥃 Bebidas",
            "🍓 Frutas e Insumos",
            "🧪 Artesanais"
        ]
    )


    # -----------------------------------------------------
    # BEBIDAS
    # -----------------------------------------------------

    with aba_bebidas:

        tela_precificacao(
            "precos_bebidas"
        )


    # -----------------------------------------------------
    # FRUTAS / INSUMOS
    # -----------------------------------------------------

    with aba_insumos:

        tela_insumos()


    # -----------------------------------------------------
    # ARTESANAIS
    # -----------------------------------------------------

    with aba_artesanais:

        tela_precificacao(
            "precos_artesanais"
        )

# -------------------------
# ESTOQUE
# -------------------------

elif menu == "Estoque":

    st.title("Controle de Estoque")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Entrada", "Saída", "Estoque físico", "Registros"]
    )

    # =========================
    # ENTRADA
    # =========================
    with tab1:
        with st.form("entrada_estoque", clear_on_submit=True):
            st.markdown("### 📥 Registrar Movimentação")

            # Padroniza a digitação com .title() e remove espaços com .strip()
            produto = st.text_input("Tipo do Produto (Ex: Whisky, Vodka)").title().strip()
            marca = st.text_input("Marca (Ex: Jack Daniels, Absolut)").title().strip()
            tamanho = st.text_input("Tamanho (Ex: 750, 1000)").strip()

            qtd = st.number_input("Quantidade", min_value=0.0)

            status = st.selectbox("Status", ["Compra", "Volta evento", "Teste"])

            preco = 0.0
            if status == "Compra":
                preco = st.number_input("Preço unitário", min_value=0.0)
            else:
                st.info("🔁 Não altera preço existente")

            if st.form_submit_button("Registrar entrada"):
                if not produto or not marca:
                    st.error("Por favor, preencha o tipo do produto e a marca!")
                else:
                    if status != "Teste":
                        # Filtra exatamente usando os nomes padronizados
                        dados = supabase.table("estoque")\
                            .select("*")\
                            .eq("produto", produto)\
                            .eq("marca", marca)\
                            .eq("tamanho", tamanho)\
                            .execute()

                        atual = pd.DataFrame(dados.data)

                        if atual.empty:
                            # Se não existe, cria o primeiro registro
                            supabase.table("estoque").insert({
                                "produto": produto,
                                "marca": marca,
                                "quantidade": float(qtd),
                                "tamanho": tamanho,
                                "preco": float(preco)
                            }).execute()
                        else:
                            # Se JÁ EXISTE, ele apenas SOMARÁ na mesma linha!
                            qtd_atual = float(atual.iloc[0]["quantidade"])
                            preco_atual = float(atual.iloc[0]["preco"])

                            nova_qtd = qtd_atual + float(qtd)
                            novo_preco = float(preco) if status == "Compra" else preco_atual

                            supabase.table("estoque").update({
                                "quantidade": nova_qtd,
                                "preco": novo_preco
                            }).eq("produto", produto)\
                              .eq("marca", marca)\
                              .eq("tamanho", tamanho)\
                              .execute()
                    else:
                        st.warning("Movimentação de teste não altera estoque")

                    # Registra histórico
                    supabase.table("movimentacoes").insert({
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "produto": produto,
                        "marca": marca,
                        "tipo": "Entrada",
                        "quantidade": float(qtd),
                        "status": status
                    }).execute()

                    st.success(f"Estoque atualizado para {produto} {marca}!")
                    st.rerun()

    # =========================
    # SAÍDA COM JUSTIFICATIVA (CORRIGIDA)
    # =========================
    with tab2:
        dados = supabase.table("estoque").select("*").execute()
        estoque = pd.DataFrame(dados.data)

        if estoque.empty:
            st.info("Estoque vazio")
        else:
            st.markdown("### 📤 Registrar Saída de Estoque")
            
            # 1. Seletores dinâmicos ficam FORA do form para o Streamlit conseguir atualizar a tela
            produto_sel = st.selectbox("1️⃣ Selecione o Produto", sorted(estoque["produto"].unique()))
            
            marcas_filtradas = estoque[estoque["produto"] == produto_sel]["marca"].unique()
            marca_sel = st.selectbox("2️⃣ Selecione a Marca", sorted(marcas_filtradas))

            tamanhos_filtrados = estoque[
                (estoque["produto"] == produto_sel) & 
                (estoque["marca"] == marca_sel)
            ]["tamanho"].fillna("").unique()
            tamanho_sel = st.selectbox("3️⃣ Selecione o Tamanho", sorted(tamanhos_filtrados))

            # 2. O formulário engloba apenas a quantidade, justificativa e o botão de envio
            with st.form("executar_saida", clear_on_submit=True):
                
                qtd = st.number_input("Quantidade para dar baixa", min_value=1.0, step=1.0)

                justificativa = st.selectbox(
                    "Motivo da saída / Justificativa",
                    [
                        "Evento", 
                        "Ajuste de Estoque", 
                        "Teste de Drink", 
                        "Consumo Interno", 
                        "Avaria / Perda"
                    ]
                )

                if st.form_submit_button("Confirmar Baixa no Estoque"):
                    # Busca o item exato no banco de dados
                    dados_item = supabase.table("estoque")\
                        .select("*")\
                        .eq("produto", str(produto_sel))\
                        .eq("marca", str(marca_sel))\
                        .eq("tamanho", str(tamanho_sel))\
                        .execute()

                    atual = pd.DataFrame(dados_item.data)

                    if atual.empty:
                        st.error("Erro grave: Item não encontrado no banco de dados.")
                    else:
                        qtd_atual = float(atual.iloc[0]["quantidade"])
                        nova_qtd = qtd_atual - float(qtd)

                        if nova_qtd < 0:
                            st.error(f"❌ Estoque insuficiente! Você tentou retirar {qtd}, mas só tem {qtd_atual} unidades em estoque.")
                        else:
                            # A) Atualiza a quantidade no estoque físico
                            supabase.table("estoque").update({
                                "quantidade": nova_qtd
                            }).eq("produto", str(produto_sel))\
                              .eq("marca", str(marca_sel))\
                              .eq("tamanho", str(tamanho_sel))\
                              .execute()

                            # B) Registra a movimentação no histórico
                            supabase.table("movimentacoes").insert({
                                "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "produto": str(produto_sel),
                                "marca": str(marca_sel),
                                "tipo": "Saída",
                                "quantidade": float(qtd),
                                "status": str(justificativa)
                            }).execute()

                            st.success(f"✅ Baixa realizada com sucesso! Motivo: {justificativa}")
                            st.rerun()

    # =========================
    # ESTOQUE FÍSICO (AGRUPADO E UNIFICADO)
    # =========================
    with tab3:
        dados = supabase.table("estoque").select("*").execute()
        df_bruto = pd.DataFrame(dados.data)

        busca = st.text_input("🔍 Buscar por Marca")

        if busca and not df_bruto.empty:
            df_bruto = df_bruto[df_bruto["marca"].str.contains(busca, case=False, na=False)]

        if df_bruto.empty:
            st.info("Estoque vazio")
        else:
            # 1. Limpeza e padronização rápida dos dados brutos
            df_bruto["produto"] = df_bruto["produto"].fillna("Sem Produto").astype(str).str.title().str.strip()
            df_bruto["marca"] = df_bruto["marca"].fillna("Sem Marca").astype(str).str.title().str.strip()
            df_bruto["tamanho"] = df_bruto["tamanho"].fillna("").astype(str).str.strip()
            
            df_bruto["quantidade"] = pd.to_numeric(df_bruto["quantidade"], errors="coerce").fillna(0)
            df_bruto["preco"] = pd.to_numeric(df_bruto["preco"], errors="coerce").fillna(0)

            # 2. AGRUPAMENTO INTELIGENTE: Junta tudo que tem o mesmo produto, marca e tamanho
            # Isso garante que se houver qualquer linha duplicada por erro no banco, a tela soma tudo em uma linha só!
            df = df_bruto.groupby(["produto", "marca", "tamanho"], as_index=False).agg({
                "quantidade": "sum",
                "preco": "max"  # Pega o maior preço praticado ou o último atualizado
            })

            # Calcula o valor total de forma segura
            df["valor_total"] = df["quantidade"] * df["preco"]
            total = float(df["valor_total"].sum())

            # Exibe a tabela unificada na tela
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "quantidade": st.column_config.NumberColumn("🔢 Qtd"),
                    "preco": st.column_config.NumberColumn("💰 Preço", format="R$ %.2f"),
                    "valor_total": st.column_config.NumberColumn("💎 Total", format="R$ %.2f")
                }
            )

            st.metric("💰 Valor total em estoque", f"R$ {total:,.2f}")

            st.markdown("---")
            st.subheader("🗑 Remover item")

            # Cria o identificador para o selectbox baseado na tabela já unificada
            df["id_item"] = (
                df["produto"] + " | " +
                df["marca"] + " | " +
                df["tamanho"]
            )

            item = st.selectbox("Selecione o item para excluir", df["id_item"])

            if st.button("Excluir item"):
                row = df[df["id_item"] == item].iloc[0]

                produto_sel = str(row["produto"])
                marca_sel = str(row["marca"])
                tamanho_sel = str(row["tamanho"])
                qtd_sel = float(row["quantidade"])

                # Registra a movimentação de exclusão
                supabase.table("movimentacoes").insert({
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "produto": produto_sel,
                    "marca": marca_sel,
                    "tipo": "Exclusão",
                    "quantidade": qtd_sel,
                    "status": "Manual"
                }).execute()

                # Deleta do banco todas as variações que possam ter gerado a duplicação
                query = supabase.table("estoque").delete()\
                    .eq("produto", produto_sel)\
                    .eq("marca", marca_sel)
                
                if tamanho_sel == "":
                    query = query.is_("tamanho", "null")
                else:
                    query = query.eq("tamanho", tamanho_sel)

                query.execute()

                st.success("Item removido com sucesso!")
                st.rerun()
    # =========================
    # REGISTROS CONFIGURADOS
    # =========================
    with tab4:
        dados = supabase.table("movimentacoes")\
            .select("*")\
            .order("data", desc=True)\
            .execute()

        df = pd.DataFrame(dados.data)

        if df.empty:
            st.info("Nenhuma movimentação registrada ainda.")
        else:
            # Mostra a tabela renomeando a coluna 'status' para ficar mais clara
            st.dataframe(
                df, 
                use_container_width=True,
                column_config={
                    "status": st.column_config.TextColumn("📋 Justificativa / Status"),
                    "data": st.column_config.TextColumn("📅 Data/Hora"),
                    "produto": st.column_config.TextColumn("📦 Produto"),
                    "marca": st.column_config.TextColumn("🏷️ Marca"),
                    "tipo": st.column_config.TextColumn("🔄 Tipo"),
                    "quantidade": st.column_config.NumberColumn("🔢 Qtd")
                }
            )

        st.info("Movimentações com status 'Teste' não afetam o estoque físico")
        
elif menu == "Relatórios":

    st.title("📊 Dashboard Geral")

    # =========================================================
    # FILTROS DE DATA / PERÍODO
    # =========================================================
    col_p, col_i, col_f = st.columns([2, 1, 1])

    periodo = col_p.selectbox(
        "📅 Período",
        ["Este ano", "Este mês", "Últimos 30 dias", "Todos"],
        key="dash_periodo"
    )

    hoje = datetime.now()

    if periodo == "Este ano":
        dt_inicio = datetime(hoje.year, 1, 1).date()
        dt_fim = hoje.date()

    elif periodo == "Este mês":
        dt_inicio = datetime(hoje.year, hoje.month, 1).date()
        dt_fim = hoje.date()

    elif periodo == "Últimos 30 dias":
        dt_inicio = (hoje - timedelta(days=30)).date()
        dt_fim = hoje.date()

    else:
        dt_inicio = datetime(2020, 1, 1).date()
        dt_fim = hoje.date()

    data_i = col_i.date_input(
        "🗓️ Data inicial",
        value=dt_inicio,
        key="dash_dt_i"
    )

    data_f = col_f.date_input(
        "🗓️ Data final",
        value=dt_fim,
        key="dash_dt_f"
    )


    # =========================================================
    # CARREGAMENTO DOS EVENTOS
    # =========================================================
    try:

        response_eventos = (
            supabase.table("eventos")
            .select("*")
            .in_(
                "status",
                ["aprovado", "finalizado", "concluido", "pago"]
            )
            .execute()
        )

        df_eventos = pd.DataFrame(
            response_eventos.data or []
        )

    except Exception:

        df_eventos = pd.DataFrame()


    # =========================================================
    # CARREGAMENTO DOS ADITIVOS
    # =========================================================
    try:

        response_aditivos = (
            supabase.table("aditivos_evento")
            .select("*")
            .execute()
        )

        df_aditivos = pd.DataFrame(
            response_aditivos.data or []
        )

    except Exception:

        df_aditivos = pd.DataFrame()


    # =========================================================
    # CARREGAMENTO DO FINANCEIRO
    # =========================================================
    try:

        response_fin = (
            supabase.table("Financeiro")
            .select("*")
            .execute()
        )

        df_financeiro = pd.DataFrame(
            response_fin.data or []
        )

    except Exception:

        try:

            response_fin = (
                supabase.table("financeiro")
                .select("*")
                .execute()
            )

            df_financeiro = pd.DataFrame(
                response_fin.data or []
            )

        except Exception:

            df_financeiro = pd.DataFrame()


    # =========================================================
    # PREPARAÇÃO DOS EVENTOS
    # =========================================================
    if not df_eventos.empty:

        # -----------------------------------------------------
        # VALOR BASE DO CONTRATO
        # -----------------------------------------------------
        if "venda" in df_eventos.columns:

            df_eventos["venda_base"] = pd.to_numeric(
                df_eventos["venda"],
                errors="coerce"
            ).fillna(0)

        else:

            df_eventos["venda_base"] = 0.0


        # -----------------------------------------------------
        # ADITIVOS / HORAS EXTRAS
        # -----------------------------------------------------
        if (
            not df_aditivos.empty
            and "evento_id" in df_aditivos.columns
            and "valor_cliente" in df_aditivos.columns
        ):

            df_aditivos["valor_cliente"] = pd.to_numeric(
                df_aditivos["valor_cliente"],
                errors="coerce"
            ).fillna(0)

            aditivos_agrupados = (
                df_aditivos
                .groupby("evento_id")["valor_cliente"]
                .sum()
                .reset_index()
            )

            aditivos_agrupados.rename(
                columns={
                    "valor_cliente": "aditivos_total"
                },
                inplace=True
            )

            df = df_eventos.merge(
                aditivos_agrupados,
                left_on="id",
                right_on="evento_id",
                how="left"
            )

            df["aditivos_total"] = (
                df["aditivos_total"]
                .fillna(0)
            )

        else:

            df = df_eventos.copy()
            df["aditivos_total"] = 0.0


        # -----------------------------------------------------
        # FATURAMENTO REAL DO EVENTO
        # CONTRATO + ADITIVOS
        # -----------------------------------------------------
        df["faturamento_evento"] = (
            df["venda_base"]
            + df["aditivos_total"]
        )

    else:

        df = pd.DataFrame()


    # =========================================================
    # DATA DOS EVENTOS
    # =========================================================
    if not df.empty and "data" in df.columns:

        df["data_dt"] = pd.to_datetime(
            df["data"],
            errors="coerce"
        )

        df = df[
            (df["data_dt"].dt.date >= data_i)
            &
            (df["data_dt"].dt.date <= data_f)
        ].copy()


    # =========================================================
    # PRÓXIMOS EVENTOS
    # =========================================================
    st.subheader("📅 Próximos Eventos")

    if (
        not df_eventos.empty
        and "data" in df_eventos.columns
    ):

        df_proximos = df_eventos.copy()

        df_proximos["data_dt"] = pd.to_datetime(
            df_proximos["data"],
            errors="coerce"
        )

        proximos = (
            df_proximos[
                df_proximos["data_dt"].dt.date >= hoje.date()
            ]
            .sort_values("data_dt")
        )

        if not proximos.empty:

            colunas_proximos = []

            if "cliente" in proximos.columns:
                colunas_proximos.append("cliente")

            if "data" in proximos.columns:
                colunas_proximos.append("data")

            if "venda" in proximos.columns:
                colunas_proximos.append("venda")

            if "status" in proximos.columns:
                colunas_proximos.append("status")

            st.dataframe(
                proximos[colunas_proximos],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Nenhum próximo evento confirmado."
            )

    else:

        st.info(
            "Nenhum próximo evento confirmado."
        )


    st.divider()


    # =========================================================
    # CUSTOS DOS EVENTOS
    # =========================================================
    coluna_custo = None

    possiveis_colunas_custo = [
        "custo_total",
        "custo",
        "custo_evento",
        "custo_real",
        "custos"
    ]

    if not df.empty:

        for coluna in possiveis_colunas_custo:

            if coluna in df.columns:

                coluna_custo = coluna
                break


    if (
        not df.empty
        and coluna_custo
    ):

        df["custo_evento"] = pd.to_numeric(
            df[coluna_custo],
            errors="coerce"
        ).fillna(0)

    elif not df.empty:

        df["custo_evento"] = 0.0


    # =========================================================
    # RESULTADO DE CADA EVENTO
    # =========================================================
    if not df.empty:

        # -----------------------------------------------------
        # LUCRO TOTAL ANTES DA RESERVA
        # -----------------------------------------------------
        df["lucro_evento"] = (
            df["faturamento_evento"]
            - df["custo_evento"]
        )

        # -----------------------------------------------------
        # RESERVA DE EMERGÊNCIA - 35%
        # -----------------------------------------------------
        df["caixa_pj_evento"] = df[
            "lucro_evento"
        ].apply(
            lambda x: x * 0.35 if x > 0 else 0
        )

        # -----------------------------------------------------
        # CAIXA DISPONÍVEL - 65%
        # -----------------------------------------------------
        df["lucro_real_evento"] = (
            df["lucro_evento"]
            - df["caixa_pj_evento"]
        )


    # =========================================================
    # CONSOLIDAÇÃO DOS EVENTOS
    # =========================================================
    faturamento = (
        df["faturamento_evento"].sum()
        if not df.empty
        else 0.0
    )

    custos = (
        df["custo_evento"].sum()
        if not df.empty
        else 0.0
    )

    lucro_total = (
        df["lucro_evento"].sum()
        if not df.empty
        else 0.0
    )

    reserva_emergencia_total = (
        df["caixa_pj_evento"].sum()
        if not df.empty
        else 0.0
    )

    caixa_disponivel_total = (
        df["lucro_real_evento"].sum()
        if not df.empty
        else 0.0
    )

    margem = (
        (lucro_total / faturamento) * 100
        if faturamento > 0
        else 0.0
    )


    # =========================================================
    # ABAS
    # =========================================================
    tab_visao, tab_fin, tab_vendas, tab_metas, tab_prod = st.tabs([
        "📊 Visão Geral",
        "💰 Financeiro",
        "📈 Vendas",
        "🎯 Metas",
        "📦 Produtos"
    ])


    # =========================================================
    # TAB 1 - VISÃO GERAL
    # =========================================================
    with tab_visao:

        st.markdown(
            "## 📊 Resultado Consolidado dos Eventos"
        )

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "💰 Faturamento",
            f"R$ {faturamento:,.2f}"
        )

        c2.metric(
            "💸 Custos dos Eventos",
            f"R$ {custos:,.2f}"
        )

        c3.metric(
            "📈 Lucro Total",
            f"R$ {lucro_total:,.2f}"
        )

        c4.metric(
            "📊 Margem",
            f"{margem:.1f}%"
        )

        c5.metric(
            "🛡️ Reserva de Emergência",
            f"R$ {reserva_emergencia_total:,.2f}",
            help="35% do lucro positivo de cada evento."
        )


        st.divider()


        
        # =====================================================
        # RESULTADO REAL
        # =====================================================
        st.markdown(
            "## 💰 Resultado Real do Negócio"
        )

        r1, r2, r3 = st.columns(3)

        r1.metric(
            "📈 Lucro Total",
            f"R$ {lucro_total:,.2f}",
            help="Lucro total dos eventos antes da dedução dos 35%."
        )

        r2.metric(
            "🛡️ Reserva de Emergência",
            f"R$ {reserva_emergencia_total:,.2f}",
            help="35% do lucro positivo de cada evento."
        )

        r3.metric(
            "💵 Caixa Disponível",
            f"R$ {caixa_disponivel_total:,.2f}",
            help="Valor restante após separar os 35% para a Reserva de Emergência."
        )

        st.caption(
            "Para cada evento, 35% do lucro positivo é separado "
            "para a Reserva de Emergência. Os 65% restantes "
            "representam o Caixa Disponível."
        )


        st.divider()


        # =====================================================
        # DETALHAMENTO POR EVENTO
        # =====================================================
        st.markdown(
            "### 📋 Resultado por Evento"
        )

        if not df.empty:

            colunas_evento = []

            if "cliente" in df.columns:
                colunas_evento.append("cliente")

            if "data" in df.columns:
                colunas_evento.append("data")

            colunas_evento += [
                "faturamento_evento",
                "custo_evento",
                "lucro_evento",
                "caixa_pj_evento",
                "lucro_real_evento"
            ]

            colunas_evento = [
                c
                for c in colunas_evento
                if c in df.columns
            ]

            df_resultado = df[
                colunas_evento
            ].copy()

            df_resultado.rename(
                columns={
                    "cliente": "🥂 Cliente",
                    "data": "📅 Data",
                    "faturamento_evento": "💰 Faturamento Total",
                    "custo_evento": "💸 Custo",
                    "lucro_evento": "📈 Lucro Total",
                    "caixa_pj_evento": "🛡️ Reserva de Emergência (35%)",
                    "lucro_real_evento": "💵 Caixa Disponível"
                },
                inplace=True
            )

            st.dataframe(
                df_resultado,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Nenhum evento encontrado no período selecionado."
            )


        # =====================================================
        # GRÁFICO MÊS A MÊS
        # =====================================================
        st.subheader(
            "📈 Faturamento, Custos e Lucro — Mês a Mês"
        )

        if (
            not df.empty
            and "data_dt" in df.columns
        ):

            df_mensal = df.copy()

            df_mensal["mes_ano"] = (
                df_mensal["data_dt"]
                .dt.strftime("%Y-%m")
            )

            consolidado_mensal = (
                df_mensal
                .groupby("mes_ano")[
                    [
                        "faturamento_evento",
                        "custo_evento",
                        "lucro_evento"
                    ]
                ]
                .sum()
            )

            consolidado_mensal.rename(
                columns={
                    "faturamento_evento": "Faturamento",
                    "custo_evento": "Custos",
                    "lucro_evento": "Lucro"
                },
                inplace=True
            )

            st.line_chart(
                consolidado_mensal
            )

        else:

            st.info(
                "Não há dados suficientes para gerar o gráfico."
            )


    # =========================================================
    # TAB 2 - FINANCEIRO
    # =========================================================
    with tab_fin:

        st.markdown(
            "## 💰 Livro Caixa"
        )

        # =====================================================
        # AQUI USAMOS OS MESMOS CUSTOS DOS EVENTOS
        # DO RESULTADO CONSOLIDADO
        # =====================================================
        entrada_total = faturamento
        saida_total = custos
        saldo_caixa = entrada_total - saida_total


        # -----------------------------------------------------
        # MÉTRICAS DO LIVRO CAIXA
        # -----------------------------------------------------
        c1, c2, c3 = st.columns(3)

        c1.metric(
            "💵 Faturamento Total",
            f"R$ {entrada_total:,.2f}"
        )

        c2.metric(
            "💸 Custos dos Eventos",
            f"R$ {saida_total:,.2f}"
        )

        c3.metric(
            "📈 Lucro Total",
            f"R$ {lucro_total:,.2f}"
        )


        st.divider()


        # =====================================================
        # RESUMO DOS 35%
        # =====================================================
        st.markdown(
            "### 🛡️ Distribuição do Lucro"
        )

        f1, f2, f3 = st.columns(3)

        f1.metric(
            "📈 Lucro Total",
            f"R$ {lucro_total:,.2f}"
        )

        f2.metric(
            "🛡️ Reserva de Emergência (35%)",
            f"R$ {reserva_emergencia_total:,.2f}"
        )

        f3.metric(
            "💵 Caixa Disponível (65%)",
            f"R$ {caixa_disponivel_total:,.2f}"
        )


        st.caption(
            "O Lucro Total corresponde ao resultado antes da separação. "
            "35% são destinados à Reserva de Emergência e os 65% restantes "
            "formam o Caixa Disponível."
        )


        st.divider()


        # =====================================================
        # MOVIMENTAÇÕES DO LIVRO CAIXA
        # =====================================================
        st.markdown(
            "### 📋 Movimentações Financeiras"
        )

        if not df_financeiro.empty:

            df_fin_exibicao = df_financeiro.copy()

            if "valor" in df_fin_exibicao.columns:

                df_fin_exibicao["valor"] = pd.to_numeric(
                    df_fin_exibicao["valor"],
                    errors="coerce"
                ).fillna(0)

            colunas_fin = [
                "data",
                "tipo",
                "categoria",
                "forma_pagamento",
                "descricao",
                "valor"
            ]

            colunas_fin = [
                c
                for c in colunas_fin
                if c in df_fin_exibicao.columns
            ]

            if colunas_fin:

                df_fin_exibicao = df_fin_exibicao[
                    colunas_fin
                ].copy()

                df_fin_exibicao.rename(
                    columns={
                        "data": "📅 Data",
                        "tipo": "🔄 Tipo",
                        "categoria": "📂 Categoria",
                        "forma_pagamento": "💳 Forma",
                        "descricao": "📝 Descrição",
                        "valor": "💰 Valor"
                    },
                    inplace=True
                )

                st.dataframe(
                    df_fin_exibicao,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.dataframe(
                    df_financeiro,
                    use_container_width=True,
                    hide_index=True
                )

        else:

            st.info(
                "Nenhuma movimentação financeira encontrada."
            )

    # =========================================================
    # TAB 3 - VENDAS
    # =========================================================
    with tab_vendas:

        st.markdown(
            "## 📈 Vendas"
        )

        total_eventos = len(df)

        ticket_medio = (
            faturamento / total_eventos
            if total_eventos > 0
            else 0.0
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "📦 Eventos",
            f"{total_eventos}"
        )

        c2.metric(
            "💰 Faturamento",
            f"R$ {faturamento:,.2f}"
        )

        c3.metric(
            "🎯 Ticket Médio",
            f"R$ {ticket_medio:,.2f}"
        )

        st.divider()


        # -----------------------------------------------------
        # BUSCAR CLIENTE
        # -----------------------------------------------------
        cliente_busca = st.text_input(
            "🔎 Buscar cliente",
            key="relatorio_busca_cliente"
        )

        df_vendas = df.copy()

        if (
            cliente_busca
            and not df_vendas.empty
            and "cliente" in df_vendas.columns
        ):

            df_vendas = df_vendas[
                df_vendas["cliente"]
                .astype(str)
                .str.contains(
                    cliente_busca,
                    case=False,
                    na=False
                )
            ]


        if not df_vendas.empty:

            colunas_vendas = [
                c
                for c in [
                    "cliente",
                    "data",
                    "venda_base",
                    "aditivos_total",
                    "faturamento_evento",
                    "status"
                ]
                if c in df_vendas.columns
            ]

            df_vendas_exibir = df_vendas[
                colunas_vendas
            ].copy()

            df_vendas_exibir.rename(
                columns={
                    "cliente": "🥂 Cliente",
                    "data": "📅 Data",
                    "venda_base": "📋 Contrato Base",
                    "aditivos_total": "⏰ Horas Extras / Aditivos",
                    "faturamento_evento": "💰 Valor Total Real",
                    "status": "📌 Status"
                },
                inplace=True
            )

            st.dataframe(
                df_vendas_exibir,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Nenhuma venda encontrada no período."
            )


    # =========================================================
    # TAB 4 - METAS
    # =========================================================
    with tab_metas:

        st.markdown(
            "## 🎯 Metas de Faturamento"
        )

        st.caption(
            "Defina uma meta para cada mês e acompanhe "
            "automaticamente o faturamento realizado."
        )

        # =====================================================
        # CONFIGURAÇÃO
        # =====================================================

        meses_nomes = [
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro"
        ]

        ano_atual = hoje.year

        # =====================================================
        # CARREGA METAS DO SUPABASE
        # =====================================================

        try:

            response_metas = (
                supabase
                .table("metas_mensais")
                .select("*")
                .eq("ano", ano_atual)
                .order("mes")
                .execute()
            )

            dados_metas_supabase = (
                response_metas.data or []
            )

        except Exception as e:

            dados_metas_supabase = []

            st.error(
                f"❌ Erro ao carregar as metas: {e}"
            )


        # =====================================================
        # MONTA DICIONÁRIO DAS METAS
        # =====================================================

        metas_salvas = {}

        for registro in dados_metas_supabase:

            try:

                mes = int(registro["mes"])

                valor = float(
                    registro.get(
                        "meta_valor",
                        0
                    ) or 0
                )

                metas_salvas[mes] = valor

            except Exception:
                pass


        # =====================================================
        # GARANTE OS 12 MESES
        # =====================================================

        dados_metas = []

        for numero_mes in range(1, 13):

            valor_meta = metas_salvas.get(
                numero_mes,
                10000.0
            )

            dados_metas.append({

                "Mês":
                    meses_nomes[
                        numero_mes - 1
                    ],

                "Meta":
                    valor_meta
            })


        df_metas = pd.DataFrame(
            dados_metas
        )


        # =====================================================
        # EDITOR
        # =====================================================

        df_metas_editado = st.data_editor(

            df_metas,

            use_container_width=True,

            hide_index=True,

            disabled=["Mês"],

            column_config={

                "Mês":
                    st.column_config.TextColumn(
                        "📅 Mês"
                    ),

                "Meta":
                    st.column_config.NumberColumn(

                        "🎯 Meta de Faturamento",

                        min_value=0.0,

                        step=500.0,

                        format="R$ %.2f"
                    )
            },

            key="editor_metas_mensais"
        )


        st.divider()


        # =====================================================
        # BOTÃO SALVAR
        # =====================================================

        if st.button(
            "💾 Salvar Metas",
            type="primary",
            use_container_width=True
        ):

            try:

                for indice, linha in df_metas_editado.iterrows():

                    numero_mes = indice + 1

                    valor_meta = float(
                        linha["Meta"] or 0
                    )


                    # -----------------------------------------
                    # VERIFICA SE JÁ EXISTE
                    # -----------------------------------------

                    existente = (
                        supabase
                        .table("metas_mensais")
                        .select("id")
                        .eq("ano", ano_atual)
                        .eq("mes", numero_mes)
                        .execute()
                    )


                    dados = {

                        "ano":
                            ano_atual,

                        "mes":
                            numero_mes,

                        "mes_ano":
                            meses_nomes[
                                numero_mes - 1
                            ],

                        "meta_valor":
                            valor_meta
                    }


                    # -----------------------------------------
                    # ATUALIZA
                    # -----------------------------------------

                    if existente.data:

                        supabase \
                            .table("metas_mensais") \
                            .update(dados) \
                            .eq(
                                "ano",
                                ano_atual
                            ) \
                            .eq(
                                "mes",
                                numero_mes
                            ) \
                            .execute()


                    # -----------------------------------------
                    # INSERE
                    # -----------------------------------------

                    else:

                        supabase \
                            .table("metas_mensais") \
                            .insert(dados) \
                            .execute()


                st.success(
                    "✅ Metas salvas com sucesso!"
                )

                st.rerun()


            except Exception as e:

                st.error(
                    f"❌ Erro ao salvar as metas: {e}"
                )


        st.divider()


        # =====================================================
        # FATURAMENTO POR MÊS
        # =====================================================

        df_meta_vendas = pd.DataFrame({

            "mes":
                range(1, 13),

            "mes_nome":
                meses_nomes,

            "meta":
                [
                    float(
                        linha["Meta"] or 0
                    )
                    for _, linha
                    in df_metas_editado.iterrows()
                ],

            "faturamento":
                [0.0] * 12
        })


        # =====================================================
        # CALCULA FATURAMENTO REAL
        # =====================================================

        if (
            not df.empty
            and "data_dt" in df.columns
            and "faturamento_evento" in df.columns
        ):

            faturamento_mensal = (

                df
                .groupby(
                    df["data_dt"].dt.month
                )[
                    "faturamento_evento"
                ]
                .sum()
            )


            for numero_mes in range(1, 13):

                if numero_mes in faturamento_mensal.index:

                    df_meta_vendas.loc[
                        df_meta_vendas["mes"]
                        == numero_mes,
                        "faturamento"
                    ] = float(
                        faturamento_mensal[
                            numero_mes
                        ]
                    )


        # =====================================================
        # DIFERENÇA
        # =====================================================

        df_meta_vendas["diferença"] = (

            df_meta_vendas["faturamento"]

            -

            df_meta_vendas["meta"]
        )


        # =====================================================
        # PERCENTUAL
        # =====================================================

        df_meta_vendas["percentual"] = (

            df_meta_vendas["faturamento"]

            /

            df_meta_vendas["meta"]

            * 100

        ).replace(

            [
                float("inf"),
                -float("inf")
            ],

            0

        ).fillna(0)


        # =====================================================
        # STATUS
        # =====================================================

        df_meta_vendas["status"] = (

            df_meta_vendas.apply(

                lambda linha:

                    "🟢 Atingida"

                    if (
                        linha["faturamento"]
                        >=
                        linha["meta"]
                    )

                    else

                    "🔴 Não atingida",

                axis=1
            )
        )


        # =====================================================
        # ATUALIZA RESULTADOS NO SUPABASE
        # =====================================================

        for _, linha in df_meta_vendas.iterrows():

            numero_mes = int(
                linha["mes"]
            )

            meta_valor = float(
                linha["meta"]
            )

            faturamento = float(
                linha["faturamento"]
            )

            diferenca = float(
                linha["diferença"]
            )

            percentual = float(
                linha["percentual"]
            )

            atingida = (
                faturamento
                >=
                meta_valor
            )


            try:

                supabase \
                    .table("metas_mensais") \
                    .update({

                        "faturamento":
                            faturamento,

                        "diferenca":
                            diferenca,

                        "percentual":
                            percentual,

                        "atingida":
                            atingida,

                        "atualizado_em":
                            datetime.now().isoformat()

                    }) \
                    .eq(
                        "ano",
                        ano_atual
                    ) \
                    .eq(
                        "mes",
                        numero_mes
                    ) \
                    .execute()

            except Exception:
                pass


        # =====================================================
        # RESUMO DO ANO
        # =====================================================

        meta_total_ano = (

            df_meta_vendas["meta"]
            .sum()
        )

        faturamento_total_ano = (

            df_meta_vendas[
                "faturamento"
            ]
            .sum()
        )

        diferenca_total_ano = (

            faturamento_total_ano
            -
            meta_total_ano
        )

        percentual_ano = (

            faturamento_total_ano
            /
            meta_total_ano
            *
            100

            if meta_total_ano > 0

            else 0
        )


        # =====================================================
        # RESUMO
        # =====================================================

        st.markdown(
            "### 📊 Resumo das Metas"
        )

        cm1, cm2, cm3, cm4 = st.columns(4)


        cm1.metric(
            "🎯 Meta Anual",
            f"R$ {meta_total_ano:,.2f}"
        )


        cm2.metric(
            "💰 Faturamento",
            f"R$ {faturamento_total_ano:,.2f}"
        )


        cm3.metric(
            "📊 Atingimento",
            f"{percentual_ano:.1f}%"
        )


        cm4.metric(
            "📈 Diferença",
            f"R$ {diferenca_total_ano:,.2f}"
        )


        st.divider()


        # =====================================================
        # ACOMPANHAMENTO MENSAL
        # =====================================================

        st.markdown(
            "### 📋 Acompanhamento Mês a Mês"
        )


        df_metas_exibir = (

            df_meta_vendas[

                [
                    "mes_nome",
                    "meta",
                    "faturamento",
                    "diferença",
                    "percentual",
                    "status"
                ]

            ].copy()
        )


        df_metas_exibir.rename(

            columns={

                "mes_nome":
                    "📅 Mês",

                "meta":
                    "🎯 Meta",

                "faturamento":
                    "💰 Faturamento",

                "diferença":
                    "📊 Diferença",

                "percentual":
                    "% Atingido",

                "status":
                    "Status"
            },

            inplace=True
        )


        st.dataframe(

            df_metas_exibir,

            use_container_width=True,

            hide_index=True,

            column_config={

                "🎯 Meta":
                    st.column_config.NumberColumn(
                        format="R$ %.2f"
                    ),

                "💰 Faturamento":
                    st.column_config.NumberColumn(
                        format="R$ %.2f"
                    ),

                "📊 Diferença":
                    st.column_config.NumberColumn(
                        format="R$ %.2f"
                    ),

                "% Atingido":
                    st.column_config.NumberColumn(
                        format="%.1f%%"
                    )
            }
        )


        st.divider()


        # =====================================================
        # GRÁFICO
        # =====================================================

        st.markdown(
            "### 📈 Meta x Faturamento por Mês"
        )


        grafico_metas = (

            df_meta_vendas[

                [
                    "mes_nome",
                    "meta",
                    "faturamento"
                ]

            ].copy()
        )


        grafico_metas.set_index(
            "mes_nome",
            inplace=True
        )


        grafico_metas.rename(

            columns={

                "meta":
                    "Meta",

                "faturamento":
                    "Faturamento"
            },

            inplace=True
        )


        st.bar_chart(
            grafico_metas
        )


        st.divider()


        # =====================================================
        # METAS ATINGIDAS / NÃO ATINGIDAS
        # =====================================================

        meses_atingidos = (

            df_meta_vendas[
                df_meta_vendas[
                    "faturamento"
                ]
                >=
                df_meta_vendas[
                    "meta"
                ]
            ]
        )


        meses_nao_atingidos = (

            df_meta_vendas[
                df_meta_vendas[
                    "faturamento"
                ]
                <
                df_meta_vendas[
                    "meta"
                ]
            ]
        )


        ca, cn = st.columns(2)


        with ca:

            st.markdown(
                "### 🟢 Metas Atingidas"
            )


            if not meses_atingidos.empty:

                for _, linha in (
                    meses_atingidos.iterrows()
                ):

                    excesso = (

                        linha["faturamento"]
                        -
                        linha["meta"]
                    )


                    st.write(

                        f"**{linha['mes_nome']}** — "
                        f"R$ {linha['faturamento']:,.2f} "
                        f"(meta R$ {linha['meta']:,.2f}) "
                        f"→ **+R$ {excesso:,.2f}**"
                    )

            else:

                st.info(
                    "Nenhuma meta atingida ainda."
                )


        with cn:

            st.markdown(
                "### 🔴 Metas Não Atingidas"
            )


            if not meses_nao_atingidos.empty:

                for _, linha in (
                    meses_nao_atingidos.iterrows()
                ):

                    falta = (

                        linha["meta"]
                        -
                        linha["faturamento"]
                    )


                    st.write(

                        f"**{linha['mes_nome']}** — "
                        f"R$ {linha['faturamento']:,.2f} "
                        f"→ faltam **R$ {falta:,.2f}**"
                    )

            else:

                st.success(
                    "🎉 Todas as metas foram atingidas!"
                )

    # =========================================================
    # TAB 5 - PRODUTOS
    # =========================================================
    with tab_prod:

        st.markdown(
            "## 📦 Desempenho por Produto / Serviço"
        )

        st.info(
            "Cadastre e vincule serviços aos orçamentos "
            "para visualizar a distribuição por produto."
        )


elif menu == "Eventos":

    st.title("📋 Eventos")

    # =========================================================
    # CARREGAR EVENTOS
    # =========================================================

    response = (
        supabase.table("eventos")
        .select("*")
        .in_(
            "status",
            [
                "aprovado",
                "finalizado",
                "concluido",
                "pago"
            ]
        )
        .order("data", desc=False)
        .execute()
    )

    df_eventos = pd.DataFrame(
        response.data or []
    )

    # =========================================================
    # CARREGAR ADITIVOS / HORAS EXTRAS
    # =========================================================

    response_aditivos = (
        supabase.table("aditivos_evento")
        .select("*")
        .execute()
    )

    df_aditivos = pd.DataFrame(
        response_aditivos.data or []
    )

    # =========================================================
    # PREPARAR DADOS
    # =========================================================

    if not df_eventos.empty:

        df_eventos["data_dt"] = pd.to_datetime(
            df_eventos["data"],
            errors="coerce"
        )

        df_eventos["venda"] = pd.to_numeric(
            df_eventos.get("venda", 0),
            errors="coerce"
        ).fillna(0)

        df_eventos["convidados"] = pd.to_numeric(
            df_eventos.get("convidados", 0),
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # ADITIVOS
        # =====================================================

        if (
            not df_aditivos.empty
            and "evento_id" in df_aditivos.columns
            and "valor_cliente" in df_aditivos.columns
        ):

            df_aditivos["valor_cliente"] = pd.to_numeric(
                df_aditivos["valor_cliente"],
                errors="coerce"
            ).fillna(0)

            aditivos_agrupados = (
                df_aditivos
                .groupby("evento_id")["valor_cliente"]
                .sum()
                .reset_index()
            )

            aditivos_agrupados.rename(
                columns={
                    "valor_cliente": "aditivos"
                },
                inplace=True
            )

            df_eventos = df_eventos.merge(
                aditivos_agrupados,
                left_on="id",
                right_on="evento_id",
                how="left"
            )

            df_eventos["aditivos"] = (
                df_eventos["aditivos"]
                .fillna(0)
            )

        else:

            df_eventos["aditivos"] = 0.0

        # =====================================================
        # FATURAMENTO REAL
        # =====================================================

        df_eventos["faturamento"] = (
            df_eventos["venda"]
            +
            df_eventos["aditivos"]
        )

    # =========================================================
    # DATA ATUAL
    # =========================================================

    hoje = pd.Timestamp.now().normalize()

    # =========================================================
    # SEPARAR PRÓXIMOS E REALIZADOS
    # =========================================================

    if not df_eventos.empty:

        df_proximos = df_eventos[
            (
                df_eventos["data_dt"] >= hoje
            )
            &
            (
                df_eventos["status"] == "aprovado"
            )
        ].copy()

        df_realizados = df_eventos[
            (
                df_eventos["status"].isin(
                    [
                        "finalizado",
                        "concluido",
                        "pago"
                    ]
                )
            )
            |
            (
                (df_eventos["data_dt"] < hoje)
                &
                (df_eventos["status"] == "aprovado")
            )
        ].copy()

    else:

        df_proximos = pd.DataFrame()
        df_realizados = pd.DataFrame()

    # =========================================================
    # INDICADORES
    # =========================================================

    eventos_realizados = len(
        df_realizados
    )

    proximos_eventos = len(
        df_proximos
    )

    # =========================================================
    # TOTAL FATURADO
    # =========================================================

    total_vendido = (
        df_realizados["faturamento"].sum()
        if not df_realizados.empty
        else 0
    )

    total_pessoas = (
        df_realizados["convidados"].sum()
        if not df_realizados.empty
        else 0
    )

    # =========================================================
    # MAIOR EVENTO
    # =========================================================

    if not df_realizados.empty:

        maior_evento = df_realizados.loc[
            df_realizados["convidados"].idxmax()
        ]

        maior_evento_nome = maior_evento.get(
            "cliente",
            "N/A"
        )

        maior_evento_qtd = maior_evento.get(
            "convidados",
            0
        )

    else:

        maior_evento_nome = "N/A"
        maior_evento_qtd = 0

    # =========================================================
    # MAIOR VENDA
    # =========================================================

    if not df_realizados.empty:

        maior_venda = df_realizados.loc[
            df_realizados["faturamento"].idxmax()
        ]

        maior_venda_nome = maior_venda.get(
            "cliente",
            "N/A"
        )

        maior_venda_valor = maior_venda.get(
            "faturamento",
            0
        )

    else:

        maior_venda_nome = "N/A"
        maior_venda_valor = 0

    # =========================================================
    # TICKET MÉDIO
    # =========================================================

    ticket_medio = (
        total_vendido / eventos_realizados
        if eventos_realizados > 0
        else 0
    )

    # =========================================================
    # PAINEL PRINCIPAL
    # =========================================================

    st.markdown(
        "## 📊 Visão Geral"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🎉 Eventos Realizados",
        eventos_realizados
    )

    c2.metric(
        "📅 Próximos Eventos",
        proximos_eventos
    )

    c3.metric(
        "💰 Total Faturado",
        f"R$ {total_vendido:,.2f}"
    )

    c4.metric(
        "👥 Pessoas Atendidas",
        f"{total_pessoas:,.0f}"
    )

    c5, c6, c7 = st.columns(3)

    c5.metric(
        "🏆 Maior Evento",
        f"{maior_evento_qtd:,.0f} pessoas"
    )

    c6.metric(
        "💎 Maior Venda",
        f"R$ {maior_venda_valor:,.2f}"
    )

    c7.metric(
        "📈 Ticket Médio",
        f"R$ {ticket_medio:,.2f}"
    )

    if maior_evento_nome != "N/A":

        st.caption(
            f"🏆 Maior evento: **{maior_evento_nome}** "
            f"({maior_evento_qtd:,.0f} convidados)"
        )

    if maior_venda_nome != "N/A":

        st.caption(
            f"💎 Maior venda: **{maior_venda_nome}** "
            f"(R$ {maior_venda_valor:,.2f})"
        )

    # =========================================================
    # PRÓXIMOS EVENTOS
    # =========================================================

    st.divider()

    st.markdown(
        "## 📅 Próximos Eventos"
    )

    if df_proximos.empty:

        st.info(
            "Nenhum próximo evento aprovado."
        )

    else:

        proximos_exibir = df_proximos[
            [
                "data",
                "cliente",
                "cidade",
                "convidados",
                "venda",
                "aditivos",
                "faturamento",
                "status"
            ]
        ].copy()

        proximos_exibir.rename(
            columns={
                "data": "Data",
                "cliente": "Cliente",
                "cidade": "Cidade",
                "convidados": "Convidados",
                "venda": "Contrato Base",
                "aditivos": "Aditivos",
                "faturamento": "Faturamento",
                "status": "Status"
            },
            inplace=True
        )

        st.dataframe(
            proximos_exibir,
            use_container_width=True,
            hide_index=True,
            column_config={

                "Data":
                    st.column_config.DateColumn(
                        "📅 Data"
                    ),

                "Cliente":
                    st.column_config.TextColumn(
                        "👤 Cliente"
                    ),

                "Cidade":
                    st.column_config.TextColumn(
                        "📍 Cidade"
                    ),

                "Convidados":
                    st.column_config.NumberColumn(
                        "👥 Convidados"
                    ),

                "Contrato Base":
                    st.column_config.NumberColumn(
                        "📋 Contrato Base",
                        format="R$ %.2f"
                    ),

                "Aditivos":
                    st.column_config.NumberColumn(
                        "⏰ Aditivos",
                        format="R$ %.2f"
                    ),

                "Faturamento":
                    st.column_config.NumberColumn(
                        "💰 Faturamento",
                        format="R$ %.2f"
                    ),

                "Status":
                    st.column_config.TextColumn(
                        "📌 Status"
                    )
            }
        )

    # =========================================================
    # EVOLUÇÃO MENSAL
    # =========================================================

    st.divider()

    st.markdown(
        "## 📈 Evolução dos Eventos"
    )

    if not df_realizados.empty:

        df_grafico = df_realizados.copy()

        df_grafico["Mes"] = (
            df_grafico["data_dt"]
            .dt.to_period("M")
            .astype(str)
        )

        eventos_mes = (
            df_grafico
            .groupby("Mes")
            .size()
        )

        if not eventos_mes.empty:

            st.line_chart(
                eventos_mes
            )

    else:

        st.info(
            "Ainda não existem eventos realizados "
            "para gerar o gráfico."
        )

    # =========================================================
    # HISTÓRICO
    # =========================================================

    st.divider()

    st.markdown(
        "## 📋 Histórico de Eventos"
    )

    busca = st.text_input(
        "🔎 Buscar cliente, cidade ou evento"
    )

    df_lista = df_eventos.copy()

    if busca:

        filtro_cliente = (
            df_lista["cliente"]
            .astype(str)
            .str.contains(
                busca,
                case=False,
                na=False
            )
        )

        filtro_cidade = (
            df_lista["cidade"]
            .astype(str)
            .str.contains(
                busca,
                case=False,
                na=False
            )
        )

        filtro_id = (
            df_lista["id"]
            .astype(str)
            .str.contains(
                busca,
                case=False,
                na=False
            )
        )

        df_lista = df_lista[
            filtro_cliente
            |
            filtro_cidade
            |
            filtro_id
        ]

    # =========================================================
    # EVENTOS
    # =========================================================

    if df_lista.empty:

        st.info(
            "Nenhum evento encontrado."
        )

    else:

        for _, row in df_lista.iterrows():

            evento_id = row["id"]

            cliente = row.get(
                "cliente",
                "Sem cliente"
            )

            data_evento = row.get(
                "data",
                ""
            )

            cidade = row.get(
                "cidade",
                ""
            )

            status = row.get(
                "status",
                ""
            )

            convidados = row.get(
                "convidados",
                0
            )

            venda = row.get(
                "venda",
                0
            )

            aditivos = row.get(
                "aditivos",
                0
            )

            faturamento = row.get(
                "faturamento",
                venda
            )

            # =================================================
            # STATUS
            # =================================================

            if status == "aprovado":

                icone_status = "🟢"

            elif status == "finalizado":

                icone_status = "🔵"

            elif status == "concluido":

                icone_status = "✅"

            elif status == "pago":

                icone_status = "💰"

            else:

                icone_status = "⚪"

            # =================================================
            # CABEÇALHO
            # =================================================

            st.markdown(
                f"### 🍸 {cliente}"
            )

            st.caption(
                f"🆔 Evento #{evento_id}  |  "
                f"📅 {data_evento}  |  "
                f"📍 {cidade}  |  "
                f"{icone_status} {status.upper()}"
            )

            ec1, ec2, ec3, ec4 = st.columns(4)

            ec1.metric(
                "👥 Convidados",
                f"{float(convidados):,.0f}"
            )

            ec2.metric(
                "📋 Contrato Base",
                f"R$ {float(venda):,.2f}"
            )

            ec3.metric(
                "⏰ Aditivos",
                f"R$ {float(aditivos):,.2f}"
            )

            ec4.metric(
                "💰 Faturamento",
                f"R$ {float(faturamento):,.2f}"
            )

            # =================================================
            # CONTROLE DE ABERTURA
            # =================================================

            chave_aberto = (
                f"evento_aberto_{evento_id}"
            )

            if chave_aberto not in st.session_state:

                st.session_state[
                    chave_aberto
                ] = False

            if st.button(
                "📋 Abrir Evento",
                key=f"abrir_evento_{evento_id}"
            ):

                st.session_state[
                    chave_aberto
                ] = not st.session_state[
                    chave_aberto
                ]

            # =================================================
            # EVENTO ABERTO
            # =================================================

            if st.session_state[
                chave_aberto
            ]:

                st.divider()

                # =================================================
                # INFORMAÇÕES
                # =================================================

                st.markdown(
                    "## 📍 Informações do Evento"
                )

                i1, i2, i3 = st.columns(3)

                with i1:

                    st.write(
                        f"**👤 Cliente:** {cliente}"
                    )

                    st.write(
                        f"**📞 Telefone:** "
                        f"{row.get('telefone', '')}"
                    )

                    st.write(
                        f"**🎉 Tipo:** "
                        f"{row.get('tipo_evento', '')}"
                    )

                with i2:

                    st.write(
                        f"**📅 Data:** {data_evento}"
                    )

                    st.write(
                        f"**📍 Cidade:** {cidade}"
                    )

                    st.write(
                        f"**🏠 Endereço:** "
                        f"{row.get('endereco', '')}"
                    )

                with i3:

                    st.write(
                        f"**🕒 Chegada equipe:** "
                        f"{row.get('hora_chegada', '')}"
                    )

                    st.write(
                        f"**🍸 Início:** "
                        f"{row.get('hora_inicio', '')}"
                    )

                    st.write(
                        f"**👥 Convidados:** "
                        f"{row.get('convidados', 0)}"
                    )

                # =================================================
                # CARTA DE DRINKS
                # =================================================

                st.divider()

                st.markdown(
                    "## 🍸 Carta de Drinks"
                )

                drinks = row.get(
                    "drinks",
                    ""
                )

                if drinks:

                    lista_drinks = [
                        d.strip()
                        for d in str(drinks).split("\n")
                        if d.strip()
                    ]

                    if lista_drinks:

                        d1, d2 = st.columns(2)

                        for i, drink in enumerate(
                            lista_drinks
                        ):

                            with (
                                d1
                                if i % 2 == 0
                                else d2
                            ):

                                st.write(
                                    f"☐ {drink}"
                                )

                    else:

                        st.info(
                            "Nenhum drink cadastrado."
                        )

                else:

                    st.info(
                        "Este evento não possui "
                        "carta de drinks cadastrada."
                    )

                # =================================================
                # BUSCAR ITENS
                # =================================================

                itens = pd.DataFrame(
                    supabase.table(
                        "evento_itens"
                    )
                    .select("*")
                    .eq(
                        "evento_id",
                        evento_id
                    )
                    .execute()
                    .data or []
                )

                # =================================================
                # CONFERÊNCIA
                # =================================================

                st.divider()

                st.markdown(
                    "## 📦 Conferência do Evento"
                )

                st.info(
                    "Sistema = quantidade calculada "
                    "no orçamento."
                )

                if itens.empty:

                    st.warning(
                        "Nenhum item encontrado "
                        "neste evento."
                    )

                else:

                    categorias_estoque = [
                        "bebidas",
                        "insumos",
                        "frutas",
                        "locação",
                        "custos"
                    ]

                    itens_check = itens[
                        itens["categoria"]
                        .astype(str)
                        .str.lower()
                        .isin(
                            categorias_estoque
                        )
                    ].copy()

                    if itens_check.empty:

                        st.info(
                            "Nenhum item de estoque "
                            "para conferência."
                        )

                    else:

                        # =============================================
                        # BUSCAR DADOS JÁ SALVOS
                        # =============================================

                        dados_existentes = pd.DataFrame(
                            supabase.table(
                                "evento_conferencia"
                            )
                            .select("*")
                            .eq(
                                "evento_id",
                                evento_id
                            )
                            .execute()
                            .data or []
                        )

                        lista = []

                        for _, item in itens_check.iterrows():

                            produto = str(
                                item.get(
                                    "produto",
                                    ""
                                )
                            )

                            categoria = str(
                                item.get(
                                    "categoria",
                                    ""
                                )
                            )

                            unidade = str(
                                item.get(
                                    "unidade",
                                    "un"
                                )
                            )

                            quantidade_sistema = float(
                                item.get(
                                    "quantidade",
                                    0
                                ) or 0
                            )

                            existente = pd.DataFrame()

                            if not dados_existentes.empty:

                                existente = (
                                    dados_existentes[
                                        dados_existentes[
                                            "produto"
                                        ]
                                        .astype(str)
                                        == produto
                                    ]
                                )

                            if not existente.empty:

                                registro = existente.iloc[0]

                                quantidade_ida = float(
                                    registro.get(
                                        "quantidade_ida",
                                        0
                                    ) or 0
                                )

                                quantidade_volta = float(
                                    registro.get(
                                        "quantidade_volta",
                                        0
                                    ) or 0
                                )

                                quantidade_conferencia = float(
                                    registro.get(
                                        "quantidade_conferencia",
                                        0
                                    ) or 0
                                )

                                observacao = str(
                                    registro.get(
                                        "observacao",
                                        ""
                                    ) or ""
                                )

                            else:

                                quantidade_ida = 0
                                quantidade_volta = 0
                                quantidade_conferencia = 0
                                observacao = ""

                            consumo = (
                                quantidade_ida
                                - quantidade_volta
                            )

                            perda = max(
                                0,
                                quantidade_volta
                                - quantidade_conferencia
                            )

                            lista.append({

                                "Categoria":
                                    categoria,

                                "Produto":
                                    produto,

                                "Unidade":
                                    unidade,

                                "Sistema":
                                    quantidade_sistema,

                                "Ida":
                                    quantidade_ida,

                                "Volta":
                                    quantidade_volta,

                                "Conferência":
                                    quantidade_conferencia,

                                "Consumo":
                                    consumo,

                                "Perda":
                                    perda,

                                "Observação":
                                    observacao
                            })

                        df_conferencia = pd.DataFrame(
                            lista
                        )

                        # =============================================
                        # EDITOR
                        # =============================================

                        df_editado = st.data_editor(

                            df_conferencia,

                            use_container_width=True,

                            hide_index=True,

                            disabled=[
                                "Categoria",
                                "Produto",
                                "Unidade",
                                "Sistema",
                                "Consumo",
                                "Perda"
                            ],

                            column_config={

                                "Categoria":
                                    st.column_config.TextColumn(
                                        "Categoria"
                                    ),

                                "Produto":
                                    st.column_config.TextColumn(
                                        "📦 Produto"
                                    ),

                                "Unidade":
                                    st.column_config.TextColumn(
                                        "Unidade"
                                    ),

                                "Sistema":
                                    st.column_config.NumberColumn(
                                        "🧮 Sistema"
                                    ),

                                "Ida":
                                    st.column_config.NumberColumn(
                                        "🚚 Ida",
                                        min_value=0
                                    ),

                                "Volta":
                                    st.column_config.NumberColumn(
                                        "🔙 Volta",
                                        min_value=0
                                    ),

                                "Conferência":
                                    st.column_config.NumberColumn(
                                        "🔎 Conferência",
                                        min_value=0
                                    ),

                                "Consumo":
                                    st.column_config.NumberColumn(
                                        "📉 Consumo"
                                    ),

                                "Perda":
                                    st.column_config.NumberColumn(
                                        "🚨 Perda"
                                    ),

                                "Observação":
                                    st.column_config.TextColumn(
                                        "📝 Observação"
                                    )
                            },

                            key=(
                                f"editor_conferencia_"
                                f"{evento_id}"
                            )
                        )

                        # =============================================
                        # SALVAR CONFERÊNCIA
                        # =============================================

                        if st.button(
                            "💾 Salvar Conferência",
                            key=(
                                f"salvar_conferencia_"
                                f"{evento_id}"
                            )
                        ):

                            supabase.table(
                                "evento_conferencia"
                            ) \
                            .delete() \
                            .eq(
                                "evento_id",
                                evento_id
                            ) \
                            .execute()

                            for _, item in (
                                df_editado.iterrows()
                            ):

                                ida = float(
                                    item["Ida"]
                                    or 0
                                )

                                volta = float(
                                    item["Volta"]
                                    or 0
                                )

                                conferencia = float(
                                    item["Conferência"]
                                    or 0
                                )

                                consumo = (
                                    ida - volta
                                )

                                perda = max(
                                    0,
                                    volta
                                    - conferencia
                                )

                                supabase.table(
                                    "evento_conferencia"
                                ).insert({

                                    "evento_id":
                                        evento_id,

                                    "produto":
                                        item["Produto"],

                                    "categoria":
                                        item["Categoria"],

                                    "unidade":
                                        item["Unidade"],

                                    "quantidade_sistema":
                                        float(
                                            item["Sistema"]
                                            or 0
                                        ),

                                    "quantidade_ida":
                                        ida,

                                    "quantidade_volta":
                                        volta,

                                    "quantidade_conferencia":
                                        conferencia,

                                    "consumo":
                                        consumo,

                                    "perda":
                                        perda,

                                    "observacao":
                                        item["Observação"]

                                }).execute()

                            st.success(
                                "✅ Conferência salva!"
                            )

                            st.rerun()

                # =================================================
                # RESUMO DA CONFERÊNCIA
                # =================================================

                st.divider()

                st.markdown(
                    "## 📊 Resumo da Conferência"
                )

                conferencia_atual = pd.DataFrame(
                    supabase.table(
                        "evento_conferencia"
                    )
                    .select("*")
                    .eq(
                        "evento_id",
                        evento_id
                    )
                    .execute()
                    .data or []
                )

                if conferencia_atual.empty:

                    st.info(
                        "A conferência ainda não "
                        "foi registrada."
                    )

                else:

                    conferencia_atual[
                        "consumo"
                    ] = pd.to_numeric(
                        conferencia_atual[
                            "consumo"
                        ],
                        errors="coerce"
                    ).fillna(0)

                    conferencia_atual[
                        "perda"
                    ] = pd.to_numeric(
                        conferencia_atual[
                            "perda"
                        ],
                        errors="coerce"
                    ).fillna(0)

                    total_consumo = (
                        conferencia_atual[
                            "consumo"
                        ].sum()
                    )

                    total_perda = (
                        conferencia_atual[
                            "perda"
                        ].sum()
                    )

                    r1, r2 = st.columns(2)

                    r1.metric(
                        "📉 Consumo",
                        f"{total_consumo:,.2f}"
                    )

                    r2.metric(
                        "🚨 Perdas / Divergências",
                        f"{total_perda:,.2f}"
                    )

                    if total_perda > 0:

                        st.error(
                            "🚨 Foram encontradas "
                            "perdas/divergências."
                        )

                    else:

                        st.success(
                            "✅ Nenhuma perda registrada."
                        )

                # =================================================
                # RESULTADO FINANCEIRO
                # =================================================

                st.divider()

                st.markdown(
                    "## 💰 Resultado Financeiro"
                )

                venda_evento = float(
                    row.get(
                        "venda",
                        0
                    ) or 0
                )

                aditivos_evento = float(
                    row.get(
                        "aditivos",
                        0
                    ) or 0
                )

                faturamento_evento = (
                    venda_evento
                    +
                    aditivos_evento
                )

                custo_evento = float(
                    row.get(
                        "custo",
                        0
                    ) or 0
                )

                lucro_evento = (
                    faturamento_evento
                    -
                    custo_evento
                )

                f1, f2, f3, f4 = st.columns(4)

                f1.metric(
                    "📋 Contrato",
                    f"R$ {venda_evento:,.2f}"
                )

                f2.metric(
                    "⏰ Aditivos",
                    f"R$ {aditivos_evento:,.2f}"
                )

                f3.metric(
                    "💰 Faturamento",
                    f"R$ {faturamento_evento:,.2f}"
                )

                f4.metric(
                    "📈 Lucro",
                    f"R$ {lucro_evento:,.2f}"
                )

                # =================================================
                # FECHAR
                # =================================================

                if st.button(
                    "🔽 Fechar Evento",
                    key=(
                        f"fechar_evento_"
                        f"{evento_id}"
                    )
                ):

                    st.session_state[
                        chave_aberto
                    ] = False

                    st.rerun()

            st.divider()


# =========================================================
# COPOS, TAÇAS E DECOR
# =========================================================

elif menu == "Copos, Taças e Decor":

    st.title("🥂 Copos, Taças e Decor")

    aba_copos, aba_decor = st.tabs(
        [
            "🥂 Copos e Taças",
            "✨ Materiais Decorativos"
        ]
    )

    # =====================================================
    # ABA — COPOS E TAÇAS
    # =====================================================

    with aba_copos:

        cadastro, lista = st.tabs(
            [
                "➕ Cadastro",
                "📋 Lista"
            ]
        )

        # =================================================
        # CADASTRO
        # =================================================

        with cadastro:

            st.subheader("Cadastro de Copos e Taças")

            with st.form(
                "form_copos_tacas",
                clear_on_submit=True
            ):

                col1, col2 = st.columns(2)

                with col1:

                    tipo = st.selectbox(
                        "Tipo",
                        [
                            "Copo",
                            "Taça"
                        ]
                    )

                    nome = st.text_input(
                        "Nome"
                    )

                    modelo = st.text_input(
                        "Modelo"
                    )

                with col2:

                    capacidade = st.number_input(
                        "Capacidade (ml)",
                        min_value=0.0,
                        step=10.0,
                        format="%.0f"
                    )

                    quantidade = st.number_input(
                        "Quantidade disponível",
                        min_value=0,
                        step=1
                    )

                    observacao = st.text_area(
                        "Observação"
                    )

                cadastrar = st.form_submit_button(
                    "💾 Cadastrar"
                )

            if cadastrar:

                if not nome.strip():

                    st.error(
                        "Informe o nome do copo ou taça."
                    )

                elif quantidade < 0:

                    st.error(
                        "A quantidade não pode ser negativa."
                    )

                else:

                    try:

                        supabase.table(
                            "copos_tacas"
                        ).insert({

                            "tipo": tipo,

                            "nome": normalizar_nome(
                                nome
                            ),

                            "modelo": modelo.strip(),

                            "capacidade": capacidade,

                            "quantidade": quantidade,

                            "observacao": observacao.strip()

                        }).execute()

                        st.success(
                            "✅ Copo/Taça cadastrado com sucesso!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Erro ao cadastrar: {e}"
                        )

        # =================================================
        # LISTA
        # =================================================

        with lista:

            st.subheader(
                "Copos e Taças cadastrados"
            )

            try:

                dados = (
                    supabase
                    .table("copos_tacas")
                    .select("*")
                    .order("tipo")
                    .execute()
                )

                df_copos = pd.DataFrame(
                    dados.data
                    if dados.data
                    else []
                )

            except Exception as e:

                st.error(
                    f"Erro ao carregar copos e taças: {e}"
                )

                df_copos = pd.DataFrame()


            if df_copos.empty:

                st.info(
                    "Nenhum copo ou taça cadastrado."
                )

            else:

                # -----------------------------------------
                # PESQUISA
                # -----------------------------------------

                busca = st.text_input(
                    "🔎 Pesquisar",
                    key="busca_copos_tacas"
                )

                if busca.strip():

                    busca = busca.strip()

                    filtro = (
                        df_copos["nome"]
                        .fillna("")
                        .astype(str)
                        .str.contains(
                            busca,
                            case=False,
                            na=False
                        )
                        |
                        df_copos["modelo"]
                        .fillna("")
                        .astype(str)
                        .str.contains(
                            busca,
                            case=False,
                            na=False
                        )
                        |
                        df_copos["tipo"]
                        .fillna("")
                        .astype(str)
                        .str.contains(
                            busca,
                            case=False,
                            na=False
                        )
                    )

                    df_copos = df_copos[filtro]


                if df_copos.empty:

                    st.info(
                        "Nenhum item encontrado."
                    )

                else:

                    # -------------------------------------
                    # TOTAL
                    # -------------------------------------

                    total_copos = int(
                        df_copos["quantidade"]
                        .fillna(0)
                        .sum()
                    )

                    st.metric(
                        "🥂 Total disponível",
                        total_copos
                    )

                    st.divider()

                    # -------------------------------------
                    # EDITOR
                    # -------------------------------------

                    df_editado = st.data_editor(

                        df_copos,

                        use_container_width=True,

                        hide_index=True,

                        column_config={

                            "id":
                                st.column_config.NumberColumn(
                                    "ID",
                                    disabled=True
                                ),

                            "tipo":
                                st.column_config.SelectboxColumn(
                                    "Tipo",
                                    options=[
                                        "Copo",
                                        "Taça"
                                    ]
                                ),

                            "nome":
                                st.column_config.TextColumn(
                                    "Nome"
                                ),

                            "modelo":
                                st.column_config.TextColumn(
                                    "Modelo"
                                ),

                            "capacidade":
                                st.column_config.NumberColumn(
                                    "Capacidade (ml)",
                                    min_value=0,
                                    step=10
                                ),

                            "quantidade":
                                st.column_config.NumberColumn(
                                    "Quantidade",
                                    min_value=0,
                                    step=1
                                ),

                            "observacao":
                                st.column_config.TextColumn(
                                    "Observação"
                                ),

                            "created_at":
                                st.column_config.DatetimeColumn(
                                    "Cadastro",
                                    disabled=True
                                )
                        }
                    )

                    # -------------------------------------
                    # SALVAR
                    # -------------------------------------

                    if st.button(
                        "💾 Salvar alterações",
                        key="salvar_copos_tacas"
                    ):

                        try:

                            for _, row in df_editado.iterrows():

                                supabase.table(
                                    "copos_tacas"
                                ).update({

                                    "tipo":
                                        str(
                                            row["tipo"]
                                        ).strip(),

                                    "nome":
                                        normalizar_nome(
                                            row["nome"]
                                        ),

                                    "modelo":
                                        str(
                                            row["modelo"]
                                        ).strip(),

                                    "capacidade":
                                        float(
                                            row["capacidade"]
                                            or 0
                                        ),

                                    "quantidade":
                                        int(
                                            row["quantidade"]
                                            or 0
                                        ),

                                    "observacao":
                                        str(
                                            row["observacao"]
                                        ).strip()

                                }).eq(
                                    "id",
                                    row["id"]
                                ).execute()

                            st.success(
                                "✅ Alterações salvas!"
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Erro ao salvar: {e}"
                            )

                    # -------------------------------------
                    # EXCLUIR
                    # -------------------------------------

                    st.divider()

                    item_excluir = st.selectbox(

                        "Selecionar item para excluir",

                        df_copos["id"].tolist(),

                        key="excluir_copo_taca"
                    )

                    if st.button(
                        "🗑️ Excluir selecionado",
                        key="botao_excluir_copo_taca"
                    ):

                        try:

                            supabase.table(
                                "copos_tacas"
                            ).delete().eq(
                                "id",
                                item_excluir
                            ).execute()

                            st.success(
                                "Item excluído."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Erro ao excluir: {e}"
                            )


    # =====================================================
    # ABA — MATERIAIS DECORATIVOS
    # =====================================================

    with aba_decor:

        cadastro_decor, lista_decor = st.tabs(
            [
                "➕ Cadastro",
                "📋 Lista"
            ]
        )

        # =================================================
        # CADASTRO
        # =================================================

        with cadastro_decor:

            st.subheader(
                "Cadastro de Materiais Decorativos"
            )

            with st.form(
                "form_materiais_decorativos",
                clear_on_submit=True
            ):

                col1, col2 = st.columns(2)

                with col1:

                    nome = st.text_input(
                        "Nome do material"
                    )

                    categoria = st.text_input(
                        "Categoria"
                    )

                with col2:

                    quantidade = st.number_input(
                        "Quantidade disponível",
                        min_value=0,
                        step=1
                    )

                    observacao = st.text_area(
                        "Observação"
                    )

                cadastrar = st.form_submit_button(
                    "💾 Cadastrar"
                )

            if cadastrar:

                if not nome.strip():

                    st.error(
                        "Informe o nome do material."
                    )

                else:

                    try:

                        supabase.table(
                            "materiais_decorativos"
                        ).insert({

                            "nome":
                                normalizar_nome(
                                    nome
                                ),

                            "categoria":
                                categoria.strip(),

                            "quantidade":
                                quantidade,

                            "observacao":
                                observacao.strip()

                        }).execute()

                        st.success(
                            "✅ Material decorativo cadastrado!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Erro ao cadastrar: {e}"
                        )

        # =================================================
        # LISTA
        # =================================================

        with lista_decor:

            st.subheader(
                "Materiais Decorativos cadastrados"
            )

            try:

                dados = (
                    supabase
                    .table("materiais_decorativos")
                    .select("*")
                    .order("nome")
                    .execute()
                )

                df_decor = pd.DataFrame(
                    dados.data
                    if dados.data
                    else []
                )

            except Exception as e:

                st.error(
                    f"Erro ao carregar materiais: {e}"
                )

                df_decor = pd.DataFrame()


            if df_decor.empty:

                st.info(
                    "Nenhum material decorativo cadastrado."
                )

            else:

                # -----------------------------------------
                # PESQUISA
                # -----------------------------------------

                busca = st.text_input(
                    "🔎 Pesquisar",
                    key="busca_materiais_decorativos"
                )

                if busca.strip():

                    busca = busca.strip()

                    filtro = (
                        df_decor["nome"]
                        .fillna("")
                        .astype(str)
                        .str.contains(
                            busca,
                            case=False,
                            na=False
                        )
                        |
                        df_decor["categoria"]
                        .fillna("")
                        .astype(str)
                        .str.contains(
                            busca,
                            case=False,
                            na=False
                        )
                    )

                    df_decor = df_decor[filtro]


                if df_decor.empty:

                    st.info(
                        "Nenhum material encontrado."
                    )

                else:

                    # -------------------------------------
                    # TOTAL
                    # -------------------------------------

                    total_decor = int(
                        df_decor["quantidade"]
                        .fillna(0)
                        .sum()
                    )

                    st.metric(
                        "✨ Total de materiais disponíveis",
                        total_decor
                    )

                    st.divider()

                    # -------------------------------------
                    # EDITOR
                    # -------------------------------------

                    df_editado = st.data_editor(

                        df_decor,

                        use_container_width=True,

                        hide_index=True,

                        column_config={

                            "id":
                                st.column_config.NumberColumn(
                                    "ID",
                                    disabled=True
                                ),

                            "nome":
                                st.column_config.TextColumn(
                                    "Nome"
                                ),

                            "categoria":
                                st.column_config.TextColumn(
                                    "Categoria"
                                ),

                            "quantidade":
                                st.column_config.NumberColumn(
                                    "Quantidade",
                                    min_value=0,
                                    step=1
                                ),

                            "observacao":
                                st.column_config.TextColumn(
                                    "Observação"
                                ),

                            "created_at":
                                st.column_config.DatetimeColumn(
                                    "Cadastro",
                                    disabled=True
                                )
                        }
                    )

                    # -------------------------------------
                    # SALVAR
                    # -------------------------------------

                    if st.button(
                        "💾 Salvar alterações",
                        key="salvar_materiais_decorativos"
                    ):

                        try:

                            for _, row in df_editado.iterrows():

                                supabase.table(
                                    "materiais_decorativos"
                                ).update({

                                    "nome":
                                        normalizar_nome(
                                            row["nome"]
                                        ),

                                    "categoria":
                                        str(
                                            row["categoria"]
                                        ).strip(),

                                    "quantidade":
                                        int(
                                            row["quantidade"]
                                            or 0
                                        ),

                                    "observacao":
                                        str(
                                            row["observacao"]
                                        ).strip()

                                }).eq(
                                    "id",
                                    row["id"]
                                ).execute()

                            st.success(
                                "✅ Alterações salvas!"
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Erro ao salvar: {e}"
                            )

                    # -------------------------------------
                    # EXCLUIR
                    # -------------------------------------

                    st.divider()

                    item_excluir = st.selectbox(

                        "Selecionar material para excluir",

                        df_decor["id"].tolist(),

                        key="excluir_material_decorativo"
                    )

                    if st.button(
                        "🗑️ Excluir selecionado",
                        key="botao_excluir_material_decorativo"
                    ):

                        try:

                            supabase.table(
                                "materiais_decorativos"
                            ).delete().eq(
                                "id",
                                item_excluir
                            ).execute()

                            st.success(
                                "Material excluído."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Erro ao excluir: {e}"
                            )

# =========================================================
# MATERIAIS E UTENSÍLIOS DE BAR
# =========================================================

elif menu == "Materiais e Utensílios de Bar":

    st.title("🍸 Materiais e Utensílios de Bar")

    cadastro, lista = st.tabs(
        [
            "➕ Cadastro",
            "📋 Estoque"
        ]
    )

    # =====================================================
    # ABA — CADASTRO
    # =====================================================

    with cadastro:

        st.subheader("➕ Cadastro de Material / Utensílio")

        with st.form(
            "form_materiais_utensilios_bar",
            clear_on_submit=True
        ):

            col1, col2 = st.columns(2)

            # -------------------------------------------------
            # COLUNA 1
            # -------------------------------------------------

            with col1:

                nome = st.text_input(
                    "Nome do material / utensílio",
                    placeholder="Ex.: Coqueteleira, dosador, colher bailarina..."
                )

                categoria = st.selectbox(
                    "Categoria",
                    [
                        "Utensílio",
                        "Equipamento",
                        "Material de Bar",
                        "Acessório",
                        "Outros"
                    ]
                )

                unidade = st.selectbox(
                    "Unidade de controle",
                    [
                        "Unidade",
                        "Kit",
                        "Caixa",
                        "Pacote",
                        "Par"
                    ]
                )

            # -------------------------------------------------
            # COLUNA 2
            # -------------------------------------------------

            with col2:

                quantidade = st.number_input(
                    "Quantidade disponível",
                    min_value=0,
                    value=0,
                    step=1
                )

                valor_unitario = st.number_input(
                    "Valor unitário de referência",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    help=(
                        "Valor de referência de uma unidade. "
                        "Não interfere no custo dos drinks."
                    )
                )

                observacao = st.text_area(
                    "Observação",
                    placeholder="Ex.: Uso exclusivo para eventos grandes..."
                )

            cadastrar = st.form_submit_button(
                "💾 Cadastrar"
            )

        # =====================================================
        # PROCESSAR CADASTRO
        # =====================================================

        if cadastrar:

            nome_limpo = normalizar_nome(nome)

            if not nome_limpo:

                st.error(
                    "Informe o nome do material ou utensílio."
                )

            elif quantidade < 0:

                st.error(
                    "A quantidade não pode ser negativa."
                )

            elif valor_unitario < 0:

                st.error(
                    "O valor unitário não pode ser negativo."
                )

            else:

                valor_total = (
                    quantidade
                    *
                    valor_unitario
                )

                try:

                    supabase.table(
                        "materiais_utensilios_bar"
                    ).insert({

                        "nome":
                            nome_limpo,

                        "categoria":
                            categoria,

                        "unidade":
                            unidade,

                        "quantidade":
                            int(quantidade),

                        "valor_unitario":
                            float(valor_unitario),

                        "valor_total":
                            float(valor_total),

                        "observacao":
                            observacao.strip()

                    }).execute()

                    st.success(
                        "✅ Material/utensílio cadastrado com sucesso!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Erro ao cadastrar: {e}"
                    )


    # =====================================================
    # ABA — ESTOQUE
    # =====================================================

    with lista:

        st.subheader(
            "📦 Estoque de Materiais e Utensílios"
        )

        try:

            dados = (
                supabase
                .table("materiais_utensilios_bar")
                .select("*")
                .order("categoria")
                .order("nome")
                .execute()
            )

            df_materiais = pd.DataFrame(
                dados.data
                if dados.data
                else []
            )

        except Exception as e:

            st.error(
                f"Erro ao carregar materiais: {e}"
            )

            df_materiais = pd.DataFrame()


        # =================================================
        # NENHUM ITEM
        # =================================================

        if df_materiais.empty:

            st.info(
                "Nenhum material ou utensílio cadastrado."
            )

        else:

            # =================================================
            # PESQUISA
            # =================================================

            busca = st.text_input(
                "🔎 Pesquisar material ou utensílio",
                key="busca_materiais_utensilios_bar"
            )

            if busca.strip():

                busca = busca.strip()

                filtro = (

                    df_materiais["nome"]
                    .fillna("")
                    .astype(str)
                    .str.contains(
                        busca,
                        case=False,
                        na=False
                    )

                    |

                    df_materiais["categoria"]
                    .fillna("")
                    .astype(str)
                    .str.contains(
                        busca,
                        case=False,
                        na=False
                    )

                    |

                    df_materiais["unidade"]
                    .fillna("")
                    .astype(str)
                    .str.contains(
                        busca,
                        case=False,
                        na=False
                    )
                )

                df_materiais = (
                    df_materiais[filtro]
                )


            # =================================================
            # RESULTADO DA PESQUISA
            # =================================================

            if df_materiais.empty:

                st.info(
                    "Nenhum material encontrado."
                )

            else:

                # =================================================
                # GARANTIR VALORES NUMÉRICOS
                # =================================================

                df_materiais["quantidade"] = (
                    pd.to_numeric(
                        df_materiais["quantidade"],
                        errors="coerce"
                    )
                    .fillna(0)
                )

                df_materiais["valor_unitario"] = (
                    pd.to_numeric(
                        df_materiais["valor_unitario"],
                        errors="coerce"
                    )
                    .fillna(0)
                )


                # =================================================
                # RECALCULAR VALOR TOTAL
                # =================================================

                df_materiais["valor_total"] = (
                    df_materiais["quantidade"]
                    *
                    df_materiais["valor_unitario"]
                )


                # =================================================
                # INDICADORES
                # =================================================

                quantidade_total = int(
                    df_materiais["quantidade"]
                    .sum()
                )

                valor_total_estoque = float(
                    df_materiais["valor_total"]
                    .sum()
                )


                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "📦 Quantidade total",
                        quantidade_total
                    )

                with col2:

                    st.metric(
                        "💰 Valor total do estoque",
                        (
                            f"R$ {valor_total_estoque:,.2f}"
                            .replace(",", "X")
                            .replace(".", ",")
                            .replace("X", ".")
                        )
                    )


                st.divider()


                # =================================================
                # TABELA
                # =================================================

                df_editado = st.data_editor(

                    df_materiais,

                    use_container_width=True,

                    hide_index=True,

                    column_config={

                        "id":
                            st.column_config.NumberColumn(
                                "ID",
                                disabled=True
                            ),

                        "nome":
                            st.column_config.TextColumn(
                                "Nome"
                            ),

                        "categoria":
                            st.column_config.SelectboxColumn(
                                "Categoria",
                                options=[
                                    "Utensílio",
                                    "Equipamento",
                                    "Material de Bar",
                                    "Acessório",
                                    "Outros"
                                ]
                            ),

                        "unidade":
                            st.column_config.SelectboxColumn(
                                "Unidade",
                                options=[
                                    "Unidade",
                                    "Kit",
                                    "Caixa",
                                    "Pacote",
                                    "Par"
                                ]
                            ),

                        "quantidade":
                            st.column_config.NumberColumn(
                                "Quantidade",
                                min_value=0,
                                step=1
                            ),

                        "valor_unitario":
                            st.column_config.NumberColumn(
                                "💰 Valor Unitário",
                                min_value=0,
                                step=0.01,
                                format="R$ %.2f"
                            ),

                        "valor_total":
                            st.column_config.NumberColumn(
                                "💰 Valor Total",
                                format="R$ %.2f",
                                disabled=True
                            ),

                        "observacao":
                            st.column_config.TextColumn(
                                "Observação"
                            ),

                        "created_at":
                            st.column_config.DatetimeColumn(
                                "Cadastro",
                                disabled=True
                            )
                    }
                )


                # =================================================
                # SALVAR ALTERAÇÕES
                # =================================================

                if st.button(
                    "💾 Salvar alterações",
                    key="salvar_materiais_utensilios_bar"
                ):

                    try:

                        for _, row in df_editado.iterrows():

                            quantidade = int(
                                row["quantidade"]
                                or 0
                            )

                            valor_unitario = float(
                                row["valor_unitario"]
                                or 0
                            )

                            valor_total = (
                                quantidade
                                *
                                valor_unitario
                            )


                            supabase.table(
                                "materiais_utensilios_bar"
                            ).update({

                                "nome":
                                    normalizar_nome(
                                        row["nome"]
                                    ),

                                "categoria":
                                    str(
                                        row["categoria"]
                                    ).strip(),

                                "unidade":
                                    str(
                                        row["unidade"]
                                    ).strip(),

                                "quantidade":
                                    quantidade,

                                "valor_unitario":
                                    valor_unitario,

                                "valor_total":
                                    valor_total,

                                "observacao":
                                    str(
                                        row["observacao"]
                                    ).strip()

                            }).eq(
                                "id",
                                row["id"]
                            ).execute()


                        st.success(
                            "✅ Alterações salvas com sucesso!"
                        )

                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"Erro ao salvar alterações: {e}"
                        )


                # =================================================
                # EXCLUSÃO
                # =================================================

                st.divider()

                st.subheader(
                    "🗑️ Excluir material"
                )

                item_excluir = st.selectbox(

                    "Selecione o item",

                    df_materiais[
                        ["id", "nome"]
                    ].apply(
                        lambda x:
                        f"{x['id']} - {x['nome']}",
                        axis=1
                    ).tolist(),

                    key="excluir_material_utensilio"
                )


                if st.button(
                    "🗑️ Excluir selecionado",
                    key="botao_excluir_material_utensilio"
                ):

                    try:

                        id_excluir = int(
                            item_excluir.split(
                                " - ",
                                1
                            )[0]
                        )

                        supabase.table(
                            "materiais_utensilios_bar"
                        ).delete().eq(
                            "id",
                            id_excluir
                        ).execute()

                        st.success(
                            "✅ Material/utensílio excluído."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Erro ao excluir: {e}"
                        )


elif menu == "Receitas":

    import unicodedata

    st.title("🍸 Receitas")

    # =========================================================
    # BASES
    # =========================================================
    df_receitas = carregar_tabela("receitas")
    df_bebidas = carregar_tabela("precos_bebidas")
    df_insumos = carregar_tabela("precos_insumos")
    df_artesanais = carregar_tabela("precos_artesanais")

    # =========================================================
    # COLUNA DO DRINK
    # =========================================================
    if not df_receitas.empty:
        if "drink" in df_receitas.columns:
            COLUNA_DRINK = "drink"
        elif "bebida" in df_receitas.columns:
            COLUNA_DRINK = "bebida"
        else:
            st.error(
                "A tabela 'receitas' precisa possuir a coluna 'drink' ou 'bebida'."
            )
            st.stop()
    else:
        COLUNA_DRINK = "bebida"

    # =========================================================
    # VALIDAÇÃO DA MIGRAÇÃO
    # =========================================================
    colunas_novas = ["categoria", "tipo_base"]

    # Com a tabela vazia, o DataFrame não informa o schema do Supabase.
    # Nesse caso deixamos o INSERT validar a estrutura depois da migração.
    colunas_faltantes = (
        [
            c for c in colunas_novas
            if c not in df_receitas.columns
        ]
        if not df_receitas.empty
        else []
    )

    if colunas_faltantes:
        st.warning(
            "⚠️ A tabela `receitas` ainda não possui todas as colunas da "
            "padronização nova: "
            + ", ".join(colunas_faltantes)
            + ". Execute primeiro o SQL de migração que acompanha este código."
        )

    # =========================================================
    # FUNÇÕES AUXILIARES
    # =========================================================
    CATEGORIAS_RECEITA = [
        "Bebida",
        "Fruta / Insumo",
        "Artesanal",
        "Gelo",
    ]

    UNIDADES_RECEITA = [
        "ml",
        "g",
        "un",
        "gota",
        "fatia",
        "guarnição",
    ]

    def texto_seguro(valor):
        """Converte valores vazios/NaN em texto vazio para não exibir 'nan'."""
        try:
            if valor is None or pd.isna(valor):
                return ""
        except (TypeError, ValueError):
            pass
        return str(valor).strip()

    def chave_texto(valor):
        """Normalização apenas para comparação."""
        texto = texto_seguro(valor).lower()
        texto = unicodedata.normalize("NFKD", texto)
        texto = "".join(
            c for c in texto
            if not unicodedata.combining(c)
        )
        return " ".join(texto.split())

    def numero_seguro(valor, padrao=0.0):
        try:
            if pd.isna(valor):
                return float(padrao)
            return float(valor)
        except (TypeError, ValueError):
            return float(padrao)

    def valores_unicos(df, coluna):
        if df is None or df.empty or coluna not in df.columns:
            return []

        valores = []
        vistos = set()

        for valor in df[coluna].dropna().astype(str):
            valor_limpo = valor.strip()
            chave = chave_texto(valor_limpo)

            if valor_limpo and chave not in vistos:
                valores.append(valor_limpo)
                vistos.add(chave)

        return sorted(valores, key=lambda x: chave_texto(x))

    def tabela_da_categoria(categoria):
        if categoria == "Bebida":
            return df_bebidas, "precos_bebidas"
        if categoria == "Fruta / Insumo":
            return df_insumos, "precos_insumos"
        if categoria == "Artesanal":
            return df_artesanais, "precos_artesanais"
        if categoria == "Gelo":
            return df_insumos, "precos_insumos"
        return pd.DataFrame(), None

    def obter_bases_categoria(categoria):
        """
        Opções sempre geradas a partir do banco.
        Não existe lista fixa de marcas, tipos ou tamanhos.
        """
        df_base, _ = tabela_da_categoria(categoria)

        if df_base.empty:
            return []

        if categoria == "Gelo":
            candidatos = []

            if "nome" in df_base.columns:
                for valor in df_base["nome"].dropna().astype(str):
                    if "gelo" in chave_texto(valor):
                        candidatos.append(valor.strip())

            if "tipo" in df_base.columns:
                for _, linha in df_base.iterrows():
                    tipo = str(linha.get("tipo", "") or "").strip()
                    nome = str(linha.get("nome", "") or "").strip()
                    if "gelo" in chave_texto(tipo):
                        candidatos.append(tipo or nome)

            return sorted(
                list({x for x in candidatos if str(x).strip()}),
                key=lambda x: chave_texto(x),
            )

        if categoria == "Bebida":
            # A receita fica vinculada SOMENTE ao TIPO da bebida.
            # Nome/marca e tamanho de embalagem nunca entram como base da receita.
            return valores_unicos(df_base, "tipo")

        if categoria == "Artesanal":
            tipos = valores_unicos(df_base, "tipo")
            nomes_sem_tipo = []

            if "nome" in df_base.columns:
                for _, linha in df_base.iterrows():
                    tipo = str(linha.get("tipo", "") or "").strip()
                    nome = str(linha.get("nome", "") or "").strip()
                    if nome and not tipo:
                        nomes_sem_tipo.append(nome)

            bases = tipos + nomes_sem_tipo
            return sorted(
                list({x for x in bases if str(x).strip()}),
                key=lambda x: chave_texto(x),
            )

        return valores_unicos(df_base, "nome")

    def localizar_opcoes_base(categoria, tipo_base):
        """
        Ex.: base Gin -> todas as marcas/tamanhos cujo tipo seja Gin.
        """
        df_base, _ = tabela_da_categoria(categoria)

        if df_base.empty or not str(tipo_base or "").strip():
            return pd.DataFrame()

        chave_base = chave_texto(tipo_base)
        mascara = pd.Series(False, index=df_base.index)

        if categoria == "Bebida":
            # Para bebidas, o vínculo é exclusivamente pelo TIPO.
            # A marca/nome será escolhida apenas no orçamento.
            if "tipo" not in df_base.columns:
                return pd.DataFrame()

            mascara = (
                df_base["tipo"]
                .fillna("")
                .astype(str)
                .apply(chave_texto)
                == chave_base
            )
            return df_base[mascara].copy()

        if "tipo" in df_base.columns:
            mascara = mascara | (
                df_base["tipo"]
                .fillna("")
                .astype(str)
                .apply(chave_texto)
                == chave_base
            )

        if "nome" in df_base.columns:
            mascara = mascara | (
                df_base["nome"]
                .fillna("")
                .astype(str)
                .apply(chave_texto)
                == chave_base
            )

        return df_base[mascara].copy()

    def custo_base_unitario(categoria, tipo_base):
        """
        Custo por unidade-base sem escolher marca fixa.
        Se houver várias marcas/tamanhos, retorna mínimo, média e máximo.
        """
        opcoes = localizar_opcoes_base(categoria, tipo_base)

        if opcoes.empty:
            return {
                "encontrado": False,
                "quantidade_opcoes": 0,
                "unidade_base": None,
                "min": None,
                "medio": None,
                "max": None,
            }

        custos = []

        for _, linha in opcoes.iterrows():
            preco = numero_seguro(linha.get("preco", 0))

            if preco < 0:
                continue

            if categoria in ["Bebida", "Artesanal"]:
                volume = numero_seguro(linha.get("quantidade", 0))
                if volume > 0:
                    custos.append(preco / volume)

            elif categoria in ["Fruta / Insumo", "Gelo"]:
                # Em precos_insumos o preço é por KG.
                custos.append(preco / 1000)

        unidade_base = (
            "ml" if categoria in ["Bebida", "Artesanal"] else "g"
        )

        if not custos:
            return {
                "encontrado": True,
                "quantidade_opcoes": len(opcoes),
                "unidade_base": unidade_base,
                "min": None,
                "medio": None,
                "max": None,
            }

        return {
            "encontrado": True,
            "quantidade_opcoes": len(opcoes),
            "unidade_base": unidade_base,
            "min": min(custos),
            "medio": sum(custos) / len(custos),
            "max": max(custos),
        }

    def calcular_custo_referencia(categoria, tipo_base, quantidade, unidade):
        """
        Custo MÍNIMO de referência de UM drink.
        Para cada base, utiliza a opção cadastrada com menor custo proporcional.
        A receita continua vinculada somente ao tipo/base; marca e embalagem
        permanecem livres para simulação e para escolha posterior no orçamento.
        """
        custo_base = custo_base_unitario(categoria, tipo_base)

        if not custo_base["encontrado"] or custo_base["min"] is None:
            return None, custo_base

        if str(unidade) != custo_base["unidade_base"]:
            # Não inventa conversão de fatia/un/gota para g ou ml.
            return None, custo_base

        return (
            numero_seguro(quantidade) * custo_base["min"],
            custo_base,
        )

    def custo_componente_por_opcao(categoria, linha_opcao, quantidade, unidade):
        """Calcula o custo do componente usando uma linha específica da precificação."""
        quantidade = numero_seguro(quantidade)
        preco = numero_seguro(linha_opcao.get("preco", 0))

        if categoria in ["Bebida", "Artesanal"]:
            if str(unidade) != "ml":
                return None
            volume = numero_seguro(linha_opcao.get("quantidade", 0))
            if volume <= 0:
                return None
            return quantidade * (preco / volume)

        if categoria in ["Fruta / Insumo", "Gelo"]:
            if str(unidade) != "g":
                return None
            return quantidade * (preco / 1000)

        return None

    def faixa_custo_drink(receita):
        """Retorna custo mínimo, médio e máximo do drink sem fixar marcas."""
        totais = {"min": 0.0, "medio": 0.0, "max": 0.0}
        completo = True

        for _, row in receita.iterrows():
            categoria = texto_seguro(row.get("categoria", ""))
            tipo_base = texto_seguro(row.get("tipo_base", ""))
            quantidade = numero_seguro(row.get("quantidade", 0))
            unidade = texto_seguro(row.get("unidade", ""))

            if not categoria or not tipo_base:
                completo = False
                continue

            info = custo_base_unitario(categoria, tipo_base)

            if (
                not info.get("encontrado")
                or info.get("min") is None
                or info.get("medio") is None
                or info.get("max") is None
                or unidade != info.get("unidade_base")
            ):
                completo = False
                continue

            totais["min"] += quantidade * info["min"]
            totais["medio"] += quantidade * info["medio"]
            totais["max"] += quantidade * info["max"]

        totais["completo"] = completo
        return totais

    def sugerir_vinculo_antigo(ingrediente):
        """
        Sugestão conservadora: somente correspondência EXATA por nome ou tipo.
        Nada de similaridade automática.
        """
        chave = chave_texto(ingrediente)
        candidatos = []

        if not df_bebidas.empty:
            for _, linha in df_bebidas.iterrows():
                nome = str(linha.get("nome", "") or "").strip()
                tipo = str(linha.get("tipo", "") or "").strip()

                # Mesmo que a receita antiga tenha o NOME/MARCA,
                # a sugestão sempre converte para o TIPO da bebida.
                # Se o cadastro não possui tipo, não criamos vínculo automático.
                if tipo and chave and (
                    chave_texto(nome) == chave
                    or chave_texto(tipo) == chave
                ):
                    candidatos.append(("Bebida", tipo))

        if not df_insumos.empty:
            for _, linha in df_insumos.iterrows():
                nome = str(linha.get("nome", "") or "").strip()
                tipo = str(linha.get("tipo", "") or "").strip()

                tipo_util = tipo and chave_texto(tipo) != "fruta"

                if chave and (
                    chave_texto(nome) == chave
                    or (tipo_util and chave_texto(tipo) == chave)
                ):
                    categoria = (
                        "Gelo"
                        if "gelo" in chave_texto(nome)
                        or "gelo" in chave_texto(tipo)
                        else "Fruta / Insumo"
                    )
                    base = nome if categoria == "Fruta / Insumo" else (tipo or nome)
                    candidatos.append((categoria, base))

        if not df_artesanais.empty:
            for _, linha in df_artesanais.iterrows():
                nome = str(linha.get("nome", "") or "").strip()
                tipo = str(linha.get("tipo", "") or "").strip()
                if chave and (
                    chave_texto(nome) == chave
                    or chave_texto(tipo) == chave
                ):
                    candidatos.append(("Artesanal", tipo or nome))

        unicos = []
        vistos = set()

        for categoria, base in candidatos:
            k = (chave_texto(categoria), chave_texto(base))
            if k not in vistos:
                unicos.append((categoria, base))
                vistos.add(k)

        if len(unicos) == 1:
            return {
                "status": "sugerido",
                "categoria": unicos[0][0],
                "tipo_base": unicos[0][1],
            }

        if len(unicos) > 1:
            return {
                "status": "ambiguo",
                "categoria": None,
                "tipo_base": None,
                "candidatos": unicos,
            }

        return {
            "status": "nao_encontrado",
            "categoria": None,
            "tipo_base": None,
        }

    def unidade_padrao_categoria(categoria):
        if categoria in ["Bebida", "Artesanal"]:
            return "ml"
        if categoria in ["Fruta / Insumo", "Gelo"]:
            return "g"
        return "un"

    def limpar_cadastro_receita():
        st.session_state["ingredientes_temp_v3"] = []
        st.session_state["drink_nome_v3"] = ""
        st.session_state["tipo_copo_temp_v3"] = "Alto"
        st.session_state["modelo_copo_temp_v3"] = ""

        for chave in [
            "campo_nome_drink_v3",
            "modelo_copo_cadastro_v3",
        ]:
            if chave in st.session_state:
                del st.session_state[chave]


    # =========================================================
    # EDIÇÃO COMPLETA DE RECEITA
    # =========================================================
    def limpar_edicao_receita():
        """Limpa somente os estados usados pelo editor de receitas."""
        prefixos = (
            "editar_receita_v6",
            "edit_receita_",
        )

        for chave in list(st.session_state.keys()):
            if chave.startswith(prefixos):
                del st.session_state[chave]

    def iniciar_edicao_receita(nome_drink):
        """
        Carrega a receita atual para um editor seguro.
        A receita continua vinculada apenas à categoria/base; marcas e
        embalagens nunca são gravadas aqui.
        """
        receita_edit = df_receitas[
            df_receitas[COLUNA_DRINK].astype(str) == str(nome_drink)
        ].copy()

        if receita_edit.empty:
            return

        tipo_copo_atual = "Alto"
        modelo_copo_atual = ""

        if "tipo_copo" in receita_edit.columns:
            valores = receita_edit["tipo_copo"].dropna().astype(str).tolist()
            if valores and str(valores[0]).strip():
                tipo_copo_atual = str(valores[0]).strip()

        if "modelo_copo" in receita_edit.columns:
            valores = receita_edit["modelo_copo"].dropna().astype(str).tolist()
            if valores:
                modelo_copo_atual = str(valores[0]).strip()

        itens = []
        ids_originais = []

        for posicao, (_, linha) in enumerate(receita_edit.iterrows()):
            item_id = linha.get("id") if "id" in receita_edit.columns else None
            if item_id is not None and not pd.isna(item_id):
                try:
                    item_id = int(item_id)
                    ids_originais.append(item_id)
                except (TypeError, ValueError):
                    item_id = None

            ingrediente = texto_seguro(linha.get("ingrediente", ""))
            categoria = texto_seguro(linha.get("categoria", ""))
            tipo_base = texto_seguro(linha.get("tipo_base", ""))

            if not categoria or not tipo_base:
                sugestao = sugerir_vinculo_antigo(ingrediente)
                if sugestao.get("status") == "sugerido":
                    categoria = categoria or sugestao.get("categoria", "")
                    tipo_base = tipo_base or sugestao.get("tipo_base", "")

            itens.append({
                "id": item_id,
                "uid": f"db_{item_id}" if item_id is not None else f"linha_{posicao}",
                "ingrediente_original": ingrediente,
                "categoria": categoria,
                "tipo_base": tipo_base,
                "quantidade": numero_seguro(linha.get("quantidade", 0)),
                "unidade": str(linha.get("unidade", "") or "").strip(),
            })

        limpar_edicao_receita()

        st.session_state["editar_receita_v7_ativa"] = str(nome_drink)
        st.session_state["editar_receita_v7_nome_original"] = str(nome_drink)
        st.session_state["editar_receita_v7_itens"] = itens
        st.session_state["editar_receita_v7_ids_originais"] = ids_originais
        st.session_state["editar_receita_v7_contador"] = 0

        st.session_state["edit_receita_nome_v6"] = str(nome_drink)
        st.session_state["edit_receita_tipo_copo_v6"] = (
            tipo_copo_atual if tipo_copo_atual in [
                "Alto", "Baixo", "Taça", "Coupé", "Martini", "Caneca", "Outro"
            ] else "Alto"
        )
        st.session_state["edit_receita_modelo_copo_v6"] = modelo_copo_atual

    # =========================================================
    # ESTADOS
    # =========================================================
    if "ingredientes_temp_v3" not in st.session_state:
        st.session_state["ingredientes_temp_v3"] = []
    if "drink_nome_v3" not in st.session_state:
        st.session_state["drink_nome_v3"] = ""
    if "tipo_copo_temp_v3" not in st.session_state:
        st.session_state["tipo_copo_temp_v3"] = "Alto"
    if "modelo_copo_temp_v3" not in st.session_state:
        st.session_state["modelo_copo_temp_v3"] = ""

    # =========================================================
    # ABAS
    # =========================================================
    aba_cadastro, aba_lista, aba_revisao = st.tabs([
        "➕ Cadastro",
        "📋 Drinks Cadastrados",
        "🔎 Revisão das Receitas",
    ])

    # =========================================================
    # ABA 1 — CADASTRO
    # =========================================================
    with aba_cadastro:
        st.subheader("🍸 Cadastro de Drink")
        st.caption(
            "A receita define somente a BASE/TIPO do ingrediente. Para bebidas, "
            "marca e tamanho da embalagem nunca ficam presos à receita e serão "
            "escolhidos apenas no orçamento."
        )

        drink = st.text_input(
            "Nome do drink",
            value=st.session_state["drink_nome_v3"],
            key="campo_nome_drink_v3",
        )

        st.markdown("### 🥂 Copo / Taça")

        tipos_copo = [
            "Alto", "Baixo", "Taça", "Coupé", "Martini", "Caneca", "Outro"
        ]

        col1, col2 = st.columns(2)

        with col1:
            tipo_copo = st.selectbox(
                "Tipo de copo",
                tipos_copo,
                index=(
                    tipos_copo.index(st.session_state["tipo_copo_temp_v3"])
                    if st.session_state["tipo_copo_temp_v3"] in tipos_copo
                    else 0
                ),
                key="tipo_copo_cadastro_v3",
            )

        with col2:
            modelo_copo = st.text_input(
                "Modelo do copo / taça",
                value=st.session_state["modelo_copo_temp_v3"],
                placeholder="Ex.: Long Drink 350 ml",
                key="modelo_copo_cadastro_v3",
            )

        st.divider()
        st.markdown("### 🧪 Componentes do Drink")

        c1, c2 = st.columns(2)
        with c1:
            categoria_nova = st.selectbox(
                "Categoria",
                CATEGORIAS_RECEITA,
                key="nova_categoria_receita_v3",
            )

        bases_disponiveis = obter_bases_categoria(categoria_nova)

        with c2:
            if bases_disponiveis:
                tipo_base_novo = st.selectbox(
                    "Base do ingrediente",
                    bases_disponiveis,
                    key="novo_tipo_base_receita_v3",
                )
            else:
                tipo_base_novo = ""
                st.selectbox(
                    "Base do ingrediente",
                    ["Nenhum cadastro disponível"],
                    disabled=True,
                    key="novo_tipo_base_vazio_v3",
                )

        if not bases_disponiveis:
            if categoria_nova == "Bebida":
                st.warning(
                    "Não há **Tipos de bebida** disponíveis. Na Precificação, "
                    "preencha o campo **Tipo do item** (ex.: Gin, Vodka, Rum). "
                    "Marca e tamanho não são usados como base da receita."
                )
            else:
                st.warning(
                    f"Não há base disponível para **{categoria_nova}**. "
                    "Cadastre primeiro o item na Precificação."
                )

        unidade_sugerida = unidade_padrao_categoria(categoria_nova)
        c3, c4, c5 = st.columns([2, 2, 1])

        with c3:
            quantidade_nova = st.number_input(
                "Quantidade por drink",
                min_value=0.0,
                step=1.0,
                format="%.2f",
                key="nova_quantidade_receita_v3",
            )

        with c4:
            indice_unidade = (
                UNIDADES_RECEITA.index(unidade_sugerida)
                if unidade_sugerida in UNIDADES_RECEITA
                else 0
            )
            unidade_nova = st.selectbox(
                "Unidade",
                UNIDADES_RECEITA,
                index=indice_unidade,
                key=(
                    "nova_unidade_receita_v3_"
                    + chave_texto(categoria_nova)
                    .replace(" ", "_")
                    .replace("/", "_")
                ),
            )

        with c5:
            adicionar = st.button(
                "➕ Adicionar",
                use_container_width=True,
                key="add_ingrediente_receita_v3",
            )

        if tipo_base_novo:
            custo_previa, info_custo = calcular_custo_referencia(
                categoria_nova,
                tipo_base_novo,
                quantidade_nova,
                unidade_nova,
            )

            if info_custo["encontrado"]:
                if custo_previa is not None:
                    st.caption(
                        f"💰 Custo mínimo de referência deste componente: "
                        f"**R$ {custo_previa:,.2f}** "
                        f"({info_custo['quantidade_opcoes']} opção(ões) de preço)"
                    )
                else:
                    st.caption(
                        "ℹ️ O item está cadastrado, mas não existe conversão "
                        f"automática de **{unidade_nova}** para "
                        f"**{info_custo['unidade_base']}**. Para custo exato, "
                        "prefira ml para líquidos e g para itens por KG."
                    )

        if adicionar:
            if not drink.strip():
                st.warning("Informe primeiro o nome do drink.")
            elif not tipo_base_novo:
                st.warning("Selecione uma base de ingrediente.")
            elif quantidade_nova <= 0:
                st.warning("A quantidade deve ser maior que zero.")
            else:
                st.session_state["drink_nome_v3"] = drink.strip()
                st.session_state["tipo_copo_temp_v3"] = tipo_copo
                st.session_state["modelo_copo_temp_v3"] = modelo_copo.strip()

                chave_nova = (
                    chave_texto(categoria_nova),
                    chave_texto(tipo_base_novo),
                    unidade_nova,
                )

                duplicado = False
                for item in st.session_state["ingredientes_temp_v3"]:
                    chave_item = (
                        chave_texto(item.get("categoria")),
                        chave_texto(item.get("tipo_base")),
                        str(item.get("unidade", "")),
                    )
                    if chave_item == chave_nova:
                        duplicado = True
                        break

                if duplicado:
                    st.warning(
                        "Esse componente já foi adicionado à receita. "
                        "Remova e adicione novamente com a quantidade correta."
                    )
                else:
                    st.session_state["ingredientes_temp_v3"].append({
                        "ingrediente": str(tipo_base_novo).strip(),
                        "categoria": categoria_nova,
                        "tipo_base": str(tipo_base_novo).strip(),
                        "quantidade": float(quantidade_nova),
                        "unidade": unidade_nova,
                    })
                    st.rerun()

        temp = st.session_state["ingredientes_temp_v3"]

        if temp:
            st.markdown("### 📋 Componentes da receita")

            linhas_preview = []
            custo_total_preview = 0.0
            custo_incompleto = False

            for posicao, item in enumerate(temp):
                custo_item, custo_info = calcular_custo_referencia(
                    item["categoria"],
                    item["tipo_base"],
                    item["quantidade"],
                    item["unidade"],
                )

                if custo_item is None:
                    custo_incompleto = True
                else:
                    custo_total_preview += custo_item

                linhas_preview.append({
                    "#": posicao + 1,
                    "Categoria": item["categoria"],
                    "Base": item["tipo_base"],
                    "Quantidade": item["quantidade"],
                    "Unidade": item["unidade"],
                    "Opções preço": custo_info["quantidade_opcoes"],
                    "Custo ref.": custo_item,
                })

            st.dataframe(
                pd.DataFrame(linhas_preview),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Custo ref.": st.column_config.NumberColumn(
                        "Custo ref.", format="R$ %.2f"
                    )
                },
            )

            st.metric(
                "💰 Custo estimado do drink",
                f"R$ {custo_total_preview:,.2f}",
                help=(
                    "Custo médio de referência das opções de marca/embalagem "
                    "cadastradas. A marca real será escolhida no orçamento."
                ),
            )

            if custo_incompleto:
                st.warning(
                    "Algum componente não possui conversão de custo automática. "
                    "A soma considera apenas os componentes calculáveis."
                )

            col_rem1, col_rem2 = st.columns([3, 1])
            with col_rem1:
                remover_pos = st.selectbox(
                    "Remover componente",
                    list(range(1, len(temp) + 1)),
                    format_func=lambda x: f"{x} - {temp[x-1]['tipo_base']}",
                    key="remover_comp_receita_v3",
                )
            with col_rem2:
                if st.button(
                    "🗑️ Remover",
                    use_container_width=True,
                    key="remover_comp_btn_v3",
                ):
                    temp.pop(remover_pos - 1)
                    st.rerun()

        col_salvar, col_limpar = st.columns(2)

        with col_salvar:
            if st.button(
                "💾 Salvar Drink",
                use_container_width=True,
                key="salvar_drink_v3",
            ):
                nome_final = (st.session_state["drink_nome_v3"] or drink).strip()

                if colunas_faltantes:
                    st.error(
                        "Execute primeiro o SQL de migração da tabela `receitas` "
                        "para criar `categoria` e `tipo_base`."
                    )
                elif not nome_final:
                    st.error("Informe o nome do drink.")
                elif not temp:
                    st.error("Adicione pelo menos um componente.")
                elif not modelo_copo.strip():
                    st.error("Informe o modelo do copo / taça.")
                else:
                    try:
                        supabase.table("receitas").delete().eq(
                            COLUNA_DRINK, nome_final
                        ).execute()

                        for item in temp:
                            supabase.table("receitas").insert({
                                COLUNA_DRINK: nome_final,
                                "ingrediente": item["tipo_base"],
                                "categoria": item["categoria"],
                                "tipo_base": item["tipo_base"],
                                "quantidade": float(item["quantidade"]),
                                "unidade": item["unidade"],
                                "tipo_copo": tipo_copo,
                                "modelo_copo": modelo_copo.strip(),
                            }).execute()

                        st.success("✅ Drink salvo e padronizado com sucesso!")
                        limpar_cadastro_receita()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar drink: {e}")

        with col_limpar:
            if st.button(
                "❌ Limpar",
                use_container_width=True,
                key="limpar_drink_v3",
            ):
                limpar_cadastro_receita()
                st.rerun()

    # =========================================================
    # ABA 2 — DRINKS CADASTRADOS
    # =========================================================
    with aba_lista:
        if df_receitas.empty:
            st.info("Nenhum drink cadastrado.")
        else:
            drinks_todos = sorted(
                df_receitas[COLUNA_DRINK]
                .dropna()
                .astype(str)
                .unique(),
                key=lambda x: chave_texto(x),
            )

            # -----------------------------------------------------
            # FUNÇÃO VISUAL — RESUMO DO DRINK
            # -----------------------------------------------------
            def montar_resumo_visual_drink(drink_nome):
                receita = df_receitas[
                    df_receitas[COLUNA_DRINK].astype(str) == str(drink_nome)
                ].copy()

                custo_drink = 0.0
                custo_incompleto = False
                vinculo_pendente = False
                dados_componentes = []

                for _, row in receita.iterrows():
                    ingrediente = texto_seguro(row.get("ingrediente", ""))
                    categoria = texto_seguro(row.get("categoria", ""))
                    tipo_base = texto_seguro(row.get("tipo_base", ""))
                    quantidade = numero_seguro(row.get("quantidade", 0))
                    unidade = texto_seguro(row.get("unidade", ""))

                    categoria_exibida = categoria
                    base_exibida = tipo_base

                    if not categoria or not tipo_base:
                        vinculo_pendente = True
                        sugestao = sugerir_vinculo_antigo(ingrediente)
                        if sugestao["status"] == "sugerido":
                            categoria_exibida = "⚠️ " + sugestao["categoria"]
                            base_exibida = sugestao["tipo_base"]
                        else:
                            categoria_exibida = "⚠️ Pendente"
                            base_exibida = "Pendente"

                    custo_item = None
                    custo_info = {"quantidade_opcoes": 0}

                    if categoria and tipo_base:
                        custo_item, custo_info = calcular_custo_referencia(
                            categoria,
                            tipo_base,
                            quantidade,
                            unidade,
                        )

                    if custo_item is None:
                        custo_incompleto = True
                    else:
                        custo_drink += custo_item

                    dados_componentes.append({
                        "Ingrediente": ingrediente,
                        "Categoria": categoria_exibida,
                        "Base": base_exibida,
                        "Quantidade": quantidade,
                        "Unidade": unidade,
                        "Opções": int(custo_info.get("quantidade_opcoes", 0) or 0),
                        "Custo ref.": custo_item,
                    })

                return {
                    "receita": receita,
                    "custo": custo_drink,
                    "custo_incompleto": custo_incompleto,
                    "vinculo_pendente": vinculo_pendente,
                    "componentes": dados_componentes,
                }

            resumos_drinks = {
                drink_nome: montar_resumo_visual_drink(drink_nome)
                for drink_nome in drinks_todos
            }

            total_drinks_cadastrados = len(drinks_todos)
            total_validados = sum(
                1 for dados in resumos_drinks.values()
                if not dados["vinculo_pendente"]
            )
            total_pendentes = total_drinks_cadastrados - total_validados

            custos_completos = [
                dados["custo"]
                for dados in resumos_drinks.values()
                if not dados["custo_incompleto"]
            ]

            custo_medio = (
                sum(custos_completos) / len(custos_completos)
                if custos_completos else 0.0
            )

            # -----------------------------------------------------
            # RESUMO DA BASE
            # -----------------------------------------------------
            st.markdown("### 📊 Visão geral das receitas")

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("🍸 Drinks", total_drinks_cadastrados)
            k2.metric("✅ Validados", total_validados)
            k3.metric("⚠️ Pendentes", total_pendentes)
            k4.metric(
                "💰 Custo base médio",
                f"R$ {custo_medio:,.2f}",
                help="Média dos custos mínimos das receitas com referência completa.",
            )

            st.divider()

            # -----------------------------------------------------
            # BUSCA E FILTRO
            # -----------------------------------------------------
            f1, f2 = st.columns([3, 1])

            with f1:
                filtro_drink = st.text_input(
                    "🔎 Pesquisar drink",
                    key="busca_drink_receitas_v9",
                    placeholder="Digite parte do nome do drink...",
                )

            with f2:
                filtro_status = st.selectbox(
                    "Status",
                    ["Todos", "✅ Validados", "⚠️ Pendentes"],
                    key="filtro_status_receitas_v9",
                )

            drinks = drinks_todos.copy()

            if filtro_drink:
                drinks = [
                    d for d in drinks
                    if chave_texto(filtro_drink) in chave_texto(d)
                ]

            if filtro_status == "✅ Validados":
                drinks = [
                    d for d in drinks
                    if not resumos_drinks[d]["vinculo_pendente"]
                ]
            elif filtro_status == "⚠️ Pendentes":
                drinks = [
                    d for d in drinks
                    if resumos_drinks[d]["vinculo_pendente"]
                ]

            st.caption(
                f"Exibindo **{len(drinks)}** de **{total_drinks_cadastrados}** drinks cadastrados."
            )

            # -----------------------------------------------------
            # LISTA COMPACTA / EXPANSÍVEL
            # -----------------------------------------------------
            for drink_nome in drinks:
                dados_resumo = resumos_drinks[drink_nome]
                receita = dados_resumo["receita"]
                custo_drink = dados_resumo["custo"]
                custo_incompleto = dados_resumo["custo_incompleto"]
                vinculo_pendente = dados_resumo["vinculo_pendente"]
                dados_componentes = dados_resumo["componentes"]

                status_icone = "⚠️" if vinculo_pendente else "✅"
                qtd_componentes = len(dados_componentes)

                if custo_incompleto:
                    custo_label = f"R$ {custo_drink:,.2f} parcial"
                else:
                    custo_label = f"R$ {custo_drink:,.2f}"

                titulo_expander = (
                    f"{status_icone} 🍸 {drink_nome}  ·  "
                    f"{qtd_componentes} componentes  ·  {custo_label}"
                )

                tipo_copo_lista = ""
                modelo_copo_lista = ""

                if "tipo_copo" in receita.columns:
                    valores = receita["tipo_copo"].dropna().astype(str).unique()
                    if len(valores) > 0:
                        tipo_copo_lista = texto_seguro(valores[0])

                if "modelo_copo" in receita.columns:
                    valores = receita["modelo_copo"].dropna().astype(str).unique()
                    if len(valores) > 0:
                        modelo_copo_lista = texto_seguro(valores[0])

                with st.expander(titulo_expander, expanded=False):
                    info1, info2, acao1, acao2 = st.columns([3.2, 2, 1, 1])

                    with info1:
                        if tipo_copo_lista or modelo_copo_lista:
                            detalhes_copo = []
                            if tipo_copo_lista:
                                detalhes_copo.append(f"🥂 {tipo_copo_lista}")
                            if modelo_copo_lista:
                                detalhes_copo.append(f"📌 {modelo_copo_lista}")
                            st.caption("  •  ".join(detalhes_copo))

                        if vinculo_pendente:
                            st.warning(
                                "Esta receita ainda possui componente pendente de vínculo.",
                                icon="⚠️",
                            )
                        else:
                            st.success(
                                "Receita validada e vinculada às bases corretas.",
                                icon="✅",
                            )

                    with info2:
                        st.metric(
                            "Custo unitário estimado",
                            f"R$ {custo_drink:,.2f}",
                            help="Custo mínimo de referência para produzir 1 drink, usando a opção proporcionalmente mais barata de cada base.",
                        )

                    with acao1:
                        if st.button(
                            "✏️ Editar",
                            key=f"editar_receita_v9_{drink_nome}",
                            use_container_width=True,
                        ):
                            iniciar_edicao_receita(drink_nome)
                            st.rerun()

                    with acao2:
                        if st.button(
                            "🗑️ Excluir",
                            key=f"excluir_receita_v9_{drink_nome}",
                            use_container_width=True,
                        ):
                            supabase.table("receitas").delete().eq(
                                COLUNA_DRINK, drink_nome
                            ).execute()

                            if (
                                st.session_state.get("editar_receita_v7_ativa")
                                == str(drink_nome)
                            ):
                                limpar_edicao_receita()

                            st.rerun()

                    df_visual = pd.DataFrame(dados_componentes)

                    st.dataframe(
                        df_visual,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Ingrediente": st.column_config.TextColumn(
                                "Ingrediente"
                            ),
                            "Categoria": st.column_config.TextColumn(
                                "Categoria"
                            ),
                            "Base": st.column_config.TextColumn(
                                "Base"
                            ),
                            "Quantidade": st.column_config.NumberColumn(
                                "Qtd.", format="%.2f"
                            ),
                            "Unidade": st.column_config.TextColumn(
                                "Un."
                            ),
                            "Opções": st.column_config.NumberColumn(
                                "Opções", format="%d",
                                help="Quantidade de marcas/opções cadastradas para esta base."
                            ),
                            "Custo ref.": st.column_config.NumberColumn(
                                "Custo ref.", format="R$ %.2f"
                            ),
                        },
                    )

                    if custo_incompleto:
                        st.caption(
                            "⚠️ Custo parcial: existe componente pendente ou unidade "
                            "sem conversão automática."
                        )

                    # -------------------------------------------------
                    # SIMULADOR DE MARCAS / VARIAÇÃO DE CUSTO
                    # -------------------------------------------------
                    bebidas_receita = []
                    for posicao_sim, (_, linha_sim) in enumerate(receita.iterrows()):
                        categoria_sim = texto_seguro(linha_sim.get("categoria", ""))
                        base_sim = texto_seguro(linha_sim.get("tipo_base", ""))
                        if categoria_sim == "Bebida" and base_sim:
                            bebidas_receita.append((posicao_sim, linha_sim))

                    if bebidas_receita and not vinculo_pendente:
                        with st.expander("🎚️ Simular marcas e comparar custo", expanded=False):
                            st.caption(
                                "A receita continua presa somente ao TIPO/BASE. "
                                "As marcas abaixo servem apenas para simular o custo unitário."
                            )

                            faixa = faixa_custo_drink(receita)
                            custo_simulado = 0.0
                            simulacao_completa = True
                            linhas_simulacao = []

                            for posicao_sim, (_, linha_sim) in enumerate(receita.iterrows()):
                                categoria_sim = texto_seguro(linha_sim.get("categoria", ""))
                                base_sim = texto_seguro(linha_sim.get("tipo_base", ""))
                                qtd_sim = numero_seguro(linha_sim.get("quantidade", 0))
                                unidade_sim = texto_seguro(linha_sim.get("unidade", ""))

                                if not categoria_sim or not base_sim:
                                    simulacao_completa = False
                                    continue

                                if categoria_sim != "Bebida":
                                    custo_outro, _ = calcular_custo_referencia(
                                        categoria_sim, base_sim, qtd_sim, unidade_sim
                                    )
                                    if custo_outro is None:
                                        simulacao_completa = False
                                    else:
                                        custo_simulado += custo_outro
                                    continue

                                opcoes_sim = localizar_opcoes_base("Bebida", base_sim).copy()

                                registros_validos = []
                                for idx_opcao, linha_opcao in opcoes_sim.iterrows():
                                    custo_opcao = custo_componente_por_opcao(
                                        "Bebida", linha_opcao, qtd_sim, unidade_sim
                                    )
                                    if custo_opcao is None:
                                        continue

                                    nome_opcao = texto_seguro(linha_opcao.get("nome", "")) or base_sim
                                    embalagem = numero_seguro(linha_opcao.get("quantidade", 0))
                                    preco_opcao = numero_seguro(linha_opcao.get("preco", 0))
                                    registro_id = linha_opcao.get("id", idx_opcao)

                                    rotulo = (
                                        f"{nome_opcao} | {embalagem:g} ml | "
                                        f"R$ {preco_opcao:,.2f} | no drink: R$ {custo_opcao:,.2f}"
                                    )

                                    registros_validos.append({
                                        "id": registro_id,
                                        "nome": nome_opcao,
                                        "embalagem": embalagem,
                                        "preco": preco_opcao,
                                        "custo": custo_opcao,
                                        "rotulo": rotulo,
                                    })

                                registros_validos = sorted(
                                    registros_validos,
                                    key=lambda x: (x["custo"], chave_texto(x["nome"])),
                                )

                                if not registros_validos:
                                    simulacao_completa = False
                                    st.warning(
                                        f"Sem opção de preço válida para **{base_sim}**."
                                    )
                                    continue

                                opcoes_rotulo = [r["rotulo"] for r in registros_validos]
                                escolha_rotulo = st.selectbox(
                                    f"{base_sim} — {qtd_sim:g} {unidade_sim}",
                                    opcoes_rotulo,
                                    index=0,
                                    key=(
                                        f"sim_marca_v9_{chave_texto(drink_nome)}_"
                                        f"{posicao_sim}_{chave_texto(base_sim)}"
                                    ),
                                )
                                escolhido = next(
                                    r for r in registros_validos
                                    if r["rotulo"] == escolha_rotulo
                                )

                                custo_simulado += escolhido["custo"]
                                linhas_simulacao.append({
                                    "Base": base_sim,
                                    "Marca escolhida": escolhido["nome"],
                                    "Embalagem (ml)": escolhido["embalagem"],
                                    "Preço": escolhido["preco"],
                                    "Custo no drink": escolhido["custo"],
                                })

                            s1, s2, s3, s4 = st.columns(4)
                            s1.metric("💚 Mínimo", f"R$ {faixa['min']:,.2f}")
                            s2.metric("🎯 Simulado", f"R$ {custo_simulado:,.2f}")
                            s3.metric("📊 Médio", f"R$ {faixa['medio']:,.2f}")
                            s4.metric("🔺 Máximo", f"R$ {faixa['max']:,.2f}")

                            if faixa["min"] > 0:
                                variacao_sim = custo_simulado - faixa["min"]
                                percentual_sim = (variacao_sim / faixa["min"]) * 100
                                st.caption(
                                    f"Variação da seleção contra o menor custo: "
                                    f"R$ {variacao_sim:,.2f} ({percentual_sim:+.1f}%)."
                                )

                            if linhas_simulacao:
                                st.dataframe(
                                    pd.DataFrame(linhas_simulacao),
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "Preço": st.column_config.NumberColumn(
                                            "Preço", format="R$ %.2f"
                                        ),
                                        "Custo no drink": st.column_config.NumberColumn(
                                            "Custo no drink", format="R$ %.2f"
                                        ),
                                    },
                                )

                            if not simulacao_completa:
                                st.caption(
                                    "⚠️ A simulação está parcial porque algum componente "
                                    "não possui preço/conversão válida."
                                )

            # =====================================================
            # EDITOR DO DRINK SELECIONADO
            # =====================================================
            if st.session_state.get("editar_receita_v7_ativa"):
                st.divider()

                nome_original = st.session_state.get(
                    "editar_receita_v7_nome_original", ""
                )
                itens_edicao = st.session_state.get(
                    "editar_receita_v7_itens", []
                )

                st.subheader(f"✏️ Editando: {nome_original}")
                st.caption(
                    "Você pode corrigir quantidades, trocar a base, remover itens ou "
                    "adicionar componentes que estavam faltando. Para bebidas, a base "
                    "continua sendo somente o TIPO; marca e tamanho ficam para o orçamento."
                )

                tipos_copo_edicao = [
                    "Alto", "Baixo", "Taça", "Coupé", "Martini", "Caneca", "Outro"
                ]

                e1, e2, e3 = st.columns([3, 2, 3])

                with e1:
                    nome_editado = st.text_input(
                        "Nome do drink",
                        key="edit_receita_nome_v6",
                    )

                with e2:
                    tipo_copo_editado = st.selectbox(
                        "Tipo de copo",
                        tipos_copo_edicao,
                        key="edit_receita_tipo_copo_v6",
                    )

                with e3:
                    modelo_copo_editado = st.text_input(
                        "Modelo do copo / taça",
                        key="edit_receita_modelo_copo_v6",
                    )

                st.markdown("### 🧪 Componentes atuais")

                custo_total_edicao = 0.0
                custo_edicao_incompleto = False
                uids_remover = []

                for posicao, item in enumerate(list(itens_edicao)):
                    uid = item.get("uid", f"linha_{posicao}")

                    with st.container(border=True):
                        titulo_item = (
                            item.get("tipo_base")
                            or item.get("ingrediente_original")
                            or f"Componente {posicao + 1}"
                        )
                        st.markdown(f"#### {posicao + 1}. {titulo_item}")

                        categoria_inicial = texto_seguro(item.get("categoria", ""))
                        opcoes_categoria = ["Selecione..."] + CATEGORIAS_RECEITA

                        if categoria_inicial not in CATEGORIAS_RECEITA:
                            categoria_inicial = "Selecione..."

                        key_cat = f"edit_receita_cat_v6_{uid}"
                        if key_cat not in st.session_state:
                            st.session_state[key_cat] = categoria_inicial

                        c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 1])

                        with c1:
                            categoria_item = st.selectbox(
                                "Categoria",
                                opcoes_categoria,
                                key=key_cat,
                            )

                        bases_item = (
                            obter_bases_categoria(categoria_item)
                            if categoria_item in CATEGORIAS_RECEITA
                            else []
                        )

                        key_base = f"edit_receita_base_v7_{uid}"
                        base_inicial = texto_seguro(item.get("tipo_base", ""))

                        if key_base not in st.session_state:
                            if any(
                                chave_texto(base) == chave_texto(base_inicial)
                                for base in bases_item
                            ):
                                base_canonica = next(
                                    base for base in bases_item
                                    if chave_texto(base) == chave_texto(base_inicial)
                                )
                                st.session_state[key_base] = base_canonica
                            elif bases_item:
                                st.session_state[key_base] = bases_item[0]
                            else:
                                st.session_state[key_base] = ""
                        else:
                            atual_base = str(st.session_state.get(key_base, "") or "")
                            if bases_item and not any(
                                chave_texto(base) == chave_texto(atual_base)
                                for base in bases_item
                            ):
                                st.session_state[key_base] = bases_item[0]
                            elif not bases_item:
                                st.session_state[key_base] = ""

                        with c2:
                            if bases_item:
                                base_item = st.selectbox(
                                    "Base / tipo",
                                    bases_item,
                                    key=key_base,
                                )
                            else:
                                base_item = ""
                                st.selectbox(
                                    "Base / tipo",
                                    ["Selecione primeiro a categoria"],
                                    disabled=True,
                                    key=f"edit_receita_base_vazia_v6_{uid}_{categoria_item}",
                                )

                        key_qtd = f"edit_receita_qtd_v6_{uid}"
                        if key_qtd not in st.session_state:
                            st.session_state[key_qtd] = float(
                                numero_seguro(item.get("quantidade", 0))
                            )

                        with c3:
                            quantidade_item = st.number_input(
                                "Quantidade",
                                min_value=0.0,
                                step=1.0,
                                format="%.2f",
                                key=key_qtd,
                            )

                        key_un = f"edit_receita_un_v6_{uid}"
                        unidade_inicial = str(item.get("unidade", "") or "")
                        if unidade_inicial not in UNIDADES_RECEITA:
                            unidade_inicial = (
                                unidade_padrao_categoria(categoria_item)
                                if categoria_item in CATEGORIAS_RECEITA
                                else "un"
                            )

                        if key_un not in st.session_state:
                            st.session_state[key_un] = unidade_inicial

                        with c4:
                            unidade_item = st.selectbox(
                                "Unidade",
                                UNIDADES_RECEITA,
                                key=key_un,
                            )

                        with c5:
                            st.write("")
                            st.write("")
                            if st.button(
                                "🗑️",
                                key=f"edit_receita_remover_v6_{uid}",
                                help="Remover este componente",
                                use_container_width=True,
                            ):
                                uids_remover.append(uid)

                        if categoria_item in CATEGORIAS_RECEITA and base_item:
                            custo_item_ed, info_item_ed = calcular_custo_referencia(
                                categoria_item,
                                base_item,
                                quantidade_item,
                                unidade_item,
                            )

                            if custo_item_ed is None:
                                custo_edicao_incompleto = True
                                if info_item_ed.get("encontrado"):
                                    st.caption(
                                        "ℹ️ Vínculo encontrado, mas esta unidade não possui "
                                        "conversão automática de custo."
                                    )
                                else:
                                    st.caption("⚠️ Base sem preço válido cadastrado.")
                            else:
                                custo_total_edicao += custo_item_ed
                                st.caption(
                                    f"💰 Custo de referência: R$ {custo_item_ed:,.2f} "
                                    f"| {info_item_ed.get('quantidade_opcoes', 0)} opção(ões)"
                                )
                        else:
                            custo_edicao_incompleto = True

                if uids_remover:
                    st.session_state["editar_receita_v7_itens"] = [
                        item for item in itens_edicao
                        if item.get("uid") not in set(uids_remover)
                    ]

                    for uid in uids_remover:
                        for prefixo in [
                            "edit_receita_cat_v6_",
                            "edit_receita_base_v7_",
                            "edit_receita_qtd_v6_",
                            "edit_receita_un_v6_",
                        ]:
                            chave = prefixo + str(uid)
                            if chave in st.session_state:
                                del st.session_state[chave]

                    st.rerun()

                st.metric(
                    "💰 Custo unitário estimado após edição",
                    f"R$ {custo_total_edicao:,.2f}",
                )

                if custo_edicao_incompleto:
                    st.caption(
                        "⚠️ A estimativa pode estar parcial enquanto houver item sem "
                        "base válida ou unidade sem conversão automática."
                    )

                # -----------------------------------------------------
                # ADICIONAR COMPONENTE DURANTE A EDIÇÃO
                # -----------------------------------------------------
                st.markdown("### ➕ Adicionar componente")

                n1, n2, n3, n4, n5 = st.columns([2, 3, 2, 2, 1])

                with n1:
                    nova_cat_ed = st.selectbox(
                        "Categoria",
                        CATEGORIAS_RECEITA,
                        key="edit_receita_nova_cat_v6",
                    )

                novas_bases_ed = obter_bases_categoria(nova_cat_ed)

                with n2:
                    if novas_bases_ed:
                        nova_base_ed = st.selectbox(
                            "Base / tipo",
                            novas_bases_ed,
                            key=(
                                "edit_receita_nova_base_v6_"
                                + chave_texto(nova_cat_ed).replace(" ", "_").replace("/", "_")
                            ),
                        )
                    else:
                        nova_base_ed = ""
                        st.selectbox(
                            "Base / tipo",
                            ["Nenhum cadastro disponível"],
                            disabled=True,
                            key=f"edit_receita_nova_base_vazia_v6_{nova_cat_ed}",
                        )

                with n3:
                    nova_qtd_ed = st.number_input(
                        "Quantidade",
                        min_value=0.0,
                        step=1.0,
                        format="%.2f",
                        key="edit_receita_nova_qtd_v6",
                    )

                with n4:
                    unidade_padrao_ed = unidade_padrao_categoria(nova_cat_ed)
                    key_nova_un = (
                        "edit_receita_nova_un_v6_"
                        + chave_texto(nova_cat_ed).replace(" ", "_").replace("/", "_")
                    )
                    nova_un_ed = st.selectbox(
                        "Unidade",
                        UNIDADES_RECEITA,
                        index=(
                            UNIDADES_RECEITA.index(unidade_padrao_ed)
                            if unidade_padrao_ed in UNIDADES_RECEITA else 0
                        ),
                        key=key_nova_un,
                    )

                with n5:
                    st.write("")
                    st.write("")
                    adicionar_ed = st.button(
                        "➕",
                        key="edit_receita_adicionar_v6",
                        help="Adicionar componente",
                        use_container_width=True,
                    )

                if adicionar_ed:
                    if not nova_base_ed:
                        st.warning("Selecione uma base para o novo componente.")
                    elif nova_qtd_ed <= 0:
                        st.warning("Informe uma quantidade maior que zero.")
                    else:
                        duplicado = False

                        for item in st.session_state.get("editar_receita_v7_itens", []):
                            uid_item = item.get("uid")
                            cat_atual = st.session_state.get(
                                f"edit_receita_cat_v6_{uid_item}",
                                item.get("categoria", ""),
                            )
                            base_atual = st.session_state.get(
                                f"edit_receita_base_v7_{uid_item}",
                                item.get("tipo_base", ""),
                            )
                            un_atual = st.session_state.get(
                                f"edit_receita_un_v6_{uid_item}",
                                item.get("unidade", ""),
                            )

                            if (
                                chave_texto(cat_atual) == chave_texto(nova_cat_ed)
                                and chave_texto(base_atual) == chave_texto(nova_base_ed)
                                and str(un_atual) == str(nova_un_ed)
                            ):
                                duplicado = True
                                break

                        if duplicado:
                            st.warning(
                                "Esse componente já existe na receita. Ajuste a quantidade "
                                "na linha existente em vez de duplicá-lo."
                            )
                        else:
                            contador = int(
                                st.session_state.get("editar_receita_v7_contador", 0)
                            ) + 1
                            st.session_state["editar_receita_v7_contador"] = contador

                            novo_uid = f"novo_{contador}"
                            st.session_state["editar_receita_v7_itens"].append({
                                "id": None,
                                "uid": novo_uid,
                                "ingrediente_original": nova_base_ed,
                                "categoria": nova_cat_ed,
                                "tipo_base": nova_base_ed,
                                "quantidade": float(nova_qtd_ed),
                                "unidade": nova_un_ed,
                            })

                            st.rerun()

                st.divider()
                salvar_col, cancelar_col = st.columns(2)

                with salvar_col:
                    salvar_edicao = st.button(
                        "💾 Salvar alterações da receita",
                        use_container_width=True,
                        key="edit_receita_salvar_v6",
                    )

                with cancelar_col:
                    cancelar_edicao = st.button(
                        "❌ Cancelar edição",
                        use_container_width=True,
                        key="edit_receita_cancelar_v6",
                    )

                if cancelar_edicao:
                    limpar_edicao_receita()
                    st.rerun()

                if salvar_edicao:
                    nome_final = str(nome_editado or "").strip()
                    modelo_final = str(modelo_copo_editado or "").strip()

                    linhas_salvar = []
                    problemas = []

                    for posicao, item in enumerate(
                        st.session_state.get("editar_receita_v7_itens", [])
                    ):
                        uid = item.get("uid", f"linha_{posicao}")
                        categoria_final = st.session_state.get(
                            f"edit_receita_cat_v6_{uid}", item.get("categoria", "")
                        )
                        base_final = st.session_state.get(
                            f"edit_receita_base_v7_{uid}", item.get("tipo_base", "")
                        )
                        qtd_final = numero_seguro(
                            st.session_state.get(
                                f"edit_receita_qtd_v6_{uid}", item.get("quantidade", 0)
                            )
                        )
                        unidade_final = st.session_state.get(
                            f"edit_receita_un_v6_{uid}", item.get("unidade", "")
                        )

                        if categoria_final not in CATEGORIAS_RECEITA:
                            problemas.append(f"Componente {posicao + 1}: selecione a categoria.")
                            continue

                        bases_validas = obter_bases_categoria(categoria_final)
                        base_canonica = next(
                            (
                                base for base in bases_validas
                                if chave_texto(base) == chave_texto(base_final)
                            ),
                            None,
                        )

                        if not base_canonica:
                            problemas.append(
                                f"Componente {posicao + 1}: selecione uma base válida."
                            )
                            continue

                        if qtd_final <= 0:
                            problemas.append(
                                f"Componente {posicao + 1}: quantidade deve ser maior que zero."
                            )
                            continue

                        if unidade_final not in UNIDADES_RECEITA:
                            problemas.append(
                                f"Componente {posicao + 1}: unidade inválida."
                            )
                            continue

                        linhas_salvar.append({
                            "id": item.get("id"),
                            "categoria": categoria_final,
                            "tipo_base": base_canonica,
                            "quantidade": float(qtd_final),
                            "unidade": unidade_final,
                        })

                    if not nome_final:
                        st.error("Informe o nome do drink.")
                    elif not modelo_final:
                        st.error("Informe o modelo do copo / taça.")
                    elif not linhas_salvar:
                        st.error("A receita precisa ter pelo menos um componente.")
                    elif problemas:
                        for problema in problemas:
                            st.error(problema)
                    else:
                        # Evita sobrescrever outro drink ao renomear.
                        conflito_nome = False

                        for outro_nome in df_receitas[COLUNA_DRINK].dropna().astype(str).unique():
                            if (
                                chave_texto(outro_nome) == chave_texto(nome_final)
                                and chave_texto(outro_nome) != chave_texto(nome_original)
                            ):
                                conflito_nome = True
                                break

                        if conflito_nome:
                            st.error(
                                "Já existe outro drink com esse nome. Use um nome diferente."
                            )
                        else:
                            try:
                                ids_originais = set(
                                    int(x) for x in st.session_state.get(
                                        "editar_receita_v7_ids_originais", []
                                    )
                                )
                                ids_mantidos = set()

                                # Atualiza as linhas existentes e insere as novas.
                                for linha_salvar in linhas_salvar:
                                    dados_update = {
                                        COLUNA_DRINK: nome_final,
                                        "ingrediente": linha_salvar["tipo_base"],
                                        "categoria": linha_salvar["categoria"],
                                        "tipo_base": linha_salvar["tipo_base"],
                                        "quantidade": linha_salvar["quantidade"],
                                        "unidade": linha_salvar["unidade"],
                                        "tipo_copo": tipo_copo_editado,
                                        "modelo_copo": modelo_final,
                                    }

                                    item_id = linha_salvar.get("id")

                                    if item_id is not None and not pd.isna(item_id):
                                        item_id = int(item_id)
                                        ids_mantidos.add(item_id)
                                        supabase.table("receitas").update(
                                            dados_update
                                        ).eq("id", item_id).execute()
                                    else:
                                        supabase.table("receitas").insert(
                                            dados_update
                                        ).execute()

                                # Só remove linhas antigas depois que atualizações/inserts deram certo.
                                ids_removidos = ids_originais - ids_mantidos
                                for item_id in ids_removidos:
                                    supabase.table("receitas").delete().eq(
                                        "id", int(item_id)
                                    ).execute()

                                st.success("✅ Receita atualizada com sucesso!")
                                limpar_edicao_receita()
                                st.rerun()

                            except Exception as e:
                                st.error(f"Erro ao atualizar a receita: {e}")

    # =========================================================
    # ABA 3 — REVISÃO / PENTE-FINO
    # =========================================================
    with aba_revisao:
        st.subheader("🔎 Revisão das Receitas")
        st.caption(
            "Correspondências EXATAS e ÚNICAS entre o ingrediente da receita "
            "e um TIPO cadastrado são validadas automaticamente. Só ficam "
            "pendentes os casos ambíguos ou sem correspondência exata."
        )

        if df_receitas.empty:
            st.info("Nenhuma receita cadastrada.")
        elif colunas_faltantes:
            st.error("Execute primeiro o SQL de migração para habilitar a revisão.")
        elif "id" not in df_receitas.columns:
            st.error(
                "A tabela `receitas` precisa possuir uma coluna `id` "
                "para validar e salvar a revisão linha a linha."
            )
        else:

            # ---------------------------------------------------------
            # CORRESPONDÊNCIA ESTRITA PARA AUTO-VALIDAÇÃO
            # ---------------------------------------------------------
            # IMPORTANTE:
            # - Primeiro tenta Ingrediente x TIPO de forma exata.
            # - Se não houver TIPO exato, um NOME exato e único pode servir
            #   apenas para descobrir a BASE/TIPO canônico (ex.: Aperol -> Aperitivo).
            # - A receita continua vinculada ao TIPO, nunca à marca/tamanho.
            # - Maiúsculas, minúsculas, acentos e espaços são normalizados.
            # - Se houver mais de uma possibilidade segura, fica ambíguo.
            # ---------------------------------------------------------
            def correspondencia_exata_unica_tipo(ingrediente):
                chave = chave_texto(ingrediente)

                if not chave:
                    return {
                        "status": "nao_encontrado",
                        "categoria": None,
                        "tipo_base": None,
                        "candidatos": [],
                    }

                candidatos = []

                def adicionar_tipos_exatos(df_base, categoria):
                    if df_base is None or df_base.empty or "tipo" not in df_base.columns:
                        return

                    tipos_canonicos = {}

                    for valor in df_base["tipo"].dropna().astype(str):
                        tipo = valor.strip()
                        if not tipo:
                            continue

                        chave_tipo = chave_texto(tipo)
                        if chave_tipo == chave and chave_tipo not in tipos_canonicos:
                            tipos_canonicos[chave_tipo] = tipo

                    for tipo in tipos_canonicos.values():
                        candidatos.append((categoria, tipo))

                adicionar_tipos_exatos(df_bebidas, "Bebida")
                adicionar_tipos_exatos(df_insumos, "Fruta / Insumo")
                adicionar_tipos_exatos(df_artesanais, "Artesanal")

                # Se a base de insumos tiver um tipo exatamente "Gelo",
                # tratamos como a categoria operacional Gelo, não como insumo genérico.
                candidatos_ajustados = []
                for categoria, tipo in candidatos:
                    if categoria == "Fruta / Insumo" and chave_texto(tipo) == "gelo":
                        candidatos_ajustados.append(("Gelo", tipo))
                    else:
                        candidatos_ajustados.append((categoria, tipo))

                unicos = []
                vistos = set()

                for categoria, tipo in candidatos_ajustados:
                    k = (chave_texto(categoria), chave_texto(tipo))
                    if k not in vistos:
                        vistos.add(k)
                        unicos.append((categoria, tipo))

                if len(unicos) == 1:
                    return {
                        "status": "exato_unico",
                        "categoria": unicos[0][0],
                        "tipo_base": unicos[0][1],
                        "candidatos": unicos,
                    }

                if len(unicos) > 1:
                    return {
                        "status": "ambiguo",
                        "categoria": None,
                        "tipo_base": None,
                        "candidatos": unicos,
                    }

                # -------------------------------------------------
                # SEGUNDA REGRA SEGURA:
                # Se não houve TIPO exato, aceita um NOME exato e
                # único apenas para descobrir sua BASE/TIPO canônico.
                # Ex.: ingrediente antigo "Aperol" -> cadastro
                # nome="Aperol", tipo="Aperitivo" -> receita passa
                # a ficar vinculada a "Aperitivo", nunca à marca.
                # -------------------------------------------------
                sugestao_nome = sugerir_vinculo_antigo(ingrediente)

                if sugestao_nome.get("status") == "sugerido":
                    return {
                        "status": "exato_unico",
                        "categoria": sugestao_nome.get("categoria"),
                        "tipo_base": sugestao_nome.get("tipo_base"),
                        "candidatos": [
                            (
                                sugestao_nome.get("categoria"),
                                sugestao_nome.get("tipo_base"),
                            )
                        ],
                    }

                if sugestao_nome.get("status") == "ambiguo":
                    return {
                        "status": "ambiguo",
                        "categoria": None,
                        "tipo_base": None,
                        "candidatos": sugestao_nome.get("candidatos", []),
                    }

                return {
                    "status": "nao_encontrado",
                    "categoria": None,
                    "tipo_base": None,
                    "candidatos": [],
                }

            # ---------------------------------------------------------
            # AUTO-VALIDAÇÃO DAS RECEITAS ANTIGAS
            # ---------------------------------------------------------
            auto_validados = 0

            for indice, linha in df_receitas.iterrows():
                categoria_atual = texto_seguro(linha.get("categoria", ""))
                tipo_base_atual = texto_seguro(linha.get("tipo_base", ""))

                # Já revisado: não altera automaticamente.
                if categoria_atual and tipo_base_atual:
                    continue

                ingrediente = str(linha.get("ingrediente", "") or "").strip()
                resultado_auto = correspondencia_exata_unica_tipo(ingrediente)

                if resultado_auto["status"] != "exato_unico":
                    continue

                try:
                    item_id = int(linha.get("id"))
                    categoria_auto = resultado_auto["categoria"]
                    tipo_auto = resultado_auto["tipo_base"]

                    supabase.table("receitas").update({
                        # Padroniza o ingrediente para a base/tipo canônico.
                        # Para bebidas, continua sendo TIPO — nunca marca.
                        "ingrediente": tipo_auto,
                        "categoria": categoria_auto,
                        "tipo_base": tipo_auto,
                    }).eq("id", item_id).execute()

                    # Atualiza também o DataFrame local para refletir a mudança
                    # imediatamente nesta mesma execução.
                    df_receitas.at[indice, "ingrediente"] = tipo_auto
                    df_receitas.at[indice, "categoria"] = categoria_auto
                    df_receitas.at[indice, "tipo_base"] = tipo_auto
                    auto_validados += 1

                except Exception as e:
                    st.error(
                        f"Erro ao validar automaticamente o ingrediente "
                        f"'{ingrediente}': {e}"
                    )

            if auto_validados > 0:
                st.success(
                    f"✅ {auto_validados} componente(s) com correspondência exata "
                    "e única foram validados automaticamente."
                )

            # ---------------------------------------------------------
            # CLASSIFICA PENDÊNCIAS RESTANTES
            # ---------------------------------------------------------
            pendencias = []
            total_componentes = len(df_receitas)
            total_validados = 0
            total_ambiguos = 0
            total_sem_correspondencia = 0

            for _, linha in df_receitas.iterrows():
                categoria = texto_seguro(linha.get("categoria", ""))
                tipo_base = texto_seguro(linha.get("tipo_base", ""))

                if categoria and tipo_base:
                    total_validados += 1
                    continue

                ingrediente = str(linha.get("ingrediente", "") or "").strip()
                resultado = correspondencia_exata_unica_tipo(ingrediente)

                if resultado["status"] == "ambiguo":
                    total_ambiguos += 1
                    motivo = "Ambíguo"
                else:
                    total_sem_correspondencia += 1
                    motivo = "Sem correspondência exata"

                pendencias.append({
                    "id": linha.get("id"),
                    "drink": str(linha.get(COLUNA_DRINK, "") or "").strip(),
                    "ingrediente": ingrediente,
                    "motivo": motivo,
                    "candidatos": resultado.get("candidatos", []),
                })

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Componentes", total_componentes)
            c2.metric("✅ Validados", total_validados)
            c3.metric("⚠️ Ambíguos", total_ambiguos)
            c4.metric("❌ Sem correspondência", total_sem_correspondencia)

            st.divider()

            if not pendencias:
                st.success(
                    "✅ Todas as receitas estão padronizadas. Não há pendências de revisão."
                )
            else:
                drinks_pendentes = sorted(
                    list({p["drink"] for p in pendencias if p["drink"]}),
                    key=lambda x: chave_texto(x),
                )

                st.markdown("### ⚠️ Pendências que precisam de decisão manual")
                st.caption(
                    "Somente casos ambíguos ou sem correspondência exata aparecem aqui."
                )

                drink_revisao = st.selectbox(
                    "Escolha o drink pendente",
                    drinks_pendentes,
                    key="drink_revisao_v5",
                )

                receita_rev = df_receitas[
                    df_receitas[COLUNA_DRINK].astype(str) == str(drink_revisao)
                ].copy()

                revisoes_manuais = []

                for posicao, (_, linha) in enumerate(receita_rev.iterrows()):
                    item_id = linha.get("id")
                    ingrediente_atual = texto_seguro(
                        linha.get("ingrediente", "")
                    )
                    categoria_atual = texto_seguro(
                        linha.get("categoria", "")
                    )
                    tipo_base_atual = texto_seguro(
                        linha.get("tipo_base", "")
                    )
                    quantidade_atual = numero_seguro(
                        linha.get("quantidade", 0)
                    )
                    unidade_atual = str(
                        linha.get("unidade", "") or ""
                    ).strip()

                    # Componentes já validados aparecem apenas como confirmação
                    # e não exigem nova revisão manual.
                    if categoria_atual and tipo_base_atual:
                        with st.container(border=True):
                            st.markdown(f"#### ✅ {ingrediente_atual}")
                            st.caption(
                                f"{categoria_atual} → {tipo_base_atual} | "
                                f"{quantidade_atual:g} {unidade_atual}"
                            )

                            custo_ok, _ = calcular_custo_referencia(
                                categoria_atual,
                                tipo_base_atual,
                                quantidade_atual,
                                unidade_atual,
                            )

                            if custo_ok is not None:
                                st.success(
                                    f"Custo médio de referência: R$ {custo_ok:,.4f}"
                                )
                        continue

                    resultado_estrito = correspondencia_exata_unica_tipo(
                        ingrediente_atual
                    )
                    sugestao = sugerir_vinculo_antigo(ingrediente_atual)

                    if categoria_atual in CATEGORIAS_RECEITA:
                        categoria_padrao = categoria_atual
                    elif sugestao["status"] == "sugerido":
                        categoria_padrao = sugestao["categoria"]
                    else:
                        categoria_padrao = CATEGORIAS_RECEITA[0]

                    with st.container(border=True):
                        st.markdown(
                            f"#### ⚠️ {ingrediente_atual or 'Ingrediente sem nome'}"
                        )

                        if resultado_estrito["status"] == "ambiguo":
                            candidatos_txt = ", ".join(
                                f"{cat} → {base}"
                                for cat, base in resultado_estrito.get("candidatos", [])
                            )
                            st.warning(
                                "Há mais de uma correspondência EXATA de tipo. "
                                f"Escolha manualmente. Candidatos: {candidatos_txt}"
                            )
                        else:
                            st.warning(
                                "Não há correspondência EXATA e única com um tipo cadastrado. "
                                "Escolha a categoria e a base manualmente."
                            )

                        col_a, col_b = st.columns(2)

                        with col_a:
                            categoria_escolhida = st.selectbox(
                                "Categoria",
                                CATEGORIAS_RECEITA,
                                index=CATEGORIAS_RECEITA.index(categoria_padrao),
                                key=f"rev_cat_v5_{drink_revisao}_{item_id}_{posicao}",
                            )

                        bases_rev = obter_bases_categoria(categoria_escolhida)
                        base_sugerida = tipo_base_atual

                        # A sugestão antiga serve SOMENTE de ajuda visual/manual.
                        # Ela nunca é gravada automaticamente nesta etapa.
                        if (
                            not base_sugerida
                            and sugestao["status"] == "sugerido"
                            and sugestao["categoria"] == categoria_escolhida
                        ):
                            base_sugerida = sugestao["tipo_base"]

                        if categoria_escolhida == "Bebida":
                            # Para bebida, base sempre vem de precos_bebidas.tipo.
                            if not any(
                                chave_texto(base) == chave_texto(base_sugerida)
                                for base in bases_rev
                            ):
                                base_sugerida = ""
                        elif base_sugerida and not any(
                            chave_texto(base) == chave_texto(base_sugerida)
                            for base in bases_rev
                        ):
                            bases_rev = [base_sugerida] + bases_rev

                        with col_b:
                            if bases_rev:
                                indice_base = 0
                                for i, base in enumerate(bases_rev):
                                    if chave_texto(base) == chave_texto(base_sugerida):
                                        indice_base = i
                                        break

                                base_escolhida = st.selectbox(
                                    "Base do ingrediente",
                                    bases_rev,
                                    index=indice_base,
                                    key=(
                                        f"rev_base_v5_{drink_revisao}_{item_id}_{posicao}_"
                                        + chave_texto(categoria_escolhida)
                                        .replace(" ", "_")
                                        .replace("/", "_")
                                    ),
                                )
                            else:
                                base_escolhida = ""
                                st.selectbox(
                                    "Base do ingrediente",
                                    ["Nenhum cadastro disponível"],
                                    disabled=True,
                                    key=f"rev_base_vazia_v5_{drink_revisao}_{item_id}_{posicao}",
                                )

                        col_q, col_u = st.columns(2)

                        with col_q:
                            quantidade_escolhida = st.number_input(
                                "Quantidade por drink",
                                min_value=0.0,
                                value=float(quantidade_atual),
                                step=1.0,
                                format="%.2f",
                                key=f"rev_qtd_v5_{drink_revisao}_{item_id}_{posicao}",
                            )

                        with col_u:
                            unidade_inicial = (
                                unidade_atual
                                if unidade_atual in UNIDADES_RECEITA
                                else unidade_padrao_categoria(categoria_escolhida)
                            )
                            unidade_escolhida = st.selectbox(
                                "Unidade",
                                UNIDADES_RECEITA,
                                index=UNIDADES_RECEITA.index(unidade_inicial),
                                key=f"rev_un_v5_{drink_revisao}_{item_id}_{posicao}",
                            )

                        custo_rev = None
                        custo_info_rev = None

                        if base_escolhida:
                            custo_rev, custo_info_rev = calcular_custo_referencia(
                                categoria_escolhida,
                                base_escolhida,
                                quantidade_escolhida,
                                unidade_escolhida,
                            )

                        if custo_rev is not None:
                            st.success(
                                f"✅ Vínculo escolhido | custo mínimo por drink: "
                                f"R$ {custo_rev:,.2f}"
                            )
                        elif (
                            base_escolhida
                            and custo_info_rev
                            and custo_info_rev["encontrado"]
                        ):
                            st.info(
                                "ℹ️ Vínculo encontrado, mas a unidade da receita "
                                "não possui conversão automática de custo. "
                                f"Base de preço: {custo_info_rev['unidade_base']}."
                            )
                        elif base_escolhida:
                            st.error(
                                "❌ A base escolhida não possui preço válido cadastrado."
                            )

                        revisoes_manuais.append({
                            "id": item_id,
                            "ingrediente": base_escolhida,
                            "categoria": categoria_escolhida,
                            "tipo_base": base_escolhida,
                            "quantidade": float(quantidade_escolhida),
                            "unidade": unidade_escolhida,
                        })

                if revisoes_manuais:
                    st.divider()

                    if st.button(
                        "💾 Salvar somente as pendências deste drink",
                        use_container_width=True,
                        key="salvar_revisao_receita_v5",
                    ):
                        problemas = [
                            r for r in revisoes_manuais
                            if not str(r["tipo_base"]).strip() or r["quantidade"] <= 0
                        ]

                        if problemas:
                            st.error(
                                "Existem componentes pendentes sem base definida "
                                "ou com quantidade inválida."
                            )
                        else:
                            try:
                                for revisao in revisoes_manuais:
                                    supabase.table("receitas").update({
                                        "ingrediente": revisao["tipo_base"],
                                        "categoria": revisao["categoria"],
                                        "tipo_base": revisao["tipo_base"],
                                        "quantidade": revisao["quantidade"],
                                        "unidade": revisao["unidade"],
                                    }).eq("id", int(revisao["id"])).execute()

                                st.success("✅ Pendências do drink salvas e padronizadas!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar revisão: {e}")

            st.divider()
            st.markdown("### 📊 Status geral das receitas")

            status_receitas = []
            drinks_status = sorted(
                df_receitas[COLUNA_DRINK]
                .dropna()
                .astype(str)
                .unique(),
                key=lambda x: chave_texto(x),
            )

            for nome_drink in drinks_status:
                rec = df_receitas[
                    df_receitas[COLUNA_DRINK].astype(str) == str(nome_drink)
                ]

                total_itens = len(rec)
                revisados = 0
                ambiguos = 0
                sem_correspondencia = 0
                custo_calculavel = 0

                for _, linha in rec.iterrows():
                    categoria = texto_seguro(linha.get("categoria", ""))
                    base = texto_seguro(linha.get("tipo_base", ""))
                    quantidade = numero_seguro(linha.get("quantidade", 0))
                    unidade = str(linha.get("unidade", "") or "").strip()

                    if categoria and base:
                        revisados += 1
                        custo, _ = calcular_custo_referencia(
                            categoria,
                            base,
                            quantidade,
                            unidade,
                        )
                        if custo is not None:
                            custo_calculavel += 1
                    else:
                        resultado = correspondencia_exata_unica_tipo(
                            linha.get("ingrediente", "")
                        )
                        if resultado["status"] == "ambiguo":
                            ambiguos += 1
                        else:
                            sem_correspondencia += 1

                if total_itens > 0 and revisados == total_itens:
                    status = "✅ Validada"
                elif ambiguos > 0:
                    status = "⚠️ Ambígua"
                else:
                    status = "❌ Pendente"

                status_receitas.append({
                    "Drink": nome_drink,
                    "Componentes": total_itens,
                    "Validados": revisados,
                    "Ambíguos": ambiguos,
                    "Sem correspondência": sem_correspondencia,
                    "Com custo": custo_calculavel,
                    "Status": status,
                })

            st.dataframe(
                pd.DataFrame(status_receitas),
                use_container_width=True,
                hide_index=True,
            )

                

    
    import math
    import re
    import io
    import unicodedata
    from difflib import SequenceMatcher

    # =========================================================
    # IDENTIDADE VISUAL / SEÇÕES DO ORÇAMENTO
    # =========================================================

    def _secao_orcamento(numero, titulo, descricao="", icone=""):
        """Cabeçalho visual de ponta a ponta para separar as etapas."""
        subtitulo = (
            f'<div style="margin-top:4px;color:#AAB2BF;font-size:0.92rem;">{descricao}</div>'
            if descricao else ""
        )
        st.markdown(
            f"""
            <div style="
                margin: 30px 0 18px 0;
                padding: 15px 18px;
                border: 1px solid rgba(255,255,255,0.14);
                border-left: 6px solid #FF4B4B;
                border-radius: 10px;
                background: linear-gradient(90deg, rgba(255,75,75,0.13), rgba(255,255,255,0.025));
            ">
                <div style="font-size:1.35rem;font-weight:750;line-height:1.25;">
                    {numero} {icone} {titulo}
                </div>
                {subtitulo}
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _subsecao_orcamento(titulo, descricao=""):
        subtitulo = (
            f'<div style="margin-top:3px;color:#9199A6;font-size:0.84rem;">{descricao}</div>'
            if descricao else ""
        )
        st.markdown(
            f"""
            <div style="
                margin: 18px 0 12px 0;
                padding: 10px 14px;
                border-radius: 8px;
                background: rgba(255,255,255,0.055);
                border: 1px solid rgba(255,255,255,0.09);
            ">
                <div style="font-size:1.03rem;font-weight:700;">{titulo}</div>
                {subtitulo}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================
    # FUNÇÕES AUXILIARES DO ORÇAMENTO
    # =========================================================

    def _norm_orcamento(valor):
        texto = normalizar_nome(valor)
        texto = unicodedata.normalize("NFKD", str(texto))
        texto = "".join(c for c in texto if not unicodedata.combining(c))
        texto = re.sub(r"[^a-zA-Z0-9]+", " ", texto.lower())
        return " ".join(texto.strip().split())

    def _safe_key(valor):
        texto = _norm_orcamento(valor)
        return "".join(c if c.isalnum() else "_" for c in texto)

    def _preparar_base_orcamento(df):
        df = df.copy()
        if "nome" not in df.columns:
            df["nome"] = ""
        if "tipo" not in df.columns:
            df["tipo"] = ""
        if "quantidade" not in df.columns:
            df["quantidade"] = 0.0
        if "preco" not in df.columns:
            df["preco"] = 0.0

        df["_nome_norm"] = df["nome"].fillna("").astype(str).apply(_norm_orcamento)
        df["_tipo_norm"] = df["tipo"].fillna("").astype(str).apply(_norm_orcamento)
        df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0.0)
        df["preco"] = pd.to_numeric(df["preco"], errors="coerce").fillna(0.0)
        return df

    def _limpar_estado_calculo_orcamento():
        prefixos = (
            "orc_qtd_",
            "orc_marca_",
            "orc_insumo_",
            "orc_art_",
            "orc_prod_",
            "orc_peso_",
        )
        for chave in list(st.session_state.keys()):
            if chave.startswith(prefixos):
                del st.session_state[chave]

    def _eh_fruta_por_tipo(linha):
        # A classificação vem do cadastro do próprio item.
        # Não existe lista fixa de frutas/produtos no código.
        tipo = _norm_orcamento(linha.get("tipo", ""))
        return "fruta" in tipo

    def _similaridade_texto(a, b):
        a = _norm_orcamento(a)
        b = _norm_orcamento(b)

        if not a or not b:
            return 0.0

        if a == b:
            return 1.0

        score = SequenceMatcher(None, a, b).ratio()

        # Contenção ajuda quando o nome da receita e o nome do cadastro
        # representam o mesmo item com descrições diferentes.
        if len(a) >= 4 and len(b) >= 4 and (a in b or b in a):
            score = max(score, 0.93)

        tokens_a = set(a.split())
        tokens_b = set(b.split())

        if tokens_a and tokens_b:
            inter = len(tokens_a & tokens_b)
            uniao = len(tokens_a | tokens_b)
            jaccard = inter / uniao if uniao else 0.0
            score = max(score, jaccard)

        return score

    def _rotulo_produto(linha, indice):
        nome = str(linha.get("nome", "") or "").strip()
        tipo = str(linha.get("tipo", "") or "").strip()
        qtd = float(linha.get("quantidade", 0) or 0)
        preco = float(linha.get("preco", 0) or 0)
        item_id = linha.get("id", indice)

        partes = [nome or "Sem nome"]
        if tipo:
            partes.append(f"Tipo: {tipo}")
        if qtd > 0:
            partes.append(f"Qtd. base: {qtd:g}")
        partes.append(f"R$ {preco:,.2f}")
        partes.append(f"ID {item_id}")
        return " | ".join(partes)

    def _selecionar_linha_produto(opcoes, titulo, key):
        opcoes = opcoes.copy().reset_index(drop=True)

        if opcoes.empty:
            return None

        if len(opcoes) == 1:
            st.caption(titulo)
            st.markdown(f"**{_rotulo_produto(opcoes.iloc[0], 0)}**")
            return opcoes.iloc[0]

        indices = list(range(len(opcoes)))
        rotulos = {
            i: _rotulo_produto(opcoes.iloc[i], i)
            for i in indices
        }

        indice_escolhido = st.selectbox(
            titulo,
            indices,
            format_func=lambda i: rotulos[i],
            key=key,
        )

        return opcoes.iloc[int(indice_escolhido)]

    def _consolidar_itens(lista_itens):
        """Consolida itens iguais preservando o snapshot operacional."""
        consolidados = {}

        for item in lista_itens:
            categoria = str(item.get("categoria", "") or "").strip()
            produto = str(item.get("produto", "") or "").strip()
            unidade = str(item.get("unidade", "") or "").strip()

            if not produto:
                continue

            chave = (
                categoria.lower(),
                _norm_orcamento(produto),
                unidade.lower(),
                str(item.get("produto_ref_id", "") or ""),
            )

            if chave not in consolidados:
                consolidados[chave] = {
                    "categoria": categoria,
                    "produto": produto,
                    "quantidade": 0.0,
                    "unidade": unidade,
                    "custo_estimado": 0.0,
                    "tipo_base": str(item.get("tipo_base", "") or ""),
                    "produto_ref_id": item.get("produto_ref_id"),
                    "quantidade_base": float(item.get("quantidade_base", 0) or 0),
                    "preco_unitario": float(item.get("preco_unitario", 0) or 0),
                    "custo_unitario_operacional": float(
                        item.get("custo_unitario_operacional", 0) or 0
                    ),
                }

            consolidados[chave]["quantidade"] += float(
                item.get("quantidade", 0) or 0
            )
            consolidados[chave]["custo_estimado"] += float(
                item.get("custo_estimado", 0) or 0
            )

        return list(consolidados.values())

    def _fmt_qtd_pdf(valor):
        try:
            valor = float(valor or 0)
        except Exception:
            return ""
        if abs(valor - round(valor)) < 1e-9:
            return str(int(round(valor)))
        return f"{valor:.3f}".rstrip("0").rstrip(".")

    def _gerar_pdf_checklist_operacional(evento, itens):
        """
        PDF operacional inspirado no checklist físico do usuário.
        Não exibe custos, margem, lucro ou consumo gerencial.
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER
            from reportlab.lib.units import mm
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                PageBreak, KeepTogether,
            )
        except Exception:
            return None, (
                "PDF indisponível: falta a biblioteca reportlab. "
                "No terminal do projeto execute: python -m pip install reportlab "
                "e depois reinicie o Streamlit."
            )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=10 * mm,
            leftMargin=10 * mm,
            topMargin=10 * mm,
            bottomMargin=10 * mm,
        )

        styles = getSampleStyleSheet()
        titulo = ParagraphStyle(
            "titulo_check_v10",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=16,
            leading=19,
            spaceAfter=6,
        )
        subtitulo = ParagraphStyle(
            "sub_check_v10",
            parent=styles["Heading2"],
            fontSize=10,
            leading=12,
            spaceBefore=5,
            spaceAfter=4,
        )
        normal = ParagraphStyle(
            "normal_check_v10",
            parent=styles["BodyText"],
            fontSize=8.5,
            leading=10,
        )
        pequeno = ParagraphStyle(
            "peq_check_v10",
            parent=styles["BodyText"],
            fontSize=7.5,
            leading=9,
        )

        story = []
        story.append(Paragraph("CHECKLIST DE LOGÍSTICA E REVISÃO DE EVENTO", titulo))

        info = [
            ["Cliente", str(evento.get("cliente", "") or ""),
             "Data", str(evento.get("data", "") or ""),
             "Evento", str(evento.get("tipo_evento", "") or "")],
            ["Cidade", str(evento.get("cidade", "") or ""),
             "Local", str(evento.get("endereco", "") or ""),
             "Convidados", str(evento.get("convidados", "") or "")],
            ["Chegada equipe", str(evento.get("hora_chegada", "") or ""),
             "Início serviço", str(evento.get("hora_inicio", "") or ""),
             "Evento #", str(evento.get("id", "") or "")],
        ]
        t_info = Table(info, colWidths=[25*mm, 55*mm, 25*mm, 45*mm, 25*mm, 45*mm])
        t_info.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F3F4F6")),
            ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#B8BEC8")),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
            ("FONTNAME", (4,0), (4,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 5*mm))

        drinks_txt = str(evento.get("drinks", "") or "").strip()
        if drinks_txt:
            lista = [d.strip() for d in drinks_txt.split("\n") if d.strip()]
            story.append(Paragraph("Carta de Drinks", subtitulo))
            story.append(Paragraph(" • ".join(lista), normal))
            story.append(Spacer(1, 4*mm))

        if isinstance(itens, pd.DataFrame):
            dados_itens = itens.to_dict("records")
        else:
            dados_itens = list(itens or [])

        # Somente itens físicos/operacionais entram no mapa de carga.
        ignorar = {"equipe", "custos"}
        dados_itens = [
            x for x in dados_itens
            if str(x.get("categoria", "") or "").strip().lower() not in ignorar
            and float(x.get("quantidade", 0) or 0) > 0
        ]

        ordem = {
            "Bebidas": 1,
            "Frutas": 2,
            "Insumos": 3,
            "Artesanais": 4,
            "Gelo": 5,
            "Kit Bar": 6,
            "Materiais": 6,
            "Copos / Taças": 7,
            "Locação": 7,
            "Decoração": 8,
        }
        dados_itens = sorted(
            dados_itens,
            key=lambda x: (
                ordem.get(str(x.get("categoria", "") or ""), 99),
                _norm_orcamento(x.get("produto", "")),
            ),
        )

        cab = [
            "Tipo do Material",
            "Descrição do Item",
            "Qtd. Sistema\n(Prevista)",
            "Conf. Ida\n(Equipe)",
            "Conf. Volta\n(Equipe)",
            "Contagem Final\n(Estoque)",
            "Diferença\nSobra / Perda",
        ]
        linhas = [cab]
        for item in dados_itens:
            unidade = str(item.get("unidade", "") or "").strip()
            qtd = _fmt_qtd_pdf(item.get("quantidade", 0))
            qtd_sistema = f"{qtd} {unidade}".strip()
            linhas.append([
                str(item.get("categoria", "") or ""),
                str(item.get("produto", "") or ""),
                qtd_sistema,
                "",
                "",
                "",
                "",
            ])

        tabela = Table(
            linhas,
            repeatRows=1,
            colWidths=[30*mm, 63*mm, 31*mm, 31*mm, 31*mm, 34*mm, 34*mm],
            rowHeights=None,
        )
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F2937")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,0), 7.2),
            ("ALIGN", (2,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("GRID", (0,0), (-1,-1), 0.45, colors.HexColor("#9CA3AF")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F9FAFB")]),
            ("FONTSIZE", (0,1), (-1,-1), 7.8),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(tabela)

        story.append(Spacer(1, 5*mm))
        assinaturas = Table([
            ["Conferência de Ida - Estoquista / Equipe", "Responsável pelo Evento", "Conferência Final - Estoque"],
            ["\n\n________________________________", "\n\n________________________________", "\n\n________________________________"],
        ], colWidths=[85*mm, 85*mm, 85*mm])
        assinaturas.setStyle(TableStyle([
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        story.append(assinaturas)

        story.append(PageBreak())
        story.append(Paragraph("REGISTRO DE OCORRÊNCIAS DO EVENTO", titulo))
        story.append(Paragraph(
            "Utilize esta página para registrar fatos que impactem o fechamento do evento.",
            normal,
        ))
        story.append(Spacer(1, 4*mm))

        for secao in [
            "Horas extras / extensão do evento",
            "Atrasos / intervalos",
            "Quebras e avarias",
            "Observações gerais",
        ]:
            story.append(Paragraph(secao, subtitulo))
            linhas_obs = [["Data / Hora", "Descrição / Ocorrência", "Responsável"]]
            linhas_obs += [["", "", ""] for _ in range(4)]
            t = Table(linhas_obs, colWidths=[35*mm, 170*mm, 50*mm], rowHeights=[8*mm] + [11*mm]*4)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E5E7EB")),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#9CA3AF")),
                ("FONTSIZE", (0,0), (-1,-1), 8),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ]))
            story.append(t)
            story.append(Spacer(1, 3*mm))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue(), None

    def _gerar_pdf_proposta_cliente(dados):
        """Gera proposta comercial sem expor custos, margem ou lucro."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        except Exception:
            return None, (
                "PDF indisponível: falta a biblioteca reportlab. "
                "No terminal do projeto execute: python -m pip install reportlab "
                "e depois reinicie o Streamlit."
            )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18*mm,
            leftMargin=18*mm,
            topMargin=15*mm,
            bottomMargin=15*mm,
        )
        styles = getSampleStyleSheet()
        title = ParagraphStyle(
            "prop_title_v10", parent=styles["Title"], alignment=TA_CENTER,
            fontSize=20, leading=24, spaceAfter=8,
        )
        h2 = ParagraphStyle(
            "prop_h2_v10", parent=styles["Heading2"], fontSize=12,
            leading=15, spaceBefore=8, spaceAfter=5,
        )
        normal = ParagraphStyle(
            "prop_norm_v10", parent=styles["BodyText"], fontSize=10, leading=14,
        )
        valor = ParagraphStyle(
            "prop_val_v10", parent=styles["Title"], alignment=TA_CENTER,
            fontSize=23, leading=28, textColor=colors.HexColor("#111827"),
            spaceBefore=10, spaceAfter=8,
        )

        story = [
            Paragraph("PROPOSTA PARA EVENTO", title),
            Paragraph(
                "Uma proposta preparada especialmente para o seu evento.",
                normal,
            ),
            Spacer(1, 5*mm),
        ]
        info = [
            ["Cliente", str(dados.get("cliente", "") or "")],
            ["Evento", str(dados.get("tipo_evento", "") or "")],
            ["Data", str(dados.get("data", "") or "")],
            ["Local", str(dados.get("local", "") or "")],
            ["Convidados", str(dados.get("convidados", "") or "")],
            ["Duração", f"{dados.get('horas', 0)} horas"],
        ]
        t = Table(info, colWidths=[38*mm, 115*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F3F4F6")),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#D1D5DB")),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        story.append(t)
        drinks = dados.get("drinks", []) or []
        if drinks:
            story.append(Paragraph("Carta de Drinks", h2))
            for d in drinks:
                story.append(Paragraph(f"• {d}", normal))

        story.append(Paragraph("Serviço", h2))
        story.append(Paragraph(
            "Estrutura e operação de bar conforme a modalidade contratada, "
            "com os itens e equipe definidos para o evento.",
            normal,
        ))
        story.append(Paragraph("Investimento", h2))
        story.append(Paragraph(
            f"R$ {float(dados.get('valor_final', 0) or 0):,.2f}", valor
        ))
        if float(dados.get("valor_por_convidado", 0) or 0) > 0:
            story.append(Paragraph(
                f"Referência por convidado: R$ {float(dados.get('valor_por_convidado', 0) or 0):,.2f}",
                normal,
            ))
        story.append(Spacer(1, 8*mm))
        story.append(Paragraph("Validade da proposta: 7 dias.", normal))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue(), None

    def _renderizar_checklist_evento(evento_id, itens, prefixo, evento=None):
        """
        Checklist digital oficial. O PDF operacional usa os mesmos itens,
        mas não exibe Consumo (indicador gerencial calculado pelo sistema).
        """
        if itens.empty:
            st.info("Nenhum item foi salvo para este evento.")
            return

        categorias_operacionais = [
            "Bebidas",
            "Frutas",
            "Insumos",
            "Artesanais",
            "Gelo",
            "Kit Bar",
            "Materiais",
            "Copos / Taças",
            "Decoração",
        ]

        editores = []
        erros = []

        for categoria in categorias_operacionais:
            df_cat = itens[
                itens["categoria"].fillna("").astype(str).str.lower()
                == categoria.lower()
            ].copy()

            if df_cat.empty:
                continue

            st.markdown(f"### {categoria}")

            base = pd.DataFrame({
                "_id": df_cat["id"].tolist(),
                "Item": df_cat["produto"].fillna("").astype(str).tolist(),
                "Sistema": pd.to_numeric(
                    df_cat["quantidade"], errors="coerce"
                ).fillna(0).tolist(),
                "Ida": pd.to_numeric(
                    df_cat.get("quantidade_ida", 0), errors="coerce"
                ).fillna(0).tolist()
                if "quantidade_ida" in df_cat.columns
                else [0.0] * len(df_cat),
                "Volta": pd.to_numeric(
                    df_cat.get("quantidade_volta", 0), errors="coerce"
                ).fillna(0).tolist()
                if "quantidade_volta" in df_cat.columns
                else [0.0] * len(df_cat),
                "Conferência Final": pd.to_numeric(
                    df_cat.get("quantidade_estoquista", 0), errors="coerce"
                ).fillna(0).tolist()
                if "quantidade_estoquista" in df_cat.columns
                else [0.0] * len(df_cat),
                "Unidade": df_cat["unidade"].fillna("un").astype(str).tolist(),
            })

            editor = st.data_editor(
                base[[
                    "Item", "Sistema", "Ida", "Volta",
                    "Conferência Final", "Unidade",
                ]],
                use_container_width=True,
                hide_index=True,
                disabled=["Item", "Sistema", "Unidade"],
                column_config={
                    "Item": st.column_config.TextColumn("📦 Item"),
                    "Sistema": st.column_config.NumberColumn(
                        "📊 Sistema", format="%.3f"
                    ),
                    "Ida": st.column_config.NumberColumn(
                        "🚚 Ida", min_value=0.0, format="%.3f"
                    ),
                    "Volta": st.column_config.NumberColumn(
                        "↩️ Volta", min_value=0.0, format="%.3f"
                    ),
                    "Conferência Final": st.column_config.NumberColumn(
                        "🔎 Conferência Final", min_value=0.0, format="%.3f"
                    ),
                    "Unidade": st.column_config.TextColumn("Unidade"),
                },
                key=f"{prefixo}_{_safe_key(categoria)}_{evento_id}",
            )

            resumo = editor.copy()
            ida = pd.to_numeric(resumo["Ida"], errors="coerce").fillna(0)
            volta = pd.to_numeric(resumo["Volta"], errors="coerce").fillna(0)
            final = pd.to_numeric(
                resumo["Conferência Final"], errors="coerce"
            ).fillna(0)
            resumo["Consumo"] = ida - final
            resumo["Divergência"] = volta - final

            if (volta > ida).any():
                erros.append(f"{categoria}: há Volta maior que Ida.")
            if (final > ida).any():
                erros.append(f"{categoria}: há Conferência Final maior que Ida.")

            # Para garrafas, mantém a regra operacional de meio em meio.
            if categoria == "Bebidas":
                for col in ["Ida", "Volta", "Conferência Final"]:
                    serie = pd.to_numeric(editor[col], errors="coerce").fillna(0)
                    if ((serie * 2 - (serie * 2).round()).abs() > 1e-7).any():
                        erros.append(
                            "Bebidas: use quantidades em passos de 0,5 "
                            "para Ida, Volta e Conferência Final."
                        )
                        break

            st.dataframe(
                resumo[[
                    "Item", "Sistema", "Ida", "Volta", "Conferência Final",
                    "Consumo", "Divergência", "Unidade",
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Sistema": st.column_config.NumberColumn(format="%.3f"),
                    "Consumo": st.column_config.NumberColumn(
                        "🔥 Consumo", format="%.3f"
                    ),
                    "Divergência": st.column_config.NumberColumn(
                        "⚠️ Divergência", format="%.3f"
                    ),
                },
            )
            editores.append((base, editor, categoria))

        # Categorias administrativas permanecem visíveis, mas não entram na conferência.
        for categoria in ["Equipe", "Custos"]:
            df_cat = itens[
                itens["categoria"].fillna("").astype(str).str.lower()
                == categoria.lower()
            ].copy()
            if not df_cat.empty:
                st.markdown(f"### {categoria}")
                cols = [c for c in ["produto", "quantidade", "unidade"] if c in df_cat.columns]
                st.dataframe(df_cat[cols], use_container_width=True, hide_index=True)

        if erros:
            for erro in sorted(set(erros)):
                st.error(erro)

        if evento is not None:
            pdf, erro_pdf = _gerar_pdf_checklist_operacional(evento, itens)
            if pdf:
                nome_pdf = f"checklist_evento_{evento_id}.pdf"
                st.download_button(
                    "📄 Baixar Checklist PDF",
                    data=pdf,
                    file_name=nome_pdf,
                    mime="application/pdf",
                    key=f"{prefixo}_pdf_{evento_id}",
                    use_container_width=True,
                )
            elif erro_pdf:
                st.caption(erro_pdf)

        if editores:
            if st.button(
                "💾 Salvar Checklist",
                key=f"{prefixo}_salvar_{evento_id}",
                use_container_width=True,
            ):
                if erros:
                    st.error("Corrija as divergências acima antes de salvar.")
                    return

                for base, editor, categoria in editores:
                    for indice, linha in editor.iterrows():
                        ida = float(linha.get("Ida", 0) or 0)
                        volta = float(linha.get("Volta", 0) or 0)
                        conferencia = float(
                            linha.get("Conferência Final", 0) or 0
                        )

                        if volta > ida or conferencia > ida:
                            continue

                        if categoria == "Bebidas":
                            valores = [ida, volta, conferencia]
                            if any(abs(v * 2 - round(v * 2)) > 1e-7 for v in valores):
                                continue

                        item_id = int(base.iloc[indice]["_id"])
                        supabase.table("evento_itens").update({
                            "quantidade_ida": ida,
                            "quantidade_volta": volta,
                            "quantidade_estoquista": conferencia,
                        }).eq("id", item_id).execute()

                st.success("✅ Checklist salvo com sucesso!")
                st.rerun()

    st.title("Orçamentos")

    tab1, tab2, tab3 = st.tabs([
        "🧾 Novo Orçamento",
        "⏳ Pendentes",
        "✅ Aprovados",
    ])

    # =========================================================
    # ABA 1 - NOVO ORÇAMENTO
    # =========================================================
    with tab1:

        _secao_orcamento(
            "1️⃣",
            "Dados do Evento e Cliente",
            "Informações comerciais, local, data, horários e configuração geral do atendimento.",
            "🎉",
        )
        _subsecao_orcamento("👤 Dados do Cliente")

        col1, col2, col3 = st.columns(3)

        nome_cliente = col1.text_input("Nome do cliente")
        data_evento = col2.date_input("Data do evento")
        cidade_evento = col3.text_input("Cidade / Local")

        telefone = st.text_input("📞 Telefone")
        endereco = st.text_input("📍 Endereço do evento")

        tipo_evento = st.selectbox(
            "🎉 Tipo de evento",
            [
                "Casamento",
                "Aniversário",
                "Corporativo",
                "Festa privada",
                "Outro",
            ],
        )

        st.divider()

        tab_bar, tab_mao_obra = st.tabs([
            "🍸 Bar Completo",
            "👷 Serviço Personalizado",
        ])

        # =====================================================
        # BAR COMPLETO
        # =====================================================
        with tab_bar:

            _subsecao_orcamento("👥 Equipe e Horários")

            nomes_equipe = st.text_area(
                "Nomes da equipe (um por linha)",
                placeholder="Ex:\nJoão\nPedro\nLucas",
                key="orc_equipe_bar",
            )

            col1, col2 = st.columns(2)

            hora_chegada = col1.time_input(
                "🕒 Chegada da equipe",
                key="orc_hora_chegada",
            )

            hora_inicio = col2.time_input(
                "🍸 Início do serviço",
                key="orc_hora_inicio",
            )

            hora_convidados = st.time_input(
                "👥 Chegada dos convidados",
                key="orc_hora_convidados",
            )

            modo_calculo = st.radio(
                "Modo de cálculo",
                ["Evento inteiro", "Por hora"],
                key="orc_modo_calculo",
            )

            _subsecao_orcamento("⚙️ Configuração do Evento")

            col1, col2, col3 = st.columns(3)

            num_convidados = col1.number_input(
                "Convidados",
                min_value=1,
                value=50,
                key="orc_convidados",
            )

            horas = col2.number_input(
                "Horas de evento",
                min_value=1,
                value=4,
                key="orc_horas",
            )

            drinks_por_hora = col3.number_input(
                "Drinks por pessoa/hora",
                min_value=0.5,
                value=2.0,
                key="orc_drinks_hora",
            )

            if modo_calculo == "Evento inteiro":
                total_drinks = num_convidados * drinks_por_hora
            else:
                total_drinks = num_convidados * horas * drinks_por_hora

            st.info(f"Total estimado de drinks: {int(total_drinks)}")

            # =================================================
            # CARREGAMENTO DAS BASES
            # =================================================

            df_receitas = pd.DataFrame(
                supabase.table("receitas").select("*").execute().data or []
            )

            df_bebidas = _preparar_base_orcamento(
                pd.DataFrame(
                    supabase.table("precos_bebidas").select("*").execute().data or []
                )
            )

            df_insumos = _preparar_base_orcamento(
                pd.DataFrame(
                    supabase.table("precos_insumos").select("*").execute().data or []
                )
            )

            df_artesanais = _preparar_base_orcamento(
                pd.DataFrame(
                    supabase.table("precos_artesanais").select("*").execute().data or []
                )
            )

            if df_receitas.empty:
                st.warning("Cadastre receitas primeiro.")

            else:
                if "drink" in df_receitas.columns:
                    coluna_drink = "drink"
                elif "bebida" in df_receitas.columns:
                    coluna_drink = "bebida"
                else:
                    coluna_drink = None

                if coluna_drink is None:
                    st.error(
                        "A tabela receitas precisa ter a coluna 'drink' ou 'bebida'."
                    )
                elif not {"ingrediente", "quantidade", "unidade"}.issubset(
                    df_receitas.columns
                ):
                    st.error(
                        "A tabela receitas precisa ter as colunas "
                        "'ingrediente', 'quantidade' e 'unidade'."
                    )
                else:
                    df_receitas[coluna_drink] = (
                        df_receitas[coluna_drink].fillna("").astype(str).str.strip()
                    )
                    df_receitas["ingrediente"] = (
                        df_receitas["ingrediente"].fillna("").astype(str).str.strip()
                    )
                    df_receitas["quantidade"] = pd.to_numeric(
                        df_receitas["quantidade"], errors="coerce"
                    ).fillna(0.0)
                    df_receitas["unidade"] = (
                        df_receitas["unidade"].fillna("").astype(str).str.strip().str.lower()
                    )

                    drinks = sorted(
                        [
                            d
                            for d in df_receitas[coluna_drink].unique().tolist()
                            if str(d).strip()
                        ]
                    )

                    _secao_orcamento(
                        "2️⃣",
                        "Carta de Drinks e Distribuição",
                        "Escolha os drinks e ajuste o peso de saída de cada opção antes do cálculo dos insumos.",
                        "🍸",
                    )
                    _subsecao_orcamento("🍹 Seleção de Drinks")

                    selecao = st.multiselect(
                        "Escolha os drinks do evento",
                        drinks,
                        key="orc_drinks_selecionados",
                    )

                    # A assinatura inclui a seleção. Quando ela muda,
                    # eliminamos somente widgets de cálculo deste orçamento.
                    assinatura_selecao = (
                        int(num_convidados),
                        int(horas),
                        float(drinks_por_hora),
                        str(modo_calculo),
                        tuple(sorted(map(str, selecao))),
                    )

                    if (
                        st.session_state.get("orc_assinatura_selecao")
                        != assinatura_selecao
                    ):
                        _limpar_estado_calculo_orcamento()
                        st.session_state["orc_assinatura_selecao"] = assinatura_selecao

                    if selecao:

                        _subsecao_orcamento(
                            "📊 Distribuição inicial",
                            "Estimativa uniforme antes do ajuste de peso de saída.",
                        )

                        media_por_drink = (
                            float(total_drinks) / len(selecao)
                            if selecao
                            else 0.0
                        )

                        for drink in selecao:
                            st.write(f"• {drink}: ~{media_por_drink:.0f} drinks")

                        _subsecao_orcamento(
                            "⚖️ Ajuste de saída por drink",
                            "Use peso 1 como padrão. Peso 2 representa aproximadamente o dobro da saída de um drink com peso 1.",
                        )

                        pesos = {}
                        total_peso = 0.0

                        colunas_peso = st.columns(2)

                        for i, drink in enumerate(selecao):
                            with colunas_peso[i % 2]:
                                peso = st.number_input(
                                    drink,
                                    min_value=1,
                                    value=1,
                                    step=1,
                                    key=f"orc_peso_{_safe_key(drink)}",
                                )

                            pesos[drink] = float(peso)
                            total_peso += float(peso)

                        assinatura_pesos = tuple(
                            sorted(
                                (
                                    str(drink),
                                    float(pesos[drink]),
                                )
                                for drink in selecao
                            )
                        )

                        if (
                            st.session_state.get("orc_assinatura_pesos")
                            != assinatura_pesos
                        ):
                            for chave in list(st.session_state.keys()):
                                if chave.startswith((
                                    "orc_qtd_",
                                    "orc_marca_",
                                    "orc_insumo_",
                                    "orc_art_",
                                    "orc_prod_",
                                )):
                                    del st.session_state[chave]

                            st.session_state["orc_assinatura_pesos"] = assinatura_pesos

                        _subsecao_orcamento(
                            "📈 Distribuição final calculada",
                            "Esta é a distribuição que será usada para calcular os ingredientes do evento.",
                        )

                        qtd_por_drink = {}

                        for drink in selecao:
                            proporcao = (
                                pesos[drink] / total_peso
                                if total_peso > 0
                                else 0.0
                            )

                            qtd_drink = float(total_drinks) * proporcao
                            qtd_por_drink[drink] = qtd_drink

                            st.write(f"• {drink}: ~{qtd_drink:.0f} drinks")

                        # =============================================
                        # LOCALIZADOR EXATO DE INGREDIENTES
                        # =============================================

                        bases = {
                            "Bebidas": df_bebidas,
                            "Insumos": df_insumos,
                            "Artesanais": df_artesanais,
                        }

                        def _filtrar_base_exata(base, categoria_receita, tipo_base):
                            chave = _norm_orcamento(tipo_base)
                            if not chave or base.empty:
                                return pd.DataFrame()

                            if categoria_receita == "Bebida":
                                return base[base["_tipo_norm"] == chave].copy()

                            if categoria_receita == "Gelo":
                                return base[
                                    (base["_nome_norm"] == chave)
                                    | (base["_tipo_norm"] == chave)
                                ].copy()

                            return base[
                                (base["_nome_norm"] == chave)
                                | (base["_tipo_norm"] == chave)
                            ].copy()

                        def localizar_receita_padronizada(linha_receita):
                            categoria_receita = str(
                                linha_receita.get("categoria", "") or ""
                            ).strip()
                            tipo_base = str(
                                linha_receita.get("tipo_base", "") or ""
                            ).strip()
                            ingrediente = str(
                                linha_receita.get("ingrediente", "") or ""
                            ).strip()

                            if categoria_receita and tipo_base:
                                if categoria_receita == "Bebida":
                                    base = df_bebidas
                                    origem = "Bebidas"
                                elif categoria_receita in ["Fruta / Insumo", "Gelo"]:
                                    base = df_insumos
                                    origem = "Insumos"
                                elif categoria_receita == "Artesanal":
                                    base = df_artesanais
                                    origem = "Artesanais"
                                else:
                                    base = pd.DataFrame()
                                    origem = ""

                                linhas = _filtrar_base_exata(
                                    base, categoria_receita, tipo_base
                                )

                                if not linhas.empty:
                                    return (
                                        origem,
                                        linhas,
                                        "receita validada",
                                        categoria_receita,
                                        tipo_base,
                                    ), None

                                return None, (
                                    f"'{tipo_base}' está validado na receita, mas não possui "
                                    f"cadastro correspondente em {categoria_receita}."
                                )

                            # Fallback apenas para receitas antigas ainda não revisadas.
                            nome_norm = _norm_orcamento(ingrediente)
                            if not nome_norm:
                                return None, "Ingrediente sem nome válido."

                            encontrados = []
                            for origem, base, cat_receita in [
                                ("Bebidas", df_bebidas, "Bebida"),
                                ("Insumos", df_insumos, "Fruta / Insumo"),
                                ("Artesanais", df_artesanais, "Artesanal"),
                            ]:
                                linhas_nome = base[base["_nome_norm"] == nome_norm].copy()
                                linhas_tipo = base[base["_tipo_norm"] == nome_norm].copy()
                                linhas = pd.concat([linhas_nome, linhas_tipo]).drop_duplicates()
                                if not linhas.empty:
                                    encontrados.append((origem, linhas, cat_receita))

                            if len(encontrados) == 1:
                                origem, linhas, cat_receita = encontrados[0]
                                tipo_ref = str(linhas.iloc[0].get("tipo", "") or "").strip()
                                nome_ref = str(linhas.iloc[0].get("nome", "") or "").strip()
                                base_ref = tipo_ref or nome_ref or ingrediente
                                return (
                                    origem,
                                    linhas,
                                    "fallback exato - revisar receita",
                                    cat_receita,
                                    base_ref,
                                ), None

                            if len(encontrados) > 1:
                                return None, (
                                    f"'{ingrediente}' possui correspondência exata em mais de "
                                    "uma base. Revise categoria e tipo_base na aba Receitas."
                                )

                            return None, (
                                f"'{ingrediente}' não possui categoria/tipo_base validado e "
                                "não foi encontrado exatamente na Precificação. Revise a receita."
                            )

                        # =============================================
                        # CÁLCULO EXATO A PARTIR DAS RECEITAS SELECIONADAS
                        # =============================================

                        necessidades = {}
                        pendencias_ingredientes = []

                        for drink in selecao:
                            receita = df_receitas[
                                df_receitas[coluna_drink].astype(str).str.strip()
                                == str(drink).strip()
                            ].copy()

                            qtd_drink = qtd_por_drink.get(drink, 0.0)

                            for _, linha_receita in receita.iterrows():
                                ingrediente = str(
                                    linha_receita.get("ingrediente", "")
                                ).strip()

                                quantidade_receita = float(
                                    linha_receita.get("quantidade", 0) or 0
                                )

                                unidade = str(
                                    linha_receita.get("unidade", "")
                                ).strip().lower()

                                if not ingrediente or quantidade_receita <= 0:
                                    continue

                                localizado, erro_localizacao = localizar_receita_padronizada(
                                    linha_receita
                                )

                                if erro_localizacao:
                                    pendencias_ingredientes.append(
                                        {
                                            "Drink": drink,
                                            "Ingrediente": ingrediente,
                                            "Problema": erro_localizacao,
                                        }
                                    )
                                    continue

                                (
                                    origem, linhas_origem, modo_match,
                                    categoria_receita, tipo_base_receita,
                                ) = localizado

                                if categoria_receita == "Gelo":
                                    categoria = "Gelo"
                                elif origem == "Insumos":
                                    primeira_linha = linhas_origem.iloc[0]
                                    categoria = (
                                        "Frutas"
                                        if _eh_fruta_por_tipo(primeira_linha)
                                        else "Insumos"
                                    )
                                else:
                                    categoria = origem

                                # A quantidade vem EXCLUSIVAMENTE da receita.
                                # Nenhuma fruta, garnish, rendimento ou ingrediente
                                # extra é inventado pelo código. Se houver decoração,
                                # perda técnica ou rendimento, isso deve estar cadastrado
                                # na própria receita/estrutura de dados.
                                necessidade = quantidade_receita * qtd_drink

                                # Consolida sinônimos/nomes diferentes quando eles
                                # apontam com segurança para a mesma referência de cadastro.
                                primeira_ref = linhas_origem.iloc[0]
                                tipo_ref = _norm_orcamento(
                                    primeira_ref.get("tipo", "")
                                )
                                nome_ref = _norm_orcamento(
                                    primeira_ref.get("nome", "")
                                )

                                if tipo_base_receita:
                                    referencia_norm = (
                                        f"base:{_norm_orcamento(tipo_base_receita)}"
                                    )
                                elif "tipo" in modo_match and tipo_ref:
                                    referencia_norm = f"tipo:{tipo_ref}"
                                else:
                                    referencia_norm = f"nome:{nome_ref}"

                                chave_necessidade = (
                                    origem,
                                    referencia_norm,
                                    unidade,
                                )

                                if chave_necessidade not in necessidades:
                                    necessidades[chave_necessidade] = {
                                        "origem": origem,
                                        "categoria": categoria,
                                        "ingrediente": ingrediente,
                                        "aliases": {ingrediente},
                                        "referencia": referencia_norm,
                                        "tipo_base": tipo_base_receita,
                                        "categoria_receita": categoria_receita,
                                        "unidade": unidade,
                                        "quantidade": 0.0,
                                        "linhas_origem": linhas_origem,
                                        "modo_match": modo_match,
                                        "drinks": set(),
                                    }
                                else:
                                    necessidades[chave_necessidade][
                                        "aliases"
                                    ].add(ingrediente)

                                necessidades[chave_necessidade]["quantidade"] += necessidade
                                necessidades[chave_necessidade]["drinks"].add(drink)

                        _secao_orcamento(
                            "3️⃣",
                            "Planejamento Operacional",
                            "Escolha marcas e embalagens, faça o ajuste fino das quantidades e inclua os materiais que irão para o evento.",
                            "📦",
                        )

                        # =============================================
                        # AUDITORIA DOS INGREDIENTES
                        # =============================================

                        auditoria = []

                        for dados_necessidade in necessidades.values():
                            auditoria.append({
                                "Ingrediente": " / ".join(
                                    sorted(
                                        dados_necessidade.get(
                                            "aliases",
                                            {dados_necessidade["ingrediente"]},
                                        )
                                    )
                                ),
                                "Categoria": dados_necessidade["categoria"],
                                "Quantidade": dados_necessidade["quantidade"],
                                "Unidade": dados_necessidade["unidade"],
                                "Drinks": ", ".join(
                                    sorted(dados_necessidade["drinks"])
                                ),
                                "Correspondência": dados_necessidade["modo_match"],
                            })

                        with st.expander(
                            "🔎 Diagnóstico técnico dos ingredientes",
                            expanded=bool(pendencias_ingredientes),
                        ):
                            if pendencias_ingredientes:
                                st.error(
                                    "Existem ingredientes das receitas que não puderam "
                                    "ser classificados com segurança. O orçamento não será "
                                    "salvo enquanto eles não forem corrigidos."
                                )
                                st.dataframe(
                                    pd.DataFrame(pendencias_ingredientes),
                                    use_container_width=True,
                                    hide_index=True,
                                )
                            else:
                                st.success(
                                    "✅ Todas as receitas selecionadas possuem vínculos válidos para este orçamento."
                                )

                            if auditoria:
                                st.dataframe(
                                    pd.DataFrame(auditoria),
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "Quantidade": st.column_config.NumberColumn(
                                            format="%.3f"
                                        )
                                    },
                                )

                        # =============================================
                        # MONTAGEM DOS ITENS FINAIS
                        # =============================================

                        itens_orcamento = []
                        custo_bebidas = 0.0
                        custo_frutas = 0.0
                        custo_insumos = 0.0
                        custo_artesanais = 0.0
                        erros_calculo = []

                        # ---------------------------------------------
                        # BEBIDAS
                        # ---------------------------------------------

                        bebidas_calc = [
                            x
                            for x in necessidades.values()
                            if x["origem"] == "Bebidas"
                        ]

                        _subsecao_orcamento(
                            "🍾 Bebidas",
                            "Cada item fica separado em duas decisões: marca/embalagem e ajuste fino da quantidade que irá para o evento.",
                        )

                        if not bebidas_calc:
                            st.caption("Nenhuma bebida necessária para os drinks selecionados.")

                        for item in bebidas_calc:
                            ingrediente = " / ".join(
                                sorted(item.get("aliases", {item["ingrediente"]}))
                            )
                            qtd_necessaria = float(item["quantidade"])
                            unidade = item["unidade"]
                            opcoes = item["linhas_origem"].copy()

                            if unidade != "ml":
                                erros_calculo.append(
                                    f"{ingrediente}: bebida cadastrada na receita com unidade '{unidade}'. "
                                    "Para bebidas, utilize ml."
                                )
                                continue

                            if opcoes.empty:
                                erros_calculo.append(
                                    f"{ingrediente}: nenhuma opção de bebida encontrada."
                                )
                                continue

                            chave_base = _safe_key(
                                f"{ingrediente}_{unidade}"
                            )

                            with st.container(border=True):
                                st.markdown(f"#### 🍾 {ingrediente}")
                                st.caption(
                                    f"Necessidade calculada pela carta: {qtd_necessaria:.0f} ml"
                                )

                                col_marca, col_ajuste = st.columns([3, 2], gap="large")

                                with col_marca:
                                    linha_produto = _selecionar_linha_produto(
                                        opcoes,
                                        "1️⃣ Marca / embalagem",
                                        key=f"orc_marca_{chave_base}",
                                    )

                                if linha_produto is None:
                                    erros_calculo.append(
                                        f"{ingrediente}: nenhuma opção válida encontrada."
                                    )
                                    continue

                                marca = str(
                                    linha_produto.get("nome", ingrediente) or ingrediente
                                ).strip()
                                volume = float(
                                    linha_produto.get("quantidade", 0) or 0
                                )
                                preco = float(
                                    linha_produto.get("preco", 0) or 0
                                )

                                if volume <= 0:
                                    erros_calculo.append(
                                        f"{marca}: quantidade/volume cadastrado é inválido."
                                    )
                                    continue

                                qtd_calculada = math.ceil(qtd_necessaria / volume)
                                chave_qtd = (
                                    f"orc_qtd_beb_{chave_base}_{_safe_key(marca)}"
                                )
                                if chave_qtd not in st.session_state:
                                    st.session_state[chave_qtd] = int(qtd_calculada)

                                with col_ajuste:
                                    st.markdown("**2️⃣ Ajuste fino da saída**")
                                    st.caption(
                                        f"Sugestão do sistema: {int(qtd_calculada)} garrafa(s)"
                                    )
                                    qtd_editavel = st.number_input(
                                        "Garrafas que irão para o evento",
                                        min_value=0,
                                        step=1,
                                        key=chave_qtd,
                                    )

                                custo_item = float(qtd_editavel) * preco

                                info1, info2, info3, info4 = st.columns(4)
                                info1.caption("Produto selecionado")
                                info1.markdown(f"**{marca}**")
                                info2.caption("Embalagem")
                                info2.markdown(f"**{volume:g} ml**")
                                info3.caption("Preço unitário")
                                info3.markdown(f"**R$ {preco:,.2f}**")
                                info4.caption("Custo previsto")
                                info4.markdown(f"**R$ {custo_item:,.2f}**")

                            custo_bebidas += custo_item

                            itens_orcamento.append({
                                "categoria": "Bebidas",
                                "produto": marca,
                                "quantidade": float(qtd_editavel),
                                "unidade": "garrafas",
                                "custo_estimado": custo_item,
                                "tipo_base": item.get("tipo_base", ingrediente),
                                "produto_ref_id": linha_produto.get("id"),
                                "quantidade_base": volume,
                                "preco_unitario": preco,
                                "custo_unitario_operacional": preco,
                            })

                        st.markdown(
                            f"**Subtotal Bebidas:** R$ {custo_bebidas:,.2f}"
                        )

                        # ---------------------------------------------
                        # FRUTAS E INSUMOS
                        # ---------------------------------------------

                        for categoria_alvo in ["Frutas", "Insumos", "Gelo"]:
                            itens_calc = [
                                x
                                for x in necessidades.values()
                                if x["categoria"] == categoria_alvo
                            ]

                            if categoria_alvo == "Frutas":
                                titulo = "🍋 Frutas"
                            elif categoria_alvo == "Gelo":
                                titulo = "🧊 Gelo"
                            else:
                                titulo = "🧴 Insumos"

                            _subsecao_orcamento(titulo)

                            if not itens_calc:
                                st.caption(
                                    f"Nenhum item em {categoria_alvo.lower()} "
                                    "para os drinks selecionados."
                                )

                            for item in itens_calc:
                                ingrediente = " / ".join(
                                    sorted(item.get("aliases", {item["ingrediente"]}))
                                )
                                unidade = item["unidade"]
                                qtd_necessaria = float(item["quantidade"])
                                opcoes = item["linhas_origem"].copy()

                                if opcoes.empty:
                                    erros_calculo.append(
                                        f"{ingrediente}: item não encontrado na base de insumos."
                                    )
                                    continue

                                chave_base = _safe_key(
                                    f"{categoria_alvo}_{ingrediente}_{unidade}"
                                )

                                linha_produto = _selecionar_linha_produto(
                                    opcoes,
                                    f"Cadastro / embalagem para {ingrediente}",
                                    key=f"orc_insumo_{chave_base}",
                                )

                                if linha_produto is None:
                                    erros_calculo.append(
                                        f"{ingrediente}: nenhuma opção válida encontrada."
                                    )
                                    continue

                                produto_escolhido = str(
                                    linha_produto.get("nome", ingrediente) or ingrediente
                                ).strip()

                                preco = float(
                                    linha_produto.get("preco", 0) or 0
                                )

                                quantidade_embalagem = float(
                                    linha_produto.get("quantidade", 0) or 0
                                )

                                chave_qtd = f"orc_qtd_ins_{chave_base}"

                                if chave_qtd not in st.session_state:
                                    st.session_state[chave_qtd] = float(
                                        qtd_necessaria
                                    )

                                col1, col2, col3 = st.columns([4, 2, 2])

                                col1.write(
                                    f"✔ {produto_escolhido}"
                                )
                                col1.caption(
                                    f"Necessidade calculada: "
                                    f"{qtd_necessaria:.2f} {unidade}"
                                )

                                qtd_editavel = col2.number_input(
                                    unidade or "Quantidade",
                                    min_value=0.0,
                                    key=chave_qtd,
                                )

                                if unidade == "g":
                                    custo_item = (
                                        float(qtd_editavel)
                                        * (preco / 1000.0)
                                    )

                                elif unidade == "kg":
                                    custo_item = (
                                        float(qtd_editavel)
                                        * preco
                                    )

                                elif quantidade_embalagem > 0:
                                    custo_item = (
                                        float(qtd_editavel)
                                        / quantidade_embalagem
                                        * preco
                                    )

                                else:
                                    custo_item = 0.0
                                    erros_calculo.append(
                                        f"{produto_escolhido}: não foi possível calcular "
                                        f"o custo para a unidade '{unidade}'."
                                    )

                                col3.write(
                                    f"💰 R$ {custo_item:,.2f}"
                                )

                                if categoria_alvo == "Frutas":
                                    custo_frutas += custo_item
                                else:
                                    custo_insumos += custo_item

                                if unidade == "g":
                                    custo_unit_oper = preco / 1000.0
                                    qtd_base_snapshot = 1000.0
                                elif unidade == "kg":
                                    custo_unit_oper = preco
                                    qtd_base_snapshot = 1.0
                                elif quantidade_embalagem > 0:
                                    custo_unit_oper = preco / quantidade_embalagem
                                    qtd_base_snapshot = quantidade_embalagem
                                else:
                                    custo_unit_oper = 0.0
                                    qtd_base_snapshot = 0.0

                                itens_orcamento.append({
                                    "categoria": categoria_alvo,
                                    "produto": produto_escolhido,
                                    "quantidade": float(qtd_editavel),
                                    "unidade": unidade,
                                    "custo_estimado": custo_item,
                                    "tipo_base": item.get("tipo_base", ingrediente),
                                    "produto_ref_id": linha_produto.get("id"),
                                    "quantidade_base": qtd_base_snapshot,
                                    "preco_unitario": preco,
                                    "custo_unitario_operacional": custo_unit_oper,
                                })

                        # ---------------------------------------------
                        # ARTESANAIS
                        # ---------------------------------------------

                        artesanais_calc = [
                            x
                            for x in necessidades.values()
                            if x["origem"] == "Artesanais"
                        ]

                        _subsecao_orcamento("🧪 Produção Artesanal")

                        if not artesanais_calc:
                            st.caption(
                                "Nenhum artesanal necessário para os drinks selecionados."
                            )

                        for item in artesanais_calc:
                            ingrediente = " / ".join(
                                sorted(item.get("aliases", {item["ingrediente"]}))
                            )
                            unidade = item["unidade"]
                            qtd_necessaria = float(item["quantidade"])
                            opcoes = item["linhas_origem"].copy()

                            if opcoes.empty:
                                erros_calculo.append(
                                    f"{ingrediente}: item não encontrado em precos_artesanais."
                                )
                                continue

                            chave_base = _safe_key(
                                f"{ingrediente}_{unidade}"
                            )

                            linha_produto = _selecionar_linha_produto(
                                opcoes,
                                f"Cadastro / embalagem artesanal para {ingrediente}",
                                key=f"orc_art_{chave_base}",
                            )

                            if linha_produto is None:
                                erros_calculo.append(
                                    f"{ingrediente}: nenhuma opção válida encontrada."
                                )
                                continue

                            produto_escolhido = str(
                                linha_produto.get("nome", ingrediente) or ingrediente
                            ).strip()

                            quantidade_base = float(
                                linha_produto.get("quantidade", 0) or 0
                            )

                            preco_base = float(
                                linha_produto.get("preco", 0) or 0
                            )

                            chave_qtd = f"orc_qtd_art_{chave_base}"

                            if chave_qtd not in st.session_state:
                                st.session_state[chave_qtd] = float(
                                    qtd_necessaria
                                )

                            col1, col2, col3 = st.columns([4, 2, 2])

                            col1.write(f"✔ {produto_escolhido}")
                            col1.caption(
                                f"Necessidade calculada: "
                                f"{qtd_necessaria:.2f} {unidade}"
                            )

                            qtd_editavel = col2.number_input(
                                unidade or "Quantidade",
                                min_value=0.0,
                                key=chave_qtd,
                            )

                            if quantidade_base > 0:
                                custo_item = (
                                    float(qtd_editavel)
                                    / quantidade_base
                                    * preco_base
                                )
                            else:
                                custo_item = 0.0
                                erros_calculo.append(
                                    f"{produto_escolhido}: quantidade base inválida "
                                    "em precos_artesanais."
                                )

                            col3.write(
                                f"💰 R$ {custo_item:,.2f}"
                            )

                            custo_artesanais += custo_item

                            itens_orcamento.append({
                                "categoria": "Artesanais",
                                "produto": produto_escolhido,
                                "quantidade": float(qtd_editavel),
                                "unidade": unidade,
                                "custo_estimado": custo_item,
                                "tipo_base": item.get("tipo_base", ingrediente),
                                "produto_ref_id": linha_produto.get("id"),
                                "quantidade_base": quantidade_base,
                                "preco_unitario": preco_base,
                                "custo_unitario_operacional": (
                                    preco_base / quantidade_base
                                    if quantidade_base > 0 else 0.0
                                ),
                            })

                        st.markdown(
                            f"**Subtotal Artesanais:** "
                            f"R$ {custo_artesanais:,.2f}"
                        )

                        # =============================================
                        # ERROS DE CÁLCULO
                        # =============================================

                        if erros_calculo:
                            st.error(
                                "Existem cadastros que impedem um cálculo "
                                "100% confiável:"
                            )
                            for erro in erros_calculo:
                                st.write(f"• {erro}")

                        # =============================================
                        # CUSTOS EXTRAS
                        # =============================================

                        _subsecao_orcamento(
                            "💸 Custos Operacionais Extras",
                            "Somente custos que não nasceram das receitas ou do checklist calculado.",
                        )

                        col1, col2, col3, col4 = st.columns(4)

                        custo_gelo = col1.number_input(
                            "🧊 Gelo",
                            min_value=0.0,
                            format="%.2f",
                            key="orc_custo_gelo",
                        )

                        custo_transporte = col2.number_input(
                            "🚚 Transporte",
                            min_value=0.0,
                            format="%.2f",
                            key="orc_custo_transporte",
                        )

                        custo_viagem = col3.number_input(
                            "🛣️ Viagem / Km",
                            min_value=0.0,
                            format="%.2f",
                            key="orc_custo_viagem",
                        )

                        custo_caches = col4.number_input(
                            "👥 Cachês equipe",
                            min_value=0.0,
                            format="%.2f",
                            key="orc_custo_caches",
                        )

                        custo_outros = st.number_input(
                            "📦 Outros custos",
                            min_value=0.0,
                            format="%.2f",
                            key="orc_custo_outros",
                        )

                        custo_extras = (
                            custo_gelo
                            + custo_transporte
                            + custo_viagem
                            + custo_caches
                            + custo_outros
                        )

                        st.metric(
                            "💸 Total dos Custos Extras",
                            f"R$ {custo_extras:,.2f}",
                        )

                        # =============================================
                        # SERVIÇOS ADICIONAIS
                        # Mantidos, mas isolados do cálculo principal
                        # para não apagar/duplicar itens dos drinks.
                        # =============================================

                        _subsecao_orcamento("📦 Serviços Adicionais")

                        pacotes = (
                            supabase.table("pacotes")
                            .select("*")
                            .eq("ativo", True)
                            .execute()
                            .data
                            or []
                        )

                        custo_servicos = 0.0
                        total_pacotes = 0.0
                        itens_pacotes = []

                        if pacotes:
                            for pacote in pacotes:
                                usar = st.checkbox(
                                    pacote["nome"],
                                    key=f'orc_pacote_{pacote["id"]}',
                                )

                                if not usar:
                                    continue

                                dados_pacote = pacote.get("dados") or {}

                                percentual = st.number_input(
                                    "Percentual de consumo (%)",
                                    value=float(
                                        dados_pacote.get(
                                            "percentual_consumo",
                                            30,
                                        )
                                    ),
                                    key=f'orc_perc_{pacote["id"]}',
                                )

                                doses = st.number_input(
                                    "Doses por pessoa",
                                    value=float(
                                        dados_pacote.get(
                                            "doses_pessoa",
                                            4,
                                        )
                                    ),
                                    key=f'orc_dose_{pacote["id"]}',
                                )

                                ml_dose = st.number_input(
                                    "ML por dose",
                                    value=float(
                                        dados_pacote.get(
                                            "ml_dose",
                                            50,
                                        )
                                    ),
                                    key=f'orc_ml_{pacote["id"]}',
                                )

                                markup = st.number_input(
                                    "Markup",
                                    value=float(
                                        dados_pacote.get(
                                            "markup",
                                            3,
                                        )
                                    ),
                                    key=f'orc_markup_{pacote["id"]}',
                                )

                                pessoas = num_convidados * percentual / 100
                                doses_total = pessoas * doses
                                ml_total = doses_total * ml_dose

                                st.info(
                                    f"Consumo previsto: {ml_total:.0f} ml"
                                )

                                produtos = (
                                    supabase.table("pacote_produtos")
                                    .select("*")
                                    .eq("pacote_id", pacote["id"])
                                    .execute()
                                    .data
                                    or []
                                )

                                custo_pacote = 0.0

                                for produto in produtos:
                                    resultado_estoque = (
                                        supabase.table("estoque")
                                        .select("*")
                                        .eq(
                                            "id",
                                            produto["estoque_id"],
                                        )
                                        .execute()
                                        .data
                                        or []
                                    )

                                    if not resultado_estoque:
                                        st.warning(
                                            f"Produto de estoque "
                                            f"(id {produto['estoque_id']}) "
                                            "não encontrado. Item ignorado."
                                        )
                                        continue

                                    estoque_item = resultado_estoque[0]

                                    usar_produto = st.checkbox(
                                        str(
                                            estoque_item.get(
                                                "marca",
                                                "Produto",
                                            )
                                        ),
                                        value=True,
                                        key=f'orc_usar_pac_{produto["id"]}',
                                    )

                                    if not usar_produto:
                                        continue

                                    participacao = st.number_input(
                                        "%",
                                        min_value=0.0,
                                        max_value=100.0,
                                        value=float(
                                            produto.get(
                                                "participacao",
                                                0,
                                            )
                                            or 0
                                        ),
                                        key=f'orc_part_pac_{produto["id"]}',
                                    )

                                    ml_produto = (
                                        ml_total
                                        * participacao
                                        / 100.0
                                    )

                                    try:
                                        tamanho = float(
                                            estoque_item.get(
                                                "tamanho",
                                                0,
                                            )
                                        )

                                        if tamanho <= 0:
                                            raise ValueError

                                    except (TypeError, ValueError):
                                        st.error(
                                            f"Tamanho inválido para "
                                            f"{estoque_item.get('marca', 'produto')}."
                                        )
                                        continue

                                    garrafas = math.ceil(
                                        ml_produto / tamanho
                                    )

                                    preco = float(
                                        estoque_item.get(
                                            "preco",
                                            0,
                                        )
                                        or 0
                                    )

                                    custo_produto = (
                                        garrafas * preco
                                    )

                                    custo_pacote += custo_produto

                                    itens_pacotes.append({
                                        "categoria": "Bebidas",
                                        "produto": str(
                                            estoque_item.get("marca", "")
                                        ),
                                        "quantidade": float(garrafas),
                                        "unidade": "garrafas",
                                        "custo_estimado": custo_produto,
                                        "tipo_base": str(
                                            estoque_item.get("produto", "") or ""
                                        ),
                                        "produto_ref_id": estoque_item.get("id"),
                                        "quantidade_base": tamanho,
                                        "preco_unitario": preco,
                                        "custo_unitario_operacional": preco,
                                    })

                                    st.write(
                                        f"🍾 {estoque_item.get('marca', '')} "
                                        f"- {garrafas} garrafas"
                                    )

                                venda_pacote = (
                                    custo_pacote * markup
                                )

                                custo_servicos += custo_pacote
                                total_pacotes += venda_pacote

                                st.success(
                                    f"Custo: R$ {custo_pacote:,.2f} | "
                                    f"Venda de referência: "
                                    f"R$ {venda_pacote:,.2f}"
                                )

                        else:
                            st.info("Nenhum serviço cadastrado.")

                        st.metric(
                            "Total Serviços Adicionais",
                            f"R$ {total_pacotes:,.2f}",
                        )

                        # =============================================
                        # MATERIAIS OPERACIONAIS OPCIONAIS
                        # =============================================
                        st.divider()
                        _subsecao_orcamento(
                            "🧰 Materiais Operacionais",
                            "Tudo que a equipe precisa levar além dos ingredientes: utensílios, copos, decoração, limpeza e itens adicionais.",
                        )
                        with st.expander(
                            "Selecionar materiais e itens adicionais",
                            expanded=False,
                        ):
                            st.caption(
                                "Itens selecionados aqui entram no checklist/PDF, "
                                "mas não alteram automaticamente o custo de bebidas e ingredientes."
                            )
                            itens_materiais = []

                            for tabela_mat, categoria_mat, titulo_mat in [
                                ("materiais_utensilios_bar", "Kit Bar", "Utensílios de Bar"),
                                ("copos_tacas", "Copos / Taças", "Copos e Taças"),
                                ("materiais_decorativos", "Decoração", "Materiais Decorativos"),
                            ]:
                                try:
                                    dados_mat = (
                                        supabase.table(tabela_mat)
                                        .select("*")
                                        .execute()
                                        .data
                                        or []
                                    )
                                    df_mat = pd.DataFrame(dados_mat)
                                except Exception:
                                    df_mat = pd.DataFrame()

                                if df_mat.empty or "nome" not in df_mat.columns:
                                    continue

                                st.markdown(f"**{titulo_mat}**")
                                opcoes_mat = [
                                    str(x).strip()
                                    for x in df_mat["nome"].dropna().astype(str).tolist()
                                    if str(x).strip()
                                ]
                                selecionados_mat = st.multiselect(
                                    f"Selecionar {titulo_mat.lower()}",
                                    opcoes_mat,
                                    key=f"orc_mat_{_safe_key(tabela_mat)}",
                                )
                                for nome_mat in selecionados_mat:
                                    linha_mat = df_mat[
                                        df_mat["nome"].astype(str) == nome_mat
                                    ].iloc[0]
                                    qtd_padrao = 1.0
                                    unidade_mat = str(
                                        linha_mat.get("unidade", "un") or "un"
                                    )
                                    qtd_mat = st.number_input(
                                        f"Quantidade - {nome_mat}",
                                        min_value=0.0,
                                        value=qtd_padrao,
                                        step=1.0,
                                        key=f"orc_mat_qtd_{_safe_key(tabela_mat)}_{_safe_key(nome_mat)}",
                                    )
                                    if qtd_mat > 0:
                                        itens_materiais.append({
                                            "categoria": categoria_mat,
                                            "produto": nome_mat,
                                            "quantidade": float(qtd_mat),
                                            "unidade": unidade_mat,
                                            "custo_estimado": 0.0,
                                            "tipo_base": categoria_mat,
                                            "produto_ref_id": linha_mat.get("id"),
                                            "quantidade_base": 1.0,
                                            "preco_unitario": 0.0,
                                            "custo_unitario_operacional": 0.0,
                                        })

                            st.markdown("---")
                            st.markdown("**➕ Item adicional do checklist**")
                            st.caption(
                                "Use para limpeza/higienização ou qualquer item operacional que ainda não possua cadastro próprio."
                            )

                            if "orc_itens_manuais" not in st.session_state:
                                st.session_state["orc_itens_manuais"] = []

                            m1, m2, m3, m4 = st.columns([2, 4, 1.5, 1.5])
                            categoria_manual = m1.selectbox(
                                "Categoria",
                                [
                                    "Kit Bar",
                                    "Limpeza / Higienização",
                                    "Copos / Taças",
                                    "Decoração",
                                    "Gelo",
                                    "Outros",
                                ],
                                key="orc_manual_categoria",
                            )
                            item_manual = m2.text_input(
                                "Item",
                                key="orc_manual_item",
                                placeholder="Ex.: pano multiuso, saco de lixo, balde...",
                            )
                            qtd_manual = m3.number_input(
                                "Qtd.",
                                min_value=0.0,
                                value=1.0,
                                step=1.0,
                                key="orc_manual_qtd",
                            )
                            unidade_manual = m4.selectbox(
                                "Unidade",
                                ["un", "kit", "pct", "cx", "kg", "g", "L", "ml"],
                                key="orc_manual_unidade",
                            )

                            if st.button(
                                "➕ Adicionar item ao checklist",
                                key="orc_manual_add",
                                use_container_width=True,
                            ):
                                if not item_manual.strip():
                                    st.warning("Informe o nome do item adicional.")
                                elif qtd_manual <= 0:
                                    st.warning("A quantidade deve ser maior que zero.")
                                else:
                                    st.session_state["orc_itens_manuais"].append({
                                        "categoria": categoria_manual,
                                        "produto": item_manual.strip(),
                                        "quantidade": float(qtd_manual),
                                        "unidade": unidade_manual,
                                        "custo_estimado": 0.0,
                                        "tipo_base": categoria_manual,
                                        "produto_ref_id": None,
                                        "quantidade_base": 1.0,
                                        "preco_unitario": 0.0,
                                        "custo_unitario_operacional": 0.0,
                                    })
                                    st.rerun()

                            if st.session_state["orc_itens_manuais"]:
                                st.dataframe(
                                    pd.DataFrame(st.session_state["orc_itens_manuais"])[
                                        ["categoria", "produto", "quantidade", "unidade"]
                                    ].rename(columns={
                                        "categoria": "Categoria",
                                        "produto": "Item",
                                        "quantidade": "Quantidade",
                                        "unidade": "Unidade",
                                    }),
                                    use_container_width=True,
                                    hide_index=True,
                                )
                                if st.button(
                                    "🗑️ Limpar itens adicionais",
                                    key="orc_manual_limpar",
                                ):
                                    st.session_state["orc_itens_manuais"] = []
                                    st.rerun()

                            itens_materiais.extend(
                                st.session_state.get("orc_itens_manuais", [])
                            )

                        # =============================================
                        # LISTA CANÔNICA DO EVENTO
                        # É esta lista que é mostrada e depois salva.
                        # =============================================

                        itens_orcamento.extend(itens_pacotes)
                        itens_orcamento.extend(itens_materiais)
                        itens_orcamento = _consolidar_itens(
                            itens_orcamento
                        )

                        _secao_orcamento(
                            "4️⃣",
                            "Checklist Operacional",
                            "Mapa oficial da equipe. O sistema acrescenta Consumo e Divergência; o PDF segue o modelo operacional sem custos internos.",
                            "📋",
                        )
                        _subsecao_orcamento("📋 Checklist Previsto do Evento")

                        if itens_orcamento:
                            df_check_previsto = pd.DataFrame(itens_orcamento)
                            df_check_sistema = pd.DataFrame({
                                "Categoria": df_check_previsto["categoria"],
                                "Item": df_check_previsto["produto"],
                                "Sistema": df_check_previsto["quantidade"],
                                "Ida": 0.0,
                                "Volta": 0.0,
                                "Conferência Final": 0.0,
                                "Consumo": 0.0,
                                "Divergência": 0.0,
                                "Unidade": df_check_previsto["unidade"],
                            })
                            st.dataframe(
                                df_check_sistema,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Sistema": st.column_config.NumberColumn(format="%.3f"),
                                    "Ida": st.column_config.NumberColumn(format="%.3f"),
                                    "Volta": st.column_config.NumberColumn(format="%.3f"),
                                    "Conferência Final": st.column_config.NumberColumn(format="%.3f"),
                                    "Consumo": st.column_config.NumberColumn(format="%.3f"),
                                    "Divergência": st.column_config.NumberColumn(format="%.3f"),
                                },
                            )

                            evento_preview = {
                                "id": "RASCUNHO",
                                "cliente": nome_cliente,
                                "data": str(data_evento),
                                "cidade": cidade_evento,
                                "endereco": endereco,
                                "tipo_evento": tipo_evento,
                                "convidados": num_convidados,
                                "hora_chegada": str(hora_chegada),
                                "hora_inicio": str(hora_inicio),
                                "drinks": "\n".join(map(str, selecao)),
                            }
                            pdf_check, erro_pdf_check = _gerar_pdf_checklist_operacional(
                                evento_preview,
                                pd.DataFrame(itens_orcamento),
                            )
                            if pdf_check:
                                st.download_button(
                                    "📄 Baixar Checklist Operacional PDF",
                                    data=pdf_check,
                                    file_name="checklist_operacional_orcamento.pdf",
                                    mime="application/pdf",
                                    key="orc_pdf_checklist_preview",
                                    use_container_width=True,
                                )
                            elif erro_pdf_check:
                                st.caption(erro_pdf_check)
                        else:
                            st.warning("Nenhum item operacional foi calculado.")

                        # =============================================
                        # TOTAL
                        # =============================================

                        custo_total = (
                            custo_bebidas
                            + custo_frutas
                            + custo_insumos
                            + custo_artesanais
                            + custo_extras
                            + custo_servicos
                        )

                        _secao_orcamento(
                            "5️⃣",
                            "Precificação Interna e Fechamento",
                            "Área interna: custo, margem, desconto, comissão e resultado estimado. Estes dados não aparecem no modo cliente.",
                            "💰",
                        )

                        col_custo_resumo, col_itens_resumo = st.columns(2)
                        col_custo_resumo.metric(
                            "💰 Custo Total do Evento (Orçado)",
                            f"R$ {custo_total:,.2f}",
                        )
                        col_itens_resumo.metric(
                            "📦 Itens no Checklist",
                            len(itens_orcamento),
                        )

                        # =============================================
                        # PRECIFICAÇÃO
                        # =============================================

                        _subsecao_orcamento("📈 Precificação Interna")

                        margem = st.slider(
                            "Margem de lucro (%)",
                            0,
                            300,
                            100,
                            key="orc_margem",
                        )

                        preco_venda = (
                            custo_total
                            * (1 + margem / 100)
                        )

                        desconto = st.slider(
                            "Desconto (%)",
                            0,
                            100,
                            0,
                            key="orc_desconto",
                        )

                        preco_com_desconto = (
                            preco_venda
                            * (1 - desconto / 100)
                        )

                        valor_desconto = (
                            preco_venda
                            - preco_com_desconto
                        )

                        st.subheader("🤝 Comissão")

                        incluir_comissao = st.checkbox(
                            "Incluir comissão nesta venda",
                            value=False,
                            key="orc_incluir_comissao",
                        )

                        valor_comissao = 0.0
                        percentual_comissao = 0.0

                        if incluir_comissao:
                            percentual_comissao = (
                                st.number_input(
                                    "Percentual da comissão (%)",
                                    min_value=0.0,
                                    max_value=100.0,
                                    value=10.0,
                                    step=0.5,
                                    key="orc_percentual_comissao",
                                )
                            )

                            valor_comissao = (
                                preco_com_desconto
                                * (
                                    percentual_comissao
                                    / 100
                                )
                            )

                        valor_final_venda = (
                            preco_com_desconto
                            + valor_comissao
                        )

                        lucro = (
                            valor_final_venda
                            - custo_total
                        )

                        valor_por_convidado = (
                            valor_final_venda
                            / num_convidados
                            if num_convidados > 0
                            else 0
                        )

                        valor_por_hora = (
                            valor_final_venda
                            / horas
                            if horas > 0
                            else 0
                        )

                        margem_real = (
                            lucro
                            / valor_final_venda
                            * 100
                            if valor_final_venda > 0
                            else 0
                        )

                        st.divider()
                        st.subheader("📊 Resumo Financeiro")

                        col1, col2, col3, col4 = st.columns(4)

                        col1.metric(
                            "💰 Custo Orçado",
                            f"R$ {custo_total:,.2f}",
                        )

                        col2.metric(
                            "📈 Venda",
                            f"R$ {preco_com_desconto:,.2f}",
                        )

                        col3.metric(
                            "💵 Lucro Orçado",
                            f"R$ {lucro:,.2f}",
                        )

                        col4.metric(
                            "🤝 Comissão",
                            f"R$ {valor_comissao:,.2f}",
                        )

                        st.metric(
                            "🏆 VALOR FINAL DO ORÇAMENTO",
                            f"R$ {valor_final_venda:,.2f}",
                        )

                        col1, col2, col3 = st.columns(3)

                        col1.metric(
                            "🔻 Desconto",
                            f"R$ {valor_desconto:,.2f}",
                            f"{desconto}%",
                        )

                        col2.metric(
                            "👤 Valor por convidado",
                            f"R$ {valor_por_convidado:,.2f}",
                        )

                        col3.metric(
                            "⏱️ Valor por hora",
                            f"R$ {valor_por_hora:,.2f}",
                        )

                        if lucro < 0:
                            st.error(
                                f"⚠️ Prejuízo estimado: "
                                f"R$ {lucro:,.2f}"
                            )
                        else:
                            st.success(
                                f"✅ Lucro estimado: "
                                f"R$ {lucro:,.2f}"
                            )

                        st.info(
                            f"📈 Margem estimada: "
                            f"**{margem_real:.1f}%**"
                        )

                        _secao_orcamento(
                            "6️⃣",
                            "Apresentação ao Cliente",
                            "Visão comercial limpa: carta, dados do evento e investimento final, sem custo, margem ou lucro interno.",
                            "👁️",
                        )

                        with st.expander("👁️ Modo Cliente / Prévia", expanded=False):
                            st.markdown(f"## 🍸 Proposta para {nome_cliente or 'Cliente'}")
                            st.write(
                                f"**Evento:** {tipo_evento}  |  "
                                f"**Data:** {data_evento}  |  "
                                f"**Local:** {cidade_evento or endereco}"
                            )
                            st.write(f"**Convidados:** {num_convidados}")
                            st.markdown("### Carta de Drinks")
                            for drink_cliente in selecao:
                                st.write(f"• {drink_cliente}")
                            st.markdown("### Investimento")
                            st.metric(
                                "VALOR FINAL",
                                f"R$ {valor_final_venda:,.2f}",
                            )
                            if valor_por_convidado > 0:
                                st.caption(
                                    f"Referência por convidado: "
                                    f"R$ {valor_por_convidado:,.2f}"
                                )
                            st.caption("Validade da proposta: 7 dias.")

                        dados_proposta = {
                            "cliente": nome_cliente,
                            "tipo_evento": tipo_evento,
                            "data": str(data_evento),
                            "local": cidade_evento or endereco,
                            "convidados": num_convidados,
                            "horas": horas,
                            "drinks": list(selecao),
                            "valor_final": valor_final_venda,
                            "valor_por_convidado": valor_por_convidado,
                        }
                        pdf_proposta, erro_pdf_proposta = _gerar_pdf_proposta_cliente(
                            dados_proposta
                        )
                        if pdf_proposta:
                            st.download_button(
                                "📄 Baixar Proposta Comercial PDF",
                                data=pdf_proposta,
                                file_name=(
                                    f"proposta_{_safe_key(nome_cliente or 'cliente')}.pdf"
                                ),
                                mime="application/pdf",
                                key="orc_pdf_proposta_cliente",
                                use_container_width=True,
                            )
                        elif erro_pdf_proposta:
                            st.caption(erro_pdf_proposta)

                        # =============================================
                        # SALVAR ORÇAMENTO
                        # =============================================

                        if st.button(
                            "💾 Salvar orçamento",
                            key="salvar_bar_completo",
                            use_container_width=True,
                        ):

                            if not nome_cliente.strip():
                                st.error(
                                    "Informe o nome do cliente."
                                )

                            elif not selecao:
                                st.error(
                                    "Selecione pelo menos um drink."
                                )

                            elif pendencias_ingredientes:
                                st.error(
                                    "Corrija os ingredientes não encontrados "
                                    "antes de salvar o orçamento."
                                )

                            elif erros_calculo:
                                st.error(
                                    "Corrija os cadastros destacados "
                                    "antes de salvar o orçamento."
                                )

                            elif not itens_orcamento:
                                st.error(
                                    "O orçamento não possui itens "
                                    "operacionais para salvar."
                                )

                            else:
                                evento_id = None

                                try:
                                    texto_drinks = "\n".join(
                                        map(str, selecao)
                                    )

                                    response = (
                                        supabase.table("eventos")
                                        .insert({
                                            "cliente":
                                                nome_cliente.strip(),

                                            "data":
                                                str(data_evento),

                                            "cidade":
                                                cidade_evento.strip(),

                                            "telefone":
                                                telefone.strip(),

                                            "endereco":
                                                endereco.strip(),

                                            "tipo_evento":
                                                tipo_evento,

                                            "modalidade":
                                                "Bar Completo",

                                            "hora_chegada":
                                                str(hora_chegada),

                                            "hora_inicio":
                                                str(hora_inicio),

                                            "hora_convidados":
                                                str(hora_convidados),

                                            "convidados":
                                                int(num_convidados),

                                            "custo":
                                                float(custo_total),

                                            "venda":
                                                float(
                                                    valor_final_venda
                                                ),

                                            "comissao_percentual":
                                                float(
                                                    percentual_comissao
                                                ),

                                            "comissao_valor":
                                                float(
                                                    valor_comissao
                                                ),

                                            "equipe":
                                                nomes_equipe,

                                            "status":
                                                "pendente",

                                            "drinks":
                                                texto_drinks,
                                        })
                                        .execute()
                                    )

                                    evento_id = int(
                                        response.data[0]["id"]
                                    )

                                    payload_itens = []

                                    for item in itens_orcamento:
                                        quantidade_item = float(
                                            item.get(
                                                "quantidade",
                                                0,
                                            )
                                            or 0
                                        )

                                        if quantidade_item <= 0:
                                            continue

                                        payload_itens.append({
                                            "evento_id": evento_id,
                                            "produto": str(item["produto"]),
                                            "quantidade": quantidade_item,
                                            "unidade": str(item["unidade"]),
                                            "categoria": str(item["categoria"]),
                                            "tipo_base": str(item.get("tipo_base", "") or ""),
                                            "produto_ref_id": item.get("produto_ref_id"),
                                            "quantidade_base": float(
                                                item.get("quantidade_base", 0) or 0
                                            ),
                                            "preco_unitario": float(
                                                item.get("preco_unitario", 0) or 0
                                            ),
                                            "custo_unitario_operacional": float(
                                                item.get("custo_unitario_operacional", 0) or 0
                                            ),
                                            "custo_estimado": float(
                                                item.get("custo_estimado", 0) or 0
                                            ),
                                        })

                                    if not payload_itens:
                                        raise ValueError(
                                            "Nenhum item válido "
                                            "foi gerado para o checklist."
                                        )

                                    supabase.table(
                                        "evento_itens"
                                    ).insert(
                                        payload_itens
                                    ).execute()

                                    st.success(
                                        "✅ Orçamento salvo com sucesso! "
                                        "O checklist foi criado com os "
                                        "mesmos itens exibidos acima."
                                    )

                                    _limpar_estado_calculo_orcamento()
                                    st.session_state["orc_itens_manuais"] = []

                                    st.rerun()

                                except Exception as e:
                                    # Evita deixar evento incompleto
                                    # caso a gravação dos itens falhe.
                                    if evento_id is not None:
                                        try:
                                            supabase.table(
                                                "evento_itens"
                                            ).delete().eq(
                                                "evento_id",
                                                evento_id,
                                            ).execute()

                                            supabase.table(
                                                "eventos"
                                            ).delete().eq(
                                                "id",
                                                evento_id,
                                            ).execute()

                                        except Exception:
                                            pass

                                    st.error(
                                        f"❌ Erro ao salvar orçamento: {e}"
                                    )

        with tab_mao_obra:
        
            st.subheader("👷 Serviço Personalizado")
        
            # =========================
            # DADOS DO EVENTO
            # =========================
        
            st.subheader("👥 Equipe")
        
            nomes_equipe = st.text_area(
                "Nomes da equipe (um por linha)",
                key="sp_equipe"
            )
        
            col1, col2 = st.columns(2)
        
            hora_chegada = col1.time_input(
                "🕒 Chegada da equipe",
                key="sp_chegada"
            )
        
            hora_inicio = col2.time_input(
                "🍸 Início do serviço",
                key="sp_inicio"
            )
        
            hora_convidados = st.time_input(
                "👥 Chegada dos convidados",
                key="sp_convidados"
            )
        
            tipo_evento_sp = st.selectbox(
                "🎉 Tipo de evento",
                [
                    "Casamento",
                    "Aniversário",
                    "Corporativo",
                    "Festa privada",
                    "Outro"
                ],
                key="sp_tipo"
            )
        
            st.divider()
        
            # =========================
            # PROFISSIONAIS
            # =========================
        
            st.subheader("👷 Profissionais")
        
            qtd_pessoas = st.number_input(
                "Quantidade de profissionais",
                min_value=1,
                max_value=20,
                value=3,
                key="sp_qtd"
            )
        
            total_mao_obra = 0
        
            for i in range(qtd_pessoas):
        
                st.markdown(f"#### Profissional {i+1}")
        
                col1, col2, col3 = st.columns(3)
        
                nome = col1.text_input(
                    "Nome",
                    key=f"sp_nome_{i}"
                )
        
                funcao = col2.selectbox(
                    "Função",
                    [
                        "Bartender",
                        "Barback",
                        "Líder",
                        "Garçom",
                        "Recepcionista",
                        "Auxiliar"
                    ],
                    key=f"sp_funcao_{i}"
                )
        
                valor = col3.number_input(
                    "Valor",
                    min_value=0.0,
                    value=250.0,
                    step=10.0,
                    key=f"sp_valor_{i}"
                )
        
                total_mao_obra += valor
        
            st.metric(
                "💰 Total da Mão de Obra",
                f"R$ {total_mao_obra:,.2f}"
            )
        
            st.divider()
        
            # =========================
            # LOCAÇÕES
            # =========================
        
            st.subheader("🥂 Locações")
        
            col1, col2 = st.columns(2)
        
            valor_copos = col1.number_input(
                "🍸 Locação de Copos",
                min_value=0.0,
                value=0.0
            )
        
            valor_tacas = col2.number_input(
                "🥂 Locação de Taças",
                min_value=0.0,
                value=0.0
            )
        
            valor_decoracao = st.number_input(
                "🎉 Decoração do Bar",
                min_value=0.0,
                value=0.0
            )
        
            st.divider()
        
            # =========================
            # CUSTOS EXTRAS
            # =========================
        
            st.subheader("💸 Custos Extras")
        
            transporte = st.number_input(
                "🚚 Transporte",
                min_value=0.0,
                value=0.0
            )
        
            outros = st.number_input(
                "📦 Outros Custos",
                min_value=0.0,
                value=0.0
            )
        
            custo_total = (
                total_mao_obra +
                valor_copos +
                valor_tacas +
                valor_decoracao +
                transporte +
                outros
            )
        
            st.metric(
                "💰 Custo Total",
                f"R$ {custo_total:,.2f}"
            )
        
            st.divider()
        
            # =========================
            # PRECIFICAÇÃO
            # =========================

            st.subheader("📈 Precificação")

            # Opção para zerar custo da mão de obra
            sem_custo_equipe = st.checkbox(
                "🚫 Ignorar custo de mão de obra neste orçamento (lançar cachês separadamente)",
                key="sp_sem_custo_equipe"
            )

            # Recalcula o custo_total dependendo do checkbox
            if sem_custo_equipe:
                custo_financeiro_real = (
                    valor_copos +
                    valor_tacas +
                    valor_decoracao +
                    transporte +
                    outros
                )
            else:
                custo_financeiro_real = custo_total

            margem = st.slider(
                "Margem de lucro (%)",
                0,
                300,
                100,
                key="sp_margem"
            )

            # O preço base de venda usa o custo total original (ou ajustado)
            preco_venda = custo_total * (1 + margem / 100)

            desconto = st.slider(
                "Desconto (%)",
                0,
                100,
                0,
                key="sp_desconto"
            )

            preco_com_desconto = preco_venda * (1 - desconto / 100)

            st.subheader("🤝 Comissão")

            incluir_comissao = st.checkbox(
                "Incluir comissão",
                key="sp_comissao"
            )

            valor_comissao = 0
            percentual_comissao = 0

            if incluir_comissao:

                percentual_comissao = st.number_input(
                    "Percentual (%)",
                    value=10.0,
                    key="sp_percentual"
                )

                valor_comissao = (
                    preco_com_desconto *
                    percentual_comissao / 100
                )

            valor_final_venda = preco_com_desconto + valor_comissao

            # Lucro agora desconta apenas o custo_financeiro_real
            lucro = valor_final_venda - custo_financeiro_real

            st.divider()

            st.subheader("📊 Resumo Financeiro")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "💰 Custo",
                    f"R$ {custo_financeiro_real:,.2f}"
                )

            with col2:
                st.metric(
                    "📈 Venda",
                    f"R$ {preco_com_desconto:,.2f}"
                )

            with col3:
                st.metric(
                    "💵 Lucro",
                    f"R$ {lucro:,.2f}"
                )

            with col4:
                st.metric(
                    "🤝 Comissão",
                    f"R$ {valor_comissao:,.2f}"
                )

            st.metric(
                "🏆 VALOR FINAL",
                f"R$ {valor_final_venda:,.2f}"
            )

            
            # =========================
            # SALVAR ORÇAMENTO
            # =========================
        
            if st.button(
                "💾 Salvar orçamento",
                key="salvar_servico_personalizado"
            ):
        
                response = supabase.table("eventos").insert({
        
                    "cliente": nome_cliente,
                    "data": str(data_evento),
                    "cidade": cidade_evento,
                    "telefone": telefone,
                    "endereco": endereco,
        
                    "tipo_evento": tipo_evento_sp,
                    "modalidade": "Serviço Personalizado",
        
                    "hora_chegada": str(hora_chegada),
                    "hora_inicio": str(hora_inicio),
                    "hora_convidados": str(hora_convidados),
        
                    "convidados": 0,
        
                    "custo": custo_total,
                    "venda": valor_final_venda,
        
                    "comissao_percentual": percentual_comissao,
                    "comissao_valor": valor_comissao,
        
                    "equipe": nomes_equipe,
        
                    "status": "pendente"
        
                }).execute()
        
                evento_id = response.data[0]["id"]
        
                # EQUIPE
                for i in range(qtd_pessoas):
        
                    nome = st.session_state.get(f"sp_nome_{i}", "")
                    funcao = st.session_state.get(f"sp_funcao_{i}", "")
        
                    if nome.strip():
        
                        supabase.table("evento_itens").insert({
        
                            "evento_id": evento_id,
                            "produto": f"{funcao} - {nome}",
                            "quantidade": 1,
                            "unidade": "profissional",
                            "categoria": "Equipe"
        
                        }).execute()
        
                # LOCAÇÕES
                locacoes = {
                    "Copos": valor_copos,
                    "Taças": valor_tacas,
                    "Decoração": valor_decoracao
                }
        
                for nome, valor in locacoes.items():
        
                    if valor > 0:
        
                        supabase.table("evento_itens").insert({
        
                            "evento_id": evento_id,
                            "produto": nome,
                            "quantidade": valor,
                            "unidade": "R$",
                            "categoria": "Locação"
        
                        }).execute()
        
                # EXTRAS
                extras = {
                    "Transporte": transporte,
                    "Outros": outros
                }
        
                for nome, valor in extras.items():
        
                    if valor > 0:
        
                        supabase.table("evento_itens").insert({
        
                            "evento_id": evento_id,
                            "produto": nome,
                            "quantidade": valor,
                            "unidade": "R$",
                            "categoria": "Custos"
        
                        }).execute()
        
                st.success("✅ Orçamento salvo com sucesso!")

        # =========================================================
        # ABA 2 - PENDENTES / CHECKLIST
        # =========================================================
        with tab2:

            st.subheader("📋 Eventos Pendentes e Checklists")

            df_eventos = pd.DataFrame(
                supabase.table("eventos")
                .select("*")
                .eq("status", "pendente")
                .order("data", desc=False)
                .execute()
                .data or []
            )

            if df_eventos.empty:
                st.info("Nenhum orçamento pendente.")

            else:
                for _, row in df_eventos.iterrows():

                    evento_id = int(row["id"])

                    itens = pd.DataFrame(
                        supabase.table("evento_itens")
                        .select("*")
                        .eq("evento_id", evento_id)
                        .execute()
                        .data or []
                    )

                    modalidade = str(
                        row.get("modalidade", "Bar Completo")
                        or "Bar Completo"
                    )

                    icone = (
                        "🍸"
                        if modalidade == "Bar Completo"
                        else "👷"
                    )

                    st.markdown(
                        f"### {icone} "
                        f"{row.get('cliente', 'Sem cliente')}"
                    )

                    st.caption(
                        f"📅 {row.get('data', '')} | "
                        f"📍 {row.get('cidade', '')} | "
                        f"🆔 Evento #{evento_id} | "
                        "🟡 PENDENTE"
                    )

                    c1, c2, c3 = st.columns(3)

                    c1.metric(
                        "💰 Venda",
                        f"R$ {float(row.get('venda', 0) or 0):,.2f}",
                    )

                    c2.metric(
                        "💸 Custo Orçado",
                        f"R$ {float(row.get('custo', 0) or 0):,.2f}",
                    )

                    c3.metric(
                        "📈 Lucro Orçado",
                        f"R$ {(
                            float(row.get('venda', 0) or 0)
                            - float(row.get('custo', 0) or 0)
                        ):,.2f}",
                    )

                    chave_abrir = f"orc_pendente_aberto_{evento_id}"

                    if chave_abrir not in st.session_state:
                        st.session_state[chave_abrir] = False

                    if st.button(
                        "📋 Abrir Checklist",
                        key=f"orc_abrir_pendente_{evento_id}",
                    ):
                        st.session_state[chave_abrir] = (
                            not st.session_state[chave_abrir]
                        )

                    if st.session_state[chave_abrir]:

                        st.divider()
                        st.markdown("## 📍 Informações do Evento")

                        info1, info2, info3 = st.columns(3)

                        info1.write(
                            f"**👤 Cliente:** "
                            f"{row.get('cliente', '')}"
                        )
                        info1.write(
                            f"**📞 Telefone:** "
                            f"{row.get('telefone', '')}"
                        )
                        info1.write(
                            f"**🎉 Tipo:** "
                            f"{row.get('tipo_evento', '')}"
                        )

                        info2.write(
                            f"**📅 Data:** "
                            f"{row.get('data', '')}"
                        )
                        info2.write(
                            f"**📍 Cidade:** "
                            f"{row.get('cidade', '')}"
                        )
                        info2.write(
                            f"**🏠 Endereço:** "
                            f"{row.get('endereco', '')}"
                        )

                        info3.write(
                            f"**🕒 Chegada equipe:** "
                            f"{row.get('hora_chegada', '')}"
                        )
                        info3.write(
                            f"**🍸 Início:** "
                            f"{row.get('hora_inicio', '')}"
                        )
                        info3.write(
                            f"**👥 Convidados:** "
                            f"{row.get('convidados', 0)}"
                        )

                        st.markdown("## 🍸 Carta de Drinks")

                        drinks_evento = str(
                            row.get("drinks", "") or ""
                        )

                        lista_drinks = [
                            d.strip()
                            for d in drinks_evento.split("\n")
                            if d.strip()
                        ]

                        if lista_drinks:
                            for drink in lista_drinks:
                                st.write(f"☐ {drink}")
                        else:
                            st.info("Nenhum drink cadastrado.")

                        st.divider()
                        st.markdown("## 📦 Checklist Operacional")

                        _renderizar_checklist_evento(
                            evento_id,
                            itens,
                            "orc_check_pendente",
                            evento=row.to_dict(),
                        )

                    st.divider()

                    col_aprovar, col_excluir = st.columns(2)

                    if col_aprovar.button(
                        "✅ Aprovar",
                        key=f"orc_aprovar_{evento_id}",
                        use_container_width=True,
                    ):
                        try:
                            supabase.table("eventos").update({
                                "status": "aprovado"
                            }).eq(
                                "id",
                                evento_id,
                            ).execute()

                            valor_venda = float(
                                row.get("venda", 0) or 0
                            )

                            custo = float(
                                row.get("custo", 0) or 0
                            )

                            venda_existente = (
                                supabase.table("vendas")
                                .select("id")
                                .eq("evento_id", evento_id)
                                .execute()
                                .data
                                or []
                            )

                            dados_venda = {
                                "evento_id": evento_id,
                                "cliente": row.get(
                                    "cliente",
                                    "",
                                ),
                                "data": row.get(
                                    "data",
                                    "",
                                ),
                                "valor_venda": valor_venda,
                                "custo": custo,
                                "lucro": (
                                    valor_venda
                                    - custo
                                ),
                            }

                            if venda_existente:
                                supabase.table(
                                    "vendas"
                                ).update(
                                    dados_venda
                                ).eq(
                                    "evento_id",
                                    evento_id,
                                ).execute()
                            else:
                                supabase.table(
                                    "vendas"
                                ).insert(
                                    dados_venda
                                ).execute()

                            st.success(
                                "✅ Evento aprovado e venda registrada!"
                            )
                            st.rerun()

                        except Exception as e:
                            st.error(
                                f"Erro ao aprovar evento: {e}"
                            )

                    if col_excluir.button(
                        "🗑 Excluir",
                        key=f"orc_excluir_{evento_id}",
                        use_container_width=True,
                    ):
                        try:
                            supabase.table(
                                "evento_itens"
                            ).delete().eq(
                                "evento_id",
                                evento_id,
                            ).execute()

                            supabase.table(
                                "eventos"
                            ).delete().eq(
                                "id",
                                evento_id,
                            ).execute()

                            st.success(
                                "🗑 Evento excluído com sucesso!"
                            )
                            st.rerun()

                        except Exception as e:
                            st.error(
                                f"Erro ao excluir evento: {e}"
                            )

                    st.divider()

        # =========================================================
        # ABA 3 - APROVADOS
        # =========================================================
        with tab3:

            st.subheader("✅ Eventos Aprovados")

            df_eventos = pd.DataFrame(
                supabase.table("eventos")
                .select("*")
                .eq("status", "aprovado")
                .order("data", desc=False)
                .execute()
                .data or []
            )

            if df_eventos.empty:
                st.info("Nenhum evento aprovado.")

            else:
                for _, row in df_eventos.iterrows():

                    evento_id = int(row["id"])

                    itens = pd.DataFrame(
                        supabase.table("evento_itens")
                        .select("*")
                        .eq("evento_id", evento_id)
                        .execute()
                        .data or []
                    )

                    modalidade = str(
                        row.get("modalidade", "Bar Completo")
                        or "Bar Completo"
                    )

                    icone = (
                        "🍸"
                        if modalidade == "Bar Completo"
                        else "👷"
                    )

                    st.markdown(
                        f"### {icone} "
                        f"{row.get('cliente', 'Sem cliente')}"
                    )

                    st.caption(
                        f"📅 {row.get('data', '')} | "
                        f"📍 {row.get('cidade', '')} | "
                        f"🆔 Evento #{evento_id}"
                    )

                    col_edit, col_check = st.columns(2)

                    chave_editar = (
                        f"orc_editar_aprovado_{evento_id}"
                    )

                    if chave_editar not in st.session_state:
                        st.session_state[chave_editar] = False

                    if col_edit.button(
                        "✏️ Editar Evento",
                        key=f"orc_btn_edit_{evento_id}",
                        use_container_width=True,
                    ):
                        st.session_state[chave_editar] = (
                            not st.session_state[chave_editar]
                        )

                    chave_check = (
                        f"orc_check_aprovado_aberto_{evento_id}"
                    )

                    if chave_check not in st.session_state:
                        st.session_state[chave_check] = False

                    if col_check.button(
                        "📋 Checklist",
                        key=f"orc_btn_check_{evento_id}",
                        use_container_width=True,
                    ):
                        st.session_state[chave_check] = (
                            not st.session_state[chave_check]
                        )

                    if st.session_state[chave_editar]:

                        st.divider()
                        st.markdown(
                            "## ✏️ Editar informações do evento"
                        )

                        col1, col2 = st.columns(2)

                        novo_cliente = col1.text_input(
                            "👤 Cliente",
                            value=str(
                                row.get("cliente", "")
                                or ""
                            ),
                            key=f"orc_edit_cliente_{evento_id}",
                        )

                        nova_data = col1.text_input(
                            "📅 Data",
                            value=str(
                                row.get("data", "")
                                or ""
                            ),
                            key=f"orc_edit_data_{evento_id}",
                        )

                        nova_cidade = col1.text_input(
                            "📍 Cidade",
                            value=str(
                                row.get("cidade", "")
                                or ""
                            ),
                            key=f"orc_edit_cidade_{evento_id}",
                        )

                        novo_telefone = col1.text_input(
                            "📞 Telefone",
                            value=str(
                                row.get("telefone", "")
                                or ""
                            ),
                            key=f"orc_edit_tel_{evento_id}",
                        )

                        novo_endereco = col1.text_input(
                            "🏠 Endereço",
                            value=str(
                                row.get("endereco", "")
                                or ""
                            ),
                            key=f"orc_edit_end_{evento_id}",
                        )

                        novo_tipo = col2.text_input(
                            "🎉 Tipo de evento",
                            value=str(
                                row.get("tipo_evento", "")
                                or ""
                            ),
                            key=f"orc_edit_tipo_{evento_id}",
                        )

                        nova_hora_chegada = col2.text_input(
                            "🕒 Chegada equipe",
                            value=str(
                                row.get("hora_chegada", "")
                                or ""
                            ),
                            key=f"orc_edit_chegada_{evento_id}",
                        )

                        nova_hora_inicio = col2.text_input(
                            "🍸 Início serviço",
                            value=str(
                                row.get("hora_inicio", "")
                                or ""
                            ),
                            key=f"orc_edit_inicio_{evento_id}",
                        )

                        nova_hora_convidados = col2.text_input(
                            "👥 Chegada convidados",
                            value=str(
                                row.get("hora_convidados", "")
                                or ""
                            ),
                            key=f"orc_edit_hconvidados_{evento_id}",
                        )

                        novos_convidados = col2.number_input(
                            "👥 Nº convidados",
                            min_value=0,
                            value=int(
                                row.get("convidados", 0)
                                or 0
                            ),
                            step=1,
                            key=f"orc_edit_qtd_convidados_{evento_id}",
                        )

                        novo_valor_venda = st.number_input(
                            "💰 Valor de venda",
                            min_value=0.0,
                            value=float(
                                row.get("venda", 0)
                                or 0
                            ),
                            step=50.0,
                            format="%.2f",
                            key=f"orc_edit_venda_{evento_id}",
                        )

                        nova_equipe = st.text_area(
                            "👥 Equipe",
                            value=str(
                                row.get("equipe", "")
                                or ""
                            ),
                            key=f"orc_edit_equipe_{evento_id}",
                        )

                        st.markdown("### 🍸 Carta de Drinks")

                        st.text_area(
                            "Drinks do orçamento",
                            value=str(
                                row.get("drinks", "")
                                or ""
                            ),
                            disabled=True,
                            key=f"orc_edit_drinks_view_{evento_id}",
                            help=(
                                "A carta fica bloqueada aqui para evitar "
                                "desalinhamento entre drinks e checklist. "
                                "As quantidades dos itens podem ser ajustadas abaixo."
                            ),
                        )

                        st.markdown(
                            "### 📦 Produtos e quantidades"
                        )

                        if itens.empty:
                            df_itens_editado = pd.DataFrame()
                            st.info(
                                "Nenhum item cadastrado."
                            )

                        else:
                            cols = [
                                c
                                for c in [
                                    "id",
                                    "categoria",
                                    "produto",
                                    "quantidade",
                                    "unidade",
                                ]
                                if c in itens.columns
                            ]

                            editor = itens[cols].copy().rename(
                                columns={
                                    "id": "ID",
                                    "categoria": "Categoria",
                                    "produto": "Produto",
                                    "quantidade": "Quantidade",
                                    "unidade": "Unidade",
                                }
                            )

                            df_itens_editado = st.data_editor(
                                editor,
                                use_container_width=True,
                                hide_index=True,
                                disabled=[
                                    "ID",
                                    "Categoria",
                                    "Unidade",
                                ],
                                column_config={
                                    "Quantidade":
                                        st.column_config.NumberColumn(
                                            min_value=0.0,
                                            format="%.3f",
                                        )
                                },
                                key=f"orc_edit_itens_{evento_id}",
                            )

                        if st.button(
                            "💾 Salvar alterações",
                            key=f"orc_salvar_edit_{evento_id}",
                            use_container_width=True,
                        ):
                            try:
                                supabase.table(
                                    "eventos"
                                ).update({
                                    "cliente":
                                        novo_cliente,

                                    "data":
                                        nova_data,

                                    "cidade":
                                        nova_cidade,

                                    "telefone":
                                        novo_telefone,

                                    "endereco":
                                        novo_endereco,

                                    "tipo_evento":
                                        novo_tipo,

                                    "hora_chegada":
                                        nova_hora_chegada,

                                    "hora_inicio":
                                        nova_hora_inicio,

                                    "hora_convidados":
                                        nova_hora_convidados,

                                    "convidados":
                                        int(
                                            novos_convidados
                                        ),

                                    "venda":
                                        float(
                                            novo_valor_venda
                                        ),

                                    "equipe":
                                        nova_equipe,
                                }).eq(
                                    "id",
                                    evento_id,
                                ).execute()

                                if (
                                    not itens.empty
                                    and not df_itens_editado.empty
                                ):
                                    for _, item in (
                                        df_itens_editado.iterrows()
                                    ):
                                        supabase.table(
                                            "evento_itens"
                                        ).update({
                                            "produto":
                                                str(
                                                    item.get(
                                                        "Produto",
                                                        "",
                                                    )
                                                ),

                                            "quantidade":
                                                float(
                                                    item.get(
                                                        "Quantidade",
                                                        0,
                                                    )
                                                    or 0
                                                ),
                                        }).eq(
                                            "id",
                                            int(
                                                item["ID"]
                                            ),
                                        ).execute()

                                venda_existente = (
                                    supabase.table("vendas")
                                    .select("id")
                                    .eq(
                                        "evento_id",
                                        evento_id,
                                    )
                                    .execute()
                                    .data
                                    or []
                                )

                                if venda_existente:
                                    custo_orcado = float(
                                        row.get("custo", 0)
                                        or 0
                                    )

                                    supabase.table(
                                        "vendas"
                                    ).update({
                                        "cliente":
                                            novo_cliente,

                                        "data":
                                            nova_data,

                                        "valor_venda":
                                            float(
                                                novo_valor_venda
                                            ),

                                        "lucro":
                                            float(
                                                novo_valor_venda
                                            )
                                            - custo_orcado,
                                    }).eq(
                                        "evento_id",
                                        evento_id,
                                    ).execute()

                                st.success(
                                    "✅ Evento atualizado!"
                                )

                                st.session_state[
                                    chave_editar
                                ] = False

                                st.rerun()

                            except Exception as e:
                                st.error(
                                    f"Erro ao salvar: {e}"
                                )

                    if st.session_state[chave_check]:

                        st.divider()

                        st.markdown(
                            "## 📦 Checklist Operacional"
                        )

                        _renderizar_checklist_evento(
                            evento_id,
                            itens,
                            "orc_check_aprovado",
                            evento=row.to_dict(),
                        )

                    if st.button(
                        "✔ Finalizar Evento",
                        key=f"orc_finalizar_{evento_id}",
                        use_container_width=True,
                    ):
                        try:
                            supabase.table(
                                "eventos"
                            ).update({
                                "status": "finalizado"
                            }).eq(
                                "id",
                                evento_id,
                            ).execute()

                            st.success(
                                "✅ Evento finalizado!"
                            )

                            st.rerun()

                        except Exception as e:
                            st.error(
                                f"Erro ao finalizar: {e}"
                            )

elif menu == "Cachês":

    st.title("👥 Gestão de Cachês")

    subaba = st.radio(
        "Escolha a visão",
        ["Resumo", "Por Pessoa", "Histórico", "Consolidado"],
        horizontal=True,
    )

    st.divider()

    # =====================================
    # CONFIGURAÇÕES DE CACHÊ (Valores Padrão)
    # =====================================
    if subaba in ["Resumo", "Por Pessoa"]:
        st.subheader("⚙️ Configuração dos Cachês Base")

        col1, col2, col3 = st.columns(3)
        valor_bartender = col1.number_input(
            "🍸 Bartender", min_value=0.0, value=250.00, step=10.0
        )
        valor_barback = col2.number_input(
            "🧰 Barback", min_value=0.0, value=180.00, step=10.0
        )
        valor_lider = col3.number_input(
            "👑 Líder", min_value=0.0, value=300.00, step=10.0
        )

        col1, col2 = st.columns(2)
        limite_horas = col1.number_input(
            "⏱ Horas inclusas no cachê base",
            min_value=1.0,
            value=7.0,
            step=0.5,
        )
        valor_hora_extra = col2.number_input(
            "💰 Valor Hora Extra (padrão)",
            min_value=0.0,
            value=40.0,
            step=5.0,
        )

        st.divider()

    # =====================================
    # SUBABA 1: RESUMO (Simulador)
    # =====================================
    if subaba == "Resumo":
        st.subheader("📊 Simulação de Custos de Equipe")

        col1, col2, col3 = st.columns(3)
        qtd_bartenders = col1.number_input("Bartenders", min_value=0, value=2)
        qtd_barbacks = col2.number_input("Barbacks", min_value=0, value=1)
        qtd_lideres = col3.number_input(
            "Líderes", min_value=0, max_value=5, value=1
        )

        st.divider()

        col1, col2, col3 = st.columns(3)
        horas_evento = col1.number_input(
            "Horas do Evento", min_value=1.0, value=7.0, step=0.5
        )
        pessoas_carro = col2.number_input(
            "Pessoas com Carro", min_value=0, value=1
        )
        ajuda_carro = col3.number_input(
            "Ajuda de Custo/Carro", min_value=0.0, value=100.0
        )

        total_base = (
            (qtd_bartenders * valor_bartender)
            + (qtd_barbacks * valor_barback)
            + (qtd_lideres * valor_lider)
        )
        horas_extra = max(0.0, horas_evento - limite_horas)
        total_horas = (
            horas_extra
            * valor_hora_extra
            * (qtd_bartenders + qtd_barbacks + qtd_lideres)
        )
        total_carro = pessoas_carro * ajuda_carro
        total_final = total_base + total_horas + total_carro

        st.divider()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Base Equipe", f"R$ {total_base:,.2f}")
        c2.metric("Horas Extras", f"R$ {total_horas:,.2f}")
        c3.metric("Ajuda de Custo", f"R$ {total_carro:,.2f}")
        c4.metric("CUSTO TOTAL ESTIMADO", f"R$ {total_final:,.2f}")

        st.info(
            "💡 Dica: Utilize esses valores para compor a proposta comercial do evento."
        )

    # =====================================
    # SUBABA 2: POR PESSOA (Lançamento de Pagamentos)
    # =====================================
    elif subaba == "Por Pessoa":
        st.subheader("👤 Lançamento de Pagamentos por Profissional")

        # Busca os eventos para vincular evento_id
        eventos_db = []
        try:
            eventos_db = (
                supabase.table("eventos")
                .select("id, cliente, data")
                .execute()
                .data
                or []
            )
        except Exception:
            pass

        col1, col2 = st.columns([3, 1])

        if eventos_db:
            opcoes_evt = {
                f"{e.get('cliente', 'Evento')} ({e.get('data', '')})": e
                for e in eventos_db
            }
            evt_sel_nome = col1.selectbox(
                "Selecione o Evento", list(opcoes_evt.keys())
            )
            evento_obj = opcoes_evt[evt_sel_nome]

            # Converte o ID para int de forma segura
            raw_id = evento_obj.get("id")
            evento_id_num = int(raw_id) if raw_id is not None else None
            evento_nome_ref = evt_sel_nome
        else:
            evento_nome_ref = col1.text_input(
                "Nome do Evento / Referência",
                placeholder="Ex.: Formatura Vitória",
            )
            evento_id_num = None

        qtd_pessoas = col2.number_input(
            "Qtd. Profissionais", min_value=1, max_value=30, value=2
        )

        st.divider()

        # Configuração de Pagamento (Status e Forma)
        st.subheader("💳 Status do Pagamento")
        c_st1, c_st2 = st.columns(2)
        ja_pago = c_st1.checkbox(
            "Marcar como JÁ PAGO", value=True
        )
        forma_pagto_padrao = c_st2.selectbox(
            "Forma de Pagamento",
            ["Pix", "Dinheiro", "Transferência", "Cartão"],
            disabled=not ja_pago,
        )

        st.divider()

        dados_pagamento = []
        total_geral = 0.0

        for i in range(int(qtd_pessoas)):
            st.markdown(f"#### 👤 Profissional {i+1}")

            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Profissional", key=f"nome_{i}")
            funcao = col2.selectbox(
                "Função",
                ["Bartender", "Barback", "Líder"],
                key=f"funcao_{i}",
            )

            col3a, col3b, col3c = st.columns(3)
            horas = col3a.number_input(
                "Horas Trabalhadas",
                min_value=1.0,
                value=7.0,
                step=0.5,
                key=f"horas_{i}",
            )
            horas_extras = col3b.number_input(
                "Horas Extras",
                min_value=0.0,
                value=0.0,
                step=0.5,
                key=f"horas_extra_{i}",
            )
            valor_hora_extra_ind = col3c.number_input(
                "Valor H. Extra",
                min_value=0.0,
                value=valor_hora_extra,
                step=5.0,
                key=f"valor_hextra_{i}",
            )

            if funcao == "Bartender":
                valor_base = valor_bartender
            elif funcao == "Barback":
                valor_base = valor_barback
            else:
                valor_base = valor_lider

            valor_horas_extras = horas_extras * valor_hora_extra_ind

            c1, c2, c3 = st.columns(3)
            utiliza_carro = c1.checkbox("Transporte / Carro", key=f"carro_{i}")
            ajuda_custo = c2.number_input(
                "Ajuda de Custo",
                min_value=0.0,
                value=100.0 if utiliza_carro else 0.0,
                step=10.0,
                disabled=not utiliza_carro,
                key=f"ajuda_{i}",
            )
            despesas = c3.number_input(
                "Despesas Diversas",
                min_value=0.0,
                value=0.0,
                step=10.0,
                key=f"despesas_{i}",
            )

            observacao = st.text_input(
                "Observação",
                placeholder="Ex.: Reembolso de Uber, etc.",
                key=f"obs_{i}",
            )

            pagamento = (
                valor_base + valor_horas_extras + ajuda_custo + despesas
            )

            m1, m2, m3 = st.columns(3)
            m1.metric("Cachê Base", f"R$ {valor_base:,.2f}")
            m2.metric(
                "Extras + Ajuda + Despesas",
                f"R$ {(valor_horas_extras + ajuda_custo + despesas):,.2f}",
            )
            m3.metric("TOTAL A RECEBER", f"R$ {pagamento:,.2f}")

            total_geral += pagamento

            if nome.strip():
                dados_pagamento.append({
                    "nome": nome.strip(),
                    "funcao": funcao,
                    "valor": pagamento,
                    "valor_base": valor_base,
                    "horas": horas,
                    "horas_extras": horas_extras,
                    "ajuda_custo": ajuda_custo,
                    "despesas": despesas,
                    "observacao": observacao,
                })

            st.divider()

        st.subheader(f"💰 Total Geral do Lançamento: R$ {total_geral:,.2f}")

        if st.button(
            "💾 Salvar Pagamentos no Supabase", use_container_width=True
        ):
            if not dados_pagamento:
                st.error("Preencha ao menos o nome de um profissional.")
                st.stop()

            try:
                agora_iso = datetime.now().isoformat()

                for pessoa in dados_pagamento:
                    status_final = "Pago" if ja_pago else "Pendente"
                    forma_final = forma_pagto_padrao if ja_pago else None
                    data_pagto_final = agora_iso if ja_pago else None

                    # Insere apenas na tabela pagamentos_equipe (sem duplicar no Financeiro)
                    payload_equipe = {
                        "evento_id": evento_id_num,
                        "evento": evento_nome_ref,
                        "nome": pessoa["nome"],
                        "funcao": pessoa["funcao"],
                        "valor": float(pessoa["valor"]),
                        "valor_base": float(pessoa["valor_base"]),
                        "horas": float(pessoa["horas"]),
                        "horas_extras": float(pessoa["horas_extras"]),
                        "ajuda_custo": float(pessoa["ajuda_custo"]),
                        "despesas": float(pessoa["despesas"]),
                        "observacao": pessoa["observacao"],
                        "status": status_final,
                        "forma_pagamento": forma_final,
                        "data_pagamento": data_pagto_final,
                    }
                    supabase.table("pagamentos_equipe").insert(
                        payload_equipe
                    ).execute()

                st.success(
                    f"✅ {len(dados_pagamento)} registro(s) salvo(s) com sucesso!"
                )
                st.rerun()

            except Exception as erro:
                st.error(f"Erro ao salvar registros: {erro}")

    # =========================================================
    # SUBABA 3: HISTÓRICO & BAIXA DE PAGAMENTOS
    # =========================================================
    elif subaba == "Histórico":
        st.subheader("📋 Histórico e Baixa de Pagamentos")

        res = supabase.table("pagamentos_equipe").select("*").execute()
        df_pagamentos = pd.DataFrame(res.data or [])

        if df_pagamentos.empty:
            st.info("Nenhum registro encontrado na tabela `pagamentos_equipe`.")
        else:
            if "created_at" in df_pagamentos.columns:
                df_pagamentos["created_at"] = pd.to_datetime(
                    df_pagamentos["created_at"]
                )

            col1, col2, col3 = st.columns(3)
            filtro_evento = col1.text_input("🔎 Filtrar por Evento")
            filtro_nome = col2.text_input("👤 Filtrar por Nome")
            filtro_status = col3.selectbox(
                "Status", ["Todos", "Pendente", "Pago"]
            )

            if filtro_evento:
                df_pagamentos = df_pagamentos[
                    df_pagamentos["evento"]
                    .astype(str)
                    .str.contains(filtro_evento, case=False, na=False)
                ]
            if filtro_nome:
                df_pagamentos = df_pagamentos[
                    df_pagamentos["nome"]
                    .astype(str)
                    .str.contains(filtro_nome, case=False, na=False)
                ]
            if filtro_status != "Todos":
                df_pagamentos = df_pagamentos[
                    df_pagamentos["status"] == filtro_status
                ]

            if "created_at" in df_pagamentos.columns and not df_pagamentos.empty:
                df_pagamentos = df_pagamentos.sort_values(
                    by="created_at", ascending=False
                )

            # Converter valores numéricos para garantir os somatórios corretos
            if not df_pagamentos.empty:
                df_pagamentos["valor"] = pd.to_numeric(df_pagamentos["valor"], errors="coerce").fillna(0)

            total_pago = (
                df_pagamentos[df_pagamentos["status"] == "Pago"]["valor"].sum()
                if not df_pagamentos.empty
                else 0
            )
            total_pendente = (
                df_pagamentos[df_pagamentos["status"] != "Pago"]["valor"].sum()
                if not df_pagamentos.empty
                else 0
            )
            total_registrado = (
                df_pagamentos["valor"].sum() if not df_pagamentos.empty else 0
            )

            c1, c2, c3 = st.columns(3)
            c1.metric("✅ Total Pago", f"R$ {total_pago:,.2f}")
            c2.metric("🟡 Total Pendente", f"R$ {total_pendente:,.2f}")
            c3.metric("📊 Total Registrado", f"R$ {total_registrado:,.2f}")

            st.divider()

            tabela = df_pagamentos.copy()
            for col in ["valor_base", "ajuda_custo", "despesas", "valor"]:
                if col in tabela.columns:
                    tabela[col] = tabela[col].apply(
                        lambda x: f"R$ {x:,.2f}" if pd.notnull(x) else "R$ 0.00"
                    )

            colunas_visiveis = [
                "id",
                "created_at",
                "evento",
                "nome",
                "funcao",
                "valor",
                "status",
                "forma_pagamento",
                "data_pagamento",
                "observacao",
            ]
            colunas_visiveis = [
                c for c in colunas_visiveis if c in tabela.columns
            ]

            st.dataframe(
                tabela[colunas_visiveis],
                use_container_width=True,
                hide_index=True,
            )

            st.divider()

            # DAR BAIXA NO PAGAMENTO
            st.subheader("💵 Dar Baixa em Pagamento Pendente")
            pendentes = df_pagamentos[df_pagamentos["status"] != "Pago"]

            if pendentes.empty:
                st.success("Não existem pagamentos pendentes no momento.")
            else:
                opcoes = pendentes.apply(
                    lambda x: f"ID #{x['id']} | {x['nome']} | {x['evento']} | R$ {x['valor']:.2f}",
                    axis=1,
                )
                selecionado = st.selectbox(
                    "Selecione o registro para confirmar pagamento", opcoes
                )

                linha = pendentes[opcoes == selecionado].iloc[0]

                col1, col2 = st.columns(2)
                forma = col1.selectbox(
                    "Forma de Pagamento",
                    ["Pix", "Dinheiro", "Transferência", "Cartão"],
                )
                obs_baixa = col2.text_input(
                    "Observação da Baixa",
                    value=linha.get("observacao") or "",
                )

                st.info(
                    f"**Confirmar pagamento de:** {linha['nome']} — **Valor:** R$ {linha['valor']:,.2f}"
                )

                if st.button("✅ Confirmar Pagamento", use_container_width=True):
                    agora_iso = datetime.now().isoformat()

                    # Atualiza status apenas na tabela pagamentos_equipe
                    supabase.table("pagamentos_equipe").update({
                        "status": "Pago",
                        "forma_pagamento": forma,
                        "observacao": obs_baixa,
                        "data_pagamento": agora_iso,
                    }).eq("id", linha["id"]).execute()

                    st.toast("✅ Pagamento confirmado com sucesso!", icon="🎉")
                    st.success("Pagamento confirmado com sucesso!")
                    st.rerun()

            st.divider()

            # 🗑️ SEÇÃO DE EXCLUSÃO SIMPLIFICADA
            with st.expander("🗑️ Área de Gerenciamento: Excluir Registro de Cachê", expanded=False):
                opcoes_exclusao = df_pagamentos.apply(
                    lambda x: f"ID #{x['id']} | {x['nome']} | Evento: {x['evento']} | R$ {x['valor']:.2f} ({x['status']})",
                    axis=1,
                )

                if not opcoes_exclusao.empty:
                    item_para_excluir = st.selectbox(
                        "Selecione o lançamento que deseja apagar:",
                        options=opcoes_exclusao,
                        key="select_del_cache"
                    )

                    linha_del = df_pagamentos[opcoes_exclusao == item_para_excluir].iloc[0]

                    st.info(f"📌 **Selecionado:** ID #{linha_del['id']} — {linha_del['nome']} ({linha_del['evento']}) — **R$ {linha_del['valor']:,.2f}**")

                    if st.button("❌ Excluir Lançamento Agora", type="primary", use_container_width=True):
                        try:
                            supabase.table("pagamentos_equipe").delete().eq("id", linha_del["id"]).execute()
                            st.toast(f"🗑️ O registro de {linha_del['nome']} foi excluído com sucesso!", icon="✅")
                            st.success(f"✅ Registro ID #{linha_del['id']} ({linha_del['nome']}) removido!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir registro: {e}")
    # =====================================
    # SUBABA 4: CONSOLIDADO & RELATÓRIOS
    # =====================================
    elif subaba == "Consolidado":
        st.subheader("📈 Consolidado e Estatísticas da Equipe")

        res = supabase.table("pagamentos_equipe").select("*").execute()
        df_pagamentos = pd.DataFrame(res.data or [])

        if df_pagamentos.empty:
            st.info("Nenhum dado cadastrado para consolidação.")
        else:
            total_geral = df_pagamentos["valor"].sum()
            total_pago = df_pagamentos[df_pagamentos["status"] == "Pago"][
                "valor"
            ].sum()
            total_pendente = df_pagamentos[df_pagamentos["status"] != "Pago"][
                "valor"
            ].sum()
            total_profissionais = df_pagamentos["nome"].nunique()
            total_eventos = df_pagamentos["evento"].nunique()

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("💰 Total Gasto", f"R$ {total_geral:,.2f}")
            c2.metric("✅ Total Pago", f"R$ {total_pago:,.2f}")
            c3.metric("🟡 Pendente", f"R$ {total_pendente:,.2f}")
            c4.metric("👥 Equipe (Únicos)", total_profissionais)
            c5.metric("🎉 Eventos", total_eventos)

            st.divider()

            # Ranking por Profissional
            st.subheader("🏆 Ranking e Histórico por Profissional")
            ranking = (
                df_pagamentos.groupby("nome", as_index=False)
                .agg(
                    Eventos=("evento", "nunique"),
                    Trabalhos=("id", "count"),
                    Total_Acumulado=("valor", "sum"),
                    Media_por_Trabalho=("valor", "mean"),
                )
                .sort_values(by="Total_Acumulado", ascending=False)
            )

            ranking["Total_Acumulado"] = ranking["Total_Acumulado"].apply(
                lambda x: f"R$ {x:,.2f}"
            )
            ranking["Media_por_Trabalho"] = ranking["Media_por_Trabalho"].apply(
                lambda x: f"R$ {x:,.2f}"
            )

            st.dataframe(ranking, use_container_width=True, hide_index=True)

            st.divider()

            # Detalhamento Individual
            st.subheader("🔍 Ficha Individual do Profissional")
            lista_nomes = sorted(df_pagamentos["nome"].unique())
            nome_selecionado = st.selectbox(
                "Selecione o profissional para ver o histórico completo",
                lista_nomes,
            )

            if nome_selecionado:
                df_ind = df_pagamentos[
                    df_pagamentos["nome"] == nome_selecionado
                ]
                tot_ind = df_ind["valor"].sum()
                pagos_ind = df_ind[df_ind["status"] == "Pago"]["valor"].sum()
                pend_ind = df_ind[df_ind["status"] != "Pago"]["valor"].sum()

                m1, m2, m3 = st.columns(3)
                m1.metric("Total Acumulado", f"R$ {tot_ind:,.2f}")
                m2.metric("Recebido (Pago)", f"R$ {pagos_ind:,.2f}")
                m3.metric("A Receber (Pendente)", f"R$ {pend_ind:,.2f}")

                st.dataframe(
                    df_ind[[
                        "evento",
                        "funcao",
                        "horas",
                        "valor",
                        "status",
                        "forma_pagamento",
                        "data_pagamento",
                        "observacao",
                    ]],
                    use_container_width=True,
                    hide_index=True,
                )
elif menu == "Vendas":

    st.title("📊 Vendas")

    # =========================================================
    # 1. CARREGA EVENTOS VÁLIDOS
    # =========================================================
    response_eventos = (
        supabase.table("eventos")
        .select("*")
        .in_("status", ["aprovado", "finalizado", "concluido", "pago"])
        .execute()
    )

    df_eventos = pd.DataFrame(response_eventos.data or [])

    # =========================================================
    # 2. CARREGA ADITIVOS / HORAS EXTRAS
    # =========================================================
    response_aditivos = (
        supabase.table("aditivos_evento")
        .select("*")
        .execute()
    )

    df_aditivos = pd.DataFrame(response_aditivos.data or [])

    # =========================================================
    # 3. PREPARAÇÃO DOS EVENTOS
    # =========================================================
    if not df_eventos.empty:

        # -----------------------------------------------------
        # VALOR BASE DO CONTRATO
        # -----------------------------------------------------
        if "venda" in df_eventos.columns:
            df_eventos["venda_base"] = pd.to_numeric(
                df_eventos["venda"],
                errors="coerce"
            ).fillna(0)
        else:
            df_eventos["venda_base"] = 0.0

        # -----------------------------------------------------
        # CUSTO REAL DO EVENTO
        # -----------------------------------------------------
        # Procura automaticamente a coluna de custo existente
        # na tabela eventos.
        coluna_custo = None

        for coluna in [
            "custo_total",
            "custo",
            "custo_evento",
            "valor_custo"
        ]:
            if coluna in df_eventos.columns:
                coluna_custo = coluna
                break

        if coluna_custo:
            df_eventos["custo_evento"] = pd.to_numeric(
                df_eventos[coluna_custo],
                errors="coerce"
            ).fillna(0)
        else:
            df_eventos["custo_evento"] = 0.0

        # =====================================================
        # 4. PROCESSA ADITIVOS / HORAS EXTRAS
        # =====================================================
        if (
            not df_aditivos.empty
            and "evento_id" in df_aditivos.columns
            and "valor_cliente" in df_aditivos.columns
        ):

            df_aditivos["valor_cliente"] = pd.to_numeric(
                df_aditivos["valor_cliente"],
                errors="coerce"
            ).fillna(0)

            aditivos_agrupados = (
                df_aditivos
                .groupby("evento_id")["valor_cliente"]
                .sum()
                .reset_index()
            )

            aditivos_agrupados.rename(
                columns={
                    "valor_cliente": "aditivos"
                },
                inplace=True
            )

            # Une os aditivos ao evento
            df = df_eventos.merge(
                aditivos_agrupados,
                left_on="id",
                right_on="evento_id",
                how="left"
            )

            df["aditivos"] = df["aditivos"].fillna(0)

        else:

            df = df_eventos.copy()
            df["aditivos"] = 0.0

        # =====================================================
        # 5. FATURAMENTO REAL
        # =====================================================
        # Contrato Base + Aditivos/Horas Extras
        df["faturamento"] = (
            df["venda_base"] +
            df["aditivos"]
        )

        # =====================================================
        # 6. LUCRO DE CADA EVENTO
        # =====================================================
        df["lucro"] = (
            df["faturamento"] -
            df["custo_evento"]
        )

        # =====================================================
        # 7. CAIXA PJ - 35% DO LUCRO DE CADA EVENTO
        # =====================================================
        df["caixa_pj"] = df["lucro"].apply(
            lambda x: x * 0.35 if x > 0 else 0
        )

        # =====================================================
        # 8. LUCRO REAL DE CADA EVENTO
        # =====================================================
        df["lucro_real"] = (
            df["lucro"] -
            df["caixa_pj"]
        )

    else:

        df = pd.DataFrame(columns=[
            "id",
            "cliente",
            "data",
            "venda_base",
            "aditivos",
            "faturamento",
            "custo_evento",
            "lucro",
            "caixa_pj",
            "lucro_real",
            "status"
        ])

    # =========================================================
    # 9. INDICADORES CONSOLIDADOS
    # =========================================================

    total_vendas = (
        df["faturamento"].sum()
        if not df.empty else 0.0
    )

    total_custo = (
        df["custo_evento"].sum()
        if not df.empty else 0.0
    )

    total_lucro = (
        df["lucro"].sum()
        if not df.empty else 0.0
    )

    total_caixa_pj = (
        df["caixa_pj"].sum()
        if not df.empty else 0.0
    )

    total_lucro_real = (
        df["lucro_real"].sum()
        if not df.empty else 0.0
    )

    margem = (
        total_lucro / total_vendas * 100
        if total_vendas > 0
        else 0.0
    )

    # =========================================================
    # 10. KPIs
    # =========================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💰 Receita Total",
        f"R$ {total_vendas:,.2f}"
    )

    col2.metric(
        "💸 Custo Total dos Eventos",
        f"R$ {total_custo:,.2f}"
    )

    col3.metric(
        "📈 Lucro Total",
        f"R$ {total_lucro:,.2f}"
    )

    col4.metric(
        "📊 Margem",
        f"{margem:.1f}%"
    )

    # =========================================================
    # 11. RESULTADO REAL
    # =========================================================

    st.divider()

    st.subheader("💰 Resultado Real")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "📈 Lucro Total dos Eventos",
        f"R$ {total_lucro:,.2f}"
    )

    c2.metric(
        "🛡️ Caixa PJ (35%)",
        f"R$ {total_caixa_pj:,.2f}"
    )

    c3.metric(
        "💵 Lucro Real",
        f"R$ {total_lucro_real:,.2f}"
    )

    # =========================================================
    # 12. FILTRO DE CLIENTE
    # =========================================================

    st.divider()

    cliente = st.text_input(
        "Buscar cliente"
    )

    df_filtrado = df.copy()

    if (
        cliente
        and not df_filtrado.empty
        and "cliente" in df_filtrado.columns
    ):
        df_filtrado = df_filtrado[
            df_filtrado["cliente"]
            .astype(str)
            .str.contains(
                cliente,
                case=False,
                na=False
            )
        ]

    # =========================================================
    # 13. TABELA DE VENDAS
    # =========================================================

    if not df_filtrado.empty:

        colunas_exibir = [
            "cliente",
            "data",
            "venda_base",
            "aditivos",
            "faturamento",
            "custo_evento",
            "lucro",
            "caixa_pj",
            "lucro_real",
            "status"
        ]

        # Só utiliza colunas que realmente existem
        colunas_exibir = [
            c for c in colunas_exibir
            if c in df_filtrado.columns
        ]

        df_exibir = df_filtrado[colunas_exibir].copy()

        st.dataframe(
            df_exibir,
            use_container_width=True,
            hide_index=True,
            column_config={

                "cliente":
                    st.column_config.TextColumn(
                        "🥂 Cliente"
                    ),

                "data":
                    st.column_config.DateColumn(
                        "📅 Data"
                    ),

                "venda_base":
                    st.column_config.NumberColumn(
                        "📋 Contrato Base",
                        format="R$ %.2f"
                    ),

                "aditivos":
                    st.column_config.NumberColumn(
                        "⏰ Aditivos",
                        format="R$ %.2f"
                    ),

                "faturamento":
                    st.column_config.NumberColumn(
                        "💰 Faturamento",
                        format="R$ %.2f"
                    ),

                "custo_evento":
                    st.column_config.NumberColumn(
                        "💸 Custo",
                        format="R$ %.2f"
                    ),

                "lucro":
                    st.column_config.NumberColumn(
                        "📈 Lucro",
                        format="R$ %.2f"
                    ),

                "caixa_pj":
                    st.column_config.NumberColumn(
                        "🛡️ Caixa PJ (35%)",
                        format="R$ %.2f"
                    ),

                "lucro_real":
                    st.column_config.NumberColumn(
                        "💵 Lucro Real",
                        format="R$ %.2f"
                    ),

                "status":
                    st.column_config.TextColumn(
                        "📌 Status"
                    ),
            }
        )

    else:

        st.warning(
            "Nenhuma venda registrada ainda — "
            "aparecerá ao aprovar/finalizar eventos."
        )

    # =========================================================
    # 14. GRÁFICO DE EVOLUÇÃO DAS VENDAS
    # =========================================================

    st.divider()

    st.subheader(
        "📊 Evolução das vendas "
        "(Valor Total com Aditivos)"
    )

    if not df_filtrado.empty and "data" in df_filtrado.columns:

        df_filtrado["data_dt"] = pd.to_datetime(
            df_filtrado["data"],
            errors="coerce"
        )

        vendas_por_data = (
            df_filtrado
            .dropna(subset=["data_dt"])
            .groupby(
                df_filtrado["data_dt"].dt.date
            )["faturamento"]
            .sum()
        )

        if not vendas_por_data.empty:
            st.line_chart(vendas_por_data)
        else:
            st.info(
                "Sem dados suficientes para gerar o gráfico."
            )

    else:

        st.info(
            "Sem dados ainda para o gráfico."
        )

elif menu == "CMV":

    st.title("📊 CMV — Custo Real dos Eventos")

    # ============================================================
    # CONFIGURAÇÕES
    # ============================================================

    status_eventos = ["aprovado", "finalizado", "concluido", "pago"]

    categorias_cmv = [
        "Bebidas",
        "Frutas",
        "Gelo",
        "Insumos",
        "Outros"
    ]

    # ============================================================
    # ABAS
    # ============================================================

    tab1, tab2, tab3 = st.tabs([
        "📋 Por Evento",
        "📊 Análise",
        "➕ Adendos"
    ])

    # ============================================================
    # TAB 1 — POR EVENTO
    # ============================================================

    with tab1:

        st.subheader("📋 Custo Real por Evento")

        try:

            # ----------------------------------------------------
            # CARREGA EVENTOS
            # ----------------------------------------------------

            resposta_eventos = (
                supabase
                .table("eventos")
                .select("*")
                .in_("status", status_eventos)
                .order("data", desc=True)
                .execute()
            )

            df_eventos_cmv = pd.DataFrame(resposta_eventos.data)

            if df_eventos_cmv.empty:

                st.info("Nenhum evento aprovado/finalizado encontrado.")

            else:

                for _, evento in df_eventos_cmv.iterrows():

                    evento_id = evento.get("id")
                    cliente = evento.get("cliente", "Evento sem cliente")
                    data_evento = evento.get("data")
                    valor_venda = float(evento.get("venda", 0) or 0)
                    custo_previsto = float(evento.get("custo", 0) or 0)

                    # ------------------------------------------------
                    # DATA
                    # ------------------------------------------------

                    if pd.notna(data_evento):

                        try:
                            data_formatada = pd.to_datetime(
                                data_evento
                            ).strftime("%d/%m/%Y")

                        except:
                            data_formatada = str(data_evento)

                    else:
                        data_formatada = "-"

                    # ------------------------------------------------
                    # CUSTOS REAIS DO EVENTO
                    # ------------------------------------------------

                    resposta_custos = (
                        supabase
                        .table("evento_custos")
                        .select("*")
                        .eq("evento_id", int(evento_id))
                        .execute()
                    )

                    df_custos = pd.DataFrame(resposta_custos.data)

                    if df_custos.empty:

                        total_custo_evento = 0.0

                    else:

                        total_custo_evento = pd.to_numeric(
                            df_custos["valor"],
                            errors="coerce"
                        ).fillna(0).sum()

                    # ------------------------------------------------
                    # ADENDOS DO EVENTO
                    # ------------------------------------------------

                    resposta_adendos = (
                        supabase
                        .table("aditivos_evento")
                        .select("*")
                        .eq("evento_id", int(evento_id))
                        .neq("status", "Cancelado")
                        .execute()
                    )

                    df_adendos = pd.DataFrame(resposta_adendos.data)

                    if df_adendos.empty:

                        total_adendos_cliente = 0.0
                        total_adendos_equipe = 0.0

                    else:

                        total_adendos_cliente = pd.to_numeric(
                            df_adendos.get("valor_cliente", 0),
                            errors="coerce"
                        ).fillna(0).sum()

                        total_adendos_equipe = pd.to_numeric(
                            df_adendos.get("valor_equipe", 0),
                            errors="coerce"
                        ).fillna(0).sum()

                    # ------------------------------------------------
                    # RESULTADO REAL
                    # ------------------------------------------------

                    faturamento_real = (
                        valor_venda +
                        total_adendos_cliente
                    )

                    custo_real = (
                        total_custo_evento +
                        total_adendos_equipe
                    )

                    lucro_real = (
                        faturamento_real -
                        custo_real
                    )

                    economia = (
                        custo_previsto -
                        custo_real
                    )

                    if faturamento_real > 0:

                        cmv_percentual = (
                            custo_real /
                            faturamento_real
                        ) * 100

                    else:

                        cmv_percentual = 0

                    # ------------------------------------------------
                    # CABEÇALHO DO EVENTO
                    # ------------------------------------------------

                    st.markdown(
                        f"### 🍸 {cliente} — {data_formatada}"
                    )

                    # ------------------------------------------------
                    # MÉTRICAS
                    # ------------------------------------------------

                    col1, col2, col3, col4, col5, col6 = st.columns(6)

                    with col1:
                        st.metric(
                            "💰 Venda Original",
                            f"R$ {valor_venda:,.2f}"
                        )

                    with col2:
                        st.metric(
                            "➕ Adendos",
                            f"R$ {total_adendos_cliente:,.2f}"
                        )

                    with col3:
                        st.metric(
                            "💵 Faturamento Real",
                            f"R$ {faturamento_real:,.2f}"
                        )

                    with col4:
                        st.metric(
                            "📦 Custo Real",
                            f"R$ {custo_real:,.2f}"
                        )

                    with col5:
                        st.metric(
                            "📊 CMV",
                            f"{cmv_percentual:.2f}%"
                        )

                    with col6:
                        st.metric(
                            "💎 Lucro Real",
                            f"R$ {lucro_real:,.2f}"
                        )

                    # ------------------------------------------------
                    # ALERTAS DE CMV
                    # ------------------------------------------------

                    if cmv_percentual > 50:

                        st.error(
                            "🚨 CMV CRÍTICO — acima de 50%"
                        )

                    elif cmv_percentual > 40:

                        st.warning(
                            "⚠️ CMV elevado — acima de 40%"
                        )

                    elif cmv_percentual > 0:

                        st.success(
                            "✅ CMV dentro de uma faixa saudável."
                        )

                    # ------------------------------------------------
                    # DIFERENÇA DO CUSTO PREVISTO
                    # ------------------------------------------------

                    if economia >= 0:

                        st.success(
                            f"💚 Economia em relação ao previsto: "
                            f"R$ {economia:,.2f}"
                        )

                    else:

                        st.warning(
                            f"🟠 Custo acima do previsto em: "
                            f"R$ {abs(economia):,.2f}"
                        )

                    # =================================================
                    # LANÇAMENTO DE CUSTO REAL
                    # =================================================

                    with st.expander("➕ Lançar custo real"):

                        with st.form(
                            key=f"form_custo_cmv_{evento_id}"
                        ):

                            col_a, col_b = st.columns(2)

                            with col_a:

                                categoria = st.selectbox(
                                    "Categoria",
                                    categorias_cmv,
                                    key=f"categoria_cmv_{evento_id}"
                                )

                            with col_b:

                                valor = st.number_input(
                                    "Valor",
                                    min_value=0.0,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"valor_cmv_{evento_id}"
                                )

                            descricao = st.text_input(
                                "Descrição",
                                key=f"descricao_cmv_{evento_id}"
                            )

                            salvar_custo = st.form_submit_button(
                                "💾 Lançar Custo"
                            )

                            if salvar_custo:

                                if valor <= 0:

                                    st.warning(
                                        "Informe um valor maior que zero."
                                    )

                                elif not descricao.strip():

                                    st.warning(
                                        "Informe uma descrição."
                                    )

                                else:

                                    supabase.table(
                                        "evento_custos"
                                    ).insert({
                                        "evento_id": int(evento_id),
                                        "descricao": (
                                            f"{categoria} - "
                                            f"{descricao.strip()}"
                                        ),
                                        "valor": float(valor)
                                    }).execute()

                                    st.success(
                                        "Custo lançado com sucesso!"
                                    )

                                    st.rerun()

                    # =================================================
                    # CUSTOS JÁ LANÇADOS
                    # =================================================

                    if not df_custos.empty:

                        st.markdown(
                            "**📦 Custos reais lançados:**"
                        )

                        for _, custo in df_custos.iterrows():

                            custo_id = custo.get("id")
                            descricao_custo = custo.get(
                                "descricao",
                                "Sem descrição"
                            )

                            valor_custo = float(
                                custo.get("valor", 0) or 0
                            )

                            col_c1, col_c2, col_c3 = st.columns(
                                [6, 2, 1]
                            )

                            with col_c1:
                                st.write(descricao_custo)

                            with col_c2:
                                st.write(
                                    f"R$ {valor_custo:,.2f}"
                                )

                            with col_c3:

                                if st.button(
                                    "🗑️",
                                    key=f"del_custo_{custo_id}"
                                ):

                                    supabase.table(
                                        "evento_custos"
                                    ).delete().eq(
                                        "id",
                                        int(custo_id)
                                    ).execute()

                                    st.rerun()

                    # =================================================
                    # ADENDOS DO EVENTO
                    # =================================================

                    if not df_adendos.empty:

                        st.markdown(
                            "**➕ Adendos deste evento:**"
                        )

                        df_adendos_exibir = df_adendos.copy()

                        colunas_adendos = [
                            "tipo",
                            "descrição",
                            "valor_cliente",
                            "valor_equipe",
                            "status"
                        ]

                        colunas_adendos = [
                            c for c in colunas_adendos
                            if c in df_adendos_exibir.columns
                        ]

                        if colunas_adendos:

                            st.dataframe(
                                df_adendos_exibir[
                                    colunas_adendos
                                ],
                                use_container_width=True,
                                hide_index=True
                            )

                    st.divider()

        except Exception as e:

            st.error(
                f"Erro ao carregar o CMV por evento: {e}"
            )

    # ============================================================
    # TAB 2 — ANÁLISE
    # ============================================================

    with tab2:

        st.subheader("📊 Análise Consolidada")

        try:

            resposta_eventos = (
                supabase
                .table("eventos")
                .select("*")
                .in_("status", status_eventos)
                .order("data", desc=True)
                .execute()
            )

            df_eventos_analise = pd.DataFrame(
                resposta_eventos.data
            )

            if df_eventos_analise.empty:

                st.info(
                    "Nenhum evento aprovado/finalizado encontrado."
                )

            else:

                dados_resumo = []

                for _, evento in df_eventos_analise.iterrows():

                    evento_id = evento.get("id")
                    cliente = evento.get(
                        "cliente",
                        "Evento sem cliente"
                    )

                    data_evento = evento.get("data")

                    venda_original = float(
                        evento.get("venda", 0) or 0
                    )

                    custo_previsto = float(
                        evento.get("custo", 0) or 0
                    )

                    # --------------------------------------------
                    # CUSTOS
                    # --------------------------------------------

                    resposta_custos = (
                        supabase
                        .table("evento_custos")
                        .select("valor")
                        .eq("evento_id", int(evento_id))
                        .execute()
                    )

                    df_custos = pd.DataFrame(
                        resposta_custos.data
                    )

                    if df_custos.empty:

                        custo_evento = 0.0

                    else:

                        custo_evento = pd.to_numeric(
                            df_custos["valor"],
                            errors="coerce"
                        ).fillna(0).sum()

                    # --------------------------------------------
                    # ADENDOS
                    # --------------------------------------------

                    resposta_adendos = (
                        supabase
                        .table("aditivos_evento")
                        .select(
                            "valor_cliente, valor_equipe, status"
                        )
                        .eq("evento_id", int(evento_id))
                        .neq("status", "Cancelado")
                        .execute()
                    )

                    df_adendos = pd.DataFrame(
                        resposta_adendos.data
                    )

                    if df_adendos.empty:

                        adendos_cliente = 0.0
                        adendos_equipe = 0.0

                    else:

                        adendos_cliente = pd.to_numeric(
                            df_adendos.get(
                                "valor_cliente",
                                0
                            ),
                            errors="coerce"
                        ).fillna(0).sum()

                        adendos_equipe = pd.to_numeric(
                            df_adendos.get(
                                "valor_equipe",
                                0
                            ),
                            errors="coerce"
                        ).fillna(0).sum()

                    # --------------------------------------------
                    # CONSOLIDAÇÃO
                    # --------------------------------------------

                    faturamento_real = (
                        venda_original +
                        adendos_cliente
                    )

                    custo_real = (
                        custo_evento +
                        adendos_equipe
                    )

                    diferenca = (
                        custo_previsto -
                        custo_real
                    )

                    lucro = (
                        faturamento_real -
                        custo_real
                    )

                    if faturamento_real > 0:

                        cmv = (
                            custo_real /
                            faturamento_real
                        ) * 100

                    else:

                        cmv = 0

                    dados_resumo.append({

                        "Cliente": cliente,

                        "Data": (
                            pd.to_datetime(data_evento)
                            .strftime("%d/%m/%Y")
                            if pd.notna(data_evento)
                            else "-"
                        ),

                        "Venda Original":
                            venda_original,

                        "Adendos":
                            adendos_cliente,

                        "Faturamento Real":
                            faturamento_real,

                        "Previsto":
                            custo_previsto,

                        "Custo Real":
                            custo_real,

                        "Diferença":
                            diferenca,

                        "Lucro":
                            lucro,

                        "CMV (%)":
                            cmv
                    })

                df_resumo = pd.DataFrame(
                    dados_resumo
                )

                # =================================================
                # MÉTRICAS CONSOLIDADAS
                # =================================================

                total_venda_original = (
                    df_resumo["Venda Original"].sum()
                )

                total_adendos = (
                    df_resumo["Adendos"].sum()
                )

                total_faturamento_real = (
                    df_resumo["Faturamento Real"].sum()
                )

                total_previsto = (
                    df_resumo["Previsto"].sum()
                )

                total_custo_real = (
                    df_resumo["Custo Real"].sum()
                )

                total_economia = (
                    total_previsto -
                    total_custo_real
                )

                total_lucro = (
                    total_faturamento_real -
                    total_custo_real
                )

                if total_faturamento_real > 0:

                    cmv_medio = (
                        total_custo_real /
                        total_faturamento_real
                    ) * 100

                else:

                    cmv_medio = 0

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "💰 Venda Original",
                        f"R$ {total_venda_original:,.2f}"
                    )

                with col2:
                    st.metric(
                        "➕ Adendos",
                        f"R$ {total_adendos:,.2f}"
                    )

                with col3:
                    st.metric(
                        "💵 Faturamento Real",
                        f"R$ {total_faturamento_real:,.2f}"
                    )

                col4, col5, col6 = st.columns(3)

                with col4:
                    st.metric(
                        "📦 Custo Real",
                        f"R$ {total_custo_real:,.2f}"
                    )

                with col5:
                    st.metric(
                        "📊 CMV Médio",
                        f"{cmv_medio:.2f}%"
                    )

                with col6:
                    st.metric(
                        "💎 Lucro Real",
                        f"R$ {total_lucro:,.2f}"
                    )

                # =================================================
                # ALERTA
                # =================================================

                if cmv_medio > 50:

                    st.error(
                        "🚨 CMV médio crítico — acima de 50%."
                    )

                elif cmv_medio > 40:

                    st.warning(
                        "⚠️ CMV médio elevado — acima de 40%."
                    )

                else:

                    st.success(
                        "✅ CMV médio dentro de uma faixa saudável."
                    )

                # =================================================
                # TABELA
                # =================================================

                st.markdown(
                    "### 📋 Resumo dos Eventos"
                )

                st.dataframe(
                    df_resumo,
                    use_container_width=True,
                    hide_index=True,
                    column_config={

                        "Venda Original":
                            st.column_config.NumberColumn(
                                "Venda Original",
                                format="R$ %.2f"
                            ),

                        "Adendos":
                            st.column_config.NumberColumn(
                                "Adendos",
                                format="R$ %.2f"
                            ),

                        "Faturamento Real":
                            st.column_config.NumberColumn(
                                "Faturamento Real",
                                format="R$ %.2f"
                            ),

                        "Previsto":
                            st.column_config.NumberColumn(
                                "Previsto",
                                format="R$ %.2f"
                            ),

                        "Custo Real":
                            st.column_config.NumberColumn(
                                "Custo Real",
                                format="R$ %.2f"
                            ),

                        "Diferença":
                            st.column_config.NumberColumn(
                                "Diferença",
                                format="R$ %.2f"
                            ),

                        "Lucro":
                            st.column_config.NumberColumn(
                                "Lucro",
                                format="R$ %.2f"
                            ),

                        "CMV (%)":
                            st.column_config.NumberColumn(
                                "CMV (%)",
                                format="%.2f%%"
                            )
                    }
                )

        except Exception as e:

            st.error(
                f"Erro na análise do CMV: {e}"
            )

    # ============================================================
    # TAB 3 — ADENDOS
    # ============================================================
    
    with tab3:
    
        st.subheader("➕ Adendos dos Eventos")
    
        st.caption(
            "Registre valores adicionais cobrados do cliente, "
            "como horas extras, vendas adicionais, quebras e "
            "serviços extras, além dos custos adicionais da equipe."
        )
    
        # ========================================================
        # CADASTRAR NOVO ADENDO
        # ========================================================
    
        with st.expander(
            "➕ Cadastrar novo adendo",
            expanded=False
        ):
    
            try:
    
                # ====================================================
                # BUSCAR EVENTOS
                # ====================================================
    
                resposta_eventos_adendo = (
                    supabase
                    .table("eventos")
                    .select("id, cliente, data")
                    .in_("status", status_eventos)
                    .order("data", desc=True)
                    .execute()
                )
    
                df_eventos_adendo = pd.DataFrame(
                    resposta_eventos_adendo.data
                    if resposta_eventos_adendo.data
                    else []
                )
    
                if df_eventos_adendo.empty:
    
                    st.info(
                        "Nenhum evento disponível para cadastrar adendo."
                    )
    
                else:
    
                    # =================================================
                    # MONTAR LISTA DE EVENTOS
                    # =================================================
    
                    opcoes_eventos = {}
    
                    for _, ev in df_eventos_adendo.iterrows():
    
                        ev_id = int(
                            ev.get("id")
                        )
    
                        ev_cliente = str(
                            ev.get(
                                "cliente",
                                "Evento sem cliente"
                            )
                        )
    
                        ev_data = ev.get("data")
    
                        # ---------------------------------------------
                        # FORMATAR DATA
                        # ---------------------------------------------
    
                        if pd.notna(ev_data):
    
                            try:
    
                                ev_data_formatada = (
                                    pd.to_datetime(
                                        ev_data
                                    ).strftime(
                                        "%d/%m/%Y"
                                    )
                                )
    
                            except Exception:
    
                                ev_data_formatada = str(
                                    ev_data
                                )
    
                        else:
    
                            ev_data_formatada = "-"
    
                        texto_evento = (
                            f"{ev_cliente} | "
                            f"{ev_data_formatada} | "
                            f"ID {ev_id}"
                        )
    
                        opcoes_eventos[
                            texto_evento
                        ] = {
    
                            "id": ev_id,
    
                            "cliente": ev_cliente
    
                        }
    
                    # =================================================
                    # FORMULÁRIO
                    # =================================================
    
                    with st.form(
                        "form_cadastro_adendo",
                        clear_on_submit=True
                    ):
    
                        # ---------------------------------------------
                        # EVENTO
                        # ---------------------------------------------
    
                        evento_selecionado = st.selectbox(
                            "Evento",
                            list(
                                opcoes_eventos.keys()
                            )
                        )
    
                        # ---------------------------------------------
                        # TIPO / STATUS
                        # ---------------------------------------------
    
                        col1, col2 = st.columns(2)
    
                        with col1:
    
                            tipo_adendo = st.selectbox(
                                "Tipo de Adendo",
                                [
                                    "Hora Extra",
                                    "Venda de Garrafa",
                                    "Quebra de Copo/Taça",
                                    "Serviço Adicional",
                                    "Custo Adicional",
                                    "Outros"
                                ]
                            )
    
                        with col2:
    
                            status_adendo = st.selectbox(
                                "Status",
                                [
                                    "Pendente",
                                    "Pago",
                                    "Cancelado"
                                ]
                            )
    
                        # ---------------------------------------------
                        # DESCRIÇÃO
                        # ---------------------------------------------
    
                        descricao_adendo = st.text_input(
                            "Descrição",
                            placeholder=(
                                "Ex.: 2 horas extras "
                                "de atendimento"
                            )
                        )
    
                        # ---------------------------------------------
                        # VALORES
                        # ---------------------------------------------
    
                        col3, col4 = st.columns(2)
    
                        with col3:
    
                            valor_cliente_adendo = (
                                st.number_input(
                                    "💰 Valor cobrado do cliente",
                                    min_value=0.0,
                                    step=0.01,
                                    format="%.2f"
                                )
                            )
    
                        with col4:
    
                            valor_equipe_adendo = (
                                st.number_input(
                                    "👷 Custo adicional da equipe",
                                    min_value=0.0,
                                    step=0.01,
                                    format="%.2f"
                                )
                            )
    
                        # ---------------------------------------------
                        # PAGAMENTO
                        # ---------------------------------------------
    
                        col5, col6 = st.columns(2)
    
                        with col5:
    
                            forma_pagamento = (
                                st.selectbox(
                                    "Forma de Pagamento",
                                    [
                                        "Pix",
                                        "Dinheiro",
                                        "Cartão",
                                        "Transferência",
                                        "Outro"
                                    ]
                                )
                            )
    
                        with col6:
    
                            data_pagamento = (
                                st.date_input(
                                    "📅 Data do Pagamento",
                                    value=None
                                )
                            )
    
                        # ---------------------------------------------
                        # BOTÃO
                        # ---------------------------------------------
    
                        salvar_adendo = (
                            st.form_submit_button(
                                "💾 Salvar Adendo",
                                use_container_width=True
                            )
                        )
    
                    # =================================================
                    # PROCESSAR CADASTRO
                    # =================================================
    
                    if salvar_adendo:
    
                        # ---------------------------------------------
                        # VALIDAÇÃO
                        # ---------------------------------------------
    
                        if (
                            valor_cliente_adendo <= 0
                            and
                            valor_equipe_adendo <= 0
                        ):
    
                            st.warning(
                                "⚠️ Informe pelo menos um valor: "
                                "valor cobrado do cliente ou "
                                "custo da equipe."
                            )
    
                        elif not descricao_adendo.strip():
    
                            st.warning(
                                "⚠️ Informe uma descrição "
                                "para o adendo."
                            )
    
                        else:
    
                            try:
    
                                # =====================================
                                # EVENTO SELECIONADO
                                # =====================================
    
                                dados_evento_selecionado = (
                                    opcoes_eventos[
                                        evento_selecionado
                                    ]
                                )
    
                                # =====================================
                                # DATA PAGAMENTO
                                # =====================================
    
                                data_pagamento_db = None
    
                                if data_pagamento is not None:
    
                                    data_pagamento_db = (
                                        data_pagamento.isoformat()
                                    )
    
                                # =====================================
                                # DADOS PARA INSERÇÃO
                                # =====================================
    
                                dados_adendo = {
    
                                    "evento_id":
                                        int(
                                            dados_evento_selecionado[
                                                "id"
                                            ]
                                        ),
    
                                    "evento":
                                        str(
                                            dados_evento_selecionado[
                                                "cliente"
                                            ]
                                        ),
    
                                    "tipo":
                                        str(
                                            tipo_adendo
                                        ),
    
                                    # IMPORTANTE:
                                    # nome exato da coluna no Supabase
                                    "descricao":
                                        descricao_adendo
                                        .strip(),
    
                                    "valor_cliente":
                                        float(
                                            valor_cliente_adendo
                                        ),
    
                                    "valor_equipe":
                                        float(
                                            valor_equipe_adendo
                                        ),
    
                                    "status":
                                        str(
                                            status_adendo
                                        ),
    
                                    "forma_pagamento":
                                        str(
                                            forma_pagamento
                                        ),
    
                                    "data_pagamento":
                                        data_pagamento_db
    
                                }
    
                                # =====================================
                                # INSERT
                                # =====================================
    
                                resposta_insert = (
                                    supabase
                                    .table(
                                        "aditivos_evento"
                                    )
                                    .insert(
                                        dados_adendo
                                    )
                                    .execute()
                                )
    
                                # =====================================
                                # CONFIRMAÇÃO
                                # =====================================
    
                                st.success(
                                    "✅ Adendo cadastrado com sucesso!"
                                )
    
                                st.rerun()
    
                            except Exception as erro_insert:
    
                                st.error(
                                    "❌ Erro ao salvar o adendo: "
                                    f"{erro_insert}"
                                )
    
            except Exception as e:
    
                st.error(
                    f"❌ Erro ao carregar eventos para adendo: {e}"
                )
    
    
        # ========================================================
        # FILTRO E LISTA DOS ADENDOS
        # ========================================================
    
        st.markdown("---")
    
        try:
    
            # ====================================================
            # CARREGAR ADENDOS
            # ====================================================
    
            resposta_adendos = (
                supabase
                .table("aditivos_evento")
                .select("*")
                .order("id", desc=True)
                .execute()
            )
    
            df_adendos_edicao = pd.DataFrame(
                resposta_adendos.data
                if resposta_adendos.data
                else []
            )
    
            # ====================================================
            # SEM ADENDOS
            # ====================================================
    
            if df_adendos_edicao.empty:
    
                st.info(
                    "Nenhum adendo cadastrado."
                )
    
            else:
    
                # =================================================
                # FILTRO POR EVENTO
                # =================================================
    
                eventos_filtro = [
                    "Todos"
                ]
    
                if (
                    "evento"
                    in df_adendos_edicao.columns
                ):
    
                    valores_eventos = (
                        df_adendos_edicao[
                            "evento"
                        ]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )
    
                    eventos_filtro.extend(
                        sorted(
                            valores_eventos
                        )
                    )
    
                filtro_evento = st.selectbox(
                    "🔎 Filtrar por evento",
                    eventos_filtro,
                    key="cmv_filtro_adendo"
                )
    
                # =================================================
                # APLICAR FILTRO
                # =================================================
    
                if (
                    filtro_evento != "Todos"
                    and
                    "evento"
                    in df_adendos_edicao.columns
                ):
    
                    df_edicao = (
                        df_adendos_edicao[
                            df_adendos_edicao[
                                "evento"
                            ]
                            .astype(str)
                            ==
                            filtro_evento
                        ]
                        .copy()
                    )
    
                else:
    
                    df_edicao = (
                        df_adendos_edicao.copy()
                    )
    
                # =================================================
                # NORMALIZAR DATA
                # =================================================
    
                if (
                    "data_pagamento"
                    in df_edicao.columns
                ):
    
                    df_edicao[
                        "data_pagamento"
                    ] = pd.to_datetime(
    
                        df_edicao[
                            "data_pagamento"
                        ],
    
                        errors="coerce",
    
                        utc=True
    
                    )
    
                    df_edicao[
                        "data_pagamento"
                    ] = (
    
                        df_edicao[
                            "data_pagamento"
                        ]
                        .dt
                        .tz_localize(None)
    
                    )
    
                # =================================================
                # NORMALIZAR VALORES
                # =================================================
    
                for coluna in [
    
                    "valor_cliente",
    
                    "valor_equipe"
    
                ]:
    
                    if (
                        coluna
                        in df_edicao.columns
                    ):
    
                        df_edicao[
                            coluna
                        ] = pd.to_numeric(
    
                            df_edicao[
                                coluna
                            ],
    
                            errors="coerce"
    
                        ).fillna(0.0)
    
                # =================================================
                # NORMALIZAR TEXTOS
                # =================================================
    
                for coluna in [
    
                    "tipo",
    
                    "descricao",
    
                    "status",
    
                    "forma_pagamento"
    
                ]:
    
                    if (
                        coluna
                        in df_edicao.columns
                    ):
    
                        df_edicao[
                            coluna
                        ] = (
    
                            df_edicao[
                                coluna
                            ]
                            .fillna("")
                            .astype(str)
    
                        )
    
                # =================================================
                # COLUNAS
                # =================================================
    
                colunas_editor = [
    
                    "id",
    
                    "evento",
    
                    "tipo",
    
                    "descricao",
    
                    "valor_cliente",
    
                    "valor_equipe",
    
                    "status",
    
                    "forma_pagamento",
    
                    "data_pagamento"
    
                ]
    
                colunas_editor = [
    
                    coluna
    
                    for coluna
                    in colunas_editor
    
                    if coluna
                    in df_edicao.columns
    
                ]
    
                df_edicao = (
    
                    df_edicao[
                        colunas_editor
                    ]
                    .copy()
    
                )
    
                # =================================================
                # CONFIGURAÇÃO EDITOR
                # =================================================
    
                config_editor = {
    
                    "id":
    
                        st.column_config.NumberColumn(
                            "ID",
                            disabled=True
                        ),
    
                    "evento":
    
                        st.column_config.TextColumn(
                            "Evento",
                            disabled=True
                        ),
    
                    "tipo":
    
                        st.column_config.TextColumn(
                            "Tipo"
                        ),
    
                    "descricao":
    
                        st.column_config.TextColumn(
                            "Descrição"
                        ),
    
                    "valor_cliente":
    
                        st.column_config.NumberColumn(
                            "💰 Cliente",
                            min_value=0.0,
                            step=0.01,
                            format="R$ %.2f"
                        ),
    
                    "valor_equipe":
    
                        st.column_config.NumberColumn(
                            "👷 Equipe",
                            min_value=0.0,
                            step=0.01,
                            format="R$ %.2f"
                        ),
    
                    "status":
    
                        st.column_config.TextColumn(
                            "Status"
                        ),
    
                    "forma_pagamento":
    
                        st.column_config.TextColumn(
                            "Pagamento"
                        ),
    
                    "data_pagamento":
    
                        st.column_config.DatetimeColumn(
                            "📅 Data Pagamento",
                            format="DD/MM/YYYY HH:mm"
                        )
    
                }
    
                # =================================================
                # EDITOR
                # =================================================
    
                df_editado = st.data_editor(
    
                    df_edicao,
    
                    use_container_width=True,
    
                    hide_index=True,
    
                    num_rows="fixed",
    
                    column_config=config_editor,
    
                    key="editor_adendos_cmv"
    
                )
    
                # =================================================
                # BOTÕES
                # =================================================
    
                col_salvar, col_excluir = st.columns(2)
    
                # =================================================
                # SALVAR ALTERAÇÕES
                # =================================================
    
                with col_salvar:
    
                    if st.button(
                        "💾 Salvar alterações",
                        key="cmv_salvar_edicao"
                    ):
    
                        try:
    
                            for _, linha in (
                                df_editado.iterrows()
                            ):
    
                                adendo_id = (
                                    linha.get("id")
                                )
    
                                if pd.isna(
                                    adendo_id
                                ):
    
                                    continue
    
                                dados_update = {}
    
                                # =====================================
                                # TIPO
                                # =====================================
    
                                if (
                                    "tipo"
                                    in linha.index
                                ):
    
                                    dados_update[
                                        "tipo"
                                    ] = str(
                                        linha[
                                            "tipo"
                                        ]
                                    ).strip()
    
                                # =====================================
                                # DESCRIÇÃO
                                # =====================================
    
                                if (
                                    "descricao"
                                    in linha.index
                                ):
    
                                    dados_update[
                                        "descricao"
                                    ] = str(
                                        linha[
                                            "descricao"
                                        ]
                                    ).strip()
    
                                # =====================================
                                # VALOR CLIENTE
                                # =====================================
    
                                if (
                                    "valor_cliente"
                                    in linha.index
                                ):
    
                                    valor_cliente = (
                                        pd.to_numeric(
    
                                            linha[
                                                "valor_cliente"
                                            ],
    
                                            errors="coerce"
    
                                        )
                                    )
    
                                    if pd.isna(
                                        valor_cliente
                                    ):
    
                                        valor_cliente = 0.0
    
                                    dados_update[
                                        "valor_cliente"
                                    ] = float(
                                        valor_cliente
                                    )
    
                                # =====================================
                                # VALOR EQUIPE
                                # =====================================
    
                                if (
                                    "valor_equipe"
                                    in linha.index
                                ):
    
                                    valor_equipe = (
                                        pd.to_numeric(
    
                                            linha[
                                                "valor_equipe"
                                            ],
    
                                            errors="coerce"
    
                                        )
                                    )
    
                                    if pd.isna(
                                        valor_equipe
                                    ):
    
                                        valor_equipe = 0.0
    
                                    dados_update[
                                        "valor_equipe"
                                    ] = float(
                                        valor_equipe
                                    )
    
                                # =====================================
                                # STATUS
                                # =====================================
    
                                if (
                                    "status"
                                    in linha.index
                                ):
    
                                    dados_update[
                                        "status"
                                    ] = str(
                                        linha[
                                            "status"
                                        ]
                                    ).strip()
    
                                # =====================================
                                # FORMA DE PAGAMENTO
                                # =====================================
    
                                if (
                                    "forma_pagamento"
                                    in linha.index
                                ):
    
                                    dados_update[
                                        "forma_pagamento"
                                    ] = str(
                                        linha[
                                            "forma_pagamento"
                                        ]
                                    ).strip()
    
                                # =====================================
                                # DATA PAGAMENTO
                                # =====================================
    
                                if (
                                    "data_pagamento"
                                    in linha.index
                                ):
    
                                    data_valor = (
                                        linha[
                                            "data_pagamento"
                                        ]
                                    )
    
                                    if pd.isna(
                                        data_valor
                                    ):
    
                                        dados_update[
                                            "data_pagamento"
                                        ] = None
    
                                    else:
    
                                        data_timestamp = (
                                            pd.to_datetime(
    
                                                data_valor,
    
                                                errors="coerce"
    
                                            )
                                        )
    
                                        if pd.isna(
                                            data_timestamp
                                        ):
    
                                            dados_update[
                                                "data_pagamento"
                                            ] = None
    
                                        else:
    
                                            dados_update[
                                                "data_pagamento"
                                            ] = (
                                                data_timestamp
                                                .isoformat()
                                            )
    
                                # =====================================
                                # UPDATE
                                # =====================================
    
                                if dados_update:
    
                                    supabase.table(
                                        "aditivos_evento"
                                    ).update(
    
                                        dados_update
    
                                    ).eq(
    
                                        "id",
    
                                        int(
                                            adendo_id
                                        )
    
                                    ).execute()
    
                            st.success(
                                "✅ Alterações salvas com sucesso!"
                            )
    
                            st.rerun()
    
                        except Exception as erro_update:
    
                            st.error(
                                "❌ Erro ao salvar alterações: "
                                f"{erro_update}"
                            )
    
                # =================================================
                # EXCLUIR
                # =================================================
    
                with col_excluir:
    
                    ids_adendos = (
    
                        df_edicao[
                            "id"
                        ]
                        .dropna()
                        .astype(int)
                        .tolist()
    
                        if (
                            "id"
                            in df_edicao.columns
                        )
    
                        else []
    
                    )
    
                    if ids_adendos:
    
                        id_excluir = st.selectbox(
    
                            "Selecionar adendo para excluir",
    
                            ids_adendos,
    
                            key="cmv_id_excluir"
    
                        )
    
                        if st.button(
    
                            "🗑️ Excluir adendo selecionado",
    
                            key="cmv_excluir_adendo"
    
                        ):
    
                            try:
    
                                supabase.table(
                                    "aditivos_evento"
                                ).delete().eq(
    
                                    "id",
    
                                    int(
                                        id_excluir
                                    )
    
                                ).execute()
    
                                st.success(
                                    "✅ Adendo excluído com sucesso!"
                                )
    
                                st.rerun()
    
                            except Exception as erro_delete:
    
                                st.error(
                                    "❌ Erro ao excluir adendo: "
                                    f"{erro_delete}"
                                )
    
                # =================================================
                # RESUMO
                # =================================================
    
                st.markdown("---")
    
                st.markdown(
                    "### 📊 Resumo dos Adendos"
                )
    
                total_cliente_adendos = (
    
                    pd.to_numeric(
    
                        df_edicao.get(
    
                            "valor_cliente",
    
                            pd.Series(
                                dtype=float
                            )
    
                        ),
    
                        errors="coerce"
    
                    )
                    .fillna(0)
                    .sum()
    
                )
    
                total_equipe_adendos = (
    
                    pd.to_numeric(
    
                        df_edicao.get(
    
                            "valor_equipe",
    
                            pd.Series(
                                dtype=float
                            )
    
                        ),
    
                        errors="coerce"
    
                    )
                    .fillna(0)
    
                    .sum()
    
                )
    
                resultado_adendos = (
    
                    total_cliente_adendos
    
                    -
    
                    total_equipe_adendos
    
                )
    
                c1, c2, c3 = st.columns(3)
    
                with c1:
    
                    st.metric(
    
                        "💰 Receita dos Adendos",
    
                        f"R$ {total_cliente_adendos:,.2f}"
    
                    )
    
                with c2:
    
                    st.metric(
    
                        "👷 Custo de Equipe",
    
                        f"R$ {total_equipe_adendos:,.2f}"
    
                    )
    
                with c3:
    
                    st.metric(
    
                        "💎 Resultado dos Adendos",
    
                        f"R$ {resultado_adendos:,.2f}"
    
                    )
    
        except Exception as e:
    
            st.error(
                f"❌ Erro ao carregar os adendos: {e}"
            )
            
elif menu == "Financeiro":

    st.title("💰 Financeiro")

    tab1, tab_pendentes, tab2, tab4, tab5 = st.tabs([
        "📊 Resumo",
        "🔔 Pendências / A Receber",
        "🎉 Eventos",
        "➕ Lançamentos Manuais",
        "📄 Extrato Completo",
    ])

    # =========================================================
    # 📊 TAB 1: RESUMO
    # =========================================================
    with tab1:

        # -----------------------------------------------------
        # DATA PADRÃO
        # -----------------------------------------------------
        data_inicial = date(date.today().year, 1, 1)
        data_final = date.today()

        # -----------------------------------------------------
        # BUSCAR FINANCEIRO
        # -----------------------------------------------------
        response_fin = (
            supabase
            .table("Financeiro")
            .select("*")
            .execute()
        )

        df_fin = pd.DataFrame(response_fin.data or [])

        # -----------------------------------------------------
        # BUSCAR EVENTOS
        # -----------------------------------------------------
        response_eventos = (
            supabase
            .table("eventos")
            .select("*")
            .in_(
                "status",
                ["aprovado", "finalizado", "concluido", "pago"]
            )
            .execute()
        )

        df_eventos = pd.DataFrame(response_eventos.data or [])

        # -----------------------------------------------------
        # BUSCAR ADITIVOS
        # -----------------------------------------------------
        response_aditivos = (
            supabase
            .table("aditivos_evento")
            .select("*")
            .execute()
        )

        df_aditivos = pd.DataFrame(
            response_aditivos.data or []
        )

        # =====================================================
        # PREPARAÇÃO FINANCEIRO
        # =====================================================

        entrada_manual = 0.0
        saida_manual = 0.0

        if not df_fin.empty:

            if "valor" in df_fin.columns:

                df_fin["valor"] = pd.to_numeric(
                    df_fin["valor"],
                    errors="coerce"
                ).fillna(0)

            else:

                df_fin["valor"] = 0.0

            # -------------------------------------------------
            # ENTRADAS
            # -------------------------------------------------
            entrada_manual = (
                df_fin[
                    df_fin["tipo"] == "Entrada"
                ]["valor"].sum()
            )

            # -------------------------------------------------
            # SAÍDAS
            # -------------------------------------------------
            #
            # Mantém a lógica existente:
            # cachês/equipe não entram novamente como saída
            # para evitar duplicidade.
            # -------------------------------------------------
            if "categoria" in df_fin.columns:

                df_saidas_validas = df_fin[
                    (df_fin["tipo"] == "Saída") &
                    (
                        ~df_fin["categoria"]
                        .astype(str)
                        .str.lower()
                        .str.contains(
                            "cachê|cache|equipe",
                            na=False
                        )
                    )
                ]

                saida_manual = (
                    df_saidas_validas["valor"].sum()
                )

            else:

                saida_manual = (
                    df_fin[
                        df_fin["tipo"] == "Saída"
                    ]["valor"].sum()
                )

        # =====================================================
        # CUSTOS DOS EVENTOS
        # =====================================================

        custo_eventos_total = 0.0

        if not df_eventos.empty:

            if "custo" in df_eventos.columns:

                df_eventos["custo"] = pd.to_numeric(
                    df_eventos["custo"],
                    errors="coerce"
                ).fillna(0)

                custo_eventos_total = (
                    df_eventos["custo"].sum()
                )

        # =====================================================
        # RESULTADO FINANCEIRO
        # =====================================================

        entrada = entrada_manual

        saida = (
            custo_eventos_total +
            saida_manual
        )

        saldo = entrada - saida

        # Mantém a lógica existente
        lucro = max(0.0, saldo)

        # =====================================================
        # RESERVA DE EMERGÊNCIA — 35%
        # =====================================================

        reserva_emergencia = lucro * 0.35

        # =====================================================
        # CAIXA DISPONÍVEL — 65%
        # =====================================================

        caixa_disponivel = (
            lucro -
            reserva_emergencia
        )

        # =====================================================
        # CARDS PRINCIPAIS
        # =====================================================

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "💰 Entradas Totais",
            f"R$ {entrada:,.2f}"
        )

        c2.metric(
            "💸 Saídas / Custos Totais",
            f"R$ {saida:,.2f}"
        )

        c3.metric(
            "📈 Lucro",
            f"R$ {lucro:,.2f}",
            help="Resultado financeiro antes da separação dos 35% para a Reserva de Emergência."
        )

        c4.metric(
            "🛡️ Reserva de Emergência",
            f"R$ {reserva_emergencia:,.2f}",
            help="35% do lucro destinados à Reserva de Emergência."
        )

        c5.metric(
            "💵 Caixa Disponível",
            f"R$ {caixa_disponivel:,.2f}",
            help="65% restantes do lucro após separar os 35% da Reserva de Emergência."
        )

        st.divider()

        # =====================================================
        # CONTAS A RECEBER
        # FATURAMENTO REAL = CONTRATO + ADITIVOS
        # =====================================================

        try:

            recebimentos = pd.DataFrame(
                supabase
                .table("recebimentos_eventos")
                .select("*")
                .execute()
                .data or []
            )

            # -------------------------------------------------
            # CONTRATADO / FATURAMENTO REAL
            # -------------------------------------------------

            total_contratado = 0.0

            if not df_eventos.empty:

                df_eventos["venda"] = pd.to_numeric(
                    df_eventos["venda"],
                    errors="coerce"
                ).fillna(0)

                total_contratado = (
                    df_eventos["venda"].sum()
                )

            # -------------------------------------------------
            # ADITIVOS
            # -------------------------------------------------

            total_aditivos = 0.0
            total_aditivos_pagos = 0.0

            if not df_aditivos.empty:

                if "valor_cliente" in df_aditivos.columns:

                    df_aditivos["valor_cliente"] = pd.to_numeric(
                        df_aditivos["valor_cliente"],
                        errors="coerce"
                    ).fillna(0)

                    # Todos os aditivos cobrados
                    total_aditivos = (
                        df_aditivos["valor_cliente"].sum()
                    )

                    # Apenas aditivos pagos
                    if "status" in df_aditivos.columns:

                        aditivos_pagos = df_aditivos[
                            df_aditivos["status"]
                            .astype(str)
                            .str.lower()
                            == "pago"
                        ]

                        total_aditivos_pagos = (
                            aditivos_pagos[
                                "valor_cliente"
                            ].sum()
                        )

            # -------------------------------------------------
            # FATURAMENTO REAL
            # -------------------------------------------------

            total_faturamento_real = (
                total_contratado +
                total_aditivos
            )

            # -------------------------------------------------
            # RECEBIMENTOS DOS CONTRATOS
            # -------------------------------------------------

            total_recebido_contratos = 0.0

            if not recebimentos.empty:

                if "valor" in recebimentos.columns:

                    recebimentos["valor"] = pd.to_numeric(
                        recebimentos["valor"],
                        errors="coerce"
                    ).fillna(0)

                    total_recebido_contratos = (
                        recebimentos["valor"].sum()
                    )

            # -------------------------------------------------
            # TOTAL RECEBIDO
            # -------------------------------------------------

            total_recebido = (
                total_recebido_contratos +
                total_aditivos_pagos
            )

            # -------------------------------------------------
            # TOTAL A RECEBER
            # -------------------------------------------------

            total_a_receber = max(
                0.0,
                total_faturamento_real -
                total_recebido
            )

            # -------------------------------------------------
            # EXIBIÇÃO
            # -------------------------------------------------

            st.subheader(
                "📋 Contas a Receber — Faturamento Real"
            )

            st.caption(
                "O valor contratado considera o contrato base "
                "mais todos os aditivos cobrados do cliente."
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "🎉 Faturamento Total",
                f"R$ {total_faturamento_real:,.2f}"
            )

            c2.metric(
                "💰 Recebido",
                f"R$ {total_recebido:,.2f}"
            )

            c3.metric(
                "🟡 A Receber",
                f"R$ {total_a_receber:,.2f}"
            )

        except Exception as e:

            st.info(
                "Controle de recebimentos ainda não disponível."
            )

        st.divider()

        # =====================================================
        # GRÁFICOS DE ACOMPANHAMENTO
        # =====================================================

        if not df_fin.empty:

            df_fin["data"] = pd.to_datetime(
                df_fin["data"],
                errors="coerce"
            )

            df_fin = df_fin.dropna(
                subset=["data"]
            )

            if not df_fin.empty:

                # -------------------------------------------------
                # MÊS
                # -------------------------------------------------

                df_fin["mes"] = (
                    df_fin["data"]
                    .dt.to_period("M")
                )

                mensal = (
                    df_fin
                    .groupby(
                        ["mes", "tipo"]
                    )["valor"]
                    .sum()
                    .unstack()
                    .fillna(0)
                )

                st.subheader(
                    "📊 Resultado Mensal"
                )

                st.bar_chart(
                    mensal
                )

                # -------------------------------------------------
                # GASTOS POR CATEGORIA
                # -------------------------------------------------

                st.subheader(
                    "💸 Gastos por Categoria"
                )

                if "categoria" in df_fin.columns:

                    gastos = (
                        df_fin[
                            df_fin["tipo"] == "Saída"
                        ]
                        .groupby("categoria")["valor"]
                        .sum()
                        .sort_values(
                            ascending=False
                        )
                    )

                    if not gastos.empty:

                        st.dataframe(
                            gastos,
                            use_container_width=True
                        )

                # -------------------------------------------------
                # ENTRADAS POR CATEGORIA
                # -------------------------------------------------

                st.subheader(
                    "💳 Entradas por Categoria"
                )

                if "categoria" in df_fin.columns:

                    entradas_cat = (
                        df_fin[
                            df_fin["tipo"] == "Entrada"
                        ]
                        .groupby("categoria")["valor"]
                        .sum()
                        .sort_values(
                            ascending=False
                        )
                    )

                    if not entradas_cat.empty:

                        st.dataframe(
                            entradas_cat,
                            use_container_width=True
                        )

                # -------------------------------------------------
                # EVOLUÇÃO DO CAIXA
                # -------------------------------------------------

                df_ordenado = (
                    df_fin
                    .sort_values("data")
                    .copy()
                )

                df_ordenado["fluxo"] = df_ordenado.apply(
                    lambda x:
                    (
                        x["valor"]
                        if x["tipo"] == "Entrada"
                        else -x["valor"]
                    ),
                    axis=1
                )

                df_ordenado["saldo_acumulado"] = (
                    df_ordenado["fluxo"].cumsum()
                )

                st.subheader(
                    "🏦 Evolução do Caixa"
                )

                st.line_chart(
                    df_ordenado
                    .set_index("data")[
                        "saldo_acumulado"
                    ]
                )

            # -------------------------------------------------
            # ALERTA DE CAIXA NEGATIVO
            # -------------------------------------------------

            if saida > entrada:

                st.error(
                    "⚠️ Atenção: as saídas e custos totais "
                    "superaram as entradas no período!"
                )

    # =========================================================
    # 🔔 TAB 2: PENDÊNCIAS / A RECEBER
    # =========================================================

    with tab_pendentes:

        st.subheader(
            "🔔 Eventos com Saldo Pendente"
        )

        st.caption(
            "Central de ações para lançar pagamentos "
            "e aditivos de eventos em aberto."
        )

        eventos = pd.DataFrame(
            supabase
            .table("eventos")
            .select("*")
            .in_(
                "status",
                [
                    "aprovado",
                    "finalizado",
                    "concluido",
                    "pago"
                ]
            )
            .order("data")
            .execute()
            .data or []
        )

        recebimentos = pd.DataFrame(
            supabase
            .table("recebimentos_eventos")
            .select("*")
            .execute()
            .data or []
        )

        aditivos_df = pd.DataFrame(
            supabase
            .table("aditivos_evento")
            .select("*")
            .execute()
            .data or []
        )

        if eventos.empty:

            st.info(
                "Nenhum evento encontrado."
            )

        else:

            eventos_com_pendencia = 0

            for _, evento in eventos.iterrows():

                evento_id = evento["id"]

                cliente = evento.get(
                    "cliente",
                    "Cliente"
                )

                data_evento = evento.get(
                    "data",
                    ""
                )

                # -------------------------------------------------
                # ADITIVOS
                # -------------------------------------------------

                total_aditivos_cliente = 0.0
                total_aditivos_pagos = 0.0

                aditivos_evento = pd.DataFrame()

                if not aditivos_df.empty:

                    aditivos_evento = (
                        aditivos_df[
                            aditivos_df[
                                "evento_id"
                            ].astype(str)
                            == str(evento_id)
                        ]
                        .copy()
                    )

                    if not aditivos_evento.empty:

                        total_aditivos_cliente = (
                            pd.to_numeric(
                                aditivos_evento[
                                    "valor_cliente"
                                ],
                                errors="coerce"
                            )
                            .fillna(0)
                            .sum()
                        )

                        aditivos_pagos = (
                            aditivos_evento[
                                aditivos_evento[
                                    "status"
                                ]
                                .astype(str)
                                .str.lower()
                                == "pago"
                            ]
                        )

                        if not aditivos_pagos.empty:

                            total_aditivos_pagos = (
                                pd.to_numeric(
                                    aditivos_pagos[
                                        "valor_cliente"
                                    ],
                                    errors="coerce"
                                )
                                .fillna(0)
                                .sum()
                            )

                # -------------------------------------------------
                # VALORES DO EVENTO
                # -------------------------------------------------

                valor_contrato_base = float(
                    evento.get("venda", 0) or 0
                )

                custo_evento_total = float(
                    evento.get("custo", 0) or 0
                )

                valor_contratado_total = (
                    valor_contrato_base +
                    total_aditivos_cliente
                )

                lucro_evento = max(
                    0.0,
                    valor_contratado_total -
                    custo_evento_total
                )

                reserva_caixa_35 = (
                    lucro_evento * 0.35
                )

                # -------------------------------------------------
                # RECEBIMENTOS
                # -------------------------------------------------

                if not recebimentos.empty:

                    receb_evento = (
                        recebimentos[
                            recebimentos[
                                "evento_id"
                            ].astype(str)
                            == str(evento_id)
                        ]
                        .copy()
                    )

                else:

                    receb_evento = pd.DataFrame()

                receb_contrato = (
                    pd.to_numeric(
                        receb_evento["valor"],
                        errors="coerce"
                    )
                    .fillna(0)
                    .sum()
                    if not receb_evento.empty
                    else 0.0
                )

                recebido = (
                    receb_contrato +
                    total_aditivos_pagos
                )

                a_receber = max(
                    0.0,
                    valor_contratado_total -
                    recebido
                )

                # -------------------------------------------------
                # MOSTRAR SOMENTE PENDENTES
                # -------------------------------------------------

                if round(a_receber, 2) > 0:

                    eventos_com_pendencia += 1

                    status_fin = (
                        "🟡 PARCIAL"
                        if recebido > 0
                        else "🔴 NÃO RECEBIDO"
                    )

                    st.markdown(
                        f"### 🎉 {cliente}"
                    )

                    st.caption(
                        f"📅 **Data do Evento:** "
                        f"{data_evento} | "
                        f"**Situação:** {status_fin}"
                    )

                    m1, m2, m3, m4 = st.columns(4)

                    delta_venda = (
                        f"+ R$ {total_aditivos_cliente:,.2f} aditivos"
                        if total_aditivos_cliente > 0
                        else None
                    )

                    m1.metric(
                        "Faturamento Total",
                        f"R$ {valor_contratado_total:,.2f}",
                        delta=delta_venda
                    )

                    m2.metric(
                        "Custo Estimado",
                        f"R$ {custo_evento_total:,.2f}"
                    )

                    m3.metric(
                        "Lucro Estimado",
                        f"R$ {lucro_evento:,.2f}"
                    )

                    m4.metric(
                        "🛡️ Reserva de Emergência (35%)",
                        f"R$ {reserva_caixa_35:,.2f}"
                    )

                    c1, c2 = st.columns(2)

                    c1.metric(
                        "💵 Recebido",
                        f"R$ {recebido:,.2f}"
                    )

                    c2.metric(
                        "🟡 A Receber",
                        f"R$ {a_receber:,.2f}"
                    )

                    # =================================================
                    # REGISTRAR RECEBIMENTO
                    # =================================================

                    with st.expander(
                        f"💰 Registrar Recebimento — {cliente}"
                    ):

                        col1, col2 = st.columns(2)

                        valor_recebimento = (
                            col1.number_input(
                                "Valor recebido",
                                min_value=0.0,
                                max_value=float(
                                    a_receber
                                ),
                                value=float(
                                    a_receber
                                ),
                                step=50.0,
                                key=f"p_valor_rec_{evento_id}"
                            )
                        )

                        data_recebimento = (
                            col2.date_input(
                                "Data do recebimento",
                                value=date.today(),
                                key=f"p_data_rec_{evento_id}"
                            )
                        )

                        forma = st.selectbox(
                            "Forma de pagamento",
                            [
                                "Pix",
                                "Dinheiro",
                                "Cartão",
                                "Transferência"
                            ],
                            key=f"p_forma_rec_{evento_id}"
                        )

                        data_prevista = st.date_input(
                            "📅 Data prevista para cobrança do restante",
                            value=date.today(),
                            key=f"p_data_prev_{evento_id}"
                        )

                        descricao = st.text_input(
                            "Descrição",
                            value=f"Recebimento evento {cliente}",
                            key=f"p_desc_rec_{evento_id}"
                        )

                        if st.button(
                            "💾 Confirmar Recebimento",
                            key=f"p_registrar_rec_{evento_id}",
                            use_container_width=True
                        ):

                            if valor_recebimento <= 0:

                                st.warning(
                                    "Informe um valor maior que zero."
                                )

                            elif valor_recebimento > a_receber:

                                st.warning(
                                    "O valor não pode ser maior "
                                    "que o saldo a receber."
                                )

                            else:

                                try:

                                    supabase.table(
                                        "recebimentos_eventos"
                                    ).insert({
                                        "evento_id": int(evento_id),
                                        "data_recebimento": str(
                                            data_recebimento
                                        ),
                                        "data_prevista": str(
                                            data_prevista
                                        ),
                                        "valor": valor_recebimento,
                                        "forma_pagamento": forma,
                                        "descricao": descricao,
                                        "status": "recebido",
                                    }).execute()

                                    supabase.table(
                                        "Financeiro"
                                    ).insert({
                                        "data": str(
                                            data_recebimento
                                        ),
                                        "tipo": "Entrada",
                                        "categoria": "Evento",
                                        "forma_pagamento": forma,
                                        "descricao": descricao,
                                        "valor": valor_recebimento,
                                    }).execute()

                                    st.toast(
                                        "✅ Recebimento registrado no Financeiro!",
                                        icon="🎉"
                                    )

                                    st.rerun()

                                except Exception as e:

                                    st.error(
                                        f"❌ Erro ao registrar recebimento: {e}"
                                    )

                    # =================================================
                    # REGISTRAR ADITIVOS
                    # =================================================

                    with st.expander(
                        f"➕ Aditivos / Horas Extras — {cliente}"
                    ):

                        with st.form(
                            key=f"p_form_aditivo_{evento_id}"
                        ):

                            col_a, col_b = st.columns(2)

                            tipo_aditivo = col_a.selectbox(
                                "Tipo de Aditivo",
                                [
                                    "Hora Extra",
                                    "Quebra de Copos",
                                    "Consumo Extra",
                                    "Outros"
                                ],
                                key=f"p_tipo_adt_{evento_id}"
                            )

                            valor_cobrado_cliente = (
                                col_b.number_input(
                                    "💰 Cobrado do Cliente (R$)",
                                    min_value=0.0,
                                    value=400.0,
                                    step=50.0,
                                    key=f"p_v_cli_{evento_id}"
                                )
                            )

                            col_st, col_fpg = st.columns(2)

                            status_aditivo = col_st.selectbox(
                                "Status",
                                [
                                    "Pago",
                                    "Pendente"
                                ],
                                key=f"p_st_adt_{evento_id}"
                            )

                            forma_pagto_aditivo = col_fpg.selectbox(
                                "Forma de Pagamento",
                                [
                                    "Pix",
                                    "Dinheiro",
                                    "Cartão",
                                    "Transferência"
                                ],
                                key=f"p_fpg_adt_{evento_id}"
                            )

                            obs_aditivo = st.text_input(
                                "Observação / Detalhes",
                                placeholder="Ex.: 2h extras contratadas no local",
                                key=f"p_obs_adt_{evento_id}"
                            )

                            btn_salvar_aditivo = (
                                st.form_submit_button(
                                    "💾 Salvar Aditivo",
                                    use_container_width=True
                                )
                            )

                        if btn_salvar_aditivo:

                            agora_iso = datetime.now().isoformat()

                            data_hoje = str(
                                datetime.now().date()
                            )

                            try:

                                payload_aditivo = {
                                    "evento_id": int(evento_id),
                                    "evento": str(cliente),
                                    "tipo": str(tipo_aditivo),
                                    "descricao": str(obs_aditivo),
                                    "valor_cliente": float(
                                        valor_cobrado_cliente
                                    ),
                                    "valor_equipe": 0.0,
                                    "status": str(
                                        status_aditivo
                                    ),
                                    "forma_pagamento": (
                                        str(
                                            forma_pagto_aditivo
                                        )
                                        if status_aditivo == "Pago"
                                        else None
                                    ),
                                    "data_pagamento": (
                                        agora_iso
                                        if status_aditivo == "Pago"
                                        else None
                                    ),
                                }

                                supabase.table(
                                    "aditivos_evento"
                                ).insert(
                                    payload_aditivo
                                ).execute()

                                if (
                                    status_aditivo == "Pago"
                                    and
                                    valor_cobrado_cliente > 0
                                ):

                                    supabase.table(
                                        "Financeiro"
                                    ).insert({
                                        "data": data_hoje,
                                        "tipo": "Entrada",
                                        "categoria": f"Aditivo - {tipo_aditivo}",
                                        "forma_pagamento": str(
                                            forma_pagto_aditivo
                                        ),
                                        "descricao": (
                                            f"Aditivo "
                                            f"({tipo_aditivo}) - "
                                            f"{cliente}"
                                        ),
                                        "valor": float(
                                            valor_cobrado_cliente
                                        ),
                                    }).execute()

                                st.toast(
                                    "✅ Aditivo registrado com sucesso!",
                                    icon="➕"
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"❌ Erro ao registrar aditivo: {e}"
                                )

                    st.markdown("---")

            if eventos_com_pendencia == 0:

                st.success(
                    "🎉 Nenhum evento com saldo pendente no momento!"
                )

    # =========================================================
    # 🎉 TAB 3: HISTÓRICO FINANCEIRO DOS EVENTOS
    # =========================================================

    with tab2:

        st.subheader(
            "🎉 Histórico Financeiro dos Eventos"
        )

        st.caption(
            "Visão histórica dos recebimentos e fechamento de cada contrato."
        )

        eventos = pd.DataFrame(
            supabase
            .table("eventos")
            .select("*")
            .in_(
                "status",
                [
                    "aprovado",
                    "finalizado",
                    "concluido",
                    "pago"
                ]
            )
            .order("data")
            .execute()
            .data or []
        )

        recebimentos = pd.DataFrame(
            supabase
            .table("recebimentos_eventos")
            .select("*")
            .execute()
            .data or []
        )

        aditivos_df = pd.DataFrame(
            supabase
            .table("aditivos_evento")
            .select("*")
            .execute()
            .data or []
        )

        if eventos.empty:

            st.info(
                "Nenhum evento cadastrado."
            )

        else:

            for _, evento in eventos.iterrows():

                evento_id = evento["id"]

                cliente = evento.get(
                    "cliente",
                    "Cliente"
                )

                data_evento = evento.get(
                    "data",
                    ""
                )

                total_aditivos_cliente = 0.0
                total_aditivos_pagos = 0.0

                aditivos_evento = pd.DataFrame()

                if not aditivos_df.empty:

                    aditivos_evento = (
                        aditivos_df[
                            aditivos_df[
                                "evento_id"
                            ].astype(str)
                            == str(evento_id)
                        ]
                        .copy()
                    )

                    if not aditivos_evento.empty:

                        total_aditivos_cliente = (
                            pd.to_numeric(
                                aditivos_evento[
                                    "valor_cliente"
                                ],
                                errors="coerce"
                            )
                            .fillna(0)
                            .sum()
                        )

                        aditivos_pagos = (
                            aditivos_evento[
                                aditivos_evento[
                                    "status"
                                ]
                                .astype(str)
                                .str.lower()
                                == "pago"
                            ]
                        )

                        if not aditivos_pagos.empty:

                            total_aditivos_pagos = (
                                pd.to_numeric(
                                    aditivos_pagos[
                                        "valor_cliente"
                                    ],
                                    errors="coerce"
                                )
                                .fillna(0)
                                .sum()
                            )

                valor_contrato_base = float(
                    evento.get("venda", 0) or 0
                )

                custo_evento_total = float(
                    evento.get("custo", 0) or 0
                )

                valor_contratado_total = (
                    valor_contrato_base +
                    total_aditivos_cliente
                )

                lucro_evento = max(
                    0.0,
                    valor_contratado_total -
                    custo_evento_total
                )

                reserva_caixa_35 = (
                    lucro_evento * 0.35
                )

                caixa_disponivel_evento = (
                    lucro_evento -
                    reserva_caixa_35
                )

                if not recebimentos.empty:

                    receb_evento = (
                        recebimentos[
                            recebimentos[
                                "evento_id"
                            ].astype(str)
                            == str(evento_id)
                        ]
                        .copy()
                    )

                else:

                    receb_evento = pd.DataFrame()

                receb_contrato = (
                    pd.to_numeric(
                        receb_evento["valor"],
                        errors="coerce"
                    )
                    .fillna(0)
                    .sum()
                    if not receb_evento.empty
                    else 0.0
                )

                recebido = (
                    receb_contrato +
                    total_aditivos_pagos
                )

                a_receber = max(
                    0.0,
                    valor_contratado_total -
                    recebido
                )

                if round(a_receber, 2) <= 0:

                    status_fin = "🟢 PAGO"

                elif recebido > 0:

                    status_fin = "🟡 PARCIAL"

                else:

                    status_fin = "🔴 NÃO RECEBIDO"

                st.markdown(
                    f"### 🎉 {cliente}"
                )

                st.caption(
                    f"📅 **Data do Evento:** "
                    f"{data_evento} | "
                    f"**Situação:** {status_fin}"
                )

                m1, m2, m3, m4 = st.columns(4)

                delta_venda = (
                    f"+ R$ {total_aditivos_cliente:,.2f} aditivos"
                    if total_aditivos_cliente > 0
                    else None
                )

                m1.metric(
                    "Faturamento Total",
                    f"R$ {valor_contratado_total:,.2f}",
                    delta=delta_venda
                )

                m2.metric(
                    "Custo",
                    f"R$ {custo_evento_total:,.2f}"
                )

                m3.metric(
                    "Lucro",
                    f"R$ {lucro_evento:,.2f}"
                )

                m4.metric(
                    "🛡️ Reserva de Emergência (35%)",
                    f"R$ {reserva_caixa_35:,.2f}"
                )

                c1, c2 = st.columns(2)

                c1.metric(
                    "💵 Caixa Disponível",
                    f"R$ {caixa_disponivel_evento:,.2f}"
                )

                c2.metric(
                    "🟡 A Receber",
                    f"R$ {a_receber:,.2f}"
                )

                # -------------------------------------------------
                # ADITIVOS
                # -------------------------------------------------

                if not aditivos_evento.empty:

                    st.markdown(
                        "#### ➕ Aditivos Registrados"
                    )

                    for idx, aditivo in aditivos_evento.iterrows():

                        tipo = aditivo.get(
                            "tipo",
                            "Aditivo"
                        )

                        valor_adt = float(
                            aditivo.get(
                                "valor_cliente",
                                0
                            ) or 0
                        )

                        status_adt = aditivo.get(
                            "status",
                            "Pendente"
                        )

                        obs = aditivo.get(
                            "descricao",
                            ""
                        )

                        st.write(
                            f"• **{tipo}**: "
                            f"R$ {valor_adt:,.2f} | "
                            f"**Status:** {status_adt} | "
                            f"*{obs}*"
                        )

                # -------------------------------------------------
                # HISTÓRICO RECEBIMENTOS
                # -------------------------------------------------

                if not receb_evento.empty:

                    st.markdown(
                        "#### 💳 Histórico de Recebimentos"
                    )

                    historico = receb_evento[
                        [
                            "data_recebimento",
                            "valor",
                            "forma_pagamento",
                            "descricao",
                        ]
                    ].copy()

                    historico = historico.rename(
                        columns={
                            "data_recebimento": "Data",
                            "valor": "Valor",
                            "forma_pagamento": "Forma",
                            "descricao": "Descrição",
                        }
                    )

                    historico["Valor"] = pd.to_numeric(
                        historico["Valor"],
                        errors="coerce"
                    )

                    st.dataframe(
                        historico,
                        use_container_width=True,
                        hide_index=True
                    )

                st.divider()

    # =========================================================
    # ➕ TAB 4: LANÇAMENTOS MANUAIS
    # =========================================================

    with tab4:

        st.subheader(
            "➕ Lançamento Manual "
            "(Entradas Avulsas & Gastos/Melhorias)"
        )

        st.caption(
            "Use este formulário para lançar saídas "
            "(gastos com estrutura, bebidas, investimentos, "
            "manutenção) e entradas manuais que NÃO vêm "
            "de contratos de eventos."
        )

        with st.form(
            "form_lancamento_manual",
            clear_on_submit=True
        ):

            col_t1, col_t2 = st.columns(2)

            tipo_mov = col_t1.selectbox(
                "Tipo de Movimentação",
                [
                    "Saída",
                    "Entrada"
                ],
                help=(
                    "Selecione Saída para gastos/melhorias "
                    "ou Entrada para receitas avulsas."
                )
            )

            data_mov = col_t2.date_input(
                "Data da Transação",
                value=date.today()
            )

            col_v1, col_v2 = st.columns(2)

            valor_mov = col_v1.number_input(
                "Valor (R$)",
                min_value=0.0,
                step=10.0,
                format="%.2f"
            )

            if tipo_mov == "Saída":

                categorias_opcoes = [
                    "Investimentos / Melhorias",
                    "Compra de Bebidas / Insumos",
                    "Equipe / Mão de Obra Avulsa",
                    "Transporte / Logística",
                    "Marketing / Anúncios",
                    "Manutenção de Equipamentos",
                    "Custos Operacionais / Fixos",
                    "Outras Saídas",
                ]

            else:

                categorias_opcoes = [
                    "Aporte de Capital / Sócios",
                    "Rendimentos / Aplicações",
                    "Venda de Equipamentos / Ativos",
                    "Outras Entradas Avulsas",
                ]

            categoria_mov = col_v2.selectbox(
                "Categoria",
                categorias_opcoes
            )

            col_f1, col_f2 = st.columns(2)

            forma_mov = col_f1.selectbox(
                "Forma de Pagamento / Recebimento",
                [
                    "Pix",
                    "Cartão de Crédito",
                    "Cartão de Débito",
                    "Dinheiro",
                    "Transferência / TED"
                ]
            )

            descricao_mov = col_f2.text_input(
                "Descrição / Observação",
                placeholder=(
                    "Ex.: Compra de novo balcão para bar, "
                    "Anúncio Meta Ads, etc."
                )
            )

            btn_salvar_manual = st.form_submit_button(
                "💾 Salvar Lançamento",
                use_container_width=True
            )

            if btn_salvar_manual:

                if valor_mov <= 0:

                    st.warning(
                        "⚠️ Informe um valor maior que zero."
                    )

                elif not descricao_mov.strip():

                    st.warning(
                        "⚠️ Forneça uma breve descrição do lançamento."
                    )

                else:

                    try:

                        supabase.table(
                            "Financeiro"
                        ).insert({
                            "data": str(data_mov),
                            "tipo": tipo_mov,
                            "categoria": categoria_mov,
                            "forma_pagamento": forma_mov,
                            "descricao": descricao_mov.strip(),
                            "valor": valor_mov,
                        }).execute()

                        st.toast(
                            "✅ Lançamento manual gravado no caixa!",
                            icon="💾"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"❌ Erro ao salvar lançamento: {e}"
                        )

    # =========================================================
    # 📄 TAB 5: EXTRATO
    # =========================================================

    with tab5:

        st.subheader(
            "📄 Extrato Completo do Caixa"
        )

        st.caption(
            "Consulte, filtre e remova qualquer movimentação "
            "financeira salva no banco."
        )

        res_extrato = (
            supabase
            .table("Financeiro")
            .select("*")
            .order("data", desc=True)
            .execute()
        )

        df_extrato = pd.DataFrame(
            res_extrato.data or []
        )

        if df_extrato.empty:

            st.info(
                "Nenhuma transação cadastrada até o momento."
            )

        else:

            col_f1, col_f2 = st.columns(2)

            tipos_presentes = list(
                df_extrato["tipo"].unique()
            )

            filtro_tipo = col_f1.multiselect(
                "Filtrar por Tipo",
                tipos_presentes,
                default=tipos_presentes
            )

            if "categoria" in df_extrato.columns:

                cats_presentes = [
                    c
                    for c in df_extrato[
                        "categoria"
                    ]
                    .dropna()
                    .unique()
                    if c
                ]

                filtro_cat = col_f2.multiselect(
                    "Filtrar por Categoria",
                    cats_presentes,
                    default=cats_presentes
                )

            else:

                filtro_cat = []

            # -------------------------------------------------
            # FILTROS
            # -------------------------------------------------

            df_exibicao = df_extrato[
                df_extrato["tipo"].isin(
                    filtro_tipo
                )
            ]

            if (
                filtro_cat
                and
                "categoria" in df_exibicao.columns
            ):

                df_exibicao = df_exibicao[
                    df_exibicao[
                        "categoria"
                    ].isin(filtro_cat)
                ]

            st.dataframe(
                df_exibicao,
                use_container_width=True,
                hide_index=True
            )

            # -------------------------------------------------
            # EXCLUSÃO
            # -------------------------------------------------

            with st.expander(
                "🗑️ Excluir lançamento incorreto"
            ):

                id_excluir = st.number_input(
                    "Insira o ID do lançamento",
                    min_value=1,
                    step=1
                )

                if st.button(
                    "❌ Excluir do Banco de Dados",
                    type="primary"
                ):

                    try:

                        supabase.table(
                            "Financeiro"
                        ).delete().eq(
                            "id",
                            id_excluir
                        ).execute()

                        st.toast(
                            f"✅ Lançamento #{id_excluir} removido!",
                            icon="🗑️"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Erro ao excluir registro: {e}"
                        )
elif menu == "Pacotes":

    st.title("📦 Cadastro de Serviços")

    if "editar_pacote" not in st.session_state:
        st.session_state["editar_pacote"] = None

    # ------------------------------------------------------------
    # Função auxiliar: limpa os widgets de produtos do session_state
    # Isso é necessário porque o Streamlit ignora o "value=" de um
    # widget se a "key" dele já existe no session_state. Sem isso,
    # ao editar um pacote os checkboxes/valores antigos não somem
    # e os novos (vindos do banco) não aparecem marcados.
    # ------------------------------------------------------------
    def limpar_widgets_produtos():
        chaves = [
            k for k in list(st.session_state.keys())
            if k.startswith("produto_")
            or k.startswith("part_")
            or k.startswith("qtd_")
        ]
        for k in chaves:
            del st.session_state[k]

    aba_cadastro, aba_gerenciar = st.tabs([
        "➕ Cadastro",
        "📋 Gerenciar"
    ])

    # ==========================================================
    # CADASTRO
    # ==========================================================
    with aba_cadastro:

        pacote = None
        dados = {}
        produtos_edicao = {}

        if st.session_state["editar_pacote"]:

            resposta = supabase.table("pacotes")\
                .select("*")\
                .eq("id", st.session_state["editar_pacote"])\
                .single()\
                .execute()

            pacote = resposta.data

            dados = pacote.get("dados") or {}

            vinculados = supabase.table("pacote_produtos")\
                .select("*")\
                .eq("pacote_id", pacote["id"])\
                .execute().data

            for item in vinculados:
                produtos_edicao[item["estoque_id"]] = item

            st.info(f"✏️ Editando: **{pacote['nome']}**")

        st.subheader("📦 Dados do Serviço")

        nome = st.text_input(
            "Nome",
            value=pacote["nome"] if pacote else ""
        )

        categorias = [
            "Receptivo",
            "Open Bar",
            "Bar Especial",
            "Premium",
            "Estação",
            "Personalizado"
        ]

        categoria = st.selectbox(
            "Categoria",
            categorias,
            index=categorias.index(pacote["categoria"]) if pacote else 0
        )

        descricao = st.text_area(
            "Descrição",
            value=pacote["descricao"] if pacote else ""
        )

        ativo = st.checkbox(
            "Serviço ativo",
            value=pacote["ativo"] if pacote else True
        )

        st.divider()

        st.subheader("⚙️ Parâmetros")

        percentual_consumo = st.number_input(
            "Percentual de consumo (%)",
            value=float(dados.get("percentual_consumo", 30))
        )

        doses_pessoa = st.number_input(
            "Doses por pessoa",
            value=float(dados.get("doses_pessoa", 4))
        )

        ml_dose = st.number_input(
            "ML por dose",
            value=float(dados.get("ml_dose", 50))
        )

        markup = st.number_input(
            "Markup",
            value=float(dados.get("markup", 3))
        )

        st.divider()

        st.subheader("🍾 Produtos do Serviço")

        estoque = supabase.table("estoque")\
            .select("*")\
            .order("produto")\
            .order("marca")\
            .execute().data

        if not estoque:
            st.warning("Nenhum produto cadastrado no estoque ainda.")

        produtos_servico = []

        for item in estoque:

            salvo = produtos_edicao.get(item["id"])

            marcado = st.checkbox(
                f'{item["produto"]} - {item["marca"]}',
                value=salvo is not None,
                key=f'produto_{item["id"]}'
            )

            if marcado:

                c1, c2 = st.columns(2)

                with c1:

                    participacao = st.number_input(
                        f"Participação {item['marca']} (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=float(salvo["participacao"]) if salvo else 0.0,
                        key=f'part_{item["id"]}'
                    )

                with c2:

                    quantidade = st.number_input(
                        f"Qtd Base {item['marca']}",
                        min_value=0.0,
                        value=float(salvo["quantidade"]) if salvo else 1.0,
                        key=f'qtd_{item["id"]}'
                    )

                produtos_servico.append({
                    "estoque_id": item["id"],
                    "participacao": participacao,
                    "quantidade": quantidade,
                    "unidade": None
                })

        st.divider()

        texto_botao = "💾 Atualizar Serviço" if pacote else "💾 Salvar Serviço"

        if st.button(texto_botao, use_container_width=True):

            if not nome.strip():
                st.error("Informe o nome do serviço antes de salvar.")
                st.stop()

            dados = {
                "percentual_consumo": percentual_consumo,
                "doses_pessoa": doses_pessoa,
                "ml_dose": ml_dose,
                "markup": markup
            }

            try:

                if pacote:

                    supabase.table("pacotes")\
                        .update({
                            "nome": nome,
                            "categoria": categoria,
                            "descricao": descricao,
                            "ativo": ativo,
                            "dados": dados
                        })\
                        .eq("id", pacote["id"])\
                        .execute()

                    pacote_id = pacote["id"]

                    supabase.table("pacote_produtos")\
                        .delete()\
                        .eq("pacote_id", pacote_id)\
                        .execute()

                else:

                    resposta = supabase.table("pacotes")\
                        .insert({
                            "nome": nome,
                            "categoria": categoria,
                            "descricao": descricao,
                            "ativo": ativo,
                            "dados": dados
                        })\
                        .execute()

                    pacote_id = resposta.data[0]["id"]

                for produto in produtos_servico:

                    supabase.table("pacote_produtos")\
                        .insert({
                            "pacote_id": pacote_id,
                            "estoque_id": produto["estoque_id"],
                            "participacao": produto["participacao"],
                            "quantidade": produto["quantidade"],
                            "obrigatorio": True
                        })\
                        .execute()

                # limpa os widgets antigos para a próxima renderização
                # não "herdar" valores da edição/cadastro anterior
                limpar_widgets_produtos()

                st.session_state["editar_pacote"] = None

                st.success("Serviço salvo com sucesso!")

                st.rerun()

            except Exception as e:
                st.error("Ocorreu um erro ao salvar o serviço.")
                st.exception(e)

        if pacote:
            if st.button("✖️ Cancelar edição"):
                limpar_widgets_produtos()
                st.session_state["editar_pacote"] = None
                st.rerun()

    # ==========================================================
    # GERENCIAR
    # ==========================================================
    with aba_gerenciar:

        st.subheader("📋 Serviços Cadastrados")

        pacotes = supabase.table("pacotes")\
            .select("*")\
            .order("nome")\
            .execute().data

        if not pacotes:

            st.info("Nenhum serviço cadastrado.")

        else:

            for pacote in pacotes:

                with st.container(border=True):

                    col1, col2, col3 = st.columns([8, 1, 1])

                    with col1:

                        st.markdown(f"### 📦 {pacote['nome']}")

                        st.caption(
                            f"{pacote['categoria']} • {'Ativo' if pacote['ativo'] else 'Inativo'}"
                        )

                        if pacote["descricao"]:
                            st.write(pacote["descricao"])

                    with col2:

                        if st.button(
                            "✏️",
                            key=f"editar_{pacote['id']}"
                        ):
                            # limpa widgets antigos ANTES de trocar de pacote,
                            # senão o Streamlit mantém valores da tela anterior
                            limpar_widgets_produtos()

                            st.session_state["editar_pacote"] = pacote["id"]

                            st.rerun()

                    with col3:

                        if st.button(
                            "🗑",
                            key=f"excluir_{pacote['id']}"
                        ):

                            supabase.table("pacote_produtos")\
                                .delete()\
                                .eq("pacote_id", pacote["id"])\
                                .execute()

                            supabase.table("pacotes")\
                                .delete()\
                                .eq("id", pacote["id"])\
                                .execute()

                            if (
                                st.session_state["editar_pacote"]
                                == pacote["id"]
                            ):
                                limpar_widgets_produtos()
                                st.session_state["editar_pacote"] = None

                            st.success("Serviço excluído!")

                            st.rerun()
