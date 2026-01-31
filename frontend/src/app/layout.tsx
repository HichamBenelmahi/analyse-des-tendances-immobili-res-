import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'Estimation Immobilière Maroc | Prédiction de Prix',
    description: 'Estimez le prix de votre bien immobilier au Maroc grâce à notre assistant intelligent. Appartements, villas, maisons et riads à Casablanca, Marrakech, Rabat et Tanger.',
    keywords: 'immobilier, maroc, estimation, prix, appartement, villa, maison, riad, casablanca, marrakech, rabat, tanger',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="fr">
            <body className={inter.className}>{children}</body>
        </html>
    );
}
