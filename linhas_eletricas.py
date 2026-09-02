import math


class LinhaEletrica:
    def __init__(self,
                 id_linha: str, tipo_linha: str, l_l: float,
                 c_i: float, c_e: float, c_t: float,
                 enterrada: bool = False, rho: float = 400.0,
                 blindada: bool = False, r_s: float = 0.0,
                 mesmo_barramento: bool = False, conduto_metalico: bool = False,
                 interface_isolante: bool = False, u_w: float = 1.5):
        self.id_linha = str(id_linha)
        self.tipo_linha = str(tipo_linha)
        self.L_L = float(l_l)
        self.C_I = float(c_i)
        self.C_E = float(c_e)
        self.C_T = float(c_t)

        self.enterrada = enterrada
        self.rho = float(rho)

        self.blindada = blindada
        self.R_S = float(r_s)
        self.mesmo_barramento = mesmo_barramento
        self.conduto_metalico = conduto_metalico
        self.interface_isolante = interface_isolante
        self.U_W = float(u_w)

    def calcular_al(self) -> float:
        if self.enterrada and self.rho > 400.0:
            return 0.6 * math.sqrt(self.rho) * self.L_L
        return 40.0 * self.L_L

    def calcular_ai(self) -> float:
        return 4000.0 * self.L_L