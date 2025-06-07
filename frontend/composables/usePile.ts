import { useState } from '#app';
import { useAuth } from './useAuth';

export const usePile = () => {
    const { api } = useAuth();
    const piles = useState('piles', () => []);

    const fetchPiles = async () => {
        try {
            const data = await api('/admin/piles');
            piles.value = data;
        } catch (error) {
            console.error("Failed to fetch piles:", error);
            piles.value = [];
        }
    };

    return {
        piles,
        fetchPiles,
    };
}; 