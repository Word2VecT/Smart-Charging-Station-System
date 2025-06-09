import { useState } from '#app';
import { useAuth } from './useAuth';

export const useHistory = () => {
    const { api } = useAuth();
    const historyItems = useState('historyItems', () => []);
    const historyItem = useState('historyItem', () => null);

    const fetchHistory = async () => {
        try {
            const data = await api('/history', {
                method: 'GET',
            });
            historyItems.value = data;
        } catch (error) {
            console.error('Failed to fetch history:', error);
            historyItems.value = [];
        }
    };

    const fetchHistoryItemById = async (item_id) => {
        // The detail view for requests is not on a separate page in this design,
        // but this function handles fetching order details.
        try {
            const data = await api(`/history/${item_id}`, {
                method: 'GET',
            });
            historyItem.value = data;
        } catch (error) {
            console.error(`Failed to fetch order ${item_id}:`, error);
            historyItem.value = null;
        }
    };

    return {
        historyItems,
        historyItem,
        fetchHistory,
        fetchHistoryItemById,
    };
}; 