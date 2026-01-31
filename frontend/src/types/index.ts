// Types pour l'application de prédiction immobilière

export interface PredictionInput {
    transaction_type: string;  // 'vente' ou 'location'
    city: string;
    quartier: string;
    property_type: string;
    surface_m2: number;
    num_rooms: number;
    num_bathrooms: number;
}

export interface PredictionResult {
    success: boolean;
    transaction_type: string;  // 'vente' ou 'location'
    prediction: {
        price_dh: number;
        price_millions: number | null;  // null pour location
        price_per_m2: number;
        price_monthly?: number;  // Pour location uniquement
        confidence_interval: {
            min: number;
            max: number;
            margin: number;
        };
    };
    input: {
        transaction_type: string;
        city: string;
        quartier: string;
        property_type: string;
        surface_m2: number;
        num_rooms: number;
        num_bathrooms: number;
    };
}

export interface AvailableData {
    cities: string[];
    quartiers: { [city: string]: string[] };
    property_types: string[];
}

export interface Message {
    id: string;
    type: 'user' | 'bot';
    content: string;
    timestamp: Date;
    component?: 'buttons' | 'select' | 'input' | 'result' | 'loading';
    options?: string[] | { label: string; value: string; icon?: string }[];
    placeholder?: string;
    result?: PredictionResult;
}

export interface ConversationState {
    step: number;
    transactionType: string;
    propertyType: string;
    city: string;
    quartier: string;
    surface: number;
    rooms: number;
    bathrooms: number;
}

export type Step =
    | 'welcome'
    | 'transaction_type'
    | 'property_type'
    | 'city'
    | 'quartier'
    | 'surface'
    | 'rooms'
    | 'bathrooms'
    | 'loading'
    | 'result';
