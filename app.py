Tem toda a razão! Peço desculpas. Quando te enviei o bloco corrigido da aba 3 na última mensagem, acabei cortando acidentalmente as linhas finais que renderizavam a tabela de zonas salvas na tela.Além disso, transformar as variáveis $L_f$, $L_o$ e $L_t$ em caixas de seleção é uma excelente melhoria, pois evita erros de digitação e obriga o preenchimento normativo (Tabelas C.2, C.10 e C.12 da NBR 5419-2).Vou te passar o código completo e definitivo da Aba 3, já com os três novos menus suspensos e com a lista de zonas recuperada!Substitua todo o bloco with aba3: no seu arquivo app.py por este código abaixo:Python# =============================================================================
# ABA 3: GERENCIADOR DE ZONAS
# =============================================================================
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
        
        # --- NOVOS SELETORES NORMATIVOS (Lt, Lf, Lo) ---
        lt_op = z3.selectbox("Ferimento Choque (Lt):", [
            "0.01 - Todos os tipos (Pessoas/Animais)", 
            "0.0 - Não se aplica"
        ])
        
        lf_op = z1.selectbox("Dano Físico Típico (Lf):", [
            "0.1 - Outros", 
            "1.0 - Risco de explosão", 
            "0.5 - Hospital, industrial, museu, agricultura", 
            "0.2 - Hotel, escola, escritório, igreja, comercial"
        ])
        
        lo_op = z2.selectbox("Falha de Sistemas (Lo):", [
            "0.0001 - Outros", 
            "0.1 - Risco de explosão", 
            "0.01 - Hospital, industrial, escritório, comercial", 
            "0.001 - Museu, agricultura, escola, igreja"
        ])
        # ----------------------------------------------
        
        pta_op = z3.selectbox("Proteção Choque (PTA):", ["1.0 - Sem proteção", "0.1 - Avisos", "0.01 - Isolação PE", "0.0 - Restrição física"])
        ptu_op = z1.selectbox("Proteção Linha (PTU):", ["1.0 - Sem proteção", "0.1 - Avisos", "0.01 - Isolação", "0.0 - Restrição física"], index=2)
        ks3_op = z2.selectbox("Roteamento (KS3):", ["1.0 - Cabos não blindados", "0.5 - Evita grandes laços", "0.2 - Evita laços médios", "0.01 - pequenos laços"])
        
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

    # --- LISTA DE ZONAS RECUPERADA ---
    if st.session_state.zonas:
        st.subheader("Zonas Cadastradas")
        df_z = pd.DataFrame([{
            "ID": z.id_zona, 
            "Pessoas (nz)": z.n_z, 
            "Lf (Dano Físico)": z.L_F,
            "Lo (Falha Sist.)": z.L_O,
            "Valor Total (ct)": f"R$ {z.c_t:,.2f}"
        } for z in st.session_state.zonas])
        st.dataframe(df_z, use_container_width=True)
        
        if st.button("Limpar Zonas"):
            st.session_state.zonas = []
            st.rerun()
