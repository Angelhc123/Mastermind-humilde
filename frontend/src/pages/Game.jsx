import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import ColorCircle from '../components/ColorCircle'

export default function Game() {
  const navigate = useNavigate()
  const [proposal, setProposal] = useState([])
  const [history, setHistory] = useState([])
  const [selectedHits, setSelectedHits] = useState(0)
  const [colors, setColors] = useState(4)

  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search)
    const numColors = parseInt(queryParams.get('colors')) || 4
    setColors(numColors)

    axios.post('http://localhost:5000/iniciar', { num_elementos: numColors })
      .then(() => fetchProposal())
  }, [])

  const fetchProposal = () => {
    axios.get('http://localhost:5000/propuesta')
      .then(res => setProposal(res.data.propuesta))
  }

  const submitResponse = () => {
    axios.post('http://localhost:5000/responder', {
      propuesta: proposal,
      aciertos: selectedHits
    }).then(res => {
      setHistory([...history, { proposal, hits: selectedHits }])
      if (res.data.status === 'Ganado') {
        alert(`¡La máquina adivinó en ${history.length + 1} intentos!`)
        navigate('/')
      } else {
        fetchProposal()
        setSelectedHits(0)
      }
    })
  }

  return (
    <div className="game-container">
      <h2>Intento #{history.length + 1}</h2>
      
      <div className="proposal">
        {proposal.map((color, i) => (
          <ColorCircle key={i} color={color.replace('p'+i, '')} />
        ))}
      </div>
      
      <div className="controls">
        <label>Aciertos:</label>
        <select 
          value={selectedHits} 
          onChange={(e) => setSelectedHits(parseInt(e.target.value))}
        >
          {[...Array(colors + 1).keys()].map(num => (
            <option key={num} value={num}>{num}</option>
          ))}
        </select>
        <button onClick={submitResponse}>Enviar</button>
      </div>
      
      <div className="history">
        <h3>Historial</h3>
        {history.map((item, idx) => (
          <div key={idx} className="history-item">
            <p>Intento {idx + 1}: {item.hits} aciertos</p>
            <div className="proposal-history">
              {item.proposal.map((color, i) => (
                <ColorCircle key={i} color={color.replace('p'+i, '')} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}