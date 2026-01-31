'use client';

import { motion } from 'framer-motion';

interface MessageBubbleProps {
    type: 'user' | 'bot';
    content: string;
    timestamp?: Date;
    children?: React.ReactNode;
}

export default function MessageBubble({ type, content, timestamp, children }: MessageBubbleProps) {
    const isUser = type === 'user';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
        >
            <div
                className={`max-w-[80%] md:max-w-[70%] ${isUser
                    ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-2xl rounded-br-md shadow-orange'
                    : 'bg-dark-800 text-dark-100 rounded-2xl rounded-bl-md border border-dark-700'
                    } px-4 py-3 shadow-lg`}
            >
                {/* Avatar pour le bot */}
                {!isUser && (
                    <div className="flex items-center mb-2">
                        <div className="w-6 h-6 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center mr-2">
                            <span className="text-xs">🏠</span>
                        </div>
                        <span className="text-xs text-dark-400">Assistant Immobilier</span>
                    </div>
                )}

                {/* Contenu du message */}
                <div className="whitespace-pre-wrap text-sm md:text-base">{content}</div>

                {/* Contenu supplémentaire (boutons, sélecteurs, etc.) */}
                {children && <div className="mt-3">{children}</div>}

                {/* Timestamp */}
                {timestamp && (
                    <div className={`text-xs mt-2 ${isUser ? 'text-primary-200' : 'text-dark-500'}`}>
                        {timestamp.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                    </div>
                )}
            </div>
        </motion.div>
    );
}
