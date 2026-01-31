'use client';

import { motion } from 'framer-motion';

interface QuartierData {
    quartier: string;
    count: number;
    prix_moyen: number;
}

interface PriceChartProps {
    data: QuartierData[];
    type: 'vente' | 'location';
    maxPrice?: number;
}

export default function PriceChart({ data, type, maxPrice }: PriceChartProps) {
    if (!data || data.length === 0) {
        return (
            <div className="text-center text-dark-400 py-8">
                Aucune donnée disponible
            </div>
        );
    }

    const max = maxPrice || Math.max(...data.map(d => d.prix_moyen));
    const isLocation = type === 'location';
    const barColor = isLocation ? 'from-purple-500 to-purple-600' : 'from-primary-500 to-primary-600';

    const formatPrice = (price: number) => {
        if (isLocation) {
            return `${Math.round(price).toLocaleString('fr-FR')} DH/mois`;
        }
        if (price >= 1000000) {
            return `${(price / 1000000).toFixed(1)}M DH`;
        }
        return `${Math.round(price).toLocaleString('fr-FR')} DH`;
    };

    return (
        <div className="space-y-3">
            {data.map((item, index) => {
                const width = (item.prix_moyen / max) * 100;
                return (
                    <motion.div
                        key={item.quartier}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                        className="group"
                    >
                        <div className="flex justify-between items-center mb-1">
                            <span className="text-sm text-dark-300 truncate max-w-[60%]">
                                {item.quartier}
                            </span>
                            <span className="text-xs text-dark-400">
                                {item.count} annonces
                            </span>
                        </div>
                        <div className="relative h-7 bg-dark-800 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${width}%` }}
                                transition={{ duration: 0.5, delay: 0.2 + index * 0.05 }}
                                className={`absolute left-0 top-0 h-full bg-gradient-to-r ${barColor} rounded-full`}
                            />
                            <div className="absolute inset-0 flex items-center justify-end pr-3">
                                <span className="text-xs font-medium text-white drop-shadow-lg">
                                    {formatPrice(item.prix_moyen)}
                                </span>
                            </div>
                        </div>
                    </motion.div>
                );
            })}
        </div>
    );
}
