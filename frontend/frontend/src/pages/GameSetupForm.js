import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function GameSetupForm() {
  const [categories, setCategories] = useState([]);
  const [players, setPlayers] = useState('');
  const [confirmacion, setConfirmacion] = useState('');
  const navigate = useNavigate();

  const addCategory = () => {
    setCategories([...categories, { nombre: '', tipo: 0 }]);
  };

  const updateCategory = (index, field, value) => {
    const updated = [...categories];
    updated[index][field] = value;
    setCategories(updated);
  };

  const removeCategory = (index) => {
    const updated = categories.filter((_, i) => i !== index);
    setCategories(updated);
  };

  const createGame = async () => {
    setConfirmacion('¡Partida creada con éxito!');
    const jugadores = players.split('\n').map(p => p.trim()).filter(p => p);
    const response = await fetch('https://virgometro.onrender.com/newgame', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ categorias: categories, jugadores })
    });
    
    const game = await response.json();
    navigate(`/${game.codigo}`);

  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Crear Nuevo Juego</h1>

      <div>
        <h2 className="text-xl">Categorías</h2>
        {categories.map((cat, index) => (
          <div key={index} className="flex gap-2 items-center">
            <input
              type="text"
              placeholder="Nombre de la categoría"
              value={cat.nombre}
              onChange={(e) => updateCategory(index, 'nombre', e.target.value)}
            />
            <select
              value={cat.tipo}
              onChange={(e) => updateCategory(index, 'tipo', Number(e.target.value))}
            >
              <option value={99} disabled>Seleccione tipo</option>
              <option value={0}>Del 1 al 5</option>
              <option value={1}>Sí o No</option>
            </select>
            <button onClick={() => removeCategory(index)} className="p-1 bg-red-500 text-white rounded-2xl">Eliminar</button>
          </div>
        ))}
        <button onClick={addCategory} className="p-2 bg-blue-500 text-white rounded-2xl">Añadir Categoría</button>
      </div>

      <div className="mt-4">
        <h2 className="text-xl">Jugadores</h2>
        <textarea
          rows="5"
          placeholder="Escribe un jugador por línea"
          value={players}
          onChange={(e) => setPlayers(e.target.value)}
          className="w-full p-2 border rounded-2xl"
        />
      </div>

      <button onClick={createGame} className="mt-4 p-2 hover:bg-green-600 bg-green-500 text-white rounded-2xl">Crear Juego</button>
      {confirmacion && (
        <div className="bg-green-100 text-green-800 p-3 rounded-lg mt-4">
      {confirmacion}
  </div>
)}

    </div>
  );
}