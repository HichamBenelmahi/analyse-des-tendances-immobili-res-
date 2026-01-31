'use client';

import { motion } from 'framer-motion';
import { PredictionResult } from '@/types';
import { formatPrice } from '@/lib/api';

interface ResultCardProps {
    result: PredictionResult;
    onNewEstimation: () => void;
}

export default function ResultCard({ result, onNewEstimation }: ResultCardProps) {
    const { prediction, input } = result;
    const transaction_type = result.transaction_type || 'vente';  // Default to vente
    const isLocation = transaction_type === 'location';

    const propertyTypeIcons: { [key: string]: string } = {
        Appartement: '🏢',
        Villa: '🏡',
        Maison: '🏘️',
        Riad: '🕌',
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
            className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 border border-gray-700 shadow-2xl"
        >
            {/* En-tête */}
            <div className="flex items-center mb-6">
                <div className={`w-10 h-10 ${isLocation ? 'bg-purple-500' : 'bg-green-500'} rounded-full flex items-center justify-center mr-3`}>
                    <span className="text-xl">{isLocation ? '🔑' : '✅'}</span>
                </div>
                <div>
                    <h3 className="text-xl font-bold text-white">Estimation terminée !</h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${isLocation ? 'bg-purple-500/20 text-purple-300' : 'bg-green-500/20 text-green-300'}`}>
                        {isLocation ? 'Location' : 'Vente'}
                    </span>
                </div>
            </div>

            {/* Récapitulatif du bien */}
            <div className="bg-gray-700/50 rounded-xl p-4 mb-6">
                <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center">
                    <span className="mr-2">🏠</span> Votre bien
                </h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="text-gray-400">Type :</div>
                    <div className="text-white font-medium">
                        {propertyTypeIcons[input.property_type]} {input.property_type}
                    </div>
                    <div className="text-gray-400">Ville :</div>
                    <div className="text-white font-medium">{input.city}</div>
                    <div className="text-gray-400">Quartier :</div>
                    <div className="text-white font-medium">{input.quartier}</div>
                    <div className="text-gray-400">Surface :</div>
                    <div className="text-white font-medium">{input.surface_m2} m²</div>
                    <div className="text-gray-400">Chambres :</div>
                    <div className="text-white font-medium">{input.num_rooms}</div>
                    <div className="text-gray-400">Salles de bain :</div>
                    <div className="text-white font-medium">{input.num_bathrooms}</div>
                </div>
            </div>

            {/* Prix estimé */}
            <div className={`bg-gradient-to-r ${isLocation ? 'from-purple-600/20 to-pink-600/20 border-purple-500/30' : 'from-blue-600/20 to-purple-600/20 border-blue-500/30'} rounded-xl p-6 mb-6 border`}>
                <h4 className="text-sm font-semibold text-gray-400 mb-2 flex items-center">
                    <span className="mr-2">💰</span>
                    {isLocation ? 'Loyer mensuel estimé' : 'Prix de vente estimé'}
                </h4>
                <div className="text-center">
                    <div className="text-4xl font-bold text-white mb-1">
                        {formatPrice(prediction.price_dh)} <span className="text-xl text-gray-400">DH{isLocation ? '/mois' : ''}</span>
                    </div>
                    {!isLocation && prediction.price_millions && (
                        <div className="text-lg text-blue-400">
                            Soit environ {prediction.price_millions.toFixed(2)} Millions DH
                        </div>
                    )}
                    {isLocation && (
                        <div className="text-lg text-purple-400">
                            Soit environ {formatPrice(prediction.price_dh * 12)} DH/an
                        </div>
                    )}
                </div>
            </div>

            {/* Prix au m² et intervalle de confiance */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-700/50 rounded-xl p-4 text-center">
                    <div className="text-2xl font-bold text-white">
                        {formatPrice(prediction.price_per_m2)}
                    </div>
                    <div className="text-sm text-gray-400 flex items-center justify-center">
                        <span className="mr-1">📊</span> DH/m²{isLocation ? '/mois' : ''}
                    </div>
                </div>
                <div className="bg-gray-700/50 rounded-xl p-4 text-center">
                    <div className="text-lg font-bold text-white">
                        ± {formatPrice(prediction.confidence_interval.margin || 0)}
                    </div>
                    <div className="text-sm text-gray-400 flex items-center justify-center">
                        <span className="mr-1">ℹ️</span> Marge
                    </div>
                </div>
            </div>

            {/* Intervalle de confiance détaillé */}
            <div className="text-center text-sm text-gray-400 mb-6">
                Intervalle : {formatPrice(prediction.confidence_interval.min)} - {formatPrice(prediction.confidence_interval.max)} DH
            </div>

            {/* Bouton nouvelle estimation */}
            <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={onNewEstimation}
                className={`w-full py-4 bg-gradient-to-r ${isLocation ? 'from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500' : 'from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500'} 
                   text-white font-semibold rounded-xl transition-all duration-200 flex items-center justify-center`}
            >
                <span className="mr-2">🔄</span> Nouvelle estimation
            </motion.button>
        </motion.div>
    );
}
