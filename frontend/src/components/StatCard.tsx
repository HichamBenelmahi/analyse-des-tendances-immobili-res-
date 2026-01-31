'use client';

import { motion } from 'framer-motion';

interface StatCardProps {
    icon: string;
    label: string;
    value: string | number;
    subValue?: string;
    color?: 'orange' | 'white' | 'green' | 'blue';
    delay?: number;
}

export default function StatCard({ icon, label, value, subValue, color = 'orange', delay = 0 }: StatCardProps) {
    const colorClasses = {
        orange: 'from-primary-500/20 to-primary-600/10 border-primary-500/30',
        white: 'from-dark-700/50 to-dark-800/50 border-dark-600',
        green: 'from-green-500/20 to-green-600/10 border-green-500/30',
        blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
    };

    const textColorClasses = {
        orange: 'text-primary-400',
        white: 'text-white',
        green: 'text-green-400',
        blue: 'text-blue-400',
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay }}
            className={`bg-gradient-to-br ${colorClasses[color]} border rounded-xl p-5 hover:scale-[1.02] transition-transform duration-200`}
        >
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <p className="text-dark-400 text-sm mb-1">{label}</p>
                    <p className={`text-2xl font-bold ${textColorClasses[color]}`}>
                        {typeof value === 'number' ? value.toLocaleString('fr-FR') : value}
                    </p>
                    {subValue && (
                        <p className="text-dark-500 text-xs mt-1">{subValue}</p>
                    )}
                </div>
                <span className="text-3xl">{icon}</span>
            </div>
        </motion.div>
    );
}
