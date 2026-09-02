import math


class Estrutura:
    def __init__(self,
                 l: float, w: float, h_min: float, h_max: float, c_d: float,
                 tem_adjacente: bool = False, l_j: float = 0.0, w_j: float = 0.0, h_j: float = 0.0, c_dj: float = 1.0,
                 risco_ambiental: bool = False, l_fe: float = 0.0, t_e: float = 0.0):
        self.L = float(l)
        self.W = float(w)
        self.H_min = float(h_min)
        self.H_max = max(float(h_max), float(h_min))
        self.C_D = float(c_d)

        self.tem_adjacente = tem_adjacente
        self.L_J = float(l_j)
        self.W_J = float(w_j)
        self.H_J = float(h_j)
        self.C_DJ = float(c_dj)

        self.risco_ambiental = risco_ambiental
        self.L_FE = float(l_fe)
        self.t_e = min(float(t_e), 8760.0)

    def calcular_ad(self) -> float:
        ad_principal = (self.L * self.W) + 2 * (3 * self.H_min) * (self.L + self.W) + math.pi * (3 * self.H_min) ** 2
        ad_saliencia = math.pi * (3 * self.H_max) ** 2
        return max(ad_principal, ad_saliencia)

    def calcular_am(self) -> float:
        return 2 * 500 * (self.L + self.W) + math.pi * (500 ** 2)

    def calcular_adj(self) -> float:
        if not self.tem_adjacente:
            return 0.0
        return (self.L_J * self.W_J) + 2 * (3 * self.H_J) * (self.L_J + self.W_J) + math.pi * (3 * self.H_J) ** 2

    def calcular_le(self) -> float:
        if not self.risco_ambiental:
            return 0.0
        return self.L_FE * (self.t_e / 8760.0)