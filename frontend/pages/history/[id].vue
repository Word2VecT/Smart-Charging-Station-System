<template>
  <div class="order-detail-page">
    <!-- 背景装饰 -->
    <div class="detail-background">
      <div class="circuit-pattern"></div>
      <div class="floating-data">
        <div
          v-for="i in 8"
          :key="i"
          class="data-particle"
          :style="{
            left: Math.random() * 100 + '%',
            animationDelay: Math.random() * 12 + 's',
            animationDuration: (Math.random() * 8 + 6) + 's'
          }"
        >
          <v-icon :icon="getRandomDataIcon()" size="14" />
        </div>
      </div>
    </div>

    <v-container class="detail-container">
      <!-- 返回按钮 -->
      <div class="navigation-section mb-6">
        <v-btn
          to="/history"
          variant="outlined"
          color="primary"
          class="btn-futuristic back-btn"
          prepend-icon="mdi-arrow-left"
          size="large"
        >
          返回历史记录
        </v-btn>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-section">
        <v-card class="loading-card glass-morph" elevation="0">
          <v-card-text class="text-center pa-12">
            <v-progress-circular
              :size="60"
              :width="4"
              color="primary"
              indeterminate
              class="mb-4"
            ></v-progress-circular>
            <h3 class="text-h5 text-primary-custom mb-2">加载中...</h3>
            <p class="text-body-1 text-secondary-custom">
              正在获取订单详细信息
            </p>
          </v-card-text>
        </v-card>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="!order" class="error-section">
        <v-card class="error-card glass-morph" elevation="0">
          <v-card-text class="text-center pa-12">
            <v-icon size="80" color="error" class="mb-4">
              mdi-alert-circle-outline
            </v-icon>
            <h3 class="text-h4 text-error-custom mb-4">
              订单未找到
            </h3>
            <p class="text-body-1 text-secondary-custom mb-6">
              订单不存在或您没有权限查看此订单
            </p>
            <v-btn
              to="/history"
              variant="flat"
              color="primary"
              class="btn-futuristic"
              prepend-icon="mdi-arrow-left"
            >
              返回历史记录
            </v-btn>
          </v-card-text>
        </v-card>
      </div>

      <!-- 订单详情 -->
      <div v-else class="order-details">
        <!-- 订单标题卡片 -->
        <v-card class="header-card glass-morph card-hover mb-6" elevation="0">
          <v-card-text class="pa-8">
            <div class="d-flex align-center justify-space-between flex-wrap">
              <div class="order-header">
                <div class="d-flex align-center mb-3">
                  <v-icon size="48" color="success" class="mr-4 pulse">
                    mdi-receipt
                  </v-icon>
                  <div>
                    <h1 class="text-h3 futuristic-font text-glow text-accent-blue mb-1">
                      订单 #{{ order.order_id }}
                    </h1>
                    <p class="text-h6 text-secondary-custom ma-0">
                      {{ formatDateTime(order.created_at) }}
                    </p>
                  </div>
                </div>
              </div>
              <div class="order-status">
                <v-chip
                  color="success"
                  variant="elevated"
                  size="large"
                  class="status-chip-large"
                >
                  <v-icon size="16" class="mr-2">mdi-check-circle</v-icon>
                  已完成
                </v-chip>
              </div>
            </div>
          </v-card-text>
        </v-card>

        <!-- 费用信息卡片 -->
        <v-row class="mb-6">
          <v-col cols="12" md="8">
            <v-card class="fee-card glass-morph card-hover" elevation="0">
              <v-card-title class="card-title pa-6">
                <div class="d-flex align-center">
                  <v-icon size="32" color="warning" class="mr-3">
                    mdi-currency-cny
                  </v-icon>
                  <span class="futuristic-font text-glow">费用详情</span>
                </div>
              </v-card-title>
              <v-card-text class="pa-6">
                <v-row>
                  <v-col cols="12" sm="4">
                    <div class="fee-item text-center">
                      <div class="fee-icon mb-3">
                        <v-icon size="40" color="success">mdi-cash-multiple</v-icon>
                      </div>
                      <h3 class="text-h4 text-success-custom font-weight-bold mb-2">
                        ¥{{ order.total_fee.toFixed(2) }}
                      </h3>
                      <p class="text-body-1 text-muted-custom">总费用</p>
                    </div>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <div class="fee-item text-center">
                      <div class="fee-icon mb-3">
                        <v-icon size="40" color="info">mdi-cog</v-icon>
                      </div>
                      <h3 class="text-h4 text-info-custom font-weight-bold mb-2">
                        ¥{{ order.service_fee.toFixed(2) }}
                      </h3>
                      <p class="text-body-1 text-muted-custom">服务费</p>
                    </div>
                  </v-col>
                  <v-col cols="12" sm="4">
                    <div class="fee-item text-center">
                      <div class="fee-icon mb-3">
                        <v-icon size="40" color="primary">mdi-lightning-bolt</v-icon>
                      </div>
                      <h3 class="text-h4 text-primary-custom font-weight-bold mb-2">
                        ¥{{ order.charge_fee.toFixed(2) }}
                      </h3>
                      <p class="text-body-1 text-muted-custom">充电费</p>
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card class="energy-card glass-morph card-hover" elevation="0">
              <v-card-title class="card-title pa-6">
                <div class="d-flex align-center">
                  <v-icon size="32" color="success" class="mr-3">
                    mdi-battery-charging
                  </v-icon>
                  <span class="futuristic-font text-glow">充电量</span>
                </div>
              </v-card-title>
              <v-card-text class="pa-6 text-center">
                <div class="energy-display">
                  <div class="energy-circle mb-4">
                    <v-progress-circular
                      :model-value="100"
                      :size="120"
                      :width="8"
                      color="success"
                      class="energy-progress"
                    >
                      <div class="energy-value">
                        <h2 class="text-h3 text-success-custom font-weight-bold">
                          {{ order.actual_charge_amount.toFixed(1) }}
                        </h2>
                        <p class="text-body-2 text-muted-custom">kWh</p>
                      </div>
                    </v-progress-circular>
                  </div>
                  <p class="text-body-1 text-secondary-custom">
                    实际充电量
                  </p>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 充电信息卡片 -->
        <v-row class="mb-6">
          <v-col cols="12" md="6">
            <v-card class="time-card glass-morph card-hover" elevation="0">
              <v-card-title class="card-title pa-6">
                <div class="d-flex align-center">
                  <v-icon size="32" color="info" class="mr-3">
                    mdi-clock-outline
                  </v-icon>
                  <span class="futuristic-font text-glow">充电时间</span>
                </div>
              </v-card-title>
              <v-card-text class="pa-6">
                <div class="time-info">
                  <div class="time-item mb-4">
                    <div class="d-flex align-center mb-2">
                      <v-icon size="20" color="success" class="mr-2">
                        mdi-play-circle
                      </v-icon>
                      <span class="text-body-1 font-weight-medium text-primary-custom">
                        开始时间
                      </span>
                    </div>
                    <p class="text-h6 text-secondary-custom ml-7">
                      {{ formatDateTime(order.start_time) }}
                    </p>
                  </div>
                  <div class="time-item mb-4">
                    <div class="d-flex align-center mb-2">
                      <v-icon size="20" color="error" class="mr-2">
                        mdi-stop-circle
                      </v-icon>
                      <span class="text-body-1 font-weight-medium text-primary-custom">
                        结束时间
                      </span>
                    </div>
                    <p class="text-h6 text-secondary-custom ml-7">
                      {{ formatDateTime(order.end_time) }}
                    </p>
                  </div>
                  <div class="duration-display pa-4 rounded-lg">
                    <div class="text-center">
                      <v-icon size="40" color="warning" class="mb-2">
                        mdi-timer
                      </v-icon>
                      <h3 class="text-h5 text-warning-custom font-weight-bold">
                        {{ chargeDuration }}
                      </h3>
                      <p class="text-body-2 text-muted-custom">充电时长</p>
                    </div>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="6">
            <v-card class="device-card glass-morph card-hover" elevation="0">
              <v-card-title class="card-title pa-6">
                <div class="d-flex align-center">
                  <v-icon size="32" color="primary" class="mr-3">
                    mdi-ev-station
                  </v-icon>
                  <span class="futuristic-font text-glow">设备信息</span>
                </div>
              </v-card-title>
              <v-card-text class="pa-6">
                <div class="device-info">
                  <div class="device-item mb-6">
                    <div class="d-flex align-center justify-space-between pa-4 device-item-bg rounded-lg">
                      <div class="d-flex align-center">
                        <v-icon size="32" color="primary" class="mr-3">
                          mdi-tower-fire
                        </v-icon>
                        <div>
                          <p class="text-body-1 font-weight-medium text-primary-custom mb-1">
                            充电桩 ID
                          </p>
                          <h3 class="text-h5 text-accent-blue font-weight-bold">
                            #{{ order.pile_id }}
                          </h3>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="device-item">
                    <div class="d-flex align-center justify-space-between pa-4 device-item-bg rounded-lg">
                      <div class="d-flex align-center">
                        <v-icon size="32" color="secondary" class="mr-3">
                          mdi-identifier
                        </v-icon>
                        <div>
                          <p class="text-body-1 font-weight-medium text-primary-custom mb-1">
                            请求 ID
                          </p>
                          <h3 class="text-h5 text-accent-orange font-weight-bold">
                            #{{ order.request_id }}
                          </h3>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useOrder } from '~/composables/useOrder';

const route = useRoute();
const { order, fetchOrderById } = useOrder();
const loading = ref(false);

const orderId = route.params.id;

const chargeDuration = computed(() => {
  if (!order.value) return 'N/A';
  const start = new Date(order.value.start_time);
  const end = new Date(order.value.end_time);
  const diffMs = end - start;
  const diffMins = Math.round(diffMs / 60000);
  const hours = Math.floor(diffMins / 60);
  const mins = diffMins % 60;
  
  if (hours > 0) {
    return `${hours}小时${mins}分钟`;
  }
  return `${mins}分钟`;
});

const formatDateTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

const getRandomDataIcon = () => {
  const icons = ['mdi-chart-line', 'mdi-database', 'mdi-server', 'mdi-cloud'];
  return icons[Math.floor(Math.random() * icons.length)];
};

onMounted(async () => {
  loading.value = true;
  try {
    await fetchOrderById(orderId);
  } finally {
    loading.value = false;
  }
});

definePageMeta({
  layout: 'default'
});
</script>

<style scoped>
.order-detail-page {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(135deg, #0F0F23 0%, #1A1A2E 100%) !important;
}

.detail-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}

.circuit-pattern {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(0, 217, 255, 0.1) 2px, transparent 2px),
    radial-gradient(circle at 75% 75%, rgba(255, 107, 53, 0.1) 2px, transparent 2px),
    linear-gradient(90deg, rgba(0, 217, 255, 0.03) 1px, transparent 1px),
    linear-gradient(rgba(255, 107, 53, 0.03) 1px, transparent 1px);
  background-size: 100px 100px, 100px 100px, 25px 25px, 25px 25px;
  animation: circuitMove 20s linear infinite;
}

@keyframes circuitMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(25px, 25px);
  }
}

.floating-data {
  position: absolute;
  width: 100%;
  height: 100%;
}

.data-particle {
  position: absolute;
  color: rgba(0, 217, 255, 0.4);
  animation: dataFloat 8s infinite linear;
}

@keyframes dataFloat {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  80% {
    opacity: 1;
  }
  100% {
    transform: translateY(-50px) rotate(360deg);
    opacity: 0;
  }
}

.detail-container {
  position: relative;
  z-index: 2;
  padding-top: 2rem;
}

.back-btn {
  border-radius: 12px;
  font-weight: 600;
}

.loading-card,
.error-card {
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(26, 26, 46, 0.8);
}

.header-card {
  border-radius: 20px;
  border: 1px solid rgba(0, 217, 255, 0.3);
  background: rgba(26, 26, 46, 0.8);
}

.status-chip-large {
  font-size: 1rem;
  font-weight: bold;
  padding: 0.5rem 1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.fee-card,
.energy-card,
.time-card,
.device-card {
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(26, 26, 46, 0.8);
  height: 100%;
}

.card-title {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
}

.fee-item {
  transition: all 0.3s ease;
}

.fee-item:hover {
  transform: translateY(-4px);
}

.fee-icon {
  position: relative;
}

.fee-icon::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: iconPulse 2s infinite;
}

@keyframes iconPulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.1;
  }
}

.energy-display {
  position: relative;
}

.energy-circle {
  position: relative;
  display: inline-block;
}

.energy-progress {
  filter: drop-shadow(0 0 4px rgba(76, 175, 80, 0.2));
}

.energy-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.time-info {
  position: relative;
}

.time-item {
  position: relative;
  padding-left: 1rem;
}

.time-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.5rem;
  width: 2px;
  height: calc(100% - 1rem);
  background: linear-gradient(to bottom, rgba(0, 217, 255, 0.5), rgba(255, 107, 53, 0.5));
  border-radius: 1px;
}

.duration-display {
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
}

.device-item-bg {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.device-item-bg:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 217, 255, 0.3);
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .order-header .d-flex {
    flex-direction: column;
    align-items: flex-start !important;
  }
  
  .order-status {
    margin-top: 1rem;
    width: 100%;
  }
  
  .fee-item {
    margin-bottom: 2rem;
  }
  
  .circuit-pattern {
    background-size: 60px 60px, 60px 60px, 15px 15px, 15px 15px;
  }
  
  .energy-progress {
    width: 100px !important;
    height: 100px !important;
  }
  
  .energy-value h2 {
    font-size: 1.5rem !important;
  }
}

/* 卡片悬停效果增强 */
.card-hover:hover {
  transform: translateY(-3px);
  box-shadow: 
    0 8px 16px rgba(0, 0, 0, 0.2),
    0 0 12px rgba(0, 217, 255, 0.08);
}

/* 加载动画 */
.loading-card .v-progress-circular {
  filter: drop-shadow(0 0 4px rgba(0, 217, 255, 0.2));
}
</style> 