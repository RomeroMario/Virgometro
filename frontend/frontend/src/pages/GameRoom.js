import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

export default function GameRoom() {
  const { codigo } = useParams();
  const [playerName, setPlayerName] = useState('');
  const [isNameSet, setIsNameSet] = useState(false);
  const [votoConfirmado, setVotoConfirmado] = useState('');
  const [playerCalificado, setPlayer] = useState('');
  const [gameFinished, setGameFinished] = useState(false);
  const [currentCategory, setCurrentCategory] = useState(null);
  const [totales, setTotales] = useState(null);
  const [ws, setWs] = useState(null);  // Mantener el WebSocket en el estado
  const [isWsOpen, setIsWsOpen] = useState(false);  // Para saber si la conexión está abierta

  useEffect(() => {
    if (isNameSet) {
      const socket = new WebSocket(`ws://localhost:8000/ws/${codigo}/${playerName}`);
      socket.onopen = () => {
        setIsWsOpen(true);  // Marcar como abierta la conexión cuando esté lista
      };

      socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if(message.status==='finalizado'){
            setGameFinished(true);
            console.log(message.promedios);
            setTotales(message.totales);
        } else if (message.categoria.id) {
            setCurrentCategory(message.categoria);
            setPlayer(message.jugador);
        } 
      };

      socket.onclose = () => {
        setIsWsOpen(false);  // Marcar como cerrada la conexión
      };

      setWs(socket);

      return () => {
        socket.close();
      };
    }
  }, [codigo, isNameSet, playerName]);

  const handleNameSubmit = (e) => {
    e.preventDefault();
    setIsNameSet(true);
  };

  const handleVote = (voto) => {
    if (isWsOpen && ws) {
      const categoria_id = currentCategory ? currentCategory.id : -1;
      ws.send(JSON.stringify({ categoria_id, playerCalificado, playerName, voto }));
      setVotoConfirmado('¡Voto registrado!');
      setTimeout(() => setVotoConfirmado(''), 1000);
    } else {
      console.error('WebSocket no está listo para enviar el mensaje');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-extrabold text-blue-600 mb-6">Sala de Juego</h1>

      {!isNameSet ? (
        <form onSubmit={handleNameSubmit} className="bg-white shadow-lg rounded-2xl p-6 w-full max-w-md">
          <input
            type="text"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            placeholder="Tu nombre"
            required
            className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
          />
          <button
            type="submit"
            className="w-full mt-4 bg-blue-500 text-white py-2 px-4 rounded-xl hover:bg-blue-600 transition duration-300"
          >
            Entrar
          </button>
        </form>
      ) : gameFinished ? (
        <div className="bg-white shadow-lg rounded-2xl p-6 w-full max-w-md text-center">
  <h2 className="text-2xl font-semibold text-green-600 mb-4">¡Votación finalizada!</h2>
  <p className="text-lg text-gray-800 mb-4">Gracias por participar. Aquí están los resultados:</p>
  
  <ul className="text-left bg-gray-50 rounded-lg p-4">
    {Object.entries(totales)
      .sort(([, a], [, b]) => b - a) // Ordenar de mayor a menor puntaje
      .map(([jugador, puntaje]) => (
        <li
          key={jugador}
          className="flex justify-between border-b border-gray-200 py-2 last:border-b-0"
        >
          <span className="font-medium text-gray-700">{jugador}</span>
          <span className="text-blue-600 font-bold">{puntaje}</span>
        </li>
      ))}
  </ul>
</div>

      ): (
        <div className="w-full max-w-md">
          {currentCategory && (
            <div className="bg-white shadow-lg rounded-2xl p-6 mb-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">{currentCategory.nombre}</h2>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">{playerCalificado}</h2>
              <div className="flex justify-center gap-4">
                {currentCategory.tipo === 0 ? (
                  // Si es tipo 0, mostrar botones de voto del 1 al 5
                  <>
                    <button
                      onClick={() => handleVote(1)}
                      className="bg-green-500 text-white py-2 px-6 rounded-xl hover:bg-green-600 active:scale-95 transition duration-200 transform"
                    >
                       1
                    </button>
                    <button
                      onClick={() => handleVote(2)}
                      className="bg-green-500 text-white py-2 px-6 rounded-xl hover:bg-green-600 active:scale-95 transition duration-200 transform"
                    >
                       2
                    </button>
                    <button
                      onClick={() => handleVote(3)}
                      className="bg-green-500 text-white py-2 px-6 rounded-xl hover:bg-green-600 active:scale-95 transition duration-200 transform"
                    >
                       3
                    </button>
                    <button
                      onClick={() => handleVote(4)}
                      className="bg-green-500 text-white py-2 px-6 rounded-xl hover:bg-green-600 active:scale-95 transition duration-200 transform"
                    >
                       4
                    </button>
                    <button
                      onClick={() => handleVote(5)}
                      className="bg-green-500 text-white py-2 px-6 rounded-xl hover:bg-green-600 active:scale-95 transition duration-200 transform"
                    >
                       5
                    </button>
                  </>
                ) : (
                  // Si es tipo 1, mostrar "Sí" y "No"
                  <>
                    <button
                      onClick={() => handleVote(5)}
                      className="bg-blue-500 text-white py-2 px-6 rounded-xl hover:bg-blue-600 transition duration-300"
                    >
                      Sí
                    </button>
                    <button
                      onClick={() => handleVote(0)}
                      className="bg-red-500 text-white py-2 px-6 rounded-xl hover:bg-red-600 transition duration-300"
                    >
                      No
                    </button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      )}
      {votoConfirmado && (
  <div className="bg-blue-100 text-blue-800 p-3 rounded-lg mt-4">
    {votoConfirmado}
  </div>
)}
    </div>
  );
}
