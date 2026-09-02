import streamlit as st
import pandas as pd

# =============================================================================
# 1. SISTEMA DE LOGIN E SEGURANÇA (SaaS)
# =============================================================================
st.set_page_config(page_title="SPDA Risk - NBR 5419-2:2026", layout="wide", page_icon="⚡")

def verificar_login():
    """Cria a tela de login e valida contra o st.secrets"""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.markdown("<h1 style='text-align: center;'>⚡ SPDA Risk Pro</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: gray;'>Faça login para acessar o sistema de cálculos</h4>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            with st.form("form_login"):
                usuario = st.text_input("Usuário")
                senha = st.text_input("Senha", type="password")
                botao_login = st.form_submit_button("Entrar", use_container_width=True)

                if botao_login:
                    try:
                        senhas_salvas = st.secrets["clientes"]
                        if usuario in senhas_salvas and senhas_salvas[usuario] == senha:
                            st.session_state.autenticado = True
                            st.rerun()
                        else:
                            st.error("Usuário ou senha incorretos.")
                    except KeyError:
                        st.error("Erro no servidor: 'Secrets' não configurado corretamente.")
        
        st.stop()

verificar_login()

# Botão de Logout
c1, c2 = st.columns([9, 1])
with c2:
    if st.button("🚪 Sair (Logout)", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.linhas = []
        st.session_state.zonas = []
        st.rerun()

# =============================================================================
# 2. SEU APLICATIVO PRINCIPAL (Backend e Interface)
# =============================================================================
from estrutura import Estrutura
from linhas_eletricas import LinhaEletrica
from probabilidades import Probabilidades, FatoresK
from perdas import ZonaEstudo
from analisador import AnalisadorRisco
from gerador_pdf import gerar_pdf_laudo

# Inicia estado das listas
if "linhas" not in st.session_state:
    st.session_state.linhas = []
if "zonas" not in st.session_state:
    st.session_state.zonas = []

st.title("⚡ Sistema Web de Análise de Risco - ABNT NBR 5419-2:2026")

aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "1. Geral & Geometria", 
    "2. Linhas Elétricas (SL)", 
    "3. Zonas de Estudo (ZS)", 
    "4. Proteção Global", 
    "5. Relatório e Laudo PDF"
])

# --- ABA 1: GEOMETRIA E LOCALIDADE ---
with aba1:
    st.header("Dados do Projeto e Geometria da Estrutura")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Atividade Atmosférica")
        cidade = st.text_input("Nome da Localidade / Projeto:", "Petrolina - PE")
        ng = st.number_input("Densidade de Raios (NG - raios/km²/ano):", value=6.0, step=0.1)

        st.subheader("Geometria Principal")
        l_est = st.number_input("Comprimento L (m):", value=43.2)
        w_est = st.number_input("Largura W (m):", value=10.85)
        h_min = st.number_input("Altura Corpo Principal H_min (m):", value=4.65)
        h_max = st.number_input("Altura Saliência/Antena H_max (m):", value=0.0)
        cd_op = st.selectbox("Fator de Localização (CD):", ["1.0 - Isolada", "0.5 - Cercada mesma altura", "0.25 - Cercada objetos altos", "2.0 - Topo de colina/monte"], index=1)

    with col2:
        st.subheader("Estrutura Adjacente (Vizinhança Conectada)")
        tem_adj = st.checkbox("Considerar Estrutura Adjacente Conectada por Linha", value=True)
        lj = st.number_input("Comprimento Adjacente LJ (m):", value=30.0, disabled=not tem_adj)
        wj = st.number_input("Largura Adjacente WJ (m):", value=9.0, disabled=not tem_adj)
        hj = st.number_input("Altura Adjacente HJ (m):", value=4.65, disabled=not tem_adj)
        cdj_op = st.selectbox("Fator CDJ:", ["1.0 - Isolada", "0.5 - Mesma altura", "0.25 - Mais baixa"], index=1, disabled=not tem_adj)


# --- ABA 2: GERENCIADOR DE LINHAS ---
with aba2:
    st.header("Trechos de Linhas Elétricas (S_L)")
    
    with st.expander("➕ Cadastrar Nova Linha Elétrica", expanded=True):
        c1, c2, c3 = st.columns(3)
        id_lin = c1.text_input("ID da Linha:", "Linha Energia BT")
        tipo_lin = c2.selectbox("Tipo de Linha:", ["energia", "sinal"])
        ll_lin = c3.number_input("Comprimento LL (m):", value=300.0)
        
        ci_op = c1.selectbox("Fator Instalação (CI):", ["1.0 - Aérea", "0.5 - Enterrada", "0.01 - Enterrada em Malha"], index=1)
        ce_op = c2.selectbox("Fator Ambiental (CE):", ["1.0 - Rural", "0.5 - Suburbano", "0.1 - Urbano", "0.01 - Urbano (>20m)"], index=1)
        ct_op = c3.selectbox("Fator do Tipo (CT):", ["1.0 - Linha BT / Sinal sem Trafo", "0.2 - Linha AT com Trafo Isolador"])
        
        blindada = c1.checkbox("Linha Blindada")
        rs_lin = c2.number_input("Resistência Blindagem (Ohm/km):", value=1.0)
        uw_lin = c3.number_input("Tensão Suportável UW (kV):", value=6.0)
        
        if st.button("Salvar Linha na Lista"):
            ci = float(ci_op.split(" - ")[0])
            ce = float(ce_op.split(" - ")[0])
            ct = float(ct_op.split(" - ")[0])
            nova_linha = LinhaEletrica(
                id_linha=id_lin, tipo_linha=tipo_lin, l_l=ll_lin,
                c_i=ci, c_e=ce, c_t=ct, blindada=blindada, r_s=rs_lin, u_w=uw_lin
            )
            st.session_state.linhas.append(nova_linha)
            st.success(f"Linha '{id_lin}' adicionada!")

    if st.session_state.linhas:
        st.subheader("Linhas Cadastradas")
        df_lin = pd.DataFrame([{
            "ID": l.id_linha, "Tipo": l.tipo_linha, "Comprimento (m)": l.L_L, "Blindada": l.blindada, "UW (kV)": l.U_W
        } for l in st.session_state.linhas])
        st.dataframe(df_lin, use_container_width=True)
        if st.button("Limpar Linhas"):
            st.session_state.linhas = []
            st.rerun()


# --- ABA 3: GERENCIADOR DE ZONAS ---
with aba3:
    st.header("Zonas de Estudo (Z_S)")
    
    with st.expander("➕ Cadastrar Nova Zona de Estudo", expanded=True):
        z1, z2, z3 = st.columns(3)
        id_z = z1.text_input("ID da Zona:", "Zona_Geral")
        nz_z = z2.number_input("Pessoas na Zona (nz):", value=10.0)
        nt_z = z3.number_input("Pessoas na Estrutura Total (nt):", value=15.0)
        
        tz_z = z1.number_input("Tempo Exposição (tz h/ano):", value=5475.0)
        rt_op = z2.selectbox("Fator do Piso (rt):", ["1e-5 - Asfalto/Madeira", "1e-4 - Carpete", "1e-3 - Mármore", "1e-2 - Terra/Concreto"], index=2)
        rf_op = z3.selectbox("Risco de Incêndio (rf):", ["1.0 - Explosão", "0.1 - Alto", "0.01 - Normal", "0.001 - Baixo", "0.0 - Sem Risco"], index=3)
        
        rp_op = z1.selectbox("Proteção Incêndio (rp):", ["1.0 - Sem providências", "0.5 - Extintores/Hidrantes", "0.2 - Alarme automático"], index=2)
        hz_op = z2.selectbox("Perigo Pânico (hz):", ["1.0 - Sem Perigo", "2.0 - Baixo Pânico", "5.0 - Dificuldade Evacuação"], index=1)
        lt_op = z3.selectbox("Ferimento Choque (Lt):", ["0.0 - Não se aplica", "0.01 - Todos os tipos (Pessoas/Animais)"])
        
        lf_op = z1.selectbox("Dano Físico Típico (Lf):",["0.1 - Outros","1.0 - Risco de explosão","0.5 - Hospital, industrial, museu, agricultura","0.2 - Hotel, escola, escritório, igreja, comercial"])
        lo_op = z2.selectbox("Falha de Sistemas (Lo):", ["0.0001 - Outros","0.1 - Risco de explosão", "0.01 - Hospital, comercial", "0.001 - Museu, agricultura"])
        ks3_op = z3.selectbox("Roteamento (KS3):", ["1.0 - Cabos não blindados", "0.5 - Evita grandes laços", "0.2 - Evita laços médios", "0.01 - pequenos laços"])
        
        pta_op = z1.selectbox("Proteção Choque Estrutura (PTA):", ["1.0 - Sem proteção", "0.1 - Avisos", "0.01 - Isolação PE", "0.0 - Restrição física"])
        ptu_op = z2.selectbox("Proteção Choque Linha (PTU):", ["1.0 - Sem proteção", "0.1 - Avisos", "0.01 - Isolação", "0.0 - Restrição física"], index=2)
        
        st.markdown("**Custos Financeiros na Zona (R$)**")
        cx1, cx2, cx3 = st.columns(3)
        c_a = cx1.number_input("Animais (ca):", value=0.0)
        c_b = cx2.number_input("Edificação (cb):", value=0.0)
        c_c = cx3.number_input("Conteúdo (cc):", value=0.0)
        c_s = cx1.number_input("Sistemas (cs):", value=0.0)
        c_z = cx2.number_input("Patrimônio (cz):", value=0.0)
        c_t = cx3.number_input("Total (ct):", value=0.0)
        
        if st.button("Salvar Zona na Lista"):
            rt = float(rt_op.split(" - ")[0])
            rf = float(rf_op.split(" - ")[0])
            rp = float(rp_op.split(" - ")[0])
            hz = float(hz_op.split(" - ")[0])
            lt = float(lt_op.split(" - ")[0])
            lf = float(lf_op.split(" - ")[0])
            lo = float(lo_op.split(" - ")[0])
            pta = float(pta_op.split(" - ")[0])
            ptu = float(ptu_op.split(" - ")[0])
            ks3 = float(ks3_op.split(" - ")[0])
            
            nova_zona = ZonaEstudo(
                id_zona=id_z, n_z=nz_z, n_t=nt_z, t_z=tz_z,
                l_t=lt, l_f=lf, l_o=lo,
                r_t=rt, r_f=rf, r_p=rp, h_z=hz, p_ta=pta, p_tu=ptu,
                c_a=c_a, c_b=c_b, c_c=c_c, c_s=c_s, c_z=c_z, c_t=c_t,
                fatores_k=FatoresK(k_s3=ks3)
            )
            st.session_state.zonas.append(nova_zona)
            st.success(f"Zona '{id_z}' adicionada!")

    if st.session_state.zonas:
        st.subheader("Zonas Cadastradas")
        df_z = pd.DataFrame([{
            "ID": z.id_zona, "Pessoas (nz)": z.n_z, "Lf (Dano Físico)": z.L_F, "Lo (Falha Sist.)": z.L_O, "Valor Total (ct)": f"R$ {z.c_t:,.2f}"
        } for z in st.session_state.zonas])
        st.dataframe(df_z, use_container_width=True)
        if st.button("Limpar Zonas"):
            st.session_state.zonas = []
            st.rerun()


# --- ABA 4: PROTEÇÃO GLOBAL ---
with aba4:
    st.header("Medidas de Proteção Globais")
    spda_op = st.selectbox("Nível do SPDA Externo (PB):", ["nenhum", "IV", "III", "II", "I"])
    dps_op = st.selectbox("Nível Coordenado de DPS (PSPD):", ["nenhum", "III-IV", "II", "I"])
    peb_op = st.selectbox("Equipotencialização de Entrada (PEB):", ["1.0 - Sem DPS Classe I", "0.05 - DPS Nível III-IV", "0.02 - DPS Nível II", "0.01 - DPS Nível I"])
    falha_vida = st.checkbox("Falhas de sistemas colocam vidas humanas em risco imediato (ex: UTI)")


# --- ABA 5: PROCESSAMENTO E RELATÓRIO ---
with aba5:
    st.header("Relatório e Emissão de Laudo Técnico")
    
    if st.button("🚀 Executar Análise de Risco Completa", type="primary"):
        if not st.session_state.zonas or not st.session_state.linhas:
            st.error("Cadastre pelo menos uma Zona de Estudo e uma Linha Elétrica antes de rodar o cálculo!")
        else:
            cd = float(cd_op.split(" - ")[0])
            cdj = float(cdj_op.split(" - ")[0]) if tem_adj else 1.0
            peb = float(peb_op.split(" - ")[0])
            
            est = Estrutura(l=l_est, w=w_est, h_min=h_min, h_max=h_max, c_d=cd, tem_adjacente=tem_adj, l_j=lj, w_j=wj, h_j=hj, c_dj=cdj)
            z1 = st.session_state.zonas[0]
            probs = Probabilidades(nivel_spda=spda_op, nivel_dps=dps_op, p_ta=z1.P_TA, p_tu=z1.P_TU, p_eb=peb, fatores_k=z1.fatores_k)
            
            analisador = AnalisadorRisco(n_g=ng, estrutura=est, zonas=st.session_state.zonas, linhas=st.session_state.linhas, probabilidades=probs)
            
            r1 = analisador.calcular_r1_total(falha_sistema_risco_vida=falha_vida)
            r3 = analisador.calcular_r3_total()
            f_total = analisador.calcular_f_total()
            r4 = analisador.calcular_r4_total()
            ct_medio = sum(z.c_t for z in st.session_state.zonas) / len(st.session_state.zonas)
            custo_perda = r4 * ct_medio

            st.success("Cálculo realizado com sucesso!")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Risco R1 (Vida)", f"{r1:.2e}", delta="Aprovado" if r1 <= 1e-5 else "Reprovado", delta_color="normal" if r1 <= 1e-5 else "inverse")
            c2.metric("Risco R3 (Patrimônio)", f"{r3:.2e}", delta="Aprovado" if r3 <= 1e-4 else "Reprovado", delta_color="normal" if r3 <= 1e-4 else "inverse")
            c3.metric("Frequência F (Danos)", f"{f_total:.4f}/ano", delta="Seguro" if f_total <= 1.0 else "Inseguro", delta_color="normal" if f_total <= 1.0 else "inverse")
            c4.metric("Custo Provável (R4)", f"R$ {custo_perda:,.2f}")

            try:
                resultados_dict = {'r1': r1, 'r3': r3, 'f': f_total, 'r4': r4, 'custo_perda': custo_perda}
                pdf_data = gerar_pdf_laudo(cidade, ng, est, st.session_state.zonas, st.session_state.linhas, resultados_dict)
                
                st.download_button(
                    label="📄 Baixar Laudo Técnico em PDF",
                    data=pdf_data,
                    file_name=f"Laudo_SPDA_{cidade.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")
