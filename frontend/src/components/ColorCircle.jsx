export default function ColorCircle({ color }) {
    const colorMap = {
      c0: '#FF0000', // Rojo
      c1: '#0000FF', // Azul
      c2: '#00FF00', // Verde
      c3: '#FFFF00', // Amarillo
      c4: '#800080', // Morado
      c5: '#FFA500', // Naranja
      c6: '#FFC0CB', // Rosa
      c7: '#00FFFF', // Cian
      c8: '#A9A9A9'  // Gris
    }
  
    return (
      <div 
        className="color-circle"
        style={{ backgroundColor: colorMap[color] || '#FFFFFF' }}
      />
    )
  }