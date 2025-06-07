<template>
  <div class="home-page">
    <!-- 已登录用户界面 -->
    <div v-if="user" class="dashboard-container">
      <!-- 欢迎标题区域 -->
      <div class="welcome-section mb-8">
        <v-row align="center" class="text-center">
          <v-col cols="12">
            <div class="welcome-content">
              <h1 class="display-1 futuristic-font text-glow mb-2">
                欢迎回来，{{ user.username }}！
              </h1>
              <p class="text-h6 mb-4 text-secondary-custom">
                智能充电管理系统已为您准备就绪
              </p>
              <div class="status-indicators d-flex justify-center flex-wrap">
                <v-chip class="ma-1 neon-glow" color="success" variant="outlined">
                  <v-icon start>mdi-check-circle</v-icon>
                  系统在线
                </v-chip>
                <v-chip class="ma-1" color="primary" variant="outlined">
                  <v-icon start>mdi-flash</v-icon>
                  充电桩可用
                </v-chip>
                <v-chip class="ma-1" color="info" variant="outlined">
                  <v-icon start>mdi-shield-check</v-icon>
                  安全保护
                </v-chip>
              </div>
            </div>
          </v-col>
        </v-row>
      </div>

      <!-- 充电仪表盘 -->
      <div class="dashboard-card">
        <ChargingDashboard />
      </div>
    </div>

    <!-- 未登录用户界面 -->
    <div v-else class="landing-page">
      <!-- 主要hero区域 -->
      <section class="hero-section">
        <v-container>
          <v-row align="center" justify="center" class="min-vh-100">
            <v-col cols="12" md="8" lg="6" class="text-center">
              <!-- 主标题动画 -->
              <div class="hero-content">
                <div class="logo-animation mb-6">
                  <v-icon size="120" color="primary" class="pulse">
                    mdi-ev-station
                  </v-icon>
                </div>
                
                <h1 class="display-2 futuristic-font text-glow mb-4">
                  SMART CHARGE
                </h1>
                
                <h2 class="text-h4 mb-6 font-weight-light text-primary-custom">
                  智能电动汽车充电站
                </h2>
                
                <p class="text-h6 mb-8 text-secondary-custom">
                  体验未来充电技术，享受智能化服务
                </p>

                <!-- 特色功能 -->
                <div class="features-grid mb-8">
                  <v-row>
                    <v-col cols="12" sm="4" class="mb-4">
                      <div class="feature-item glass-morph pa-4 card-hover">
                        <v-icon size="48" color="primary" class="mb-3">
                          mdi-lightning-bolt
                        </v-icon>
                        <h3 class="text-h6 mb-2 text-primary-custom">快速充电</h3>
                        <p class="text-body-2 text-muted-custom">
                          支持快充和慢充模式
                        </p>
                      </div>
                    </v-col>
                    <v-col cols="12" sm="4" class="mb-4">
                      <div class="feature-item glass-morph pa-4 card-hover">
                        <v-icon size="48" color="secondary" class="mb-3">
                          mdi-chart-line
                        </v-icon>
                        <h3 class="text-h6 mb-2 text-primary-custom">实时监控</h3>
                        <p class="text-body-2 text-muted-custom">
                          实时查看充电进度
                        </p>
                      </div>
                    </v-col>
                    <v-col cols="12" sm="4" class="mb-4">
                      <div class="feature-item glass-morph pa-4 card-hover">
                        <v-icon size="48" color="success" class="mb-3">
                          mdi-leaf
                        </v-icon>
                        <h3 class="text-h6 mb-2 text-primary-custom">绿色环保</h3>
                        <p class="text-body-2 text-muted-custom">
                          清洁能源充电方案
                        </p>
                      </div>
                    </v-col>
                  </v-row>
                </div>

                <!-- 行动按钮 -->
                <div class="action-buttons">
                  <v-btn
                    to="/register"
                    size="x-large"
                    color="primary"
                    class="btn-futuristic neon-glow mr-4 mb-2"
                    prepend-icon="mdi-account-plus"
                  >
                    立即注册
                  </v-btn>
                  <v-btn
                    to="/login"
                    size="x-large"
                    variant="outlined"
                    color="primary"
                    class="btn-futuristic mb-2"
                    prepend-icon="mdi-login"
                  >
                    用户登录
                  </v-btn>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <!-- 统计数据展示 -->
      <section class="stats-section py-12">
        <v-container>
          <v-row>
            <v-col cols="12" class="text-center mb-8">
              <h2 class="text-h3 futuristic-font text-glow">
                服务数据
              </h2>
            </v-col>
          </v-row>
          <v-row justify="center">
            <v-col cols="6" md="3" class="text-center" v-for="stat in stats" :key="stat.label">
              <div class="stat-item glass-morph pa-6 card-hover">
                <v-icon size="48" :color="stat.color" class="mb-3">
                  {{ stat.icon }}
                </v-icon>
                <h3 class="text-h4 font-weight-bold mb-2 text-glow text-primary-custom">
                  {{ stat.value }}
                </h3>
                <p class="text-body-2 text-muted-custom">
                  {{ stat.label }}
                </p>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useAuth } from '~/composables/useAuth';
import ChargingDashboard from '~/components/ChargingDashboard.vue';

const { user } = useAuth();

// 统计数据
const stats = [
  {
    icon: 'mdi-ev-station',
    value: '50+',
    label: '充电桩数量',
    color: 'primary'
  },
  {
    icon: 'mdi-account-group',
    value: '1000+',
    label: '注册用户',
    color: 'secondary'
  },
  {
    icon: 'mdi-flash',
    value: '10000+',
    label: '充电次数',
    color: 'success'
  },
  {
    icon: 'mdi-leaf',
    value: '99.9%',
    label: '服务可用性',
    color: 'info'
  }
];

definePageMeta({
  layout: 'default'
});
</script>

<style scoped>
.home-page {
  min-height: 100vh;
}

.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.welcome-section {
  text-align: center;
  padding: 2rem 0;
}

.welcome-content {
  position: relative;
}

.status-indicators {
  gap: 1rem;
}

.dashboard-card {
  position: relative;
}

.dashboard-card::before {
  content: '';
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  background: linear-gradient(45deg, #00D9FF, #FF6B35, #9C27B0, #4CAF50);
  border-radius: 20px;
  z-index: -1;
  opacity: 0.1;
  animation: gradientShift 15s ease infinite;
}

.landing-page {
  position: relative;
}

.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.hero-content {
  position: relative;
  z-index: 2;
}

.logo-animation {
  position: relative;
}

.logo-animation::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  border: 2px solid rgba(0, 217, 255, 0.3);
  border-radius: 50%;
  animation: logoRotate 20s linear infinite;
}

@keyframes logoRotate {
  0% {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  100% {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

.features-grid .feature-item {
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  border-radius: 16px;
}

.stats-section {
  background: rgba(26, 26, 46, 0.5);
  backdrop-filter: blur(10px);
}

.stat-item {
  border-radius: 16px;
  height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.action-buttons {
  margin-top: 2rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-content h1 {
    font-size: 2rem !important;
  }
  
  .hero-content h2 {
    font-size: 1.5rem !important;
  }
  
  .features-grid .feature-item {
    height: 150px;
  }
  
  .stat-item {
    height: 120px;
  }
  
  .action-buttons .v-btn {
    width: 100%;
    margin-bottom: 1rem;
  }
}

/* 动画增强 */
.v-enter-active,
.v-leave-active {
  transition: all 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
  transform: translateY(30px);
}
</style> 