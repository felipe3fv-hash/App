from estrutura import Estrutura

class EventosPerigosos:
    def __init__(self, n_g: float, estrutura: Estrutura):
        self.N_G = float(n_g)
        self.est = estrutura

    def calcular_nd(self) -> float:
        return self.N_G * self.est.calcular_ad() * self.est.C_D * 1e-6

    def calcular_nm(self) -> float:
        return self.N_G * self.est.calcular_am() * 1e-6

    def calcular_ndj(self, c_t: float) -> float:
        if not self.est.tem_adjacente:
            return 0.0
        return self.N_G * self.est.calcular_adj() * self.est.C_DJ * c_t * 1e-6