class ZonaEstudo:
    def __init__(self,
                 id_zona: str,
                 n_z: float = 1.0, n_t: float = 1.0, t_z: float = 8760.0,
                 l_t: float = 1e-2, l_f: float = 1e-1, l_o: float = 1e-3,
                 r_t: float = 1.0, r_p: float = 1.0, r_f: float = 1.0,
                 h_z: float = 1.0, r_s: float = 1.0,
                 p_ta: float = 1.0, p_tu: float = 1.0,
                 c_a: float = 0.0, c_b: float = 0.0, c_c: float = 0.0,
                 c_s: float = 0.0, c_z: float = 0.0, c_t: float = 1.0,
                 fatores_k=None):
        self.id_zona = str(id_zona)

        self.n_z = float(n_z)
        self.n_t = max(float(n_t), 1.0)
        self.t_z = min(float(t_z), 8760.0)

        self.L_T = float(l_t)
        self.L_F = float(l_f)
        self.L_O = float(l_o)

        self.r_t = float(r_t)
        self.r_p = float(r_p)
        self.r_f = float(r_f)
        self.h_z = float(h_z)
        self.r_s = float(r_s)

        self.P_TA = float(p_ta)
        self.P_TU = float(p_tu)

        self.c_a = float(c_a)
        self.c_b = float(c_b)
        self.c_c = float(c_c)
        self.c_s = float(c_s)
        self.c_z = float(c_z)
        self.c_t = max(float(c_t), 1.0)

        self.fatores_k = fatores_k

    def _fator_presenca(self) -> float:
        return (self.n_z / self.n_t) * (self.t_z / 8760.0)

    def calcular_la1(self) -> float: return self.r_t * self.L_T * self._fator_presenca() * self.r_s

    def calcular_lu1(self) -> float: return self.calcular_la1()

    def calcular_lb1(self, l_e: float = 0.0) -> float:
        l_f_total = self.L_F + float(l_e)
        return self.r_p * self.r_f * self.h_z * l_f_total * self._fator_presenca() * self.r_s

    def calcular_lv1(self, l_e: float = 0.0) -> float: return self.calcular_lb1(l_e)

    def calcular_lc1(self) -> float: return self.L_O * self._fator_presenca() * self.r_s

    def calcular_lm1(self) -> float: return self.calcular_lc1()

    def calcular_lw1(self) -> float: return self.calcular_lc1()

    def calcular_lz1(self) -> float: return self.calcular_lc1()

    def calcular_lb3(self) -> float: return self.r_p * self.r_f * self.L_F * (self.c_z / self.c_t)

    def calcular_lv3(self) -> float: return self.calcular_lb3()

    def calcular_la4(self) -> float: return self.r_t * self.L_T * (self.c_a / self.c_t)

    def calcular_lu4(self) -> float: return self.calcular_la4()

    def calcular_lb4(self) -> float:
        soma_bens = self.c_a + self.c_b + self.c_c + self.c_s
        return self.r_p * self.r_f * self.L_F * (soma_bens / self.c_t)

    def calcular_lv4(self) -> float: return self.calcular_lb4()

    def calcular_lc4(self) -> float: return self.L_O * (self.c_s / self.c_t)

    def calcular_lm4(self) -> float: return self.calcular_lc4()

    def calcular_lw4(self) -> float: return self.calcular_lc4()

    def calcular_lz4(self) -> float: return self.calcular_lc4()