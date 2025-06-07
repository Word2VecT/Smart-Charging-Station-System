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

    const fetchHistoryItemById = async (item) => {
        // The detail view for requests is not on a separate page in this design,
        // but this function handles fetching order details.
        if (item.item_type === 'ORDER') {
            try {
                const data = await api(`/orders/${item.item_id}`, {
                    method: 'GET',
                });
                historyItem.value = data;
            } catch (error) {
                console.error(`Failed to fetch order ${item.item_id}:`, error);
                historyItem.value = null;
            }
        } else {
            // For requests, we don't have a separate detail page, so we just clear the state
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