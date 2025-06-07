import { useAuth } from './useAuth';
import { useState } from '#app';

export const useRequest = () => {
    const { api, token, user } = useAuth(); // Re-use the configured $fetch instance from useAuth
    const activeRequest = useState('active_request', () => null);

    const createRequest = async (type, amount) => {
        if (!user.value) throw new Error("User not logged in");

        const response = await api('/requests', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token.value}`
            },
            body: {
                // user_id will be inferred from token on the backend
                requested_charge_type: type,
                requested_charge_amount: amount,
            }
        });
        activeRequest.value = response;
        return response;
    };
    
    const fetchWaitingQueue = async () => {
        return await api('/requests/waiting-queue');
    };

    const fetchActiveRequest = async () => {
        try {
            const userRequest = await api('/requests/me/active', {
                headers: {
                    'Authorization': `Bearer ${token.value}`
                }
            });
            activeRequest.value = userRequest;
        } catch (error) {
            // If the request returns 404 or another error, it means there's no active request.
            // Or the user is logged out, in which case the API call will fail.
            activeRequest.value = null;
        }
    }

    const cancelRequest = async (requestId) => {
        const response = await api(`/requests/${requestId}/cancel`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token.value}`
            }
        });
        await fetchActiveRequest(); // Refresh state
        return response;
    };

    const stopRequest = async (requestId) => {
        const response = await api(`/requests/${requestId}/stop`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token.value}`
            }
        });
        await fetchActiveRequest(); // Refresh state
        return response;
    };

    const updateRequest = async (requestId, updates) => {
        const response = await api(`/requests/${requestId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token.value}`
            },
            body: updates,
        });
        activeRequest.value = response;
        return response;
    };

    return {
        activeRequest,
        createRequest,
        fetchWaitingQueue,
        fetchActiveRequest,
        cancelRequest,
        stopRequest,
        updateRequest,
    };
}; 