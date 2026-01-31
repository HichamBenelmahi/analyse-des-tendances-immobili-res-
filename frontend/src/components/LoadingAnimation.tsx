'use client';

import { motion } from 'framer-motion';

export default function LoadingAnimation() {
    return (
        <div className="flex items-center space-x-2 py-4">
            <span className="text-gray-400">Analyse en cours</span>
            <div className="flex space-x-1">
                {[0, 1, 2].map((i) => (
                    <motion.div
                        key={i}
                        className="w-2 h-2 bg-blue-500 rounded-full"
                        animate={{
                            y: [0, -8, 0],
                        }}
                        transition={{
                            duration: 0.6,
                            repeat: Infinity,
                            delay: i * 0.15,
                        }}
                    />
                ))}
            </div>
        </div>
    );
}
