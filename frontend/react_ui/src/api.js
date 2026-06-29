import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/api'
});

export const getSeasons = () => API.get('/seasons');
export const getSeasonSummary = (season) => API.get(`/seasons/${season}/summary`);
export const getSeasonMatchweek = (season) => API.get(`/seasons/${season}/matchweek`);
export const getMatchweekData = (season, week) => API.get(`/seasons/${season}/matchweek/${week}`);
export const getTopPoints = (season) => API.get('/superbru/points/top/global', { params: season ? { season } : {} });
export const postPoints = (data) => API.post('/superbru/points', { data });
export const getModelEvaluation = () => API.get('/evaluate/validation');
export const getModelExplanation = () => API.get('/content/model_explanation');
