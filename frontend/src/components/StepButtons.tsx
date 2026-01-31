'use client';

import { motion } from 'framer-motion';

interface ButtonOption {
    label: string;
    value: string;
    icon?: string;
}

interface StepButtonsProps {
    options: ButtonOption[];
    onSelect: (value: string) => void;
    columns?: number;
}

export default function StepButtons({ options, onSelect, columns = 2 }: StepButtonsProps) {
    const gridCols = {
        1: 'grid-cols-1',
        2: 'grid-cols-2',
        3: 'grid-cols-3',
        4: 'grid-cols-4',
        6: 'grid-cols-3 sm:grid-cols-6',
    };

    return (
        <div className={`grid ${gridCols[columns as keyof typeof gridCols] || 'grid-cols-2'} gap-2 mt-3`}>
            {options.map((option, index) => (
                <motion.button
                    key={option.value}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2, delay: index * 0.05 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => onSelect(option.value)}
                    className="flex items-center justify-center px-4 py-3 bg-dark-800 hover:bg-dark-700 
                     text-white rounded-xl transition-all duration-200 border border-dark-600
                     hover:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50
                     hover:shadow-orange"
                >
                    {option.icon && <span className="mr-2 text-lg">{option.icon}</span>}
                    <span className="text-sm font-medium">{option.label}</span>
                </motion.button>
            ))}
        </div>
    );
}
