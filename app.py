import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ellosystem - Gestão de Bares", layout="wide", page_icon="🍸")

# --- CONEXÃO COM BANCO DE DADOS ---
conn = sqlite3.connect("ellosystem.db", check_same_thread=False)
cursor = conn.cursor()

def inicializar_sistema():
    # Tabelas de Precificação
    for tabela in ["precos_bebidas", "precos_insumos", "precos_artesanais"]:
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {tabela}(
            id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, nome TEXT,
            quantidade REAL, preco REAL, uso REAL, rendimento REAL, custo REAL
        )""")
    
    # Tabela de Receitas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receitas(
        id INTEGER PRIMARY KEY AUTOINCREMENT, drink TEXT, ingrediente TEXT, 
        quantidade REAL, unidade TEXT
    )""")

    # Tabela de Itens Fixos de Logística (O que sempre deve ir pro bar)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itens_logistica_fixos(
        id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT, qtd_sugerida TEXT
    )""")

    # Tabela de Orçamentos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orcamentos_eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome_evento TEXT, data_evento TEXT, 
        local TEXT, convidados INTEGER, custo_total REAL, status TEXT, 
        checklist_texto TEXT, staff_contagem INTEGER
    )""")

    # Financeiro e Vendas
    cursor.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, valor_total REAL, evento TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS gastos_extras (id INTEGER PRIMARY KEY AUTOINCREMENT, categoria TEXT, valor REAL, data TEXT)")
    
    conn.commit()

inicializar_sistema()

# --- NAVEGAÇÃO ---
menu = st.sidebar.radio("Menu Principal", 
    ["📊 Dashboard", "💰 Precificação", "🍹 Receitas", "📑 Orçamentos & Logística", "⚙️ Configurações"])

# --- FUNÇÕES DE FORMATAÇÃO ---
def format_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 1. DASHBOARD (COM FLASHCARDS) ---
if menu == "📊 Dashboard":
    st.title("Painel de Controle Ellosystem")
    
    df_vendas = pd.read_sql("SELECT valor_total FROM vendas", conn)
    df_gastos = pd.read_sql("SELECT valor FROM gastos_extras", conn)
    num_eventos = len(df_vendas)
    
    total_vendas = df_vendas['valor_total'].sum() if not df_vendas.empty else 0.0
    total_gastos = df_gastos['valor'].sum() if not df_gastos.empty else 0.0
    lucro_real = total_vendas - total_gastos
    ticket_medio = total_vendas / num_eventos if num_eventos > 0 else 0.0

    # FLASHCARDS (MÉTRICAS)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Faturamento Total", format_moeda(total_vendas))
    c2.metric("📉 Custos/Gastos", format_moeda(total_gastos), delta_color="inverse")
    c3.metric("💎 Lucro Líquido", format_moeda(lucro_real))
    c4.metric("📅 Eventos Feitos", num_eventos)

    st.divider()
    
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.subheader("🚀 Performance")
        st.metric("Ticket Médio por Evento", format_moeda(ticket_medio))
    
    with col_inf2:
        st.subheader("📝 Últimos Lançamentos")
        if num_eventos > 0:
            st.write(pd.read_sql("SELECT evento, valor_total FROM vendas ORDER BY id DESC LIMIT 5", conn))

# --- 2. PRECIFICAÇÃO (KG/ML CORRIGIDOS) ---
elif menu == "💰 Precificação":
    st.title("Gestão de Custos")
    t_beb, t_ins = st.tabs(["🍾 Bebidas", "🍋 Insumos (KG)"])
    
    with t_beb:
        with st.form("cad_beb"):
            nome = st.text_input("Marca/Nome")
            vol = st.number_input("Volume Garrafa (ml)", value=750.0)
            prc = st.number_input("Preço Garrafa", value=0.0)
            dose = st.number_input("Dose Padrão (ml)", value=50.0)
            if st.form_submit_button("Salvar Bebida"):
                custo = (prc / vol) * dose
                cursor.execute("INSERT INTO precos_bebidas (nome, quantidade, preco, uso, custo) VALUES (?,?,?,?,?)",
                               (nome.lower(), vol, prc, dose, custo))
                conn.commit()
                st.success("Cadastrado!")

    with t_ins:
        with st.form("cad_ins"):
            nome_i = st.text_input("Fruta/Insumo")
            prc_kg = st.number_input("Preço do KG", value=0.0)
            uso_g = st.number_input("Gramas por Drink", value=20.0)
            if st.form_submit_button("Salvar Insumo"):
                custo_i = (prc_kg / 1000) * uso_g
                cursor.execute("INSERT INTO precos_insumos (nome, quantidade, preco, uso, custo) VALUES (?,?,?,?,?)",
                               (nome_i.lower(), 1.0, prc_kg, uso_g, custo_i))
                conn.commit()
                st.success("Cadastrado!")

# --- 3. ORÇAMENTOS & LOGÍSTICA (A LÓGICA DE 1/25 PESSOAS) ---
elif menu == "📑 Orçamentos & Logística":
    st.title("Eventos e Logística")
    aba_n, aba_op = st.tabs(["🆕 Novo Orçamento", "🚚 Operação & Checklist"])
    
    with aba_n:
        with st.form("orc_form"):
            ev = st.text_input("Nome do Evento")
            pax = st.number_input("Convidados", value=50)
            staff = -(-pax // 25) # Regra 1 barman a cada 25 pessoas
            st.info(f"Staff Sugerido: {staff} profissionais")
            
            custo_est = st.number_input("Custo de Bebidas/Insumos", value=0.0)
            margem = st.slider("Margem de Lucro %", 50, 300, 100)
            venda = custo_est * (1 + (margem/100))
            
            if st.form_submit_button("Gerar Orçamento"):
                # Puxa itens fixos das configurações
                fixos = pd.read_sql("SELECT item, qtd_sugerida FROM itens_logistica_fixos", conn)
                check_base = f"*CHECKLIST - {ev}*\nStaff: {staff} barmans\n\n"
                for _, r in fixos.iterrows():
                    check_base += f"☐ {r['item']} ({r['qtd_sugerida']})\n"
                
                cursor.execute("""INSERT INTO orcamentos_eventos 
                (nome_evento, convidados, custo_total, status, checklist_texto, staff_contagem) 
                VALUES (?,?,?,?,?,?)""", (ev, pax, venda, "Pendente", check_base, staff))
                conn.commit()
                st.success("Orçamento Pendente Criado!")

    with aba_op:
        df_op = pd.read_sql("SELECT * FROM orcamentos_eventos WHERE status != 'Finalizado'", conn)
        if not df_op.empty:
            sel_ev = st.selectbox("Evento", df_op['nome_evento'])
            dados = df_op[df_op['nome_evento'] == sel_ev].iloc[0]
            
            # CHECKLIST EDITÁVEL ANTES DO ENVIO
            check_edit = st.text_area("Checklist (Pode editar agora):", value=dados['checklist_texto'], height=250)
            
            c1, c2 = st.columns(2)
            # Link WhatsApp
            link = f"https://wa.me/?text={urllib.parse.quote(check_edit)}"
            c1.markdown(f"[📲 Enviar WhatsApp]({link})")
            
            if c2.button("🏁 Finalizar Evento (Recebido)"):
                cursor.execute("UPDATE orcamentos_eventos SET status='Finalizado' WHERE id=?", (dados['id'],))
                cursor.execute("INSERT INTO vendas (data, valor_total, evento) VALUES (?,?,?)",
                               (datetime.now().strftime("%Y-%m-%d"), dados['custo_total'], sel_ev))
                conn.commit()
                st.rerun()

# --- 4. CONFIGURAÇÕES (ITENS FIXOS) ---
elif menu == "⚙️ Configurações":
    st.title("Configurações do Bar")
    st.subheader("🎒 Itens que NUNCA podem faltar (Logística)")
    with st.form("f_fixo"):
        it = st.text_input("Material (ex: Coqueteleira, Gelo, Tapete)")
        qt = st.text_input("Sugestão de Qtd (ex: 2 por Barman)")
        if st.form_submit_button("Adicionar"):
            cursor.execute("INSERT INTO itens_logistica_fixos (item, qtd_sugerida) VALUES (?,?)", (it, qt))
            conn.commit()
            st.rerun()
    
    st.table(pd.read_sql("SELECT item, qtd_sugerida FROM itens_logistica_fixos", conn))
