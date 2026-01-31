'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatInterface from '@/components/ChatInterface';
import StatsSection from '@/components/StatsSection';

type TabType = 'home' | 'prediction' | 'stats';

// Theme Toggle Component
const ThemeToggle = ({ isDark, toggle }: { isDark: boolean; toggle: () => void }) => (
    <button
        onClick={toggle}
        className={`relative w-14 h-7 rounded-full transition-colors duration-300 ${isDark ? 'bg-gray-700' : 'bg-orange-100'
            }`}
    >
        <motion.div
            animate={{ x: isDark ? 26 : 2 }}
            transition={{ type: "spring", stiffness: 500, damping: 30 }}
            className={`absolute top-1 w-5 h-5 rounded-full flex items-center justify-center text-xs ${isDark ? 'bg-gray-900' : 'bg-orange-400'
                }`}
        >
            {isDark ? '🌙' : '☀️'}
        </motion.div>
    </button>
);

// Animated Background Pattern
const BackgroundPattern = ({ isDark }: { isDark: boolean }) => (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {/* Gradient Orbs */}
        <div className={`absolute top-0 right-0 w-96 h-96 rounded-full blur-3xl ${isDark ? 'bg-orange-500/10' : 'bg-orange-200/40'
            }`} />
        <div className={`absolute bottom-0 left-0 w-80 h-80 rounded-full blur-3xl ${isDark ? 'bg-orange-600/5' : 'bg-orange-100/50'
            }`} />
        <div className={`absolute top-1/2 left-1/2 w-64 h-64 rounded-full blur-3xl ${isDark ? 'bg-orange-400/5' : 'bg-orange-50/60'
            }`} />

        {/* Grid Pattern */}
        <div
            className="absolute inset-0 opacity-[0.02]"
            style={{
                backgroundImage: `linear-gradient(${isDark ? '#fff' : '#000'} 1px, transparent 1px), linear-gradient(90deg, ${isDark ? '#fff' : '#000'} 1px, transparent 1px)`,
                backgroundSize: '50px 50px'
            }}
        />
    </div>
);

export default function Home() {
    const [activeTab, setActiveTab] = useState<TabType>('home');
    const [isDark, setIsDark] = useState(true);

    // Apply theme to document
    useEffect(() => {
        document.documentElement.classList.toggle('dark', isDark);
    }, [isDark]);

    const LandingPage = () => (
        <div className="relative min-h-[calc(100vh-140px)]">
            {/* Main Content */}
            <div className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-140px)] px-6 py-12">
                {/* Hero Section */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="text-center max-w-3xl"
                >
                    {/* Logo */}
                    <motion.div
                        initial={{ scale: 0, rotate: -180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        transition={{ type: "spring", duration: 1 }}
                        className="relative w-28 h-28 mx-auto mb-8"
                    >
                        <div className="absolute inset-0 bg-gradient-to-br from-orange-400 to-orange-600 rounded-3xl rotate-6 opacity-20" />
                        <div className="absolute inset-0 bg-gradient-to-br from-orange-400 to-orange-600 rounded-3xl -rotate-6 opacity-40" />
                        <div className="relative bg-gradient-to-br from-orange-400 to-orange-600 rounded-3xl w-full h-full flex items-center justify-center shadow-2xl">
                            <span className="text-5xl">🏠</span>
                        </div>
                    </motion.div>

                    {/* Title */}
                    <h1 className={`text-5xl md:text-7xl font-black mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                        Immo<span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-orange-600">Predict</span>
                    </h1>

                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className={`text-xl md:text-2xl font-light mb-2 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}
                    >
                        Maroc
                    </motion.p>

                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4 }}
                        className={`text-lg md:text-xl mb-10 max-w-xl mx-auto ${isDark ? 'text-gray-500' : 'text-gray-500'}`}
                    >
                        Estimez le prix de votre bien immobilier grâce à notre{' '}
                        <span className="text-orange-500 font-semibold">Intelligence Artificielle</span>
                    </motion.p>

                    {/* Feature Tags */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        className="flex flex-wrap justify-center gap-3 mb-12"
                    >
                        {[
                            { icon: '🎯', label: 'Prédiction IA' },
                            { icon: '📊', label: 'Analyse Marché' },
                            { icon: '🏠', label: 'Vente' },
                            { icon: '🔑', label: 'Location' },
                        ].map((tag, i) => (
                            <span
                                key={tag.label}
                                className={`px-4 py-2 rounded-full text-sm font-medium flex items-center gap-2 ${isDark
                                    ? 'bg-white/5 text-gray-300 border border-white/10'
                                    : 'bg-orange-50 text-orange-700 border border-orange-100'
                                    }`}
                            >
                                <span>{tag.icon}</span>
                                {tag.label}
                            </span>
                        ))}
                    </motion.div>

                    {/* CTA Buttons */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 }}
                        className="flex flex-col sm:flex-row gap-4 justify-center"
                    >
                        <motion.button
                            whileHover={{ scale: 1.02, y: -2 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => setActiveTab('prediction')}
                            className="group px-8 py-4 bg-gradient-to-r from-orange-500 to-orange-600 text-white font-bold rounded-2xl shadow-lg shadow-orange-500/25 hover:shadow-xl hover:shadow-orange-500/30 transition-all"
                        >
                            <span className="flex items-center justify-center gap-2">
                                🎯 Estimer mon bien
                                <motion.span
                                    animate={{ x: [0, 4, 0] }}
                                    transition={{ repeat: Infinity, duration: 1.5 }}
                                >
                                    →
                                </motion.span>
                            </span>
                        </motion.button>
                        <motion.button
                            whileHover={{ scale: 1.02, y: -2 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => setActiveTab('stats')}
                            className={`px-8 py-4 font-bold rounded-2xl transition-all ${isDark
                                ? 'bg-white/5 text-white border border-white/10 hover:bg-white/10'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                        >
                            📊 Explorer les données
                        </motion.button>
                    </motion.div>
                </motion.div>

                {/* Stats Preview */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8, duration: 0.5 }}
                    className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 max-w-4xl w-full"
                >
                    {[
                        { icon: '🏢', value: '14K+', label: 'Annonces' },
                        { icon: '🏙️', value: '8+', label: 'Villes' },
                        { icon: '🎯', value: '95%', label: 'Précision' },
                        { icon: '⚡', value: '<1s', label: 'Rapide' },
                    ].map((stat, index) => (
                        <motion.div
                            key={stat.label}
                            whileHover={{ y: -5, scale: 1.02 }}
                            className={`text-center p-6 rounded-2xl backdrop-blur-sm transition-all ${isDark
                                ? 'bg-white/5 border border-white/10 hover:border-orange-500/30'
                                : 'bg-white/80 border border-gray-100 shadow-sm hover:shadow-md'
                                }`}
                        >
                            <div className="text-3xl mb-2">{stat.icon}</div>
                            <div className={`text-3xl font-black ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                {stat.value}
                            </div>
                            <div className={`text-sm ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                                {stat.label}
                            </div>
                        </motion.div>
                    ))}
                </motion.div>

                {/* Data Sources */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1 }}
                    className="mt-16 text-center"
                >
                    <p className={`text-sm mb-4 font-medium uppercase tracking-wider ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                        Sources de données fiables
                    </p>
                    <div className="flex justify-center gap-8 items-center">
                        <div className={`px-4 py-2 rounded-lg border ${isDark ? 'border-white/10 bg-white/5' : 'border-gray-200 bg-white'}`}>
                            <span className={`text-xl font-bold ${isDark ? 'text-blue-400' : 'text-blue-600'}`}>Avito</span>
                        </div>
                        <div className={`px-4 py-2 rounded-lg border ${isDark ? 'border-white/10 bg-white/5' : 'border-gray-200 bg-white'}`}>
                            <span className={`text-xl font-bold ${isDark ? 'text-orange-400' : 'text-orange-600'}`}>Mubawab</span>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );

    return (
        <main className={`min-h-screen transition-colors duration-300 ${isDark ? 'bg-gray-950' : 'bg-gray-50'
            }`}>
            <BackgroundPattern isDark={isDark} />

            {/* Header */}
            <header className={`relative z-50 backdrop-blur-xl border-b px-4 py-4 sticky top-0 ${isDark
                ? 'bg-gray-950/80 border-white/5'
                : 'bg-white/80 border-gray-100'
                }`}>
                <div className="max-w-6xl mx-auto flex items-center justify-between">
                    {/* Logo */}
                    <button
                        onClick={() => setActiveTab('home')}
                        className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
                    >
                        <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-600 rounded-xl flex items-center justify-center shadow-lg">
                            <span className="text-xl">🏠</span>
                        </div>
                        <div className="hidden sm:block">
                            <h1 className={`text-lg font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                Immo<span className="text-orange-500">Predict</span>
                            </h1>
                        </div>
                    </button>

                    {/* Nav */}
                    <div className={`flex rounded-xl p-1 ${isDark ? 'bg-white/5' : 'bg-gray-100'}`}>
                        {[
                            { id: 'home', icon: '🏡', label: 'Accueil' },
                            { id: 'prediction', icon: '🎯', label: 'Prédiction' },
                            { id: 'stats', icon: '📊', label: 'Stats' },
                        ].map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as TabType)}
                                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-1.5 text-sm ${activeTab === tab.id
                                    ? 'bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-lg shadow-orange-500/20'
                                    : isDark
                                        ? 'text-gray-400 hover:text-white'
                                        : 'text-gray-500 hover:text-gray-900'
                                    }`}
                            >
                                <span>{tab.icon}</span>
                                <span className="hidden md:inline">{tab.label}</span>
                            </button>
                        ))}
                    </div>

                    {/* Theme Toggle */}
                    <ThemeToggle isDark={isDark} toggle={() => setIsDark(!isDark)} />
                </div>
            </header>

            {/* Content */}
            <div className="relative z-10 flex-1">
                <AnimatePresence mode="wait">
                    {activeTab === 'home' && (
                        <motion.div
                            key="home"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.2 }}
                        >
                            <LandingPage />
                        </motion.div>
                    )}
                    {activeTab === 'prediction' && (
                        <motion.div
                            key="prediction"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ duration: 0.2 }}
                            className="max-w-3xl w-full mx-auto min-h-[calc(100vh-140px)]"
                        >
                            <ChatInterface />
                        </motion.div>
                    )}
                    {activeTab === 'stats' && (
                        <motion.div
                            key="stats"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ duration: 0.2 }}
                            className="max-w-6xl w-full mx-auto"
                        >
                            <StatsSection />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Footer */}
            <footer className={`relative z-10 border-t px-4 py-4 text-center ${isDark ? 'border-white/5 text-gray-600' : 'border-gray-100 text-gray-400'
                }`}>
                <p className="text-sm">
                    © 2026 ImmoPredict Maroc • Estimations à titre indicatif
                </p>
            </footer>
        </main>
    );
}
