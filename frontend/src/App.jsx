import React, { useState, useEffect } from 'react'
setStatus('Enviando...')


try {
const res = await fetch('https://SEU_BACKEND_URL/upload', {
method: 'POST',
body: form,
})


const data = await res.json()
if (!res.ok) throw new Error(data.detail || JSON.stringify(data))


setStatus('Resposta: ' + JSON.stringify(data))
} catch (err) {
setStatus('Erro no upload: ' + err.message)
}
}


return (
<div className="min-h-screen flex items-center justify-center p-4">
<div className="w-full max-w-lg">
<h1 className="text-2xl mb-4">Validador de Formulários PDF</h1>


{!user ? (
<div>
<form onSubmit={handleRegister} className="mb-4">
<input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
<input type="password" placeholder="Senha" value={password} onChange={e=>setPassword(e.target.value)} required />
<button type="submit">Registrar</button>
</form>


<form onSubmit={handleLogin}>
<input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
<input type="password" placeholder="Senha" value={password} onChange={e=>setPassword(e.target.value)} required />
<button type="submit">Entrar</button>
</form>
</div>
) : (
<div>
<p>Logado como: {user.email}</p>
<button onClick={handleLogout}>Sair</button>


<form onSubmit={handleUpload} className="mt-4">
<input type="file" accept="application/pdf" onChange={e=>setFile(e.target.files[0])} />
<button type="submit">Enviar PDF</button>
</form>
</div>
)}


<div className="mt-4">{status}</div>
</div>
</div>
)
}
