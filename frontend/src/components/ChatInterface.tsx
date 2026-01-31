'use client';

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import MessageBubble from './MessageBubble';
import StepButtons from './StepButtons';
import ResultCard from './ResultCard';
import LoadingAnimation from './LoadingAnimation';
import CustomSelect from './CustomSelect';
import { fetchAvailableData, predictPrice } from '@/lib/api';
import { AvailableData, PredictionResult, Step } from '@/types';

interface Message {
    id: string;
    type: 'user' | 'bot';
    content: string;
    timestamp: Date;
    step?: Step;
}

const TRANSACTION_OPTIONS = [
    { label: 'Vente', value: 'vente', icon: '🏠' },
    { label: 'Location', value: 'location', icon: '🔑' },
];

const PROPERTY_OPTIONS = [
    { label: 'Appartement', value: 'Appartement', icon: '🏢' },
    { label: 'Villa', value: 'Villa', icon: '🏡' },
    { label: 'Maison', value: 'Maison', icon: '🏘️' },
    { label: 'Riad', value: 'Riad', icon: '🕌' },
];

const ROOM_OPTIONS = [
    { label: '1', value: '1' },
    { label: '2', value: '2' },
    { label: '3', value: '3' },
    { label: '4', value: '4' },
    { label: '5', value: '5' },
    { label: '6+', value: '6' },
];

const BATHROOM_OPTIONS = [
    { label: '1', value: '1' },
    { label: '2', value: '2' },
    { label: '3', value: '3' },
    { label: '4', value: '4' },
    { label: '5+', value: '5' },
];

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [currentStep, setCurrentStep] = useState<Step>('welcome');
    const [availableData, setAvailableData] = useState<AvailableData | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<PredictionResult | null>(null);

    // Données collectées
    const [transactionType, setTransactionType] = useState('');
    const [propertyType, setPropertyType] = useState('');
    const [city, setCity] = useState('');
    const [quartier, setQuartier] = useState('');
    const [surface, setSurface] = useState('');
    const [rooms, setRooms] = useState('');
    const [bathrooms, setBathrooms] = useState('');

    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Scroll automatique
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, currentStep, result]);

    // Charger les données au démarrage
    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await fetchAvailableData();
                setAvailableData(data);
            } catch (err) {
                console.error('Erreur chargement données:', err);
                setError('Impossible de charger les données. Veuillez réessayer.');
            }
        };
        loadData();

        // Message de bienvenue
        addBotMessage(
            "👋 Bonjour ! Je suis votre assistant d'estimation immobilière. Je vais vous aider à estimer le prix de votre bien au Maroc.\n\nPour commencer, quel type de transaction vous intéresse ?",
            'transaction_type'
        );
    }, []);

    const addBotMessage = (content: string, step?: Step) => {
        const newMessage: Message = {
            id: Date.now().toString(),
            type: 'bot',
            content,
            timestamp: new Date(),
            step,
        };
        setMessages((prev) => [...prev, newMessage]);
        if (step) setCurrentStep(step);
    };

    const addUserMessage = (content: string) => {
        const newMessage: Message = {
            id: Date.now().toString(),
            type: 'user',
            content,
            timestamp: new Date(),
            step,
        };
        setMessages((prev) => [...prev, newMessage]);
    };

    // Gestionnaires d'étapes
    const handleTransactionSelect = (value: string) => {
        const label = value === 'vente' ? '🏠 Vente' : '🔑 Location';
        addUserMessage(label);
        setTransactionType(value);

        setTimeout(() => {
            addBotMessage('Parfait ! Quel type de bien souhaitez-vous évaluer ?', 'property_type');
        }, 300);
    };

    const handlePropertySelect = (value: string) => {
        const option = PROPERTY_OPTIONS.find((o) => o.value === value);
        addUserMessage(`${option?.icon} ${option?.label}`);
        setPropertyType(value);

        setTimeout(() => {
            addBotMessage('Dans quelle ville se trouve votre bien ?', 'city');
        }, 300);
    };

    const handleCitySelect = (value: string) => {
        addUserMessage(`📍 ${value}`);
        setCity(value);

        setTimeout(() => {
            addBotMessage('Sélectionnez le quartier :', 'quartier');
        }, 300);
    };

    const handleQuartierSelect = (value: string) => {
        addUserMessage(`📍 ${value}`);
        setQuartier(value);

        setTimeout(() => {
            addBotMessage('Quelle est la surface du bien (en m²) ?', 'surface');
        }, 300);
    };

    const handleSurfaceSubmit = () => {
        const surfaceNum = parseInt(surface);
        if (isNaN(surfaceNum) || surfaceNum < 10 || surfaceNum > 10000) {
            setError('Veuillez entrer une surface valide (entre 10 et 10 000 m²)');
            return;
        }
        setError(null);
        addUserMessage(`📐 ${surface} m²`);

        setTimeout(() => {
            addBotMessage('Combien de chambres ?', 'rooms');
        }, 300);
    };

    const handleRoomsSelect = (value: string) => {
        addUserMessage(`🛏️ ${value} chambre${parseInt(value) > 1 ? 's' : ''}`);
        setRooms(value);

        setTimeout(() => {
            addBotMessage('Combien de salles de bain ?', 'bathrooms');
        }, 300);
    };

    const handleBathroomsSelect = async (value: string) => {
        addUserMessage(`🚿 ${value} salle${parseInt(value) > 1 ? 's' : ''} de bain`);
        setBathrooms(value);

        setTimeout(() => {
            addBotMessage('🔄 Analyse en cours de vos informations...', 'loading');
            setIsLoading(true);

            // Faire la prédiction après un délai
            setTimeout(async () => {
                await makePrediction(value);
            }, 1500);
        }, 300);
    };

    const makePrediction = async (bathroomsValue: string) => {
        console.log('🔄 makePrediction appelée avec:', { transactionType, city, quartier, propertyType, surface, rooms, bathroomsValue });

        try {
            const payload = {
                transaction_type: transactionType,
                city,
                quartier,
                property_type: propertyType,
                surface_m2: parseInt(surface),
                num_rooms: parseInt(rooms),
                num_bathrooms: parseInt(bathroomsValue),
            };
            console.log('📤 Payload envoyé:', payload);

            const predictionResult = await predictPrice(payload);
            console.log('📥 Résultat reçu:', predictionResult);

            setResult(predictionResult);
            setIsLoading(false);

            // Ajouter un message avec step 'result' pour déclencher l'affichage du ResultCard
            addBotMessage('✨ Voici votre estimation :', 'result');
            console.log('✅ Étape mise à jour vers result');
        } catch (err) {
            console.error('❌ Erreur prédiction:', err);
            setIsLoading(false);
            addBotMessage(
                "❌ Désolé, une erreur s'est produite lors de l'estimation. Veuillez réessayer.",
                'result'
            );
        }
    };

    const handleNewEstimation = () => {
        // Réinitialiser tout
        setMessages([]);
        setCurrentStep('welcome');
        setResult(null);
        setTransactionType('');
        setPropertyType('');
        setCity('');
        setQuartier('');
        setSurface('');
        setRooms('');
        setBathrooms('');
        setError(null);

        // Nouveau message de bienvenue
        setTimeout(() => {
            addBotMessage(
                "👋 Bonjour ! Je suis votre assistant d'estimation immobilière. Je vais vous aider à estimer le prix de votre bien au Maroc.\n\nPour commencer, quel type de transaction vous intéresse ?",
                'transaction_type'
            );
        }, 100);
    };

    const renderCurrentStep = () => {
        switch (currentStep) {
            case 'transaction_type':
                return <StepButtons options={TRANSACTION_OPTIONS} onSelect={handleTransactionSelect} />;

            case 'property_type':
                return <StepButtons options={PROPERTY_OPTIONS} onSelect={handlePropertySelect} />;

            case 'city':
                return (
                    <div className="mt-3 w-full max-w-xs transition-all duration-300 ease-in-out">
                        <CustomSelect
                            options={availableData?.cities.map(c => ({ value: c, label: c, icon: '📍' })) || []}
                            value={city}
                            onChange={(val) => handleCitySelect(val)}
                            placeholder="Choisissez une ville..."
                            icon="🏙️"
                        />
                    </div>
                );

            case 'quartier':
                return (
                    <div className="mt-3 w-full max-w-xs transition-all duration-300 ease-in-out">
                        <CustomSelect
                            options={availableData?.quartiers[city]?.map(q => ({ value: q, label: q, icon: '🏘️' })) || []}
                            value={quartier}
                            onChange={(val) => handleQuartierSelect(val)}
                            placeholder="Choisissez un quartier..."
                            icon="📍"
                        />
                    </div>
                );

            case 'surface':
                return (
                    <div className="mt-3">
                        <div className="flex gap-2">
                            <input
                                type="number"
                                placeholder="Ex: 120"
                                value={surface}
                                onChange={(e) => setSurface(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSurfaceSubmit()}
                                className="flex-1 px-4 py-3 bg-gray-700 text-white rounded-xl border border-gray-600 
                           focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500
                           placeholder-gray-400"
                            />
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={handleSurfaceSubmit}
                                className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl 
                           transition-colors font-medium"
                            >
                                OK
                            </motion.button>
                        </div>
                        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
                    </div>
                );

            case 'rooms':
                return <StepButtons options={ROOM_OPTIONS} onSelect={handleRoomsSelect} columns={6} />;

            case 'bathrooms':
                return (
                    <StepButtons options={BATHROOM_OPTIONS} onSelect={handleBathroomsSelect} columns={6} />
                );

            case 'loading':
                return <LoadingAnimation />;

            case 'result':
                if (result) {
                    return <ResultCard result={result} onNewEstimation={handleNewEstimation} />;
                }
                return null;

            default:
                return null;
        }
    };

    return (
        <div className="flex flex-col h-full bg-dark-950">
            {/* Zone des messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message, index) => (
                    <MessageBubble
                        key={message.id}
                        type={message.type}
                        content={message.content}
                        timestamp={message.timestamp}
                    >
                        {/* Afficher les contrôles uniquement pour le dernier message bot */}
                        {message.type === 'bot' &&
                            index === messages.length - 1 &&
                            message.step === currentStep &&
                            renderCurrentStep()}
                    </MessageBubble>
                ))}
                <div ref={messagesEndRef} />
            </div>
        </div>
    );
}
