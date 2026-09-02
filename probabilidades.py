from linhas_eletricas import LinhaEletrica


class FatoresK:
    def __init__(self, w_m1: float = 0.0, w_m2: float = 0.0,
                 blindagem_continua: bool = False, malha_equipotencial: bool = False,
                 k_s3: float = 1.0, u_w: float = 1.5, interface_optica: bool = False):
        self.w_m1 = float(w_m1)
        self.w_m2 = float(w_m2)
        self.blindagem_continua = blindagem_continua
        self.malha_equipotencial = malha_equipotencial
        self.K_S3 = float(k_s3)
        self.U_W = float(u_w)
        self.interface_optica = interface_optica

    def calcular_ks1(self) -> float:
        if self.blindagem_continua: return 1e-4
        k = min(0.12 * self.w_m1, 1.0)
        return k / 2.0 if self.malha_equipotencial else k

    def calcular_ks2(self) -> float:
        if self.blindagem_continua: return 1e-4
        k = min(0.12 * self.w_m2, 1.0)
        return k / 2.0 if self.malha_equipotencial else k

    def calcular_pms(self, uw_linha: float = None) -> float:
        """
        Calcula o PMS. Agora pode receber o UW dinamicamente da linha avaliada.
        """
        if self.interface_optica: return 0.0
        uw = uw_linha if uw_linha is not None else self.U_W
        ks4 = min(1.0 / max(uw, 0.001), 1.0)
        return (self.calcular_ks1() * self.calcular_ks2() * self.K_S3 * ks4) ** 2


class Probabilidades:
    def __init__(self, nivel_spda: str, nivel_dps: str,
                 p_ta: float = 1.0, p_tu: float = 1.0, p_eb: float = 1.0,
                 fatores_k: FatoresK = None):
        self.nivel_spda = str(nivel_spda)
        self.nivel_dps = str(nivel_dps)
        self.P_TA = float(p_ta)
        self.P_TU = float(p_tu)
        self.P_EB = float(p_eb)
        self.fk = fatores_k if fatores_k else FatoresK()

    def obter_pb(self) -> float:
        return {'nenhum': 1.0, 'IV': 0.2, 'III': 0.1, 'II': 0.05, 'I': 0.02}.get(self.nivel_spda, 1.0)

    def obter_pspd(self) -> float:
        return {'nenhum': 1.0, 'III-IV': 0.05, 'II': 0.02, 'I': 0.01}.get(self.nivel_dps, 1.0)

    def obter_cld_cli(self, linha: LinhaEletrica) -> tuple:
        if linha is None:
            return (1.0, 1.0)
        if linha.interface_isolante or linha.conduto_metalico:
            return (0.0, 0.0)
        if linha.blindada and linha.mesmo_barramento:
            return (1.0, 0.0)
        if linha.blindada and not linha.mesmo_barramento:
            return (1.0, 0.3 if linha.enterrada else 0.1)
        if linha.tipo_linha == 'energia' and linha.C_T == 1.0:
            return (1.0, 0.2)
        return (1.0, 1.0)

    def obter_pld(self, linha: LinhaEletrica) -> float:
        if linha is None or not linha.blindada or not linha.mesmo_barramento:
            return 1.0
        uw = linha.U_W
        rs = linha.R_S
        if 5.0 < rs <= 20.0:
            if uw >= 6.0: return 0.8
            if uw >= 4.0: return 0.9
            if uw >= 2.5: return 0.95
            return 1.0
        elif 1.0 < rs <= 5.0:
            if uw >= 6.0: return 0.1
            if uw >= 4.0: return 0.3
            if uw >= 2.5: return 0.8
            return 0.9
        elif rs <= 1.0:
            if uw >= 6.0: return 0.02
            if uw >= 4.0: return 0.04
            if uw >= 2.5: return 0.4
            return 0.6
        return 1.0

    def obter_pli(self, linha: LinhaEletrica) -> float:
        if linha is None:
            return 1.0
        uw = linha.U_W
        if linha.tipo_linha == 'energia':
            if uw >= 6.0: return 0.1
            if uw >= 4.0: return 0.16
            if uw >= 2.5: return 0.3
            if uw >= 1.5: return 0.6
            return 1.0
        else:
            if uw >= 6.0: return 0.04
            if uw >= 4.0: return 0.08
            if uw >= 2.5: return 0.2
            if uw >= 1.5: return 0.5
            return 1.0

    def calcular_pa(self) -> float:
        return self.P_TA * self.obter_pb()

    def calcular_pb(self) -> float:
        return self.obter_pb()

    def calcular_pc(self, linha: LinhaEletrica = None) -> float:
        c_ld, _ = self.obter_cld_cli(linha)
        return self.obter_pspd() * c_ld

    def calcular_pm(self, fk_zona: FatoresK, linha: LinhaEletrica = None) -> float:
        uw = linha.U_W if linha else 1.5
        return self.obter_pspd() * fk_zona.calcular_pms(uw_linha=uw)

    def calcular_pu(self, linha: LinhaEletrica) -> float:
        c_ld, _ = self.obter_cld_cli(linha)
        return self.P_TU * self.P_EB * self.obter_pld(linha) * c_ld

    def calcular_pv(self, linha: LinhaEletrica) -> float:
        c_ld, _ = self.obter_cld_cli(linha)
        return self.P_EB * self.obter_pld(linha) * c_ld

    def calcular_pw(self, linha: LinhaEletrica) -> float:
        c_ld, _ = self.obter_cld_cli(linha)
        return self.obter_pspd() * self.obter_pld(linha) * c_ld

    def calcular_pz(self, linha: LinhaEletrica) -> float:
        _, c_li = self.obter_cld_cli(linha)
        return self.obter_pspd() * self.obter_pli(linha) * c_li