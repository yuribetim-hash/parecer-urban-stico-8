import streamlit as st

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO

# -------------------------
# PERGUNTAS + REGRAS
# -------------------------
perguntas = [
    {
        "id": "aceite_prazo",
        "pergunta": "Aceite Urbanístico deferido dentro do prazo?",
        "opcoes": ["Sim", "Não"],
        "regras": {
            "Não": {
                "tipo": "inconformidade",
                "texto": "Apresentar Aceite urbanístico aprovado, dentro do prazo de validade."
            }
        }
    },
    {
        "id": "alteracao_lotes",
        "pergunta": "Alterou a quantidade de lotes aprovado no Aceite urbanístico?",
        "opcoes": ["Não", "Sim"],
        "regras": {
            "Sim": {
                "tipo": "inconformidade",
                "texto": "Deverá retornar à análise do aceite urbanístico para compatibilização do empreendimento. Obs¹ – verificar compatibilidade dos projetos de redes de água, esgoto, drenagem, licenciamento ambiental e acesso viário."
            }
        }
    }
]

# -------------------------
# FUNÇÕES
# -------------------------
def analisar(respostas, perguntas):
    inconformidades = []

    for p in perguntas:
        r = respostas[p["id"]]

        if r in p.get("regras", {}):
            regra = p["regras"][r]
            inconformidades.append(regra["texto"])

    return inconformidades


def definir_conclusao(inconformidades):
    if inconformidades:
        return "DESFAVORÁVEL"
    return "FAVORÁVEL"


def gerar_parecer(dados, respostas, observacoes, inconformidades, conclusao):

    texto = f"""
PARECER DE ANÁLISE URBANÍSTICA

N° Protocolo: {dados['protocolo']}
Tipo do Empreendimento: {dados['tipo']}
Requerente: {dados['interessado']}
Número de Lotes: {dados['n_lotes']}
"""

    # RESPOSTAS + OBSERVAÇÕES (sem perguntas)
    for p in perguntas:
        resp = respostas[p["id"]]
        obs = observacoes[p["id"]]

        texto += f"\nResposta: {resp}"

        if obs.strip() != "":
            texto += f"\nObservação: {obs}"

        texto += "\n"

    # INCONFORMIDADES
    if inconformidades:
        texto += "\nINCONFORMIDADES IDENTIFICADAS:\n"
        for i, item in enumerate(inconformidades, 1):
            texto += f"{i}. {item}\n"
    else:
        texto += "\nNão foram identificadas inconformidades.\n"

    texto += f"""

CONCLUSÃO

Diante do exposto, o parecer é {conclusao}.
"""

    return texto


# -------------------------
# GERAR PDF
# -------------------------
def gerar_pdf_bytes(texto):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    conteudo = []

    # CABEÇALHO (papel timbrado)
    conteudo.append(Paragraph("<b>PREFEITURA MUNICIPAL</b>", styles["Title"]))
    conteudo.append(Paragraph("Secretaria de Planejamento Urbano", styles["Normal"]))
    conteudo.append(Spacer(1, 12))
    conteudo.append(Paragraph("______________________________________________", styles["Normal"]))
    conteudo.append(Spacer(1, 12))

    # CORPO
    for linha in texto.split("\n"):
        conteudo.append(Paragraph(linha, styles["Normal"]))
        conteudo.append(Spacer(1, 8))

    doc.build(conteudo)

    buffer.seek(0)
    return buffer


# -------------------------
# INTERFACE
# -------------------------
st.title("Gerador de Parecer Urbanístico")

st.header("Dados do Empreendimento")

protocolo = st.text_input("N° Protocolo")
tipo = st.selectbox("Tipo do Empreendimento", ["Loteamento", "Condomínio fechado de lotes"])
interessado = st.text_input("Nome do Requerente/Interessado")
n_lotes = st.number_input("Número de Lotes", min_value=1)

st.header("Análise")

respostas = {}
observacoes = {}

for p in perguntas:
    st.subheader(p["pergunta"])

    respostas[p["id"]] = st.selectbox(
        "Resposta",
        p["opcoes"],
        key=p["id"]
    )

    observacoes[p["id"]] = st.text_area(
        "Observação do analista",
        key=f"obs_{p['id']}"
    )

# -------------------------
# EXECUÇÃO
# -------------------------
if st.button("Gerar Parecer"):

    dados = {
        "protocolo": protocolo,
        "tipo": tipo,
        "interessado": interessado,
        "n_lotes": n_lotes
    }

    inconformidades = analisar(respostas, perguntas)
    conclusao = definir_conclusao(inconformidades)

    parecer = gerar_parecer(dados, respostas, observacoes, inconformidades, conclusao)

    st.text_area("Parecer Gerado", parecer, height=400)

    pdf = gerar_pdf_bytes(parecer)

    st.download_button(
        label="📄 Baixar PDF",
        data=pdf,
        file_name="parecer_urbanistico.pdf",
        mime="application/pdf"
    )