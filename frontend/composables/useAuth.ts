import {
    useState,
    useRouter
} from '#app';
import {
    useCookie
} from '#imports';

export const useAuth = () => {
    const token = useCookie<string | null>('auth_token');
    const user = useState<any | null>('auth_user', () => null);
    const router = useRouter();

    const apiFetch = (endpoint, options = {}) => {
        const headers = options.headers || {};
        if (token.value && !headers.Authorization) {
            headers.Authorization = `Bearer ${token.value}`;
        }

        return $fetch(endpoint, {
            baseURL: 'http://localhost:8000',
            ...options,
            headers,
        });
    };

    const fetchUser = async (tokenOverride?: string) => {
        const currentToken = tokenOverride || token.value;
        if (!currentToken) {
            user.value = null;
            return;
        }
        try {
            const userData = await apiFetch('/auth/users/me', {
                headers: {
                    Authorization: `Bearer ${currentToken}`
                }
            });
            user.value = userData;
        } catch (error) {
            console.error("Failed to fetch user. Token might be invalid.", error);
            // token.value = null; // Do not clear token, it might still be valid.
            user.value = null;
        }
    };

    const login = async (username, password) => {
        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const data = await apiFetch('/auth/token', {
                method: 'POST',
                body: formData,
            });
            
            token.value = data.access_token;

            await fetchUser(data.access_token);
            
            if (user.value) {
                router.push('/');
            } else {
                throw new Error("Login succeeded, but failed to retrieve user details.");
            }
        } catch (error) {
            console.error('Login failed:', error);
            token.value = null;
            user.value = null;
            throw error;
        }
    };

    const register = async (username, password) => {
        try {
            await apiFetch('/auth/register', {
                method: 'POST',
                body: { username, password, role: 'user' },
            });
            await login(username, password);
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    };

    const logout = (redirect = true) => {
        token.value = null;
        user.value = null;
        if (redirect) {
            router.push('/login');
        }
    };

    const init = async () => {
        await fetchUser();
    };

    return {
        token,
        user,
        api: apiFetch, // Keep 'api' for backward compatibility, now pointing to apiFetch
        apiFetch,
        login,
        register,
        logout,
        fetchUser,
        init,
    };
}; 