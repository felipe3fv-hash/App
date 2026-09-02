import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QComboBox,
                             QPushButton, QTextEdit, QTabWidget, QFormLayout,
                             QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QCheckBox, QMessageBox)

# Importando os módulos do backend
from estrutura import Estrutura
from linhas_eletricas import LinhaEletrica
from probabilidades import Probabilidades, FatoresK
from perdas import ZonaEstudo
from analisador import AnalisadorRisco


# =============================================================================
# DIÁLOGO 1: CADASTRO DE LINHA ELÉTRICA (SL)
# =============================================================================
class DialogoLinha(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar / Editar Linha Elétrica (SL)")
        self.setMinimumWidth(400)

        layout = QFormLayout()

        self.in_id = QLineEdit("Linha Energia Principal")
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["energia", "sinal"])

        self.in_ll = QLineEdit("1000")
        self.combo_ci = QComboBox()
        self.combo_ci.addItems(["1.0 - Aérea", "0.5 - Enterrada", "0.01 - Enterrada em Malha"])

        self.combo_ce = QComboBox()
        self.combo_ce.addItems(["1.0 - Rural", "0.5 - Suburbano", "0.1 - Urbano", "0.01 - Urbano (>20m)"])

        self.combo_ct = QComboBox()
        self.combo_ct.addItems(["1.0 - Linha BT / Sinal sem Trafo", "0.2 - Linha AT com Trafo Isolador"])

        self.chk_enterrada = QCheckBox("Linha Subterrânea")
        self.in_rho = QLineEdit("400.0")

        self.chk_blindada = QCheckBox("Possui Blindagem Metálica")
        self.in_rs = QLineEdit("1.0")  # Ohms/km
        self.chk_mesmo_bep = QCheckBox("Blindagem interligada no mesmo BEP do Equipamento")
        self.chk_conduto = QCheckBox("Instalada em Eletroduto Metálico Contínuo")
        self.chk_interface = QCheckBox("Possui Interface Isolante (Fibra Óptica/Trafo)")
        self.in_uw = QLineEdit("1.5")  # kV

        layout.addRow("ID da Linha:", self.in_id)
        layout.addRow("Tipo de Linha:", self.combo_tipo)
        layout.addRow("Comprimento LL (m):", self.in_ll)
        layout.addRow("Fator Instalação (CI):", self.combo_ci)
        layout.addRow("Fator Ambiental (CE):", self.combo_ce)
        layout.addRow("Fator do Tipo (CT):", self.combo_ct)
        layout.addRow("", self.chk_enterrada)
        layout.addRow("Resistividade Solo (Ohm.m):", self.in_rho)
        layout.addRow("", self.chk_blindada)
        layout.addRow("Resistência Blindagem (Ohm/km):", self.in_rs)
        layout.addRow("", self.chk_mesmo_bep)
        layout.addRow("", self.chk_conduto)
        layout.addRow("", self.chk_interface)
        layout.addRow("Tensão Suportável UW (kV):", self.in_uw)

        btn_salvar = QPushButton("Salvar Linha")
        btn_salvar.clicked.connect(self.validar_e_aceitar)
        layout.addRow(btn_salvar)

        self.setLayout(layout)
        self.linha_criada = None

    def validar_e_aceitar(self):
        try:
            ci = float(self.combo_ci.currentText().split(" - ")[0])
            ce = float(self.combo_ce.currentText().split(" - ")[0])
            ct = float(self.combo_ct.currentText().split(" - ")[0])

            self.linha_criada = LinhaEletrica(
                id_linha=self.in_id.text(),
                tipo_linha=self.combo_tipo.currentText(),
                l_l=float(self.in_ll.text()),
                c_i=ci, c_e=ce, c_t=ct,
                enterrada=self.chk_enterrada.isChecked(),
                rho=float(self.in_rho.text()),
                blindada=self.chk_blindada.isChecked(),
                r_s=float(self.in_rs.text()),
                mesmo_barramento=self.chk_mesmo_bep.isChecked(),
                conduto_metalico=self.chk_conduto.isChecked(),
                interface_isolante=self.chk_interface.isChecked(),
                u_w=float(self.in_uw.text())
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro nos Dados", f"Preencha números válidos.\nErro: {str(e)}")


# =============================================================================
# DIÁLOGO 2: CADASTRO DE ZONA DE ESTUDO (ZS)
# =============================================================================
class DialogoZona(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar / Editar Zona de Estudo (ZS)")
        self.setMinimumWidth(480)

        layout = QFormLayout()

        self.in_id = QLineEdit("Zona_1_Escritorios")
        self.in_nz = QLineEdit("50")
        self.in_nt = QLineEdit("200")
        self.in_tz = QLineEdit("2000")

        self.combo_rt = QComboBox()
        self.combo_rt.addItems(
            ["1e-5 - Asfalto/Linóleo/Madeira", "1e-4 - Brita/Tapete/Carpete", "1e-3 - Mármore/Cerâmica",
             "1e-2 - Terra/Concreto"])

        self.combo_rp = QComboBox()
        self.combo_rp.addItems(["1.0 - Sem providências / Risco de explosão", "0.5 - Extintores/Hidrantes manuais",
                                "0.2 - Alarme ou sprinklers automáticos"])

        self.combo_rf = QComboBox()
        self.combo_rf.addItems(["1.0 - Explosão / Zonas 0, 20", "0.1 - Alto Risco de Incêndio", "0.01 - Risco Normal",
                                "0.001 - Risco Baixo", "0.0 - Sem Risco"])

        self.combo_hz = QComboBox()
        self.combo_hz.addItems(["1.0 - Sem Perigo Especial", "2.0 - Baixo Pânico (<100 pessoas)",
                                "5.0 - Dificuldade de Evacuação / Hospital", "10.0 - Alto Pânico (>1000 pessoas)"])

        self.combo_rs = QComboBox()
        self.combo_rs.addItems(
            ["1.0 - Robusta (Estrutura metálica ou concreto armado)", "2.0 - Simples (Madeira ou alvenaria simples)"])

        self.combo_pta = QComboBox()
        self.combo_pta.addItems(["1.0 - Sem proteção choque na estrutura", "0.1 - Avisos visíveis de alerta",
                                 "0.01 - Isolação elétrica (3mm PE) / Malha de solo",
                                 "0.001 - Descida de concreto contínuo", "0.0 - Restrições físicas fixas"])

        self.combo_ptu = QComboBox()
        self.combo_ptu.addItems(["1.0 - Sem proteção choque na linha", "0.1 - Avisos visíveis de alerta",
                                 "0.01 - Isolação elétrica na entrada", "0.0 - Restrições físicas"])

        self.in_ca = QLineEdit("0.0")  # Animais
        self.in_cb = QLineEdit("5000000.0")  # Edificação
        self.in_cc = QLineEdit("2000000.0")  # Conteúdo
        self.in_cs = QLineEdit("1000000.0")  # Sistemas
        self.in_cz = QLineEdit("0.0")  # Patrimônio Cultural
        self.in_ct = QLineEdit("8000000.0")  # Total da estrutura

        self.in_wm1 = QLineEdit("0.0")
        self.in_wm2 = QLineEdit("0.0")
        self.chk_continua = QCheckBox("Blindagem Metálica Contínua na Zona")
        self.chk_malha_eq = QCheckBox("Rede de Equipotencialização em Malha")
        self.combo_ks3 = QComboBox()
        self.combo_ks3.addItems(
            ["1.0 - Cabos não blindados (sem roteamento)", "0.5 - Evita grandes laços", "0.2 - Evita laços médios",
             "0.01 - Evita pequenos laços", "0.0001 - Cabos blindados/duto metálico"])

        layout.addRow("ID da Zona:", self.in_id)
        layout.addRow("Pessoas na Zona (nz):", self.in_nz)
        layout.addRow("Pessoas na Estrutura (nt):", self.in_nt)
        layout.addRow("Tempo Exposição (tz h/ano):", self.in_tz)
        layout.addRow("Fator do Piso (rt):", self.combo_rt)
        layout.addRow("Proteção Incêndio (rp):", self.combo_rp)
        layout.addRow("Risco de Incêndio (rf):", self.combo_rf)
        layout.addRow("Perigo Especial / Pânico (hz):", self.combo_hz)
        layout.addRow("Tipo de Construção (rs):", self.combo_rs)

        layout.addRow("Proteção Choque Estrutura (PTA):", self.combo_pta)
        layout.addRow("Proteção Choque Linha (PTU):", self.combo_ptu)

        layout.addRow("Valor Animais - ca (R$):", self.in_ca)
        layout.addRow("Valor Edificação - cb (R$):", self.in_cb)
        layout.addRow("Valor Conteúdo - cc (R$):", self.in_cc)
        layout.addRow("Valor Sistemas - cs (R$):", self.in_cs)
        layout.addRow("Valor Patrimônio - cz (R$):", self.in_cz)
        layout.addRow("Valor Total Estrutura - ct (R$):", self.in_ct)

        layout.addRow("Largura Malha ZPR0/1 (wm1):", self.in_wm1)
        layout.addRow("Largura Malha ZPR1/2 (wm2):", self.in_wm2)
        layout.addRow("", self.chk_continua)
        layout.addRow("", self.chk_malha_eq)
        layout.addRow("Roteamento Cabos (KS3):", self.combo_ks3)

        btn_salvar = QPushButton("Salvar Zona")
        btn_salvar.clicked.connect(self.validar_e_aceitar)
        layout.addRow(btn_salvar)

        self.setLayout(layout)
        self.zona_criada = None

    def validar_e_aceitar(self):
        try:
            rt = float(self.combo_rt.currentText().split(" - ")[0])
            rp = float(self.combo_rp.currentText().split(" - ")[0])
            rf = float(self.combo_rf.currentText().split(" - ")[0])
            hz = float(self.combo_hz.currentText().split(" - ")[0])
            rs = float(self.combo_rs.currentText().split(" - ")[0])
            pta = float(self.combo_pta.currentText().split(" - ")[0])
            ptu = float(self.combo_ptu.currentText().split(" - ")[0])
            ks3 = float(self.combo_ks3.currentText().split(" - ")[0])

            fk = FatoresK(
                w_m1=float(self.in_wm1.text()),
                w_m2=float(self.in_wm2.text()),
                blindagem_continua=self.chk_continua.isChecked(),
                malha_equipotencial=self.chk_malha_eq.isChecked(),
                k_s3=ks3,
                u_w=1.5
            )

            self.zona_criada = ZonaEstudo(
                id_zona=self.in_id.text(),
                n_z=float(self.in_nz.text()),
                n_t=float(self.in_nt.text()),
                t_z=float(self.in_tz.text()),
                r_t=rt, r_p=rp, r_f=rf, h_z=hz, r_s=rs,
                p_ta=pta, p_tu=ptu,
                c_a=float(self.in_ca.text()), c_b=float(self.in_cb.text()),
                c_c=float(self.in_cc.text()), c_s=float(self.in_cs.text()),
                c_z=float(self.in_cz.text()), c_t=float(self.in_ct.text()),
                fatores_k=fk
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro de Conversão",
                                 f"Verifique se digitou apenas números nos campos.\nErro: {str(e)}")


# =============================================================================
# JANELA PRINCIPAL (MainWindow)
# =============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Análise de Risco Completa - ABNT NBR 5419-2:2026")
        self.resize(850, 700)

        self.lista_linhas = []
        self.lista_zonas = []

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)

        self.abas = QTabWidget()
        layout_principal.addWidget(self.abas)

        self.abas.addTab(self.criar_aba_geral(), "1. Geral & Geometria")
        self.abas.addTab(self.criar_aba_linhas(), "2. Linhas Elétricas (SL)")
        self.abas.addTab(self.criar_aba_zonas(), "3. Zonas de Estudo (ZS)")
        self.abas.addTab(self.criar_aba_protecao(), "4. Proteção Global")
        self.abas.addTab(self.criar_aba_relatorios(), "5. Relatório e Veredito")

    def criar_aba_geral(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)

        grp_ng = QGroupBox("Atividade Atmosférica")
        f_ng = QFormLayout(grp_ng)
        self.in_cidade = QLineEdit("Petrolina - PE")
        self.in_ng = QLineEdit("6.0")
        f_ng.addRow("Nome da Localidade:", self.in_cidade)
        f_ng.addRow("Densidade de Raios (NG raios/km²/ano):", self.in_ng)
        layout.addWidget(grp_ng)

        grp_geom = QGroupBox("Geometria da Estrutura Principal")
        f_geom = QFormLayout(grp_geom)
        self.in_l = QLineEdit("40.0")
        self.in_w = QLineEdit("30.0")
        self.in_hmin = QLineEdit("15.0")
        self.in_hmax = QLineEdit("20.0")
        self.combo_cd = QComboBox()
        self.combo_cd.addItems(["1.0 - Isolada", "0.5 - Cercada mesma altura", "0.25 - Cercada objetos altos",
                                "2.0 - Topo de colina/monte"])

        f_geom.addRow("Comprimento L (m):", self.in_l)
        f_geom.addRow("Largura W (m):", self.in_w)
        f_geom.addRow("Altura Corpo Principal H_min (m):", self.in_hmin)
        f_geom.addRow("Altura Saliência H_max (m):", self.in_hmax)
        f_geom.addRow("Fator Localização (CD):", self.combo_cd)
        layout.addWidget(grp_geom)

        grp_adj = QGroupBox("Estrutura Adjacente (Vizinhança Conectada)")
        f_adj = QFormLayout(grp_adj)
        self.chk_adj = QCheckBox("Considerar Estrutura Adjacente")
        self.in_lj = QLineEdit("10.0")
        self.in_wj = QLineEdit("10.0")
        self.in_hj = QLineEdit("5.0")
        self.combo_cdj = QComboBox()
        self.combo_cdj.addItems(["1.0 - Isolada", "0.5 - Mesma altura", "0.25 - Mais baixa"])

        f_adj.addRow("", self.chk_adj)
        f_adj.addRow("Comprimento LJ (m):", self.in_lj)
        f_adj.addRow("Largura WJ (m):", self.in_wj)
        f_adj.addRow("Altura HJ (m):", self.in_hj)
        f_adj.addRow("Fator CDJ:", self.combo_cdj)
        layout.addWidget(grp_adj)

        return aba

    def criar_aba_linhas(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)

        self.tabela_linhas = QTableWidget(0, 5)
        self.tabela_linhas.setHorizontalHeaderLabels(["ID da Linha", "Tipo", "LL (m)", "Blindada", "UW (kV)"])
        self.tabela_linhas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela_linhas)

        botoes = QHBoxLayout()
        btn_add = QPushButton("➕ Adicionar Linha")
        btn_add.clicked.connect(self.adicionar_linha)
        btn_del = QPushButton("❌ Remover Selecionada")
        btn_del.clicked.connect(self.remover_linha)

        botoes.addWidget(btn_add)
        botoes.addWidget(btn_del)
        layout.addLayout(botoes)

        return aba

    def adicionar_linha(self):
        dlg = DialogoLinha(self)
        if dlg.exec() and dlg.linha_criada:
            linha = dlg.linha_criada
            self.lista_linhas.append(linha)

            row = self.tabela_linhas.rowCount()
            self.tabela_linhas.insertRow(row)
            self.tabela_linhas.setItem(row, 0, QTableWidgetItem(linha.id_linha))
            self.tabela_linhas.setItem(row, 1, QTableWidgetItem(linha.tipo_linha))
            self.tabela_linhas.setItem(row, 2, QTableWidgetItem(str(linha.L_L)))
            self.tabela_linhas.setItem(row, 3, QTableWidgetItem("Sim" if linha.blindada else "Não"))
            self.tabela_linhas.setItem(row, 4, QTableWidgetItem(str(linha.U_W)))

    def remover_linha(self):
        row = self.tabela_linhas.currentRow()
        if row >= 0:
            self.tabela_linhas.removeRow(row)
            self.lista_linhas.pop(row)

    def criar_aba_zonas(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)

        self.tabela_zonas = QTableWidget(0, 5)
        self.tabela_zonas.setHorizontalHeaderLabels(
            ["ID da Zona", "nz (Pessoas)", "tz (h/ano)", "Risco Incêndio", "Valor Total (ct)"])
        self.tabela_zonas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela_zonas)

        botoes = QHBoxLayout()
        btn_add = QPushButton("➕ Adicionar Zona de Estudo")
        btn_add.clicked.connect(self.adicionar_zona)
        btn_del = QPushButton("❌ Remover Selecionada")
        btn_del.clicked.connect(self.remover_zona)

        botoes.addWidget(btn_add)
        botoes.addWidget(btn_del)
        layout.addLayout(botoes)

        return aba

    def adicionar_zona(self):
        dlg = DialogoZona(self)
        if dlg.exec() and dlg.zona_criada:
            zona = dlg.zona_criada
            self.lista_zonas.append(zona)

            row = self.tabela_zonas.rowCount()
            self.tabela_zonas.insertRow(row)
            self.tabela_zonas.setItem(row, 0, QTableWidgetItem(zona.id_zona))
            self.tabela_zonas.setItem(row, 1, QTableWidgetItem(str(zona.n_z)))
            self.tabela_zonas.setItem(row, 2, QTableWidgetItem(str(zona.t_z)))
            self.tabela_zonas.setItem(row, 3, QTableWidgetItem(str(zona.r_f)))
            self.tabela_zonas.setItem(row, 4, QTableWidgetItem(f"R$ {zona.c_t:,.2f}"))

    def remover_zona(self):
        row = self.tabela_zonas.currentRow()
        if row >= 0:
            self.tabela_zonas.removeRow(row)
            self.lista_zonas.pop(row)

    def criar_aba_protecao(self):
        aba = QWidget()
        layout = QFormLayout(aba)

        self.combo_spda = QComboBox()
        self.combo_spda.addItems(["nenhum", "IV", "III", "II", "I"])

        self.combo_dps = QComboBox()
        self.combo_dps.addItems(["nenhum", "III-IV", "II", "I"])

        self.combo_peb = QComboBox()
        self.combo_peb.addItems(
            ["1.0 - Sem DPS Classe I na entrada", "0.05 - DPS Classe I Nível III-IV", "0.02 - DPS Classe I Nível II",
             "0.01 - DPS Classe I Nível I"])

        self.chk_falha_sistema_vida = QCheckBox(
            "Falhas nos sistemas colocam vidas humanas em risco imediato (ex: UTI / Explosão)")

        layout.addRow("Nível SPDA Externo (PB):", self.combo_spda)
        layout.addRow("Nível Coordenado de DPS (PSPD):", self.combo_dps)
        layout.addRow("Equipotencialização Entrada (PEB):", self.combo_peb)
        layout.addRow("", self.chk_falha_sistema_vida)

        return aba

    def criar_aba_relatorios(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)

        self.btn_calcular = QPushButton("🚀 Executar Análise de Risco Completa (R1, R3, F, R4)")
        self.btn_calcular.setStyleSheet(
            "background-color: #1B4F72; color: white; font-weight: bold; font-size: 14px; padding: 14px;")
        self.btn_calcular.clicked.connect(self.executar_analise)
        layout.addWidget(self.btn_calcular)

        self.area_relatorio = QTextEdit()
        self.area_relatorio.setReadOnly(True)
        # ESTILO DEFINITIVO: Texto escuro sobre fundo branco puro
        self.area_relatorio.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, 'Courier New', monospace;
                background-color: #FFFFFF;
                color: #1C2833;
                font-size: 13px;
                padding: 10px;
                border: 1px solid #BDC3C7;
            }
        """)
        layout.addWidget(self.area_relatorio)

        return aba

    def executar_analise(self):
        try:
            if not self.lista_zonas or not self.lista_linhas:
                QMessageBox.warning(self, "Listas Vazia",
                                    "Cadastre pelo menos uma Zona de Estudo e uma Linha Elétrica para rodar a análise.")
                return

            cd = float(self.combo_cd.currentText().split(" - ")[0])
            cdj = float(self.combo_cdj.currentText().split(" - ")[0])

            est = Estrutura(
                l=float(self.in_l.text()), w=float(self.in_w.text()),
                h_min=float(self.in_hmin.text()), h_max=float(self.in_hmax.text()),
                c_d=cd,
                tem_adjacente=self.chk_adj.isChecked(),
                l_j=float(self.in_lj.text()), w_j=float(self.in_wj.text()), h_j=float(self.in_hj.text()), c_dj=cdj
            )

            peb = float(self.combo_peb.currentText().split(" - ")[0])
            z1 = self.lista_zonas[0]

            probs = Probabilidades(
                nivel_spda=self.combo_spda.currentText(),
                nivel_dps=self.combo_dps.currentText(),
                p_ta=z1.P_TA, p_tu=z1.P_TU, p_eb=peb,
                fatores_k=z1.fatores_k
            )

            ng = float(self.in_ng.text())
            analisador = AnalisadorRisco(
                n_g=ng,
                estrutura=est,
                zonas=self.lista_zonas,
                linhas=self.lista_linhas,
                probabilidades=probs
            )

            falha_vida = self.chk_falha_sistema_vida.isChecked()
            r1 = analisador.calcular_r1_total(falha_sistema_risco_vida=falha_vida)
            r3 = analisador.calcular_r3_total()
            f_total = analisador.calcular_f_total()
            r4 = analisador.calcular_r4_total()

            rel = f"======================================================================\n"
            rel += f"             RELATÓRIO NORMATIVO DE RISCO - ABNT NBR 5419-2:2026\n"
            rel += f"======================================================================\n\n"
            rel += f"📍 Localidade: {self.in_cidade.text()} | NG: {ng} raios/km²/ano\n"
            rel += f"🏢 Estrutura: {est.L}m x {est.W}m | Hmin: {est.H_min}m | Hmax: {est.H_max}m\n"
            rel += f"📁 Zonas de Estudo Processadas: {len(self.lista_zonas)}\n"
            rel += f"⚡ Linhas Elétricas Processadas: {len(self.lista_linhas)}\n"
            rel += f"🛡️ Proteção: SPDA: {probs.nivel_spda} | DPS: {probs.nivel_dps}\n"
            rel += f"----------------------------------------------------------------------\n\n"

            rel += f"1. RISCO DE PERDA DE VIDA HUMANA (R1)\n"
            rel += f"   - R1 Calculado: {r1:.4e}\n"
            rel += f"   - R1 Tolerável: {analisador.RT_1:.4e}\n"
            rel += f"   - Veredito: {'✅ APROVADO (R1 <= RT)' if r1 <= analisador.RT_1 else '❌ REPROVADO (Necessita Proteção)'}\n\n"

            rel += f"2. RISCO AO PATRIMÔNIO CULTURAL (R3)\n"
            rel += f"   - R3 Calculado: {r3:.4e}\n"
            rel += f"   - R3 Tolerável: {analisador.RT_3:.4e}\n"
            rel += f"   - Veredito: {'✅ APROVADO (R3 <= RT)' if r3 <= analisador.RT_3 else '❌ REPROVADO (Necessita Proteção)'}\n\n"

            rel += f"3. FREQUÊNCIA DE DANOS AOS SISTEMAS (F)\n"
            rel += f"   - Frequência Calculada: {f_total:.4f} falhas/ano\n"
            rel += f"   - Limite Tolerável FT:  1.0000 falhas/ano\n"
            rel += f"   - Veredito: {'✅ SISTEMAS SEGUROS' if f_total <= 1.0 else '❌ NECESSITA MEDIDAS MPS'}\n\n"

            ct_total = sum(z.c_t for z in self.lista_zonas) / len(self.lista_zonas)
            custo_perda = r4 * ct_total
            rel += f"4. RISCO ECONÔMICO (R4 - ANEXO D)\n"
            rel += f"   - R4 Calculado: {r4:.4e}\n"
            rel += f"   - Custo Anual Provável de Perdas: R$ {custo_perda:,.2f}\n"

            self.area_relatorio.setText(rel)

        except Exception as e:
            QMessageBox.critical(self, "Erro nos Dados", f"Falha ao executar cálculo.\nErro: {str(e)}")