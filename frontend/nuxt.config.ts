// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  modules: ['vuetify-nuxt-module'],
  vuetify: {
    theme: {
      defaultTheme: 'dark',
      themes: {
        dark: {
          dark: true,
          colors: {
            primary: '#00D9FF',
            secondary: '#FF6B35',
            accent: '#9C27B0',
            error: '#FF5252',
            info: '#2196F3',
            success: '#4CAF50',
            warning: '#FF9800',
            background: '#0F0F23',
            surface: '#1A1A2E',
            'on-primary': '#FFFFFF',
            'on-secondary': '#FFFFFF',
            'on-surface': '#FFFFFF',
            'on-background': '#FFFFFF'
          }
        },
        light: {
          dark: false,
          colors: {
            primary: '#00D9FF',
            secondary: '#FF6B35',
            accent: '#9C27B0',
            error: '#FF5252',
            info: '#2196F3',
            success: '#4CAF50',
            warning: '#FF9800'
          }
        }
      }
    },
    defaults: {
      VCard: {
        class: 'glass-morph card-hover'
      },
      VBtn: {
        class: 'btn-futuristic'
      },
      VAlert: {
        class: 'glass-morph'
      }
    }
  },
  css: ['~/assets/styles/global.css'],
  app: {
    head: {
      title: 'Smart Charging Station',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { hid: 'description', name: 'description', content: 'Smart Electric Vehicle Charging Station Management System' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap' }
      ]
    }
  }
})