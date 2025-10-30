import os
import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from openai import OpenAI

# Inicialização do app FastAPI
app = FastAPI()

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pode restringir depois para o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variáveis de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "nao-responder@seudominio.com")

# Clientes das APIs
openai_client = OpenAI(api_key=OPENAI_API_KEY)
sg_client = SendGridAPIClient(SENDGRID_API_KEY)

# -------------------------------------------------------------------------
# Funções auxiliares
# -------------------------------------------------------------------------

def extrair_campos_pdf_bytes(pdf_bytes: bytes):
    """Lê um PDF e retorna um dicionário com {nome_campo: valor}"""
    campos = {}
    try:
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in pdf:
            widgets = page.widgets()
            if not widgets:
                continue
            for w in widgets:
                campos[w.field_name] = w.field_value
        return campos
    except Exception:
        return None


def gerar_texto_openai(faltantes):
    """Gera uma mensagem personalizada usando o modelo GPT-5"""
    prompt = (
        "Gere uma mensagem educada para informar que o formulário PDF enviado "
        "não está completamente preenchido. Liste os campos faltantes: "
        + ", ".join(faltantes)
    )

    resp = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
    )
    return resp.choices[0].message.content


def enviar_email_sendgrid(destinatario: str, assunto: str, corpo: str):
    """Envia e-mail via SendGrid"""
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=destinatario,
        subject=assunto,
        plain_text_content=corpo,
    )
    try:
        response = sg_client.send(message)
        return response.status_code
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        raise HTTPException(status_code=500, detail="Falha ao enviar e-mail")


# -------------------------------------------------------------------------
# Rotas principais
# -------------------------------------------------------------------------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), user_email: str = Form(...)):
    """Recebe o PDF e o e-mail do usuário e valida o preenchimento"""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos")

    content = await file.read()
    campos = extrair_campos_pdf_bytes(content)

    # Caso o PDF não contenha campos legíveis
    if not campos:
        raise HTTPException(
            status_code=422,
            detail="PDF não possui campos de formulário legíveis. Caso seja imagem, aplique OCR.",
        )

    # Verifica campos vazios
    faltantes = [nome for nome, val in campos.items() if not val]

    if faltantes:
        try:
            corpo = gerar_texto_openai(faltantes)
        except Exception as e:
            print("Erro OpenAI:", e)
            corpo = (
                "O seu formulário não foi preenchido completamente. "
                "Campos faltantes: " + ", ".join(faltantes)
            )

        assunto = "Formulário incompleto - campos faltantes"
        enviar_email_sendgrid(user_email, assunto, corpo)

        return {
            "status": "incompleto",
            "faltantes": faltantes,
            "mensagem_enviada_para": user_email,
        }

    return {"status": "completo", "mensagem": "Todos os campos estão preenchidos!"}


@app.get("/health")
def health():
    return {"status": "ok"}
