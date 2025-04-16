import { useNavigate } from 'react-router-dom'
import { useState } from 'react'

export default function Home() {
  const navigate = useNavigate()
  const [colors, setColors] = useState(4)

  const startGame = () => {
    navigate(`/game?colors=${colors}`)
  }

  return (
    <div className="container">
      <h1>MASTERMIND</h1>
      <img 
        src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Mastermind.jpg/320px-Mastermind.jpg" 
        alt="Mastermind" 
        style={{ width: '200px' }}
      />
      <div className="controls">
        <label>Selecciona el número de colores:</label>
        <select 
          value={colors} 
          onChange={(e) => setColors(parseInt(e.target.value))}
        >
          {[3, 4, 5, 6, 7, 8, 9].map(num => (
            <option key={num} value={num}>{num}</option>
          ))}
        </select>
        <button onClick={startGame}>Jugar</button>
      </div>
    </div>
  )
}