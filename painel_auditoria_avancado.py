import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
from datetime import datetime

st.set_page_config(
    page_title="Painel Avançado de Auditoria Financeira",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .alert-warning {background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 0.25rem; padding: 0.75rem; margin: 1rem 0;}
    .alert-danger {background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 0.25rem; padding: 0.75rem; margin: 1rem 0;}
    .alert-success {background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 0.25rem; padding: 0.75rem; margin: 1rem 0;}
    .risk-panel {background-color: #f8f9fa; border-left: 4px solid #dc3545; padding: 1rem; margin: 1rem 0;}
    .governance-panel {background-color: #e7f3ff; border-left: 4px solid #007bff; padding: 1rem; margin: 1rem 0;}
    @media (max-width: 768px) {.stColumns > div {min-width: 100% !important;}}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df_fin = pd.read_csv('Ação Financeiro_renomeado.csv')
        df_fis = pd.read_csv('Ação Fisico_renomeado.csv')
        df_prog = pd.read_csv('Programa_renomeado.csv')
        df_acao = pd.read_csv('Ação_renomeado.csv')
        df_rest = pd.read_csv('Restrição_renomeado.csv')
        df_ind = pd.read_csv('Avaliação Indicador_renomeado.csv')
        return df_fin, df_fis, df_prog, df_acao, df_rest, df_ind
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None, None, None, None, None

@st.cache_data
def detectar_outliers(df, colunas, threshold=3):
    outliers_df = df.copy()
    for col in colunas:
        if col in df.columns and df[col].dtype in ['int64', 'float64']:
            media = df[col].mean()
            std = df[col].std()
            if std > 0:
                outliers_df[f'outlier_{col}'] = np.abs(df[col] - media) > threshold * std
            else:
                outliers_df[f'outlier_{col}'] = False
    return outliers_df

def analisar_riscos(df_fin, df_fis, df_rest, df_conform):
    riscos = []
    # Risco 1: Execução física sem financeira
    if not df_conform.empty and 'status' in df_conform.columns:
        fis_sem_fin = df_conform[df_conform['status'] == "Físico sem Financeiro"]
        if not fis_sem_fin.empty:
            riscos.append({
                'tipo': 'Alto',
                'descricao': f'{len(fis_sem_fin)} ações com execução física mas sem execução financeira',
                'impacto': 'Possível irregularidade na execução orçamentária',
                'dados': fis_sem_fin
            })
    # Risco 2: Restos a pagar crescentes
    if 'valor_restos_a_pagar' in df_fin.columns:
        rp_alto = df_fin[df_fin['valor_restos_a_pagar'] > df_fin['valor_restos_a_pagar'].quantile(0.9)]
        if not rp_alto.empty:
            riscos.append({
                'tipo': 'Médio',
                'descricao': f'{len(rp_alto)} registros com restos a pagar no percentil 90%',
                'impacto': 'Possível comprometimento do orçamento futuro',
                'dados': rp_alto
            })
    # Risco 3: Concentração de despesas
    concentracao = df_fin.groupby('programa_codigo')['valor_pago'].sum()
    total_pago = concentracao.sum()
    if total_pago > 0:
        top_programa = concentracao.max() / total_pago
        if top_programa > 0.3:
            riscos.append({
                'tipo': 'Baixo',
                'descricao': f'Um programa concentra {top_programa:.1%} dos pagamentos',
                'impacto': 'Concentração excessiva de recursos',
                'dados': concentracao.head(5)
            })
    # Risco 4: Restrições recorrentes
    if not df_rest.empty:
        rest_recorrentes = df_rest['restricao_codigo'].value_counts()
        if len(rest_recorrentes) > 0 and rest_recorrentes.iloc[0] > 5:
            riscos.append({
                'tipo': 'Médio',
                'descricao': f'Restrição {rest_recorrentes.index[0]} aparece {rest_recorrentes.iloc[0]} vezes',
                'impacto': 'Problema sistêmico não resolvido',
                'dados': rest_recorrentes.head(5)
            })
    return riscos

df_fin, df_fis, df_prog, df_acao, df_rest, df_ind = load_data()
if df_fin is None:
    st.stop()

uo_to_nome_orgao = df_prog[['uo_codigo', 'Nome_orgao']].drop_duplicates().set_index('uo_codigo')['Nome_orgao'].to_dict()
for df in [df_fin, df_fis, df_rest]:
    if 'Nome_orgao' not in df.columns and 'uo_codigo' in df.columns:
        df['Nome_orgao'] = df['uo_codigo'].map(uo_to_nome_orgao)

st.sidebar.title("🔍 Filtros de Auditoria Avançada")
st.sidebar.subheader("📁 Upload de Arquivos")
uploaded_file = st.sidebar.file_uploader("Carregar arquivo auxiliar", type=['csv', 'xlsx'])
if uploaded_file:
    st.sidebar.success("Arquivo carregado com sucesso!")

anos = sorted(df_fin['ano'].unique())
anos_selecionados = st.sidebar.multiselect("📅 Ano(s)", anos, default=anos[-2:])

quadrimestres = sorted(df_fin['quadrimestre'].unique())
quadrimestres_selecionados = st.sidebar.multiselect("📊 Quadrimestre(s)", quadrimestres, default=quadrimestres)

orgaos_disponiveis = sorted(df_prog['Nome_orgao'].dropna().unique())
orgaos_selecionados = st.sidebar.multiselect("🏢 Órgão", orgaos_disponiveis)

valor_minimo = st.sidebar.number_input("💰 Valor mínimo para análise (R$)", min_value=0, value=100000, step=10000)
threshold_outlier = st.sidebar.slider("🎯 Sensibilidade para outliers (desvios padrão)", 1.0, 5.0, 3.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.info("💡 Painel com recursos avançados de auditoria e detecção de anomalias.")

df_fin_filtrado = df_fin[
    df_fin['ano'].isin(anos_selecionados) &
    df_fin['quadrimestre'].isin(quadrimestres_selecionados) &
    (df_fin['valor_empenhado'] >= valor_minimo)
]
df_fis_filtrado = df_fis[
    df_fis['ano'].isin(anos_selecionados) &
    df_fis['quadrimestre'].isin(quadrimestres_selecionados)
]
df_rest_filtrado = df_rest[
    df_rest['ano'].isin(anos_selecionados) &
    df_rest['quadrimestre'].isin(quadrimestres_selecionados)
]

if orgaos_selecionados:
    df_fin_filtrado = df_fin_filtrado[df_fin_filtrado['Nome_orgao'].isin(orgaos_selecionados)]
    df_fis_filtrado = df_fis_filtrado[df_fis_filtrado['Nome_orgao'].isin(orgaos_selecionados)]
    df_rest_filtrado = df_rest_filtrado[df_rest_filtrado['Nome_orgao'].isin(orgaos_selecionados)]

st.title("🔍 Painel Avançado de Auditoria Financeira")
st.markdown(f"**Período:** {', '.join(map(str, anos_selecionados))} | **Quadrimestre(s):** {', '.join(map(str, quadrimestres_selecionados))}")
st.markdown(f"**Filtro de valor:** Acima de R$ {valor_minimo:,.2f}")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Visão Geral", 
    "🔍 Análise de Outliers", 
    "⚠️ Painel de Riscos", 
    "📈 Linha do Tempo", 
    "🏛️ Governança", 
    "📝 Relatórios"
])

with tab1:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Programas", df_prog['programa_codigo'].nunique())
    with col2:
        st.metric("Ações", df_acao['acao_codigo'].nunique())
    with col3:
        valor_empenhado = df_fin_filtrado['valor_empenhado'].sum()
        st.metric("Empenhado", f"R$ {valor_empenhado/1e6:.1f}M")
    with col4:
        valor_liquidado = df_fin_filtrado['valor_liquidado_ano'].sum()
        perc_exec = (valor_liquidado / valor_empenhado * 100) if valor_empenhado > 0 else 0
        st.metric("% Execução", f"{perc_exec:.1f}%")
    with col5:
        total_restricoes = len(df_rest_filtrado)
        st.metric("Restrições", f"{total_restricoes:,}")

    st.markdown("---")
    if not df_fin_filtrado.empty:
        df_ano = df_fin_filtrado.groupby(['ano', 'quadrimestre']).agg({
            'valor_empenhado': 'sum',
            'valor_liquidado_ano': 'sum',
            'valor_pago': 'sum'
        }).reset_index()
        fig = px.bar(
            df_ano, 
            x='quadrimestre', 
            y=['valor_empenhado', 'valor_liquidado_ano', 'valor_pago'],
            color='ano',
            barmode='group',
            labels={'value': 'Valor (R$)', 'quadrimestre': 'Quadrimestre', 'ano': 'Ano'},
            title="Execução Financeira Comparativa por Ano e Quadrimestre"
        )
        st.plotly_chart(fig, use_container_width=True)
    if not df_fin_filtrado.empty:
        df_heat = df_fin_filtrado.groupby(['Nome_orgao', 'ano'])['valor_pago'].sum().reset_index()
        if not df_heat.empty:
            heatmap = df_heat.pivot(index='Nome_orgao', columns='ano', values='valor_pago')
            fig_heat = px.imshow(
                heatmap,
                labels=dict(x="Ano", y="Órgão", color="Valor Pago (R$)"),
                aspect="auto",
                title="Heatmap: Distribuição de Pagamentos por Órgão e Ano"
            )
            st.plotly_chart(fig_heat, use_container_width=True)

with tab2:
    st.header("🔍 Detecção Automática de Outliers")
    if not df_fin_filtrado.empty:
        colunas_analise = ['valor_empenhado', 'valor_liquidado_ano', 'valor_pago']
        df_outliers = detectar_outliers(df_fin_filtrado, colunas_analise, threshold_outlier)
        outlier_cols = [col for col in df_outliers.columns if col.startswith('outlier_')]
        outliers = df_outliers[df_outliers[outlier_cols].any(axis=1)]
        if not outliers.empty:
            st.markdown(f"""
            <div class="alert-warning">
                🚨 <strong>{len(outliers)} registros identificados como outliers</strong> 
                (valores que desviam mais de {threshold_outlier} desvios padrão da média)
            </div>
            """, unsafe_allow_html=True)
            fig_scatter = px.scatter(
                df_outliers, 
                x='valor_empenhado', 
                y='valor_liquidado_ano',
                color=df_outliers[outlier_cols].any(axis=1),
                hover_data=['programa_codigo', 'Nome_orgao'],
                title="Dispersão: Empenhado vs Liquidado (Outliers em Destaque)",
                color_discrete_map={True: 'red', False: 'blue'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.subheader("📋 Registros Outliers Identificados")
            colunas_exibir = ['programa_codigo', 'acao_codigo', 'Nome_orgao', 'valor_empenhado', 'valor_liquidado_ano', 'valor_pago']
            st.dataframe(outliers[colunas_exibir], use_container_width=True)
        else:
            st.success("✅ Nenhum outlier detectado com o threshold atual.")

with tab3:
    st.header("⚠️ Painel de Riscos e Alertas")
    if not df_fis_filtrado.empty and not df_fin_filtrado.empty:
        df_conform = pd.merge(
            df_fis_filtrado[['acao_codigo', 'quantidade_ppa']].groupby('acao_codigo').sum().reset_index(),
            df_fin_filtrado[['acao_codigo', 'valor_empenhado', 'valor_liquidado_ano']].groupby('acao_codigo').sum().reset_index(),
            on='acao_codigo', how='outer'
        )
        df_conform['status'] = np.where(
            (df_conform['quantidade_ppa'].fillna(0) > 0) & (df_conform['valor_empenhado'].fillna(0) == 0),
            "Físico sem Financeiro",
            np.where(
                (df_conform['quantidade_ppa'].fillna(0) == 0) & (df_conform['valor_empenhado'].fillna(0) > 0),
                "Financeiro sem Físico",
                "OK"
            )
        )
    else:
        df_conform = pd.DataFrame()
    riscos = analisar_riscos(df_fin_filtrado, df_fis_filtrado, df_rest_filtrado, df_conform)
    if riscos:
        for i, risco in enumerate(riscos):
            cor_risco = {"Alto": "danger", "Médio": "warning", "Baixo": "success"}[risco['tipo']]
            st.markdown(f"""
            <div class="alert-{cor_risco}">
                <strong>Risco {risco['tipo']}:</strong> {risco['descricao']}<br>
                <strong>Impacto:</strong> {risco['impacto']}
            </div>
            """, unsafe_allow_html=True)
            with st.expander(f"Ver detalhes do Risco {i+1}"):
                if isinstance(risco['dados'], pd.DataFrame):
                    st.dataframe(risco['dados'])
                else:
                    st.write(risco['dados'])
    else:
        st.success("✅ Nenhum risco crítico identificado no período selecionado.")

with tab4:
    st.header("📈 Linha do Tempo da Execução")
    if not df_fin_filtrado.empty:
        df_timeline = df_fin_filtrado.groupby(['ano', 'quadrimestre']).agg({
            'valor_empenhado': 'sum',
            'valor_liquidado_ano': 'sum',
            'valor_pago': 'sum'
        }).reset_index()
        df_timeline['periodo'] = df_timeline['ano'].astype(str) + '-Q' + df_timeline['quadrimestre'].astype(str)
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(x=df_timeline['periodo'], y=df_timeline['valor_empenhado'], 
                                        mode='lines+markers', name='Empenhado', line=dict(color='blue')))
        fig_timeline.add_trace(go.Scatter(x=df_timeline['periodo'], y=df_timeline['valor_liquidado_ano'], 
                                        mode='lines+markers', name='Liquidado', line=dict(color='green')))
        fig_timeline.add_trace(go.Scatter(x=df_timeline['periodo'], y=df_timeline['valor_pago'], 
                                        mode='lines+markers', name='Pago', line=dict(color='red')))
        fig_timeline.update_layout(
            title="Evolução Temporal da Execução Financeira",
            xaxis_title="Período",
            yaxis_title="Valor (R$)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        if len(df_timeline) > 1:
            st.subheader("📊 Análise de Sazonalidade")
            df_sazon = df_fin_filtrado.groupby('quadrimestre')['valor_pago'].sum().reset_index()
            fig_sazon = px.bar(df_sazon, x='quadrimestre', y='valor_pago', 
                             title="Distribuição de Pagamentos por Quadrimestre")
            st.plotly_chart(fig_sazon, use_container_width=True)

with tab5:
    st.header("🏛️ Painel de Governança e Transparência")
    st.markdown("""
    <div class="governance-panel">
        <h4>🎯 Indicadores de Governança</h4>
        <p>Este painel monitora a transparência e eficiência da gestão pública.</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Índices de Transparência")
        if not df_fin_filtrado.empty:
            indice_exec = (df_fin_filtrado['valor_liquidado_ano'].sum() / df_fin_filtrado['valor_empenhado'].sum() * 100) if df_fin_filtrado['valor_empenhado'].sum() > 0 else 0
            st.metric("Índice de Execução", f"{indice_exec:.1f}%")
            if not df_fis_filtrado.empty:
                acoes_com_ambos = len(set(df_fin_filtrado['acao_codigo']) & set(df_fis_filtrado['acao_codigo']))
                total_acoes = len(set(df_fin_filtrado['acao_codigo']) | set(df_fis_filtrado['acao_codigo']))
                indice_efic = (acoes_com_ambos / total_acoes * 100) if total_acoes > 0 else 0
                st.metric("Índice de Eficiência", f"{indice_efic:.1f}%")
    with col2:
        st.subheader("🔗 Links de Transparência")
        st.markdown("""
        - [Portal da Transparência](https://transparencia.gov.br)
        - [Dados Abertos](https://dados.gov.br)
        - [Controladoria Geral](https://cgu.gov.br)
        - [Tribunal de Contas](https://tcu.gov.br)
        """)
    if not df_fin_filtrado.empty:
        st.subheader("🏆 Ranking de Eficiência por Órgão")
        df_ranking = df_fin_filtrado.groupby('Nome_orgao').agg({
            'valor_empenhado': 'sum',
            'valor_liquidado_ano': 'sum'
        }).reset_index()
        df_ranking['eficiencia'] = (df_ranking['valor_liquidado_ano'] / df_ranking['valor_empenhado'] * 100).round(1)
        df_ranking = df_ranking.sort_values('eficiencia', ascending=False)
        fig_ranking = px.bar(df_ranking.head(10), x='eficiencia', y='Nome_orgao', 
                           orientation='h', title="Top 10 Órgãos por Eficiência de Execução")
        st.plotly_chart(fig_ranking, use_container_width=True)

with tab6:
    st.header("📝 Sumário Executivo e Relatórios")
    st.subheader("📋 Sumário Executivo Automático")
    sumario = []
    if not df_fin_filtrado.empty:
        valor_total = df_fin_filtrado['valor_empenhado'].sum()
        valor_liquidado = df_fin_filtrado['valor_liquidado_ano'].sum()
        perc_exec = (valor_liquidado / valor_total * 100) if valor_total > 0 else 0
        sumario.append(f"No período analisado, foram empenhados R$ {valor_total/1e6:.1f} milhões, com execução de {perc_exec:.1f}%.")
        if perc_exec < 70:
            sumario.append("A execução está abaixo do esperado, requerendo atenção especial.")
        elif perc_exec > 90:
            sumario.append("A execução está dentro dos parâmetros ideais.")
        df_outliers_sumario = detectar_outliers(df_fin_filtrado, ['valor_empenhado', 'valor_liquidado_ano'], threshold_outlier)
        outlier_cols = [col for col in df_outliers_sumario.columns if col.startswith('outlier_')]
        outliers_count = df_outliers_sumario[df_outliers_sumario[outlier_cols].any(axis=1)].shape[0]
        if outliers_count > 0:
            sumario.append(f"Foram identificados {outliers_count} registros com valores atípicos que requerem investigação.")
        if not df_rest_filtrado.empty:
            sumario.append(f"Há {len(df_rest_filtrado)} restrições ativas que podem impactar a execução.")
    if not sumario:
        sumario.append("Não há dados suficientes para gerar o sumário executivo.")
    sumario_texto = " ".join(sumario)
    st.markdown(f"**{sumario_texto}**")
    if st.button("📋 Copiar Sumário"):
        st.code(sumario_texto)
        st.success("Sumário copiado! Use Ctrl+A e Ctrl+C para copiar o texto.")
    st.subheader("📥 Exportação de Relatórios")
    col1, col2 = st.columns(2)
    with col1:
        if not df_fin_filtrado.empty:
            csv_data = df_fin_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Dados Financeiros (CSV)",
                data=csv_data,
                file_name=f'auditoria_financeira_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv'
            )
    with col2:
        if not df_fin_filtrado.empty:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_fin_filtrado.to_excel(writer, index=False, sheet_name='Financeiro')
                if not df_fis_filtrado.empty:
                    df_fis_filtrado.to_excel(writer, index=False, sheet_name='Físico')
                if not df_rest_filtrado.empty:
                    df_rest_filtrado.to_excel(writer, index=False, sheet_name='Restrições')
                sumario_df = pd.DataFrame({'Sumário Executivo': [sumario_texto]})
                sumario_df.to_excel(writer, index=False, sheet_name='Sumário')
            st.download_button(
                label="📊 Relatório Completo (Excel)",
                data=output.getvalue(),
                file_name=f'relatorio_auditoria_completo_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Painel Avançado de Auditoria Financeira**")
with col2:
    st.markdown(f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")