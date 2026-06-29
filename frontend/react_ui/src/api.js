import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/api'
});

export const getMatchweek = () => API.get('/matchweek');
export const getSeasons = () => API.get('/seasons');
export const getFixtures = (season) => API.get('/fixtures', { params: season ? { season } : {} });
export const postPredictions = (data, season) => API.post('/predict', { data, season });
export const postPoints = (data) => API.post('/superbru/points', { data });
export const getTopPoints = () => API.get('/superbru/points/top/global');
export const postEvaluation = (data) => API.post('/evaluate', {data});
export const getModelEvaluation = () => API.get('/evaluate/validation');
export const getModelExplanation = () => API.get('/content/model_explanation');
