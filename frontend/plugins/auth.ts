import { useAuth } from '~/composables/useAuth';

export default defineNuxtPlugin(async (nuxtApp) => {
    const { init } = useAuth();
    await init();
}); 