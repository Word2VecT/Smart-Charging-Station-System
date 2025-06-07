<template>
  <div class="auth-page">
    <!-- 背景装饰元素 -->
    <div class="auth-background">
      <div class="floating-particles">
        <div
          v-for="i in 30"
          :key="i"
          class="particle"
          :style="{
            left: Math.random() * 100 + '%',
            animationDelay: Math.random() * 10 + 's',
            animationDuration: (Math.random() * 8 + 4) + 's'
          }"
        ></div>
      </div>
      <div class="grid-overlay"></div>
    </div>

    <v-container class="auth-container">
      <v-row justify="center" align="center" class="min-vh-100">
        <v-col cols="12" sm="10" md="8" lg="6" xl="4">
          <!-- 主登录卡片 -->
          <div class="auth-card-wrapper">
            <v-card class="auth-card glass-morph card-hover" elevation="0">
              <!-- 标题区域 -->
              <div class="auth-header text-center pa-8">
                <div class="auth-logo mb-6">
                  <v-icon size="80" color="primary" class="pulse">
                    mdi-account-lock
                  </v-icon>
                  <div class="logo-ring"></div>
                </div>
                <h1 class="text-h3 futuristic-font text-glow text-accent-blue mb-2">
                  用户登录
                </h1>
                <p class="text-body-1 text-secondary-custom">
                  访问智能充电管理系统
                </p>
              </div>

              <!-- 表单区域 -->
              <v-card-text class="pa-8">
                <v-alert 
                  v-if="error" 
                  type="error" 
                  class="mb-6 glass-morph"
                  prominent
                  border="start"
                >
                  {{ error }}
                </v-alert>

                <v-form @submit.prevent="handleLogin" class="auth-form">
                  <div class="form-group mb-6">
                    <v-text-field
                      v-model="username"
                      label="用户名"
                      prepend-inner-icon="mdi-account"
                      variant="outlined"
                      required
                      :disabled="loading"
                      class="auth-input"
                      color="primary"
                    ></v-text-field>
                  </div>

                  <div class="form-group mb-8">
                    <v-text-field
                      v-model="password"
                      label="密码"
                      type="password"
                      prepend-inner-icon="mdi-lock"
                      variant="outlined"
                      required
                      :disabled="loading"
                      class="auth-input"
                      color="primary"
                    ></v-text-field>
                  </div>

                  <div class="form-actions">
                    <v-btn
                      type="submit"
                      size="x-large"
                      color="primary"
                      class="auth-submit-btn btn-futuristic neon-glow mb-4"
                      :loading="loading"
                      :disabled="loading"
                      block
                      prepend-icon="mdi-login"
                    >
                      <span class="futuristic-font">登录系统</span>
                    </v-btn>
                    
                    <div class="auth-links text-center">
                      <p class="text-body-2 text-muted-custom mb-2">
                        还没有账户？
                      </p>
                      <NuxtLink 
                        to="/register" 
                        class="auth-link text-accent-blue"
                      >
                        立即注册 →
                      </NuxtLink>
                    </div>
                  </div>
                </v-form>
              </v-card-text>
            </v-card>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuth } from '~/composables/useAuth';

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref(null);
const { login } = useAuth();

const handleLogin = async () => {
  loading.value = true;
  error.value = null;
  try {
    await login(username.value, password.value);
    // Redirect on success is handled within useAuth
  } catch (e) {
    error.value = e.data?.detail || 'An unknown error occurred during login.';
  } finally {
    loading.value = false;
  }
};

definePageMeta({
  layout: 'default'
});
</script>

<style scoped>
.auth-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #0F0F23 0%, #1A1A2E 100%) !important;
}

.auth-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}

.floating-particles {
  position: absolute;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  width: 3px;
  height: 3px;
  background: var(--text-accent-blue);
  border-radius: 50%;
  animation: particleFloat 6s infinite linear;
  opacity: 0.6;
}

@keyframes particleFloat {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-10vh) rotate(360deg);
    opacity: 0;
  }
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(90deg, rgba(0, 217, 255, 0.05) 1px, transparent 1px),
    linear-gradient(rgba(0, 217, 255, 0.05) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

.auth-container {
  position: relative;
  z-index: 2;
}

.auth-card-wrapper {
  position: relative;
}

.auth-card {
  border-radius: 24px !important;
  border: 1px solid rgba(0, 217, 255, 0.3) !important;
  background: rgba(26, 26, 46, 0.9) !important;
  backdrop-filter: blur(20px) !important;
  overflow: hidden;
}

.auth-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 217, 255, 0.1), rgba(255, 107, 53, 0.05));
  z-index: -1;
  opacity: 0.5;
}

.auth-header {
  position: relative;
  border-bottom: 1px solid rgba(0, 217, 255, 0.2);
}

.auth-logo {
  position: relative;
  display: inline-block;
}

.logo-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  border: 2px solid rgba(0, 217, 255, 0.3);
  border-radius: 50%;
  animation: logoRotate 15s linear infinite;
}

@keyframes logoRotate {
  0% {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  100% {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

.auth-form {
  position: relative;
}

.form-group {
  position: relative;
}

.auth-input :deep(.v-field) {
  border-radius: 12px !important;
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(0, 217, 255, 0.2) !important;
}

.auth-input :deep(.v-field:hover) {
  border-color: rgba(0, 217, 255, 0.4) !important;
}

.auth-input :deep(.v-field--focused) {
  border-color: var(--text-accent-blue) !important;
  box-shadow: 0 0 15px rgba(0, 217, 255, 0.3) !important;
}

.auth-submit-btn {
  position: relative;
  border-radius: 12px !important;
  background: linear-gradient(45deg, var(--text-accent-blue), rgba(0, 217, 255, 0.8)) !important;
  height: 56px !important;
  font-size: 1.1rem !important;
  letter-spacing: 1px !important;
}

.auth-submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s;
}

.auth-submit-btn:hover::before {
  left: 100%;
}

.auth-links {
  margin-top: 2rem;
}

.auth-link {
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  text-decoration: none !important;
}

.auth-link:hover {
  color: var(--text-accent-orange) !important;
  text-shadow: 0 0 10px currentColor;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .auth-header {
    padding: 2rem 1.5rem !important;
  }
  
  .auth-card-text {
    padding: 1.5rem !important;
  }
  
  .auth-logo .v-icon {
    font-size: 60px !important;
  }
  
  .logo-ring {
    width: 90px;
    height: 90px;
  }
  
  .particle {
    width: 2px;
    height: 2px;
  }
  
  .grid-overlay {
    background-size: 30px 30px;
  }
}

/* 加载状态动画 */
.auth-submit-btn.v-btn--loading {
  background: linear-gradient(45deg, rgba(0, 217, 255, 0.6), rgba(0, 217, 255, 0.4)) !important;
}
</style> 