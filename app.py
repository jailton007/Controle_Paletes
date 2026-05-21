import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(page_title="Controle de Paletes e Logística", layout="centered")


# Função para inicializar as variáveis de contagem no sistema
def inicializar_estoque():
    variaveis = [
        "retrabalho_total",
        "pnc",
        "avarias",
        "carros_amarrados",
        "carros_desamarrados",
        "devolvidos",
        "pulmao",
    ]
    for var in variaveis:
        if var not in st.session_state:
            st.session_state[var] = 0

    # Inicializar os 10 Fast Works
    for i in range(1, 11):
        if f"fast_work_{i}" not in st.session_state:
            st.session_state[f"fast_work_{i}"] = 0

    # Inicializar os Blocados (Dinâmico)
    if "blocados" not in st.session_state:
        st.session_state["blocados"] = {"Blocado A": 0, "Blocado B": 0}


inicializar_estoque()

st.title("📊 Controle Operacional de Paletes")
st.write("Registre e conte as movimentações do pátio e galpão de forma simples.")

# --- SEÇÃO 1: CONTAGEM GERAL ---
st.header("1. Indicadores Gerais")


# Função auxiliar para criar botões de + e -
def secao_contador(label, key):
    st.subheader(label)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("➖", key=f"dec_{key}"):
            if st.session_state[key] > 0:
                st.session_state[key] -= 1
    with col2:
        st.metric(label="Total", value=st.session_state[key])
    with col3:
        if st.button("➕", key=f"inc_{key}"):
            st.session_state[key] += 1
    st.markdown("---")


secao_contador("Paletes para Retrabalho (Geral)", "retrabalho_total")
secao_contador("Paletes para PNC (Produto Não Conforme)", "pnc")
secao_contador("Quantidade de Avarias", "avarias")
secao_contador("Carros Amarrados", "carros_amarrados")
secao_contador("Carros Desamarrados", "carros_desamarrados")
secao_contador("Paletes Devolvidos", "devolvidos")
secao_contador("Paletes no Pulmão", "pulmao")

# --- SEÇÃO 2: CONTROLAR BLOCADOS ---
st.header("2. Paletes por Blocado")

# Adicionar um novo blocado se necessário
novo_blocado = st.text_input("Adicionar novo Blocado (Ex: Blocado C):")
if st.button("Adicionar Blocado") and novo_blocado:
    if novo_blocado not in st.session_state["blocados"]:
        st.session_state["blocados"][novo_blocado] = 0
        st.rerun()

# Listar e contar cada blocado
for blocado in list(st.session_state["blocados"].keys()):
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.write(f"**{blocado}**")
    with col2:
        if st.button("➖", key=f"dec_{blocado}"):
            if st.session_state["blocados"][blocado] > 0:
                st.session_state["blocados"][blocado] -= 1
    with col3:
        st.write(f"{st.session_state['blocados'][blocado]} paletes")
    with col4:
        if st.button("➕", key=f"inc_{blocado}"):
            st.session_state["blocados"][blocado] += 1

st.markdown("---")

# --- SEÇÃO 3: FAST WORKS ---
st.header("3. Retrabalho por Fast Work (1 a 10)")

cols_fw = st.columns(2)
for i in range(1, 11):
    # Divide os 10 fast works em duas colunas na tela para ficar organizado
    col_atual = cols_fw[0] if i <= 5 else cols_fw[1]
    with col_atual:
        st.session_state[f"fast_work_{i}"] = st.number_input(
            f"Fast Work {i}", min_value=0, value=st.session_state[f"fast_work_{i}"]
        )

st.markdown("---")

# --- SEÇÃO 4: EXPORTAR DADOS ---
st.header("4. Fechamento e Relatório")

if st.button("📊 Gerar Relatório / Planilha Excel"):
    # Organizando os dados gerais e fast works
    dados = {
        "Indicador": [
            "Retrabalho Geral",
            "PNC",
            "Avarias",
            "Carros Amarrados",
            "Carros Desamarrados",
            "Devolvidos",
            "Pulmão",
        ],
        "Quantidade": [
            st.session_state["retrabalho_total"],
            st.session_state["pnc"],
            st.session_state["avarias"],
            st.session_state["carros_amarrados"],
            st.session_state["carros_desamarrados"],
            st.session_state["devolvidos"],
            st.session_state["pulmao"],
        ],
    }

    # Adicionando os blocados na planilha
    for b, qtd in st.session_state["blocados"].items():
        dados["Indicador"].append(f"Estoque - {b}")
        dados["Quantidade"].append(qtd)

    # Adicionando os Fast Works na planilha
    for i in range(1, 11):
        dados["Indicador"].append(f"Fast Work {i} (Retrabalho)")
        dados["Quantidade"].append(st.session_state[f"fast_work_{i}"])

    df = pd.DataFrame(dados)


    # Convertendo para excel para o usuário baixar
    @st.cache_data
    def convert_df(df_para_converter):
        return df_para_converter.to_csv(index=False).encode("utf-8")

    csv = convert_df(df)

    st.success("Relatório gerado com sucesso!")
    st.dataframe(df)

    st.download_button(
        label="📥 Baixar Planilha (CSV/Excel)",
        data=csv,
        file_name="relatorio_paletes.csv",
        mime="text/csv",
    )

# Botão de Reset
if st.button("⚠️ Zerar Todas as Contagens (Novo Turno)"):
    for key in list(st.session_state.keys()):
        if key.startswith("fast_work_") or key in [
            "retrabalho_total",
            "pnc",
            "avarias",
            "carros_amarrados",
            "carros_desamarrados",
            "devolvidos",
            "pulmao",
        ]:
            st.session_state[key] = 0
    st.session_state["blocados"] = {"Blocado A": 0, "Blocado B": 0}
    st.rerun()