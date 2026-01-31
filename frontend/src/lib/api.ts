import axios from 'axios';
import { PredictionInput, PredictionResult, AvailableData } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Récupérer les données disponibles (villes, quartiers, types de biens)
 */
export const fetchAvailableData = async (): Promise<AvailableData> => {
    const response = await api.get('/data');
    return response.data;
};

/**
 * Faire une prédiction de prix
 */
export const predictPrice = async (data: PredictionInput): Promise<PredictionResult> => {
    const response = await api.post('/predict', data);
    return response.data;
};

/**
 * Vérifier l'état de l'API
 */
export const checkHealth = async (): Promise<{ status: string; models_loaded: boolean }> => {
    const response = await api.get('/health');
    return response.data;
};

/**
 * Obtenir les infos du modèle
 */
export const getModelInfo = async (): Promise<{
    model_name: string;
    r2_score: number;
    rmse: number;
    features: string[];
}> => {
    const response = await api.get('/model-info');
    return response.data;
};

/**
 * Formater un nombre avec des espaces pour les milliers
 */
export const formatPrice = (price: number): string => {
    return Math.round(price).toLocaleString('fr-FR').replace(/,/g, ' ');
};
