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
    st.caption(
        "Resultado econômico dos eventos com base no fechamento oficial do CMV. "
        "Eventos fechados usam faturamento e custos reais; eventos futuros permanecem como previsão."
    )

    # =========================================================
    # HELPERS
    # =========================================================
    def _rel_num(valor, padrao=0.0):
        try:
            if valor is None:
                return float(padrao)
            if pd.isna(valor):
                return float(padrao)
            return float(valor)
        except Exception:
            return float(padrao)

    def _rel_moeda(valor):
        try:
            valor = float(valor or 0)
        except Exception:
            valor = 0.0
        txt = f"{valor:,.2f}"
        txt = txt.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {txt}"

    def _rel_percentual(valor):
        try:
            return f"{float(valor or 0):.2f}%".replace(".", ",")
        except Exception:
            return "0,00%"

    meses_nomes = [
        "Janeiro", "Fevereiro", "Março", "Abril",
        "Maio", "Junho", "Julho", "Agosto",
        "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    def _rel_carregar_metas(ano):
        try:
            dados = (
                supabase.table("metas_mensais")
                .select("*")
                .eq("ano", int(ano))
                .order("mes")
                .execute()
                .data
                or []
            )
            return pd.DataFrame(dados)
        except Exception:
            return pd.DataFrame()

    def _rel_salvar_meta(ano, mes, valor):
        existente = (
            supabase.table("metas_mensais")
            .select("id")
            .eq("ano", int(ano))
            .eq("mes", int(mes))
            .execute()
        )

        dados = {
            "ano": int(ano),
            "mes": int(mes),
            "mes_ano": f"{int(ano)}-{int(mes):02d}",
            "meta_valor": float(valor or 0),
            "atualizado_em": datetime.now().isoformat(),
        }

        if existente.data:
            (
                supabase.table("metas_mensais")
                .update(dados)
                .eq("ano", int(ano))
                .eq("mes", int(mes))
                .execute()
            )
        else:
            supabase.table("metas_mensais").insert(dados).execute()

    # =========================================================
    # FILTROS DE DATA / PERÍODO
    # =========================================================
    col_p, col_i, col_f = st.columns([2, 1, 1])

    periodo = col_p.selectbox(
        "📅 Período",
        ["Este ano", "Este mês", "Últimos 30 dias", "Todos"],
        key="dash_periodo_real"
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
        key="dash_real_dt_i"
    )

    data_f = col_f.date_input(
        "🗓️ Data final",
        value=dt_fim,
        key="dash_real_dt_f"
    )

    # =========================================================
    # CARREGAMENTO DAS BASES
    # =========================================================
    try:
        response_eventos = (
            supabase.table("eventos")
            .select("*")
            .in_("status", ["aprovado", "finalizado", "concluido", "pago"])
            .execute()
        )
        df_eventos = pd.DataFrame(response_eventos.data or [])
    except Exception as erro:
        st.error(f"Erro ao carregar eventos: {erro}")
        df_eventos = pd.DataFrame()

    try:
        response_aditivos = (
            supabase.table("aditivos_evento")
            .select("*")
            .execute()
        )
        df_aditivos = pd.DataFrame(response_aditivos.data or [])
    except Exception:
        df_aditivos = pd.DataFrame()

    try:
        response_fin = (
            supabase.table("Financeiro")
            .select("*")
            .execute()
        )
        df_financeiro = pd.DataFrame(response_fin.data or [])
    except Exception:
        try:
            response_fin = (
                supabase.table("financeiro")
                .select("*")
                .execute()
            )
            df_financeiro = pd.DataFrame(response_fin.data or [])
        except Exception:
            df_financeiro = pd.DataFrame()

    # =========================================================
    # PREPARAÇÃO DOS EVENTOS
    # =========================================================
    if not df_eventos.empty:

        df_eventos["data_dt"] = pd.to_datetime(
            df_eventos.get("data"),
            errors="coerce"
        )

        for col in [
            "venda", "custo", "convidados",
            "cmv_faturamento_total",
            "cmv_custo_produtos",
            "cmv_custo_equipe",
            "cmv_custos_extras",
            "cmv_custo_total",
            "cmv_percentual",
            "cmv_lucro_real",
        ]:
            if col not in df_eventos.columns:
                df_eventos[col] = None

        df_eventos["venda_base"] = pd.to_numeric(
            df_eventos["venda"], errors="coerce"
        ).fillna(0)

        df_eventos["custo_previsto"] = pd.to_numeric(
            df_eventos["custo"], errors="coerce"
        ).fillna(0)

        df_eventos["convidados"] = pd.to_numeric(
            df_eventos["convidados"], errors="coerce"
        ).fillna(0)

        # -----------------------------------------------------
        # ADENDOS = RECEITA EXTRA
        # Cancelados não entram no faturamento.
        # -----------------------------------------------------
        if (
            not df_aditivos.empty
            and "evento_id" in df_aditivos.columns
            and "valor_cliente" in df_aditivos.columns
        ):
            adit = df_aditivos.copy()

            if "status" in adit.columns:
                adit = adit[
                    adit["status"].fillna("").astype(str).str.lower() != "cancelado"
                ].copy()

            adit["valor_cliente"] = pd.to_numeric(
                adit["valor_cliente"], errors="coerce"
            ).fillna(0)

            aditivos_agrupados = (
                adit.groupby("evento_id", as_index=False)["valor_cliente"].sum()
            )
            aditivos_agrupados.rename(
                columns={"valor_cliente": "aditivos_total"},
                inplace=True
            )

            df_eventos = df_eventos.merge(
                aditivos_agrupados,
                left_on="id",
                right_on="evento_id",
                how="left"
            )

            df_eventos["aditivos_total"] = (
                pd.to_numeric(df_eventos["aditivos_total"], errors="coerce")
                .fillna(0)
            )
        else:
            df_eventos["aditivos_total"] = 0.0

        df_eventos["faturamento_calculado"] = (
            df_eventos["venda_base"] + df_eventos["aditivos_total"]
        )

        if "cmv_status" in df_eventos.columns:
            df_eventos["cmv_fechado"] = (
                df_eventos["cmv_status"]
                .fillna("aberto")
                .astype(str)
                .str.lower()
                .eq("fechado")
            )
        else:
            df_eventos["cmv_fechado"] = False

        # -----------------------------------------------------
        # FATURAMENTO REAL
        # Fechado: snapshot do CMV.
        # Aberto: contrato + adendos apenas como referência.
        # -----------------------------------------------------
        fat_snapshot = pd.to_numeric(
            df_eventos["cmv_faturamento_total"], errors="coerce"
        )

        df_eventos["faturamento_evento"] = df_eventos[
            "faturamento_calculado"
        ].astype(float)

        mask_fat_real = df_eventos["cmv_fechado"] & fat_snapshot.notna()
        df_eventos.loc[mask_fat_real, "faturamento_evento"] = (
            fat_snapshot[mask_fat_real]
        )

        # -----------------------------------------------------
        # CUSTO REAL
        # Fechado: snapshot oficial do CMV.
        # Aberto: custo previsto apenas para referência.
        # -----------------------------------------------------
        custo_snapshot = pd.to_numeric(
            df_eventos["cmv_custo_total"], errors="coerce"
        )

        df_eventos["custo_evento"] = df_eventos["custo_previsto"].astype(float)

        mask_custo_real = df_eventos["cmv_fechado"] & custo_snapshot.notna()
        df_eventos.loc[mask_custo_real, "custo_evento"] = (
            custo_snapshot[mask_custo_real]
        )

        # Componentes reais do custo
        df_eventos["custo_produtos_real"] = pd.to_numeric(
            df_eventos["cmv_custo_produtos"], errors="coerce"
        ).fillna(0)

        df_eventos["custo_equipe_real"] = pd.to_numeric(
            df_eventos["cmv_custo_equipe"], errors="coerce"
        ).fillna(0)

        df_eventos["custos_extras_real"] = pd.to_numeric(
            df_eventos["cmv_custos_extras"], errors="coerce"
        ).fillna(0)

        # -----------------------------------------------------
        # LUCRO / CMV / MARGEM
        # -----------------------------------------------------
        lucro_snapshot = pd.to_numeric(
            df_eventos["cmv_lucro_real"], errors="coerce"
        )

        df_eventos["lucro_evento"] = (
            df_eventos["faturamento_evento"]
            - df_eventos["custo_evento"]
        )

        mask_lucro_real = df_eventos["cmv_fechado"] & lucro_snapshot.notna()
        df_eventos.loc[mask_lucro_real, "lucro_evento"] = (
            lucro_snapshot[mask_lucro_real]
        )

        cmv_snapshot = pd.to_numeric(
            df_eventos["cmv_percentual"], errors="coerce"
        )

        df_eventos["cmv_real"] = 0.0
        mask_receita = df_eventos["faturamento_evento"] > 0
        df_eventos.loc[mask_receita, "cmv_real"] = (
            df_eventos.loc[mask_receita, "custo_evento"]
            / df_eventos.loc[mask_receita, "faturamento_evento"]
            * 100
        )

        mask_cmv_real = df_eventos["cmv_fechado"] & cmv_snapshot.notna()
        df_eventos.loc[mask_cmv_real, "cmv_real"] = (
            cmv_snapshot[mask_cmv_real]
        )

        df_eventos["margem_real"] = 0.0
        df_eventos.loc[mask_receita, "margem_real"] = (
            df_eventos.loc[mask_receita, "lucro_evento"]
            / df_eventos.loc[mask_receita, "faturamento_evento"]
            * 100
        )

        # -----------------------------------------------------
        # RESERVA: 35% SOMENTE SOBRE LUCRO POSITIVO
        # -----------------------------------------------------
        df_eventos["reserva_evento"] = df_eventos["lucro_evento"].apply(
            lambda x: float(x) * 0.35 if _rel_num(x) > 0 else 0.0
        )

        df_eventos["disponivel_evento"] = (
            df_eventos["lucro_evento"]
            - df_eventos["reserva_evento"]
        )

        df_eventos["previsto_x_real"] = (
            df_eventos["custo_previsto"]
            - df_eventos["custo_evento"]
        )

        df_eventos["fonte_resultado"] = df_eventos["cmv_fechado"].map(
            {True: "Real — CMV Fechado", False: "Previsto / Em aberto"}
        )

        df = df_eventos[
            (df_eventos["data_dt"].dt.date >= data_i)
            & (df_eventos["data_dt"].dt.date <= data_f)
        ].copy()

    else:
        df = pd.DataFrame()

    # =========================================================
    # PRÓXIMOS EVENTOS
    # =========================================================
    st.markdown("### 📅 Próximos Eventos")

    if not df_eventos.empty:
        proximos = df_eventos[
            (df_eventos["data_dt"].dt.date >= hoje.date())
            & (df_eventos["status"].astype(str).str.lower() == "aprovado")
            & (~df_eventos["cmv_fechado"])
        ].copy()

        proximos = proximos.sort_values("data_dt")

        if not proximos.empty:
            prox = proximos[
                [
                    "data",
                    "cliente",
                    "cidade",
                    "convidados",
                    "venda_base",
                    "custo_previsto",
                ]
            ].copy()

            prox.rename(
                columns={
                    "data": "Data",
                    "cliente": "Cliente",
                    "cidade": "Cidade",
                    "convidados": "Convidados",
                    "venda_base": "Venda Prevista",
                    "custo_previsto": "Custo Previsto",
                },
                inplace=True
            )

            st.dataframe(
                prox,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Venda Prevista": st.column_config.NumberColumn(
                        format="R$ %.2f"
                    ),
                    "Custo Previsto": st.column_config.NumberColumn(
                        format="R$ %.2f"
                    ),
                }
            )
        else:
            st.info("Nenhum próximo evento confirmado.")
    else:
        st.info("Nenhum próximo evento confirmado.")

    # =========================================================
    # BASE REAL: SOMENTE CMV FECHADO
    # =========================================================
    if not df.empty:
        df_real = df[df["cmv_fechado"]].copy()
        df_abertos = df[~df["cmv_fechado"]].copy()
    else:
        df_real = pd.DataFrame()
        df_abertos = pd.DataFrame()

    # Base histórica completa para comparativos anuais e metas
    if not df_eventos.empty:
        df_real_total = df_eventos[df_eventos["cmv_fechado"]].copy()
    else:
        df_real_total = pd.DataFrame()

    # Eventos passados ainda sem fechamento
    if not df_abertos.empty:
        passados_abertos = df_abertos[
            df_abertos["data_dt"].dt.date < hoje.date()
        ]
        if not passados_abertos.empty:
            st.warning(
                f"⚠️ {len(passados_abertos)} evento(s) passado(s) no período ainda não possuem "
                "CMV fechado. Eles não entram nos resultados reais abaixo."
            )

    # =========================================================
    # CONSOLIDAÇÃO REAL
    # =========================================================
    if not df_real.empty:
        faturamento = float(df_real["faturamento_evento"].sum())
        custos = float(df_real["custo_evento"].sum())
        lucro_total = float(df_real["lucro_evento"].sum())
        reserva_emergencia_total = float(df_real["reserva_evento"].sum())
        caixa_disponivel_total = float(df_real["disponivel_evento"].sum())
        custo_produtos_total = float(df_real["custo_produtos_real"].sum())
        custo_equipe_total = float(df_real["custo_equipe_real"].sum())
        custos_extras_total = float(df_real["custos_extras_real"].sum())
        custo_previsto_total = float(df_real["custo_previsto"].sum())
    else:
        faturamento = 0.0
        custos = 0.0
        lucro_total = 0.0
        reserva_emergencia_total = 0.0
        caixa_disponivel_total = 0.0
        custo_produtos_total = 0.0
        custo_equipe_total = 0.0
        custos_extras_total = 0.0
        custo_previsto_total = 0.0

    margem = (
        lucro_total / faturamento * 100
        if faturamento > 0 else 0.0
    )

    cmv_consolidado = (
        custos / faturamento * 100
        if faturamento > 0 else 0.0
    )

    diferenca_previsto_real = (
        custo_previsto_total - custos
    )

    # =========================================================
    # ABAS
    # =========================================================
    (
        tab_visao,
        tab_dre,
        tab_metas,
        tab_anual,
        tab_fechamento,
        tab_fin,
        tab_vendas,
        tab_prod,
    ) = st.tabs([
        "📊 Visão Geral",
        "🧾 DRE",
        "🎯 Metas & Crescimento",
        "📈 Comparativo Anual",
        "🏁 Fechamento Anual",
        "💰 Financeiro",
        "💵 Vendas",
        "📦 Produtos"
    ])

    # =========================================================
    # TAB 1 — VISÃO GERAL
    # =========================================================
    with tab_visao:

        st.markdown("## 📊 Resultado Real Consolidado")

        with st.container(border=True):
            st.markdown("#### 💰 Receita e Resultado")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Faturamento Real", _rel_moeda(faturamento))
            c2.metric("Custo Real Total", _rel_moeda(custos))
            c3.metric("Lucro Real", _rel_moeda(lucro_total))
            c4.metric("Margem Real", _rel_percentual(margem))

        with st.container(border=True):
            st.markdown("#### 📦 Composição do Custo Real")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Produtos Consumidos", _rel_moeda(custo_produtos_total))
            c2.metric("Cachês / Equipe", _rel_moeda(custo_equipe_total))
            c3.metric("Outros Custos", _rel_moeda(custos_extras_total))
            c4.metric("CMV Consolidado", _rel_percentual(cmv_consolidado))

        with st.container(border=True):
            st.markdown("#### 🛡️ Destinação do Lucro")
            c1, c2, c3 = st.columns(3)
            c1.metric("Lucro Real", _rel_moeda(lucro_total))
            c2.metric("Reserva de Emergência (35%)", _rel_moeda(reserva_emergencia_total))
            c3.metric("Disponível após Reserva (65%)", _rel_moeda(caixa_disponivel_total))

        with st.container(border=True):
            st.markdown("#### 🎯 Previsto x Real")
            c1, c2, c3 = st.columns(3)
            c1.metric("Custo Previsto", _rel_moeda(custo_previsto_total))
            c2.metric("Custo Real", _rel_moeda(custos))
            c3.metric(
                "Diferença",
                _rel_moeda(diferenca_previsto_real),
                help="Positivo = custo real abaixo do previsto. Negativo = custo real acima do previsto."
            )

        st.markdown("### 📋 Resultado por Evento")

        if not df_real.empty:
            df_resultado = df_real[
                [
                    "cliente",
                    "data",
                    "faturamento_evento",
                    "custo_produtos_real",
                    "custo_equipe_real",
                    "custos_extras_real",
                    "custo_evento",
                    "lucro_evento",
                    "cmv_real",
                    "margem_real",
                    "reserva_evento",
                    "disponivel_evento",
                    "previsto_x_real",
                ]
            ].copy()

            df_resultado.rename(
                columns={
                    "cliente": "Cliente",
                    "data": "Data",
                    "faturamento_evento": "Faturamento Real",
                    "custo_produtos_real": "Produtos",
                    "custo_equipe_real": "Equipe",
                    "custos_extras_real": "Outros",
                    "custo_evento": "Custo Real",
                    "lucro_evento": "Lucro Real",
                    "cmv_real": "CMV (%)",
                    "margem_real": "Margem (%)",
                    "reserva_evento": "Reserva 35%",
                    "disponivel_evento": "Disponível 65%",
                    "previsto_x_real": "Previsto x Real",
                },
                inplace=True
            )

            st.dataframe(
                df_resultado,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Faturamento Real": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Produtos": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Equipe": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Outros": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Custo Real": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Lucro Real": st.column_config.NumberColumn(format="R$ %.2f"),
                    "CMV (%)": st.column_config.NumberColumn(format="%.2f%%"),
                    "Margem (%)": st.column_config.NumberColumn(format="%.2f%%"),
                    "Reserva 35%": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Disponível 65%": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Previsto x Real": st.column_config.NumberColumn(format="R$ %.2f"),
                }
            )

            st.markdown("### 📈 Faturamento, Custos e Lucro — Mês a Mês")

            df_mensal = df_real.dropna(subset=["data_dt"]).copy()
            if not df_mensal.empty:
                df_mensal["mes_ano"] = df_mensal["data_dt"].dt.strftime("%Y-%m")

                consolidado_mensal = (
                    df_mensal.groupby("mes_ano")[
                        ["faturamento_evento", "custo_evento", "lucro_evento"]
                    ]
                    .sum()
                )

                consolidado_mensal.rename(
                    columns={
                        "faturamento_evento": "Faturamento Real",
                        "custo_evento": "Custo Real",
                        "lucro_evento": "Lucro Real",
                    },
                    inplace=True
                )

                st.line_chart(consolidado_mensal)
        else:
            st.info("Nenhum evento com CMV fechado no período selecionado.")

    # =========================================================
    # TAB 2 — DRE GERENCIAL
    # =========================================================
    with tab_dre:

        st.markdown("## 🧾 DRE Gerencial dos Eventos")
        st.caption(
            "Resultado gerencial baseado apenas em eventos com CMV fechado. "
            "A Reserva de Emergência é mostrada como destinação do lucro, não como despesa."
        )

        anos_dre = sorted(
            set(df_real_total["data_dt"].dropna().dt.year.astype(int).tolist())
        ) if not df_real_total.empty else [hoje.year]

        if not anos_dre:
            anos_dre = [hoje.year]

        d1, d2 = st.columns(2)
        ano_dre = d1.selectbox(
            "Ano",
            anos_dre,
            index=len(anos_dre) - 1,
            key="rel_v3_dre_ano"
        )
        mes_dre = d2.selectbox(
            "Mês",
            list(range(1, 13)),
            index=max(0, min(11, hoje.month - 1)),
            format_func=lambda m: meses_nomes[m - 1],
            key="rel_v3_dre_mes"
        )

        dre_base = df_real_total[
            (df_real_total["data_dt"].dt.year == int(ano_dre))
            & (df_real_total["data_dt"].dt.month == int(mes_dre))
        ].copy() if not df_real_total.empty else pd.DataFrame()

        if dre_base.empty:
            st.info("Nenhum evento com CMV fechado nesse mês.")
        else:
            venda_original = float(dre_base["venda_base"].sum())
            adendos = float(dre_base["aditivos_total"].sum())
            fat_real = float(dre_base["faturamento_evento"].sum())
            ajuste_receita = fat_real - venda_original - adendos

            prod = float(dre_base["custo_produtos_real"].sum())
            equipe = float(dre_base["custo_equipe_real"].sum())
            extras = float(dre_base["custos_extras_real"].sum())
            custo_real = float(dre_base["custo_evento"].sum())
            ajuste_custo = custo_real - prod - equipe - extras

            lucro_dre = float(dre_base["lucro_evento"].sum())
            reserva_dre = float(dre_base["reserva_evento"].sum())
            disponivel_dre = float(dre_base["disponivel_evento"].sum())
            cmv_dre = custo_real / fat_real * 100 if fat_real > 0 else 0.0
            margem_dre = lucro_dre / fat_real * 100 if fat_real > 0 else 0.0

            linhas = [
                ("Venda original dos eventos", venda_original, "moeda"),
                ("(+) Adendos / receita extra", adendos, "moeda"),
            ]
            if abs(ajuste_receita) >= 0.01:
                linhas.append(("(+/-) Ajuste de fechamento", ajuste_receita, "moeda"))
            linhas += [
                ("= FATURAMENTO REAL", fat_real, "moeda"),
                ("(-) Produtos consumidos", -prod, "moeda"),
                ("(-) Cachês / equipe", -equipe, "moeda"),
                ("(-) Outros custos dos eventos", -extras, "moeda"),
            ]
            if abs(ajuste_custo) >= 0.01:
                linhas.append(("(-/+) Ajuste de custos", -ajuste_custo, "moeda"))
            linhas += [
                ("= CUSTO REAL TOTAL", -custo_real, "moeda"),
                ("= RESULTADO OPERACIONAL", lucro_dre, "moeda"),
                ("CMV", cmv_dre, "pct"),
                ("Margem", margem_dre, "pct"),
                ("Reserva de Emergência — 35%", reserva_dre, "moeda"),
                ("Disponível após Reserva — 65%", disponivel_dre, "moeda"),
            ]

            dre_df = pd.DataFrame(linhas, columns=["DRE", "_valor", "_tipo"])
            dre_df["Valor"] = dre_df.apply(
                lambda r: _rel_percentual(r["_valor"])
                if r["_tipo"] == "pct"
                else _rel_moeda(r["_valor"]),
                axis=1
            )

            st.dataframe(
                dre_df[["DRE", "Valor"]],
                use_container_width=True,
                hide_index=True
            )

            with st.container(border=True):
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Faturamento Real", _rel_moeda(fat_real))
                k2.metric("Custo Real", _rel_moeda(custo_real))
                k3.metric("Lucro Real", _rel_moeda(lucro_dre))
                k4.metric("Margem", _rel_percentual(margem_dre))

    # =========================================================
    # TAB 2 — FINANCEIRO
    # Separa resultado econômico de caixa realizado.
    # =========================================================
    with tab_fin:

        st.markdown("## 💰 Resultado Econômico x Caixa Realizado")

        with st.container(border=True):
            st.markdown("#### 📊 Resultado Econômico dos Eventos")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Faturamento Real", _rel_moeda(faturamento))
            c2.metric("Custos Reais", _rel_moeda(custos))
            c3.metric("Lucro Real", _rel_moeda(lucro_total))
            c4.metric("Reserva 35%", _rel_moeda(reserva_emergencia_total))

        st.caption(
            "O resultado econômico usa o CMV fechado. Consumo de estoque é custo do evento, "
            "mas não é automaticamente uma saída de caixa nesta tela."
        )

        # Caixa realizado vem apenas da tabela Financeiro
        fin_filtrado = df_financeiro.copy()

        if not fin_filtrado.empty:
            if "valor" not in fin_filtrado.columns:
                fin_filtrado["valor"] = 0.0

            fin_filtrado["valor"] = pd.to_numeric(
                fin_filtrado["valor"], errors="coerce"
            ).fillna(0)

            if "data" in fin_filtrado.columns:
                fin_filtrado["data_dt"] = pd.to_datetime(
                    fin_filtrado["data"], errors="coerce"
                )
                fin_filtrado = fin_filtrado[
                    (fin_filtrado["data_dt"].dt.date >= data_i)
                    & (fin_filtrado["data_dt"].dt.date <= data_f)
                ].copy()

            tipo_lower = fin_filtrado.get(
                "tipo", pd.Series("", index=fin_filtrado.index)
            ).fillna("").astype(str).str.lower()

            entradas_caixa = float(
                fin_filtrado.loc[tipo_lower == "entrada", "valor"].sum()
            )
            saidas_caixa = float(
                fin_filtrado.loc[
                    tipo_lower.isin(["saída", "saida"]),
                    "valor"
                ].sum()
            )
        else:
            entradas_caixa = 0.0
            saidas_caixa = 0.0

        saldo_caixa = entradas_caixa - saidas_caixa

        with st.container(border=True):
            st.markdown("#### 🏦 Movimentação de Caixa Registrada")
            c1, c2, c3 = st.columns(3)
            c1.metric("Entradas Realizadas", _rel_moeda(entradas_caixa))
            c2.metric("Saídas Realizadas", _rel_moeda(saidas_caixa))
            c3.metric("Saldo de Caixa", _rel_moeda(saldo_caixa))

        if not fin_filtrado.empty:
            st.markdown("### 📋 Movimentações Financeiras")
            colunas_fin = [
                c for c in [
                    "data", "tipo", "categoria",
                    "forma_pagamento", "descricao", "valor"
                ]
                if c in fin_filtrado.columns
            ]

            st.dataframe(
                fin_filtrado[colunas_fin],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "valor": st.column_config.NumberColumn(
                        "Valor", format="R$ %.2f"
                    )
                }
            )
        else:
            st.info("Nenhuma movimentação financeira no período.")

    # =========================================================
    # TAB 3 — VENDAS
    # =========================================================
    with tab_vendas:

        st.markdown("## 📈 Vendas e Faturamento")

        total_eventos_fechados = len(df_real)
        ticket_medio = (
            faturamento / total_eventos_fechados
            if total_eventos_fechados > 0
            else 0.0
        )

        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Eventos Fechados", total_eventos_fechados)
            c2.metric("Faturamento Real", _rel_moeda(faturamento))
            c3.metric("Ticket Médio Real", _rel_moeda(ticket_medio))

        cliente_busca = st.text_input(
            "🔎 Buscar cliente",
            key="relatorio_real_busca_cliente"
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
                .str.contains(cliente_busca, case=False, na=False)
            ]

        if not df_vendas.empty:
            venda_exibir = df_vendas[
                [
                    "cliente",
                    "data",
                    "venda_base",
                    "aditivos_total",
                    "faturamento_evento",
                    "custo_evento",
                    "lucro_evento",
                    "cmv_real",
                    "fonte_resultado",
                ]
            ].copy()

            venda_exibir.rename(
                columns={
                    "cliente": "Cliente",
                    "data": "Data",
                    "venda_base": "Contrato Base",
                    "aditivos_total": "Adendos",
                    "faturamento_evento": "Faturamento",
                    "custo_evento": "Custo",
                    "lucro_evento": "Lucro",
                    "cmv_real": "CMV (%)",
                    "fonte_resultado": "Fonte",
                },
                inplace=True
            )

            st.dataframe(
                venda_exibir,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Contrato Base": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Adendos": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Faturamento": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Custo": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Lucro": st.column_config.NumberColumn(format="R$ %.2f"),
                    "CMV (%)": st.column_config.NumberColumn(format="%.2f%%"),
                }
            )
        else:
            st.info("Nenhum evento encontrado no período.")

    # =========================================================
    # METAS & CRESCIMENTO — V3.1
    # =========================================================
    with tab_metas:

        st.markdown("## 🎯 Metas & Crescimento")
        st.caption(
            "Primeiro você define e salva as metas. Depois, quando quiser preparar o próximo ano, "
            "o sistema usa o faturamento real do mesmo mês do ano anterior. "
            "Se não houve faturamento naquele mês, usa uma meta mínima definida por você."
        )

        (
            tab_definir_meta,
            tab_gerar_meta,
            tab_acompanhar_meta,
        ) = st.tabs([
            "✍️ Definir Metas",
            "⚙️ Gerar Próximo Ano",
            "📊 Acompanhamento",
        ])

        # =====================================================
        # A) DEFINIR METAS MANUALMENTE
        # =====================================================
        with tab_definir_meta:

            st.markdown("### ✍️ Definir metas do ano")
            st.caption(
                "Use esta área para cadastrar ou corrigir as metas mensais. "
                "O valor salvo fica gravado por ano + mês no Supabase."
            )

            ano_min_meta = 2025

            if not df_eventos.empty and df_eventos["data_dt"].notna().any():
                ano_min_meta = min(
                    ano_min_meta,
                    int(df_eventos["data_dt"].dropna().dt.year.min())
                )

            anos_definir = list(
                range(ano_min_meta, hoje.year + 4)
            )

            ano_definir = st.selectbox(
                "Ano",
                anos_definir,
                index=(
                    anos_definir.index(hoje.year)
                    if hoje.year in anos_definir
                    else 0
                ),
                key="rel_v31_meta_ano_definir"
            )

            metas_ano_df = _rel_carregar_metas(ano_definir)

            metas_salvas = {}

            if not metas_ano_df.empty:
                for _, registro in metas_ano_df.iterrows():
                    try:
                        metas_salvas[int(registro["mes"])] = _rel_num(
                            registro.get("meta_valor")
                        )
                    except Exception:
                        pass

            dados_metas_manual = []

            for mes in range(1, 13):
                dados_metas_manual.append({
                    "Mês": meses_nomes[mes - 1],
                    "Meta": metas_salvas.get(mes, 1000.0),
                })

            df_metas_manual = pd.DataFrame(
                dados_metas_manual
            )

            editor_metas_manual = st.data_editor(
                df_metas_manual,
                use_container_width=True,
                hide_index=True,
                disabled=["Mês"],
                column_config={
                    "Mês":
                        st.column_config.TextColumn("Mês"),
                    "Meta":
                        st.column_config.NumberColumn(
                            "Meta mensal",
                            min_value=0.0,
                            step=100.0,
                            format="R$ %.2f"
                        ),
                },
                key=f"rel_v31_editor_manual_{ano_definir}"
            )

            meta_anual_manual = float(
                pd.to_numeric(
                    editor_metas_manual["Meta"],
                    errors="coerce"
                ).fillna(0).sum()
            )

            m1, m2 = st.columns([1, 2])

            m1.metric(
                "Meta anual",
                _rel_moeda(meta_anual_manual)
            )

            m2.info(
                "Exemplo do seu fluxo: 2025 e 2026 podem ficar em R$ 1.000 por mês. "
                "Depois você usa a aba 'Gerar Próximo Ano' para montar 2027 automaticamente."
            )

            if st.button(
                f"💾 Salvar metas de {ano_definir}",
                type="primary",
                use_container_width=True,
                key=f"rel_v31_salvar_manual_{ano_definir}"
            ):
                try:
                    for indice, linha in editor_metas_manual.iterrows():
                        _rel_salvar_meta(
                            ano_definir,
                            indice + 1,
                            _rel_num(linha["Meta"])
                        )

                    st.success(
                        f"✅ Metas de {ano_definir} salvas com sucesso."
                    )
                    st.rerun()

                except Exception as erro:
                    st.error(
                        f"Não foi possível salvar as metas: {erro}"
                    )

        # =====================================================
        # B) GERAR META DO PRÓXIMO ANO
        # =====================================================
        with tab_gerar_meta:

            st.markdown("### ⚙️ Gerar metas do próximo ano")
            st.caption(
                "Regra: se o mês teve faturamento, a nova meta é calculada sobre o faturado. "
                "Se não teve faturamento, entra a meta mínima."
            )

            anos_com_base = sorted(
                set(
                    df_real_total["data_dt"]
                    .dropna()
                    .dt.year
                    .astype(int)
                    .tolist()
                )
            ) if not df_real_total.empty else []

            # Permite também usar anos cadastrados em metas,
            # mesmo quando não houve faturamento real.
            anos_candidatos = sorted(
                set(
                    anos_com_base
                    + list(range(2025, hoje.year + 2))
                )
            )

            if not anos_candidatos:
                anos_candidatos = [hoje.year]

            g1, g2, g3 = st.columns(3)

            ano_base_meta = g1.selectbox(
                "Ano-base",
                anos_candidatos,
                index=(
                    anos_candidatos.index(hoje.year)
                    if hoje.year in anos_candidatos
                    else len(anos_candidatos) - 1
                ),
                key="rel_v31_gerar_ano_base"
            )

            ano_destino_meta = int(ano_base_meta) + 1

            crescimento_meta = g2.number_input(
                "Crescimento desejado (%)",
                min_value=0.0,
                max_value=500.0,
                value=15.0,
                step=1.0,
                key="rel_v31_crescimento"
            )

            meta_minima = g3.number_input(
                "Meta mínima sem faturamento",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                key="rel_v31_meta_minima"
            )

            st.info(
                f"Você está preparando as metas de **{ano_destino_meta}** "
                f"usando **{ano_base_meta}** como referência."
            )

            faturamento_base_mensal = pd.Series(
                [0.0] * 12,
                index=range(1, 13),
                dtype=float
            )

            if not df_real_total.empty:
                base_ano = df_real_total[
                    df_real_total["data_dt"].dt.year == int(ano_base_meta)
                ].copy()

                if not base_ano.empty:
                    faturamento_base_mensal = (
                        base_ano.groupby(
                            base_ano["data_dt"].dt.month
                        )["faturamento_evento"]
                        .sum()
                        .reindex(
                            range(1, 13),
                            fill_value=0.0
                        )
                    )

            metas_destino_df = _rel_carregar_metas(
                ano_destino_meta
            )

            metas_destino_salvas = {}

            if not metas_destino_df.empty:
                for _, registro in metas_destino_df.iterrows():
                    try:
                        metas_destino_salvas[
                            int(registro["mes"])
                        ] = _rel_num(
                            registro.get("meta_valor")
                        )
                    except Exception:
                        pass

            linhas_sugestao = []

            for mes in range(1, 13):

                faturado_base = float(
                    faturamento_base_mensal.get(
                        mes,
                        0
                    ) or 0
                )

                if faturado_base > 0:
                    meta_sugerida = (
                        faturado_base
                        * (1 + crescimento_meta / 100)
                    )

                    regra = (
                        f"Faturado + {crescimento_meta:.0f}%"
                    )
                else:
                    meta_sugerida = float(
                        meta_minima
                    )

                    regra = "Meta mínima"

                meta_final = metas_destino_salvas.get(
                    mes,
                    meta_sugerida
                )

                linhas_sugestao.append({
                    "Mês":
                        meses_nomes[mes - 1],
                    f"Faturado {ano_base_meta}":
                        faturado_base,
                    "Regra":
                        regra,
                    "Meta sugerida":
                        meta_sugerida,
                    f"Meta {ano_destino_meta}":
                        meta_final,
                })

            df_sugestao = pd.DataFrame(
                linhas_sugestao
            )

            editor_sugestao = st.data_editor(
                df_sugestao,
                use_container_width=True,
                hide_index=True,
                disabled=[
                    "Mês",
                    f"Faturado {ano_base_meta}",
                    "Regra",
                    "Meta sugerida",
                ],
                column_config={
                    f"Faturado {ano_base_meta}":
                        st.column_config.NumberColumn(
                            format="R$ %.2f"
                        ),
                    "Meta sugerida":
                        st.column_config.NumberColumn(
                            format="R$ %.2f"
                        ),
                    f"Meta {ano_destino_meta}":
                        st.column_config.NumberColumn(
                            format="R$ %.2f",
                            min_value=0.0,
                            step=100.0
                        ),
                },
                key=(
                    f"rel_v31_editor_geracao_"
                    f"{ano_base_meta}_{ano_destino_meta}"
                )
            )

            meta_sugerida_anual = float(
                pd.to_numeric(
                    editor_sugestao[
                        f"Meta {ano_destino_meta}"
                    ],
                    errors="coerce"
                ).fillna(0).sum()
            )

            st.metric(
                f"Meta anual proposta para {ano_destino_meta}",
                _rel_moeda(
                    meta_sugerida_anual
                )
            )

            st.caption(
                "Exemplo: se setembro faturou R$ 11.332,96 e o crescimento é 15%, "
                "a meta do próximo setembro será R$ 13.032,90. "
                "Se um mês faturou R$ 0,00, entra a meta mínima de R$ 1.000,00."
            )

            if st.button(
                f"💾 Salvar metas geradas de {ano_destino_meta}",
                type="primary",
                use_container_width=True,
                key=f"rel_v31_salvar_geradas_{ano_destino_meta}"
            ):
                try:
                    for indice, linha in editor_sugestao.iterrows():

                        _rel_salvar_meta(
                            ano_destino_meta,
                            indice + 1,
                            _rel_num(
                                linha[
                                    f"Meta {ano_destino_meta}"
                                ]
                            )
                        )

                    st.success(
                        f"✅ Metas de {ano_destino_meta} salvas com sucesso."
                    )

                    st.rerun()

                except Exception as erro:
                    st.error(
                        f"Não foi possível salvar as metas: {erro}"
                    )

        # =====================================================
        # C) ACOMPANHAMENTO
        # =====================================================
        with tab_acompanhar_meta:

            st.markdown("### 📊 Acompanhamento das metas")
            st.caption(
                "Aqui você acompanha Meta x Realizado. "
                "O comparativo com o ano anterior só aparece para meses que já aconteceram."
            )

            anos_acomp = list(
                range(
                    2025,
                    hoje.year + 4
                )
            )

            ano_acomp = st.selectbox(
                "Ano acompanhado",
                anos_acomp,
                index=(
                    anos_acomp.index(hoje.year)
                    if hoje.year in anos_acomp
                    else 0
                ),
                key="rel_v31_ano_acomp"
            )

            metas_acomp_df = _rel_carregar_metas(
                ano_acomp
            )

            metas_acomp = {
                mes: 0.0
                for mes in range(1, 13)
            }

            if not metas_acomp_df.empty:
                for _, registro in metas_acomp_df.iterrows():
                    try:
                        metas_acomp[
                            int(registro["mes"])
                        ] = _rel_num(
                            registro.get("meta_valor")
                        )
                    except Exception:
                        pass

            realizado_acomp = pd.Series(
                [0.0] * 12,
                index=range(1, 13),
                dtype=float
            )

            realizado_anterior = pd.Series(
                [0.0] * 12,
                index=range(1, 13),
                dtype=float
            )

            if not df_real_total.empty:

                base_acomp = df_real_total[
                    df_real_total["data_dt"].dt.year
                    == int(ano_acomp)
                ].copy()

                if not base_acomp.empty:
                    realizado_acomp = (
                        base_acomp.groupby(
                            base_acomp["data_dt"].dt.month
                        )["faturamento_evento"]
                        .sum()
                        .reindex(
                            range(1, 13),
                            fill_value=0.0
                        )
                    )

                base_ant = df_real_total[
                    df_real_total["data_dt"].dt.year
                    == int(ano_acomp) - 1
                ].copy()

                if not base_ant.empty:
                    realizado_anterior = (
                        base_ant.groupby(
                            base_ant["data_dt"].dt.month
                        )["faturamento_evento"]
                        .sum()
                        .reindex(
                            range(1, 13),
                            fill_value=0.0
                        )
                    )

            linhas_acomp = []

            for mes in range(1, 13):

                meta_mes = float(
                    metas_acomp.get(
                        mes,
                        0
                    ) or 0
                )

                realizado_mes = float(
                    realizado_acomp.get(
                        mes,
                        0
                    ) or 0
                )

                anterior_mes = float(
                    realizado_anterior.get(
                        mes,
                        0
                    ) or 0
                )

                # ---------------------------------------------
                # ESTADO DO MÊS
                # ---------------------------------------------
                mes_futuro = (
                    int(ano_acomp) > hoje.year
                    or (
                        int(ano_acomp) == hoje.year
                        and mes > hoje.month
                    )
                )

                mes_atual = (
                    int(ano_acomp) == hoje.year
                    and mes == hoje.month
                )

                # ---------------------------------------------
                # ATINGIMENTO
                # ---------------------------------------------
                if mes_futuro:
                    atingimento = None
                    diferenca = None
                    crescimento_texto = "—"
                    status = "⏳ Aguardando"

                else:

                    atingimento = (
                        realizado_mes / meta_mes * 100
                        if meta_mes > 0
                        else None
                    )

                    diferenca = (
                        realizado_mes - meta_mes
                        if meta_mes > 0
                        else None
                    )

                    # O mês atual ainda está em andamento:
                    # não compara parcial com mês inteiro do ano anterior.
                    if mes_atual:
                        crescimento_texto = "Em andamento"
                    elif anterior_mes > 0:
                        crescimento_valor = (
                            realizado_mes / anterior_mes - 1
                        ) * 100

                        crescimento_texto = (
                            f"{crescimento_valor:+.2f}%"
                            .replace(".", ",")
                        )
                    elif realizado_mes > 0:
                        crescimento_texto = (
                            "Novo faturamento"
                        )
                    else:
                        crescimento_texto = "—"

                    if mes_atual:
                        status = "🔵 Em andamento"
                    elif meta_mes <= 0:
                        status = "🟡 Sem meta"
                    elif realizado_mes >= meta_mes:
                        status = "🟢 Atingida"
                    else:
                        status = "🔴 Abaixo"

                linhas_acomp.append({
                    "Mês":
                        meses_nomes[mes - 1],
                    "Meta":
                        meta_mes,
                    "Realizado":
                        realizado_mes,
                    "Atingimento (%)":
                        atingimento,
                    "Diferença p/ Meta":
                        diferenca,
                    "Crescimento vs Ano Anterior":
                        crescimento_texto,
                    "Status":
                        status,
                })

            df_acomp = pd.DataFrame(
                linhas_acomp
            )

            # ---------------------------------------------
            # RESUMO DO PERÍODO JUSTO
            # ---------------------------------------------
            if int(ano_acomp) < hoje.year:
                limite_mes = 12
            elif int(ano_acomp) == hoje.year:
                limite_mes = hoje.month
            else:
                limite_mes = 0

            if limite_mes > 0:

                meta_periodo = float(
                    sum(
                        metas_acomp.get(
                            mes,
                            0
                        ) or 0
                        for mes in range(
                            1,
                            limite_mes + 1
                        )
                    )
                )

                realizado_periodo = float(
                    sum(
                        realizado_acomp.get(
                            mes,
                            0
                        ) or 0
                        for mes in range(
                            1,
                            limite_mes + 1
                        )
                    )
                )

                anterior_periodo = float(
                    sum(
                        realizado_anterior.get(
                            mes,
                            0
                        ) or 0
                        for mes in range(
                            1,
                            limite_mes + 1
                        )
                    )
                )

                atingimento_periodo = (
                    realizado_periodo
                    / meta_periodo
                    * 100
                    if meta_periodo > 0
                    else 0.0
                )

                crescimento_periodo_texto = (
                    _rel_percentual(
                        (
                            realizado_periodo
                            / anterior_periodo
                            - 1
                        ) * 100
                    )
                    if anterior_periodo > 0
                    else "—"
                )

                with st.container(border=True):

                    a1, a2, a3, a4 = st.columns(
                        4
                    )

                    a1.metric(
                        "Meta do período",
                        _rel_moeda(
                            meta_periodo
                        )
                    )

                    a2.metric(
                        "Realizado",
                        _rel_moeda(
                            realizado_periodo
                        )
                    )

                    a3.metric(
                        "Atingimento",
                        _rel_percentual(
                            atingimento_periodo
                        )
                    )

                    a4.metric(
                        "Crescimento vs Ano Anterior",
                        crescimento_periodo_texto
                    )

            else:

                meta_anual_futura = float(
                    sum(
                        metas_acomp.values()
                    )
                )

                with st.container(border=True):

                    a1, a2 = st.columns(2)

                    a1.metric(
                        "Meta anual planejada",
                        _rel_moeda(
                            meta_anual_futura
                        )
                    )

                    a2.metric(
                        "Situação",
                        "Aguardando início"
                    )

            st.dataframe(
                df_acomp,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Meta":
                        st.column_config.NumberColumn(
                            format="R$ %.2f"
                        ),
                    "Realizado":
                        st.column_config.NumberColumn(
                            format="R$ %.2f"
                        ),
                    "Atingimento (%)":
                        st.column_config.NumberColumn(
                            format="%.2f%%"
                        ),
                    "Diferença p/ Meta":
                        st.column_config.NumberColumn(
                            format="R$ %.2f"
                        ),
                }
            )

            graf_acomp = df_acomp[
                [
                    "Mês",
                    "Meta",
                    "Realizado",
                ]
            ].copy()

            graf_acomp.set_index(
                "Mês",
                inplace=True
            )

            st.markdown(
                "### 📈 Meta x Realizado"
            )

            st.line_chart(
                graf_acomp
            )

    # =========================================================
    # COMPARATIVO ANUAL
    # =========================================================
    with tab_anual:

        st.markdown("## 📈 Comparativo Ano a Ano")
        st.caption("Compara crescimento de venda e eficiência do negócio entre dois anos.")

        anos_existentes = sorted(
            set(df_real_total["data_dt"].dropna().dt.year.astype(int).tolist())
        ) if not df_real_total.empty else []
        anos_comp = sorted(set(anos_existentes + [hoje.year - 1, hoje.year, hoje.year + 1]))

        y1, y2 = st.columns(2)
        ano_a = y1.selectbox(
            "Ano base", anos_comp,
            index=anos_comp.index(hoje.year - 1) if hoje.year - 1 in anos_comp else 0,
            key="rel_v3_ano_a"
        )
        ano_b = y2.selectbox(
            "Ano comparado", anos_comp,
            index=anos_comp.index(hoje.year) if hoje.year in anos_comp else len(anos_comp) - 1,
            key="rel_v3_ano_b"
        )

        def _resumo_ano_rel(ano):
            base = df_real_total[df_real_total["data_dt"].dt.year == int(ano)].copy() if not df_real_total.empty else pd.DataFrame()
            if base.empty:
                return {"fat":0.0,"custo":0.0,"lucro":0.0,"cmv":0.0,"margem":0.0,"eventos":0,"convidados":0.0,"ticket":0.0,"reserva":0.0}
            fat = float(base["faturamento_evento"].sum())
            custo = float(base["custo_evento"].sum())
            lucro = float(base["lucro_evento"].sum())
            eventos = int(len(base))
            return {
                "fat":fat,"custo":custo,"lucro":lucro,
                "cmv":custo/fat*100 if fat>0 else 0.0,
                "margem":lucro/fat*100 if fat>0 else 0.0,
                "eventos":eventos,
                "convidados":float(base["convidados"].sum()),
                "ticket":fat/eventos if eventos>0 else 0.0,
                "reserva":float(base["reserva_evento"].sum()),
            }

        ra = _resumo_ano_rel(ano_a)
        rb = _resumo_ano_rel(ano_b)
        linhas = []
        for nome, chave, tipo in [
            ("Faturamento","fat","moeda"),("Custo Real","custo","moeda"),("Lucro Real","lucro","moeda"),
            ("CMV","cmv","pp"),("Margem","margem","pp"),("Eventos","eventos","numero"),
            ("Convidados","convidados","numero"),("Ticket Médio","ticket","moeda"),("Reserva Gerada","reserva","moeda")
        ]:
            va, vb = ra[chave], rb[chave]
            if tipo == "pp":
                evol = f"{vb-va:+.2f} p.p.".replace(".", ",")
                fa, fb = _rel_percentual(va), _rel_percentual(vb)
            elif tipo == "moeda":
                evol = _rel_percentual((vb/va-1)*100 if va != 0 else 0.0)
                fa, fb = _rel_moeda(va), _rel_moeda(vb)
            else:
                evol = _rel_percentual((vb/va-1)*100 if va != 0 else 0.0)
                fa, fb = f"{va:,.0f}", f"{vb:,.0f}"
            linhas.append({"Indicador":nome,str(ano_a):fa,str(ano_b):fb,"Evolução":evol})

        st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)

        mensal = []
        for mes in range(1,13):
            def _mes(ano):
                b = df_real_total[(df_real_total["data_dt"].dt.year==int(ano)) & (df_real_total["data_dt"].dt.month==mes)] if not df_real_total.empty else pd.DataFrame()
                return float(b["faturamento_evento"].sum()) if not b.empty else 0.0
            fa, fb = _mes(ano_a), _mes(ano_b)
            mensal.append({"Mês":meses_nomes[mes-1], f"Faturamento {ano_a}":fa, f"Faturamento {ano_b}":fb, "Evolução (%)":((fb/fa)-1)*100 if fa>0 else 0.0})
        mensal_df = pd.DataFrame(mensal)
        st.markdown("### 📅 Comparativo Mês a Mês")
        st.dataframe(
            mensal_df, use_container_width=True, hide_index=True,
            column_config={
                f"Faturamento {ano_a}": st.column_config.NumberColumn(format="R$ %.2f"),
                f"Faturamento {ano_b}": st.column_config.NumberColumn(format="R$ %.2f"),
                "Evolução (%)": st.column_config.NumberColumn(format="%.2f%%")
            }
        )
        graf = mensal_df[["Mês", f"Faturamento {ano_a}", f"Faturamento {ano_b}"]].copy().set_index("Mês")
        st.line_chart(graf)

    # =========================================================
    # FECHAMENTO ANUAL
    # =========================================================
    with tab_fechamento:

        st.markdown("## 🏁 Fechamento Anual")
        anos_fecha = sorted(set(df_real_total["data_dt"].dropna().dt.year.astype(int).tolist())) if not df_real_total.empty else [hoje.year]
        if not anos_fecha:
            anos_fecha = [hoje.year]
        ano_fecha = st.selectbox("Ano do fechamento", anos_fecha, index=len(anos_fecha)-1, key="rel_v3_fecha_ano")
        ano_df = df_real_total[df_real_total["data_dt"].dt.year == int(ano_fecha)].copy() if not df_real_total.empty else pd.DataFrame()

        if ano_df.empty:
            st.info("Nenhum evento com CMV fechado neste ano.")
        else:
            fat = float(ano_df["faturamento_evento"].sum())
            custo = float(ano_df["custo_evento"].sum())
            lucro = float(ano_df["lucro_evento"].sum())
            reserva = float(ano_df["reserva_evento"].sum())
            disp = float(ano_df["disponivel_evento"].sum())
            eventos = int(len(ano_df))
            convidados = float(ano_df["convidados"].sum())
            ticket = fat/eventos if eventos>0 else 0.0
            cmv = custo/fat*100 if fat>0 else 0.0
            margem_ano = lucro/fat*100 if fat>0 else 0.0

            metas_ano = _rel_carregar_metas(ano_fecha)
            meta_total = float(pd.to_numeric(metas_ano.get("meta_valor", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not metas_ano.empty else 0.0
            ating = fat/meta_total*100 if meta_total>0 else 0.0

            with st.container(border=True):
                st.markdown(f"#### 🏆 Fechamento {ano_fecha}")
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Eventos Fechados", eventos)
                c2.metric("Faturamento Real", _rel_moeda(fat))
                c3.metric("Custo Real", _rel_moeda(custo))
                c4.metric("Lucro Real", _rel_moeda(lucro))
                c5,c6,c7,c8 = st.columns(4)
                c5.metric("CMV", _rel_percentual(cmv))
                c6.metric("Margem", _rel_percentual(margem_ano))
                c7.metric("Convidados", f"{convidados:,.0f}")
                c8.metric("Ticket Médio", _rel_moeda(ticket))

            with st.container(border=True):
                st.markdown("#### 🛡️ Destinação e Metas")
                d1,d2,d3,d4 = st.columns(4)
                d1.metric("Reserva Gerada", _rel_moeda(reserva))
                d2.metric("Disponível após Reserva", _rel_moeda(disp))
                d3.metric("Meta Anual", _rel_moeda(meta_total))
                d4.metric("Atingimento", _rel_percentual(ating))

            maior_fat = ano_df.loc[ano_df["faturamento_evento"].idxmax()]
            maior_lucro = ano_df.loc[ano_df["lucro_evento"].idxmax()]
            e1,e2 = st.columns(2)
            e1.info(f"💰 Maior faturamento: {maior_fat.get('cliente','Evento')} — {_rel_moeda(maior_fat.get('faturamento_evento',0))}")
            e2.info(f"📈 Maior lucro: {maior_lucro.get('cliente','Evento')} — {_rel_moeda(maior_lucro.get('lucro_evento',0))}")

            mensal = []
            for mes in range(1,13):
                b = ano_df[ano_df["data_dt"].dt.month==mes]
                f = float(b["faturamento_evento"].sum()) if not b.empty else 0.0
                c = float(b["custo_evento"].sum()) if not b.empty else 0.0
                l = float(b["lucro_evento"].sum()) if not b.empty else 0.0
                mensal.append({"Mês":meses_nomes[mes-1],"Eventos":int(len(b)),"Faturamento":f,"Custo":c,"Lucro":l,"CMV (%)":c/f*100 if f>0 else 0.0})
            mensal_df = pd.DataFrame(mensal)
            st.markdown("### 📅 Fechamento Mês a Mês")
            st.dataframe(
                mensal_df, use_container_width=True, hide_index=True,
                column_config={
                    "Faturamento": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Custo": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Lucro": st.column_config.NumberColumn(format="R$ %.2f"),
                    "CMV (%)": st.column_config.NumberColumn(format="%.2f%%")
                }
            )

    # =========================================================
    # TAB 5 — PRODUTOS
    # =========================================================
    with tab_prod:

        st.markdown("## 📦 Desempenho por Produto / Serviço")
        st.info(
            "A análise detalhada por produto continuará sendo construída a partir "
            "do histórico real de consumo do CMV. O resultado financeiro acima já "
            "usa somente os fechamentos oficiais."
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

                
elif menu == "Orçamentos":
    
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
            "orc_sig_qtd_",
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
        """Seleciona um produto usando uma referência estável do cadastro.

        A V11 usava a posição (0, 1, 2...) da linha como valor do selectbox.
        Se a ordem retornada pelo Supabase mudasse entre reruns, o estado do
        Streamlit podia ficar associado à posição antiga. Aqui usamos o ID do
        cadastro (ou uma chave composta quando não houver ID), evitando que a
        marca exibida e o produto usado no cálculo fiquem desencontrados.
        """
        opcoes = opcoes.copy().reset_index(drop=True)

        if opcoes.empty:
            return None

        # Ordem determinística para evitar mudança visual entre reruns.
        colunas_ordem = [
            c for c in ["_tipo_norm", "_nome_norm", "quantidade", "preco", "id"]
            if c in opcoes.columns
        ]
        if colunas_ordem:
            opcoes = opcoes.sort_values(
                by=colunas_ordem,
                kind="stable",
                na_position="last",
            ).reset_index(drop=True)

        refs = []
        rotulos = {}

        for i, linha in opcoes.iterrows():
            item_id = linha.get("id")
            if pd.notna(item_id) and str(item_id).strip() not in ("", "nan", "None"):
                ref = f"id:{item_id}"
            else:
                ref = (
                    "item:"
                    f"{_norm_orcamento(linha.get('tipo', ''))}|"
                    f"{_norm_orcamento(linha.get('nome', ''))}|"
                    f"{float(linha.get('quantidade', 0) or 0):.6f}|"
                    f"{float(linha.get('preco', 0) or 0):.6f}|{i}"
                )

            # Garante unicidade mesmo se houver duplicidade de cadastro.
            ref_original = ref
            contador = 2
            while ref in rotulos:
                ref = f"{ref_original}#{contador}"
                contador += 1

            refs.append(ref)
            rotulos[ref] = _rotulo_produto(linha, i)
            opcoes.loc[i, "_orc_ref_estavel"] = ref

        if len(opcoes) == 1:
            st.caption(titulo)
            st.markdown(f"**{rotulos[refs[0]]}**")
            return opcoes.iloc[0]

        ref_escolhido = st.selectbox(
            titulo,
            refs,
            format_func=lambda ref: rotulos[ref],
            key=key,
        )

        linha_escolhida = opcoes[
            opcoes["_orc_ref_estavel"] == ref_escolhido
        ]

        if linha_escolhida.empty:
            return None

        return linha_escolhida.iloc[0]

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

    def _orc_info_unidade_operacional(item):
        """
        Unidade usada pela equipe no checklist, sem alterar a unidade técnica
        que permanece gravada no banco para manter os cálculos das receitas.
        """
        categoria_raw = str(item.get("categoria", "") or "").strip()
        categoria = _norm_orcamento(categoria_raw)
        unidade_raw = str(item.get("unidade", "") or "un").strip()
        unidade = _norm_orcamento(unidade_raw)
        quantidade_base = float(item.get("quantidade_base", 0) or 0)

        if categoria in {"artesanais", "artesanal"} and quantidade_base > 0:
            if quantidade_base >= 1000:
                litros = quantidade_base / 1000.0
                litros_txt = (
                    str(int(round(litros)))
                    if abs(litros - round(litros)) < 1e-9
                    else f"{litros:.1f}".rstrip("0").rstrip(".")
                )
                unidade_exibicao = f"garrafas {litros_txt}L"
            else:
                unidade_exibicao = f"garrafas {int(round(quantidade_base))}ml"
            return {
                "fator": quantidade_base,
                "unidade": unidade_exibicao,
                "categoria": "Artesanais",
                "passo": 0.5,
            }

        if unidade in {"g", "gr", "grama", "gramas"}:
            return {
                "fator": 1000.0,
                "unidade": "kg",
                "categoria": categoria_raw,
                "passo": 0.1,
            }

        if categoria == "bebidas" or "garrafa" in unidade:
            return {
                "fator": 1.0,
                "unidade": unidade_raw or "garrafas",
                "categoria": categoria_raw,
                "passo": 0.5,
            }

        return {
            "fator": 1.0,
            "unidade": unidade_raw,
            "categoria": categoria_raw,
            "passo": 0.1,
        }

    def _orc_item_checklist_operacional(item):
        info = _orc_info_unidade_operacional(item)
        fator = max(float(info.get("fator", 1.0) or 1.0), 1e-12)
        novo = dict(item)
        novo["categoria_exibicao"] = info.get("categoria") or item.get("categoria", "")
        novo["quantidade_exibicao"] = round(float(item.get("quantidade", 0) or 0) / fator, 1)
        novo["unidade_exibicao"] = info.get("unidade") or item.get("unidade", "un")
        novo["fator_operacional"] = fator
        novo["passo_operacional"] = float(info.get("passo", 0.1) or 0.1)
        return novo

    def _fmt_qtd_pdf(valor):
        try:
            valor = round(float(valor or 0), 1)
        except Exception:
            return ""
        if abs(valor - round(valor)) < 1e-9:
            return str(int(round(valor)))
        return f"{valor:.1f}".replace(".", ",")

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
            item_op = _orc_item_checklist_operacional(item)
            unidade = str(item_op.get("unidade_exibicao", "") or "").strip()
            qtd = _fmt_qtd_pdf(item_op.get("quantidade_exibicao", 0))
            qtd_sistema = f"{qtd} {unidade}".strip()
            linhas.append([
                str(item_op.get("categoria_exibicao", item.get("categoria", "")) or ""),
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
        Checklist digital oficial em unidade operacional.
        A base continua gravada em unidade técnica; a equipe vê kg/garrafas.
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

            linhas_base = []
            for _, reg in df_cat.reset_index(drop=True).iterrows():
                info = _orc_info_unidade_operacional(reg)
                fator = max(float(info.get("fator", 1.0) or 1.0), 1e-12)
                linhas_base.append({
                    "_id": int(reg.get("id")),
                    "_fator": fator,
                    "_passo": float(info.get("passo", 0.1) or 0.1),
                    "Item": str(reg.get("produto", "") or ""),
                    "Sistema": round(float(reg.get("quantidade", 0) or 0) / fator, 1),
                    "Ida": round(float(reg.get("quantidade_ida", 0) or 0) / fator, 1),
                    "Volta": round(float(reg.get("quantidade_volta", 0) or 0) / fator, 1),
                    "Conferência Final": round(float(reg.get("quantidade_estoquista", 0) or 0) / fator, 1),
                    "Unidade": info.get("unidade") or str(reg.get("unidade", "un") or "un"),
                })

            base = pd.DataFrame(linhas_base)

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
                        "📊 Sistema", format="%.1f"
                    ),
                    "Ida": st.column_config.NumberColumn(
                        "🚚 Ida", min_value=0.0, step=0.1, format="%.1f"
                    ),
                    "Volta": st.column_config.NumberColumn(
                        "↩️ Volta", min_value=0.0, step=0.1, format="%.1f"
                    ),
                    "Conferência Final": st.column_config.NumberColumn(
                        "🔎 Conferência Final", min_value=0.0, step=0.1, format="%.1f"
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

            for indice, linha in editor.iterrows():
                passo = float(base.iloc[indice]["_passo"] or 0.1)
                if abs(passo - 0.5) < 1e-9:
                    for col in ["Ida", "Volta", "Conferência Final"]:
                        valor = float(linha.get(col, 0) or 0)
                        if abs(valor * 2 - round(valor * 2)) > 1e-7:
                            erros.append(
                                f"{linha.get('Item', 'Item')}: use quantidades em passos de 0,5 garrafa."
                            )

            st.dataframe(
                resumo[[
                    "Item", "Sistema", "Ida", "Volta", "Conferência Final",
                    "Consumo", "Divergência", "Unidade",
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Sistema": st.column_config.NumberColumn(format="%.1f"),
                    "Consumo": st.column_config.NumberColumn(
                        "🔥 Consumo", format="%.1f"
                    ),
                    "Divergência": st.column_config.NumberColumn(
                        "⚠️ Divergência", format="%.1f"
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

                        passo = float(base.iloc[indice]["_passo"] or 0.1)
                        if abs(passo - 0.5) < 1e-9:
                            valores = [ida, volta, conferencia]
                            if any(abs(v * 2 - round(v * 2)) > 1e-7 for v in valores):
                                continue

                        fator = float(base.iloc[indice]["_fator"] or 1.0)
                        item_id = int(base.iloc[indice]["_id"])
                        supabase.table("evento_itens").update({
                            "quantidade_ida": ida * fator,
                            "quantidade_volta": volta * fator,
                            "quantidade_estoquista": conferencia * fator,
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
                                        key=f"orc_marca_v12_{chave_base}",
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

                                # Uma única chave de quantidade por base/ingrediente.
                                # A assinatura abaixo força a sugestão a ser reaplicada
                                # somente quando muda a necessidade ou o produto escolhido.
                                # Em reruns normais, o ajuste manual do usuário é preservado.
                                chave_qtd = f"orc_qtd_beb_{chave_base}"
                                chave_sig_qtd = f"orc_sig_qtd_beb_{chave_base}"

                                produto_ref = linha_produto.get("id")
                                if pd.isna(produto_ref):
                                    produto_ref = (
                                        f"{_norm_orcamento(marca)}|"
                                        f"{volume:.6f}|{preco:.6f}"
                                    )

                                assinatura_qtd = (
                                    str(produto_ref),
                                    round(float(qtd_necessaria), 6),
                                    round(float(volume), 6),
                                    int(qtd_calculada),
                                )

                                if (
                                    st.session_state.get(chave_sig_qtd)
                                    != assinatura_qtd
                                ):
                                    st.session_state[chave_qtd] = int(qtd_calculada)
                                    st.session_state[chave_sig_qtd] = assinatura_qtd
                                elif chave_qtd not in st.session_state:
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

                                    if int(qtd_editavel) != int(qtd_calculada):
                                        if st.button(
                                            "↩️ Usar sugestão",
                                            key=f"orc_reset_qtd_beb_{chave_base}",
                                            help="Restaura a quantidade calculada pelo sistema para esta bebida.",
                                        ):
                                            st.session_state[chave_qtd] = int(qtd_calculada)
                                            st.rerun()

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
                            itens_check = [
                                _orc_item_checklist_operacional(item)
                                for item in itens_orcamento
                            ]
                            df_check_sistema = pd.DataFrame({
                                "Categoria": [x.get("categoria_exibicao", x.get("categoria", "")) for x in itens_check],
                                "Item": [x.get("produto", "") for x in itens_check],
                                "Sistema": [x.get("quantidade_exibicao", 0) for x in itens_check],
                                "Ida": 0.0,
                                "Volta": 0.0,
                                "Conferência Final": 0.0,
                                "Consumo": 0.0,
                                "Divergência": 0.0,
                                "Unidade": [x.get("unidade_exibicao", "un") for x in itens_check],
                            })
                            st.caption(
                                "Checklist em unidade operacional: frutas/insumos em kg e "
                                "artesanais em garrafas conforme a embalagem cadastrada."
                            )
                            st.dataframe(
                                df_check_sistema,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Sistema": st.column_config.NumberColumn(format="%.1f"),
                                    "Ida": st.column_config.NumberColumn(format="%.1f"),
                                    "Volta": st.column_config.NumberColumn(format="%.1f"),
                                    "Conferência Final": st.column_config.NumberColumn(format="%.1f"),
                                    "Consumo": st.column_config.NumberColumn(format="%.1f"),
                                    "Divergência": st.column_config.NumberColumn(format="%.1f"),
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

                    st.divider()

elif menu == "Cachês":

    st.title("👥 Gestão de Cachês")
    st.caption(
        "Livro de registro da equipe + integração segura com CMV e Financeiro. "
        "Agora com correção e exclusão sincronizadas: o CMV usa o valor registrado e o Financeiro usa somente o que foi pago."
    )

    # =========================================================
    # INTEGRAÇÃO CACHÊS -> CMV -> FINANCEIRO
    # =========================================================

    def _cache_num(valor, padrao=0.0):
        try:
            if valor is None or pd.isna(valor):
                return float(padrao)
            return float(valor)
        except Exception:
            return float(padrao)

    def _cache_texto(valor):
        if valor is None:
            return ""
        try:
            if pd.isna(valor):
                return ""
        except Exception:
            pass
        texto = str(valor).strip()
        return "" if texto.lower() in {"nan", "none", "null"} else texto

    def _cache_financeiro_existente(cache_id):
        try:
            dados = (
                supabase.table("Financeiro")
                .select("id")
                .eq("origem", "cache")
                .eq("origem_id", int(cache_id))
                .limit(1)
                .execute()
                .data
                or []
            )
            return dados[0].get("id") if dados else None
        except Exception:
            return None

    def _cache_registrar_financeiro(registro, forma_pagamento=None, data_pagamento=None):
        """
        Cria UMA saída no Financeiro para um cachê efetivamente pago.
        A chave origem='cache' + origem_id protege contra duplicidade.
        """
        cache_id = int(registro.get("id"))
        existente = _cache_financeiro_existente(cache_id)

        if existente:
            supabase.table("pagamentos_equipe").update({
                "financeiro_lancado": True,
                "financeiro_id": int(existente),
                "financeiro_data_lancamento": datetime.now().isoformat(),
            }).eq("id", cache_id).execute()
            return int(existente), False

        valor = _cache_num(registro.get("valor"))
        nome = _cache_texto(registro.get("nome")) or "Profissional"
        funcao = _cache_texto(registro.get("funcao"))
        evento = _cache_texto(registro.get("evento")) or "Evento"
        evento_id = registro.get("evento_id")
        forma = forma_pagamento or _cache_texto(registro.get("forma_pagamento")) or "Não informado"
        data_ref = data_pagamento or registro.get("data_pagamento") or datetime.now().isoformat()

        try:
            data_mov = pd.to_datetime(data_ref).date().isoformat()
        except Exception:
            data_mov = datetime.now().date().isoformat()

        payload_fin = {
            "data": data_mov,
            "tipo": "Saída",
            "categoria": "Cachês / Equipe",
            "forma_pagamento": forma,
            "descricao": f"Cachê - {nome} ({funcao}) - {evento}",
            "valor": float(valor),
            "evento_id": int(evento_id) if evento_id is not None and not pd.isna(evento_id) else None,
            "origem": "cache",
            "origem_id": cache_id,
        }

        resposta = supabase.table("Financeiro").insert(payload_fin).execute()
        financeiro_id = None
        if resposta.data:
            financeiro_id = resposta.data[0].get("id")

        supabase.table("pagamentos_equipe").update({
            "financeiro_lancado": True,
            "financeiro_id": int(financeiro_id) if financeiro_id is not None else None,
            "financeiro_data_lancamento": datetime.now().isoformat(),
        }).eq("id", cache_id).execute()

        return financeiro_id, True

    def _cache_estornar_financeiro(cache_id):
        """Remove somente a saída criada por este cachê e volta o registro para Pendente."""
        supabase.table("Financeiro").delete()\
            .eq("origem", "cache")\
            .eq("origem_id", int(cache_id))\
            .execute()

        supabase.table("pagamentos_equipe").update({
            "status": "Pendente",
            "forma_pagamento": None,
            "data_pagamento": None,
            "financeiro_lancado": False,
            "financeiro_id": None,
            "financeiro_data_lancamento": None,
        }).eq("id", int(cache_id)).execute()


    def _cache_evento_fechado(evento_id):
        """Retorna True quando o evento vinculado já possui CMV fechado."""
        if evento_id is None:
            return False
        try:
            dados = (
                supabase.table("eventos")
                .select("cmv_status")
                .eq("id", int(evento_id))
                .limit(1)
                .execute()
                .data
                or []
            )
            if not dados:
                return False
            return _cache_texto(dados[0].get("cmv_status")).lower() == "fechado"
        except Exception:
            return False

    def _cache_atualizar_financeiro(registro):
        """
        Sincroniza o Financeiro com um cachê corrigido.

        - Pendente: não deve existir saída de caixa; remove eventual saída vinculada.
        - Pago: cria ou ATUALIZA a mesma saída usando origem='cache' + origem_id.
        Nunca cria duplicidade para o mesmo cachê.
        """
        cache_id = int(registro.get("id"))
        status = _cache_texto(registro.get("status")).lower()

        if status != "pago":
            supabase.table("Financeiro").delete()                .eq("origem", "cache")                .eq("origem_id", cache_id)                .execute()

            supabase.table("pagamentos_equipe").update({
                "financeiro_lancado": False,
                "financeiro_id": None,
                "financeiro_data_lancamento": None,
            }).eq("id", cache_id).execute()
            return None, "removido"

        valor = _cache_num(registro.get("valor"))
        nome = _cache_texto(registro.get("nome")) or "Profissional"
        funcao = _cache_texto(registro.get("funcao"))
        evento = _cache_texto(registro.get("evento")) or "Evento"
        evento_id = registro.get("evento_id")
        forma = _cache_texto(registro.get("forma_pagamento")) or "Não informado"
        data_ref = registro.get("data_pagamento") or datetime.now().isoformat()

        try:
            data_mov = pd.to_datetime(data_ref).date().isoformat()
        except Exception:
            data_mov = datetime.now().date().isoformat()

        payload_fin = {
            "data": data_mov,
            "tipo": "Saída",
            "categoria": "Cachês / Equipe",
            "forma_pagamento": forma,
            "descricao": f"Cachê - {nome} ({funcao}) - {evento}",
            "valor": float(valor),
            "evento_id": int(evento_id)
                if evento_id is not None and not pd.isna(evento_id)
                else None,
            "origem": "cache",
            "origem_id": cache_id,
        }

        financeiro_id = _cache_financeiro_existente(cache_id)

        if financeiro_id:
            supabase.table("Financeiro").update(payload_fin)                .eq("id", int(financeiro_id))                .execute()
            criado = False
        else:
            resposta = supabase.table("Financeiro").insert(payload_fin).execute()
            financeiro_id = (
                resposta.data[0].get("id")
                if resposta.data
                else None
            )
            criado = True

        supabase.table("pagamentos_equipe").update({
            "financeiro_lancado": True,
            "financeiro_id": int(financeiro_id) if financeiro_id is not None else None,
            "financeiro_data_lancamento": datetime.now().isoformat(),
        }).eq("id", cache_id).execute()

        return financeiro_id, "criado" if criado else "atualizado"

    # =========================================================
    # LEMBRETE DE EVENTOS REALIZADOS SEM CACHÊS
    # =========================================================
    try:
        eventos_realizados = pd.DataFrame(
            supabase.table("eventos")
            .select("id, cliente, data, modalidade, status")
            .in_("status", ["aprovado", "finalizado", "concluido", "pago"])
            .execute()
            .data or []
        )
        caches_base = pd.DataFrame(
            supabase.table("pagamentos_equipe")
            .select("evento_id, id")
            .execute()
            .data or []
        )

        if not eventos_realizados.empty:
            eventos_realizados["_data"] = pd.to_datetime(
                eventos_realizados.get("data"), errors="coerce"
            )
            hoje_ts = pd.Timestamp(date.today())
            realizados = eventos_realizados[
                eventos_realizados["_data"].notna()
                & (eventos_realizados["_data"].dt.normalize() <= hoje_ts)
            ].copy()

            ids_com_cache = set()
            if not caches_base.empty and "evento_id" in caches_base.columns:
                ids_com_cache = set(
                    pd.to_numeric(caches_base["evento_id"], errors="coerce")
                    .dropna().astype(int).tolist()
                )

            sem_cache = realizados[
                ~pd.to_numeric(realizados["id"], errors="coerce")
                .fillna(-1).astype(int).isin(ids_com_cache)
            ]

            if not sem_cache.empty:
                st.warning(
                    f"🔔 {len(sem_cache)} evento(s) já realizado(s) ainda não possuem "
                    "cachês registrados. Isso não bloqueia o sistema, mas o CMV ficará sem "
                    "o custo real de equipe até o lançamento."
                )
                with st.expander("Ver eventos sem cachês", expanded=False):
                    for _, ev in sem_cache.sort_values("_data", ascending=False).iterrows():
                        st.write(
                            f"• #{int(ev['id'])} — {_cache_texto(ev.get('cliente')) or 'Sem cliente'} "
                            f"— {pd.to_datetime(ev.get('data')).strftime('%d/%m/%Y')}"
                        )
    except Exception:
        pass

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
                .select("id, cliente, data, cmv_status")
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

            if _cache_texto(evento_obj.get("cmv_status")).lower() == "fechado":
                st.warning(
                    "🔒 O CMV deste evento já está fechado. Você pode registrar o cachê, mas "
                    "para ele entrar no resultado real do evento será necessário reabrir e "
                    "finalizar novamente o CMV."
                )
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
                        "financeiro_lancado": False,
                    }
                    resposta_cache = supabase.table("pagamentos_equipe").insert(
                        payload_equipe
                    ).execute()

                    # CMV usa o registro assim que ele existe, pago ou pendente.
                    # Financeiro recebe a saída somente se o pagamento já ocorreu.
                    if status_final == "Pago" and resposta_cache.data:
                        try:
                            registro_salvo = resposta_cache.data[0]
                            _cache_registrar_financeiro(
                                registro_salvo,
                                forma_pagamento=forma_final,
                                data_pagamento=data_pagto_final,
                            )
                        except Exception as erro_fin:
                            st.warning(
                                "O cachê foi salvo como Pago, mas a saída no Financeiro "
                                f"não pôde ser sincronizada: {erro_fin}. "
                                "Ele ficará sinalizado para sincronização no Histórico."
                            )

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

        feedback_cache = st.session_state.pop("cache_feedback_gerenciamento", None)
        if feedback_cache:
            st.success(feedback_cache.get("mensagem", "Alteração concluída."))
            if feedback_cache.get("cmv_fechado"):
                st.warning(
                    "⚠️ O evento alterado possui CMV fechado. O registro de Cachês já foi corrigido, "
                    "mas o snapshot do fechamento precisa ser revisado: abra o evento no CMV, "
                    "reabra o fechamento e finalize novamente para atualizar o resultado/PDF."
                )

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

            # Pagos antigos ou falhas de sincronização ficam visíveis.
            if "financeiro_lancado" in df_pagamentos.columns:
                fin_flag = df_pagamentos["financeiro_lancado"].fillna(False).astype(bool)
            else:
                fin_flag = pd.Series(False, index=df_pagamentos.index)

            pagos_sem_financeiro = df_pagamentos[
                (df_pagamentos["status"].astype(str).str.lower() == "pago")
                & (~fin_flag)
            ].copy()

            if not pagos_sem_financeiro.empty:
                st.warning(
                    f"⚠️ {len(pagos_sem_financeiro)} pagamento(s) estão marcados como Pago, "
                    "mas ainda não possuem saída rastreada no Financeiro. "
                    "Isso é esperado para registros antigos à integração."
                )
                confirmar_sync = st.checkbox(
                    "Confirmo que esses cachês ainda NÃO foram lançados manualmente no Financeiro.",
                    key="cache_confirmar_sync_legado",
                )
                if st.button(
                    "🔄 Sincronizar pagamentos pagos pendentes",
                    use_container_width=True,
                    disabled=not confirmar_sync,
                    key="cache_sync_legados",
                ):
                    erros_sync = []
                    sincronizados = 0
                    for _, registro in pagos_sem_financeiro.iterrows():
                        try:
                            _cache_registrar_financeiro(registro.to_dict())
                            sincronizados += 1
                        except Exception as erro_sync:
                            erros_sync.append(f"ID {registro.get('id')}: {erro_sync}")
                    if sincronizados:
                        st.success(f"✅ {sincronizados} pagamento(s) sincronizado(s).")
                    if erros_sync:
                        st.error("Falhas: " + " | ".join(erros_sync[:5]))
                    st.rerun()

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
                "financeiro_lancado",
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

                    try:
                        supabase.table("pagamentos_equipe").update({
                            "status": "Pago",
                            "forma_pagamento": forma,
                            "observacao": obs_baixa,
                            "data_pagamento": agora_iso,
                        }).eq("id", linha["id"]).execute()

                        registro_pago = linha.to_dict()
                        registro_pago.update({
                            "status": "Pago",
                            "forma_pagamento": forma,
                            "observacao": obs_baixa,
                            "data_pagamento": agora_iso,
                        })
                        _cache_registrar_financeiro(
                            registro_pago,
                            forma_pagamento=forma,
                            data_pagamento=agora_iso,
                        )

                        st.toast(
                            "✅ Pagamento confirmado e saída registrada no Financeiro!",
                            icon="🎉",
                        )
                        st.success(
                            "Pagamento confirmado. O CMV já considera esse cachê desde o "
                            "registro; agora o Financeiro também recebeu a saída de caixa."
                        )
                        st.rerun()
                    except Exception as erro_pagamento:
                        st.error(f"Erro ao confirmar/sincronizar pagamento: {erro_pagamento}")

            st.divider()

            # =========================================================
            # ✏️ CORRIGIR / EXCLUIR LANÇAMENTO COM SINCRONIZAÇÃO SEGURA
            # =========================================================
            st.subheader("✏️ Corrigir ou excluir um lançamento")
            st.caption(
                "A correção atualiza o custo da equipe no CMV. Se o cachê estiver Pago, "
                "a mesma saída vinculada no Financeiro também é atualizada, sem duplicar."
            )

            opcoes_gerenciar = df_pagamentos.apply(
                lambda x: (
                    f"ID #{int(x['id'])} | {x['nome']} | "
                    f"{x['evento']} | R$ {float(x['valor']):.2f} | {x['status']}"
                ),
                axis=1,
            )

            if not opcoes_gerenciar.empty:
                item_gerenciar = st.selectbox(
                    "Selecione o cachê que deseja corrigir",
                    options=opcoes_gerenciar.tolist(),
                    key="cache_gerenciar_registro",
                )
                idx_gerenciar = opcoes_gerenciar[opcoes_gerenciar == item_gerenciar].index[0]
                linha_edit = df_pagamentos.loc[idx_gerenciar].copy()
                cache_edit_id = int(linha_edit["id"])

                # Eventos disponíveis para eventual correção do vínculo.
                eventos_edicao = []
                try:
                    eventos_edicao = (
                        supabase.table("eventos")
                        .select("id, cliente, data, cmv_status")
                        .order("data", desc=True)
                        .execute()
                        .data
                        or []
                    )
                except Exception:
                    eventos_edicao = []

                opcoes_evento_edicao = {}
                for ev in eventos_edicao:
                    ev_id = int(ev.get("id"))
                    cliente_ev = _cache_texto(ev.get("cliente")) or "Evento"
                    data_ev = _cache_texto(ev.get("data"))
                    rotulo_ev = f"#{ev_id} | {cliente_ev} | {data_ev}"
                    opcoes_evento_edicao[rotulo_ev] = ev

                evento_atual_id = linha_edit.get("evento_id")
                try:
                    evento_atual_id = int(evento_atual_id) if pd.notna(evento_atual_id) else None
                except Exception:
                    evento_atual_id = None

                rotulos_evento = list(opcoes_evento_edicao.keys())
                indice_evento_atual = 0
                for pos, rotulo in enumerate(rotulos_evento):
                    if int(opcoes_evento_edicao[rotulo].get("id")) == evento_atual_id:
                        indice_evento_atual = pos
                        break

                cmv_fechado_atual = _cache_evento_fechado(evento_atual_id)
                if cmv_fechado_atual:
                    st.warning(
                        "🔒 Este cachê pertence a um evento com CMV fechado. A correção é permitida, "
                        "mas depois será necessário reabrir e finalizar novamente o CMV para atualizar "
                        "o snapshot e o PDF do evento."
                    )

                with st.form(
                    key=f"cache_form_corrigir_{cache_edit_id}"
                ):
                    if rotulos_evento:
                        evento_edit_rotulo = st.selectbox(
                            "Evento",
                            rotulos_evento,
                            index=indice_evento_atual,
                        )
                        evento_edit_obj = opcoes_evento_edicao[evento_edit_rotulo]
                        evento_edit_id = int(evento_edit_obj.get("id"))
                        evento_edit_nome = (
                            f"{_cache_texto(evento_edit_obj.get('cliente')) or 'Evento'} "
                            f"({_cache_texto(evento_edit_obj.get('data'))})"
                        )
                    else:
                        evento_edit_id = evento_atual_id
                        evento_edit_nome = st.text_input(
                            "Evento / referência",
                            value=_cache_texto(linha_edit.get("evento")),
                        )

                    ce1, ce2, ce3 = st.columns(3)
                    nome_edit = ce1.text_input(
                        "Profissional",
                        value=_cache_texto(linha_edit.get("nome")),
                    )

                    funcoes_padrao = ["Bartender", "Barback", "Líder"]
                    funcao_atual = _cache_texto(linha_edit.get("funcao")) or "Bartender"
                    if funcao_atual not in funcoes_padrao:
                        funcoes_padrao.append(funcao_atual)
                    funcao_edit = ce2.selectbox(
                        "Função",
                        funcoes_padrao,
                        index=funcoes_padrao.index(funcao_atual),
                    )

                    status_atual = (
                        "Pago"
                        if _cache_texto(linha_edit.get("status")).lower() == "pago"
                        else "Pendente"
                    )
                    status_edit = ce3.selectbox(
                        "Status",
                        ["Pendente", "Pago"],
                        index=1 if status_atual == "Pago" else 0,
                    )

                    ce4, ce5, ce6 = st.columns(3)
                    valor_base_edit = ce4.number_input(
                        "Cachê base",
                        min_value=0.0,
                        value=_cache_num(linha_edit.get("valor_base")),
                        step=10.0,
                        format="%.2f",
                    )
                    horas_edit = ce5.number_input(
                        "Horas trabalhadas",
                        min_value=0.0,
                        value=_cache_num(linha_edit.get("horas")),
                        step=0.5,
                    )
                    horas_extras_edit = ce6.number_input(
                        "Horas extras",
                        min_value=0.0,
                        value=_cache_num(linha_edit.get("horas_extras")),
                        step=0.5,
                    )

                    ce7, ce8, ce9 = st.columns(3)
                    ajuda_edit = ce7.number_input(
                        "Ajuda de custo",
                        min_value=0.0,
                        value=_cache_num(linha_edit.get("ajuda_custo")),
                        step=10.0,
                        format="%.2f",
                    )
                    despesas_edit = ce8.number_input(
                        "Despesas",
                        min_value=0.0,
                        value=_cache_num(linha_edit.get("despesas")),
                        step=10.0,
                        format="%.2f",
                    )
                    valor_total_edit = ce9.number_input(
                        "Valor total do cachê",
                        min_value=0.0,
                        value=_cache_num(linha_edit.get("valor")),
                        step=10.0,
                        format="%.2f",
                        help=(
                            "Este é o valor oficial que entra no CMV e, quando Pago, no Financeiro. "
                            "Ajuste-o caso o lançamento original tenha sido feito incorretamente."
                        ),
                    )

                    cp1, cp2 = st.columns(2)
                    formas_pagamento = ["Pix", "Dinheiro", "Transferência", "Cartão"]
                    forma_atual = _cache_texto(linha_edit.get("forma_pagamento"))
                    if forma_atual and forma_atual not in formas_pagamento:
                        formas_pagamento.append(forma_atual)
                    forma_edit = cp1.selectbox(
                        "Forma de pagamento",
                        formas_pagamento,
                        index=(
                            formas_pagamento.index(forma_atual)
                            if forma_atual in formas_pagamento
                            else 0
                        ),
                        disabled=status_edit != "Pago",
                    )

                    data_pagamento_atual = pd.to_datetime(
                        linha_edit.get("data_pagamento"), errors="coerce"
                    )
                    data_pagamento_padrao = (
                        data_pagamento_atual.date()
                        if pd.notna(data_pagamento_atual)
                        else date.today()
                    )
                    data_pagamento_edit = cp2.date_input(
                        "Data do pagamento",
                        value=data_pagamento_padrao,
                        disabled=status_edit != "Pago",
                    )

                    observacao_edit = st.text_area(
                        "Observação",
                        value=_cache_texto(linha_edit.get("observacao")),
                    )

                    confirmar_correcao = st.checkbox(
                        "Confirmo que revisei os dados deste cachê.",
                        key=f"cache_confirma_correcao_{cache_edit_id}",
                    )

                    salvar_correcao = st.form_submit_button(
                        "💾 Salvar correção",
                        use_container_width=True,
                    )

                if salvar_correcao:
                    if not confirmar_correcao:
                        st.warning("Confirme a revisão antes de salvar.")
                    elif not nome_edit.strip():
                        st.warning("Informe o nome do profissional.")
                    elif valor_total_edit <= 0:
                        st.warning("O valor total do cachê deve ser maior que zero.")
                    else:
                        try:
                            if status_edit == "Pago":
                                data_pagamento_iso = datetime.combine(
                                    data_pagamento_edit,
                                    datetime.now().time(),
                                ).isoformat()
                                forma_final_edit = forma_edit
                            else:
                                data_pagamento_iso = None
                                forma_final_edit = None

                            payload_corrigido = {
                                "evento_id": evento_edit_id,
                                "evento": evento_edit_nome,
                                "nome": nome_edit.strip(),
                                "funcao": funcao_edit,
                                "valor": float(valor_total_edit),
                                "valor_base": float(valor_base_edit),
                                "horas": float(horas_edit),
                                "horas_extras": float(horas_extras_edit),
                                "ajuda_custo": float(ajuda_edit),
                                "despesas": float(despesas_edit),
                                "observacao": observacao_edit.strip(),
                                "status": status_edit,
                                "forma_pagamento": forma_final_edit,
                                "data_pagamento": data_pagamento_iso,
                            }

                            supabase.table("pagamentos_equipe").update(
                                payload_corrigido
                            ).eq("id", cache_edit_id).execute()

                            registro_corrigido = {
                                **linha_edit.to_dict(),
                                **payload_corrigido,
                                "id": cache_edit_id,
                            }
                            _cache_atualizar_financeiro(registro_corrigido)

                            evento_antigo_fechado = _cache_evento_fechado(evento_atual_id)
                            evento_novo_fechado = _cache_evento_fechado(evento_edit_id)

                            st.session_state["cache_feedback_gerenciamento"] = {
                                "mensagem": (
                                    f"✅ Cachê ID #{cache_edit_id} corrigido com sucesso. "
                                    "CMV e Financeiro passam a usar os dados corrigidos conforme o status."
                                ),
                                "cmv_fechado": bool(
                                    evento_antigo_fechado or evento_novo_fechado
                                ),
                            }
                            st.rerun()

                        except Exception as erro_correcao:
                            st.error(f"Erro ao corrigir o cachê: {erro_correcao}")

                with st.expander("🗑️ Excluir lançamento", expanded=False):
                    st.warning(
                        "A exclusão remove o registro de Cachês. Se ele já tiver gerado uma saída "
                        "no Financeiro, essa mesma saída vinculada também será removida."
                    )
                    confirmar_exclusao = st.checkbox(
                        f"Confirmo a exclusão definitiva do cachê ID #{cache_edit_id}.",
                        key=f"cache_confirma_exclusao_{cache_edit_id}",
                    )

                    if st.button(
                        "🗑️ Excluir cachê e sincronizar",
                        type="primary",
                        use_container_width=True,
                        disabled=not confirmar_exclusao,
                        key=f"cache_excluir_seguro_{cache_edit_id}",
                    ):
                        try:
                            cmv_fechado_exclusao = _cache_evento_fechado(evento_atual_id)

                            # Primeiro remove somente a saída financeira originada por este cachê.
                            supabase.table("Financeiro").delete()\
                                .eq("origem", "cache")\
                                .eq("origem_id", cache_edit_id)\
                                .execute()

                            # Depois remove o registro de cachê.
                            supabase.table("pagamentos_equipe").delete()\
                                .eq("id", cache_edit_id)\
                                .execute()

                            st.session_state["cache_feedback_gerenciamento"] = {
                                "mensagem": (
                                    f"✅ Cachê ID #{cache_edit_id} excluído. "
                                    "Qualquer saída financeira vinculada a ele também foi removida."
                                ),
                                "cmv_fechado": bool(cmv_fechado_exclusao),
                            }
                            st.rerun()

                        except Exception as erro_exclusao:
                            st.error(f"Erro ao excluir o cachê: {erro_exclusao}")

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


elif menu == "CMV":

    import io
    import re
    import html
    import unicodedata
    from datetime import datetime

    st.title("📊 CMV — Fechamento Real dos Eventos")
    st.caption("Versão V4.5 — unidades operacionais simplificadas no checklist e no fechamento.")
    st.caption(
        "Feche o evento a partir do checklist operacional: Ida, Volta e "
        "Conferência Final geram automaticamente Consumo, Divergência e Custo Real."
    )

    # ============================================================
    # AJUSTES VISUAIS DO CMV
    # ============================================================
    st.markdown(
        """
        <style>
        /* Remove a linha horizontal longa que o Streamlit coloca sob as abas. */
        .stTabs [data-baseweb="tab-list"] {
            border-bottom: none !important;
            box-shadow: none !important;
        }
        .stTabs [data-baseweb="tab-border"] {
            display: none !important;
        }

        /* Mantém somente o destaque da aba ativa, sem o trilho cinza. */
        .stTabs [data-baseweb="tab-highlight"] {
            height: 3px !important;
            border-radius: 999px !important;
        }

        /* Avisos do CMV com tipografia única.
           Também evita que o símbolo $ seja interpretado como fórmula. */
        .cmv-aviso {
            width: 100%;
            box-sizing: border-box;
            padding: 16px 18px;
            margin: 10px 0 14px 0;
            border-radius: 10px;
            font-size: 15px !important;
            line-height: 1.45 !important;
            font-weight: 500 !important;
            letter-spacing: 0 !important;
        }
        .cmv-aviso * {
            font-size: 15px !important;
            line-height: 1.45 !important;
            font-weight: 500 !important;
        }
        .cmv-aviso-sucesso {
            background: rgba(20, 83, 45, 0.72);
            border: 1px solid rgba(74, 222, 128, 0.20);
        }
        .cmv-aviso-alerta {
            background: rgba(92, 77, 16, 0.70);
            border: 1px solid rgba(250, 204, 21, 0.18);
        }
        .cmv-aviso-info {
            background: rgba(30, 64, 95, 0.70);
            border: 1px solid rgba(96, 165, 250, 0.18);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ============================================================
    # CONFIGURAÇÕES
    # ============================================================

    STATUS_EVENTOS_CMV = ["aprovado", "finalizado", "concluido", "pago"]
    CATEGORIAS_ADMIN = {"equipe", "custos", "locação", "locacao"}
    CATEGORIAS_CUSTO_MANUAL = [
        "Transporte",
        "Locação",
        "Compra emergencial",
        "Alimentação",
        "Pedágio",
        "Hotel / Hospedagem",
        "Avaria / Quebra",
        "Gelo extra",
        "Outros",
    ]

    # ============================================================
    # FUNÇÕES AUXILIARES
    # ============================================================

    def _cmv_num(valor, padrao=0.0):
        try:
            if valor is None or pd.isna(valor):
                return float(padrao)
            return float(valor)
        except Exception:
            return float(padrao)

    def _cmv_texto(valor):
        if valor is None:
            return ""
        try:
            if pd.isna(valor):
                return ""
        except Exception:
            pass
        texto = str(valor).strip()
        return "" if texto.lower() in {"nan", "none", "null"} else texto

    def _cmv_moeda(valor):
        valor = _cmv_num(valor)
        texto = f"{valor:,.2f}"
        texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {texto}"

    def _cmv_aviso(texto, tipo="sucesso"):
        """Aviso visual do CMV com fonte uniforme e sem interpretação Markdown de R$."""
        classe = {
            "sucesso": "cmv-aviso-sucesso",
            "alerta": "cmv-aviso-alerta",
            "info": "cmv-aviso-info",
        }.get(tipo, "cmv-aviso-info")
        texto_seguro = html.escape(str(texto))
        st.markdown(
            f'<div class="cmv-aviso {classe}">{texto_seguro}</div>',
            unsafe_allow_html=True,
        )

    def _cmv_data_br(valor):
        if not _cmv_texto(valor):
            return "-"
        try:
            return pd.to_datetime(valor).strftime("%d/%m/%Y")
        except Exception:
            return str(valor)

    def _cmv_evento_rotulo(evento):
        return (
            f"#{int(evento.get('id'))} | "
            f"{_cmv_texto(evento.get('cliente')) or 'Sem cliente'} | "
            f"{_cmv_data_br(evento.get('data'))} | "
            f"{_cmv_texto(evento.get('cidade'))}"
        )

    def _cmv_carregar_eventos():
        dados = (
            supabase.table("eventos")
            .select("*")
            .in_("status", STATUS_EVENTOS_CMV)
            .order("data", desc=True)
            .execute()
            .data
            or []
        )
        return pd.DataFrame(dados)

    def _cmv_carregar_itens(evento_id):
        dados = (
            supabase.table("evento_itens")
            .select("*")
            .eq("evento_id", int(evento_id))
            .order("id")
            .execute()
            .data
            or []
        )
        return pd.DataFrame(dados)

    def _cmv_carregar_custos(evento_id):
        dados = (
            supabase.table("evento_custos")
            .select("*")
            .eq("evento_id", int(evento_id))
            .order("id", desc=True)
            .execute()
            .data
            or []
        )
        return pd.DataFrame(dados)

    def _cmv_carregar_adendos(evento_id):
        dados = (
            supabase.table("aditivos_evento")
            .select("*")
            .eq("evento_id", int(evento_id))
            .neq("status", "Cancelado")
            .order("id", desc=True)
            .execute()
            .data
            or []
        )
        return pd.DataFrame(dados)

    def _cmv_carregar_caches_evento(evento_id):
        """
        Cachês vinculados ao evento.
        No CMV, TODO cachê registrado é custo real da equipe, independentemente
        de já estar Pago ou Pendente. O status de pagamento pertence ao Financeiro.
        """
        try:
            dados = (
                supabase.table("pagamentos_equipe")
                .select("*")
                .eq("evento_id", int(evento_id))
                .order("id", desc=True)
                .execute()
                .data
                or []
            )
            return pd.DataFrame(dados)
        except Exception:
            return pd.DataFrame()

    def _cmv_resumo_caches(caches):
        if caches.empty:
            return {
                "total": 0.0,
                "pago": 0.0,
                "pendente": 0.0,
                "qtd": 0,
                "qtd_pendente": 0,
            }

        valores = pd.to_numeric(
            caches.get("valor", pd.Series(dtype=float)), errors="coerce"
        ).fillna(0)
        if "status" in caches.columns:
            status = caches["status"].fillna("Pendente").astype(str).str.lower()
        else:
            status = pd.Series("pendente", index=caches.index)

        pagos_mask = status == "pago"
        return {
            "total": float(valores.sum()),
            "pago": float(valores[pagos_mask].sum()),
            "pendente": float(valores[~pagos_mask].sum()),
            "qtd": int(len(caches)),
            "qtd_pendente": int((~pagos_mask).sum()),
        }

    def _cmv_separar_custos_manuais(custos):
        """Separa Cachê/Equipe dos demais custos sem alterar a tabela atual."""
        custo_equipe = 0.0
        outros = 0.0

        if custos.empty:
            return custo_equipe, outros

        for _, linha in custos.iterrows():
            descricao = _cmv_texto(linha.get("descricao")).lower()
            valor = _cmv_num(linha.get("valor", 0))

            # O cadastro atual salva a categoria no início da descrição.
            # Usamos "cach" + "equipe" para aceitar Cachê/Cache/Cachês.
            if "cach" in descricao and "equipe" in descricao:
                custo_equipe += valor
            else:
                outros += valor

        return custo_equipe, outros

    def _cmv_itens_operacionais(itens):
        if itens.empty:
            return itens.copy()
        if "categoria" not in itens.columns:
            return itens.copy()
        categoria_norm = itens["categoria"].fillna("").astype(str).str.strip().str.lower()
        return itens[~categoria_norm.isin(CATEGORIAS_ADMIN)].copy()

    def _cmv_custo_unitario_operacional(linha):
        # 1) snapshot ideal gravado pelo Orçamento V10+
        custo = _cmv_num(linha.get("custo_unitario_operacional", 0))
        if custo > 0:
            return custo

        # 2) fallback: custo estimado / quantidade prevista
        custo_estimado = _cmv_num(linha.get("custo_estimado", 0))
        quantidade = _cmv_num(linha.get("quantidade", 0))
        if custo_estimado > 0 and quantidade > 0:
            return custo_estimado / quantidade

        # 3) bebida antiga com preço unitário salvo
        categoria = _cmv_texto(linha.get("categoria")).lower()
        preco_unitario = _cmv_num(linha.get("preco_unitario", 0))
        if categoria == "bebidas" and preco_unitario > 0:
            return preco_unitario

        return 0.0

    def _cmv_norm_preco(valor):
        texto = _cmv_texto(valor)
        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ascii", "ignore").decode("ascii")
        texto = texto.lower().strip()
        texto = re.sub(r"[^a-z0-9]+", " ", texto)
        return " ".join(texto.split())

    def _cmv_carregar_bases_precos():
        """Carrega os preços atuais cadastrados na Precificação."""
        bases = {}
        for nome_tabela in [
            "precos_bebidas",
            "precos_insumos",
            "precos_artesanais",
        ]:
            try:
                dados = (
                    supabase.table(nome_tabela)
                    .select("*")
                    .execute()
                    .data
                    or []
                )
                df = pd.DataFrame(dados)
            except Exception:
                df = pd.DataFrame()

            if not df.empty:
                if "nome" in df.columns:
                    df["_nome_norm"] = (
                        df["nome"].fillna("").astype(str).map(_cmv_norm_preco)
                    )
                else:
                    df["_nome_norm"] = ""

                if "tipo" in df.columns:
                    df["_tipo_norm"] = (
                        df["tipo"].fillna("").astype(str).map(_cmv_norm_preco)
                    )
                else:
                    df["_tipo_norm"] = ""

            bases[nome_tabela] = df

        return bases

    def _cmv_qtd_operacional_texto(valor):
        """Exibe quantidade com no máximo uma casa decimal."""
        valor = round(_cmv_num(valor), 1)
        if abs(valor - round(valor)) < 1e-9:
            return str(int(round(valor)))
        return f"{valor:.1f}".replace(".", ",")

    def _cmv_info_unidade_operacional(item, bases=None):
        """
        Converte a unidade técnica salva no banco para a unidade que a equipe
        realmente usa no checklist, sem alterar a base histórica.

        Regras:
        - Artesanais cadastrados em embalagem (ex.: 1000 ml) -> garrafas da embalagem.
        - Itens salvos em gramas -> quilogramas.
        - Bebidas continuam em garrafas.

        O fator sempre indica quantas unidades técnicas existem em 1 unidade
        operacional. Ex.: 1000 g = 1 kg; 1000 ml = 1 garrafa de 1 L.
        """
        categoria_raw = _cmv_texto(item.get("categoria"))
        categoria = _cmv_norm_preco(categoria_raw)
        unidade_raw = _cmv_texto(item.get("unidade")) or "un"
        unidade = _cmv_norm_preco(unidade_raw)
        nome_norm = _cmv_norm_preco(item.get("produto"))

        quantidade_base = _cmv_num(item.get("quantidade_base", 0))
        preco_embalagem = _cmv_num(item.get("preco_unitario", 0))
        custo_unit_raw = _cmv_custo_unitario_operacional(item)

        linha_artesanal = None
        if bases is not None:
            df_art = bases.get("precos_artesanais", pd.DataFrame())
            if not df_art.empty and "_nome_norm" in df_art.columns and nome_norm:
                cand = df_art[df_art["_nome_norm"] == nome_norm]
                if len(cand) == 1:
                    linha_artesanal = cand.iloc[0]

        eh_artesanal = categoria in {"artesanais", "artesanal"} or linha_artesanal is not None

        if eh_artesanal:
            if quantidade_base <= 0 and linha_artesanal is not None:
                quantidade_base = _cmv_num(linha_artesanal.get("quantidade", 0))
            if preco_embalagem <= 0 and linha_artesanal is not None:
                preco_embalagem = _cmv_num(linha_artesanal.get("preco", 0))

            if quantidade_base > 0:
                if quantidade_base >= 1000:
                    litros = quantidade_base / 1000.0
                    litros_txt = _cmv_qtd_operacional_texto(litros)
                    unidade_exibicao = f"garrafas {litros_txt}L"
                else:
                    unidade_exibicao = f"garrafas {int(round(quantidade_base))}ml"

                custo_exibicao = (
                    preco_embalagem
                    if preco_embalagem > 0
                    else custo_unit_raw * quantidade_base
                )
                return {
                    "fator": float(quantidade_base),
                    "unidade": unidade_exibicao,
                    "categoria": "Artesanais",
                    "passo": 0.5,
                    "custo_unitario_exibicao": float(custo_exibicao),
                }

        if unidade in {"g", "gr", "grama", "gramas"}:
            return {
                "fator": 1000.0,
                "unidade": "kg",
                "categoria": categoria_raw or "Insumos",
                "passo": 0.1,
                "custo_unitario_exibicao": float(custo_unit_raw * 1000.0),
            }

        if categoria == "bebidas" or "garrafa" in unidade:
            return {
                "fator": 1.0,
                "unidade": unidade_raw or "garrafas",
                "categoria": categoria_raw or "Bebidas",
                "passo": 0.5,
                "custo_unitario_exibicao": float(custo_unit_raw),
            }

        return {
            "fator": 1.0,
            "unidade": unidade_raw,
            "categoria": categoria_raw,
            "passo": 0.1,
            "custo_unitario_exibicao": float(custo_unit_raw),
        }

    def _cmv_calcular_custo_atual_item(item, linha_preco, origem_preco=None):
        """
        Converte o preço atual da Precificação para a unidade operacional
        usada pelo checklist/CMV.

        V4.1: quando um item antigo está classificado na categoria errada
        (ex.: Charope salvo como Insumos, mas cadastrado em precos_artesanais),
        a origem real do preço tem prioridade para definir a conversão.
        """
        categoria = _cmv_norm_preco(item.get("categoria"))
        unidade = _cmv_norm_preco(item.get("unidade"))
        preco = _cmv_num(linha_preco.get("preco", 0))
        quantidade_cadastro = _cmv_num(linha_preco.get("quantidade", 0))

        if preco <= 0:
            return None

        # A origem real do cadastro prevalece sobre a categoria antiga do evento.
        if origem_preco == "precos_bebidas":
            return {
                "preco_unitario": preco,
                "quantidade_base": quantidade_cadastro,
                "custo_unitario_operacional": preco,
            }

        if origem_preco == "precos_artesanais":
            if quantidade_cadastro <= 0:
                return None
            return {
                "preco_unitario": preco,
                "quantidade_base": quantidade_cadastro,
                "custo_unitario_operacional": preco / quantidade_cadastro,
            }

        if origem_preco == "precos_insumos":
            if unidade in {"g", "gr", "grama", "gramas"}:
                # Na base de insumos o preço histórico é tratado como R$/kg.
                return {
                    "preco_unitario": preco,
                    "quantidade_base": 1000.0,
                    "custo_unitario_operacional": preco / 1000.0,
                }
            if unidade in {"kg", "quilo", "quilos"}:
                return {
                    "preco_unitario": preco,
                    "quantidade_base": 1.0,
                    "custo_unitario_operacional": preco,
                }
            if quantidade_cadastro > 0:
                return {
                    "preco_unitario": preco,
                    "quantidade_base": quantidade_cadastro,
                    "custo_unitario_operacional": preco / quantidade_cadastro,
                }
            return None

        # Fallback compatível com eventos mais novos.
        if categoria == "bebidas":
            return {
                "preco_unitario": preco,
                "quantidade_base": quantidade_cadastro,
                "custo_unitario_operacional": preco,
            }

        if categoria in {"frutas", "insumos", "gelo"}:
            if unidade in {"g", "gr", "grama", "gramas"}:
                return {
                    "preco_unitario": preco,
                    "quantidade_base": 1000.0,
                    "custo_unitario_operacional": preco / 1000.0,
                }
            if unidade in {"kg", "quilo", "quilos"}:
                return {
                    "preco_unitario": preco,
                    "quantidade_base": 1.0,
                    "custo_unitario_operacional": preco,
                }
            if quantidade_cadastro > 0:
                return {
                    "preco_unitario": preco,
                    "quantidade_base": quantidade_cadastro,
                    "custo_unitario_operacional": preco / quantidade_cadastro,
                }
            return None

        if categoria in {"artesanais", "artesanal"}:
            if quantidade_cadastro <= 0:
                return None
            return {
                "preco_unitario": preco,
                "quantidade_base": quantidade_cadastro,
                "custo_unitario_operacional": preco / quantidade_cadastro,
            }

        return None

    def _cmv_filtrar_candidatos_preco(item, base, permitir_tipo=True):
        """Retorna candidatos compatíveis dentro de uma base de preços."""
        if base is None or base.empty:
            return pd.DataFrame()

        candidatos = pd.DataFrame()

        produto_ref_id = item.get("produto_ref_id")
        if produto_ref_id is not None and "id" in base.columns:
            try:
                ref_num = int(float(produto_ref_id))
                candidatos = base[
                    pd.to_numeric(base["id"], errors="coerce") == ref_num
                ].copy()
            except Exception:
                pass

        if candidatos.empty:
            nome_norm = _cmv_norm_preco(item.get("produto"))
            if nome_norm:
                candidatos = base[base["_nome_norm"] == nome_norm].copy()

        if candidatos.empty and permitir_tipo:
            tipo_norm = _cmv_norm_preco(item.get("tipo_base"))
            if tipo_norm:
                por_tipo = base[base["_tipo_norm"] == tipo_norm].copy()
                if len(por_tipo) == 1:
                    candidatos = por_tipo

        return candidatos

    def _cmv_escolher_candidato_unico(item, candidatos, origem_preco):
        """Resolve embalagem/preço sem escolher arbitrariamente."""
        if candidatos is None or candidatos.empty:
            return None, "produto não encontrado"

        if len(candidatos) > 1:
            qtd_base_antiga = _cmv_num(item.get("quantidade_base", 0))
            if qtd_base_antiga > 0 and "quantidade" in candidatos.columns:
                qtds = pd.to_numeric(candidatos["quantidade"], errors="coerce")
                proximos = candidatos[(qtds - qtd_base_antiga).abs() < 1e-6]
                if len(proximos) == 1:
                    candidatos = proximos

        if len(candidatos) > 1:
            custos = []
            for _, cand in candidatos.iterrows():
                calc = _cmv_calcular_custo_atual_item(
                    item, cand, origem_preco=origem_preco
                )
                if calc:
                    custos.append(round(calc["custo_unitario_operacional"], 10))
            if custos and max(custos) - min(custos) < 1e-9:
                candidatos = candidatos.iloc[[0]].copy()
            else:
                return None, "mais de um cadastro compatível; precisa escolher a embalagem"

        linha_preco = candidatos.iloc[0]
        calculo = _cmv_calcular_custo_atual_item(
            item, linha_preco, origem_preco=origem_preco
        )
        if not calculo or calculo["custo_unitario_operacional"] <= 0:
            return None, "cadastro encontrado, mas o preço/quantidade está inválido"

        calculo["produto_ref_id"] = (
            int(linha_preco.get("id"))
            if pd.notna(linha_preco.get("id"))
            else None
        )
        calculo["origem_preco"] = origem_preco
        return calculo, None

    def _cmv_resolver_preco_atual(item, bases):
        """
        Resolve preço atual sem adivinhar.

        V4.1:
        1) tenta primeiro a base esperada pela categoria do evento;
        2) se não encontrar, procura o NOME EXATO normalizado nas outras bases;
        3) só aceita a busca cruzada quando existe uma única origem/cadastro seguro.

        Isso recupera eventos antigos em que, por exemplo, Charopes/Espumas
        foram salvos como 'Insumos', embora o preço esteja em precos_artesanais.
        """
        categoria = _cmv_norm_preco(item.get("categoria"))
        tabela_por_categoria = {
            "bebidas": "precos_bebidas",
            "frutas": "precos_insumos",
            "insumos": "precos_insumos",
            "gelo": "precos_insumos",
            "artesanais": "precos_artesanais",
            "artesanal": "precos_artesanais",
        }
        nome_tabela_primaria = tabela_por_categoria.get(categoria)
        ordem_bases = [
            x for x in [
                nome_tabela_primaria,
                "precos_bebidas",
                "precos_insumos",
                "precos_artesanais",
            ] if x
        ]
        # Remove duplicados preservando a ordem.
        ordem_bases = list(dict.fromkeys(ordem_bases))

        # 1) Base principal: ID -> nome -> tipo_base único.
        if nome_tabela_primaria:
            base_principal = bases.get(nome_tabela_primaria, pd.DataFrame())
            candidatos = _cmv_filtrar_candidatos_preco(
                item, base_principal, permitir_tipo=True
            )
            if not candidatos.empty:
                return _cmv_escolher_candidato_unico(
                    item, candidatos, nome_tabela_primaria
                )

        # 2) Busca cruzada SOMENTE por nome exato normalizado.
        nome_norm = _cmv_norm_preco(item.get("produto"))
        if not nome_norm:
            return None, "produto sem nome para pesquisa"

        encontrados = []
        for nome_base in ordem_bases:
            if nome_base == nome_tabela_primaria:
                continue
            base = bases.get(nome_base, pd.DataFrame())
            if base.empty or "_nome_norm" not in base.columns:
                continue
            cand = base[base["_nome_norm"] == nome_norm].copy()
            if not cand.empty:
                encontrados.append((nome_base, cand))

        if not encontrados:
            return None, "produto não encontrado na Precificação atual"

        if len(encontrados) > 1:
            # Se o mesmo nome existe em bases diferentes, não adivinha.
            origens = ", ".join(x[0] for x in encontrados)
            return None, f"produto encontrado em mais de uma base: {origens}"

        origem_preco, candidatos = encontrados[0]
        calculo, erro = _cmv_escolher_candidato_unico(
            item, candidatos, origem_preco
        )
        if calculo:
            calculo["busca_cruzada"] = True
        return calculo, erro

    def _cmv_preencher_custos_zerados(evento_id, bases=None):
        """
        Grava um snapshot dos PREÇOS ATUAIS somente nos itens cujo custo
        operacional está zerado. Não altera itens que já possuem preço salvo.
        """
        if bases is None:
            bases = _cmv_carregar_bases_precos()

        itens_evento = _cmv_itens_operacionais(_cmv_carregar_itens(evento_id))
        atualizados = 0
        ignorados = 0
        pendencias = []

        for _, item in itens_evento.iterrows():
            if _cmv_custo_unitario_operacional(item) > 0:
                ignorados += 1
                continue

            resolvido, erro = _cmv_resolver_preco_atual(item, bases)
            if not resolvido:
                pendencias.append({
                    "Item": _cmv_texto(item.get("produto")),
                    "Categoria": _cmv_texto(item.get("categoria")),
                    "Motivo": erro,
                })
                continue

            quantidade_prevista = _cmv_num(item.get("quantidade", 0))
            custo_unit = _cmv_num(resolvido.get("custo_unitario_operacional", 0))
            custo_estimado = quantidade_prevista * custo_unit

            consumo_salvo = _cmv_num(item.get("cmv_consumo_real", 0))
            if consumo_salvo == 0:
                ida = _cmv_num(item.get("quantidade_ida", 0))
                final = _cmv_num(item.get("quantidade_estoquista", 0))
                consumo_salvo = ida - final

            payload = {
                "produto_ref_id": resolvido.get("produto_ref_id"),
                "quantidade_base": _cmv_num(resolvido.get("quantidade_base", 0)),
                "preco_unitario": _cmv_num(resolvido.get("preco_unitario", 0)),
                "custo_unitario_operacional": custo_unit,
                "custo_estimado": custo_estimado,
                "cmv_custo_real": consumo_salvo * custo_unit,
            }

            supabase.table("evento_itens").update(payload).eq(
                "id", int(item.get("id"))
            ).execute()
            atualizados += 1

        return {
            "atualizados": atualizados,
            "ignorados": ignorados,
            "pendencias": pendencias,
        }

    def _cmv_calcular_item(linha, ida=None, volta=None, final=None):
        ida = _cmv_num(linha.get("quantidade_ida", 0) if ida is None else ida)
        volta = _cmv_num(linha.get("quantidade_volta", 0) if volta is None else volta)
        final = _cmv_num(linha.get("quantidade_estoquista", 0) if final is None else final)

        consumo = ida - final
        divergencia = volta - final
        custo_unit = _cmv_custo_unitario_operacional(linha)
        custo_real = consumo * custo_unit

        return {
            "ida": ida,
            "volta": volta,
            "final": final,
            "consumo": consumo,
            "divergencia": divergencia,
            "custo_unitario": custo_unit,
            "custo_real": custo_real,
        }

    def _cmv_resumo_financeiro(evento, itens, custos, adendos, caches):
        venda_original = _cmv_num(evento.get("venda", 0))
        custo_previsto = _cmv_num(evento.get("custo", 0))

        # Adendos representam SOMENTE receita adicional cobrada do cliente.
        # Qualquer custo real decorrente do evento deve vir da aba Cachês
        # (equipe) ou de Outros Custos (transporte, alimentação, pedágio etc.).
        adendos_cliente = 0.0
        if not adendos.empty:
            adendos_cliente = pd.to_numeric(
                adendos.get("valor_cliente", pd.Series(dtype=float)),
                errors="coerce",
            ).fillna(0).sum()

        # Custos manuais antigos de equipe ficam como fallback.
        custo_equipe_manual, outros_custos_manuais = _cmv_separar_custos_manuais(custos)
        resumo_caches = _cmv_resumo_caches(caches)

        # Regra anti-duplicidade:
        # se houver ao menos um cachê vinculado ao evento, a aba Cachês é a fonte
        # oficial do custo real de equipe e os lançamentos manuais de Cachê/Equipe
        # em evento_custos são ignorados.
        if resumo_caches["qtd"] > 0:
            custo_equipe = resumo_caches["total"]
            fonte_equipe = "Cachês"
            custo_equipe_manual_ignorado = float(custo_equipe_manual)
        else:
            custo_equipe = float(custo_equipe_manual)
            fonte_equipe = "Manual" if custo_equipe > 0 else "Não informado"
            custo_equipe_manual_ignorado = 0.0

        custo_produtos = 0.0
        itens_operacionais = _cmv_itens_operacionais(itens)
        if not itens_operacionais.empty:
            if "cmv_custo_real" in itens_operacionais.columns:
                custo_produtos = pd.to_numeric(
                    itens_operacionais["cmv_custo_real"], errors="coerce"
                ).fillna(0).sum()
            else:
                for _, item in itens_operacionais.iterrows():
                    custo_produtos += _cmv_calcular_item(item)["custo_real"]

        faturamento_real = venda_original + float(adendos_cliente)
        custo_total = (
            float(custo_produtos)
            + float(custo_equipe)
            + float(outros_custos_manuais)
        )
        lucro_real = faturamento_real - custo_total
        cmv_percentual = (
            custo_total / faturamento_real * 100
            if faturamento_real > 0
            else 0.0
        )

        return {
            "venda_original": venda_original,
            "adendos_cliente": float(adendos_cliente),
            "faturamento_real": faturamento_real,
            "custo_previsto": custo_previsto,
            "custo_produtos": float(custo_produtos),
            "custo_equipe": float(custo_equipe),
            "fonte_equipe": fonte_equipe,
            "custo_equipe_pago": float(resumo_caches["pago"]),
            "custo_equipe_pendente": float(resumo_caches["pendente"]),
            "qtd_caches": int(resumo_caches["qtd"]),
            "qtd_caches_pendentes": int(resumo_caches["qtd_pendente"]),
            "custo_equipe_manual_ignorado": custo_equipe_manual_ignorado,
            "outros_custos_manuais": float(outros_custos_manuais),
            "custos_manuais": float(custo_equipe + outros_custos_manuais),
            "custo_adendos": 0.0,
            "custo_total": float(custo_total),
            "lucro_real": float(lucro_real),
            "cmv_percentual": float(cmv_percentual),
            "diferenca_previsto": float(custo_previsto - custo_total),
        }

    def _cmv_resumo_snapshot(evento, resumo_calculado):
        if _cmv_texto(evento.get("cmv_status")).lower() != "fechado":
            return resumo_calculado

        resumo = dict(resumo_calculado)
        resumo["custo_produtos"] = _cmv_num(
            evento.get("cmv_custo_produtos"), resumo["custo_produtos"]
        )

        # V3 separa equipe de outros custos. Fechamentos antigos podem ter
        # cmv_custo_equipe NULL; nesse caso preservamos o detalhamento calculado
        # e respeitamos o custo total congelado do evento.
        snap_equipe = evento.get("cmv_custo_equipe")
        if snap_equipe is not None:
            try:
                if not pd.isna(snap_equipe):
                    resumo["custo_equipe"] = _cmv_num(snap_equipe)
                    resumo["outros_custos_manuais"] = _cmv_num(
                        evento.get("cmv_custos_extras"),
                        resumo["outros_custos_manuais"],
                    )
                    resumo["custos_manuais"] = (
                        resumo["custo_equipe"] + resumo["outros_custos_manuais"]
                    )
            except Exception:
                pass

        # V4.2: adendos nunca são custo. Fechamentos feitos em versões
        # anteriores podem ter congelado valor_equipe como custo de adendo;
        # por isso corrigimos o snapshot em leitura sem apagar o histórico.
        resumo["custo_adendos"] = 0.0
        resumo["faturamento_real"] = _cmv_num(
            evento.get("cmv_faturamento_total"), resumo["faturamento_real"]
        )

        resumo["custo_total"] = (
            _cmv_num(resumo.get("custo_produtos"))
            + _cmv_num(resumo.get("custo_equipe"))
            + _cmv_num(resumo.get("outros_custos_manuais"))
        )
        resumo["lucro_real"] = resumo["faturamento_real"] - resumo["custo_total"]
        resumo["cmv_percentual"] = (
            resumo["custo_total"] / resumo["faturamento_real"] * 100
            if resumo["faturamento_real"] > 0 else 0.0
        )
        resumo["diferenca_previsto"] = resumo["custo_previsto"] - resumo["custo_total"]
        return resumo

    def _cmv_pdf_fechamento(evento, itens, custos, adendos, caches, resumo):
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER
            from reportlab.lib.units import mm
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            )
        except Exception:
            return None, (
                "A biblioteca reportlab não está disponível. "
                "Mantenha 'reportlab' no requirements.txt e reinicie o app."
            )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=12 * mm,
            leftMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
        )

        styles = getSampleStyleSheet()
        titulo = ParagraphStyle(
            "TituloCMV",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=10,
        )
        subtitulo = ParagraphStyle(
            "SubtituloCMV",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            spaceBefore=8,
            spaceAfter=6,
        )
        normal = ParagraphStyle(
            "NormalCMV",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
        )

        story = [Paragraph("RELATORIO DE FECHAMENTO E CMV", titulo)]

        info = [
            ["Evento #", str(int(evento.get("id"))), "Cliente", _cmv_texto(evento.get("cliente"))],
            ["Data", _cmv_data_br(evento.get("data")), "Tipo", _cmv_texto(evento.get("tipo_evento"))],
            ["Cidade", _cmv_texto(evento.get("cidade")), "Convidados", str(int(_cmv_num(evento.get("convidados", 0))))],
            ["Responsável", _cmv_texto(evento.get("cmv_responsavel")), "Fechado em", _cmv_data_br(evento.get("cmv_data_fechamento"))],
        ]
        t_info = Table(info, colWidths=[32*mm, 75*mm, 38*mm, 100*mm])
        t_info.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#EEF1F5")),
            ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#EEF1F5")),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 8.5),
            ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#BFC6D0")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 5),
            ("RIGHTPADDING", (0,0), (-1,-1), 5),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        story += [t_info, Spacer(1, 8)]

        story.append(Paragraph("Resumo financeiro", subtitulo))
        fin = [
            ["Venda original", _cmv_moeda(resumo["venda_original"]),
             "Adendos cliente", _cmv_moeda(resumo["adendos_cliente"]),
             "Faturamento total", _cmv_moeda(resumo["faturamento_real"])],
            ["Custo real produtos", _cmv_moeda(resumo["custo_produtos"]),
             "Cachês / equipe", _cmv_moeda(resumo.get("custo_equipe", 0)),
             "Outros custos", _cmv_moeda(resumo.get("outros_custos_manuais", 0))],
            ["Custo total evento", _cmv_moeda(resumo["custo_total"]),
             "CMV", f"{resumo['cmv_percentual']:.2f}%",
             "Lucro real", _cmv_moeda(resumo["lucro_real"])],
            ["Custo previsto", _cmv_moeda(resumo["custo_previsto"]),
             "Dif. previsto x real", _cmv_moeda(resumo["diferenca_previsto"]),
             "Adendos = receita", _cmv_moeda(resumo["adendos_cliente"])],
        ]
        t_fin = Table(fin, colWidths=[38*mm, 40*mm, 42*mm, 40*mm, 42*mm, 40*mm])
        t_fin.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#F7F8FA")),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
            ("FONTNAME", (4,0), (4,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 8.5),
            ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#BFC6D0")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 5),
            ("RIGHTPADDING", (0,0), (-1,-1), 5),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        story += [t_fin, Spacer(1, 8)]

        if not caches.empty:
            story.append(Paragraph("Equipe / Cachês registrados", subtitulo))
            dados_eq = [["Profissional", "Função", "Horas", "Valor", "Status", "Pagamento"]]
            for _, reg in caches.iterrows():
                dados_eq.append([
                    _cmv_texto(reg.get("nome")),
                    _cmv_texto(reg.get("funcao")),
                    f"{_cmv_num(reg.get('horas')):.1f}",
                    _cmv_moeda(reg.get("valor")),
                    _cmv_texto(reg.get("status")),
                    _cmv_texto(reg.get("forma_pagamento")),
                ])
            t_eq = Table(dados_eq, colWidths=[55*mm, 35*mm, 22*mm, 30*mm, 28*mm, 40*mm], repeatRows=1)
            t_eq.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F2937")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 8),
                ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#BFC6D0")),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ]))
            story += [t_eq, Spacer(1, 8)]

        itens_op = _cmv_itens_operacionais(itens)
        if not itens_op.empty:
            story.append(Paragraph("Consumo real por item", subtitulo))
            dados = [[
                "Categoria", "Item", "Sistema", "Ida", "Volta",
                "Conf. Final", "Consumo", "Diverg.", "Custo Real"
            ]]
            bases_pdf = _cmv_carregar_bases_precos()
            for _, item in itens_op.iterrows():
                calculo = _cmv_calcular_item(item)
                info_op = _cmv_info_unidade_operacional(item, bases_pdf)
                fator = max(_cmv_num(info_op.get("fator"), 1.0), 1e-12)
                consumo_raw = _cmv_num(item.get("cmv_consumo_real"), calculo["consumo"])
                diverg_raw = _cmv_num(item.get("cmv_divergencia"), calculo["divergencia"])
                custo_real = _cmv_num(item.get("cmv_custo_real"), calculo["custo_real"])
                dados.append([
                    info_op.get("categoria") or _cmv_texto(item.get("categoria")),
                    _cmv_texto(item.get("produto")),
                    f"{_cmv_qtd_operacional_texto(_cmv_num(item.get('quantidade')) / fator)} {info_op.get('unidade')}",
                    _cmv_qtd_operacional_texto(_cmv_num(item.get("quantidade_ida")) / fator),
                    _cmv_qtd_operacional_texto(_cmv_num(item.get("quantidade_volta")) / fator),
                    _cmv_qtd_operacional_texto(_cmv_num(item.get("quantidade_estoquista")) / fator),
                    _cmv_qtd_operacional_texto(consumo_raw / fator),
                    _cmv_qtd_operacional_texto(diverg_raw / fator),
                    _cmv_moeda(custo_real),
                ])

            t_itens = Table(
                dados,
                repeatRows=1,
                colWidths=[25*mm, 55*mm, 28*mm, 22*mm, 22*mm, 26*mm, 25*mm, 25*mm, 30*mm],
            )
            t_itens.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F2937")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 7.2),
                ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#BFC6D0")),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("LEFTPADDING", (0,0), (-1,-1), 3),
                ("RIGHTPADDING", (0,0), (-1,-1), 3),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ]))
            story += [t_itens, Spacer(1, 8)]

        if not custos.empty:
            story.append(Paragraph("Custos reais lançados", subtitulo))
            dados_c = [["Descrição", "Valor"]]
            for _, c in custos.iterrows():
                dados_c.append([
                    _cmv_texto(c.get("descricao")),
                    _cmv_moeda(c.get("valor")),
                ])
            t_c = Table(dados_c, repeatRows=1, colWidths=[180*mm, 45*mm])
            t_c.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F2937")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 8),
                ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#BFC6D0")),
            ]))
            story += [t_c, Spacer(1, 8)]

        if not adendos.empty:
            story.append(Paragraph("Adendos", subtitulo))
            dados_a = [["Tipo", "Descrição", "Valor cobrado", "Status"]]
            for _, a in adendos.iterrows():
                dados_a.append([
                    _cmv_texto(a.get("tipo")),
                    _cmv_texto(a.get("descricao")),
                    _cmv_moeda(a.get("valor_cliente")),
                    _cmv_texto(a.get("status")),
                ])
            t_a = Table(dados_a, repeatRows=1, colWidths=[50*mm, 135*mm, 40*mm, 35*mm])
            t_a.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F2937")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 7.5),
                ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#BFC6D0")),
            ]))
            story += [t_a, Spacer(1, 8)]

        story.append(Spacer(1, 5))
        story.append(Paragraph(
            f"Relatório gerado pelo Ellosystem em {datetime.now().strftime('%d/%m/%Y %H:%M')}.",
            normal,
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue(), None

    def _cmv_mostrar_metricas(resumo):
        # ========================================================
        # LAYOUT EXECUTIVO DO RESULTADO
        # Mantém a mesma regra de cálculo da V4.2; muda somente a apresentação.
        # ========================================================

        with st.container(border=True):
            st.markdown("#### 💰 Receita do Evento")
            c1, c2, c3 = st.columns(3)
            c1.metric(
                "Venda Original",
                _cmv_moeda(resumo["venda_original"]),
            )
            c2.metric(
                "Adendos / Receita Extra",
                _cmv_moeda(resumo["adendos_cliente"]),
            )
            c3.metric(
                "Faturamento Real",
                _cmv_moeda(resumo["faturamento_real"]),
            )

        with st.container(border=True):
            st.markdown("#### 📦 Composição do Custo Real")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(
                "Produtos Consumidos",
                _cmv_moeda(resumo["custo_produtos"]),
            )
            c2.metric(
                "Cachês / Equipe",
                _cmv_moeda(resumo.get("custo_equipe", 0)),
            )
            c3.metric(
                "Outros Custos",
                _cmv_moeda(resumo.get("outros_custos_manuais", 0)),
            )
            c4.metric(
                "Custo Total",
                _cmv_moeda(resumo["custo_total"]),
            )

        with st.container(border=True):
            st.markdown("#### 📊 Resultado do Evento")
            c1, c2, c3 = st.columns(3)
            c1.metric(
                "Lucro Real",
                _cmv_moeda(resumo["lucro_real"]),
            )
            c2.metric(
                "CMV",
                f"{resumo['cmv_percentual']:.2f}%",
            )
            c3.metric(
                "Previsto x Real",
                _cmv_moeda(resumo["diferenca_previsto"]),
            )

        if resumo.get("qtd_caches", 0) > 0:
            with st.expander("👥 Detalhes dos cachês / equipe", expanded=False):
                ce1, ce2, ce3 = st.columns(3)
                ce1.metric(
                    "Registros",
                    int(resumo.get("qtd_caches", 0)),
                )
                ce2.metric(
                    "Pago",
                    _cmv_moeda(resumo.get("custo_equipe_pago", 0)),
                )
                ce3.metric(
                    "Pendente",
                    _cmv_moeda(resumo.get("custo_equipe_pendente", 0)),
                )
                st.caption(
                    "O custo da equipe já pertence ao CMV quando o cachê é registrado. "
                    "O Financeiro considera como saída somente o que estiver marcado como pago."
                )

    # ============================================================
    # CARREGAMENTO BASE
    # ============================================================

    try:
        df_eventos_cmv = _cmv_carregar_eventos()
    except Exception as erro:
        st.error(f"Erro ao carregar eventos do CMV: {erro}")
        df_eventos_cmv = pd.DataFrame()

    tab_fechamento, tab_resultado, tab_historico, tab_adendos = st.tabs([
        "🧾 Fechamento do Evento",
        "📊 Resultado Real",
        "📚 Histórico de Consumo",
        "➕ Adendos",
    ])

    # ============================================================
    # 1 — FECHAMENTO DO EVENTO
    # ============================================================

    with tab_fechamento:

        st.subheader("🧾 Fechamento Operacional")
        st.caption(
            "Transcreva o checklist físico. O sistema calcula Consumo, "
            "Divergência e Custo Real sem alterar o orçamento original."
        )

        if df_eventos_cmv.empty:
            st.info("Nenhum evento aprovado/finalizado disponível.")
        else:
            opcoes = {
                _cmv_evento_rotulo(row): int(row.get("id"))
                for _, row in df_eventos_cmv.iterrows()
            }
            escolha = st.selectbox(
                "Selecione o evento",
                list(opcoes.keys()),
                key="cmv_evento_fechamento",
            )
            evento_id = opcoes[escolha]
            evento = df_eventos_cmv[
                pd.to_numeric(df_eventos_cmv["id"], errors="coerce") == evento_id
            ].iloc[0]

            itens = _cmv_carregar_itens(evento_id)
            custos = _cmv_carregar_custos(evento_id)
            adendos = _cmv_carregar_adendos(evento_id)
            caches_registro = _cmv_carregar_caches_evento(evento_id)
            itens_op = _cmv_itens_operacionais(itens)

            status_cmv = _cmv_texto(evento.get("cmv_status")) or "aberto"
            fechado = status_cmv.lower() == "fechado"

            st.markdown(
                f"### 🍸 {_cmv_texto(evento.get('cliente')) or 'Evento sem cliente'}"
            )
            st.caption(
                f"📅 {_cmv_data_br(evento.get('data'))} | "
                f"📍 {_cmv_texto(evento.get('cidade'))} | "
                f"🆔 Evento #{evento_id} | "
                f"CMV: {'🟢 FECHADO' if fechado else '🟡 ABERTO'}"
            )

            info1, info2, info3, info4 = st.columns(4)
            info1.metric("Convidados", int(_cmv_num(evento.get("convidados", 0))))
            info2.metric("Venda", _cmv_moeda(evento.get("venda", 0)))
            info3.metric("Custo Previsto", _cmv_moeda(evento.get("custo", 0)))
            info4.metric("Itens Checklist", len(itens_op))

            # ----------------------------------------------------
            # RECUPERAÇÃO DE PREÇOS PARA EVENTOS ANTIGOS
            # ----------------------------------------------------
            if not fechado and not itens_op.empty:
                sem_custo = []
                for _, item_tmp in itens_op.iterrows():
                    if _cmv_custo_unitario_operacional(item_tmp) <= 0:
                        sem_custo.append(_cmv_texto(item_tmp.get("produto")))

                if sem_custo:
                    st.warning(
                        f"💲 {len(sem_custo)} item(ns) deste evento ainda estão sem custo unitário. "
                        "Isso acontece principalmente em eventos criados antes do snapshot de preços."
                    )
                    st.caption(
                        "O botão abaixo usa os preços que estão cadastrados AGORA em Precificação, "
                        "grava esse valor no evento e não sobrescreve itens que já possuem custo. "
                        "Assim, reajustes futuros de preço não mudam este fechamento."
                    )

                    col_preco1, col_preco2 = st.columns([2, 1])
                    if col_preco1.button(
                        "💲 Preencher custos zerados com os preços atuais",
                        key=f"cmv_preencher_precos_{evento_id}",
                        use_container_width=True,
                    ):
                        resultado_preco = _cmv_preencher_custos_zerados(evento_id)
                        st.session_state["cmv_resultado_precos"] = {
                            "evento_id": evento_id,
                            **resultado_preco,
                        }
                        st.rerun()

                    with col_preco2:
                        with st.expander("⚙️ Demais eventos"):
                            st.caption(
                                "Use uma única vez antes de reajustar a Precificação. "
                                "Somente eventos com CMV aberto e itens zerados serão atualizados."
                            )
                            confirmar_todos = st.checkbox(
                                "Confirmo usar os preços atuais",
                                key=f"cmv_confirmar_precos_todos_{evento_id}",
                            )
                            if st.button(
                                "Aplicar aos eventos abertos",
                                key=f"cmv_precos_todos_{evento_id}",
                                disabled=not confirmar_todos,
                                use_container_width=True,
                            ):
                                bases_precos = _cmv_carregar_bases_precos()
                                total_atualizados = 0
                                total_pendencias = []
                                eventos_processados = 0

                                for _, ev_tmp in df_eventos_cmv.iterrows():
                                    if (_cmv_texto(ev_tmp.get("cmv_status")) or "aberto").lower() == "fechado":
                                        continue
                                    ev_id_tmp = int(ev_tmp.get("id"))
                                    res_tmp = _cmv_preencher_custos_zerados(
                                        ev_id_tmp,
                                        bases=bases_precos,
                                    )
                                    if res_tmp["atualizados"] > 0 or res_tmp["pendencias"]:
                                        eventos_processados += 1
                                    total_atualizados += res_tmp["atualizados"]
                                    for pend in res_tmp["pendencias"]:
                                        total_pendencias.append({
                                            "Evento": ev_id_tmp,
                                            **pend,
                                        })

                                st.session_state["cmv_resultado_precos_todos"] = {
                                    "eventos": eventos_processados,
                                    "atualizados": total_atualizados,
                                    "pendencias": total_pendencias,
                                }
                                st.rerun()

            msg_preco = st.session_state.pop("cmv_resultado_precos", None)
            if msg_preco and msg_preco.get("evento_id") == evento_id:
                st.success(
                    f"✅ {msg_preco.get('atualizados', 0)} item(ns) receberam o preço atual da Precificação."
                )
                if msg_preco.get("pendencias"):
                    st.warning(
                        f"{len(msg_preco['pendencias'])} item(ns) não puderam ser associados automaticamente."
                    )
                    st.dataframe(
                        pd.DataFrame(msg_preco["pendencias"]),
                        use_container_width=True,
                        hide_index=True,
                    )

            msg_todos = st.session_state.pop("cmv_resultado_precos_todos", None)
            if msg_todos:
                st.success(
                    f"✅ Atualização concluída: {msg_todos.get('atualizados', 0)} item(ns) "
                    f"atualizados em {msg_todos.get('eventos', 0)} evento(s) aberto(s)."
                )
                if msg_todos.get("pendencias"):
                    st.warning(
                        f"{len(msg_todos['pendencias'])} associação(ões) ficaram pendentes para revisão."
                    )
                    st.dataframe(
                        pd.DataFrame(msg_todos["pendencias"]),
                        use_container_width=True,
                        hide_index=True,
                    )

            # ----------------------------------------------------
            # CACHÊS — CUSTO REAL DE EQUIPE
            # ----------------------------------------------------
            try:
                data_evento_dt = pd.to_datetime(evento.get("data"), errors="coerce")
                evento_ja_ocorreu = (
                    pd.notna(data_evento_dt)
                    and data_evento_dt.date() <= datetime.now().date()
                )
            except Exception:
                evento_ja_ocorreu = False

            resumo_cache_evento = _cmv_resumo_caches(caches_registro)
            if resumo_cache_evento["qtd"] > 0:
                _cmv_aviso(
                    f"👥 Custo real de equipe vindo da aba Cachês: "
                    f"{_cmv_moeda(resumo_cache_evento['total'])} | "
                    f"Pago: {_cmv_moeda(resumo_cache_evento['pago'])} | "
                    f"Pendente: {_cmv_moeda(resumo_cache_evento['pendente'])}. "
                    "O CMV considera o total registrado; o Financeiro considera somente o que foi pago.",
                    "sucesso",
                )
            elif evento_ja_ocorreu:
                _cmv_aviso(
                    "👥 Este evento já ocorreu e ainda não possui cachês registrados. "
                    "Você pode usar o custo manual de equipe como fallback, mas o ideal é "
                    "lançar os profissionais na aba Cachês para formar o histórico real.",
                    "alerta",
                )

            if fechado:
                _cmv_aviso(
                    "✅ Este evento já possui fechamento de CMV. "
                    "Reabra somente se precisar corrigir alguma conferência.",
                    "sucesso",
                )

                col_reabrir, _ = st.columns([1, 3])
                if col_reabrir.button(
                    "🔓 Reabrir fechamento",
                    key=f"cmv_reabrir_{evento_id}",
                    use_container_width=True,
                ):
                    supabase.table("eventos").update({
                        "cmv_status": "aberto",
                        "cmv_data_fechamento": None,
                    }).eq("id", evento_id).execute()
                    st.success("Fechamento reaberto.")
                    st.rerun()

            if itens_op.empty:
                _cmv_aviso(
                    "👷 Evento sem consumo de produtos no checklist. "
                    "O fechamento será financeiro. Se houver cachês registrados, o custo de equipe "
                    "já será puxado automaticamente; lance abaixo apenas os demais custos reais.",
                    "info",
                )
            else:
                # ----------------------------------------------------
                # UNIDADES OPERACIONAIS DO CHECKLIST
                # Mantém o banco em unidade técnica e mostra para a equipe
                # kg / garrafas conforme a Precificação.
                # ----------------------------------------------------
                bases_unidades = _cmv_carregar_bases_precos()
                linhas_base = []

                for _, item_op in itens_op.reset_index(drop=True).iterrows():
                    info_op = _cmv_info_unidade_operacional(item_op, bases_unidades)
                    fator = max(_cmv_num(info_op.get("fator"), 1.0), 1e-12)

                    linhas_base.append({
                        "_id": int(item_op.get("id")),
                        "_fator": fator,
                        "_passo": _cmv_num(info_op.get("passo"), 0.1),
                        "_custo_unit_exibicao": _cmv_num(
                            info_op.get("custo_unitario_exibicao"), 0
                        ),
                        "Categoria": info_op.get("categoria") or _cmv_texto(item_op.get("categoria")),
                        "Item": _cmv_texto(item_op.get("produto")),
                        "Sistema": round(_cmv_num(item_op.get("quantidade")) / fator, 1),
                        "Ida": round(_cmv_num(item_op.get("quantidade_ida")) / fator, 1),
                        "Volta": round(_cmv_num(item_op.get("quantidade_volta")) / fator, 1),
                        "Conferência Final": round(
                            _cmv_num(item_op.get("quantidade_estoquista")) / fator, 1
                        ),
                        "Unidade": info_op.get("unidade") or "un",
                    })

                base = pd.DataFrame(linhas_base)

                st.markdown("### 📋 Checklist de Fechamento")
                st.caption(
                    "Quantidades exibidas na unidade operacional: frutas/insumos em kg e "
                    "produções artesanais em garrafas conforme a embalagem cadastrada na Precificação."
                )
                editor = st.data_editor(
                    base[[
                        "Categoria", "Item", "Sistema", "Ida", "Volta",
                        "Conferência Final", "Unidade",
                    ]],
                    use_container_width=True,
                    hide_index=True,
                    num_rows="fixed",
                    disabled=(
                        ["Categoria", "Item", "Sistema", "Ida", "Volta", "Conferência Final", "Unidade"]
                        if fechado
                        else ["Categoria", "Item", "Sistema", "Unidade"]
                    ),
                    column_config={
                        "Sistema": st.column_config.NumberColumn(format="%.1f"),
                        "Ida": st.column_config.NumberColumn(min_value=0.0, step=0.1, format="%.1f"),
                        "Volta": st.column_config.NumberColumn(min_value=0.0, step=0.1, format="%.1f"),
                        "Conferência Final": st.column_config.NumberColumn(min_value=0.0, step=0.1, format="%.1f"),
                    },
                    key=f"cmv_editor_fechamento_{evento_id}",
                )

                preview = editor.copy()
                preview["Consumo"] = (
                    pd.to_numeric(preview["Ida"], errors="coerce").fillna(0)
                    - pd.to_numeric(preview["Conferência Final"], errors="coerce").fillna(0)
                )
                preview["Divergência"] = (
                    pd.to_numeric(preview["Volta"], errors="coerce").fillna(0)
                    - pd.to_numeric(preview["Conferência Final"], errors="coerce").fillna(0)
                )

                custos_unit = []
                custos_reais = []
                for indice, linha in preview.iterrows():
                    custo_unit_exib = _cmv_num(base.iloc[indice]["_custo_unit_exibicao"])
                    custo_real = _cmv_num(linha["Consumo"]) * custo_unit_exib
                    custos_unit.append(custo_unit_exib)
                    custos_reais.append(custo_real)

                preview["Custo Unit."] = custos_unit
                preview["Custo Real"] = custos_reais

                st.markdown("#### 🔎 Resultado calculado")
                st.dataframe(
                    preview[[
                        "Categoria", "Item", "Sistema", "Ida", "Volta",
                        "Conferência Final", "Consumo", "Divergência",
                        "Custo Unit.", "Custo Real", "Unidade",
                    ]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Sistema": st.column_config.NumberColumn(format="%.1f"),
                        "Ida": st.column_config.NumberColumn(format="%.1f"),
                        "Volta": st.column_config.NumberColumn(format="%.1f"),
                        "Conferência Final": st.column_config.NumberColumn(format="%.1f"),
                        "Consumo": st.column_config.NumberColumn(format="%.1f"),
                        "Divergência": st.column_config.NumberColumn(format="%.1f"),
                        "Custo Unit.": st.column_config.NumberColumn(format="R$ %.2f"),
                        "Custo Real": st.column_config.NumberColumn(format="R$ %.2f"),
                    },
                )

                erros = []
                avisos = []
                for indice, linha in preview.iterrows():
                    ida = _cmv_num(linha["Ida"])
                    volta = _cmv_num(linha["Volta"])
                    final = _cmv_num(linha["Conferência Final"])
                    sistema = _cmv_num(linha["Sistema"])
                    item_nome = _cmv_texto(linha["Item"])
                    passo = _cmv_num(base.iloc[indice]["_passo"], 0.1)

                    if volta > ida:
                        erros.append(f"{item_nome}: Volta maior que Ida.")
                    if final > ida:
                        erros.append(f"{item_nome}: Conferência Final maior que Ida.")
                    if sistema > 0 and ida == 0:
                        avisos.append(f"{item_nome}: previsto {sistema:g}, mas Ida está zerada.")

                    if abs(passo - 0.5) < 1e-9:
                        for valor_nome, valor in [
                            ("Ida", ida), ("Volta", volta), ("Conferência Final", final)
                        ]:
                            if abs(valor * 2 - round(valor * 2)) > 1e-7:
                                erros.append(
                                    f"{item_nome}: {valor_nome} deve usar passos de 0,5 garrafa."
                                )

                for erro in sorted(set(erros)):
                    st.error(erro)
                if avisos and not fechado:
                    with st.expander(f"⚠️ {len(avisos)} aviso(s) de conferência", expanded=False):
                        for aviso in avisos:
                            st.write(f"• {aviso}")

                if not fechado:
                    confirmar = st.checkbox(
                        "Confirmo que os valores acima foram transcritos do checklist físico do evento.",
                        key=f"cmv_confirmar_check_{evento_id}",
                    )

                    if st.button(
                        "💾 Salvar conferência no CMV",
                        key=f"cmv_salvar_conferencia_{evento_id}",
                        use_container_width=True,
                    ):
                        if erros:
                            st.error("Corrija os erros de conferência antes de salvar.")
                        elif not confirmar:
                            st.warning("Marque a confirmação do checklist antes de salvar.")
                        else:
                            for indice, linha in preview.iterrows():
                                item_id = int(base.iloc[indice]["_id"])
                                fator = _cmv_num(base.iloc[indice]["_fator"], 1.0)
                                ida_raw = _cmv_num(linha["Ida"]) * fator
                                volta_raw = _cmv_num(linha["Volta"]) * fator
                                final_raw = _cmv_num(linha["Conferência Final"]) * fator
                                consumo_raw = (_cmv_num(linha["Ida"]) - _cmv_num(linha["Conferência Final"])) * fator
                                diverg_raw = (_cmv_num(linha["Volta"]) - _cmv_num(linha["Conferência Final"])) * fator

                                supabase.table("evento_itens").update({
                                    "quantidade_ida": ida_raw,
                                    "quantidade_volta": volta_raw,
                                    "quantidade_estoquista": final_raw,
                                    "cmv_conferido": True,
                                    "cmv_consumo_real": consumo_raw,
                                    "cmv_divergencia": diverg_raw,
                                    "cmv_custo_real": _cmv_num(linha["Custo Real"]),
                                }).eq("id", item_id).execute()

                            st.success("✅ Conferência salva no CMV.")
                            st.rerun()

            st.markdown("<div style=\"height: 0.9rem;\"></div>", unsafe_allow_html=True)
            st.markdown("### 💸 Custos Reais do Evento")
            st.caption(
                "O custo de produtos vem do checklist e o custo de equipe vem automaticamente "
                "da aba Cachês quando houver registros vinculados. Use esta área para transporte, "
                "locação, compras emergenciais, avarias e outros custos reais. O custo previsto "
                "do orçamento é apenas comparação e nunca é somado novamente."
            )

            if not fechado:
                with st.form(f"cmv_form_custo_{evento_id}", clear_on_submit=True):
                    c1, c2 = st.columns([2, 1])
                    categorias_disponiveis = list(CATEGORIAS_CUSTO_MANUAL)
                    if resumo_cache_evento["qtd"] > 0:
                        categorias_disponiveis = [
                            c for c in categorias_disponiveis if c != "Cachê / Equipe"
                        ]
                        indice_categoria_padrao = 0
                    else:
                        indice_categoria_padrao = (
                            categorias_disponiveis.index("Cachê / Equipe")
                            if itens_op.empty and "Cachê / Equipe" in categorias_disponiveis
                            else 0
                        )
                    categoria_custo = c1.selectbox(
                        "Categoria",
                        categorias_disponiveis,
                        index=indice_categoria_padrao,
                        key=f"cmv_cat_custo_{evento_id}",
                    )
                    valor_custo = c2.number_input(
                        "Valor",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        key=f"cmv_valor_custo_{evento_id}",
                    )
                    descricao_custo = st.text_input(
                        "Descrição",
                        key=f"cmv_desc_custo_{evento_id}",
                    )
                    salvar_custo = st.form_submit_button("➕ Lançar custo real")

                    if salvar_custo:
                        if valor_custo <= 0:
                            st.warning("Informe um valor maior que zero.")
                        elif not descricao_custo.strip():
                            st.warning("Informe uma descrição.")
                        else:
                            supabase.table("evento_custos").insert({
                                "evento_id": int(evento_id),
                                "descricao": f"{categoria_custo} - {descricao_custo.strip()}",
                                "valor": float(valor_custo),
                            }).execute()
                            st.success("Custo real lançado.")
                            st.rerun()

            if not custos.empty:
                for _, custo in custos.iterrows():
                    cc1, cc2, cc3 = st.columns([6, 2, 1])
                    cc1.write(_cmv_texto(custo.get("descricao")))
                    cc2.write(_cmv_moeda(custo.get("valor")))
                    if not fechado:
                        if cc3.button("🗑️", key=f"cmv_del_custo_{custo.get('id')}"):
                            supabase.table("evento_custos").delete().eq(
                                "id", int(custo.get("id"))
                            ).execute()
                            st.rerun()

            # Recarrega os dados antes do fechamento financeiro.
            itens_atual = _cmv_carregar_itens(evento_id)
            custos_atual = _cmv_carregar_custos(evento_id)
            adendos_atual = _cmv_carregar_adendos(evento_id)
            caches_atual = _cmv_carregar_caches_evento(evento_id)
            resumo = _cmv_resumo_financeiro(
                evento, itens_atual, custos_atual, adendos_atual, caches_atual
            )

            st.markdown("<div style=\"height: 1.2rem;\"></div>", unsafe_allow_html=True)
            st.markdown("### 📊 Prévia do Resultado Real")
            _cmv_mostrar_metricas(resumo)

            if resumo["diferenca_previsto"] >= 0:
                st.success(
                    f"💚 Custo real abaixo do previsto em "
                    f"{_cmv_moeda(resumo['diferenca_previsto'])}."
                )
            else:
                st.warning(
                    f"🟠 Custo real acima do previsto em "
                    f"{_cmv_moeda(abs(resumo['diferenca_previsto']))}."
                )

            if not fechado:
                itens_op_atual = _cmv_itens_operacionais(itens_atual)
                # Evento somente de mão de obra/serviço pode ser fechado sem checklist de produtos.
                todos_conferidos = itens_op_atual.empty
                if not itens_op_atual.empty and "cmv_conferido" in itens_op_atual.columns:
                    todos_conferidos = itens_op_atual["cmv_conferido"].fillna(False).astype(bool).all()

                responsavel = st.text_input(
                    "Responsável pelo fechamento",
                    value=_cmv_texto(evento.get("cmv_responsavel")),
                    key=f"cmv_responsavel_{evento_id}",
                )

                if itens_op_atual.empty:
                    st.info(
                        "✅ Este evento não possui itens de consumo para conferir. "
                        "Revise os custos reais lançados e finalize normalmente."
                    )
                elif not todos_conferidos:
                    st.warning(
                        "O evento ainda possui itens sem conferência salva no CMV. "
                        "Salve o checklist antes de finalizar."
                    )

                if resumo.get("custo_equipe_manual_ignorado", 0) > 0:
                    st.warning(
                        "⚠️ Há lançamento manual antigo de Cachê / Equipe neste evento, mas ele "
                        "está sendo IGNORADO porque já existem registros na aba Cachês. Isso evita "
                        "duplicidade no custo real."
                    )

                equipe_sem_custo_confirmada = True
                if resumo.get("custo_equipe", 0) <= 0:
                    st.warning(
                        "⚠️ Nenhum custo real de equipe foi encontrado. Para evitar esquecer cachês, "
                        "o fechamento só será liberado se você confirmar explicitamente que este "
                        "evento realmente não teve custo de equipe."
                    )
                    equipe_sem_custo_confirmada = st.checkbox(
                        "Confirmo que este evento realmente NÃO teve custo de equipe / cachês.",
                        key=f"cmv_sem_custo_equipe_{evento_id}",
                    )

                confirmar_fechamento = st.checkbox(
                    "Confirmo o fechamento financeiro e operacional deste evento.",
                    key=f"cmv_confirmar_fechamento_{evento_id}",
                )

                if st.button(
                    "🔒 Finalizar CMV do Evento",
                    key=f"cmv_finalizar_{evento_id}",
                    use_container_width=True,
                ):
                    if not todos_conferidos:
                        st.error("Existem itens ainda não conferidos.")
                    elif not equipe_sem_custo_confirmada:
                        st.error(
                            "Lance os cachês da equipe ou confirme explicitamente que o evento "
                            "não teve custo de equipe."
                        )
                    elif not responsavel.strip():
                        st.warning("Informe o responsável pelo fechamento.")
                    elif not confirmar_fechamento:
                        st.warning("Confirme o fechamento antes de finalizar.")
                    else:
                        supabase.table("eventos").update({
                            "cmv_status": "fechado",
                            "cmv_data_fechamento": datetime.now().isoformat(),
                            "cmv_responsavel": responsavel.strip(),
                            "cmv_custo_produtos": float(resumo["custo_produtos"]),
                            "cmv_custo_equipe": float(resumo["custo_equipe"]),
                            "cmv_custos_extras": float(resumo["outros_custos_manuais"]),
                            "cmv_custo_adendos": 0.0,
                            "cmv_custo_total": float(resumo["custo_total"]),
                            "cmv_faturamento_total": float(resumo["faturamento_real"]),
                            "cmv_percentual": float(resumo["cmv_percentual"]),
                            "cmv_lucro_real": float(resumo["lucro_real"]),
                        }).eq("id", evento_id).execute()

                        st.success("✅ CMV do evento fechado e congelado com sucesso!")
                        st.rerun()

    # ============================================================
    # 2 — RESULTADO REAL
    # ============================================================

    with tab_resultado:

        st.subheader("📊 Resultado Real por Evento")

        if df_eventos_cmv.empty:
            st.info("Nenhum evento disponível.")
        else:
            opcoes_resultado = {
                _cmv_evento_rotulo(row): int(row.get("id"))
                for _, row in df_eventos_cmv.iterrows()
            }
            escolha_r = st.selectbox(
                "Evento para análise",
                list(opcoes_resultado.keys()),
                key="cmv_evento_resultado",
            )
            evento_id_r = opcoes_resultado[escolha_r]
            evento_r = df_eventos_cmv[
                pd.to_numeric(df_eventos_cmv["id"], errors="coerce") == evento_id_r
            ].iloc[0]

            itens_r = _cmv_carregar_itens(evento_id_r)
            custos_r = _cmv_carregar_custos(evento_id_r)
            adendos_r = _cmv_carregar_adendos(evento_id_r)
            caches_r = _cmv_carregar_caches_evento(evento_id_r)
            resumo_calc = _cmv_resumo_financeiro(
                evento_r, itens_r, custos_r, adendos_r, caches_r
            )
            resumo_r = _cmv_resumo_snapshot(evento_r, resumo_calc)

            fechado_r = _cmv_texto(evento_r.get("cmv_status")).lower() == "fechado"
            st.markdown(
                f"### {_cmv_texto(evento_r.get('cliente')) or 'Evento sem cliente'}"
            )
            st.caption(
                f"📅 {_cmv_data_br(evento_r.get('data'))} | "
                f"📍 {_cmv_texto(evento_r.get('cidade'))} | "
                f"🆔 #{evento_id_r} | "
                f"{'🟢 CMV FECHADO' if fechado_r else '🟡 CMV EM ABERTO'}"
            )

            _cmv_mostrar_metricas(resumo_r)

            st.markdown("### 📦 Consumo e Retorno Gravados")
            itens_op_r = _cmv_itens_operacionais(itens_r)
            if itens_op_r.empty:
                st.info("Nenhum item operacional encontrado.")
            else:
                linhas = []
                bases_detalhe = _cmv_carregar_bases_precos()
                for _, item in itens_op_r.iterrows():
                    calc = _cmv_calcular_item(item)
                    info_op = _cmv_info_unidade_operacional(item, bases_detalhe)
                    fator = max(_cmv_num(info_op.get("fator"), 1.0), 1e-12)
                    linhas.append({
                        "Categoria": info_op.get("categoria") or _cmv_texto(item.get("categoria")),
                        "Item": _cmv_texto(item.get("produto")),
                        "Sistema": round(_cmv_num(item.get("quantidade")) / fator, 1),
                        "Ida": round(_cmv_num(item.get("quantidade_ida")) / fator, 1),
                        "Volta": round(_cmv_num(item.get("quantidade_volta")) / fator, 1),
                        "Conferência Final": round(_cmv_num(item.get("quantidade_estoquista")) / fator, 1),
                        "Consumo": round(_cmv_num(item.get("cmv_consumo_real"), calc["consumo"]) / fator, 1),
                        "Divergência": round(_cmv_num(item.get("cmv_divergencia"), calc["divergencia"]) / fator, 1),
                        "Custo Real": _cmv_num(item.get("cmv_custo_real"), calc["custo_real"]),
                        "Unidade": info_op.get("unidade") or _cmv_texto(item.get("unidade")),
                    })
                df_detalhe = pd.DataFrame(linhas)
                st.dataframe(
                    df_detalhe,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Sistema": st.column_config.NumberColumn(format="%.1f"),
                        "Ida": st.column_config.NumberColumn(format="%.1f"),
                        "Volta": st.column_config.NumberColumn(format="%.1f"),
                        "Conferência Final": st.column_config.NumberColumn(format="%.1f"),
                        "Consumo": st.column_config.NumberColumn(format="%.1f"),
                        "Divergência": st.column_config.NumberColumn(format="%.1f"),
                        "Custo Real": st.column_config.NumberColumn(format="R$ %.2f"),
                    },
                )

            if not caches_r.empty:
                with st.expander("👥 Equipe / Cachês do evento", expanded=False):
                    cols_cache = [
                        c for c in [
                            "nome", "funcao", "horas", "horas_extras", "valor",
                            "status", "forma_pagamento", "data_pagamento"
                        ] if c in caches_r.columns
                    ]
                    st.dataframe(
                        caches_r[cols_cache],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "valor": st.column_config.NumberColumn(format="R$ %.2f"),
                        },
                    )

            if not custos_r.empty:
                with st.expander("💸 Outros custos reais", expanded=False):
                    st.dataframe(custos_r, use_container_width=True, hide_index=True)

            if not adendos_r.empty:
                with st.expander("➕ Adendos do evento", expanded=False):
                    cols_a = [
                        c for c in [
                            "tipo", "descricao", "valor_cliente",
                            "status", "forma_pagamento", "data_pagamento"
                        ] if c in adendos_r.columns
                    ]
                    st.dataframe(adendos_r[cols_a], use_container_width=True, hide_index=True)

            if fechado_r:
                pdf_cmv, erro_pdf = _cmv_pdf_fechamento(
                    evento_r, itens_r, custos_r, adendos_r, caches_r, resumo_r
                )
                if pdf_cmv:
                    st.download_button(
                        "📄 Baixar Relatório de Fechamento / CMV",
                        data=pdf_cmv,
                        file_name=f"CMV_evento_{evento_id_r}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"cmv_pdf_{evento_id_r}",
                    )
                elif erro_pdf:
                    st.warning(erro_pdf)
            else:
                st.info(
                    "Finalize o CMV na primeira aba para liberar o relatório PDF definitivo."
                )

    # ============================================================
    # 3 — HISTÓRICO DE CONSUMO
    # ============================================================

    with tab_historico:

        st.subheader("📚 Histórico de Consumo")
        st.caption(
            "Base real dos eventos já fechados. Use esta visão para descobrir "
            "médias de consumo, comportamento por item e divergências recorrentes."
        )

        if df_eventos_cmv.empty or "cmv_status" not in df_eventos_cmv.columns:
            st.info("Ainda não existem fechamentos de CMV registrados.")
        else:
            fechados = df_eventos_cmv[
                df_eventos_cmv["cmv_status"].fillna("").astype(str).str.lower() == "fechado"
            ].copy()

            if fechados.empty:
                st.info("Finalize pelo menos um evento para formar o histórico de consumo.")
            else:
                todos_itens = pd.DataFrame(
                    supabase.table("evento_itens").select("*").execute().data or []
                )
                ids_fechados = set(
                    pd.to_numeric(fechados["id"], errors="coerce").dropna().astype(int).tolist()
                )
                todos_itens = todos_itens[
                    pd.to_numeric(todos_itens["evento_id"], errors="coerce")
                    .isin(ids_fechados)
                ].copy()
                todos_itens = _cmv_itens_operacionais(todos_itens)

                if todos_itens.empty:
                    st.info("Os eventos fechados ainda não possuem consumo operacional gravado.")
                else:
                    meta_eventos = fechados[[
                        c for c in ["id", "cliente", "data", "tipo_evento", "convidados"]
                        if c in fechados.columns
                    ]].copy()
                    meta_eventos.rename(columns={"id": "evento_id"}, inplace=True)

                    hist = todos_itens.merge(meta_eventos, on="evento_id", how="left")
                    hist["Consumo"] = pd.to_numeric(
                        hist.get("cmv_consumo_real", 0), errors="coerce"
                    ).fillna(0)
                    hist["Divergência"] = pd.to_numeric(
                        hist.get("cmv_divergencia", 0), errors="coerce"
                    ).fillna(0)
                    hist["Custo Real"] = pd.to_numeric(
                        hist.get("cmv_custo_real", 0), errors="coerce"
                    ).fillna(0)
                    hist["convidados"] = pd.to_numeric(
                        hist.get("convidados", 0), errors="coerce"
                    ).fillna(0)
                    hist["Consumo / Convidado"] = hist.apply(
                        lambda x: x["Consumo"] / x["convidados"]
                        if x["convidados"] > 0 else 0.0,
                        axis=1,
                    )

                    categorias = sorted(
                        hist.get("categoria", pd.Series(dtype=str)).fillna("").astype(str).unique()
                    )
                    filtro_cat = st.selectbox(
                        "Categoria",
                        ["Todas"] + [c for c in categorias if c],
                        key="cmv_hist_cat",
                    )
                    hist_filtrado = hist.copy()
                    if filtro_cat != "Todas":
                        hist_filtrado = hist_filtrado[
                            hist_filtrado["categoria"].astype(str) == filtro_cat
                        ]

                    itens_filtro = sorted(
                        hist_filtrado.get("produto", pd.Series(dtype=str)).fillna("").astype(str).unique()
                    )
                    filtro_item = st.selectbox(
                        "Item",
                        ["Todos"] + [i for i in itens_filtro if i],
                        key="cmv_hist_item",
                    )
                    if filtro_item != "Todos":
                        hist_filtrado = hist_filtrado[
                            hist_filtrado["produto"].astype(str) == filtro_item
                        ]

                    h1, h2, h3, h4 = st.columns(4)
                    h1.metric("Eventos Fechados", fechados["id"].nunique())
                    h2.metric("Registros de Consumo", len(hist_filtrado))
                    h3.metric("Custo Real Produtos", _cmv_moeda(hist_filtrado["Custo Real"].sum()))
                    h4.metric("Divergências", int((hist_filtrado["Divergência"].abs() > 1e-9).sum()))

                    st.markdown("### 📊 Média por Item")
                    agrupado = (
                        hist_filtrado.groupby(
                            ["categoria", "produto", "unidade"],
                            dropna=False,
                        )
                        .agg(
                            Eventos=("evento_id", "nunique"),
                            Consumo_Total=("Consumo", "sum"),
                            Consumo_Medio_Evento=("Consumo", "mean"),
                            Custo_Real_Total=("Custo Real", "sum"),
                            Divergencia_Total=("Divergência", "sum"),
                        )
                        .reset_index()
                        .rename(columns={
                            "categoria": "Categoria",
                            "produto": "Item",
                            "unidade": "Unidade",
                            "Consumo_Total": "Consumo Total",
                            "Consumo_Medio_Evento": "Consumo Médio / Evento",
                            "Custo_Real_Total": "Custo Real Total",
                            "Divergencia_Total": "Divergência Total",
                        })
                    )
                    st.dataframe(
                        agrupado,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Consumo Total": st.column_config.NumberColumn(format="%.3f"),
                            "Consumo Médio / Evento": st.column_config.NumberColumn(format="%.3f"),
                            "Custo Real Total": st.column_config.NumberColumn(format="R$ %.2f"),
                            "Divergência Total": st.column_config.NumberColumn(format="%.3f"),
                        },
                    )

                    with st.expander("🔎 Ver histórico evento por evento", expanded=False):
                        detalhe_hist = hist_filtrado.copy()
                        detalhe_hist["Data"] = detalhe_hist.get("data", "").apply(_cmv_data_br)
                        colunas = [
                            c for c in [
                                "evento_id", "cliente", "Data", "tipo_evento",
                                "categoria", "produto", "Consumo", "unidade",
                                "Divergência", "Custo Real", "Consumo / Convidado"
                            ] if c in detalhe_hist.columns
                        ]
                        detalhe_hist = detalhe_hist[colunas].rename(columns={
                            "evento_id": "Evento #",
                            "cliente": "Cliente",
                            "tipo_evento": "Tipo Evento",
                            "categoria": "Categoria",
                            "produto": "Item",
                            "unidade": "Unidade",
                        })
                        st.dataframe(
                            detalhe_hist,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Consumo": st.column_config.NumberColumn(format="%.3f"),
                                "Divergência": st.column_config.NumberColumn(format="%.3f"),
                                "Custo Real": st.column_config.NumberColumn(format="R$ %.2f"),
                                "Consumo / Convidado": st.column_config.NumberColumn(format="%.4f"),
                            },
                        )

    # ============================================================
    # 4 — ADENDOS
    # ============================================================

    with tab_adendos:

        st.subheader("➕ Adendos dos Eventos")
        st.caption(
            "Adendos são receitas extras cobradas do cliente. Eles aumentam somente o "
            "faturamento do evento e nunca entram como custo. Custos reais devem ser "
            "registrados em Cachês ou em Outros Custos do CMV."
        )

        if df_eventos_cmv.empty:
            st.info("Nenhum evento disponível para adendos.")
        else:
            opcoes_a = {
                _cmv_evento_rotulo(row): int(row.get("id"))
                for _, row in df_eventos_cmv.iterrows()
            }
            escolha_a = st.selectbox(
                "Evento",
                list(opcoes_a.keys()),
                key="cmv_evento_adendo",
            )
            evento_id_a = opcoes_a[escolha_a]

            with st.expander("➕ Cadastrar novo adendo", expanded=False):
                with st.form("cmv_form_adendo", clear_on_submit=True):
                    ca1, ca2 = st.columns(2)
                    tipo_adendo = ca1.selectbox(
                        "Tipo",
                        [
                            "Hora Extra", "Venda de Garrafa", "Quebra de Copo/Taça",
                            "Serviço Adicional", "Outros"
                        ],
                    )
                    status_adendo = ca2.selectbox(
                        "Status", ["Pendente", "Pago", "Cancelado"]
                    )
                    descricao_adendo = st.text_input("Descrição")
                    valor_cliente = st.number_input(
                        "Valor cobrado do cliente",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                    )
                    st.caption(
                        "Adendo aumenta somente o faturamento. Custos de equipe devem ser "
                        "lançados em Cachês; transporte, alimentação, pedágio, hotel e demais "
                        "gastos entram em Outros Custos do CMV."
                    )
                    forma_pagamento = st.selectbox(
                        "Forma de pagamento",
                        ["", "Pix", "Dinheiro", "Cartão", "Transferência", "Outro"],
                    )
                    salvar_adendo = st.form_submit_button("💾 Salvar Adendo")

                if salvar_adendo:
                    if not descricao_adendo.strip():
                        st.warning("Informe a descrição do adendo.")
                    elif valor_cliente <= 0:
                        st.warning("Informe o valor cobrado do cliente.")
                    else:
                        evento_a = df_eventos_cmv[
                            pd.to_numeric(df_eventos_cmv["id"], errors="coerce") == evento_id_a
                        ].iloc[0]
                        supabase.table("aditivos_evento").insert({
                            "evento_id": int(evento_id_a),
                            "evento": _cmv_texto(evento_a.get("cliente")),
                            "tipo": tipo_adendo,
                            "descricao": descricao_adendo.strip(),
                            "valor_cliente": float(valor_cliente),
                            "valor_equipe": 0.0,
                            "status": status_adendo,
                            "forma_pagamento": forma_pagamento,
                            "data_pagamento": None,
                        }).execute()
                        st.success("Adendo cadastrado.")
                        st.rerun()

            adendos_a = _cmv_carregar_adendos(evento_id_a)
            if adendos_a.empty:
                st.info("Nenhum adendo ativo para este evento.")
            else:
                st.markdown("### 📋 Adendos do evento")
                colunas_a = [
                    c for c in [
                        "id", "tipo", "descricao", "valor_cliente",
                        "status", "forma_pagamento", "data_pagamento"
                    ] if c in adendos_a.columns
                ]
                edit_a = adendos_a[colunas_a].copy()
                df_edit_a = st.data_editor(
                    edit_a,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="fixed",
                    disabled=["id"],
                    column_config={
                        "valor_cliente": st.column_config.NumberColumn(format="R$ %.2f"),
                    },
                    key=f"cmv_editor_adendos_{evento_id_a}",
                )

                col_salvar_a, col_excluir_a = st.columns(2)
                if col_salvar_a.button(
                    "💾 Salvar alterações",
                    key=f"cmv_salvar_adendos_{evento_id_a}",
                    use_container_width=True,
                ):
                    for _, linha in df_edit_a.iterrows():
                        adendo_id = linha.get("id")
                        if pd.isna(adendo_id):
                            continue
                        update = {}
                        for campo in [
                            "tipo", "descricao", "status", "forma_pagamento"
                        ]:
                            if campo in linha.index:
                                update[campo] = _cmv_texto(linha.get(campo))
                        if "valor_cliente" in linha.index:
                            update["valor_cliente"] = _cmv_num(linha.get("valor_cliente"))
                        # V4.2: valor_equipe não compõe adendos; limpa ao editar.
                        update["valor_equipe"] = 0.0
                        supabase.table("aditivos_evento").update(update).eq(
                            "id", int(adendo_id)
                        ).execute()
                    st.success("Adendos atualizados.")
                    st.rerun()

                ids_adendos = pd.to_numeric(
                    adendos_a.get("id", pd.Series(dtype=float)), errors="coerce"
                ).dropna().astype(int).tolist()
                if ids_adendos:
                    id_excluir = col_excluir_a.selectbox(
                        "Excluir ID",
                        ids_adendos,
                        key=f"cmv_excluir_id_{evento_id_a}",
                    )
                    if col_excluir_a.button(
                        "🗑️ Excluir",
                        key=f"cmv_excluir_adendo_{evento_id_a}",
                        use_container_width=True,
                    ):
                        supabase.table("aditivos_evento").delete().eq(
                            "id", int(id_excluir)
                        ).execute()
                        st.success("Adendo excluído.")
                        st.rerun()


elif menu == "Financeiro":

    st.title("💰 Financeiro")
    st.caption(
        "Caixa realizado separado do resultado econômico. O caixa mostra dinheiro que efetivamente entrou/saiu; lucro, CMV e reserva vêm dos fechamentos oficiais do CMV."
    )

    def _fin_num(valor, padrao=0.0):
        try:
            if valor is None or pd.isna(valor):
                return float(padrao)
            return float(valor)
        except Exception:
            return float(padrao)

    def _fin_moeda(valor):
        txt = f"{_fin_num(valor):,.2f}"
        txt = txt.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {txt}"

    def _fin_pct(valor):
        return f"{_fin_num(valor):.2f}%".replace(".", ",")

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

        # =====================================================
        # BASES
        # =====================================================
        try:
            df_fin = pd.DataFrame(
                supabase.table("Financeiro").select("*").execute().data or []
            )
        except Exception:
            df_fin = pd.DataFrame()

        try:
            df_eventos = pd.DataFrame(
                supabase.table("eventos")
                .select("*")
                .in_("status", ["aprovado", "finalizado", "concluido", "pago"])
                .execute().data or []
            )
        except Exception:
            df_eventos = pd.DataFrame()

        try:
            df_aditivos = pd.DataFrame(
                supabase.table("aditivos_evento").select("*").execute().data or []
            )
        except Exception:
            df_aditivos = pd.DataFrame()

        try:
            recebimentos = pd.DataFrame(
                supabase.table("recebimentos_eventos").select("*").execute().data or []
            )
        except Exception:
            recebimentos = pd.DataFrame()

        # =====================================================
        # CAIXA REALIZADO — SOMENTE MOVIMENTAÇÕES DO FINANCEIRO
        # =====================================================
        entradas_realizadas = 0.0
        saidas_realizadas = 0.0

        if not df_fin.empty:
            if "valor" not in df_fin.columns:
                df_fin["valor"] = 0.0
            df_fin["valor"] = pd.to_numeric(df_fin["valor"], errors="coerce").fillna(0)
            if "tipo" not in df_fin.columns:
                df_fin["tipo"] = ""
            tipo_norm = df_fin["tipo"].fillna("").astype(str).str.lower()
            entradas_realizadas = float(df_fin.loc[tipo_norm == "entrada", "valor"].sum())
            saidas_realizadas = float(df_fin.loc[tipo_norm.isin(["saída", "saida"]), "valor"].sum())

        saldo_caixa = entradas_realizadas - saidas_realizadas

        # =====================================================
        # EVENTOS + ADENDOS
        # =====================================================
        if not df_eventos.empty:
            for col in [
                "venda", "custo", "cmv_status", "cmv_faturamento_total",
                "cmv_custo_total", "cmv_lucro_real", "cmv_percentual"
            ]:
                if col not in df_eventos.columns:
                    df_eventos[col] = None

            df_eventos["venda_base"] = pd.to_numeric(df_eventos["venda"], errors="coerce").fillna(0)
            df_eventos["custo_previsto"] = pd.to_numeric(df_eventos["custo"], errors="coerce").fillna(0)

            if not df_aditivos.empty and "evento_id" in df_aditivos.columns and "valor_cliente" in df_aditivos.columns:
                adit_ativos = df_aditivos.copy()
                if "status" in adit_ativos.columns:
                    adit_ativos = adit_ativos[
                        adit_ativos["status"].fillna("").astype(str).str.lower() != "cancelado"
                    ].copy()
                adit_ativos["valor_cliente"] = pd.to_numeric(
                    adit_ativos["valor_cliente"], errors="coerce"
                ).fillna(0)
                adit_agr = adit_ativos.groupby("evento_id", as_index=False)["valor_cliente"].sum()
                adit_agr.rename(columns={"valor_cliente": "aditivos_total"}, inplace=True)
                df_eventos = df_eventos.merge(
                    adit_agr, left_on="id", right_on="evento_id", how="left"
                )
                df_eventos["aditivos_total"] = pd.to_numeric(
                    df_eventos["aditivos_total"], errors="coerce"
                ).fillna(0)
            else:
                df_eventos["aditivos_total"] = 0.0

            df_eventos["faturamento_calculado"] = (
                df_eventos["venda_base"] + df_eventos["aditivos_total"]
            )
            df_eventos["cmv_fechado"] = (
                df_eventos["cmv_status"].fillna("aberto").astype(str).str.lower() == "fechado"
            )

            fat_snap = pd.to_numeric(df_eventos["cmv_faturamento_total"], errors="coerce")
            custo_snap = pd.to_numeric(df_eventos["cmv_custo_total"], errors="coerce")
            lucro_snap = pd.to_numeric(df_eventos["cmv_lucro_real"], errors="coerce")

            df_eventos["faturamento_real"] = df_eventos["faturamento_calculado"].astype(float)
            mask = df_eventos["cmv_fechado"] & fat_snap.notna()
            df_eventos.loc[mask, "faturamento_real"] = fat_snap[mask]

            df_eventos["custo_real"] = df_eventos["custo_previsto"].astype(float)
            mask = df_eventos["cmv_fechado"] & custo_snap.notna()
            df_eventos.loc[mask, "custo_real"] = custo_snap[mask]

            df_eventos["lucro_real"] = df_eventos["faturamento_real"] - df_eventos["custo_real"]
            mask = df_eventos["cmv_fechado"] & lucro_snap.notna()
            df_eventos.loc[mask, "lucro_real"] = lucro_snap[mask]

            df_fechados = df_eventos[df_eventos["cmv_fechado"]].copy()
        else:
            df_fechados = pd.DataFrame()

        if not df_fechados.empty:
            faturamento_real = float(df_fechados["faturamento_real"].sum())
            custo_real = float(df_fechados["custo_real"].sum())
            lucro_real = float(df_fechados["lucro_real"].sum())
            reserva_emergencia = float(
                df_fechados["lucro_real"].apply(lambda x: max(0.0, _fin_num(x)) * 0.35).sum()
            )
        else:
            faturamento_real = 0.0
            custo_real = 0.0
            lucro_real = 0.0
            reserva_emergencia = 0.0

        disponivel_economico = lucro_real - reserva_emergencia
        margem_real = (lucro_real / faturamento_real * 100) if faturamento_real > 0 else 0.0
        cmv_real = (custo_real / faturamento_real * 100) if faturamento_real > 0 else 0.0

        # =====================================================
        # CONTAS A RECEBER
        # =====================================================
        total_recebido_contratos = 0.0
        if not recebimentos.empty and "valor" in recebimentos.columns:
            recebimentos["valor"] = pd.to_numeric(recebimentos["valor"], errors="coerce").fillna(0)
            total_recebido_contratos = float(recebimentos["valor"].sum())

        total_aditivos_pagos = 0.0
        if not df_aditivos.empty and "valor_cliente" in df_aditivos.columns:
            adit_pago = df_aditivos.copy()
            adit_pago["valor_cliente"] = pd.to_numeric(adit_pago["valor_cliente"], errors="coerce").fillna(0)
            if "status" in adit_pago.columns:
                adit_pago = adit_pago[
                    adit_pago["status"].fillna("").astype(str).str.lower() == "pago"
                ]
            total_aditivos_pagos = float(adit_pago["valor_cliente"].sum()) if not adit_pago.empty else 0.0

        total_recebido = total_recebido_contratos + total_aditivos_pagos
        faturamento_contratado = float(df_eventos["faturamento_real"].sum()) if not df_eventos.empty else 0.0
        total_a_receber = max(0.0, faturamento_contratado - total_recebido)

        # =====================================================
        # PAINEL — CAIXA REALIZADO
        # =====================================================
        st.markdown("## 🏦 Caixa Realizado")
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Entradas Realizadas", _fin_moeda(entradas_realizadas))
            c2.metric("💸 Saídas Realizadas", _fin_moeda(saidas_realizadas))
            c3.metric(
                "🏦 Saldo de Caixa",
                _fin_moeda(saldo_caixa),
                help="Dinheiro que efetivamente entrou menos dinheiro que efetivamente saiu. Não é o mesmo que lucro."
            )

        st.markdown("## 📊 Resultado Econômico dos Eventos")
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Faturamento Real", _fin_moeda(faturamento_real))
            c2.metric("Custo Real", _fin_moeda(custo_real))
            c3.metric("Lucro Real", _fin_moeda(lucro_real))
            c4.metric("Margem Real", _fin_pct(margem_real))

        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("CMV Consolidado", _fin_pct(cmv_real))
            c2.metric("🛡️ Reserva Gerada — 35%", _fin_moeda(reserva_emergencia))
            c3.metric("💵 Disponível Econômico — 65%", _fin_moeda(disponivel_economico))

        st.markdown("## 📋 Contas a Receber")
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Faturamento Contratado", _fin_moeda(faturamento_contratado))
            c2.metric("Recebido", _fin_moeda(total_recebido))
            c3.metric("A Receber", _fin_moeda(total_a_receber))

        # =====================================================
        # RECONCILIAÇÃO — ADENDOS PAGOS QUE AINDA NÃO ESTÃO NO CAIXA
        # =====================================================
        adendos_sem_caixa = pd.DataFrame()

        if not df_aditivos.empty and "id" in df_aditivos.columns and "status" in df_aditivos.columns:
            pagos = df_aditivos[
                df_aditivos["status"].fillna("").astype(str).str.lower() == "pago"
            ].copy()

            ids_sincronizados = set()
            if not df_fin.empty and "origem" in df_fin.columns and "origem_id" in df_fin.columns:
                fin_adendos = df_fin[
                    df_fin["origem"].fillna("").astype(str).str.lower() == "adendo"
                ]
                ids_sincronizados = set(
                    pd.to_numeric(fin_adendos["origem_id"], errors="coerce")
                    .dropna().astype(int).tolist()
                )

            if not pagos.empty:
                adendos_sem_caixa = pagos[
                    ~pd.to_numeric(pagos["id"], errors="coerce")
                    .fillna(-1).astype(int).isin(ids_sincronizados)
                ].copy()

        if not adendos_sem_caixa.empty:
            valor_pendente_sync = float(
                pd.to_numeric(adendos_sem_caixa["valor_cliente"], errors="coerce").fillna(0).sum()
            )

            st.warning(
                f"⚠️ {len(adendos_sem_caixa)} adendo(s) marcado(s) como Pago ainda não possuem entrada rastreada no caixa. "
                f"Total: {_fin_moeda(valor_pendente_sync)}."
            )

            with st.expander("🔄 Reconciliar adendos pagos com o caixa", expanded=False):
                cols = [c for c in ["id", "evento_id", "evento", "tipo", "descricao", "valor_cliente", "forma_pagamento", "data_pagamento"] if c in adendos_sem_caixa.columns]
                st.dataframe(
                    adendos_sem_caixa[cols],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "valor_cliente": st.column_config.NumberColumn("Valor", format="R$ %.2f")
                    }
                )

                confirma = st.checkbox(
                    "Confirmo que estes adendos marcados como pagos representam valores realmente recebidos.",
                    key="fin_sync_adendos_confirma"
                )

                if st.button(
                    "🔄 Sincronizar entradas dos adendos",
                    type="primary",
                    use_container_width=True,
                    disabled=not confirma,
                    key="fin_sync_adendos_btn"
                ):
                    try:
                        criados = 0
                        for _, adt in adendos_sem_caixa.iterrows():
                            adendo_id = int(_fin_num(adt.get("id")))
                            valor = _fin_num(adt.get("valor_cliente"))
                            evento_id = int(_fin_num(adt.get("evento_id"))) if _fin_num(adt.get("evento_id")) > 0 else None
                            data_ref = adt.get("data_pagamento") or datetime.now().isoformat()
                            try:
                                data_mov = pd.to_datetime(data_ref).date().isoformat()
                            except Exception:
                                data_mov = datetime.now().date().isoformat()

                            payload = {
                                "data": data_mov,
                                "tipo": "Entrada",
                                "categoria": "Adendo / Receita Extra",
                                "forma_pagamento": _fin_txt(adt.get("forma_pagamento")) or "Não informado",
                                "descricao": f"Adendo - {_fin_txt(adt.get('tipo')) or 'Receita extra'} - {_fin_txt(adt.get('evento')) or 'Evento'}",
                                "valor": float(valor),
                                "evento_id": evento_id,
                                "origem": "adendo",
                                "origem_id": adendo_id,
                            }

                            supabase.table("Financeiro").insert(payload).execute()
                            criados += 1

                        st.success(f"✅ {criados} entrada(s) de adendo sincronizada(s) com o caixa.")
                        st.rerun()
                    except Exception as erro:
                        st.error(f"Erro ao sincronizar adendos: {erro}")

        # =====================================================
        # GRÁFICO DO CAIXA
        # =====================================================
        if not df_fin.empty and "data_dt" in df_fin.columns:
            graf = df_fin.dropna(subset=["data_dt"]).copy()
            if not graf.empty:
                graf["fluxo"] = graf.apply(
                    lambda x: x["valor"] if str(x.get("tipo", "")).lower() == "entrada" else -x["valor"],
                    axis=1
                )
                graf = graf.sort_values("data_dt")
                graf["saldo_acumulado"] = graf["fluxo"].cumsum()
                st.markdown("### 📈 Evolução do Caixa")
                st.line_chart(graf.set_index("data_dt")["saldo_acumulado"])

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

                cmv_fechado = (
                    str(evento.get("cmv_status", "") or "").lower() == "fechado"
                )

                valor_contratado_total = (
                    _fin_num(evento.get("cmv_faturamento_total"))
                    if cmv_fechado and evento.get("cmv_faturamento_total") is not None
                    else valor_contrato_base + total_aditivos_cliente
                )

                custo_evento_total = (
                    _fin_num(evento.get("cmv_custo_total"))
                    if cmv_fechado and evento.get("cmv_custo_total") is not None
                    else _fin_num(evento.get("custo"))
                )

                lucro_evento = (
                    _fin_num(evento.get("cmv_lucro_real"))
                    if cmv_fechado and evento.get("cmv_lucro_real") is not None
                    else valor_contratado_total - custo_evento_total
                )

                reserva_caixa_35 = (
                    max(0.0, lucro_evento) * 0.35
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
                        "Custo Real" if cmv_fechado else "Custo Previsto",
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

                cmv_fechado = (
                    str(evento.get("cmv_status", "") or "").lower() == "fechado"
                )

                valor_contratado_total = (
                    _fin_num(evento.get("cmv_faturamento_total"))
                    if cmv_fechado and evento.get("cmv_faturamento_total") is not None
                    else valor_contrato_base + total_aditivos_cliente
                )

                custo_evento_total = (
                    _fin_num(evento.get("cmv_custo_total"))
                    if cmv_fechado and evento.get("cmv_custo_total") is not None
                    else _fin_num(evento.get("custo"))
                )

                lucro_evento = (
                    _fin_num(evento.get("cmv_lucro_real"))
                    if cmv_fechado and evento.get("cmv_lucro_real") is not None
                    else valor_contratado_total - custo_evento_total
                )

                reserva_caixa_35 = (
                    max(0.0, lucro_evento) * 0.35
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
