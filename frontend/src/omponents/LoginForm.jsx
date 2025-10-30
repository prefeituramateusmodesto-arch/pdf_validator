import { useState } from 'react';


export default function LoginForm({ onLogin }) {
const [email, setEmail] = useState('');


const handleSubmit = (e) => {
e.preventDefault();
if (!email.includes('@')) {
alert('Por favor, insira um e-mail válido.');
return;
}
onLogin({ email });
};


return (
<form onSubmit={handleSubmit} className="card">
<h2>Acesse o sistema</h2>
<input
type="email"
placeholder="Digite seu e-mail"
value={email}
onChange={(e) => setEmail(e.target.value)}
required
/>
<button type="submit">Entrar</button>
</form>
);
}
