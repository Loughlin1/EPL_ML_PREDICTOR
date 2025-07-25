import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export const getMatchweek = () => API.get('/matchweek');
export const getFixtures = () => API.get('/fixtures');
export const postPredictions = (data) => API.post('/predict', { data });
export const postPoints = (data) => API.post('/superbru/points', { data });
export const getTopPoints = () => API.get('/superbru/points/top/global');