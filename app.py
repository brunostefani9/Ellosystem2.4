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
    # CONFIGURAÇÃO DOS PERÍODOS
    # =========================================================
    hoje = datetime.now()

    col_p, col_i, col_f = st.columns([2, 1, 1])

    periodo = col_p.selectbox(
        "📅 Período",
        [
            "Este ano",
            "Este mês",
            "Últimos 30 dias",
            "Todos"
        ],
        key="dash_periodo"
    )

    # ---------------------------------------------------------
    # DEFINIÇÃO AUTOMÁTICA DO PERÍODO
    # ---------------------------------------------------------
    if periodo == "Este ano":

        dt_inicio = datetime(
            hoje.year,
            1,
            1
        ).date()

        dt_fim = hoje.date()

    elif periodo == "Este mês":

        dt_inicio = datetime(
            hoje.year,
            hoje.month,
            1
        ).date()

        dt_fim = hoje.date()

    elif periodo == "Últimos 30 dias":

        dt_inicio = (
            hoje - timedelta(days=30)
        ).date()

        dt_fim = hoje.date()

    else:
        # "Todos"
        dt_inicio = date(2000, 1, 1)
        dt_fim = hoje.date()

    # ---------------------------------------------------------
    # FILTROS MANUAIS
    # ---------------------------------------------------------
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

    # Segurança
    if data_i > data_f:
        st.error("⚠️ A data inicial não pode ser maior que a data final.")
        st.stop()

    # =========================================================
    # 1. CARREGAR FINANCEIRO
    # =========================================================
    df_fin = pd.DataFrame()

    try:
        response_fin = (
            supabase
            .table("Financeiro")
            .select("*")
            .execute()
        )

        df_fin = pd.DataFrame(
            response_fin.data or []
        )

    except Exception:
        try:
            response_fin = (
                supabase
                .table("financeiro")
                .select("*")
                .execute()
            )

            df_fin = pd.DataFrame(
                response_fin.data or []
            )

        except Exception:
            df_fin = pd.DataFrame()

    # =========================================================
    # TRATAMENTO DO FINANCEIRO
    # =========================================================
    if not df_fin.empty:

        if "valor" in df_fin.columns:
            df_fin["valor"] = pd.to_numeric(
                df_fin["valor"],
                errors="coerce"
            ).fillna(0)

        if "data" in df_fin.columns:

            df_fin["data"] = pd.to_datetime(
                df_fin["data"],
                errors="coerce"
            )

            df_fin = df_fin.dropna(
                subset=["data"]
            )

            # Período selecionado
            df_fin_periodo = df_fin[
                (df_fin["data"].dt.date >= data_i) &
                (df_fin["data"].dt.date <= data_f)
            ].copy()

        else:
            df_fin_periodo = df_fin.copy()

    else:

        df_fin_periodo = pd.DataFrame()

    # =========================================================
    # 2. CARREGAR EVENTOS
    # =========================================================
    df_eventos = pd.DataFrame()

    try:

        response_eventos = (
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
            .execute()
        )

        df_eventos = pd.DataFrame(
            response_eventos.data or []
        )

    except Exception as e:
        df_eventos = pd.DataFrame()

    # =========================================================
    # TRATAMENTO DOS EVENTOS
    # =========================================================
    if not df_eventos.empty:

        if "data" in df_eventos.columns:

            df_eventos["data"] = pd.to_datetime(
                df_eventos["data"],
                errors="coerce"
            )

        if "venda" in df_eventos.columns:

            df_eventos["venda"] = pd.to_numeric(
                df_eventos["venda"],
                errors="coerce"
            ).fillna(0)

        if "custo" in df_eventos.columns:

            df_eventos["custo"] = pd.to_numeric(
                df_eventos["custo"],
                errors="coerce"
            ).fillna(0)

        # Eventos dentro do período
        if "data" in df_eventos.columns:

            df_eventos_periodo = df_eventos[
                (df_eventos["data"].dt.date >= data_i) &
                (df_eventos["data"].dt.date <= data_f)
            ].copy()

        else:

            df_eventos_periodo = df_eventos.copy()

    else:

        df_eventos_periodo = pd.DataFrame()

    # =========================================================
    # 3. CÁLCULO FINANCEIRO
    #
    # MESMA LÓGICA DA ABA FINANCEIRO
    # =========================================================

    entrada_manual = 0.0
    saida_manual = 0.0

    # ---------------------------------------------------------
    # ENTRADAS
    # ---------------------------------------------------------
    if not df_fin_periodo.empty:

        if "tipo" in df_fin_periodo.columns:

            entrada_manual = df_fin_periodo[
                df_fin_periodo["tipo"]
                .astype(str)
                .str.lower()
                .eq("entrada")
            ]["valor"].sum()

    # ---------------------------------------------------------
    # SAÍDAS MANUAIS
    #
    # Custos dos eventos NÃO entram aqui porque já estão
    # registrados na coluna "custo" da tabela eventos.
    #
    # Cachês/equipe também são ignorados para evitar duplicidade,
    # seguindo a mesma regra da aba Financeiro.
    # ---------------------------------------------------------
    if not df_fin_periodo.empty:

        if "tipo" in df_fin_periodo.columns:

            df_saidas = df_fin_periodo[
                df_fin_periodo["tipo"]
                .astype(str)
                .str.lower()
                .eq("saída")
            ].copy()

            if "categoria" in df_saidas.columns:

                categorias = (
                    df_saidas["categoria"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                )

                df_saidas_validas = df_saidas[
                    ~categorias.str.contains(
                        "cachê|cache|equipe",
                        na=False
                    )
                ]

                saida_manual = (
                    df_saidas_validas["valor"].sum()
                )

            else:

                saida_manual = (
                    df_saidas["valor"].sum()
                )

    # =========================================================
    # CUSTOS DIRETOS DOS EVENTOS
    # =========================================================
    custo_eventos = 0.0

    if not df_eventos_periodo.empty:

        if "custo" in df_eventos_periodo.columns:

            custo_eventos = (
                df_eventos_periodo["custo"].sum()
            )

    # =========================================================
    # CONSOLIDADO
    # =========================================================

    faturamento = float(entrada_manual)

    custos = float(
        custo_eventos +
        saida_manual
    )

    # Resultado antes da reserva
    lucro_bruto = faturamento - custos

    # Reserva de 35%
    reserva_caixa = (
        lucro_bruto * 0.35
        if lucro_bruto > 0
        else 0.0
    )

    # Lucro real depois da reserva
    lucro_real = lucro_bruto - reserva_caixa

    # Margem real antes da reserva
    margem = (
        lucro_bruto / faturamento * 100
        if faturamento > 0
        else 0.0
    )

    # =========================================================
    # 📅 PRÓXIMOS EVENTOS
    # =========================================================
    st.subheader("📅 Próximos Eventos")

    if not df_eventos.empty and "data" in df_eventos.columns:

        proximos = df_eventos[
            (
                df_eventos["data"].dt.date >= hoje.date()
            ) &
            (
                df_eventos["status"]
                .astype(str)
                .str.lower()
                .eq("aprovado")
            )
        ].sort_values("data")

        if not proximos.empty:

            dados_proximos = []

            for _, evento in proximos.iterrows():

                cliente = evento.get(
                    "cliente",
                    "Cliente"
                )

                data_evento = evento.get(
                    "data",
                    ""
                )

                venda = float(
                    evento.get(
                        "venda",
                        0
                    ) or 0
                )

                dados_proximos.append({
                    "Cliente": cliente,
                    "Data": (
                        data_evento.strftime("%d/%m/%Y")
                        if pd.notna(data_evento)
                        else ""
                    ),
                    "Valor da Venda": venda,
                    "Status": "Aprovado"
                })

            df_proximos = pd.DataFrame(
                dados_proximos
            )

            st.dataframe(
                df_proximos,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Cliente": "🥂 Cliente",
                    "Data": "📅 Data",
                    "Valor da Venda": st.column_config.NumberColumn(
                        "💰 Valor da Venda",
                        format="R$ %.2f"
                    ),
                    "Status": "📌 Status"
                }
            )

        else:

            st.info(
                "Nenhum próximo evento aprovado."
            )

    else:

        st.info(
            "Nenhum próximo evento aprovado."
        )

    st.divider()

    # =========================================================
    # ABA DE NAVEGAÇÃO INTERNA
    # =========================================================
    (
        tab_visao,
        tab_fin,
        tab_vendas,
        tab_metas,
        tab_prod
    ) = st.tabs([
        "📊 Visão Geral",
        "💰 Financeiro",
        "📈 Vendas",
        "🎯 Metas",
        "📦 Produtos"
    ])

    # =========================================================
    # TAB 1 — VISÃO GERAL
    # =========================================================
    with tab_visao:

        st.subheader("📊 Visão Geral do Negócio")

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "💰 Faturamento",
            f"R$ {faturamento:,.2f}"
        )

        c2.metric(
            "💸 Custos",
            f"R$ {custos:,.2f}"
        )

        c3.metric(
            "📈 Lucro",
            f"R$ {lucro_bruto:,.2f}"
        )

        c4.metric(
            "📊 Margem",
            f"{margem:.1f}%"
        )

        c5.metric(
            "🛡️ Reserva Caixa PJ",
            f"R$ {reserva_caixa:,.2f}",
            help="35% do lucro antes da reserva."
        )

        st.divider()

        # -----------------------------------------------------
        # RESULTADO REAL
        # -----------------------------------------------------
        st.subheader("💰 Resultado Real")

        r1, r2, r3 = st.columns(3)

        r1.metric(
            "📊 Resultado antes da Reserva",
            f"R$ {lucro_bruto:,.2f}"
        )

        r2.metric(
            "🛡️ Reserva Caixa PJ (35%)",
            f"R$ {reserva_caixa:,.2f}"
        )

        r3.metric(
            "📈 Lucro Real",
            f"R$ {lucro_real:,.2f}"
        )

        st.caption(
            "O Lucro Real representa o resultado após a separação dos 35% destinados à Reserva Caixa PJ."
        )

        st.divider()

        # -----------------------------------------------------
        # GRÁFICO MENSAL
        # -----------------------------------------------------
        st.subheader(
            "📈 Faturamento vs. Custos — Mês a Mês"
        )

        if not df_fin_periodo.empty:

            df_graf = df_fin_periodo.copy()

            df_graf["mes_ano"] = (
                df_graf["data"]
                .dt.to_period("M")
                .astype(str)
            )

            entradas_mensais = (
                df_graf[
                    df_graf["tipo"]
                    .astype(str)
                    .str.lower()
                    .eq("entrada")
                ]
                .groupby("mes_ano")["valor"]
                .sum()
            )

            saidas_mensais = (
                df_graf[
                    df_graf["tipo"]
                    .astype(str)
                    .str.lower()
                    .eq("saída")
                ]
                .groupby("mes_ano")["valor"]
                .sum()
            )

            df_mensal = pd.DataFrame({
                "Faturamento": entradas_mensais,
                "Saídas Financeiras": saidas_mensais
            }).fillna(0)

            st.line_chart(
                df_mensal
            )

        else:

            st.info(
                "Não existem movimentações financeiras no período selecionado."
            )

    # =========================================================
    # TAB 2 — FINANCEIRO
    # =========================================================
    with tab_fin:

        st.subheader(
            "💰 Resumo Financeiro"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "💵 Entradas",
            f"R$ {faturamento:,.2f}"
        )

        c2.metric(
            "💸 Saídas / Custos",
            f"R$ {custos:,.2f}"
        )

        c3.metric(
            "🏦 Saldo",
            f"R$ {lucro_bruto:,.2f}"
        )

        c4.metric(
            "🛡️ Reserva Caixa PJ",
            f"R$ {reserva_caixa:,.2f}"
        )

        st.divider()

        # -----------------------------------------------------
        # DETALHAMENTO
        # -----------------------------------------------------
        st.markdown(
            "### 📄 Movimentações Financeiras"
        )

        if not df_fin_periodo.empty:

            df_fin_exibir = (
                df_fin_periodo
                .sort_values(
                    "data",
                    ascending=False
                )
                .copy()
            )

            df_fin_exibir["data"] = (
                df_fin_exibir["data"]
                .dt.strftime("%d/%m/%Y")
            )

            colunas_exibir = [
                c for c in [
                    "id",
                    "data",
                    "tipo",
                    "categoria",
                    "forma_pagamento",
                    "descricao",
                    "valor"
                ]
                if c in df_fin_exibir.columns
            ]

            df_fin_exibir = df_fin_exibir[
                colunas_exibir
            ]

            st.dataframe(
                df_fin_exibir,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID",
                    "data": "📅 Data",
                    "tipo": "Tipo",
                    "categoria": "Categoria",
                    "forma_pagamento": "Forma",
                    "descricao": "Descrição",
                    "valor": st.column_config.NumberColumn(
                        "💰 Valor",
                        format="R$ %.2f"
                    )
                }
            )

        else:

            st.info(
                "Nenhuma movimentação encontrada no período selecionado."
            )

        st.divider()

        # -----------------------------------------------------
        # RESUMO DOS CUSTOS
        # -----------------------------------------------------
        st.markdown(
            "### 💸 Composição dos Custos"
        )

        custo_col1, custo_col2 = st.columns(2)

        custo_col1.metric(
            "🎉 Custos dos Eventos",
            f"R$ {custo_eventos:,.2f}"
        )

        custo_col2.metric(
            "🏢 Despesas Gerais",
            f"R$ {saida_manual:,.2f}"
        )

    # =========================================================
    # TAB 3 — VENDAS
    # =========================================================
    with tab_vendas:

        st.subheader(
            "📈 Desempenho de Vendas & Contratos"
        )

        # -----------------------------------------------------
        # EVENTOS FECHADOS NO PERÍODO
        # -----------------------------------------------------
        if not df_eventos_periodo.empty:

            eventos_fechados = df_eventos_periodo[
                df_eventos_periodo["status"]
                .astype(str)
                .str.lower()
                .isin([
                    "aprovado",
                    "finalizado",
                    "concluido",
                    "pago"
                ])
            ].copy()

        else:

            eventos_fechados = pd.DataFrame()

        # -----------------------------------------------------
        # MÉTRICAS
        # -----------------------------------------------------
        total_eventos = (
            len(eventos_fechados)
            if not eventos_fechados.empty
            else 0
        )

        faturamento_contratado = (
            eventos_fechados["venda"].sum()
            if not eventos_fechados.empty
            and "venda" in eventos_fechados.columns
            else 0.0
        )

        custo_contratado = (
            eventos_fechados["custo"].sum()
            if not eventos_fechados.empty
            and "custo" in eventos_fechados.columns
            else 0.0
        )

        lucro_eventos = (
            faturamento_contratado -
            custo_contratado
        )

        ticket_medio = (
            faturamento_contratado /
            total_eventos
            if total_eventos > 0
            else 0.0
        )

        v1, v2, v3, v4 = st.columns(4)

        v1.metric(
            "📦 Eventos Fechados",
            f"{total_eventos}"
        )

        v2.metric(
            "💰 Vendas Contratadas",
            f"R$ {faturamento_contratado:,.2f}"
        )

        v3.metric(
            "🎯 Ticket Médio",
            f"R$ {ticket_medio:,.2f}"
        )

        v4.metric(
            "📈 Lucro Estimado",
            f"R$ {lucro_eventos:,.2f}"
        )

        st.divider()

        # -----------------------------------------------------
        # COMPARATIVO POR EVENTO
        # -----------------------------------------------------
        st.markdown(
            "### 📊 Comparativo por Evento"
        )

        if not eventos_fechados.empty:

            dados_grafico = []

            for _, evento in eventos_fechados.iterrows():

                cliente = evento.get(
                    "cliente",
                    "Cliente"
                )

                venda = float(
                    evento.get(
                        "venda",
                        0
                    ) or 0
                )

                custo = float(
                    evento.get(
                        "custo",
                        0
                    ) or 0
                )

                dados_grafico.append({
                    "Cliente": cliente,
                    "Faturamento": venda,
                    "Custo": custo
                })

            df_grafico_eventos = pd.DataFrame(
                dados_grafico
            )

            if not df_grafico_eventos.empty:

                df_grafico_eventos = (
                    df_grafico_eventos
                    .set_index("Cliente")
                )

                st.bar_chart(
                    df_grafico_eventos[
                        [
                            "Faturamento",
                            "Custo"
                        ]
                    ]
                )

        else:

            st.info(
                "Nenhum evento fechado no período selecionado."
            )

        st.divider()

        # -----------------------------------------------------
        # LISTA DE EVENTOS
        # -----------------------------------------------------
        st.markdown(
            "### 📋 Detalhamento dos Eventos"
        )

        if not eventos_fechados.empty:

            df_vendas_exibir = pd.DataFrame()

            dados = []

            for _, evento in eventos_fechados.iterrows():

                venda = float(
                    evento.get(
                        "venda",
                        0
                    ) or 0
                )

                custo = float(
                    evento.get(
                        "custo",
                        0
                    ) or 0
                )

                dados.append({
                    "Cliente": evento.get(
                        "cliente",
                        "Cliente"
                    ),
                    "Data": (
                        evento["data"].strftime(
                            "%d/%m/%Y"
                        )
                        if "data" in evento
                        and pd.notna(evento["data"])
                        else ""
                    ),
                    "Venda": venda,
                    "Custo": custo,
                    "Lucro Estimado": venda - custo,
                    "Status": evento.get(
                        "status",
                        ""
                    )
                })

            df_vendas_exibir = pd.DataFrame(
                dados
            )

            st.dataframe(
                df_vendas_exibir,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Cliente": "🥂 Cliente",
                    "Data": "📅 Data",
                    "Venda": st.column_config.NumberColumn(
                        "💰 Venda",
                        format="R$ %.2f"
                    ),
                    "Custo": st.column_config.NumberColumn(
                        "💸 Custo",
                        format="R$ %.2f"
                    ),
                    "Lucro Estimado": st.column_config.NumberColumn(
                        "📈 Lucro Estimado",
                        format="R$ %.2f"
                    ),
                    "Status": "📌 Status"
                }
            )

        else:

            st.info(
                "Nenhum evento encontrado no período selecionado."
            )

    # =========================================================
    # TAB 4 — METAS
    # =========================================================
    with tab_metas:

        st.subheader(
            "🎯 Metas de Faturamento"
        )

        # Meta atual
        meta_mensal = 10000.00

        # Faturamento efetivo do mês atual
        if not df_fin.empty:

            df_mes_atual = df_fin[
                (
                    df_fin["data"].dt.year
                    == hoje.year
                ) &
                (
                    df_fin["data"].dt.month
                    == hoje.month
                ) &
                (
                    df_fin["tipo"]
                    .astype(str)
                    .str.lower()
                    .eq("entrada")
                )
            ]

            faturamento_mes_atual = (
                df_mes_atual["valor"].sum()
                if not df_mes_atual.empty
                else 0.0
            )

        else:

            faturamento_mes_atual = 0.0

        percentual_meta = (
            faturamento_mes_atual /
            meta_mensal
            if meta_mensal > 0
            else 0.0
        )

        percentual_progressao = min(
            percentual_meta,
            1.0
        )

        if faturamento_mes_atual >= meta_mensal:

            status_meta = "🟢 Meta atingida"

        else:

            status_meta = "🟡 Meta em andamento"

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "🎯 Meta Mensal",
            f"R$ {meta_mensal:,.2f}"
        )

        m2.metric(
            "💰 Faturado no Mês",
            f"R$ {faturamento_mes_atual:,.2f}"
        )

        m3.metric(
            "📊 Progresso",
            f"{percentual_meta * 100:.1f}%",
            delta=status_meta
        )

        st.progress(
            percentual_progressao
        )

    # =========================================================
    # TAB 5 — PRODUTOS
    # =========================================================
    with tab_prod:

        st.subheader(
            "📦 Desempenho por Produto / Serviço"
        )

        st.info(
            "Esta área ficará disponível para o controle de produtos, "
            "estoque e materiais utilizados nos eventos."
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

        # =========================
        # ABA 2 - PENDENTES
        # =========================
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

                    # 🔥 CORREÇÃO: Busca os itens aqui no início do loop para que a variável 'itens' sempre exista
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
                        
                        modalidade = row.get("modalidade", "Bar Completo")

                        st.subheader("📋 Checklist do Evento")
                        st.info(f"Modalidade: {modalidade}")

                        # =========================
                        # 🍸 CARTA DE DRINKS SELECIONADOS
                        # =========================
                        st.markdown("### 🍸 Cardápio de Drinks Escolhidos")
                        
                        # Buscando direto da coluna 'drinks' da tabela eventos
                        if "drinks" in row and row["drinks"]:
                            texto_drinks = row["drinks"]
                            # Divide o texto do banco por quebras de linha para listar um por um
                            lista_drinks = [d.strip() for d in texto_drinks.split("\n") if d.strip()]
                            
                            for drink in lista_drinks:
                                st.markdown(f"*{drink}")
                        else:
                            st.warning("Nenhum drink salvo neste orçamento ainda. Verifique o cadastro do orçamento.")
                        
                        st.markdown("---")

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
                        # ITENS DO EVENTO
                        # =========================
                        if itens.empty:
                            st.warning("Nenhum item encontrado")
                            df_checklist = pd.DataFrame(columns=["Categoria", "produto", "quantidade", "Início", "Fim"])
                        else:
                            df_checklist = itens.copy()

                        # =========================
                        # CATEGORIA INTELIGENTE
                        # =========================
                        def definir_categoria(produto):
                            produto = str(produto).lower()
                            if any(p in produto for p in ["vodka", "gin", "rum", "whisky", "tequila", "licor", "cachaça", "martini", "campari", "absolut", "jack daniels", "aperol", "salton"]):
                                return "Bebidas"
                            elif any(p in produto for p in ["limão", "limao", "laranja", "abacaxi", "morango", "fruta", "blossom"]):
                                return "Frutas"
                            elif any(p in produto for p in ["xarope", "açucar", "acucar", "grenadine", "insumo", "sarandi", "suvalan", "coca cola", "agua", "tônica", "tonica", "refrigerante"]):
                                return "Insumos"
                            else:
                                return "Outros"

                        if not df_checklist.empty:
                            df_checklist["Categoria"] = df_checklist["produto"].apply(definir_categoria)

                        if "Início" not in df_checklist.columns:
                            df_checklist["Início"] = ""
                        if "Fim" not in df_checklist.columns:
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

                            supabase.table("evento_itens")\
                                .delete()\
                                .eq("evento_id", row["id"])\
                                .execute()

                            for _, item in df_editado.iterrows():
                                if str(item["produto"]).strip() == "":
                                    continue
                                supabase.table("evento_itens").insert({
                                    "evento_id": row["id"],
                                    "produto": item["produto"],
                                    "quantidade": float(item["quantidade"]),
                                    "unidade": "un",
                                    "categoria": item["Categoria"]
                                }).execute()
                            st.success("Checklist atualizado com sucesso!")
                            st.rerun()
                        # Agora esse 'itens' sempre existirá sem quebrar o app
                        if not itens.empty:
                            equipe = itens[itens["categoria"] == "Equipe"]
                            if not equipe.empty:
                                for _, item in equipe.iterrows():
                                    st.write(f"✔ {item['produto']}")

                            locacoes = itens[itens["categoria"] == "Locação"]
                            if not locacoes.empty:
                                st.markdown("### 🥂 Locações")
                                st.dataframe(
                                    locacoes[["produto", "quantidade"]]
                                    .rename(columns={
                                        "produto": "Item",
                                        "quantidade": "Valor"
                                    }),
                                    use_container_width=True
                                )

                            custos = itens[itens["categoria"] == "Custos"]
                            if not custos.empty:
                                st.markdown("### 💸 Custos")
                                st.dataframe(
                                    custos[["produto", "quantidade"]]
                                    .rename(columns={
                                        "produto": "Item",
                                        "quantidade": "Valor"
                                    }),
                                    use_container_width=True
                                )
                        else:
                            st.warning("Nenhum item encontrado")

                    # =========================
                    # VALOR
                    # =========================
                    st.write(f"💰 Venda: R$ {row['venda']:,.2f}")

                    # =========================
                    # AÇÕES
                    # =========================
                    col1, col2 = st.columns(2)

                    if col1.button(f"✅ Aprovar {row['id']}", key=f"aprovar_{row['id']}"):

                        supabase.table("eventos")\
                            .update({"status": "aprovado"})\
                            .eq("id", row["id"])\
                            .execute()

                        valor_venda = row["venda"] if "venda" in row else 0
                        custo = row["custo"] if "custo" in row else 0
                        lucro = valor_venda - custo

                        supabase.table("vendas").insert({
                            "evento_id": row["id"],
                            "cliente": row["cliente"],
                            "data": row["data"],
                            "valor_venda": valor_venda,
                            "custo": custo,
                            "lucro": lucro
                        }).execute()
                        st.success("Evento aprovado e venda registrada!")
                        st.rerun()

                        alertas = []

                        bebidas = itens[itens["categoria"] == "Bebidas"]

                        for _, bebida in bebidas.iterrows():
                            marca = bebida["produto"]
                            qtd_necessaria = bebida["quantidade"]

                            atual = pd.DataFrame(
                                supabase.table("estoque")
                                .select("*")
                                .eq("marca", marca)
                                .execute().data or []
                            )

                            if atual.empty:
                                alertas.append(f"❌ {marca} não existe no estoque")
                            else:
                                qtd_atual = atual.iloc[0]["quantidade"]

                                if qtd_atual < qtd_necessaria:
                                    alertas.append(f"⚠️ {marca}: precisa {qtd_necessaria}, tem {qtd_atual}")

                                nova_qtd = max(0, qtd_atual - qtd_necessaria)

                                supabase.table("estoque")\
                                    .update({"quantidade": nova_qtd})\
                                    .eq("marca", marca)\
                                    .execute()

                                supabase.table("movimentacoes").insert({
                                    "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "tipo": "bebida",
                                    "produto": marca,
                                    "descricao": "Saída (orçamento aprovado)",
                                    "quantidade": qtd_necessaria,
                                    "origem": "Reserva"
                                }).execute()

                        if alertas:
                            st.warning("⚠️ Problemas no estoque:")
                            for a in alertas:
                                st.write(a)
                        else:
                            st.success("✅ Evento aprovado e estoque atualizado!")

                        st.session_state["orcamento_bebidas"] = {}
                        st.rerun()

                    if col2.button(f"🗑 Excluir {row['id']}", key=f"excluir_{row['id']}"):
                        supabase.table("eventos")\
                            .delete()\
                            .eq("id", row["id"])\
                            .execute()
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

    # 1. Carrega Eventos Válidos
    response_eventos = (
        supabase.table("eventos")
        .select("*")
        .in_("status", ["aprovado", "finalizado", "concluido", "pago"])
        .execute()
    )
    df_eventos = pd.DataFrame(response_eventos.data or [])

    # 2. Carrega Aditivos (Horas Extras, Adicionais, etc.)
    response_aditivos = supabase.table("aditivos_evento").select("*").execute()
    df_aditivos = pd.DataFrame(response_aditivos.data or [])

    # 3. Carrega Custos Reais da Tabela Financeiro (Saídas)
    response_fin = supabase.table("Financeiro").select("valor, tipo").eq("tipo", "Saída").execute()
    df_fin = pd.DataFrame(response_fin.data or [])

    if not df_eventos.empty:
        # Garante tipos numéricos
        df_eventos["venda_base"] = pd.to_numeric(df_eventos["venda"], errors="coerce").fillna(0)

        # Processa os Aditivos/Horas Extras por Evento
        if not df_aditivos.empty and "evento_id" in df_aditivos.columns:
            df_aditivos["valor_cliente"] = pd.to_numeric(df_aditivos["valor_cliente"], errors="coerce").fillna(0)
            
            aditivos_agrupados = df_aditivos.groupby("evento_id")["valor_cliente"].sum().reset_index()
            aditivos_agrupados.rename(columns={"valor_cliente": "horas_extras"}, inplace=True)

            # Une eventos com aditivos
            df = df_eventos.merge(aditivos_agrupados, left_on="id", right_on="evento_id", how="left")
            df["horas_extras"] = df["horas_extras"].fillna(0)
        else:
            df = df_eventos.copy()
            df["horas_extras"] = 0.0

        # VALOR TOTAL REAL = Valor do Contrato + Horas Extras
        df["valor_venda"] = df["venda_base"] + df["horas_extras"]
    else:
        df = pd.DataFrame(columns=[
            "id", "cliente", "data", "venda_base", "horas_extras", "valor_venda", "status"
        ])

    # Custo Total Real do Caixa
    total_custo = pd.to_numeric(df_fin["valor"], errors="coerce").fillna(0).sum() if not df_fin.empty else 0.0

    # KPIs
    total_vendas = df["valor_venda"].sum() if not df.empty else 0.0
    total_lucro = total_vendas - total_custo
    margem = (total_lucro / total_vendas * 100) if total_vendas > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Receita Total", f"R$ {total_vendas:,.2f}")
    col2.metric("💸 Custo Total", f"R$ {total_custo:,.2f}")
    col3.metric("📈 Lucro Total", f"R$ {total_lucro:,.2f}")
    col4.metric("📊 Margem", f"{margem:.1f}%")

    st.markdown("---")

    # Filtro de Busca por Cliente
    cliente = st.text_input("Buscar cliente")

    if cliente and not df.empty and "cliente" in df.columns:
        df = df[df["cliente"].str.contains(cliente, case=False, na=False)]

    # Preparação da Tabela para Exibição
    if not df.empty:
        df_exibir = df[[
            "cliente", "data", "venda_base", "horas_extras", "valor_venda", "status"
        ]].copy()

        st.dataframe(
            df_exibir,
            use_container_width=True,
            column_config={
                "cliente": "🥂 Cliente",
                "data": "📅 Data",
                "venda_base": st.column_config.NumberColumn("📋 Contrato Base", format="R$ %.2f"),
                "horas_extras": st.column_config.NumberColumn("⏰ Horas Extras / Aditivos", format="R$ %.2f"),
                "valor_venda": st.column_config.NumberColumn("💰 Valor Total Real", format="R$ %.2f"),
                "status": "📌 Status",
            }
        )
    else:
        st.warning("Nenhuma venda registrada ainda — aparecerá ao aprovar/finalizar eventos.")

    # Gráfico de Evolução das Vendas (Valor Total Real)
    st.markdown("---")
    st.subheader("📊 Evolução das vendas (Valor Total com Aditivos)")

    if not df.empty:
        df["data_dt"] = pd.to_datetime(df["data"], errors="coerce")
        vendas_por_data = df.groupby(df["data_dt"].dt.date)["valor_venda"].sum()
        st.line_chart(vendas_por_data)
    else:
        st.info("Sem dados ainda para o gráfico.")

elif menu == "CMV":

    st.title("📊 Controle de CMV")
    
    tab1, tab2 = st.tabs([
        "📋 Por Evento",
        "📊 Análise"
    ])

    with tab1:
    
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
    
                st.subheader(f"{row['cliente']} - {row['data']}")
    
                valor_venda = row.get("venda", 0)
                custo_previsto = row.get("custo", 0)
    
                # =========================
                # BUSCAR CUSTOS
                # =========================
                custos = pd.DataFrame(
                    supabase.table("evento_custos")
                    .select("*")
                    .eq("evento_id", row["id"])
                    .execute().data or []
                )
    
                total_real = custos["valor"].sum() if not custos.empty else 0
                lucro_real = valor_venda - total_real
    
                col1, col2, col3 = st.columns(3)
                col1.metric("Venda", f"R$ {valor_venda:,.2f}")
                col2.metric("Previsto", f"R$ {custo_previsto:,.2f}")
                col3.metric("Real", f"R$ {total_real:,.2f}")
    
                st.metric("Lucro Real", f"R$ {lucro_real:,.2f}")
    
                # =========================
                # LANÇAR CUSTO
                # =========================
                st.markdown("### ➕ Lançar custo")
    
                descricao = st.text_input(
                    "Descrição",
                    key=f"desc_{row['id']}"
                )
    
                valor = st.number_input(
                    "Valor",
                    min_value=0.0,
                    key=f"valor_{row['id']}"
                )
    
                if st.button(f"Adicionar {row['id']}"):
                    supabase.table("evento_custos").insert({
                        "evento_id": row["id"],
                        "descricao": descricao,
                        "valor": valor
                    }).execute()
    
                    st.success("Custo adicionado")
                    st.rerun()
    
                # =========================
                # LISTA
                # =========================
                st.markdown("### 📋 Custos")
    
                if custos.empty:
                    st.info("Sem custos lançados")
                else:
                    for _, c in custos.iterrows():
                        st.write(f"{c['descricao']} → R$ {c['valor']:,.2f}")
    
                st.divider()
    
    with tab2:
    
        df_eventos = pd.DataFrame(
            supabase.table("eventos")
            .select("*")
            .eq("status", "aprovado")
            .execute().data or []
        )
    
        resumo = []
    
        for _, row in df_eventos.iterrows():
    
            custos = pd.DataFrame(
                supabase.table("evento_custos")
                .select("*")
                .eq("evento_id", row["id"])
                .execute().data or []
            )
    
            total_real = custos["valor"].sum() if not custos.empty else 0
            lucro = row.get("venda", 0) - total_real

            valor_venda = row.get("venda", 0)
            cmv = (total_real / valor_venda) * 100 if valor_venda > 0 else 0
    
            resumo.append({
                "Cliente": row["cliente"],
                "Venda": row.get("venda", 0),
                "Previsto": row.get("custo", 0),
                "Real": total_real,
                "Lucro": lucro,
                "CMV (%)": round(cmv, 2)
            })
            
        df_resumo = pd.DataFrame(resumo)

        if df_resumo.empty:
            st.info("Sem dados")
        else:
            st.dataframe(df_resumo)
        
            # 🔥 ALERTAS DE CMV
            for _, r in df_resumo.iterrows():
                if r["CMV (%)"] > 50:
                    st.error(f"🚨 {r['Cliente']} com CMV crítico: {r['CMV (%)']}%")
                elif r["CMV (%)"] > 40:
                    st.warning(f"⚠️ {r['Cliente']} com CMV alto: {r['CMV (%)']}%")
        
            # =========================
            # MÉTRICAS GERAIS
            # =========================
            total_venda = df_resumo["Venda"].sum()
            total_custo = df_resumo["Real"].sum()
            total_lucro = df_resumo["Lucro"].sum()
        
            st.metric("Total Venda", f"R$ {total_venda:,.2f}")
            st.metric("Total Custo", f"R$ {total_custo:,.2f}")
            st.metric("Total Lucro", f"R$ {total_lucro:,.2f}")
        
            if total_venda > 0:
                cmv_medio = (total_custo / total_venda) * 100
                st.metric("CMV Médio", f"{cmv_medio:.2f}%")

elif menu == "Financeiro":

    st.title("💰 Financeiro")

    tab1, tab_pendentes, tab2, tab4, tab5 = st.tabs([
        "📊 Resumo",
        "🔔 Pendências / A Receber",
        "🎉 Eventos",
        "➕ Lançamentos Manuais",
        "📄 Extrato Complete",
    ])

    # =========================================================
    # 📊 TAB 1: RESUMO (FINANCEIRO CORRIGIDO)
    # =========================================================
    with tab1:
        # Garantia de datas padrão para evitar NameError
        data_inicial = date(date.today().year, 1, 1)
        data_final = date.today()

        # 1. Buscar transações manuais da tabela Financeiro
        response_fin = supabase.table("Financeiro").select("*").execute()
        df_fin = pd.DataFrame(response_fin.data or [])

        # 2. Buscar eventos para consolidar os custos diretos dos contratos
        response_eventos = (
            supabase.table("eventos")
            .select("custo, venda, status")
            .in_("status", ["aprovado", "finalizado", "concluido", "pago"])
            .execute()
        )
        df_eventos = pd.DataFrame(response_eventos.data or [])

        # --- CÁLCULO DE ENTRADAS ---
        entrada_manual = 0.0
        saida_manual = 0.0

        if not df_fin.empty:
            df_fin["valor"] = pd.to_numeric(df_fin["valor"], errors="coerce").fillna(0)
            
            # Entradas registradas no fluxo financeiro
            entrada_manual = df_fin[df_fin["tipo"] == "Entrada"]["valor"].sum()
            
            # Saídas manuais gerais (Ignora lançamentos de cachê para evitar duplicidade)
            if "categoria" in df_fin.columns:
                df_saidas_validas = df_fin[
                    (df_fin["tipo"] == "Saída") & 
                    (~df_fin["categoria"].str.lower().str.contains("cachê|cache|equipe", na=False))
                ]
                saida_manual = df_saidas_validas["valor"].sum()
            else:
                saida_manual = df_fin[df_fin["tipo"] == "Saída"]["valor"].sum()

        # --- CÁLCULO DE CUSTOS DOS EVENTOS ---
        custo_eventos_total = 0.0
        if not df_eventos.empty:
            df_eventos["custo"] = pd.to_numeric(df_eventos["custo"], errors="coerce").fillna(0)
            custo_eventos_total = df_eventos["custo"].sum()

        # Consolidado Final
        entrada = entrada_manual
        saida = custo_eventos_total + saida_manual
        saldo = entrada - saida
        lucro_real = max(0.0, saldo)
        
        # Reserva PJ de 35% calculada sobre o Lucro Real Consolidado
        caixa_35_total = lucro_real * 0.35

        # --- CARDS DE MÉTRICAS ---
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("💰 Entradas Totais", f"R$ {entrada:,.2f}")
        col2.metric("💸 Saídas / Custos Totais", f"R$ {saida:,.2f}")
        col3.metric("🏦 Saldo de Caixa", f"R$ {saldo:,.2f}")
        col4.metric("📈 Resultado / Lucro", f"R$ {lucro_real:,.2f}")
        col5.metric(
            "🛡️ Reserva Caixa PJ (35%)",
            f"R$ {caixa_35_total:,.2f}",
            help="35% calculados sobre o Lucro Real (Entradas - Custos Totais dos Eventos e Despesas Gerais).",
        )

        st.divider()

        # --- CONTAS A RECEBER (EVENTOS) ---
        try:
            recebimentos = pd.DataFrame(
                supabase.table("recebimentos_eventos").select("*").execute().data or []
            )

            total_contratado = 0.0
            total_recebido = 0.0
            total_a_receber = 0.0

            if not df_eventos.empty:
                df_eventos["venda"] = pd.to_numeric(df_eventos["venda"], errors="coerce").fillna(0)
                total_contratado = df_eventos["venda"].sum()

                if not recebimentos.empty:
                    recebimentos["valor"] = pd.to_numeric(recebimentos["valor"], errors="coerce").fillna(0)
                    total_recebido = recebimentos["valor"].sum()

                total_a_receber = max(0.0, total_contratado - total_recebido)

            st.subheader("📋 Contas a receber (Eventos)")
            c1, c2, c3 = st.columns(3)
            c1.metric("🎉 Contratado", f"R$ {total_contratado:,.2f}")
            c2.metric("💰 Recebido", f"R$ {total_recebido:,.2f}")
            c3.metric("🟡 A receber", f"R$ {total_a_receber:,.2f}")

        except Exception:
            st.info("Controle de recebimentos ainda não disponível.")

        st.divider()

        # --- GRÁFICOS DE ACOMPANHAMENTO ---
        if not df_fin.empty:
            df_fin["data"] = pd.to_datetime(df_fin["data"], errors="coerce")
            df_fin = df_fin.dropna(subset=["data"])

            if not df_fin.empty:
                df_fin["mes"] = df_fin["data"].dt.to_period("M")
                mensal = (
                    df_fin.groupby(["mes", "tipo"])["valor"]
                    .sum()
                    .unstack()
                    .fillna(0)
                )

                st.subheader("📊 Resultado mensal")
                st.bar_chart(mensal)

                st.subheader("💸 Gastos por categoria")
                if "categoria" in df_fin.columns:
                    gastos = (
                        df_fin[df_fin["tipo"] == "Saída"]
                        .groupby("categoria")["valor"]
                        .sum()
                        .sort_values(ascending=False)
                    )
                    if not gastos.empty:
                        st.dataframe(gastos, use_container_width=True)

                st.subheader("💳 Entradas por categoria")
                if "categoria" in df_fin.columns:
                    entradas_cat = (
                        df_fin[df_fin["tipo"] == "Entrada"]
                        .groupby("categoria")["valor"]
                        .sum()
                        .sort_values(ascending=False)
                    )
                    if not entradas_cat.empty:
                        st.dataframe(entradas_cat, use_container_width=True)

                df_ordenado = df_fin.sort_values("data").copy()
                df_ordenado["fluxo"] = df_ordenado.apply(
                    lambda x: (x["valor"] if x["tipo"] == "Entrada" else -x["valor"]),
                    axis=1,
                )
                df_ordenado["saldo_acumulado"] = df_ordenado["fluxo"].cumsum()

                st.subheader("🏦 Evolução do caixa")
                st.line_chart(df_ordenado.set_index("data")["saldo_acumulado"])

            if saida > entrada:
                st.error("⚠️ Atenção: As saídas e custos totais superaram as entradas no período!")
    # =========================================================
    # 🔔 TAB 2: PENDÊNCIAS / A RECEBER (EVENTOS)
    # =========================================================
    with tab_pendentes:
        st.subheader("🔔 Eventos com Saldo Pendente")
        st.caption("Central de ações para lançar pagamentos e aditivos de eventos em aberto.")

        eventos = pd.DataFrame(
            supabase.table("eventos")
            .select("*")
            .in_("status", ["aprovado", "finalizado", "concluido", "pago"])
            .order("data")
            .execute()
            .data
            or []
        )

        recebimentos = pd.DataFrame(
            supabase.table("recebimentos_eventos").select("*").execute().data or []
        )

        aditivos_df = pd.DataFrame(
            supabase.table("aditivos_evento").select("*").execute().data or []
        )

        if eventos.empty:
            st.info("Nenhum evento encontrado.")
        else:
            eventos_com_pendencia = 0

            for _, evento in eventos.iterrows():
                evento_id = evento["id"]
                cliente = evento.get("cliente", "Cliente")
                data_evento = evento.get("data", "")

                total_aditivos_cliente = 0.0
                total_aditivos_pagos = 0.0
                aditivos_evento = pd.DataFrame()

                if not aditivos_df.empty:
                    aditivos_evento = aditivos_df[
                        aditivos_df["evento_id"].astype(str) == str(evento_id)
                    ].copy()

                    if not aditivos_evento.empty:
                        total_aditivos_cliente = (
                            pd.to_numeric(
                                aditivos_evento["valor_cliente"],
                                errors="coerce",
                            )
                            .fillna(0)
                            .sum()
                        )
                        aditivos_pagos = aditivos_evento[
                            aditivos_evento["status"].str.lower() == "pago"
                        ]
                        if not aditivos_pagos.empty:
                            total_aditivos_pagos = (
                                pd.to_numeric(
                                    aditivos_pagos["valor_cliente"],
                                    errors="coerce",
                                )
                                .fillna(0)
                                .sum()
                            )

                valor_contrato_base = float(evento.get("venda", 0) or 0)
                custo_evento_total = float(evento.get("custo", 0) or 0)
                valor_contratado_total = valor_contrato_base + total_aditivos_cliente

                lucro_evento = max(0.0, valor_contratado_total - custo_evento_total)
                reserva_caixa_35 = lucro_evento * 0.35

                if not recebimentos.empty:
                    receb_evento = recebimentos[
                        recebimentos["evento_id"].astype(str) == str(evento_id)
                    ].copy()
                else:
                    receb_evento = pd.DataFrame()

                receb_contrato = (
                    pd.to_numeric(receb_evento["valor"], errors="coerce")
                    .fillna(0)
                    .sum()
                    if not receb_evento.empty
                    else 0.0
                )
                recebido = receb_contrato + total_aditivos_pagos
                a_receber = max(0.0, valor_contratado_total - recebido)

                if round(a_receber, 2) > 0:
                    eventos_com_pendencia += 1
                    status_fin = "🟡 PARCIAL" if recebido > 0 else "🔴 NÃO RECEBIDO"

                    st.markdown(f"### 🎉 {cliente}")
                    st.caption(
                        f"📅 **Data do Evento:** {data_evento} | **Situação:** {status_fin}"
                    )

                    m1, m2, m3, m4 = st.columns(4)
                    delta_venda = (
                        f"+ R$ {total_aditivos_cliente:,.2f} aditivos"
                        if total_aditivos_cliente > 0
                        else None
                    )

                    m1.metric(
                        "Valor Venda Total",
                        f"R$ {valor_contratado_total:,.2f}",
                        delta=delta_venda,
                    )
                    m2.metric("Custo Estimado", f"R$ {custo_evento_total:,.2f}")
                    m3.metric("Lucro Estimado", f"R$ {lucro_evento:,.2f}")
                    m4.metric(
                        "🛡️ Reserva Caixa PJ (35%)",
                        f"R$ {reserva_caixa_35:,.2f}",
                    )

                    c1, c2 = st.columns(2)
                    c1.metric("💵 Recebido", f"R$ {recebido:,.2f}")
                    c2.metric("🟡 A Receber", f"R$ {a_receber:,.2f}")

                    # REGISTRAR RECEBIMENTO
                    with st.expander(f"💰 Registrar Recebimento — {cliente}"):
                        col1, col2 = st.columns(2)
                        valor_recebimento = col1.number_input(
                            "Valor recebido",
                            min_value=0.0,
                            max_value=float(a_receber),
                            value=float(a_receber),
                            step=50.0,
                            key=f"p_valor_rec_{evento_id}",
                        )
                        data_recebimento = col2.date_input(
                            "Data do recebimento",
                            value=date.today(),
                            key=f"p_data_rec_{evento_id}",
                        )
                        forma = st.selectbox(
                            "Forma de pagamento",
                            ["Pix", "Dinheiro", "Cartão", "Transferência"],
                            key=f"p_forma_rec_{evento_id}",
                        )
                        data_prevista = st.date_input(
                            "📅 Data prevista para cobrança do restante",
                            value=date.today(),
                            key=f"p_data_prev_{evento_id}",
                        )
                        descricao = st.text_input(
                            "Descrição",
                            value=f"Recebimento evento {cliente}",
                            key=f"p_desc_rec_{evento_id}",
                        )

                        if st.button(
                            "💾 Confirmar Recebimento",
                            key=f"p_registrar_rec_{evento_id}",
                            use_container_width=True,
                        ):
                            if valor_recebimento <= 0:
                                st.warning("Informe um valor maior que zero.")
                            elif valor_recebimento > a_receber:
                                st.warning(
                                    "O valor não pode ser maior que o saldo a receber."
                                )
                            else:
                                try:
                                    supabase.table("recebimentos_eventos").insert({
                                        "evento_id": int(evento_id),
                                        "data_recebimento": str(data_recebimento),
                                        "data_prevista": str(data_prevista),
                                        "valor": valor_recebimento,
                                        "forma_pagamento": forma,
                                        "descricao": descricao,
                                        "status": "recebido",
                                    }).execute()

                                    supabase.table("Financeiro").insert({
                                        "data": str(data_recebimento),
                                        "tipo": "Entrada",
                                        "categoria": "Evento",
                                        "forma_pagamento": forma,
                                        "descricao": descricao,
                                        "valor": valor_recebimento,
                                    }).execute()

                                    st.toast(
                                        "✅ Recebimento registrado no Financeiro!",
                                        icon="🎉",
                                    )
                                    st.rerun()
                                except Exception as e:
                                    st.error(
                                        f"❌ Erro ao registrar recebimento: {e}"
                                    )

                    # REGISTRAR ADITIVOS
                    with st.expander(
                        f"➕ Aditivos / Horas Extras — {cliente}"
                    ):
                        with st.form(key=f"p_form_aditivo_{evento_id}"):
                            col_a, col_b = st.columns(2)
                            tipo_aditivo = col_a.selectbox(
                                "Tipo de Aditivo",
                                [
                                    "Hora Extra",
                                    "Quebra de Copos",
                                    "Consumo Extra",
                                    "Outros",
                                ],
                                key=f"p_tipo_adt_{evento_id}",
                            )
                            valor_cobrado_cliente = col_b.number_input(
                                "💰 Cobrado do Cliente (R$)",
                                min_value=0.0,
                                value=400.0,
                                step=50.0,
                                key=f"p_v_cli_{evento_id}",
                            )

                            col_st, col_fpg = st.columns(2)
                            status_aditivo = col_st.selectbox(
                                "Status",
                                ["Pago", "Pendente"],
                                key=f"p_st_adt_{evento_id}",
                            )
                            forma_pagto_aditivo = col_fpg.selectbox(
                                "Forma de Pagamento",
                                ["Pix", "Dinheiro", "Cartão", "Transferência"],
                                key=f"p_fpg_adt_{evento_id}",
                            )

                            obs_aditivo = st.text_input(
                                "Observação / Detalhes",
                                placeholder="Ex.: 2h extras contratadas no local",
                                key=f"p_obs_adt_{evento_id}",
                            )

                            btn_salvar_aditivo = st.form_submit_button(
                                "💾 Salvar Aditivo", use_container_width=True
                            )

                        if btn_salvar_aditivo:
                            agora_iso = datetime.now().isoformat()
                            data_hoje = str(datetime.now().date())

                            try:
                                payload_aditivo = {
                                    "evento_id": int(evento_id),
                                    "evento": str(cliente),
                                    "tipo": str(tipo_aditivo),
                                    "descricao": str(obs_aditivo),
                                    "valor_cliente": float(valor_cobrado_cliente),
                                    "valor_equipe": 0.0,
                                    "status": str(status_aditivo),
                                    "forma_pagamento": str(forma_pagto_aditivo)
                                    if status_aditivo == "Pago"
                                    else None,
                                    "data_pagamento": agora_iso
                                    if status_aditivo == "Pago"
                                    else None,
                                }
                                supabase.table("aditivos_evento").insert(
                                    payload_aditivo
                                ).execute()

                                if (
                                    status_aditivo == "Pago"
                                    and valor_cobrado_cliente > 0
                                ):
                                    supabase.table("Financeiro").insert({
                                        "data": data_hoje,
                                        "tipo": "Entrada",
                                        "categoria": f"Aditivo - {tipo_aditivo}",
                                        "forma_pagamento": str(forma_pagto_aditivo),
                                        "descricao": f"Aditivo ({tipo_aditivo}) - {cliente}",
                                        "valor": float(valor_cobrado_cliente),
                                    }).execute()

                                st.toast(
                                    "✅ Aditivo registrado com sucesso!",
                                    icon="➕",
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(
                                    f"❌ Erro ao registrar aditivo: {e}"
                                )

                    st.markdown("---")

            if eventos_com_pendencia == 0:
                st.success("🎉 Nenhum evento com saldo pendente no momento!")

    # =========================================================
    # 🎉 TAB 3: CONSULTA / HISTÓRICO EVENTOS
    # =========================================================
    with tab2:
        st.subheader("🎉 Histórico Financeiro dos Eventos")
        st.caption("Visão histórica dos recebimentos e fechamento de cada contrato.")

        eventos = pd.DataFrame(
            supabase.table("eventos")
            .select("*")
            .in_("status", ["aprovado", "finalizado", "concluido", "pago"])
            .order("data")
            .execute()
            .data
            or []
        )

        recebimentos = pd.DataFrame(
            supabase.table("recebimentos_eventos").select("*").execute().data or []
        )

        aditivos_df = pd.DataFrame(
            supabase.table("aditivos_evento").select("*").execute().data or []
        )

        if eventos.empty:
            st.info("Nenhum evento cadastrado.")
        else:
            for _, evento in eventos.iterrows():
                evento_id = evento["id"]
                cliente = evento.get("cliente", "Cliente")
                data_evento = evento.get("data", "")

                total_aditivos_cliente = 0.0
                total_aditivos_pagos = 0.0
                aditivos_evento = pd.DataFrame()

                if not aditivos_df.empty:
                    aditivos_evento = aditivos_df[
                        aditivos_df["evento_id"].astype(str) == str(evento_id)
                    ].copy()

                    if not aditivos_evento.empty:
                        total_aditivos_cliente = (
                            pd.to_numeric(
                                aditivos_evento["valor_cliente"],
                                errors="coerce",
                            )
                            .fillna(0)
                            .sum()
                        )
                        aditivos_pagos = aditivos_evento[
                            aditivos_evento["status"].str.lower() == "pago"
                        ]
                        if not aditivos_pagos.empty:
                            total_aditivos_pagos = (
                                pd.to_numeric(
                                    aditivos_pagos["valor_cliente"],
                                    errors="coerce",
                                )
                                .fillna(0)
                                .sum()
                            )

                valor_contrato_base = float(evento.get("venda", 0) or 0)
                custo_evento_total = float(evento.get("custo", 0) or 0)
                valor_contratado_total = valor_contrato_base + total_aditivos_cliente

                lucro_evento = max(0.0, valor_contratado_total - custo_evento_total)
                reserva_caixa_35 = lucro_evento * 0.35

                if not recebimentos.empty:
                    receb_evento = recebimentos[
                        recebimentos["evento_id"].astype(str) == str(evento_id)
                    ].copy()
                else:
                    receb_evento = pd.DataFrame()

                receb_contrato = (
                    pd.to_numeric(receb_evento["valor"], errors="coerce")
                    .fillna(0)
                    .sum()
                    if not receb_evento.empty
                    else 0.0
                )
                recebido = receb_contrato + total_aditivos_pagos
                a_receber = max(0.0, valor_contratado_total - recebido)

                if round(a_receber, 2) <= 0:
                    status_fin = "🟢 PAGO"
                elif recebido > 0:
                    status_fin = "🟡 PARCIAL"
                else:
                    status_fin = "🔴 NÃO RECEBIDO"

                st.markdown(f"### 🎉 {cliente}")
                st.caption(
                    f"📅 **Data do Evento:** {data_evento} | **Situação:** {status_fin}"
                )

                m1, m2, m3, m4 = st.columns(4)
                delta_venda = (
                    f"+ R$ {total_aditivos_cliente:,.2f} aditivos"
                    if total_aditivos_cliente > 0
                    else None
                )

                m1.metric(
                    "Valor Venda Total",
                    f"R$ {valor_contratado_total:,.2f}",
                    delta=delta_venda,
                )
                m2.metric("Custo Estimado", f"R$ {custo_evento_total:,.2f}")
                m3.metric("Lucro Estimado", f"R$ {lucro_evento:,.2f}")
                m4.metric(
                    "🛡️ Reserva Caixa PJ (35%)",
                    f"R$ {reserva_caixa_35:,.2f}",
                )

                c1, c2 = st.columns(2)
                c1.metric("💵 Recebido", f"R$ {recebido:,.2f}")
                c2.metric("🟡 A Receber", f"R$ {a_receber:,.2f}")

                if not aditivos_evento.empty:
                    st.markdown("#### ➕ Aditivos Registrados")
                    for idx, aditivo in aditivos_evento.iterrows():
                        tipo = aditivo.get("tipo", "Aditivo")
                        valor_adt = float(aditivo.get("valor_cliente", 0) or 0)
                        status_adt = aditivo.get("status", "Pendente")
                        obs = aditivo.get("descricao", "")
                        st.write(
                            f"• **{tipo}**: R$ {valor_adt:,.2f} | **Status:** {status_adt} | *{obs}*"
                        )

                if not receb_evento.empty:
                    st.markdown("#### 💳 Histórico de recebimentos")
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
                        historico["Valor"], errors="coerce"
                    )
                    st.dataframe(
                        historico, use_container_width=True, hide_index=True
                    )

                st.divider()

    # =========================================================
    # ➕ TAB 4: LANÇAMENTOS MANUAIS (AVULSOS, GAUSTOS E MELHORIAS)
    # =========================================================
    with tab4:
        st.subheader("➕ Lançamento Manual (Entradas Avulsas & Gastos/Melhorias)")
        st.caption(
            "Use este formulário para lançar saídas (gastos com estrutura, bebidas, investimentos, manutenção) "
            "e entradas manuais que NÃO vêm de contratos de eventos (aportes, rendimentos, etc.)."
        )

        with st.form("form_lancamento_manual", clear_on_submit=True):
            col_t1, col_t2 = st.columns(2)
            tipo_mov = col_t1.selectbox(
                "Tipo de Movimentação",
                ["Saída", "Entrada"],
                help="Selecione Saída para gastos/melhorias ou Entrada para receitas avulsas.",
            )
            data_mov = col_t2.date_input("Data da Transação", value=date.today())

            col_v1, col_v2 = st.columns(2)
            valor_mov = col_v1.number_input(
                "Valor (R$)", min_value=0.0, step=10.0, format="%.2f"
            )

            # Categorias adequadas ao tipo
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

            categoria_mov = col_v2.selectbox("Categoria", categorias_opcoes)

            col_f1, col_f2 = st.columns(2)
            forma_mov = col_f1.selectbox(
                "Forma de Pagamento / Recebimento",
                ["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Transferência / TED"],
            )
            descricao_mov = col_f2.text_input(
                "Descrição / Observação",
                placeholder="Ex.: Compra de novo balcão para bar, Anúncio Meta Ads, etc.",
            )

            btn_salvar_manual = st.form_submit_button(
                "💾 Salvar Lançamento", use_container_width=True
            )

            if btn_salvar_manual:
                if valor_mov <= 0:
                    st.warning("⚠️ Informe um valor maior que zero.")
                elif not descricao_mov.strip():
                    st.warning("⚠️ Forneça uma breve descrição do lançamento.")
                else:
                    try:
                        supabase.table("Financeiro").insert({
                            "data": str(data_mov),
                            "tipo": tipo_mov,
                            "categoria": categoria_mov,
                            "forma_pagamento": forma_mov,
                            "descricao": descricao_mov.strip(),
                            "valor": valor_mov,
                        }).execute()

                        st.toast("✅ Lançamento manual gravado no caixa!", icon="💾")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar lançamento: {e}")

    # =========================================================
    # 📄 TAB 5: EXTRATO E GESTÃO DE TRANSAÇÕES
    # =========================================================
    with tab5:
        st.subheader("📄 Extrato Completo do Caixa")
        st.caption("Consulte, filtre e remova qualquer movimentação financeira salva no banco.")

        res_extrato = (
            supabase.table("Financeiro")
            .select("*")
            .order("data", desc=True)
            .execute()
        )
        df_extrato = pd.DataFrame(res_extrato.data or [])

        if df_extrato.empty:
            st.info("Nenhuma transação cadastrada até o momento.")
        else:
            col_f1, col_f2 = st.columns(2)
            tipos_presentes = list(df_extrato["tipo"].unique())
            filtro_tipo = col_f1.multiselect(
                "Filtrar por Tipo", tipos_presentes, default=tipos_presentes
            )

            if "categoria" in df_extrato.columns:
                cats_presentes = [
                    c for c in df_extrato["categoria"].dropna().unique() if c
                ]
                filtro_cat = col_f2.multiselect(
                    "Filtrar por Categoria", cats_presentes, default=cats_presentes
                )
            else:
                filtro_cat = []

            # Aplicar filtros
            df_exibicao = df_extrato[df_extrato["tipo"].isin(filtro_tipo)]
            if filtro_cat and "categoria" in df_exibicao.columns:
                df_exibicao = df_exibicao[df_exibicao["categoria"].isin(filtro_cat)]

            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

            # Exclusão rápida por ID
            with st.expander("🗑️ Excluir lançamento incorreto"):
                id_excluir = st.number_input(
                    "Insira o ID do lançamento", min_value=1, step=1
                )
                if st.button("❌ Excluir do Banco de Dados", type="primary"):
                    try:
                        supabase.table("Financeiro").delete().eq("id", id_excluir).execute()
                        st.toast(f"✅ Lançamento #{id_excluir} removido!", icon="🗑️")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir registro: {e}")

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
