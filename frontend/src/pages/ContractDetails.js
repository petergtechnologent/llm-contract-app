import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getContractDetails, reviewContract, downloadContract } from '../api';

function ContractDetails() {
  const { id } = useParams();
  const [contract, setContract] = useState(null);
  const [instructions, setInstructions] = useState('');

  useEffect(() => {
    fetchContract();
    // eslint-disable-next-line
  }, [id]);

  const fetchContract = async () => {
    try {
      const data = await getContractDetails(id);
      setContract(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleReview = async () => {
    try {
      await reviewContract(id, instructions);
      fetchContract();
    } catch (error) {
      console.error(error);
      alert('Error reviewing contract');
    }
  };

  const handleDownload = async (version) => {
    try {
      const data = await downloadContract(id, version);
      const element = document.createElement('a');
      const file = new Blob([data.content], { type: 'text/plain' });
      element.href = URL.createObjectURL(file);
      element.download = data.file_name;
      document.body.appendChild(element);
      element.click();
    } catch (error) {
      console.error(error);
      alert('Error downloading contract');
    }
  };

  if (!contract) return <div>Loading...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2>Contract #{contract.id}</h2>
      <p><strong>File Name:</strong> {contract.file_name}</p>
      <p><strong>Original Text:</strong></p>
      <pre>{contract.original_text}</pre>

      <h3>Revisions</h3>
      {contract.revisions && contract.revisions.length > 0 ? (
        contract.revisions.map((rev) => (
          <div key={rev.id} style={{ marginBottom: '15px' }}>
            <p>Revision ID: {rev.id}</p>
            <pre>{rev.revision_text}</pre>
            <small>Created At: {new Date(rev.created_at).toLocaleString()}</small>
          </div>
        ))
      ) : (
        <p>No revisions yet.</p>
      )}

      <div style={{ marginTop: '20px' }}>
        <textarea
          placeholder="Additional instructions or guidelines..."
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
          rows={4}
          cols={50}
        />
        <br />
        <button onClick={handleReview}>Request AI Review</button>
      </div>

      <div style={{ marginTop: '20px' }}>
        <button onClick={() => handleDownload('original')}>Download Original</button>
        <button onClick={() => handleDownload('revised')}>Download Latest Revision</button>
      </div>
    </div>
  );
}

export default ContractDetails;
