import os
import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from openai import OpenAI

# Inicializa o app
app = FastAPI()

# Configuração CORS
# Substitua "*" pelo domínio do seu frontend se quiser restringir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Variáveis de ambiente
# ----------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "nao-responder@seudominio.com")

if not OPENAI_API_KEY:
    raise RuntimeError("Variável OPENAI_API_KEY não encontrada no ambiente")
if not SENDGRID_API_KEY:
    raise RuntimeError("Variável SENDGRID_API_KEY não encontrada no ambiente")

# Inicializa clientes
openai_client = OpenAI(api_key=OPENAI_API_KEY)
sg_client = SendGridAPIClient(SENDGRID_API_KEY)

# ----------------------------
# Funções auxiliares
# ----------------------------

def extrair_campos_pdf_bytes(pdf_bytes: bytes):
    """Extrai campos de formulário do PDF e retorna {nome_campo: valor}"""
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
    """Gera mensagem personalizada via OpenAI GPT-5"""
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

# ----------------------------
# Rotas
# ----------------------------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), user_email: str = Form(...)):
    """Recebe PDF e e-mail, valida campos e envia notificação"""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos")

    content = await file.read()
    campos = extrair_campos_pdf_bytes(content)

    if not campos:
        raise HTTPException(
            status_code=422,
            detail="PDF não possui campos de formulário legíveis. Caso seja imagem, aplique OCR.",
        )

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
    """Rota de health check"""
    return {"status": "ok"}
