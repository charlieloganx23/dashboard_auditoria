import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Painel Auditoria - Drill-down", layout="wide")

# Funções utilitárias
def formatar_moeda(valor):
    if pd.isnull(valor) or valor == 0:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Carregamento dos dados
@st.cache_data
def load_data():
    df_fin = pd.read_csv('Ação Financeiro_renomeado.csv')
    df_fis = pd.read_csv('Ação Fisico_renomeado.csv')
    df_prog = pd.read_csv('Programa_renomeado.csv')
    df_acao = pd.read_csv('Ação_renomeado.csv')
    df_rest = pd.read_csv('Restrição_renomeado.csv')
    return df_fin, df_fis, df_prog, df_acao, df_rest

df_fin, df_fis, df_prog, df_acao, df_rest = load_data()

# Mapeamento Nome_orgao
uo_to_nome_orgao = df_prog[['uo_codigo', 'Nome_orgao']].drop_duplicates().set_index('uo_codigo')['Nome_orgao'].to_dict()
for df in [df_fin, df_fis, df_rest]:
    if 'Nome_orgao' not in df.columns and 'uo_codigo' in df.columns:
        df['Nome_orgao'] = df['uo_codigo'].map(uo_to_nome_orgao)

# Estado de navegação do drill-down
if 'drill_level' not in st.session_state:
    st.session_state.drill_level = 'orgao'
if 'drill_value' not in st.session_state:
    st.session_state.drill_value = None

# Funções de exibição detalhada
def exibir_detalhes_orgao(orgao):
    st.subheader(f"🏢 Órgão: {orgao}")
    df_fin_o = df_fin[df_fin['Nome_orgao'] == orgao]
    df_prog_o = df_prog[df_prog['Nome_orgao'] == orgao]
    st.write(f"Total de Programas: {df_prog_o['programa_codigo'].nunique()}")
    st.write(f"Total Empenhado: {formatar_moeda(df_fin_o['valor_empenhado'].sum())}")
    # Histórico financeiro
    if not df_fin_o.empty:
        df_hist = df_fin_o.groupby(['ano', 'quadrimestre']).agg({'valor_empenhado':'sum','valor_liquidado_ano':'sum'}).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_hist['quadrimestre'], y=df_hist['valor_empenhado'], name='Empenhado'))
        fig.add_trace(go.Bar(x=df_hist['quadrimestre'], y=df_hist['valor_liquidado_ano'], name='Liquidado'))
        fig.update_layout(barmode='group', title="Histórico Financeiro por Quadrimestre")
        st.plotly_chart(fig, use_container_width=True)
    # Restrições
    df_rest_o = df_rest[df_rest['Nome_orgao'] == orgao]
    if not df_rest_o.empty:
        st.markdown("### ⚠️ Restrições do Órgão")
        st.dataframe(df_rest_o[['restricao_codigo','descricao','justificativa','sugestao_melhoria']])
    # Listar programas clicáveis
    st.markdown("### 📋 Programas do Órgão")
    for _, row in df_prog_o.iterrows():
        if st.button(f"Ver Programa {row['programa_codigo']} - {row['programa_nome']}", key=f"prog_{row['programa_codigo']}"):
            st.session_state.drill_level = 'programa'
            st.session_state.drill_value = row['programa_codigo']
            st.experimental_rerun()

def exibir_detalhes_programa(cod_programa):
    prog = df_prog[df_prog['programa_codigo'] == cod_programa].iloc[0]
    st.subheader(f"📁 Programa: {prog['programa_nome']}")
    st.write(f"Denominação: {prog['programa_denominacao']}")
    df_fin_p = df_fin[df_fin['programa_codigo'] == cod_programa]
    st.write(f"Total Empenhado: {formatar_moeda(df_fin_p['valor_empenhado'].sum())}")
    # Histórico financeiro
    if not df_fin_p.empty:
        df_hist = df_fin_p.groupby(['ano', 'quadrimestre']).agg({'valor_empenhado':'sum','valor_liquidado_ano':'sum'}).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_hist['quadrimestre'], y=df_hist['valor_empenhado'], name='Empenhado'))
        fig.add_trace(go.Bar(x=df_hist['quadrimestre'], y=df_hist['valor_liquidado_ano'], name='Liquidado'))
        fig.update_layout(barmode='group', title="Histórico Financeiro por Quadrimestre")
        st.plotly_chart(fig, use_container_width=True)
    # Restrições
    df_rest_p = df_rest[df_rest['programa_codigo'] == cod_programa]
    if not df_rest_p.empty:
        st.markdown("### ⚠️ Restrições do Programa")
        st.dataframe(df_rest_p[['restricao_codigo','descricao','justificativa','sugestao_melhoria']])
    # Listar ações clicáveis
    st.markdown("### 🎯 Ações do Programa")
    acoes = df_acao[df_acao['programa_codigo'] == cod_programa]
    for _, row in acoes.iterrows():
        if st.button(f"Ver Ação {row['acao_codigo']} - {row['finalidade'][:40]}", key=f"acao_{row['acao_codigo']}"):
            st.session_state.drill_level = 'acao'
            st.session_state.drill_value = row['acao_codigo']
            st.experimental_rerun()
    if st.button("⬅️ Voltar para Órgão"):
        st.session_state.drill_level = 'orgao'
        st.session_state.drill_value = prog['Nome_orgao']
        st.experimental_rerun()

def exibir_detalhes_acao(cod_acao):
    acao = df_acao[df_acao['acao_codigo'] == cod_acao].iloc[0]
    st.subheader(f"🎯 Ação: {acao['finalidade']}")
    st.write(f"Situação: {acao['situacao_acao']}")
    df_fin_a = df_fin[df_fin['acao_codigo'] == cod_acao]
    st.write(f"Total Empenhado: {formatar_moeda(df_fin_a['valor_empenhado'].sum())}")
    # Histórico financeiro
    if not df_fin_a.empty:
        df_hist = df_fin_a.groupby(['ano', 'quadrimestre']).agg({'valor_empenhado':'sum','valor_liquidado_ano':'sum'}).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_hist['quadrimestre'], y=df_hist['valor_empenhado'], name='Empenhado'))
        fig.add_trace(go.Bar(x=df_hist['quadrimestre'], y=df_hist['valor_liquidado_ano'], name='Liquidado'))
        fig.update_layout(barmode='group', title="Histórico Financeiro por Quadrimestre")
        st.plotly_chart(fig, use_container_width=True)
    # Restrições
    df_rest_a = df_rest[df_rest['acao_codigo'] == cod_acao]
    if not df_rest_a.empty:
        st.markdown("### ⚠️ Restrições da Ação")
        st.dataframe(df_rest_a[['restricao_codigo','descricao','justificativa','sugestao_melhoria']])
    if st.button("⬅️ Voltar para Programa"):
        st.session_state.drill_level = 'programa'
        st.session_state.drill_value = acao['programa_codigo']
        st.experimental_rerun()

# Interface principal
st.title("Painel de Auditoria - Drill-down Interativo")

if st.session_state.drill_level == 'orgao':
    st.markdown("## 🏢 Clique em um órgão para ver detalhes")
    orgaos = df_fin['Nome_orgao'].dropna().unique()
    for orgao in orgaos:
        if st.button(f"Ver Órgão: {orgao}", key=f"orgao_{orgao}"):
            st.session_state.drill_value = orgao
            st.session_state.drill_level = 'orgao_detalhe'
            st.experimental_rerun()
    if st.session_state.drill_value and st.session_state.drill_level == 'orgao_detalhe':
        exibir_detalhes_orgao(st.session_state.drill_value)

elif st.session_state.drill_level == 'programa':
    exibir_detalhes_programa(st.session_state.drill_value)

elif st.session_state.drill_level == 'acao':
    exibir_detalhes_acao(st.session_state.drill_value)