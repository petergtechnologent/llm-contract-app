import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadContract } from '../api';

function UploadContract() {
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    try {
      const result = await uploadContract(file);
      navigate(`/contracts/${result.id}`);
    } catch (error) {
      console.error(error);
      alert('Error uploading file');
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Upload a Contract</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          accept=".txt,.pdf,.doc,.docx"
        />
        <button type="submit">Upload</button>
      </form>
    </div>
  );
}

export default UploadContract;
