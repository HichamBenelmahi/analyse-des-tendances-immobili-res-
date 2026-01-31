'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Option {
    value: string;
    label: string;
    icon?: string;
}

interface CustomSelectProps {
    options: Option[];
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    icon?: string;
}

export default function CustomSelect({ options, value, onChange, placeholder = 'Sélectionner...', icon }: CustomSelectProps) {
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    const selectedOption = options.find(opt => opt.value === value);

    // Close when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <div className="relative" ref={containerRef}>
            <motion.button
                whileTap={{ scale: 0.98 }}
                onClick={() => setIsOpen(!isOpen)}
                className={`
                    flex items-center justify-between w-full min-w-[200px] px-4 py-3 
                    bg-dark-800 border rounded-xl transition-colors duration-200
                    ${isOpen ? 'border-primary-500 ring-2 ring-primary-500/20' : 'border-dark-600 hover:border-dark-500'}
                `}
            >
                <div className="flex items-center gap-2">
                    <span className="text-xl">{icon || selectedOption?.icon || '🏙️'}</span>
                    <span className={`text-sm font-medium ${selectedOption ? 'text-white' : 'text-dark-400'}`}>
                        {selectedOption ? selectedOption.label : placeholder}
                    </span>
                </div>
                <motion.span
                    animate={{ rotate: isOpen ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                    className="text-dark-400 ml-3"
                >
                    ▼
                </motion.span>
            </motion.button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="absolute z-50 w-full mt-2 overflow-hidden bg-dark-900 border border-dark-700 rounded-xl shadow-xl max-h-[300px] overflow-y-auto custom-scrollbar"
                    >
                        {options.map((option) => (
                            <motion.button
                                key={option.value}
                                whileHover={{ backgroundColor: 'rgba(249, 115, 22, 0.1)' }}
                                onClick={() => {
                                    onChange(option.value);
                                    setIsOpen(false);
                                }}
                                className={`
                                    flex items-center w-full px-4 py-3 text-left transition-colors
                                    ${option.value === value ? 'text-primary-500 bg-primary-500/5' : 'text-dark-300'}
                                `}
                            >
                                {option.icon && <span className="mr-2 text-lg">{option.icon}</span>}
                                <span className="text-sm font-medium">{option.label}</span>
                                {option.value === value && (
                                    <span className="ml-auto text-primary-500">✓</span>
                                )}
                            </motion.button>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
