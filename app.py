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

def carregar_tabela(nome):
    try:
        response = supabase.table(nome).select("*").execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        
        return pd.DataFrame()

    except Exception as e:
        st.error(f"Erro ao carregar {nome}: {e}")
        return pd.DataFrame()

st.set_page_config(page_title="Ellosystem", layout="wide")

def calcular_custo_drink(drink, df_receitas, df_bebidas, df_insumos):

    receita = df_receitas[df_receitas["drink"] == drink]

    custo = 0

    for _, row in receita.iterrows():

        ingrediente = normalizar_nome(row["ingrediente"])
        quantidade = float(row["quantidade"])

        # procura bebida
        bebida = df_bebidas[
            df_bebidas["nome"].str.lower().str.strip() == ingrediente.lower()
        ]

        if not bebida.empty:

            preco = float(bebida.iloc[0]["preco"])
            volume = float(bebida.iloc[0]["quantidade"])

            if volume > 0:
                custo += (quantidade / volume) * preco

            continue

        # procura insumo
        insumo = df_insumos[
            df_insumos["nome"].str.lower().str.strip() == ingrediente.lower()
        ]

        if not insumo.empty:

            preco = float(insumo.iloc[0]["preco"])

            custo += (quantidade / 1000) * preco

    return round(custo,2)

def ingredientes_do_drink(drink, df_receitas):

    receita = df_receitas[df_receitas["drink"] == drink]

    ingredientes = []

    for _, row in receita.iterrows():

        ingredientes.append(
            normalizar_nome(row["ingrediente"])
        )

    return ingredientes

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

def calcular_custo_ingrediente(ingrediente, quantidade, unidade):

    ingrediente = str(ingrediente).strip().lower()

    item = df_bebidas_global[
        df_bebidas_global["nome"].astype(str).str.strip().str.lower() == ingrediente
    ]

    if item.empty:
        item = df_insumos_global[
            df_insumos_global["nome"].astype(str).str.strip().str.lower() == ingrediente
        ]

    if item.empty:
        return 0

    return float(item.iloc[0]["custo"])

def tela_servico_personalizado():

    st.subheader("👷 Serviço Personalizado")

    st.info(
        "Orçamento para eventos onde o cliente fornece as bebidas."
    )

# Carrega uma única vez
df_bebidas_global = carregar_tabela("precos_bebidas")
df_insumos_global = carregar_tabela("precos_insumos")

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
"CMV",    
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
        
                    supabase.table(nome_tabela).insert({
                        "tipo": tipo,
                        "nome": normalizar_nome(nome),
                        "quantidade": quantidade,
                        "preco": preco,
                        "uso": uso,
                        "rendimento": rendimento,
                        "custo": custo
                    }).execute()
                    st.success("Item cadastrado!")

    # =========================
    # LISTA / EDIÇÃO
    # =========================
    with tab2:

        dados = supabase.table(nome_tabela).select("*").execute()
        df = pd.DataFrame(dados.data if dados.data else [])

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
                            # 🔥 DIFERENCIA AUTOMATICAMENTE
                            if nome_tabela == "precos_insumos":
                                quantidade_real = quantidade * 1000  # fruta (kg → g)
                            else:
                                quantidade_real = quantidade  # artesanal (ml direto)
            
                            rendimento = quantidade_real / uso
                            custo = preco / rendimento
            
                        # 🔥 ISSO ESTAVA COM INDENTAÇÃO ERRADA
                        supabase.table(nome_tabela).update({
                            "tipo": row["tipo"],
                            "nome": row["nome"],
                            "quantidade": quantidade,
                            "preco": preco,
                            "uso": uso,
                            "rendimento": rendimento,
                            "custo": custo
                        }).eq("id", row["id"]).execute()
            
                    st.success("Alterações salvas!")
            
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

            # =========================
            # EXCLUIR ITEM
            # =========================
            item = st.selectbox("Excluir item", df["id"], key=f"del_{nome_tabela}")

            if st.button("🗑 Excluir selecionado", key=f"btn_{nome_tabela}"):

                supabase.table(nome_tabela).delete().eq("id", item).execute()
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
            
                    try:
                        supabase.table("precos_insumos").insert({
                            "tipo": "fruta",
                            "nome": normalizar_nome(nome),
                            "quantidade": quantidade,
                            "preco": preco,
                            "uso": uso,
                            "rendimento": rendimento,
                            "custo": custo
                        }).execute()
                    
                        st.success("Fruta cadastrada corretamente!")
                    
                    except Exception as e:
                        st.error(f"Erro real: {e}")
                        print(e)
    # -------------------------
    # LISTA / EDIÇÃO
    # -------------------------
    with tab2:

        dados = supabase.table("precos_insumos").select("*").execute()
        df = pd.DataFrame(dados.data)

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
                    supabase.table("precos_insumos").update({
                    "tipo": row["tipo"],
                    "nome": row["nome"],
                    "quantidade": row["quantidade"],
                    "preco": row["preco"],
                    "uso": row["uso"],
                    "rendimento": row["rendimento"],
                    "custo": row["custo"]
                }).eq("id", row["id"]).execute()
            
                st.success("Alterações salvas!")
            
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

        # 🗑 EXCLUIR
        if not df.empty:
            item = st.selectbox("Excluir item", df["id"])

            if st.button("🗑 Excluir"):
                supabase.table("precos_insumos").delete().eq("id", item).execute()
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
        
elif menu == "Receitas":

    st.title("Receitas")

    # Controle de estado
    if "ingredientes_temp" not in st.session_state:
        st.session_state["ingredientes_temp"] = []

    if "drink_nome" not in st.session_state:
        st.session_state["drink_nome"] = ""

    if "msg" not in st.session_state:
        st.session_state["msg"] = ""

    if st.session_state["msg"]:
        st.success(st.session_state["msg"])
        st.session_state["msg"] = ""

    aba_cadastro, aba_lista = st.tabs(
        ["Cadastro de Drinks", "Lista de Drinks"]
    )

    # ==================================================
    # CADASTRO
    # ==================================================
    with aba_cadastro:

        drink = st.text_input(
            "Nome do drink",
            value=st.session_state.get("drink_nome", "")
        )

        col1, col2, col3, col4 = st.columns(4)

        ingrediente = normalizar_nome(
            col1.text_input(
                "Ingrediente",
                key="novo_ingrediente"
            )
        )

        quantidade = col2.number_input(
            "Quantidade",
            min_value=0.0,
            key="nova_quantidade"
        )

        unidade = col3.selectbox(
            "Unidade",
            ["ml", "g", "un", "gota", "fatia", "guarnição"],
            key="nova_unidade"
        )

        if col4.button("➕ Adicionar"):

            if drink and ingrediente and quantidade > 0:

                st.session_state["drink_nome"] = drink

                st.session_state["ingredientes_temp"].append({

                    "ingrediente": ingrediente,
                    "quantidade": quantidade,
                    "unidade": unidade

                })

                st.success("Ingrediente adicionado!")

            else:

                st.warning("Preencha todos os campos.")

        if st.session_state["ingredientes_temp"]:

            st.subheader("Ingredientes")

            tabela = pd.DataFrame(
                st.session_state["ingredientes_temp"]
            )

            st.dataframe(
                tabela,
                use_container_width=True
            )

        col1, col2 = st.columns(2)

        with col1:

            if st.button("💾 Salvar Drink"):

                if not st.session_state["drink_nome"]:

                    st.error("Informe o nome do drink.")

                elif not st.session_state["ingredientes_temp"]:

                    st.error("Adicione ingredientes.")

                else:

                    supabase.table("receitas")\
                        .delete()\
                        .eq(
                            "drink",
                            st.session_state["drink_nome"]
                        )\
                        .execute()

                    for item in st.session_state["ingredientes_temp"]:

                        supabase.table("receitas").insert({

                            "drink": st.session_state["drink_nome"],
                            "ingrediente": item["ingrediente"],
                            "quantidade": item["quantidade"],
                            "unidade": item["unidade"]

                        }).execute()

                    st.success("Receita salva com sucesso!")

                    st.session_state["ingredientes_temp"] = []
                    st.session_state["drink_nome"] = ""

                    st.rerun()

        with col2:

            if st.button("❌ Cancelar edição"):

                st.session_state["ingredientes_temp"] = []
                st.session_state["drink_nome"] = ""

                st.rerun()

    # ==================================================
    # LISTA
    # ==================================================
    with aba_lista:

        df = carregar_tabela("receitas")
        bebidas = carregar_tabela("precos_bebidas")
        insumos = carregar_tabela("precos_insumos")

        if df.empty:

            st.info("Nenhum drink cadastrado")

        else:

            drinks = sorted(df["drink"].dropna().unique())

            for drink in drinks:

                receita = df[df["drink"] == drink]

                custo_total = 0

                col1, col2, col3, col4 = st.columns([6, 2, 1, 1])

                with col1:

                    st.markdown(f"### 🍸 {drink}")

                    for _, row in receita.iterrows():

                        ingrediente = str(row["ingrediente"])
                        quantidade = float(row["quantidade"])
                        unidade = row["unidade"]

                        st.write(f"• {ingrediente} - {quantidade} {unidade}")

                        custo = calcular_custo_ingrediente(
                            ingrediente,
                            quantidade,
                            unidade
                        )

                        custo_total += custo

                with col2:

                    st.metric(
                        "Custo",
                        f"R$ {custo_total:.2f}"
                    )

                with col3:

                    if st.button(
                        "✏️",
                        key=f"editar_{drink}"
                    ):
                
                        st.session_state["editar_receita"] = drink
                
                        st.rerun()

                with col4:

                    if st.button(
                        "🗑️",
                        key=f"excluir_{drink}"
                    ):

                        supabase.table("receitas")\
                            .delete()\
                            .eq("drink", drink)\
                            .execute()

                        st.success("Drink excluído com sucesso!")

                        st.rerun()

                st.divider()
    # ==========================================
    # EDIÇÃO DA RECEITA
    # ==========================================
    if "editar_receita" in st.session_state:
    
        st.markdown("---")
        st.subheader(f"✏️ Editando: {st.session_state['editar_receita']}")
    
        receita = (
            df[df["drink"] == st.session_state["editar_receita"]]
            [["ingrediente","quantidade","unidade"]]
            .reset_index(drop=True)
        )
    
        editado = st.data_editor(
    
            receita,
    
            use_container_width=True,
    
            num_rows="dynamic",
    
            hide_index=True,
    
            key="editor_receita"
    
        )
    
        col1, col2 = st.columns(2)
    
        with col1:
    
            if st.button("💾 Salvar alterações"):
    
                supabase.table("receitas")\
                    .delete()\
                    .eq(
                        "drink",
                        st.session_state["editar_receita"]
                    )\
                    .execute()
    
                for _, linha in editado.iterrows():
    
                    if str(linha["ingrediente"]).strip() == "":
                        continue
    
                    supabase.table("receitas").insert({
    
                        "drink": st.session_state["editar_receita"],
    
                        "ingrediente": linha["ingrediente"],
    
                        "quantidade": float(linha["quantidade"]),
    
                        "unidade": linha["unidade"]
    
                    }).execute()
    
                st.success("Receita atualizada!")
    
                del st.session_state["editar_receita"]
    
                st.rerun()
    
        with col2:
    
            if st.button("Cancelar"):
    
                del st.session_state["editar_receita"]
    
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

        st.divider()
        st.divider()

        tab_bar, tab_mao_obra = st.tabs([
            "🍸 Bar Completo",
            "👷 Serviço Personalizado"
        ])
        
        with tab_bar:
            
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
    
            config_hash = f"{num_convidados}_{horas}_{drinks_por_hora}_{modo_calculo}"
    
            if "ultima_config" not in st.session_state:
                st.session_state["ultima_config"] = config_hash
            
            # Se mudou qualquer coisa → limpa quantidades
            if st.session_state["ultima_config"] != config_hash:
                for key in list(st.session_state.keys()):
                    if key.startswith("qtd_") or key.startswith("qtd_fruta_"):
                        del st.session_state[key]
            
                st.session_state["ultima_config"] = config_hash
    
            if modo_calculo == "Evento inteiro":
                total_drinks = num_convidados * drinks_por_hora
            else:
                total_drinks = num_convidados * horas * drinks_por_hora
                
            st.info(f"Total estimado de drinks: {int(total_drinks)}")
    
            # =========================
            # RECEITAS
            # =========================
            dados = supabase.table("receitas").select("*").execute()
            df_receitas = pd.DataFrame(dados.data if dados.data else [])
            
            if df_receitas.empty:
                st.warning("Cadastre receitas primeiro")
            
            else:
            
                st.markdown("### 🍹 Seleção de Drinks")
            
                drinks = df_receitas["drink"].unique()
            
                selecao = st.multiselect(
                    "Escolha os drinks do evento",
                    drinks
                )
            
                if selecao:
    
                    # =========================
                    # 📊 DISTRIBUIÇÃO MÉDIA (NOVO)
                    # =========================
                    st.divider()
                
                    st.markdown("### 📊 Distribuição estimada de consumo")
                    st.caption("Baseado no total de drinks do evento")
                
                    qtd_drinks_total = int(total_drinks)
                    qtd_tipos = len(selecao)
                
                    if qtd_tipos > 0:
                        media_por_drink = round(qtd_drinks_total / qtd_tipos)
                
                        st.info(
                            f"Total de {qtd_drinks_total} drinks → média de {media_por_drink} por tipo"
                        )
                
                        for drink in selecao:
                            st.write(f"• {drink}: ~{media_por_drink} drinks")
                    
                    st.divider()
            
                    # =========================
                    # PESO DOS DRINKS (NOVO VISUAL)
                    # =========================
                    st.markdown("### ⚖️ Volume de saída dos drinks")
                    st.caption("Defina quais drinks terão maior saída (peso relativo)")
                    st.caption("Ex: peso 2 = esse drink sai o dobro dos outros")
            
                    pesos = {}
                    total_peso = 0
            
                    colunas = st.columns(2)  # 🔥 muda pra 3 se quiser mais compacto
            
                    for i, drink in enumerate(selecao):
                        col = colunas[i % 2]
            
                        with col:
                            peso = st.number_input(
                                f"{drink}",
                                min_value=1,
                                value=1,
                                key=f"peso_{drink}"
                            )
            
                        pesos[drink] = peso
                        total_peso += peso
            
                    st.divider()
    
                    # =========================
                    # 📈 DISTRIBUIÇÃO REAL (NOVO)
                    # =========================
                    st.markdown("### 📈 Distribuição real (baseada nos pesos)")
                    
                    for drink in selecao:
                        proporcao = pesos[drink] / total_peso if total_peso > 0 else 0
                        qtd_real = int(total_drinks * proporcao)
                    
                        st.write(f"• {drink}: ~{qtd_real} drinks")
                    
                    st.divider()
                    
                    # =========================
                    # CÁLCULO DOS INGREDIENTES
                    # =========================
                    ingredientes_totais = {}
                    
                    for drink in selecao:
                    
                        proporcao = pesos[drink] / total_peso if total_peso > 0 else 0
                        qtd_drinks = total_drinks * proporcao
                    
                        receita = df_receitas[df_receitas["drink"] == drink]
                    
                        for _, row in receita.iterrows():
                    
                            # 🔥 ESSENCIAL (estava faltando)
                            ingrediente = normalizar_nome(row["ingrediente"])
                            qtd = row["quantidade"]
                    
                            # =========================
                            # RENDIMENTO REAL DAS FRUTAS
                            # =========================
                            rendimento = 1
                            nome = ingrediente.lower()
                    
                            if "limao" in nome or "limão" in nome:
                                rendimento = 0.6
                            elif "laranja" in nome:
                                rendimento = 0.7
                            elif "abacaxi" in nome:
                                rendimento = 0.5
                            elif "maracuja" in nome or "maracujá" in nome:
                                rendimento = 0.4
                            elif "morango" in nome:
                                rendimento = 0.8
                    
                            base = (qtd * qtd_drinks) / rendimento
                    
                            # =========================
                            # GARNISH (DECORAÇÃO)
                            # =========================
                            if any(p in nome for p in [
                                "limao", "limão", "laranja", "morango", "abacaxi", "kiwi", "maracuja", "maracujá"
                            ]):
                                garnish = 3 * qtd_drinks
                            else:
                                garnish = 0
                    
                            total_ingrediente = base + garnish
                    
                            if ingrediente in ingredientes_totais:
                                ingredientes_totais[ingrediente] += total_ingrediente
                            else:
                                ingredientes_totais[ingrediente] = total_ingrediente
                
    
                    # =========================
                    # DADOS
                    # =========================
                    df_bebidas = pd.DataFrame(
                        supabase.table("precos_bebidas").select("*").execute().data or []
                    )
                    
                    df_insumos = pd.DataFrame(
                        supabase.table("precos_insumos").select("*").execute().data or []
                    )
                    
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
                    # SEPARAÇÃO INSUMOS (FRUTAS vs ARTESANAIS)
                    # =========================
                    ingredientes_frutas = {}
                    ingredientes_artesanais = {}
                    
                    for item, qtd in ingredientes_insumos.items():
                    
                        nome = item.lower()
                    
                        # 🔥 REGRA SIMPLES E FUNCIONAL
                        if any(p in nome for p in [
                            "charope", "xarope", "espuma", "suco"
                        ]):
                            ingredientes_artesanais[item] = qtd
                        else:
                            ingredientes_frutas[item] = qtd
    
                    
                    # =========================
                    # BEBIDAS
                    # =========================
                    st.subheader("🍸 Bebidas")
                    
                    # 🔥 limpa estado (resolve bug de marcas duplicadas)
                    st.session_state["orcamento_bebidas"] = {}
                    
                    custo_bebidas = 0
                    escolhas_marcas = {}
                    
                    # =========================
                    # ESCOLHA DAS MARCAS
                    # =========================
                    st.markdown("### 🏷️ Escolha das marcas")
                    
                    for item, dados in ingredientes_bebidas.items():
                        tipo = dados["tipo"]
                    
                        opcoes = df_bebidas[df_bebidas["tipo"].str.lower() == tipo.lower()]
                    
                        if opcoes.empty:
                            opcoes = df_bebidas
                    
                        escolha = st.selectbox(
                            f"{item}",
                            opcoes["nome"],
                            key=f"marca_{item}"
                        )
                    
                        escolhas_marcas[item] = escolha
                    
                    st.divider()
                    
                    # =========================
                    # AJUSTE FINO (NOVO VISUAL)
                    # =========================
                    st.markdown("### ⚙️ Ajuste fino das quantidades")
                    st.caption("Aqui você pode corrigir manualmente as quantidades calculadas")
                    
                    for item, dados in ingredientes_bebidas.items():
                    
                        marca = escolhas_marcas[item]
                    
                        result = df_bebidas[df_bebidas["nome"] == marca]
                    
                        if not result.empty:
                    
                            preco = result.iloc[0]["preco"]
                            volume = result.iloc[0]["quantidade"]
                    
                            qtd_ml = dados["qtd"]
                    
                            qtd_real = qtd_ml / volume if volume > 0 else 0
                            qtd_garrafas = int(qtd_real) + (1 if qtd_real % 1 > 0 else 0)
                    
                            key_qtd = f"qtd_{item}_{marca}"
                    
                            if key_qtd not in st.session_state:
                                st.session_state[key_qtd] = int(qtd_garrafas)
                    
                            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                            with col1:
                                st.markdown(f"**{marca}**")
                                st.caption(f"Base: {item}")
                    
                            with col2:
                                qtd_editavel = st.number_input(
                                    "Garrafas",
                                    min_value=0,
                                    key=key_qtd
                                )
                    
                            with col3:
                                st.write(f"R$ {preco:,.2f}")
                                st.caption("Preço unit.")
                    
                            with col4:
                                total = qtd_editavel * preco
                                st.write(f"**R$ {total:,.2f}**")
                                st.caption("Total")
                    
                            # salva no estado
                            st.session_state["orcamento_bebidas"][marca] = {
                                "quantidade": qtd_editavel,
                                "preco": preco
                            }
                    
                            custo_bebidas += total
                    
                    st.divider()
                    
                    st.markdown(f"### 💰 Subtotal Bebidas: R$ {custo_bebidas:,.2f}")
                    
                    # =========================
                    # RESUMO
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
                    
                    for fruta, qtd_gramas in ingredientes_frutas.items():
                    
                        encontrado = df_insumos[
                            df_insumos["nome"].str.lower().str.strip() == fruta.lower()
                        ]
                        
                        # 🔥 fallback por tipo (igual bebidas)
                        if encontrado.empty:
                            encontrado = df_insumos[
                                df_insumos["tipo"].str.lower().str.contains(fruta.lower())
                            ]
                    
                        if not encontrado.empty:
                    
                            preco_kg = encontrado.iloc[0]["preco"]
                            custo_por_grama = preco_kg / 1000
                    
                            col1, col2, col3 = st.columns([4, 2, 2])
                    
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
                    # ARTESANAIS
                    # =========================
                    st.subheader("🧪 Produção Artesanal")
                    st.caption("Itens produzidos manualmente (xaropes, espumas, bases, etc.)")
                    
                    if "orcamento_artesanais" not in st.session_state:
                        st.session_state["orcamento_artesanais"] = {}
                    
                    custo_artesanais = 0
                    
                    for item, qtd_ml in ingredientes_artesanais.items():
                    
                        encontrado = df_insumos[
                            df_insumos["nome"].str.lower().str.contains(item.lower())
                        ]
                    
                        # 🔥 fallback caso não encontre no banco
                        if not encontrado.empty:
                            preco = encontrado.iloc[0]["preco"]
                        else:
                            preco = 0  # ou coloca um valor padrão se quiser
                    
                        col1, col2, col3 = st.columns([4, 2, 2])
                    
                        with col1:
                            st.write(f"✔ {item}")
                    
                        with col2:
                            key_qtd = f"qtd_art_{item}"
                    
                            if key_qtd not in st.session_state:
                                st.session_state[key_qtd] = float(qtd_ml)
                    
                            qtd_editavel = st.number_input(
                                "ML",
                                min_value=0.0,
                                key=key_qtd
                            )
                    
                        with col3:
                            custo_item = qtd_editavel * preco
                            st.write(f"💰 R$ {custo_item:,.2f}")
                    
                        st.session_state["orcamento_artesanais"][item] = {
                            "quantidade": qtd_editavel,
                            "preco": preco
                        }
                    
                        custo_artesanais += custo_item
                    
                    st.markdown(f"### 💰 Subtotal Artesanais: R$ {custo_artesanais:,.2f}")
                    
                    # =========================
                    # 📋 RESUMO
                    # =========================
                    st.markdown("### 📋 Resumo Produção Artesanal")
    
                    for item, dados in st.session_state["orcamento_artesanais"].items():
                    
                        qtd = dados["quantidade"]
                        preco = dados["preco"]  # 🔥 CORRIGIDO AQUI
                    
                        total = qtd * preco
                    
                        st.write(f"✔ {item} → {qtd:.0f} ml | 💰 R$ {total:,.2f}")
                    
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
    
                    st.metric(
                        "💸 Total dos Custos Extras",
                        f"R$ {custo_extras:,.2f}"
                    )
                    
                    st.divider()
                                        
                    # =========================
                    # 📦 SERVIÇOS ADICIONAIS
                    # =========================
                    
                    st.subheader("📦 Serviços Adicionais")
                    
                    pacotes = supabase.table("pacotes")\
                        .select("*")\
                        .eq("ativo", True)\
                        .execute().data
                    
                    total_pacotes = 0
                    
                    # ------------------------------------------------------------
                    # IMPORTANTE: zera os acumuladores no início do bloco.
                    # Antes, "custo_servicos" e "orcamento_bebidas" só eram criados
                    # se não existissem (if "x" not in session_state), e depois
                    # só recebiam "+=". Como o Streamlit reroda o script inteiro a
                    # cada interação (marcar checkbox, mudar %, etc.), o valor
                    # ficava sendo somado em cima do valor antigo indefinidamente,
                    # inflando o total a cada clique.
                    # ------------------------------------------------------------
                    st.session_state["orcamento_bebidas"] = {}
                    st.session_state["custo_servicos"] = 0
                    
                    if pacotes:
                    
                        for pacote in pacotes:
                    
                            usar = st.checkbox(
                                pacote["nome"],
                                key=f'pacote_{pacote["id"]}'
                            )
                    
                            if not usar:
                                continue
                    
                            dados = pacote["dados"] or {}
                    
                            percentual = st.number_input(
                                "Percentual de consumo (%)",
                                value=float(dados.get("percentual_consumo", 30)),
                                key=f'perc_{pacote["id"]}'
                            )
                    
                            doses = st.number_input(
                                "Doses por pessoa",
                                value=float(dados.get("doses_pessoa", 4)),
                                key=f'dose_{pacote["id"]}'
                            )
                    
                            ml_dose = st.number_input(
                                "ML por dose",
                                value=float(dados.get("ml_dose", 50)),
                                key=f'ml_{pacote["id"]}'
                            )
                    
                            markup = st.number_input(
                                "Markup",
                                value=float(dados.get("markup", 3)),
                                key=f'markup_{pacote["id"]}'
                            )
                    
                            pessoas = num_convidados * percentual / 100
                    
                            doses_total = pessoas * doses
                    
                            ml_total = doses_total * ml_dose
                    
                            st.info(f"Consumo previsto: {ml_total:.0f} ml")
                    
                            produtos = supabase.table("pacote_produtos")\
                                .select("*")\
                                .eq("pacote_id", pacote["id"])\
                                .execute().data
                    
                            custo_pacote = 0
                    
                            st.markdown("### Marcas")
                    
                            if not produtos:
                                st.caption("Nenhuma marca vinculada a este serviço ainda.")
                    
                            for produto in produtos:
                    
                                # -----------------------------------------------------
                                # Busca sem .single(): se o produto do estoque foi
                                # excluído mas ainda existe um vínculo órfão em
                                # "pacote_produtos", .single() lança erro e derruba
                                # a página inteira. Aqui a gente simplesmente ignora
                                # o vínculo órfão e segue em frente.
                                # -----------------------------------------------------
                                resultado_estoque = supabase.table("estoque")\
                                    .select("*")\
                                    .eq("id", produto["estoque_id"])\
                                    .execute().data
                    
                                if not resultado_estoque:
                                    st.warning(
                                        f"Produto de estoque (id {produto['estoque_id']}) "
                                        "não foi encontrado — pode ter sido excluído. Pulando."
                                    )
                                    continue
                    
                                estoque = resultado_estoque[0]
                    
                                col1, col2 = st.columns([3, 1])
                    
                                with col1:
                    
                                    usar_produto = st.checkbox(
                                        estoque["marca"],
                                        value=True,
                                        key=f'usar_{produto["id"]}'
                                    )
                    
                                with col2:
                    
                                    estoque["participacao"] = st.number_input(
                                        "%",
                                        min_value=0.0,
                                        max_value=100.0,
                                        value=float(produto["participacao"]),
                                        key=f'perc_prod_{produto["id"]}'
                                    )
                    
                                if not usar_produto:
                                    continue
                    
                                participacao = estoque["participacao"]
                    
                                ml_produto = ml_total * participacao / 100
                    
                                # -----------------------------------------------------
                                # Proteção contra "tamanho" vazio, None ou não numérico.
                                # Isso evita o NameError/erro que estava travando a tela
                                # ao marcar uma marca. Se o valor não puder ser
                                # convertido, avisamos e pulamos esse produto em vez de
                                # quebrar a página inteira.
                                # -----------------------------------------------------
                                try:
                                    tamanho = float(estoque["tamanho"])
                                    if tamanho <= 0:
                                        raise ValueError("tamanho deve ser maior que zero")
                                except (TypeError, ValueError):
                                    st.error(
                                        f"O campo 'tamanho' do produto **{estoque['marca']}** "
                                        f"está inválido (valor atual: {estoque.get('tamanho')!r}). "
                                        "Corrija esse campo na tela de Estoque para incluir esse "
                                        "item no cálculo."
                                    )
                                    continue
                    
                                garrafas = math.ceil(ml_produto / tamanho)
                    
                                preco = estoque.get("preco") or 0
                    
                                custo = garrafas * preco
                    
                                custo_pacote += custo
                    
                                st.session_state["orcamento_bebidas"][estoque["marca"]] = {
                                    "quantidade": garrafas,
                                    "preco": preco
                                }
                    
                                st.write(
                                    f'🍾 {estoque["marca"]} - {garrafas} garrafas'
                                )
                    
                            venda = custo_pacote * markup
                    
                            total_pacotes += venda
                    
                            st.session_state["custo_servicos"] += custo_pacote
                    
                            st.success(
                                f"Custo: R$ {custo_pacote:,.2f} | Venda: R$ {venda:,.2f}"
                            )
                    
                    else:
                    
                        st.info("Nenhum serviço cadastrado.")
                    
                    st.markdown(f"## 💰 Total Serviços: R$ {total_pacotes:,.2f}")
                    
                    st.divider()
                    
                    st.metric(
                        "Total Serviços Adicionais",
                        f"R$ {total_pacotes:,.2f}"
                    )
                    
                   # =========================
                    # TOTAL
                    # =========================
                    custo_total = custo_bebidas + custo_frutas + custo_artesanais + custo_extras + st.session_state.get("custo_servicos",0)
                    
                    st.divider()
                    
                    st.metric("💰 Custo Total do Evento (Bruto)", f"R$ {custo_total:,.2f}")
                    
                    # =========================
                    # MARGEM
                    # =========================
                    st.subheader("📈 Precificação")
                    
                    margem = st.slider(
                        "Margem de lucro (%)",
                        0,
                        300,
                        100
                    )
                    
                    preco_venda = custo_total * (1 + margem / 100)
                    
                    # =========================
                    # DESCONTO
                    # =========================
                    desconto = st.slider(
                        "Desconto (%)",
                        0,
                        100,
                        0
                    )
                    
                    preco_com_desconto = preco_venda * (1 - desconto / 100)
                    
                    valor_desconto = preco_venda - preco_com_desconto
                    
                    # =========================
                    # COMISSÃO
                    # =========================
                    st.subheader("🤝 Comissão")
                    
                    incluir_comissao = st.checkbox(
                        "Incluir comissão nesta venda",
                        value=False
                    )
                    
                    valor_comissao = 0
                    percentual_comissao = 0
                    
                    if incluir_comissao:
                    
                        percentual_comissao = st.number_input(
                            "Percentual da comissão (%)",
                            min_value=0.0,
                            max_value=100.0,
                            value=10.0,
                            step=0.5
                        )
                    
                        valor_comissao = (
                            preco_com_desconto *
                            (percentual_comissao / 100)
                        )
                    
                    valor_final_venda = (
                        preco_com_desconto +
                        valor_comissao
                    )
                    
                    # =========================
                    # LUCRO
                    # =========================
                    lucro = valor_final_venda - custo_total
                    
                    # =========================
                    # INDICADORES
                    # =========================
                    valor_por_convidado = (
                        valor_final_venda / num_convidados
                        if num_convidados > 0 else 0
                    )
                    
                    valor_por_hora = (
                        valor_final_venda / horas
                        if horas > 0 else 0
                    )
                    
                    margem_real = (
                        (lucro / valor_final_venda) * 100
                        if valor_final_venda > 0 else 0
                    )
                    
                    # =========================
                    # RESUMO FINANCEIRO
                    # =========================
                    st.divider()
                    
                    st.subheader("📊 Resumo Financeiro")
    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "💰 Custo",
                            f"R$ {custo_total:,.2f}"
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
                    
                    st.divider()
                    
                    st.metric(
                        "🏆 VALOR FINAL DO ORÇAMENTO",
                        f"R$ {valor_final_venda:,.2f}"
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "🔻 Desconto",
                            f"R$ {valor_desconto:,.2f}",
                            f"{desconto}%"
                        )
                    
                    with col2:
                        st.metric(
                            "👤 Valor por convidado",
                            f"R$ {valor_por_convidado:,.2f}"
                        )
                    
                    with col3:
                        st.metric(
                            "⏱️ Valor por hora",
                            f"R$ {valor_por_hora:,.2f}"
                        )
                    
                    if lucro < 0:
                        st.error(
                            f"⚠️ Prejuízo estimado: R$ {lucro:,.2f}"
                        )
                    else:
                        st.success(
                            f"✅ Lucro estimado: R$ {lucro:,.2f}"
                        )
                    
                    if margem_real >= 35:
                        st.info(f"📈 Margem de lucro: **{margem_real:.1f}%** | 🟢 Excelente")
                    
                    elif margem_real >= 25:
                        st.info(f"📈 Margem de lucro: **{margem_real:.1f}%** | ✅ Saudável")
                    
                    elif margem_real >= 15:
                        st.info(f"📈 Margem de lucro: **{margem_real:.1f}%** | 🟡 Atenção")
                    
                    else:
                        st.info(f"📈 Margem de lucro: **{margem_real:.1f}%** | 🔴 Muito baixa")
                    
                    # =========================
                    # 💾 SALVAR ORÇAMENTO (RESTAURADO)
                    # =========================
                    if st.button("💾 Salvar orçamento", key="salvar_bar_completo"):
                        
                        # 🎯 A CRIAÇÃO DO TEXTO TEM QUE FICAR AQUI DENTRO!
                        texto_drinks = "\n".join(selecao) if selecao else ""
                        
                        response = supabase.table("eventos").insert({
                            "cliente": nome_cliente,
                            "data": str(data_evento),
                            "cidade": cidade_evento,
                            "telefone": telefone,
                            "endereco": endereco,
                            "tipo_evento": tipo_evento,
                            "modalidade": "Bar Completo",
                            "hora_chegada": str(hora_chegada),
                            "hora_inicio": str(hora_inicio),
                            "hora_convidados": str(hora_convidados),
                            "convidados": num_convidados,
                            "custo": custo_total,
                            "venda": valor_final_venda,
                            "comissao_percentual": percentual_comissao,
                            "comissao_valor": valor_comissao,
                            "status": "pendente",
                            "drinks": texto_drinks  # 👈 Grava na coluna que você criou
                        }).execute()
                        
                        evento_id = response.data[0]["id"]
                    
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
                                    key_qtd = f"qtd_{item}_{marca}"
                                    qtd_garrafas = st.session_state.get(key_qtd, 0)
                    
                                    supabase.table("evento_itens").insert({
                                        "evento_id": evento_id,
                                        "produto": marca,
                                        "quantidade": qtd_garrafas,
                                        "unidade": "garrafas",
                                        "categoria": "Bebidas"
                                    }).execute()
                        st.success("✅ Orçamento salvo com sucesso!")
                        
                        # =========================
                        # SALVAR FRUTAS / INSUMOS
                        # =========================
                        for fruta, qtd_gramas in ingredientes_insumos.items():
                        
                            supabase.table("evento_itens").insert({
                                "evento_id": evento_id,
                                "produto": fruta.capitalize(),
                                "quantidade": qtd_gramas,
                                "unidade": "g",
                                "categoria": "Insumos"
                            }).execute()
                        st.success("Orçamento salvo com sucesso!")

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
        # ABA 2 - PENDENTES
        # =========================================================
        with tab2:
        
            st.subheader("📋 Orçamentos Pendentes")
        
            df_eventos = pd.DataFrame(
                supabase.table("eventos")
                .select("*")
                .eq("status", "pendente")
                .execute().data or []
            )
        
            if df_eventos.empty:
        
                st.info("Nenhum orçamento pendente")
        
            else:
        
                for _, row in df_eventos.iterrows():
        
                    evento_id = row["id"]
        
                    # =====================================================
                    # BUSCAR ITENS DO EVENTO
                    # =====================================================
        
                    itens = pd.DataFrame(
                        supabase.table("evento_itens")
                        .select("*")
                        .eq("evento_id", evento_id)
                        .execute().data or []
                    )
        
                    # =====================================================
                    # CABEÇALHO DO EVENTO
                    # =====================================================
        
                    modalidade = row.get(
                        "modalidade",
                        "Bar Completo"
                    )
        
                    icone = (
                        "🍸"
                        if modalidade == "Bar Completo"
                        else "👷"
                    )
        
                    st.markdown(
                        f"### {icone} {row.get('cliente', 'Sem cliente')}"
                    )
        
                    st.caption(
                        f"📅 {row.get('data', '')}  |  "
                        f"📍 {row.get('cidade', '')}  |  "
                        f"🆔 Evento #{evento_id}"
                    )
        
                    # =====================================================
                    # BOTÃO CHECKLIST
                    # =====================================================
        
                    if f"abrir_{evento_id}" not in st.session_state:
        
                        st.session_state[
                            f"abrir_{evento_id}"
                        ] = False
        
                    abrir = st.button(
                        "📋 Abrir Checklist",
                        key=f"check_{evento_id}"
                    )
        
                    if abrir:
        
                        st.session_state[
                            f"abrir_{evento_id}"
                        ] = not st.session_state[
                            f"abrir_{evento_id}"
                        ]
        
                    # =====================================================
                    # CHECKLIST
                    # =====================================================
        
                    if st.session_state[
                        f"abrir_{evento_id}"
                    ]:
        
                        st.divider()
        
                        st.markdown(
                            "## 📋 Checklist do Evento"
                        )
        
                        st.info(
                            f"🍸 Modalidade: **{modalidade}**"
                        )
        
                        # =================================================
                        # INFORMAÇÕES DO EVENTO
                        # =================================================
        
                        st.markdown(
                            "### 📍 Informações do Evento"
                        )
        
                        info1, info2, info3 = st.columns(3)
        
                        with info1:
        
                            st.write(
                                f"**👤 Cliente:** "
                                f"{row.get('cliente', '')}"
                            )
        
                            st.write(
                                f"**📞 Telefone:** "
                                f"{row.get('telefone', '')}"
                            )
        
                            st.write(
                                f"**🎉 Tipo:** "
                                f"{row.get('tipo_evento', '')}"
                            )
        
                        with info2:
        
                            st.write(
                                f"**📅 Data:** "
                                f"{row.get('data', '')}"
                            )
        
                            st.write(
                                f"**📍 Cidade:** "
                                f"{row.get('cidade', '')}"
                            )
        
                            st.write(
                                f"**🏠 Endereço:** "
                                f"{row.get('endereco', '')}"
                            )
        
                        with info3:
        
                            st.write(
                                f"**🕒 Chegada equipe:** "
                                f"{row.get('hora_chegada', '')}"
                            )
        
                            st.write(
                                f"**🍸 Início serviço:** "
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
                            "### 🍸 Carta de Drinks"
                        )
        
                        drinks = row.get("drinks", "")
        
                        if drinks:
        
                            lista_drinks = [
                                d.strip()
                                for d in str(drinks).split("\n")
                                if d.strip()
                            ]
        
                            if lista_drinks:
        
                                col_drink1, col_drink2 = st.columns(2)
        
                                for indice, drink in enumerate(
                                    lista_drinks
                                ):
        
                                    with (
                                        col_drink1
                                        if indice % 2 == 0
                                        else col_drink2
                                    ):
        
                                        st.markdown(
                                            f"☐ **{drink}**"
                                        )
        
                            else:
        
                                st.warning(
                                    "Nenhum drink encontrado."
                                )
        
                        else:
        
                            st.warning(
                                "Nenhum drink foi salvo neste orçamento."
                            )
        
                        # =================================================
                        # FUNÇÃO PARA CLASSIFICAR FRUTAS
                        # =================================================
        
                        def eh_fruta(produto):
        
                            produto = str(
                                produto
                            ).lower()
        
                            frutas = [
                                "limão",
                                "limao",
                                "laranja",
                                "abacaxi",
                                "morango",
                                "maracujá",
                                "maracuja",
                                "uva",
                                "melancia",
                                "manga",
                                "kiwi",
                                "maçã",
                                "maca",
                                "cereja",
                                "hortelã",
                                "hortela",
                                "fruta"
                            ]
        
                            return any(
                                fruta in produto
                                for fruta in frutas
                            )
        
                        # =================================================
                        # SEPARAR ITENS
                        # =================================================
        
                        bebidas = pd.DataFrame()
                        frutas = pd.DataFrame()
                        insumos = pd.DataFrame()
                        equipe = pd.DataFrame()
                        locacoes = pd.DataFrame()
                        custos = pd.DataFrame()
        
                        if not itens.empty:
        
                            if "categoria" in itens.columns:
        
                                bebidas = itens[
                                    itens["categoria"]
                                    .astype(str)
                                    .str.lower()
                                    == "bebidas"
                                ].copy()
        
                                insumos = itens[
                                    itens["categoria"]
                                    .astype(str)
                                    .str.lower()
                                    == "insumos"
                                ].copy()
        
                                equipe = itens[
                                    itens["categoria"]
                                    .astype(str)
                                    .str.lower()
                                    == "equipe"
                                ].copy()
        
                                locacoes = itens[
                                    itens["categoria"]
                                    .astype(str)
                                    .str.lower()
                                    == "locação"
                                ].copy()
        
                                custos = itens[
                                    itens["categoria"]
                                    .astype(str)
                                    .str.lower()
                                    == "custos"
                                ].copy()
        
                            # ---------------------------------------------
                            # SEPARAR FRUTAS DOS DEMAIS INSUMOS
                            # ---------------------------------------------
        
                            if not insumos.empty:
        
                                frutas = insumos[
                                    insumos["produto"].apply(
                                        eh_fruta
                                    )
                                ].copy()
        
                                insumos = insumos[
                                    ~insumos["produto"].apply(
                                        eh_fruta
                                    )
                                ].copy()
        
                        # =================================================
                        # BEBIDAS
                        # =================================================
        
                        st.divider()
        
                        st.markdown(
                            "### 🍾 Bebidas"
                        )
        
                        if bebidas.empty:
        
                            st.info(
                                "Nenhuma bebida registrada."
                            )
        
                        else:
        
                            dados_bebidas = []
        
                            for _, item in bebidas.iterrows():
        
                                dados_bebidas.append({
                                    "Conferido": False,
                                    "Bebida": item.get(
                                        "produto",
                                        ""
                                    ),
                                    "Quantidade": item.get(
                                        "quantidade",
                                        0
                                    ),
                                    "Unidade": item.get(
                                        "unidade",
                                        "un"
                                    )
                                })
        
                            df_bebidas_check = pd.DataFrame(
                                dados_bebidas
                            )
        
                            st.data_editor(
                                df_bebidas_check,
                                use_container_width=True,
                                hide_index=True,
                                disabled=[
                                    "Bebida",
                                    "Quantidade",
                                    "Unidade"
                                ],
                                column_config={
        
                                    "Conferido": st.column_config.CheckboxColumn(
                                        "✓"
                                    ),
        
                                    "Bebida": st.column_config.TextColumn(
                                        "🍾 Bebida"
                                    ),
        
                                    "Quantidade": st.column_config.NumberColumn(
                                        "Quantidade"
                                    ),
        
                                    "Unidade": st.column_config.TextColumn(
                                        "Unidade"
                                    )
                                },
                                key=f"check_bebidas_{evento_id}"
                            )
        
                        # =================================================
                        # FRUTAS
                        # =================================================
        
                        st.markdown(
                            "### 🍓 Frutas"
                        )
        
                        if frutas.empty:
        
                            st.info(
                                "Nenhuma fruta registrada."
                            )
        
                        else:
        
                            dados_frutas = []
        
                            for _, item in frutas.iterrows():
        
                                dados_frutas.append({
                                    "Conferido": False,
                                    "Fruta": item.get(
                                        "produto",
                                        ""
                                    ),
                                    "Quantidade": item.get(
                                        "quantidade",
                                        0
                                    ),
                                    "Unidade": item.get(
                                        "unidade",
                                        "g"
                                    )
                                })
        
                            df_frutas_check = pd.DataFrame(
                                dados_frutas
                            )
        
                            st.data_editor(
                                df_frutas_check,
                                use_container_width=True,
                                hide_index=True,
                                disabled=[
                                    "Fruta",
                                    "Quantidade",
                                    "Unidade"
                                ],
                                column_config={
        
                                    "Conferido": st.column_config.CheckboxColumn(
                                        "✓"
                                    ),
        
                                    "Fruta": st.column_config.TextColumn(
                                        "🍓 Fruta"
                                    ),
        
                                    "Quantidade": st.column_config.NumberColumn(
                                        "Quantidade"
                                    ),
        
                                    "Unidade": st.column_config.TextColumn(
                                        "Unidade"
                                    )
                                },
                                key=f"check_frutas_{evento_id}"
                            )
        
                        # =================================================
                        # INSUMOS
                        # =================================================
        
                        st.markdown(
                            "### 🧴 Insumos"
                        )
        
                        if insumos.empty:
        
                            st.info(
                                "Nenhum insumo registrado."
                            )
        
                        else:
        
                            dados_insumos = []
        
                            for _, item in insumos.iterrows():
        
                                dados_insumos.append({
                                    "Conferido": False,
                                    "Insumo": item.get(
                                        "produto",
                                        ""
                                    ),
                                    "Quantidade": item.get(
                                        "quantidade",
                                        0
                                    ),
                                    "Unidade": item.get(
                                        "unidade",
                                        "un"
                                    )
                                })
        
                            df_insumos_check = pd.DataFrame(
                                dados_insumos
                            )
        
                            st.data_editor(
                                df_insumos_check,
                                use_container_width=True,
                                hide_index=True,
                                disabled=[
                                    "Insumo",
                                    "Quantidade",
                                    "Unidade"
                                ],
                                column_config={
        
                                    "Conferido": st.column_config.CheckboxColumn(
                                        "✓"
                                    ),
        
                                    "Insumo": st.column_config.TextColumn(
                                        "🧴 Insumo"
                                    ),
        
                                    "Quantidade": st.column_config.NumberColumn(
                                        "Quantidade"
                                    ),
        
                                    "Unidade": st.column_config.TextColumn(
                                        "Unidade"
                                    )
                                },
                                key=f"check_insumos_{evento_id}"
                            )
        
                        # =================================================
                        # EQUIPE
                        # =================================================
        
                        st.markdown(
                            "### 👥 Equipe"
                        )
        
                        if equipe.empty:
        
                            st.info(
                                "Nenhuma equipe definida."
                            )
        
                        else:
        
                            for _, item in equipe.iterrows():
        
                                st.checkbox(
                                    str(
                                        item.get(
                                            "produto",
                                            ""
                                        )
                                    ),
                                    key=(
                                        f"equipe_"
                                        f"{evento_id}_"
                                        f"{item.get('id', _)}"
                                    )
                                )
        
                        # =================================================
                        # LOCAÇÕES
                        # =================================================
        
                        if not locacoes.empty:
        
                            st.markdown(
                                "### 🥂 Locações"
                            )
        
                            df_locacoes = locacoes[
                                [
                                    "produto",
                                    "quantidade"
                                ]
                            ].copy()
        
                            df_locacoes.rename(
                                columns={
                                    "produto": "Item",
                                    "quantidade": "Valor"
                                },
                                inplace=True
                            )
        
                            st.dataframe(
                                df_locacoes,
                                use_container_width=True,
                                hide_index=True
                            )
        
                        # =================================================
                        # CUSTOS EXTRAS
                        # =================================================
        
                        if not custos.empty:
        
                            st.markdown(
                                "### 💸 Custos Extras"
                            )
        
                            df_custos = custos[
                                [
                                    "produto",
                                    "quantidade"
                                ]
                            ].copy()
        
                            df_custos.rename(
                                columns={
                                    "produto": "Item",
                                    "quantidade": "Valor"
                                },
                                inplace=True
                            )
        
                            st.dataframe(
                                df_custos,
                                use_container_width=True,
                                hide_index=True
                            )
        
                        # =================================================
                        # RESUMO FINANCEIRO
                        # =================================================
        
                        st.divider()
        
                        st.markdown(
                            "### 💰 Resumo do Evento"
                        )
        
                        valor_venda = float(
                            row.get(
                                "venda",
                                0
                            ) or 0
                        )
        
                        custo_orcado = float(
                            row.get(
                                "custo",
                                0
                            ) or 0
                        )
        
                        lucro_orcado = (
                            valor_venda
                            - custo_orcado
                        )
        
                        rc1, rc2, rc3 = st.columns(3)
        
                        rc1.metric(
                            "💰 Venda",
                            f"R$ {valor_venda:,.2f}"
                        )
        
                        rc2.metric(
                            "💸 Custo Orçado",
                            f"R$ {custo_orcado:,.2f}"
                        )
        
                        rc3.metric(
                            "📈 Lucro Orçado",
                            f"R$ {lucro_orcado:,.2f}"
                        )
        
                        # =================================================
                        # FECHAR CHECKLIST
                        # =================================================
        
                        if st.button(
                            "🔽 Fechar Checklist",
                            key=f"fechar_check_{evento_id}"
                        ):
        
                            st.session_state[
                                f"abrir_{evento_id}"
                            ] = False
        
                            st.rerun()
        
                    # =====================================================
                    # VALOR DO EVENTO
                    # =====================================================
        
                    st.write(
                        f"💰 **Venda:** "
                        f"R$ {float(row.get('venda', 0) or 0):,.2f}"
                    )
        
                    # =====================================================
                    # AÇÕES
                    # =====================================================
        
                    col1, col2 = st.columns(2)
        
                    # =====================================================
                    # APROVAR
                    # =====================================================
        
                    if col1.button(
                        f"✅ Aprovar {evento_id}",
                        key=f"aprovar_{evento_id}"
                    ):
        
                        supabase.table("eventos")\
                            .update({
                                "status": "aprovado"
                            })\
                            .eq(
                                "id",
                                evento_id
                            )\
                            .execute()
        
                        valor_venda = float(
                            row.get(
                                "venda",
                                0
                            ) or 0
                        )
        
                        custo = float(
                            row.get(
                                "custo",
                                0
                            ) or 0
                        )
        
                        lucro = (
                            valor_venda
                            - custo
                        )
        
                        # ---------------------------------------------
                        # REGISTRAR VENDA
                        # ---------------------------------------------
        
                        supabase.table("vendas").insert({
        
                            "evento_id": evento_id,
                            "cliente": row["cliente"],
                            "data": row["data"],
                            "valor_venda": valor_venda,
                            "custo": custo,
                            "lucro": lucro
        
                        }).execute()
        
                        st.success(
                            "✅ Evento aprovado e venda registrada!"
                        )
        
                        st.rerun()
        
                    # =====================================================
                    # EXCLUIR
                    # =====================================================
        
                    if col2.button(
                        f"🗑 Excluir {evento_id}",
                        key=f"excluir_{evento_id}"
                    ):
        
                        # ---------------------------------------------
                        # PRIMEIRO EXCLUI OS ITENS
                        # ---------------------------------------------
        
                        supabase.table("evento_itens")\
                            .delete()\
                            .eq(
                                "evento_id",
                                evento_id
                            )\
                            .execute()
        
                        # ---------------------------------------------
                        # DEPOIS EXCLUI O EVENTO
                        # ---------------------------------------------
        
                        supabase.table("eventos")\
                            .delete()\
                            .eq(
                                "id",
                                evento_id
                            )\
                            .execute()
        
                        st.success(
                            "🗑 Evento excluído com sucesso!"
                        )
        
                        st.rerun()
        
                    st.divider()
        # =========================
        # ABA 3 - APROVADOS
        # =========================
        with tab3:
        
            st.subheader("✅ Eventos Aprovados")
        
            df_eventos = pd.DataFrame(
                supabase.table("eventos")
                .select("*")
                .eq("status", "aprovado")
                .execute().data or []
            )
        
            if df_eventos.empty:
                st.info("Nenhum evento aprovado")
            else:
                for _, row in df_eventos.iterrows():
        
                    # 🔥 CORREÇÃO: Garante que os itens existam fora da condicional do botão
                    itens = pd.DataFrame(
                        supabase.table("evento_itens")
                        .select("*")
                        .eq("evento_id", row["id"])
                        .execute().data or []
                    )

                    icone = "🍸" if row.get("modalidade") == "Bar Completo" else "👷"

                    st.write(
                        f"{icone} {row.get('modalidade', 'Bar Completo')} | "
                        f"👤 {row['cliente']} | "
                        f"📅 {row['data']} | "
                        f"📍 {row['cidade']}"
                    )
        
                    if st.button(f"📋 Checklist aprovado {row['id']}", key=f"check_aprov_{row['id']}"):
                        
                        modalidade = row.get("modalidade", "Bar Completo")
                        
                        st.subheader("📋 Checklist do Evento")
                        st.info(f"Modalidade: {modalidade}")

                        if modalidade == "Bar Completo":
                            
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
        
                            st.markdown("### 👥 Equipe")
            
                            if "equipe" in row and row["equipe"]:
                                nomes = [n.strip() for n in row["equipe"].split("\n") if n.strip()]
                                for nome in nomes:
                                    st.write(f"✔ {nome}")
                            else:
                                st.write("Sem equipe definida")
            
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

                        else:
                            st.markdown(f"""
                            ### 📍 Informações do Evento
                            
                            **👤 Cliente:** {row['cliente']}
                            
                            📞 {row['telefone']}
                            
                            📅 {row['data']}
                            📍 {row['cidade']} - {row['endereco']}
                            
                            🎉 Tipo: {row['tipo_evento']}
                            
                            🕒 Chegada equipe: {row['hora_chegada']}
                            👥 Chegada convidados: {row['hora_convidados']}
                            
                            💰 Valor contratado: R$ {row['venda']:,.2f}
                            """)
                            
                            if not itens.empty:
                                st.dataframe(
                                    itens[["categoria", "produto", "quantidade"]]
                                    .rename(columns={
                                        "categoria": "Categoria",
                                        "produto": "Produto",
                                        "quantidade": "Quantidade"
                                    }),
                                    use_container_width=True
                                )
                            else:
                                st.info("Nenhum item cadastrado.")
        
                    if st.button(f"✔ Finalizar {row['id']}", key=f"fin_{row['id']}"):
                        supabase.table("eventos")\
                            .update({"status": "finalizado"})\
                            .eq("id", row["id"])\
                            .execute()
                        
                        st.success("Evento finalizado!")
                        st.rerun()
        
                    st.divider()

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

    st.title("📊 Controle de CMV")

    tab1, tab2 = st.tabs([
        "📋 Por Evento",
        "📊 Análise"
    ])

    # =========================================================
    # CONFIGURAÇÕES
    # =========================================================

    status_eventos = [
        "aprovado",
        "finalizado",
        "concluido",
        "pago"
    ]

    categorias_cmv = [
        "Bebidas",
        "Frutas",
        "Gelo",
        "Insumos",
        "Outros"
    ]

    # =========================================================
    # 📋 TAB 1 - POR EVENTO
    # =========================================================

    with tab1:

        try:

            df_eventos = pd.DataFrame(
                supabase.table("eventos")
                .select("*")
                .in_("status", status_eventos)
                .order("data")
                .execute()
                .data
                or []
            )

        except Exception as e:

            st.error(
                f"❌ Erro ao carregar os eventos: {e}"
            )

            df_eventos = pd.DataFrame()


        if df_eventos.empty:

            st.info(
                "Nenhum evento encontrado para controle de CMV."
            )

        else:

            st.caption(
                "Registre somente os valores que realmente foram gastos "
                "para realizar cada evento. O custo previsto do orçamento "
                "não é alterado."
            )


            # =====================================================
            # LOOP DOS EVENTOS
            # =====================================================

            for _, row in df_eventos.iterrows():

                evento_id = row["id"]

                cliente = row.get(
                    "cliente",
                    "Cliente"
                )

                data_evento = row.get(
                    "data",
                    ""
                )

                valor_venda = float(
                    pd.to_numeric(
                        row.get("venda", 0),
                        errors="coerce"
                    )
                    or 0
                )

                custo_previsto = float(
                    pd.to_numeric(
                        row.get("custo", 0),
                        errors="coerce"
                    )
                    or 0
                )


                # =================================================
                # CABEÇALHO DO EVENTO
                # =================================================

                st.markdown(
                    f"## 🎉 {cliente}"
                )

                st.caption(
                    f"📅 Evento: {data_evento} | "
                    f"ID: {evento_id}"
                )


                # =================================================
                # BUSCAR CUSTOS REAIS
                # =================================================

                try:

                    custos = pd.DataFrame(
                        supabase.table("evento_custos")
                        .select("*")
                        .eq(
                            "evento_id",
                            evento_id
                        )
                        .order("id")
                        .execute()
                        .data
                        or []
                    )

                except Exception as e:

                    st.error(
                        f"❌ Erro ao carregar custos do evento: {e}"
                    )

                    custos = pd.DataFrame()


                # =================================================
                # CÁLCULOS
                # =================================================

                if not custos.empty:

                    custos["valor"] = pd.to_numeric(
                        custos["valor"],
                        errors="coerce"
                    ).fillna(0)

                    total_real = float(
                        custos["valor"].sum()
                    )

                else:

                    total_real = 0.0


                lucro_real = (
                    valor_venda
                    - total_real
                )


                economia = (
                    custo_previsto
                    - total_real
                )


                cmv_percentual = (
                    (total_real / valor_venda) * 100
                    if valor_venda > 0
                    else 0
                )


                # =================================================
                # MÉTRICAS
                # =================================================

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "💰 Faturamento",
                    f"R$ {valor_venda:,.2f}"
                )

                col2.metric(
                    "📋 Custo Previsto",
                    f"R$ {custo_previsto:,.2f}"
                )

                col3.metric(
                    "💸 Custo Real",
                    f"R$ {total_real:,.2f}"
                )

                col4.metric(
                    "📊 CMV",
                    f"{cmv_percentual:.2f}%"
                )


                col5, col6 = st.columns(2)

                col5.metric(
                    "📈 Lucro Real",
                    f"R$ {lucro_real:,.2f}"
                )

                col6.metric(
                    "💰 Diferença vs. Previsto",
                    f"R$ {economia:,.2f}",
                    help=(
                        "Diferença entre o custo previsto no orçamento "
                        "e o custo realmente lançado no CMV."
                    )
                )


                # =================================================
                # STATUS DO CMV
                # =================================================

                if custos.empty:

                    st.info(
                        "🟡 Este evento ainda não possui custos reais "
                        "lançados no CMV."
                    )

                elif cmv_percentual > 50:

                    st.error(
                        f"🚨 CMV crítico: {cmv_percentual:.2f}%"
                    )

                elif cmv_percentual > 40:

                    st.warning(
                        f"⚠️ CMV alto: {cmv_percentual:.2f}%"
                    )

                else:

                    st.success(
                        f"🟢 CMV controlado: {cmv_percentual:.2f}%"
                    )


                st.divider()


                # =================================================
                # ➕ LANÇAR CUSTO REAL
                # =================================================

                st.markdown(
                    "### ➕ Lançar custo real"
                )

                st.caption(
                    "Informe somente aquilo que realmente foi comprado "
                    "ou gasto para este evento."
                )


                col_a, col_b = st.columns(2)

                categoria = col_a.selectbox(
                    "Categoria",
                    categorias_cmv,
                    key=f"cmv_categoria_{evento_id}"
                )

                valor = col_b.number_input(
                    "Valor realmente gasto (R$)",
                    min_value=0.0,
                    step=10.0,
                    format="%.2f",
                    key=f"cmv_valor_{evento_id}"
                )


                descricao = st.text_input(
                    "Descrição",
                    placeholder=(
                        "Ex.: Compra de frutas, gelo, bebidas, "
                        "insumos etc."
                    ),
                    key=f"cmv_descricao_{evento_id}"
                )


                if st.button(
                    "💾 Registrar Custo",
                    key=f"cmv_adicionar_{evento_id}",
                    use_container_width=True
                ):

                    if valor <= 0:

                        st.warning(
                            "⚠️ Informe um valor maior que zero."
                        )

                    elif not descricao.strip():

                        st.warning(
                            "⚠️ Informe uma descrição do custo."
                        )

                    else:

                        try:

                            supabase.table(
                                "evento_custos"
                            ).insert({

                                "evento_id": int(
                                    evento_id
                                ),

                                "descricao": (
                                    f"{categoria} - "
                                    f"{descricao.strip()}"
                                ),

                                "valor": float(
                                    valor
                                )

                            }).execute()


                            st.success(
                                "✅ Custo real registrado!"
                            )

                            st.rerun()


                        except Exception as e:

                            st.error(
                                f"❌ Erro ao registrar custo: {e}"
                            )


                # =================================================
                # LISTA DOS CUSTOS REAIS
                # =================================================

                st.markdown(
                    "### 📋 Custos reais registrados"
                )


                if custos.empty:

                    st.info(
                        "Nenhum custo real registrado para este evento."
                    )

                else:

                    df_custos_exibir = custos.copy()


                    # -------------------------------------------------
                    # PREPARAÇÃO DA EXIBIÇÃO
                    # -------------------------------------------------

                    colunas_custos = []

                    if "id" in df_custos_exibir.columns:

                        colunas_custos.append(
                            "id"
                        )

                    if "descricao" in df_custos_exibir.columns:

                        colunas_custos.append(
                            "descricao"
                        )

                    if "valor" in df_custos_exibir.columns:

                        colunas_custos.append(
                            "valor"
                        )


                    df_custos_exibir = (
                        df_custos_exibir[
                            colunas_custos
                        ]
                        .copy()
                    )


                    df_custos_exibir.rename(
                        columns={

                            "id": "ID",

                            "descricao": "Descrição",

                            "valor": "Valor"

                        },
                        inplace=True
                    )


                    st.dataframe(
                        df_custos_exibir,
                        use_container_width=True,
                        hide_index=True,
                        column_config={

                            "Valor":
                                st.column_config.NumberColumn(
                                    "💰 Valor",
                                    format="R$ %.2f"
                                )

                        }
                    )


                    # =================================================
                    # EXCLUSÃO DE CUSTO
                    # =================================================

                    with st.expander(
                        "🗑️ Corrigir / excluir um custo"
                    ):

                        ids_disponiveis = (
                            custos["id"]
                            .dropna()
                            .tolist()
                            if "id" in custos.columns
                            else []
                        )


                        if ids_disponiveis:

                            id_excluir = st.selectbox(
                                "Selecione o lançamento",
                                ids_disponiveis,
                                key=f"cmv_excluir_id_{evento_id}"
                            )


                            if st.button(
                                "❌ Excluir custo selecionado",
                                key=f"cmv_excluir_{evento_id}",
                                type="secondary"
                            ):

                                try:

                                    supabase.table(
                                        "evento_custos"
                                    ).delete().eq(
                                        "id",
                                        int(id_excluir)
                                    ).execute()


                                    st.success(
                                        "✅ Custo excluído."
                                    )

                                    st.rerun()


                                except Exception as e:

                                    st.error(
                                        f"❌ Erro ao excluir custo: {e}"
                                    )


                st.divider()


    # =========================================================
    # 📊 TAB 2 - ANÁLISE
    # =========================================================

    with tab2:

        st.markdown(
            "## 📊 Análise de CMV"
        )

        st.caption(
            "Comparação entre o custo previsto no orçamento "
            "e o custo realmente realizado em cada evento."
        )


        # =====================================================
        # BUSCAR EVENTOS
        # =====================================================

        try:

            df_eventos = pd.DataFrame(
                supabase.table("eventos")
                .select("*")
                .in_(
                    "status",
                    status_eventos
                )
                .order("data")
                .execute()
                .data
                or []
            )

        except Exception as e:

            st.error(
                f"❌ Erro ao carregar eventos: {e}"
            )

            df_eventos = pd.DataFrame()


        resumo = []


        # =====================================================
        # CONSOLIDAR CADA EVENTO
        # =====================================================

        for _, row in df_eventos.iterrows():

            evento_id = row["id"]


            try:

                custos = pd.DataFrame(
                    supabase.table("evento_custos")
                    .select("*")
                    .eq(
                        "evento_id",
                        evento_id
                    )
                    .execute()
                    .data
                    or []
                )

            except Exception:

                custos = pd.DataFrame()


            if not custos.empty:

                custos["valor"] = pd.to_numeric(
                    custos["valor"],
                    errors="coerce"
                ).fillna(0)

                total_real = float(
                    custos["valor"].sum()
                )

            else:

                total_real = 0.0


            valor_venda = float(
                pd.to_numeric(
                    row.get("venda", 0),
                    errors="coerce"
                )
                or 0
            )


            custo_previsto = float(
                pd.to_numeric(
                    row.get("custo", 0),
                    errors="coerce"
                )
                or 0
            )


            lucro = (
                valor_venda
                - total_real
            )


            diferenca = (
                custo_previsto
                - total_real
            )


            cmv = (
                (total_real / valor_venda) * 100
                if valor_venda > 0
                else 0
            )


            resumo.append({

                "Cliente":
                    row.get(
                        "cliente",
                        "Cliente"
                    ),

                "Data":
                    row.get(
                        "data",
                        ""
                    ),

                "Venda":
                    valor_venda,

                "Previsto":
                    custo_previsto,

                "Real":
                    total_real,

                "Diferença":
                    diferenca,

                "Lucro":
                    lucro,

                "CMV (%)":
                    round(
                        cmv,
                        2
                    )

            })


        df_resumo = pd.DataFrame(
            resumo
        )


        # =====================================================
        # SEM DADOS
        # =====================================================

        if df_resumo.empty:

            st.info(
                "Nenhum evento disponível para análise."
            )

        else:

            # =================================================
            # TABELA
            # =================================================

            st.dataframe(
                df_resumo,
                use_container_width=True,
                hide_index=True,
                column_config={

                    "Venda":
                        st.column_config.NumberColumn(
                            "💰 Venda",
                            format="R$ %.2f"
                        ),

                    "Previsto":
                        st.column_config.NumberColumn(
                            "📋 Previsto",
                            format="R$ %.2f"
                        ),

                    "Real":
                        st.column_config.NumberColumn(
                            "💸 Custo Real",
                            format="R$ %.2f"
                        ),

                    "Diferença":
                        st.column_config.NumberColumn(
                            "📊 Economia / Diferença",
                            format="R$ %.2f"
                        ),

                    "Lucro":
                        st.column_config.NumberColumn(
                            "📈 Lucro Real",
                            format="R$ %.2f"
                        ),

                    "CMV (%)":
                        st.column_config.NumberColumn(
                            "📊 CMV",
                            format="%.2f%%"
                        )

                }
            )


            st.divider()


            # =================================================
            # ALERTAS
            # =================================================

            st.markdown(
                "### 🚨 Alertas de CMV"
            )


            alertas = False


            for _, r in df_resumo.iterrows():

                if r["CMV (%)"] > 50:

                    st.error(
                        f"🚨 **{r['Cliente']}** — "
                        f"CMV crítico: "
                        f"{r['CMV (%)']:.2f}%"
                    )

                    alertas = True


                elif r["CMV (%)"] > 40:

                    st.warning(
                        f"⚠️ **{r['Cliente']}** — "
                        f"CMV alto: "
                        f"{r['CMV (%)']:.2f}%"
                    )

                    alertas = True


            if not alertas:

                st.success(
                    "🟢 Nenhum evento apresentou CMV acima de 40%."
                )


            st.divider()


            # =================================================
            # MÉTRICAS GERAIS
            # =================================================

            total_venda = float(
                df_resumo["Venda"].sum()
            )

            total_previsto = float(
                df_resumo["Previsto"].sum()
            )

            total_custo = float(
                df_resumo["Real"].sum()
            )

            total_diferenca = float(
                df_resumo["Diferença"].sum()
            )

            total_lucro = float(
                df_resumo["Lucro"].sum()
            )


            cmv_medio = (
                (total_custo / total_venda) * 100
                if total_venda > 0
                else 0
            )


            st.markdown(
                "### 📊 Consolidado"
            )


            c1, c2, c3, c4, c5 = st.columns(5)


            c1.metric(
                "💰 Total Faturado",
                f"R$ {total_venda:,.2f}"
            )


            c2.metric(
                "📋 Custo Previsto",
                f"R$ {total_previsto:,.2f}"
            )


            c3.metric(
                "💸 Custo Real",
                f"R$ {total_custo:,.2f}"
            )


            c4.metric(
                "💰 Economia",
                f"R$ {total_diferenca:,.2f}"
            )


            c5.metric(
                "📈 Lucro Real",
                f"R$ {total_lucro:,.2f}"
            )


            st.metric(
                "📊 CMV Médio",
                f"{cmv_medio:.2f}%"
            )


            # =================================================
            # EXPLICAÇÃO
            # =================================================

            st.info(
                "💡 **Como interpretar:** o Custo Previsto é o valor "
                "calculado originalmente no orçamento. O Custo Real "
                "é somente aquilo que você efetivamente lançou como "
                "gasto após o evento. A diferença entre os dois "
                "representa o valor que não foi gasto naquele evento."
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
