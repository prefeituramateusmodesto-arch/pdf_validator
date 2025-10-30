import { useState } from 'react';


export default function UploadForm({ user, onLogout }) {
const [file, setFile] = useState(null);
const [status, setStatus] = useState(null);


const handleUpload = async (e) => {
e.preventDefault();
if (!file) {
alert('Selecione um arquivo PDF antes de enviar.');
return;
}


const formData = new FormData();
formData.append('file', file);
formData.append('user_email', user.email);


try {
const response = await fetch(`${import.meta.env.VITE_API_URL || process.env.REACT_APP_API_URL}/upload`, {
method: 'POST',
body: formData,
});


const data = await response.json();
setStatus(data);
} catch (error) {
alert('Erro ao enviar o arquivo.');
console.error(error);
}
};


return (
<div className="card">
<h2>Bem-vindo, {user.email}</h2>
<form onSubmit={handleUpload}>
<input
type="file"
accept="application/pdf"
onChange={(e) => setFile(e.target.files[0])}
/>
<button type="submit">Enviar PDF</button>
</form>


{status && (
<div className="result">
{status.status === 'completo' ? (
<p className="success">✅ {status.mensagem}</p>
) : (
<>
<p className="error">⚠️ Formulário incompleto</p>
<p>Campos faltantes: {status.faltantes.join(', ')}</p>
</>
)}
</div>
)}


<button className="logout" onClick={onLogout}>Sair</button>
</div>
);
}
