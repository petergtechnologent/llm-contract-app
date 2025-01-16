import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import UploadContract from './pages/UploadContract';
import ContractDetails from './pages/ContractDetails';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/contracts/upload" element={<UploadContract />} />
      <Route path="/contracts/:id" element={<ContractDetails />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
