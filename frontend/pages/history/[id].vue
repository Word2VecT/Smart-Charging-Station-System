<template>
  <div class="detail-page">
    <!-- 背景装饰 -->
    <div class="detail-background">
      <div class="data-grid"></div>
      <div class="floating-icons">
        <div
          v-for="i in 8"
          :key="i"
          class="data-icon"
          :style="{
            left: Math.random() * 100 + '%',
            animationDelay: Math.random() * 15 + 's',
            animationDuration: (Math.random() * 10 + 8) + 's'
          }"
        >
          <v-icon :icon="getRandomIcon()" size="16" />
        </div>
      </div>
    </div>

    <v-container class="detail-container">
      <!-- 页面标题 -->
      <div class="page-header mb-6">
        <div class="d-flex align-center justify-space-between flex-wrap">
          <div class="header-content">
            <div class="d-flex align-center mb-1">
              <v-icon size="40" color="info" class="mr-3 pulse">
                mdi-receipt-text
              </v-icon>
              <h1 class="text-h3 futuristic-font text-glow text-accent-blue ma-0">
                充电详单
              </h1>
            </div>
            <p class="text-body-1 text-secondary-custom mb-0 ml-12">
              查看您的充电订单详细信息
            </p>
          </div>
          <div class="header-actions d-flex align-center">
            <v-btn
              @click="goBack"
              variant="outlined"
              color="primary"
              class="btn-futuristic mr-3"
              prepend-icon="mdi-arrow-left"
            >
              返回历史
            </v-btn>
            <v-btn
              @click="loadDetails"
              variant="flat"
              color="success"
              class="btn-futuristic neon-glow"
              :loading="loading"
              prepend-icon="mdi-refresh"
            >
              刷新数据
            </v-btn>
          </div>
        </div>
      </div>

             <!-- 加载状态 -->
       <div v-if="loading" class="loading-section text-center mb-6">
         <v-card class="glass-morph card-hover pa-6" elevation="0">
          <v-progress-circular 
            indeterminate 
            color="success" 
            size="64"
            width="4"
            class="mb-4"
          ></v-progress-circular>
          <p class="text-h6 text-primary-custom mb-0 futuristic-font">
            正在加载详单数据...
          </p>
        </v-card>
      </div>

      <!-- 详单内容 -->
      <div v-else-if="historyItem" class="detail-content">
                 <!-- 基本信息卡片 -->
         <v-card class="detail-card glass-morph card-hover mb-4" elevation="0">
           <v-card-title class="detail-card-header pa-4">
             <div class="d-flex align-center">
               <v-icon size="28" color="info" class="mr-3">
                 mdi-receipt-text
               </v-icon>
               <div>
                 <span class="futuristic-font text-glow text-primary-custom text-h6">
                   订单详情
                 </span>
                 <div class="text-caption text-muted-custom mt-1">
                   订单编号: #{{ historyItem.order_id }}
                 </div>
               </div>
             </div>
           </v-card-title>
           
           <v-card-text class="pa-0">
             <div class="detail-grid pa-4">
              <v-row>
                <v-col cols="12" md="6">
                  <div class="info-item glass-inner pa-4">
                    <div class="d-flex align-center mb-2">
                      <v-icon color="success" size="24" class="mr-3">mdi-calendar-clock</v-icon>
                      <span class="text-primary-custom font-weight-bold">详单生成时间</span>
                    </div>
                    <div class="text-h6 text-accent-blue font-weight-medium">
                      {{ formatDateTime(historyItem.created_at) }}
                    </div>
                  </div>
                </v-col>
                <v-col cols="12" md="6">
                  <div class="info-item glass-inner pa-4">
                    <div class="d-flex align-center mb-2">
                      <v-icon color="warning" size="24" class="mr-3">mdi-ev-station</v-icon>
                      <span class="text-primary-custom font-weight-bold">充电桩编号</span>
                    </div>
                    <div class="text-h6 text-warning-custom font-weight-medium">
                      {{ historyItem.pile_code }}
                    </div>
                  </div>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-card>

                 <!-- 充电信息卡片 -->
         <v-card class="detail-card glass-morph card-hover mb-4" elevation="0">
           <v-card-title class="detail-card-header pa-4">
             <div class="d-flex align-center">
               <v-icon size="28" color="success" class="mr-3">
                 mdi-lightning-bolt
               </v-icon>
               <span class="futuristic-font text-glow text-success-custom text-h6">
                 充电信息
               </span>
             </div>
           </v-card-title>
           
           <v-card-text class="pa-0">
             <div class="detail-grid pa-4">
              <v-row>
                <v-col cols="12" md="4">
                  <div class="info-item glass-inner pa-4 text-center">
                    <div class="d-flex align-center justify-center mb-2">
                      <v-icon color="success" size="24" class="mr-2">mdi-battery</v-icon>
                      <span class="text-primary-custom font-weight-bold">充电电量</span>
                    </div>
                    <div class="text-h4 text-success-custom font-weight-bold mb-1">
                      {{ historyItem.actual_charge_amount }}
                    </div>
                    <div class="text-caption text-muted-custom">kWh</div>
                  </div>
                </v-col>
                <v-col cols="12" md="4">
                  <div class="info-item glass-inner pa-4 text-center">
                    <div class="d-flex align-center justify-center mb-2">
                      <v-icon color="info" size="24" class="mr-2">mdi-clock</v-icon>
                      <span class="text-primary-custom font-weight-bold">充电时长</span>
                    </div>
                    <div class="text-h4 text-accent-blue font-weight-bold mb-1">
                      {{ formatDurationShort(historyItem.charge_duration_seconds) }}
                    </div>
                    <div class="text-caption text-muted-custom">
                      {{ formatDuration(historyItem.charge_duration_seconds) }}
                    </div>
                  </div>
                </v-col>
                <v-col cols="12" md="4">
                  <div class="info-item glass-inner pa-4 text-center">
                    <div class="d-flex align-center justify-center mb-2">
                      <v-icon color="warning" size="24" class="mr-2">mdi-currency-cny</v-icon>
                      <span class="text-primary-custom font-weight-bold">总费用</span>
                    </div>
                    <div class="text-h4 text-warning-custom font-weight-bold mb-1">
                      ¥{{ historyItem.total_fee }}
                    </div>
                    <div class="text-caption text-muted-custom">人民币</div>
                  </div>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-card>

                 <!-- 时间信息卡片 -->
         <v-card class="detail-card glass-morph card-hover mb-4" elevation="0">
           <v-card-title class="detail-card-header pa-4">
             <div class="d-flex align-center">
               <v-icon size="28" color="primary" class="mr-3">
                 mdi-timeline-clock
               </v-icon>
               <span class="futuristic-font text-glow text-primary-custom text-h6">
                 时间信息
               </span>
             </div>
           </v-card-title>
           
           <v-card-text class="pa-0">
             <div class="detail-grid pa-4">
              <v-row>
                <v-col cols="12" md="6">
                  <div class="info-item glass-inner pa-4">
                    <div class="d-flex align-center mb-2">
                      <v-icon color="success" size="24" class="mr-3">mdi-play-circle</v-icon>
                      <span class="text-primary-custom font-weight-bold">启动时间</span>
                    </div>
                    <div class="text-h6 text-success-custom font-weight-medium">
                      {{ formatDateTime(historyItem.start_time) }}
                    </div>
                  </div>
                </v-col>
                <v-col cols="12" md="6">
                  <div class="info-item glass-inner pa-4">
                    <div class="d-flex align-center mb-2">
                      <v-icon color="error" size="24" class="mr-3">mdi-stop-circle</v-icon>
                      <span class="text-primary-custom font-weight-bold">停止时间</span>
                    </div>
                    <div class="text-h6 text-error font-weight-medium">
                      {{ formatDateTime(historyItem.end_time) }}
                    </div>
                  </div>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-card>

                 <!-- 费用明细卡片 -->
         <v-card class="detail-card glass-morph card-hover" elevation="0">
           <v-card-title class="detail-card-header pa-4">
             <div class="d-flex align-center">
               <v-icon size="28" color="warning" class="mr-3">
                 mdi-calculator
               </v-icon>
               <span class="futuristic-font text-glow text-warning-custom text-h6">
                 费用明细
               </span>
             </div>
           </v-card-title>
           
           <v-card-text class="pa-0">
             <div class="fee-section pa-4">
              <v-row>
                                 <v-col cols="12" md="4">
                   <div class="fee-item glass-inner pa-4 text-center">
                     <v-icon size="36" color="info" class="mb-2">mdi-flash</v-icon>
                     <h3 class="text-subtitle-1 text-primary-custom mb-2">充电费用</h3>
                    <div class="text-h4 text-accent-blue font-weight-bold">
                      ¥{{ historyItem.charge_fee }}
                    </div>
                  </div>
                </v-col>
                                 <v-col cols="12" md="4">
                   <div class="fee-item glass-inner pa-4 text-center">
                     <v-icon size="36" color="success" class="mb-2">mdi-cog</v-icon>
                     <h3 class="text-subtitle-1 text-primary-custom mb-2">服务费用</h3>
                    <div class="text-h4 text-success-custom font-weight-bold">
                      ¥{{ historyItem.service_fee }}
                    </div>
                  </div>
                </v-col>
                                 <v-col cols="12" md="4">
                   <div class="fee-item glass-inner pa-4 text-center total-fee">
                     <v-icon size="36" color="warning" class="mb-2 pulse">mdi-currency-cny</v-icon>
                     <h3 class="text-subtitle-1 text-primary-custom mb-2">总计费用</h3>
                    <div class="text-h3 text-warning-custom font-weight-bold neon-glow">
                      ¥{{ historyItem.total_fee }}
                    </div>
                  </div>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-card>
      </div>

             <!-- 错误状态 -->
       <div v-else class="error-section text-center">
         <v-card class="glass-morph card-hover pa-6" elevation="0">
          <v-icon size="64" color="error" class="mb-4">mdi-alert-circle</v-icon>
          <h3 class="text-h5 text-error mb-4 futuristic-font">无法加载详单信息</h3>
          <p class="text-body-1 text-muted-custom mb-6">
            抱歉，我们无法获取您的充电详单数据，请稍后重试。
          </p>
          <div class="d-flex justify-center gap-4">
            <v-btn 
              color="primary" 
              variant="outlined" 
              class="btn-futuristic"
              @click="loadDetails"
              prepend-icon="mdi-refresh"
            >
              重新加载
            </v-btn>
            <v-btn 
              color="success" 
              variant="flat" 
              class="btn-futuristic neon-glow"
              @click="goBack"
              prepend-icon="mdi-arrow-left"
            >
              返回历史
            </v-btn>
          </div>
        </v-card>
      </div>
    </v-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useHistory } from '~/composables/useHistory';

const route = useRoute();
const router = useRouter();
const { historyItem, fetchHistoryItemById } = useHistory();
const loading = ref(true);

const loadDetails = async () => {
  loading.value = true;
  const id = route.params.id;
  await fetchHistoryItemById(id);
  loading.value = false;
};

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return 'N/A';
  const options = {
    year: 'numeric', month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  };
  return new Intl.DateTimeFormat('zh-CN', options).format(new Date(dateTimeString));
};

const formatDuration = (seconds) => {
  if (seconds === null || seconds === undefined) return 'N/A';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${h}小时 ${m}分钟 ${s}秒`;
};

const formatDurationShort = (seconds) => {
  if (seconds === null || seconds === undefined) return 'N/A';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}`;
  }
  return `${m}:${Math.floor(seconds % 60).toString().padStart(2, '0')}`;
};

const getRandomIcon = () => {
  const icons = ['mdi-flash', 'mdi-battery', 'mdi-car-electric', 'mdi-ev-station', 'mdi-receipt'];
  return icons[Math.floor(Math.random() * icons.length)];
};

const goBack = () => {
  router.push('/history');
};

onMounted(() => {
  loadDetails();
});

definePageMeta({
  layout: 'default'
});
</script>

<style scoped>
.detail-page {
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

.data-grid {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(90deg, rgba(76, 175, 80, 0.05) 1px, transparent 1px),
    linear-gradient(rgba(76, 175, 80, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  animation: gridMove 30s linear infinite;
}

@keyframes gridMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(40px, 40px);
  }
}

.floating-icons {
  position: absolute;
  width: 100%;
  height: 100%;
}

.data-icon {
  position: absolute;
  color: rgba(76, 175, 80, 0.3);
  animation: iconFloat 10s infinite linear;
}

@keyframes iconFloat {
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
    transform: translateY(-20px) rotate(360deg);
    opacity: 0;
  }
}

.detail-container {
  position: relative;
  z-index: 2;
  padding-top: 2rem;
}

.page-header {
  position: relative;
}

.header-actions {
  gap: 1rem;
}

.detail-card {
  border-radius: 20px;
  border: 1px solid rgba(76, 175, 80, 0.2);
  background: rgba(26, 26, 46, 0.8);
  overflow: hidden;
  transition: all 0.3s ease;
}

.detail-card:hover {
  transform: translateY(-2px);
  border-color: rgba(76, 175, 80, 0.4);
  box-shadow: 0 8px 25px rgba(76, 175, 80, 0.15);
}

.detail-card-header {
  border-bottom: 1px solid rgba(76, 175, 80, 0.2);
  background: rgba(76, 175, 80, 0.05);
}

.info-item {
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.3s ease;
  height: 100%;
}

.info-item:hover {
  border-color: rgba(76, 175, 80, 0.3);
  background: rgba(76, 175, 80, 0.05);
}

.glass-inner {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.02);
}

.fee-item {
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.3s ease;
  height: 100%;
}

.fee-item:hover {
  transform: translateY(-4px);
  border-color: rgba(76, 175, 80, 0.3);
  background: rgba(76, 175, 80, 0.05);
}

.total-fee {
  border-color: rgba(255, 193, 7, 0.3) !important;
  background: rgba(255, 193, 7, 0.05) !important;
}

.total-fee:hover {
  border-color: rgba(255, 193, 7, 0.5) !important;
  background: rgba(255, 193, 7, 0.1) !important;
}

.loading-section .v-card,
.error-section .v-card {
  border-radius: 20px;
  border: 1px solid rgba(76, 175, 80, 0.2);
  background: rgba(26, 26, 46, 0.8);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header .d-flex {
    flex-direction: column;
    align-items: flex-start !important;
  }
  
  .header-actions {
    margin-top: 1rem;
    width: 100%;
  }
  
  .header-actions .v-btn {
    flex: 1;
  }
  
  .data-grid {
    background-size: 25px 25px;
  }
  
  .info-item,
  .fee-item {
    margin-bottom: 1rem;
  }
}
</style>
