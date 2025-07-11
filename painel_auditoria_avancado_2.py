import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
from datetime import datetime

st.set_page_config(
    page_title="Painel Institucional de Auditoria Financeira",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Institucional Impressionante
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #2a5298;
        margin: 0.5rem 0;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .alert-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #28a745;
        color: #155724;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(40, 167, 69, 0.2);
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffc107;
        color: #856404;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(255, 193, 7, 0.2);
    }
    
    .alert-danger {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #dc3545;
        color: #721c24;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(220, 53, 69, 0.2);
    }
    
    .governance-panel {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 5px solid #1976d2;
        color: #0d47a1;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(25, 118, 210, 0.1);
    }
    
    .risk-panel {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        border-left: 5px solid #ff9800;
        color: #e65100;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(255, 152, 0, 0.1);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
        color: white;
    }
    
    .stSelectbox > div > div {
        background: white;
        border-radius: 8px;
        border: 2px solid #e9ecef;
    }
    
    .stMultiSelect > div > div {
        background: white;
        border-radius: 8px;
        border: 2px solid #e9ecef;
    }
    
    .stNumberInput > div > div {
        background: white;
        border-radius: 8px;
        border: 2px solid #e9ecef;
    }
    
    .stSlider > div > div {
        background: white;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .tab-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: white;
        border-radius: 8px;
        color: #495057;
        font-weight: 500;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
        color: white;
        box-shadow: 0 5px 15px rgba(42, 82, 152, 0.3);
    }
    
    .footer {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-top: 2rem;
        text-align: center;
    }
    
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    
    @media (max-width: 768px) {
        .stColumns > div {
            min-width: 100% !important;
        }
        .header-container {
            padding: 1rem;
        }
    }
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
    if not df_conform.empty and 'status' in df_conform.columns:
        fis_sem_fin = df_conform[df_conform['status'] == "Físico sem Financeiro"]
        if not fis_sem_fin.empty:
            riscos.append({
                'tipo': 'Alto',
                'descricao': f'{len(fis_sem_fin)} ações com execução física mas sem execução financeira',
                'impacto': 'Pode indicar algum problema no acompanhamento.',
                'dados': fis_sem_fin
            })
    if 'valor_restos_a_pagar' in df_fin.columns:
        rp_alto = df_fin[df_fin['valor_restos_a_pagar'] > df_fin['valor_restos_a_pagar'].quantile(0.9)]
        if not rp_alto.empty:
            riscos.append({
                'tipo': 'Médio',
                'descricao': f'{len(rp_alto)} registros com restos a pagar muito altos.',
                'impacto': 'Pode comprometer o orçamento futuro.',
                'dados': rp_alto
            })
    concentracao = df_fin.groupby('programa_codigo')['valor_pago'].sum()
    total_pago = concentracao.sum()
    if total_pago > 0:
        top_programa = concentracao.max() / total_pago
        if top_programa > 0.3:
            riscos.append({
                'tipo': 'Baixo',
                'descricao': f'Um programa concentra {top_programa:.1%} dos pagamentos.',
                'impacto': 'Concentração excessiva de recursos.',
                'dados': concentracao.head(5)
            })
    if not df_rest.empty:
        rest_recorrentes = df_rest['restricao_codigo'].value_counts()
        if len(rest_recorrentes) > 0 and rest_recorrentes.iloc[0] > 5:
            riscos.append({
                'tipo': 'Médio',
                'descricao': f'Restrição {rest_recorrentes.index[0]} aparece {rest_recorrentes.iloc[0]} vezes.',
                'impacto': 'Problema recorrente que precisa de atenção.',
                'dados': rest_recorrentes.head(5)
            })
    return riscos

# Carregamento dos dados
df_fin, df_fis, df_prog, df_acao, df_rest, df_ind = load_data()
if df_fin is None:
    st.stop()

# Mapeamento Nome_orgao
uo_to_nome_orgao = df_prog[['uo_codigo', 'Nome_orgao']].drop_duplicates().set_index('uo_codigo')['Nome_orgao'].to_dict()
for df in [df_fin, df_fis, df_rest]:
    if 'Nome_orgao' not in df.columns and 'uo_codigo' in df.columns:
        df['Nome_orgao'] = df['uo_codigo'].map(uo_to_nome_orgao)

# Header Institucional
st.markdown("""
<div class="header-container">
    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🏛️ Painel Institucional de Auditoria Financeira</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">Sistema Avançado de Monitoramento e Controle da Gestão Pública</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Elegante
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; color: white; text-align: center;">
        <h2 style="margin: 0; color: white;">🔍 Filtros Avançados</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Configure sua análise</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📁 Upload de Arquivos")
    uploaded_file = st.file_uploader("Carregar arquivo auxiliar", type=['csv', 'xlsx'])
    if uploaded_file:
        st.success("✅ Arquivo carregado com sucesso!")
    
    st.markdown("### 📅 Período de Análise")
    anos = sorted(df_fin['ano'].unique())
    anos_selecionados = st.multiselect("Selecione o(s) ano(s):", anos, default=anos[-2:])
    
    quadrimestres = sorted(df_fin['quadrimestre'].unique())
    quadrimestres_selecionados = st.multiselect("Selecione o(s) quadrimestre(s):", quadrimestres, default=quadrimestres)
    
    st.markdown("### 🏢 Filtros Organizacionais")
    orgaos_disponiveis = sorted(df_prog['Nome_orgao'].dropna().unique())
    orgaos_selecionados = st.multiselect("Filtre por órgão:", orgaos_disponiveis)
    
    st.markdown("### ⚙️ Configurações Avançadas")
    valor_minimo = st.number_input("Valor mínimo para análise (R$):", min_value=0, value=100000, step=10000)
    threshold_outlier = st.slider("Sensibilidade para detecção de anomalias:", 1.0, 5.0, 3.0, 0.5)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 1rem; border-radius: 8px; margin-top: 1rem; color: white;">
        <strong>💡 Dica:</strong> Use os filtros para focar sua análise em períodos e órgãos específicos.
    </div>
    """, unsafe_allow_html=True)

# Aplicar filtros
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

# Informações do período
st.markdown(f"""
<div style="background: linear-gradient(135deg, #6c757d 0%, #495057 100%); color: white; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; text-align: center;">
    <strong>📊 Período Analisado:</strong> {', '.join(map(str, anos_selecionados))} | 
    <strong>Quadrimestre(s):</strong> {', '.join(map(str, quadrimestres_selecionados))} | 
    <strong>Filtro de Valor:</strong> Acima de R$ {valor_minimo:,.2f}
</div>
""", unsafe_allow_html=True)

# Abas principais com design moderno
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard Executivo", 
    "🔍 Análise de Anomalias", 
    "⚠️ Gestão de Riscos", 
    "📈 Análise Temporal", 
    "🏛️ Governança Corporativa", 
    "📝 Relatórios Gerenciais"
])

with tab1:
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    # KPIs Principais com design elegante
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #2a5298; margin: 0;">📋 Programas</h3>
            <h2 style="color: #1e3c72; margin: 0.5rem 0 0 0;">{}</h2>
        </div>
        """.format(df_prog['programa_codigo'].nunique()), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #2a5298; margin: 0;">🎯 Ações</h3>
            <h2 style="color: #1e3c72; margin: 0.5rem 0 0 0;">{}</h2>
        </div>
        """.format(df_acao['acao_codigo'].nunique()), unsafe_allow_html=True)
    
    with col3:
        valor_empenhado = df_fin_filtrado['valor_empenhado'].sum()
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #2a5298; margin: 0;">💰 Empenhado</h3>
            <h2 style="color: #1e3c72; margin: 0.5rem 0 0 0;">R$ {:.1f}M</h2>
        </div>
        """.format(valor_empenhado/1e6), unsafe_allow_html=True)
    
    with col4:
        valor_liquidado = df_fin_filtrado['valor_liquidado_ano'].sum()
        perc_exec = (valor_liquidado / valor_empenhado * 100) if valor_empenhado > 0 else 0
        cor_exec = "#28a745" if perc_exec >= 80 else "#ffc107" if perc_exec >= 60 else "#dc3545"
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #2a5298; margin: 0;">📈 Execução</h3>
            <h2 style="color: {}; margin: 0.5rem 0 0 0;">{:.1f}%</h2>
        </div>
        """.format(cor_exec, perc_exec), unsafe_allow_html=True)
    
    with col5:
        total_restricoes = len(df_rest_filtrado)
        cor_rest = "#dc3545" if total_restricoes > 10 else "#ffc107" if total_restricoes > 5 else "#28a745"
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #2a5298; margin: 0;">⚠️ Restrições</h3>
            <h2 style="color: {}; margin: 0.5rem 0 0 0;">{}</h2>
        </div>
        """.format(cor_rest, total_restricoes), unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Gráficos com containers elegantes
    if not df_fin_filtrado.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
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
            title="📊 Execução Financeira Comparativa por Período",
            color_discrete_sequence=['#1e3c72', '#2a5298', '#3d5aa1']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter",
            title_font_size=20,
            title_font_color='#1e3c72'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Heatmap elegante
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        df_heat = df_fin_filtrado.groupby(['Nome_orgao', 'ano'])['valor_pago'].sum().reset_index()
        if not df_heat.empty:
            heatmap = df_heat.pivot(index='Nome_orgao', columns='ano', values='valor_pago')
            fig_heat = px.imshow(
                heatmap,
                labels=dict(x="Ano", y="Órgão", color="Valor Pago (R$)"),
                aspect="auto",
                title="🔥 Mapa de Calor: Distribuição de Pagamentos por Órgão",
                color_continuous_scale='Blues'
            )
            fig_heat.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                title_font_size=20,
                title_font_color='#1e3c72'
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.markdown("## 🔍 Detecção Inteligente de Anomalias")
    
    if not df_fin_filtrado.empty:
        colunas_analise = ['valor_empenhado', 'valor_liquidado_ano', 'valor_pago']
        df_outliers = detectar_outliers(df_fin_filtrado, colunas_analise, threshold_outlier)
        outlier_cols = [col for col in df_outliers.columns if col.startswith('outlier_')]
        outliers = df_outliers[df_outliers[outlier_cols].any(axis=1)]
        
        if not outliers.empty:
            st.markdown(f"""
            <div class="alert-danger">
                🚨 <strong>Anomalias Detectadas:</strong> Identificamos {len(outliers)} registros com valores significativamente fora do padrão estatístico.
                <br><strong>Recomendação:</strong> Revisar estes casos para verificar possíveis inconsistências.
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_scatter = px.scatter(
                df_outliers, 
                x='valor_empenhado', 
                y='valor_liquidado_ano',
                color=df_outliers[outlier_cols].any(axis=1),
                hover_data=['programa_codigo', 'Nome_orgao'],
                title="🎯 Análise de Dispersão: Identificação de Anomalias",
                color_discrete_map={True: '#dc3545', False: '#2a5298'},
                labels={'color': 'Anomalia Detectada'}
            )
            fig_scatter.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                title_font_size=20,
                title_font_color='#1e3c72'
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("### 📋 Registros Anômalos Identificados")
            colunas_exibir = ['programa_codigo', 'acao_codigo', 'Nome_orgao', 'valor_empenhado', 'valor_liquidado_ano', 'valor_pago']
            st.dataframe(outliers[colunas_exibir], use_container_width=True)
        else:
            st.markdown("""
            <div class="alert-success">
                ✅ <strong>Sistema Estável:</strong> Não foram detectadas anomalias significativas nos dados analisados.
                <br><strong>Status:</strong> Todos os valores estão dentro dos parâmetros estatísticos esperados.
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.markdown("## ⚠️ Central de Gestão de Riscos")
    
    # Análise de conformidade
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
            icone_risco = {"Alto": "🔴", "Médio": "🟡", "Baixo": "🟢"}[risco['tipo']]
            
            st.markdown(f"""
            <div class="alert-{cor_risco}">
                <h4>{icone_risco} <strong>Risco {risco['tipo']}:</strong> {risco['descricao']}</h4>
                <p><strong>Impacto Potencial:</strong> {risco['impacto']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"📊 Análise Detalhada do Risco {i+1}"):
                if isinstance(risco['dados'], pd.DataFrame):
                    st.dataframe(risco['dados'], use_container_width=True)
                else:
                    st.write(risco['dados'])
    else:
        st.markdown("""
        <div class="alert-success">
            ✅ <strong>Ambiente Controlado:</strong> Não foram identificados riscos críticos no período analisado.
            <br><strong>Status:</strong> Todos os indicadores estão dentro dos parâmetros aceitáveis de governança.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.markdown("## 📈 Análise Temporal Avançada")
    
    if not df_fin_filtrado.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        df_timeline = df_fin_filtrado.groupby(['ano', 'quadrimestre']).agg({
            'valor_empenhado': 'sum',
            'valor_liquidado_ano': 'sum',
            'valor_pago': 'sum'
        }).reset_index()
        df_timeline['periodo'] = df_timeline['ano'].astype(str) + '-Q' + df_timeline['quadrimestre'].astype(str)
        
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=df_timeline['periodo'], 
            y=df_timeline['valor_empenhado'], 
            mode='lines+markers', 
            name='Empenhado', 
            line=dict(color='#1e3c72', width=3),
            marker=dict(size=8)
        ))
        fig_timeline.add_trace(go.Scatter(
            x=df_timeline['periodo'], 
            y=df_timeline['valor_liquidado_ano'], 
            mode='lines+markers', 
            name='Liquidado', 
            line=dict(color='#28a745', width=3),
            marker=dict(size=8)
        ))
        fig_timeline.add_trace(go.Scatter(
            x=df_timeline['periodo'], 
            y=df_timeline['valor_pago'], 
            mode='lines+markers', 
            name='Pago', 
            line=dict(color='#dc3545', width=3),
            marker=dict(size=8)
        ))
        
        fig_timeline.update_layout(
            title="📊 Evolução Temporal da Execução Financeira",
            xaxis_title="Período",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter",
            title_font_size=20,
            title_font_color='#1e3c72'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if len(df_timeline) > 1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            df_sazon = df_fin_filtrado.groupby('quadrimestre')['valor_pago'].sum().reset_index()
            fig_sazon = px.bar(
                df_sazon, 
                x='quadrimestre', 
                y='valor_pago', 
                title="📊 Análise de Sazonalidade por Quadrimestre",
                color='valor_pago',
                color_continuous_scale='Blues'
            )
            fig_sazon.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                title_font_size=20,
                title_font_color='#1e3c72'
            )
            st.plotly_chart(fig_sazon, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.markdown("## 🏛️ Painel de Governança Corporativa")
    
    st.markdown("""
    <div class="governance-panel">
        <h3>🎯 Indicadores de Governança Institucional</h3>
        <p>Monitoramento contínuo da transparência, eficiência e conformidade da gestão pública.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Métricas de Transparência")
        if not df_fin_filtrado.empty:
            indice_exec = (df_fin_filtrado['valor_liquidado_ano'].sum() / df_fin_filtrado['valor_empenhado'].sum() * 100) if df_fin_filtrado['valor_empenhado'].sum() > 0 else 0
            cor_indice = "#28a745" if indice_exec >= 80 else "#ffc107" if indice_exec >= 60 else "#dc3545"
            
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #2a5298; margin: 0;">Índice de Execução Orçamentária</h4>
                <h2 style="color: {cor_indice}; margin: 0.5rem 0 0 0;">{indice_exec:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
            
            if not df_fis_filtrado.empty:
                acoes_com_ambos = len(set(df_fin_filtrado['acao_codigo']) & set(df_fis_filtrado['acao_codigo']))
                total_acoes = len(set(df_fin_filtrado['acao_codigo']) | set(df_fis_filtrado['acao_codigo']))
                indice_efic = (acoes_com_ambos / total_acoes * 100) if total_acoes > 0 else 0
                cor_efic = "#28a745" if indice_efic >= 80 else "#ffc107" if indice_efic >= 60 else "#dc3545"
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #2a5298; margin: 0;">Índice de Eficiência Operacional</h4>
                    <h2 style="color: {cor_efic}; margin: 0.5rem 0 0 0;">{indice_efic:.1f}%</h2>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🔗 Portal de Transparência")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #2a5298;">
            <h4 style="color: #2a5298; margin-top: 0;">Links Institucionais</h4>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 0.5rem 0;"><a href="https://transparencia.gov.br" target="_blank" style="color: #1e3c72; text-decoration: none;">🌐 Portal da Transparência</a></li>
                <li style="margin: 0.5rem 0;"><a href="https://dados.gov.br" target="_blank" style="color: #1e3c72; text-decoration: none;">📊 Dados Abertos</a></li>
                <li style="margin: 0.5rem 0;"><a href="https://cgu.gov.br" target="_blank" style="color: #1e3c72; text-decoration: none;">🛡️ Controladoria Geral</a></li>
                <li style="margin: 0.5rem 0;"><a href="https://tcu.gov.br" target="_blank" style="color: #1e3c72; text-decoration: none;">⚖️ Tribunal de Contas</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    if not df_fin_filtrado.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 🏆 Ranking de Eficiência Organizacional")
        df_ranking = df_fin_filtrado.groupby('Nome_orgao').agg({
            'valor_empenhado': 'sum',
            'valor_liquidado_ano': 'sum'
        }).reset_index()
        df_ranking['eficiencia'] = (df_ranking['valor_liquidado_ano'] / df_ranking['valor_empenhado'] * 100).round(1)
        df_ranking = df_ranking.sort_values('eficiencia', ascending=False)
        
        fig_ranking = px.bar(
            df_ranking.head(10), 
            x='eficiencia', 
            y='Nome_orgao', 
            orientation='h', 
            title="🎯 Top 10 Órgãos por Eficiência de Execução",
            color='eficiencia',
            color_continuous_scale='Blues'
        )
        fig_ranking.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter",
            title_font_size=20,
            title_font_color='#1e3c72'
        )
        st.plotly_chart(fig_ranking, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab6:
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.markdown("## 📝 Central de Relatórios Gerenciais")
    
    st.markdown("### 📋 Sumário Executivo Automatizado")
    sumario = []
    if not df_fin_filtrado.empty:
        valor_total = df_fin_filtrado['valor_empenhado'].sum()
        valor_liquidado = df_fin_filtrado['valor_liquidado_ano'].sum()
        perc_exec = (valor_liquidado / valor_total * 100) if valor_total > 0 else 0
        
        sumario.append(f"**Execução Orçamentária:** No período analisado, foram empenhados R$ {valor_total/1e6:.1f} milhões.")
        sumario.append(f"**Performance:** O percentual de execução atingiu {perc_exec:.1f}%.")
        
        if perc_exec < 70:
            sumario.append("**Alerta:** A execução está abaixo do esperado, requerendo atenção especial da gestão.")
        elif perc_exec > 90:
            sumario.append("**Excelência:** A execução está dentro dos parâmetros ideais de eficiência.")
        
        df_outliers_sumario = detectar_outliers(df_fin_filtrado, ['valor_empenhado', 'valor_liquidado_ano'], threshold_outlier)
        outlier_cols = [col for col in df_outliers_sumario.columns if col.startswith('outlier_')]
        outliers_count = df_outliers_sumario[df_outliers_sumario[outlier_cols].any(axis=1)].shape[0]
        
        if outliers_count > 0:
            sumario.append(f"**Anomalias:** {outliers_count} registros apresentam valores atípicos que requerem investigação.")
        
        if not df_rest_filtrado.empty:
            sumario.append(f"**Restrições:** Identificadas {len(df_rest_filtrado)} restrições ativas que podem impactar a execução.")
    
    if not sumario:
        sumario.append("**Status:** Não há dados suficientes para gerar o sumário executivo.")
    
    sumario_texto = '\n\n'.join(sumario)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 2rem; border-radius: 12px; border-left: 4px solid #2a5298;">
        {sumario_texto.replace('**', '<strong>').replace('**', '</strong>')}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📋 Copiar Sumário Executivo", type="primary"):
        st.code(sumario_texto)
        st.success("✅ Sumário copiado! Use Ctrl+A e Ctrl+C para copiar o texto.")
    
    st.markdown("### 📥 Centro de Exportação")
    col1, col2 = st.columns(2)
    
    with col1:
        if not df_fin_filtrado.empty:
            csv_data = df_fin_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Exportar Dados Financeiros (CSV)",
                data=csv_data,
                file_name=f'auditoria_financeira_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv',
                type="primary"
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
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                type="primary"
            )
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer Institucional
st.markdown(f"""
<div class="footer">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h3 style="margin: 0; color: white;">🏛️ Painel Institucional de Auditoria Financeira</h3>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.8;">Sistema Avançado de Monitoramento e Controle da Gestão Pública</p>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; opacity: 0.8;">Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            <p style="margin: 0.25rem 0 0 0; opacity: 0.6;">Versão 2.0 | Desenvolvido com Streamlit</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)