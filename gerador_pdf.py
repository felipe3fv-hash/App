import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def gerar_pdf_laudo(cidade: str, ng: float, est, zonas: list, linhas: list, resultados: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        'TituloLaudo',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1B4F72'),
        spaceAfter=12
    )

    # 1. Cabeçalho
    elements.append(Paragraph("LAUDO TÉCNICO DE ANÁLISE DE RISCO - SPDA / MPS", titulo_style))
    elements.append(Paragraph("<b>Norma de Referência:</b> ABNT NBR 5419-2:2026", styles['Normal']))
    elements.append(Spacer(1, 12))

    # 2. Dados Gerais
    dados = [
        ["Localidade / Cidade:", cidade],
        ["Densidade de Raios (NG):", f"{ng} raios/km²/ano"],
        ["Dimensões Físicas:", f"{est.L}m x {est.W}m | Hmin: {est.H_min}m | Hmax: {est.H_max}m"],
        ["Zonas Processadas:", str(len(zonas))],
        ["Linhas Processadas:", str(len(linhas))]
    ]
    t_dados = Table(dados, colWidths=[180, 340])
    t_dados.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F2F4F4')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(t_dados)
    elements.append(Spacer(1, 16))

    # 3. Tabela de Veredito dos Riscos
    elements.append(Paragraph("<b>SÍNTESE DOS RISCOS AVALIADOS E VEREDITO</b>", styles['Heading2']))

    st_r1 = "APROVADO (R1 <= RT)" if resultados['r1'] <= 1e-5 else "REPROVADO (EXIGE SPDA/MPS)"
    st_r3 = "APROVADO (R3 <= RT)" if resultados['r3'] <= 1e-4 else "REPROVADO (EXIGE SPDA/MPS)"
    st_f = "SISTEMAS SEGUROS" if resultados['f'] <= 1.0 else "REPROVADO (EXIGE MPS)"

    matriz_riscos = [
        ["Risco Normativo", "Valor Calculado", "Limite Tolerável", "Veredito Técnico"],
        ["Perda de Vida Humana (R1)", f"{resultados['r1']:.2e}", "1.00e-05", st_r1],
        ["Patrimônio Cultural (R3)", f"{resultados['r3']:.2e}", "1.00e-04", st_r3],
        ["Frequência de Danos (F)", f"{resultados['f']:.4f}", "1.0000 falhas/ano", st_f],
        ["Risco Econômico (R4)", f"{resultados['r4']:.2e}", "Anexo D", f"R$ {resultados['custo_perda']:,.2f}/ano"]
    ]

    t_riscos = Table(matriz_riscos, colWidths=[150, 100, 110, 160])
    t_riscos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B4F72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(t_riscos)

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes