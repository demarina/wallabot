import { useEffect, useState } from 'react'
import './App.css'


type Feature = {
  e_type: string;
  e_value: string;
};


type Bike = {
  title: string;
  price: string;
  link: string;
  features: Feature[];
};

function App() {

  const [bikes, setBikes] = useState<Bike[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchBikes = async () => {
    try {
      const res = await fetch("http://localhost:8000/bikes");
      const data: Bike[] = await res.json();
      setBikes(data);
    } catch (error) {
      console.error("Error during load bikes", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBikes();
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <>
     <div>
      <h1>Anuncios</h1>
      <p>Total de anuncios: {bikes.length} </p>

 <table>
  <thead>
    <tr>
      <th>Título</th>
      <th>Precio</th>
      <th>Link</th>
      <th>Características</th>
      <th>Anunciado en buycycle.com</th>
    </tr>
  </thead>

  <tbody>
    {bikes.map((b) => (
      <tr key={b.title}>
        <td>{b.title}</td>
        <td>{b.price}</td>
        <td>
          <a href={b.link} target="_blank" rel="noopener noreferrer">
            wallapop link
          </a>
        </td>
        <td>
          <ul>
            {b.features.map((f, index) => (
              <li key={index}>
                {f.e_type.replace("ent.", "")}: {f.e_value}
              </li>
            ))}
          </ul>
        </td>
        <td>
        NO
        </td>
      </tr>
    ))}
      </tbody>
    </table>

    </div>
    </>
  )
}

export default App
