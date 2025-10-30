import { useState } from 'react';
import UploadForm from './components/UploadForm';
import LoginForm from './components/LoginForm';
import './styles.css';


export default function App() {
const [user, setUser] = useState(null);


return (
<div className="app-container">
<h1>Validador de Formulário PDF</h1>
{!user ? (
<LoginForm onLogin={setUser} />
) : (
<UploadForm user={user} onLogout={() => setUser(null)} />
)}
</div>
);
}
