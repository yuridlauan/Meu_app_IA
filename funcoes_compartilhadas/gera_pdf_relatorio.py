# funcoes_compartilhadas/gera_pdf_relatorio.py

from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib.styles import getSampleStyleSheet


def gerar_pdf_relatorio(
    cidade,
    mes,
    tipo_servico,
    opcao_pendencia,
    protocolos,
    vistorias,
    cercons,
    nao_certificou,
    notificados,
    protocolados,
    vistoria_sem_cercon,
    cercons_vencidos,
    cercons_30,
    df_protocolos
):

    buffer = BytesIO()

    pdf = SimpleDocTemplate(buffer)

    estilos = getSampleStyleSheet()

    conteudo = []

    conteudo.append(
        Paragraph(
            "RELATÓRIO OPERACIONAL",
            estilos["Title"]
        )
    )

    conteudo.append(Spacer(1, 12))

    conteudo.append(
        Paragraph(
            f"<b>Cidade:</b> {cidade}",
            estilos["Normal"]
        )
    )

    conteudo.append(
        Paragraph(
            f"<b>Mês:</b> {mes}",
            estilos["Normal"]
        )
    )

    conteudo.append(Spacer(1, 20))

    conteudo.append(
        Paragraph(
            "RESUMO GERAL",
            estilos["Heading2"]
        )
    )

    conteudo.append(
        Paragraph(
            f"Protocolos: {protocolos}",
            estilos["Normal"]
        )
    )

    conteudo.append(
        Paragraph(
            f"Vistorias: {vistorias}",
            estilos["Normal"]
        )
    )

    conteudo.append(
        Paragraph(
            f"Cercons: {cercons}",
            estilos["Normal"]
        )
    )

    conteudo.append(
        Paragraph(
            f"Não Certificou: {nao_certificou}",
            estilos["Normal"]
        )
    )

    conteudo.append(
        Paragraph(
            f"Notificados: {notificados}",
            estilos["Normal"]
        )
    )

    conteudo.append(Spacer(1, 20))

    conteudo.append(
        Paragraph(
            "PENDÊNCIAS",
            estilos["Heading2"]
        )
    )

    conteudo.append(
        Paragraph(
            f"Protocolados sem vistoria: {protocolados}",
            estilos["Normal"]
        )
    )

    conteudo.append(
        Paragraph(
            f"Vistorias sem Cercon: {vistoria_sem_cercon}",
            estilos["Normal"]
        )
    )

    conteudo.append(
        Paragraph(
            f"Cercons vencidos: {cercons_vencidos}",
            estilos["Normal"]
        )
    )

    conteudo.append(
        Paragraph(
            f"Vencem em 30 dias: {cercons_30}",
            estilos["Normal"]
        )
    )

    conteudo.append(Spacer(1, 20))

    conteudo.append(
        Paragraph(
            f"Tipo de Serviço: {tipo_servico}",
            estilos["Heading2"]
        )
    )

    conteudo.append(
        Paragraph(
            f"Pendência Selecionada: {opcao_pendencia}",
            estilos["Heading2"]
        )
    )

    conteudo.append(Spacer(1, 20))

    conteudo.append(
        Paragraph(
            "PROTOCOLOS ENCONTRADOS",
            estilos["Heading2"]
        )
    )

    for _, linha in df_protocolos.iterrows():

        texto = (
            f"{linha['Data de Protocolo']} | "
            f"{linha['Nº de Protocolo']} | "
            f"{linha['Nome Fantasia']} | "
            f"{linha['Cidade']} | "
            f"{linha['Andamento']}"
        )

        conteudo.append(
            Paragraph(
                texto,
                estilos["Normal"]
            )
        )

    pdf.build(conteudo)

    buffer.seek(0)

    return buffer