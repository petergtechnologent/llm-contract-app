import axios from 'axios';

// Point to your backend server. 
// If Docker Compose exposes the backend at localhost:8000, then:
const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

export const listContracts = async () => {
  const res = await axios.get(`${API_BASE}/api/contracts`);
  return res.data;
};

export const uploadContract = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await axios.post(`${API_BASE}/api/contracts`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const getContractDetails = async (id) => {
  const res = await axios.get(`${API_BASE}/api/contracts/${id}`);
  return res.data;
};

export const reviewContract = async (id, instructions) => {
  // POST JSON body with { instructions }
  const res = await axios.post(`${API_BASE}/api/contracts/${id}/review`, {
    instructions,
  });
  return res.data;
};

export const downloadContract = async (id, version = 'original') => {
  const res = await axios.get(`${API_BASE}/api/contracts/${id}/download`, {
    params: { version },
  });
  return res.data; // { file_name, content }
};
