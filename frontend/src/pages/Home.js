import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listContracts } from '../api';

function Home() {
  const [contracts, setContracts] = useState([]);

  useEffect(() => {
    listContracts().then(setContracts).catch(console.error);
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h1>Contracts</h1>
      <Link to="/contracts/upload">Upload a New Contract</Link>
      <ul>
        {contracts.map((c) => (
          <li key={c.id}>
            <Link to={`/contracts/${c.id}`}>{c.file_name || `Contract #${c.id}`}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Home;
