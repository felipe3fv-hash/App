from typing import List
from estrutura import Estrutura
from eventos_perigosos import EventosPerigosos
from linhas_eletricas import LinhaEletrica
from probabilidades import Probabilidades
from perdas import ZonaEstudo


class AnalisadorRisco:
    def __init__(self,
                 n_g: float,
                 estrutura: Estrutura,
                 zonas: List[ZonaEstudo],
                 linhas: List[LinhaEletrica],
                 probabilidades: Probabilidades):
        self.ev = EventosPerigosos(n_g=n_g, estrutura=estrutura)
        self.est = estrutura
        self.zonas = zonas
        self.linhas = linhas
        self.pr = probabilidades

        self.RT_1 = 1e-5
        self.RT_3 = 1e-4

    def _obter_probabilidades_compostas(self, fk_zona):
        """Calcula PC e PM totais usando a composição de múltiplas linhas."""
        pc_compl = 1.0
        pm_compl = 1.0

        if self.linhas:
            for linha in self.linhas:
                pc_compl *= (1.0 - self.pr.calcular_pc(linha))
                pm_compl *= (1.0 - self.pr.calcular_pm(fk_zona, linha))
        else:
            pc_compl = 1.0 - self.pr.calcular_pc(None)
            pm_compl = 1.0 - self.pr.calcular_pm(fk_zona, None)

        return (1.0 - pc_compl), (1.0 - pm_compl)

    def calcular_r1_total(self, falha_sistema_risco_vida: bool = False) -> float:
        nd = self.ev.calcular_nd()
        nm = self.ev.calcular_nm()
        l_e = self.est.calcular_le()

        r1_soma = 0.0

        for zona in self.zonas:
            ra = nd * self.pr.calcular_pa() * zona.calcular_la1()
            rb = nd * self.pr.calcular_pb() * zona.calcular_lb1(l_e)
            r1_soma += (ra + rb)

            if falha_sistema_risco_vida:
                pc_total, pm_total = self._obter_probabilidades_compostas(zona.fatores_k)
                rc = nd * pc_total * zona.calcular_lc1()
                rm = nm * pm_total * zona.calcular_lm1()
                r1_soma += (rc + rm)

            for linha in self.linhas:
                nl = self.ev.N_G * linha.calcular_al() * linha.C_I * linha.C_E * linha.C_T * 1e-6
                ni = self.ev.N_G * linha.calcular_ai() * linha.C_I * linha.C_E * linha.C_T * 1e-6
                ndj = self.ev.calcular_ndj(linha.C_T)

                ru = (nl + ndj) * self.pr.calcular_pu(linha) * zona.calcular_lu1()
                rv = (nl + ndj) * self.pr.calcular_pv(linha) * zona.calcular_lv1(l_e)
                r1_soma += (ru + rv)

                if falha_sistema_risco_vida:
                    rw = (nl + ndj) * self.pr.calcular_pw(linha) * zona.calcular_lw1()
                    rz = ni * self.pr.calcular_pz(linha) * zona.calcular_lz1()
                    r1_soma += (rw + rz)

        return r1_soma

    def calcular_r3_total(self) -> float:
        nd = self.ev.calcular_nd()
        r3_soma = 0.0

        for zona in self.zonas:
            rb3 = nd * self.pr.calcular_pb() * zona.calcular_lb3()
            r3_soma += rb3

            for linha in self.linhas:
                nl = self.ev.N_G * linha.calcular_al() * linha.C_I * linha.C_E * linha.C_T * 1e-6
                ndj = self.ev.calcular_ndj(linha.C_T)
                rv3 = (nl + ndj) * self.pr.calcular_pv(linha) * zona.calcular_lv3()
                r3_soma += rv3

        return r3_soma

    def calcular_f_total(self) -> float:
        nd = self.ev.calcular_nd()
        nm = self.ev.calcular_nm()

        f_soma = 0.0

        zona_base = self.zonas[0] if self.zonas else None
        fk_base = zona_base.fatores_k if zona_base else self.pr.fk

        pc_total, pm_total = self._obter_probabilidades_compostas(fk_base)
        fc = nd * pc_total
        fm = nm * pm_total
        f_soma += (fc + fm)

        for linha in self.linhas:
            nl = self.ev.N_G * linha.calcular_al() * linha.C_I * linha.C_E * linha.C_T * 1e-6
            ni = self.ev.N_G * linha.calcular_ai() * linha.C_I * linha.C_E * linha.C_T * 1e-6
            ndj = self.ev.calcular_ndj(linha.C_T)

            fv = (nl + ndj) * self.pr.P_EB
            fw = (nl + ndj) * self.pr.calcular_pw(linha)
            fz = ni * self.pr.calcular_pz(linha)
            f_soma += (fv + fw + fz)

        return f_soma

    def calcular_r4_total(self) -> float:
        nd = self.ev.calcular_nd()
        nm = self.ev.calcular_nm()
        r4_soma = 0.0

        for zona in self.zonas:
            ra4 = nd * self.pr.calcular_pa() * zona.calcular_la4()
            rb4 = nd * self.pr.calcular_pb() * zona.calcular_lb4()

            pc_total, pm_total = self._obter_probabilidades_compostas(zona.fatores_k)
            rc4 = nd * pc_total * zona.calcular_lc4()
            rm4 = nm * pm_total * zona.calcular_lm4()

            r4_soma += (ra4 + rb4 + rc4 + rm4)

            for linha in self.linhas:
                nl = self.ev.N_G * linha.calcular_al() * linha.C_I * linha.C_E * linha.C_T * 1e-6
                ni = self.ev.N_G * linha.calcular_ai() * linha.C_I * linha.C_E * linha.C_T * 1e-6
                ndj = self.ev.calcular_ndj(linha.C_T)

                ru4 = (nl + ndj) * self.pr.calcular_pu(linha) * zona.calcular_lu4()
                rv4 = (nl + ndj) * self.pr.calcular_pv(linha) * zona.calcular_lv4()
                rw4 = (nl + ndj) * self.pr.calcular_pw(linha) * zona.calcular_lw4()
                rz4 = ni * self.pr.calcular_pz(linha) * zona.calcular_lz4()
                r4_soma += (ru4 + rv4 + rw4 + rz4)

        return r4_soma