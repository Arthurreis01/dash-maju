import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# 1. CARREGAMENTO E TRATAMENTO DOS DADOS
# ----------------------------------------------------------------------------
def carregar_dados():
    """
    Carrega o dataset a partir do arquivo Excel 'data-maju.xlsx'.
    """
    caminho_arquivo = "data-maju.xlsx"
    try:
        df = pd.read_excel(caminho_arquivo, engine="openpyxl")
    except FileNotFoundError:
        st.error(f"Arquivo '{caminho_arquivo}' não encontrado.")
        st.stop()

    if "Unnamed: 0" not in df.columns:
        st.error("A coluna 'Unnamed: 0' não foi encontrada. Verifique o arquivo Excel.")
        st.stop()

    df = df.set_index("Unnamed: 0")
    df.index = df.index.str.strip().str.upper()  # Ensure consistency
    return df

# ----------------------------------------------------------------------------
# 2. CRIAÇÃO DO DASHBOARD COM STREAMLIT
# ----------------------------------------------------------------------------
def main():
    st.title("📊 Análise Financeira e de Desempenho - MajuBrownies")
    st.markdown("---")

    df = carregar_dados()

    # ----------------------------------------------------------------------------
    # INFORMATION BOXES WITH COMPARISON
    # ----------------------------------------------------------------------------
    total_revenue_2024 = df.loc["1. SOMA DAS VENDAS"].sum()
    total_revenue_2023 = df.loc["SOMA DAS VENDAS EM 2023"].sum()
    total_expenses = df.loc["2. SOMA DAS DESPESAS"].sum()
    average_margin = df.loc["7. MARGEM"].mean()

    st.markdown("### 🌟 Resumo dos Dados")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Receita Total 2024 (R$)",
            f"{total_revenue_2024:,.2f}",
            delta=f"{(total_revenue_2024 - total_revenue_2023):,.2f} a mais do que 2023"
        )
    with col2:
        st.metric("Despesas Totais (R$)", f"{total_expenses:,.2f}")
    with col3:
        st.metric("Média da Margem (%)", f"{average_margin:.2f}%")
    st.markdown("---")

    # ----------------------------------------------------------------------------
    # COMPARAÇÃO ENTRE ANOS: SOMA DAS VENDAS EM 2022, 2023, E 2024
    # ----------------------------------------------------------------------------
    st.markdown("### 📈 Comparação Entre Anos: Vendas em 2022, 2023 e 2024")
    anos_disponiveis = ["SOMA DAS VENDAS EM 2022", "SOMA DAS VENDAS EM 2023", "1. SOMA DAS VENDAS"]
    anos_presentes = [ano for ano in anos_disponiveis if ano in df.index]
    df_anos = df.loc[anos_presentes].T
    df_anos.reset_index(inplace=True)
    df_anos.columns = ["Mes", "2022", "2023", "2024"]

    fig_anos = go.Figure()
    for year in df_anos.columns[1:]:
        fig_anos.add_trace(go.Bar(
            x=df_anos["Mes"],
            y=df_anos[year],
            name=year,
            text=df_anos[year],
            textposition="outside"
        ))

    fig_anos.update_layout(
        barmode="group",
        title="Comparação de Vendas: 2022, 2023 e 2024",
        xaxis_title="Mês",
        yaxis_title="Vendas (R$)",
        height=600,
    )
    st.plotly_chart(fig_anos, use_container_width=True)

    # ----------------------------------------------------------------------------
    # TENDÊNCIA DE VENDAS E LUCRO CONSOLIDADO
    # ----------------------------------------------------------------------------
    st.markdown("### 🔄 Tendência de Vendas e Lucro Consolidado")
    df_receita_lucro = df.loc[["1. SOMA DAS VENDAS", "6. LUCRO/PREJUIZO CONSOLIDADO"]].T
    df_receita_lucro.reset_index(inplace=True)
    df_receita_lucro.columns = ["Mes", "Receita_Mensal", "Lucro_Consolidado"]
    df_receita_lucro["Ponto_de_Equilibrio"] = 2000

    fig_vendas_lucro = go.Figure()
    fig_vendas_lucro.add_trace(go.Bar(
        x=df_receita_lucro["Mes"],
        y=df_receita_lucro["Receita_Mensal"],
        name="Receita Mensal",
        text=df_receita_lucro["Receita_Mensal"],
        textposition="outside"
    ))
    fig_vendas_lucro.add_trace(go.Scatter(
        x=df_receita_lucro["Mes"],
        y=df_receita_lucro["Lucro_Consolidado"],
        name="Lucro Consolidado",
        mode="lines+markers+text",
        text=df_receita_lucro["Lucro_Consolidado"],
        textposition="top center",
        line=dict(color="yellow")
    ))
    fig_vendas_lucro.add_trace(go.Scatter(
        x=df_receita_lucro["Mes"],
        y=df_receita_lucro["Ponto_de_Equilibrio"],
        name="Ponto de Equilíbrio",
        mode="lines",
        line=dict(dash="dash", color="red")
    ))

    fig_vendas_lucro.update_layout(
        title="Tendência de Vendas e Lucro Consolidado",
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        height=600,
    )
    st.plotly_chart(fig_vendas_lucro, use_container_width=True)

    # ----------------------------------------------------------------------------
    # ANÁLISE DE MARGENS
    # ----------------------------------------------------------------------------
    st.markdown("### 📉 Análise de Margens")
    df_margens = df.loc[["7. MARGEM"]].T
    df_margens.reset_index(inplace=True)
    df_margens.columns = ["Mes", "Margem"]

    fig_margens = go.Figure()
    fig_margens.add_trace(go.Scatter(
        x=df_margens["Mes"],
        y=df_margens["Margem"],
        mode="lines+markers+text",
        name="Margem (%)",
        text=df_margens["Margem"],
        textposition="top center"
    ))

    fig_margens.update_layout(
        title="Análise de Margens",
        xaxis_title="Mês",
        yaxis_title="Margem (%)",
        height=600,
    )
    st.plotly_chart(fig_margens, use_container_width=True)

    # ----------------------------------------------------------------------------
    # RECEITA DETALHADA
    # ----------------------------------------------------------------------------
    st.markdown("### 📊 Análise Detalhada das Receitas")

    # Define revenue lines
    revenue_lines = ["1.1  VENDA EMPRESA", "1.2  VENDA COELHO", "1.5  VENDA ENCOMENDADAS"]

    # Check which lines are present
    revenues_present = [line for line in revenue_lines if line in df.index]

    if revenues_present:
        # Filter and prepare data for plotting
        df_revenues = df.loc[revenues_present].T
        df_revenues.reset_index(inplace=True)
        df_revenues.columns = ["Mes"] + revenues_present

        # Create the revenue details chart
        fig_revenues_detail = go.Figure()
        for column in df_revenues.columns[1:]:
            fig_revenues_detail.add_trace(go.Bar(
                x=df_revenues["Mes"],
                y=df_revenues[column],
                name=column,
                text=df_revenues[column],
                textposition="outside"
            ))

        fig_revenues_detail.update_layout(
            title="Análise Detalhada das Receitas",
            xaxis_title="Mês",
            yaxis_title="Valor (R$)",
            barmode="stack",
            height=600,
        )
        st.plotly_chart(fig_revenues_detail, use_container_width=True)
    else:
        st.error("Nenhuma das linhas de receita detalhada foi encontrada no conjunto de dados.")



    # ----------------------------------------------------------------------------
    # DESPESAS DETALHADAS
    # ----------------------------------------------------------------------------
    st.markdown("### 💰 Análise Detalhada das Despesas")
    expense_lines = [
        "2.1 DESPESA COM MERCADORIAS", "2.2 DESPESA COM EMBALAGENS", "3. DEPESAS GERAIS E ADMNIST.",
        "3.1 MARIANA", "3.2 ADESIVO", "3.3 UBER", "3.4 ALUGUEL DE CARRO",
        "3.5 ÔNIBUS", "3.6 TARIFA BANCO", "3.6 DANS MEI"
    ]
    expenses_present = [line for line in expense_lines if line in df.index]
    if expenses_present:
        df_expenses = df.loc[expenses_present].T
        df_expenses.reset_index(inplace=True)
        df_expenses.columns = ["Mes"] + expenses_present

        fig_expenses_detail = go.Figure()
        for column in df_expenses.columns[1:]:
            fig_expenses_detail.add_trace(go.Bar(
                x=df_expenses["Mes"],
                y=df_expenses[column],
                name=column,
                text=df_expenses[column],
                textposition="outside"
            ))

        fig_expenses_detail.update_layout(
            title="Análise Detalhada das Despesas",
            xaxis_title="Mês",
            yaxis_title="Valor (R$)",
            barmode="stack",
            height=600,
        )
        st.plotly_chart(fig_expenses_detail, use_container_width=True)
    else:
        st.error("Nenhuma das linhas de despesa detalhada foi encontrada no conjunto de dados.")

    # ----------------------------------------------------------------------------
    # DISPLAY SPREADSHEET
    # ----------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📋 Planilha de Dados")
    st.dataframe(df)

# ----------------------------------------------------------------------------
# EXECUÇÃO
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
