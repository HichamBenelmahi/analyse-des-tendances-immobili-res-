'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import StatCard from './StatCard';
import PriceChart from './PriceChart';
import CustomSelect from './CustomSelect';

interface CityStats {
    count: number;
    prix_moyen: number;
    prix_min?: number;
    prix_max?: number;
    prix_m2_moyen: number;
    surface_moyenne: number;
}

interface QuartierData {
    quartier: string;
    count: number;
    prix_moyen: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function StatsSection() {
    const [cities, setCities] = useState<string[]>([]);
    const [selectedCity, setSelectedCity] = useState<string>('');
    const [statsType, setStatsType] = useState<'vente' | 'location'>('vente');
    const [cityStats, setCityStats] = useState<{ vente: CityStats | null; location: CityStats | null } | null>(null);
    const [quartierData, setQuartierData] = useState<{ vente: QuartierData[]; location: QuartierData[] }>({ vente: [], location: [] });
    const [loading, setLoading] = useState(true);
    const [summary, setSummary] = useState<any>(null);

    // Charger la liste des villes
    useEffect(() => {
        const fetchSummary = async () => {
            try {
                const response = await axios.get(`${API_URL}/stats/summary`);
                setSummary(response.data);
                setCities(response.data.cities || []);
                if (response.data.cities?.length > 0) {
                    setSelectedCity(response.data.cities[0]);
                }
                setLoading(false);
            } catch (error) {
                console.error('Erreur chargement stats:', error);
                setLoading(false);
            }
        };
        fetchSummary();
    }, []);

    // Charger les stats de la ville sélectionnée
    useEffect(() => {
        if (!selectedCity) return;

        const fetchCityStats = async () => {
            try {
                const [statsRes, quartiersRes] = await Promise.all([
                    axios.get(`${API_URL}/stats/city/${encodeURIComponent(selectedCity)}`),
                    axios.get(`${API_URL}/stats/quartiers/${encodeURIComponent(selectedCity)}`)
                ]);
                setCityStats({ vente: statsRes.data.vente, location: statsRes.data.location });
                setQuartierData({ vente: quartiersRes.data.vente || [], location: quartiersRes.data.location || [] });
            } catch (error) {
                console.error('Erreur chargement stats ville:', error);
            }
        };
        fetchCityStats();
    }, [selectedCity]);

    const currentStats = cityStats?.[statsType];
    const currentQuartierData = quartierData[statsType];

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="flex space-x-2">
                    <div className="loading-dot"></div>
                    <div className="loading-dot"></div>
                    <div className="loading-dot"></div>
                </div>
            </div>
        );
    }

    const formatPrice = (price: number, isLocation: boolean) => {
        if (isLocation) {
            return `${Math.round(price).toLocaleString('fr-FR')} DH/mois`;
        }
        if (price >= 1000000) {
            return `${(price / 1000000).toFixed(2)}M DH`;
        }
        return `${Math.round(price).toLocaleString('fr-FR')} DH`;
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header & Sélecteurs */}
            <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-1">
                        📊 Analyse du Marché Immobilier
                    </h2>
                    <p className="text-dark-400 text-sm">
                        Statistiques descriptives par ville et quartier
                    </p>
                </div>

                <div className="flex gap-3 flex-wrap z-20">
                    {/* Sélecteur Type */}
                    <div className="flex bg-dark-800 rounded-xl p-1">
                        <button
                            onClick={() => setStatsType('vente')}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${statsType === 'vente'
                                ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-orange'
                                : 'text-dark-400 hover:text-white'
                                }`}
                        >
                            🏠 Vente
                        </button>
                        <button
                            onClick={() => setStatsType('location')}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${statsType === 'location'
                                ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white'
                                : 'text-dark-400 hover:text-white'
                                }`}
                        >
                            🔑 Location
                        </button>
                    </div>

                    {/* Sélecteur Ville Custom */}
                    <div className="w-[200px]">
                        <CustomSelect
                            options={cities.map(c => ({ value: c, label: c, icon: '📍' }))}
                            value={selectedCity}
                            onChange={(val) => setSelectedCity(val)}
                            placeholder="Choisir une ville..."
                            icon="🏙️"
                        />
                    </div>
                </div>
            </div>

            {/* Stats Globales */}
            {summary && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="grid grid-cols-2 md:grid-cols-4 gap-4"
                >
                    <StatCard
                        icon="📊"
                        label="Total Annonces Vente"
                        value={summary.vente?.count || 0}
                        color="orange"
                        delay={0}
                    />
                    <StatCard
                        icon="🔑"
                        label="Total Annonces Location"
                        value={summary.location?.count || 0}
                        color="blue"
                        delay={0.1}
                    />
                    <StatCard
                        icon="💰"
                        label="Prix Moyen Vente"
                        value={formatPrice(summary.vente?.prix_moyen || 0, false)}
                        color="orange"
                        delay={0.2}
                    />
                    <StatCard
                        icon="🏢"
                        label="Loyer Moyen"
                        value={formatPrice(summary.location?.prix_moyen || 0, true)}
                        color="blue"
                        delay={0.3}
                    />
                </motion.div>
            )}

            {/* Divider */}
            <div className="border-t border-dark-700 my-6"></div>

            {/* Stats Ville Sélectionnée */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Cartes de stats */}
                <div>
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        📍 {selectedCity}
                        <span className={`text-sm px-2 py-1 rounded-full ${statsType === 'vente' ? 'bg-primary-500/20 text-primary-400' : 'bg-purple-500/20 text-purple-400'}`}>
                            {statsType === 'vente' ? 'Vente' : 'Location'}
                        </span>
                    </h3>

                    {currentStats ? (
                        <div className="grid grid-cols-2 gap-4">
                            <StatCard
                                icon="📈"
                                label="Prix Moyen"
                                value={formatPrice(currentStats.prix_moyen, statsType === 'location')}
                                color={statsType === 'vente' ? 'orange' : 'blue'}
                                delay={0}
                            />
                            <StatCard
                                icon="📐"
                                label="Surface Moyenne"
                                value={`${Math.round(currentStats.surface_moyenne)} m²`}
                                color="white"
                                delay={0.1}
                            />
                            <StatCard
                                icon="💵"
                                label="Prix au m²"
                                value={`${Math.round(currentStats.prix_m2_moyen).toLocaleString('fr-FR')} DH`}
                                subValue={statsType === 'location' ? '/m²/mois' : '/m²'}
                                color={statsType === 'vente' ? 'orange' : 'blue'}
                                delay={0.2}
                            />
                            <StatCard
                                icon="🏘️"
                                label="Nombre d'annonces"
                                value={currentStats.count}
                                color="white"
                                delay={0.3}
                            />
                        </div>
                    ) : (
                        <div className="text-center text-dark-400 py-8 bg-dark-800 rounded-xl">
                            Aucune donnée disponible pour {statsType === 'vente' ? 'la vente' : 'la location'}
                        </div>
                    )}
                </div>

                {/* Graphique par quartier */}
                <div className="bg-dark-800 rounded-xl p-5 border border-dark-700">
                    <h3 className="text-lg font-semibold text-white mb-4">
                        🗺️ Top Quartiers par Prix
                    </h3>
                    <PriceChart data={currentQuartierData} type={statsType} />
                </div>
            </div>

            {/* Interprétation */}
            {currentStats && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="bg-gradient-to-br from-dark-800 to-dark-900 border border-dark-700 rounded-xl p-6"
                >
                    <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                        💡 Interprétation
                    </h3>
                    <p className="text-dark-300 leading-relaxed">
                        {statsType === 'vente' ? (
                            <>
                                À <strong className="text-primary-400">{selectedCity}</strong>, le prix moyen d'un bien immobilier est de{' '}
                                <strong className="text-primary-400">{formatPrice(currentStats.prix_moyen, false)}</strong>,
                                soit environ <strong className="text-primary-400">{Math.round(currentStats.prix_m2_moyen).toLocaleString('fr-FR')} DH/m²</strong>.
                                La surface moyenne des biens est de <strong className="text-white">{Math.round(currentStats.surface_moyenne)} m²</strong>.
                                {currentQuartierData.length > 0 && (
                                    <> Le quartier le plus cher est <strong className="text-primary-400">{currentQuartierData[0]?.quartier}</strong> avec un prix moyen de {formatPrice(currentQuartierData[0]?.prix_moyen || 0, false)}.</>
                                )}
                            </>
                        ) : (
                            <>
                                À <strong className="text-purple-400">{selectedCity}</strong>, le loyer moyen est de{' '}
                                <strong className="text-purple-400">{formatPrice(currentStats.prix_moyen, true)}</strong>,
                                soit environ <strong className="text-purple-400">{Math.round(currentStats.prix_m2_moyen)} DH/m²/mois</strong>.
                                La surface moyenne des biens en location est de <strong className="text-white">{Math.round(currentStats.surface_moyenne)} m²</strong>.
                                {currentQuartierData.length > 0 && (
                                    <> Le quartier avec les loyers les plus élevés est <strong className="text-purple-400">{currentQuartierData[0]?.quartier}</strong> avec un loyer moyen de {formatPrice(currentQuartierData[0]?.prix_moyen || 0, true)}.</>
                                )}
                            </>
                        )}
                    </p>
                </motion.div>
            )}
        </div>
    );
}
