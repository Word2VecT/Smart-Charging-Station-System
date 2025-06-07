export default defineNuxtPlugin(() => {
  // 强制设置深色主题
  if (process.client) {
    // 确保HTML和body有正确的背景
    document.documentElement.style.background = 'linear-gradient(135deg, #0F0F23 0%, #1A1A2E 100%)'
    document.documentElement.style.minHeight = '100vh'
    document.body.style.background = 'linear-gradient(135deg, #0F0F23 0%, #1A1A2E 100%)'
    document.body.style.minHeight = '100vh'
    document.body.style.margin = '0'
    document.body.style.padding = '0'
    document.body.style.color = '#E8F4FD'
    
    // 监听路由变化，确保背景始终保持
    window.addEventListener('load', () => {
      const app = document.getElementById('__nuxt')
      if (app) {
        app.style.background = 'linear-gradient(135deg, #0F0F23 0%, #1A1A2E 100%)'
        app.style.minHeight = '100vh'
      }
    })
    
    // 使用MutationObserver监听DOM变化
    const observer = new MutationObserver(() => {
      const app = document.getElementById('__nuxt')
      if (app && !app.style.background.includes('#0F0F23')) {
        app.style.background = 'linear-gradient(135deg, #0F0F23 0%, #1A1A2E 100%)'
        app.style.minHeight = '100vh'
      }
    })
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    })
  }
}) 