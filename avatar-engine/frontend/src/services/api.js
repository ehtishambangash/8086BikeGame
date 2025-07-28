import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Avatar API
export const avatarAPI = {
  create: async (formData) => {
    const response = await api.post('/avatars/create', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async () => {
    const response = await api.get('/avatars');
    return response.data;
  },

  get: async (token) => {
    const response = await api.get(`/avatars/${token}`);
    return response.data;
  },

  delete: async (token) => {
    const response = await api.delete(`/avatars/${token}`);
    return response.data;
  },
};

// Generation API
export const generationAPI = {
  generateImage: async (request) => {
    const response = await api.post('/generate/image', request);
    return response.data;
  },

  generateVideo: async (request) => {
    const response = await api.post('/generate/video', request);
    return response.data;
  },

  getStatus: async (jobId) => {
    const response = await api.get(`/generate/status/${jobId}`);
    return response.data;
  },
};

// Training API
export const trainingAPI = {
  getStatus: async (jobId) => {
    const response = await api.get(`/training/status/${jobId}`);
    return response.data;
  },

  restart: async (token) => {
    const response = await api.post(`/training/restart/${token}`);
    return response.data;
  },
};

// ComfyUI API
export const comfyuiAPI = {
  getStatus: async () => {
    const response = await api.get('/comfyui/status');
    return response.data;
  },

  restart: async () => {
    const response = await api.post('/comfyui/restart');
    return response.data;
  },
};

// Stats API
export const statsAPI = {
  get: async () => {
    const response = await api.get('/stats');
    return response.data;
  },
};

export default api;