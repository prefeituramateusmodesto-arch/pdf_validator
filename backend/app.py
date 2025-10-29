import os
)


resp = openai_client.chat.completions.create(
model="gpt-5",
messages=[{"role": "user", "content": prompt}],
max_tokens=400,
)
return resp.choices[0].message.content




def enviar_email_sendgrid(destinatario: str, assunto: str, corpo: str):
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
raise




@app.post('/upload')
async def upload_pdf(file: UploadFile = File(...), user_email: str = Form(...)):
# Recebe arquivo e e-mail do usuário
if not file.filename.lower().endswith('.pdf'):
raise HTTPException(status_code=400, detail='Apenas arquivos PDF são aceitos')


content = await file.read()


campos = extrair_campos_pdf_bytes(content)
# Caso o PDF não contenha campos (digitalizado), retornamos erro explicativo
if not campos:
# Você pode optar por aplicar OCR antes de devolver erro.
raise HTTPException(status_code=422, detail='PDF não possui campos de formulário legíveis. Caso seja imagem, aplique OCR.')


faltantes = [nome for nome, val in campos.items() if not val]


if faltantes:
# Gera mensagem com OpenAI
try:
corpo = gerar_texto_openai(faltantes)
except Exception:
# fallback simples caso OpenAI falhe
corpo = 'O seu formulário não foi preenchido completamente. Campos faltantes: ' + ', '.join(faltantes)


assunto = 'Formulário incompleto - campos faltantes'
enviar_email_sendgrid(user_email, assunto, corpo)


return {
'status': 'incompleto',
'faltantes': faltantes,
'mensagem_enviada_para': user_email
}


return {'status': 'completo', 'mensagem': 'Todos os campos preenchidos'}




# Endpoint simples de health check
@app.get('/health')
def health():
return {'status': 'ok'}
