<template>
  <div class="charging-dashboard">
    <!-- 主要充电卡片 -->
    <v-card class="dashboard-card glass-morph card-hover" elevation="0">
      <v-card-title class="dashboard-title">
        <div class="d-flex align-center">
          <v-icon size="32" color="primary" class="mr-3 pulse">
            mdi-ev-station
          </v-icon>
          <span class="futuristic-font text-glow text-primary-custom">充电控制中心</span>
        </div>
      </v-card-title>

      <v-card-text class="pa-6">
        <!-- 显示活跃请求状态 -->
        <div v-if="activeRequest" class="active-request-section">
          <!-- 状态警告卡片 -->
          <v-alert
            :type="alertType"
            class="status-alert mb-6 glass-morph"
            prominent
            :icon="getStatusIcon()"
            border="start"
          >
            <div class="d-flex align-center justify-space-between">
              <div class="status-content">
                <h3 class="text-h6 mb-2">{{ getStatusText() }}</h3>
                <p class="text-body-2 mb-0 text-grey-lighten-1">
                  {{ getStatusDescription() }}
                </p>
              </div>
              <div class="status-animation">
                <div v-if="activeRequest.status === 'WAITING'" class="waiting-loader">
                  <!-- Vuetify圆形进度条 -->
                  <v-progress-circular 
                    indeterminate 
                    size="40"
                    width="3"
                    color="primary"
                    class="waiting-progress"
                    :rotate="0"
                  ></v-progress-circular>
                  
                  <!-- 备用CSS动画圆圈（如果上面的不显示） -->
                  <div class="custom-spinner" v-show="false">
                    <div class="spinner-ring"></div>
                  </div>
                </div>
                <v-icon 
                  v-else-if="activeRequest.status === 'CHARGING'" 
                  size="40"
                  color="success"
                  class="pulse"
                >
                  mdi-flash
                </v-icon>
              </div>
            </div>
          </v-alert>

          <!-- 请求详情网格 -->
          <div class="request-details mb-6">
            <v-row>
              <!-- 队列信息 -->
              <v-col cols="12" md="6">
                <div class="detail-card glass-morph pa-4 h-100">
                  <div class="d-flex align-center mb-3">
                    <v-icon color="primary" class="mr-2">mdi-format-list-numbered</v-icon>
                    <h4 class="text-h6">队列信息</h4>
                  </div>
                  <div class="detail-content">
                    <div class="info-row">
                      <span class="label">队列号码:</span>
                      <span class="value text-primary font-weight-bold">
                        #{{ activeRequest.queue_number }}
                      </span>
                    </div>
                    <div v-if="activeRequest.status === 'WAITING'" class="info-row">
                      <span class="label">前方车辆:</span>
                      <span class="value text-warning font-weight-bold">
                        {{ waitingInfo.carsAhead }} 辆
                      </span>
                    </div>
                  </div>
                </div>
              </v-col>

              <!-- 充电详情 -->
              <v-col cols="12" md="6">
                <div class="detail-card glass-morph pa-4 h-100">
                  <div class="d-flex align-center mb-3">
                    <v-icon color="secondary" class="mr-2">mdi-information</v-icon>
                    <h4 class="text-h6">充电详情</h4>
                  </div>
                  <div class="detail-content">
                    <div class="info-row">
                      <span class="label">充电类型:</span>
                      <v-chip 
                        :color="activeRequest.requested_charge_type === 'FAST' ? 'success' : 'info'"
                        size="small"
                        variant="outlined"
                      >
                        {{ activeRequest.requested_charge_type === 'FAST' ? '快充' : '慢充' }}
                      </v-chip>
                    </div>
                    <div class="info-row">
                      <span class="label">充电量:</span>
                      <span class="value text-success font-weight-bold">
                        {{ activeRequest.requested_charge_amount }} kWh
                      </span>
                    </div>
                  </div>
                </div>
              </v-col>
            </v-row>
          </div>

          <!-- 充电进度（仅充电状态显示） -->
          <div v-if="activeRequest.status === 'CHARGING'" class="charging-progress mb-6">
            <div class="progress-card glass-morph pa-6">
              <div class="d-flex align-center justify-space-between mb-4">
                <div>
                  <h4 class="text-h6 mb-1">充电桩 #{{ activeRequest.assigned_pile_id }}</h4>
                  <p class="text-body-2 text-grey-lighten-1 mb-0">
                    功率: {{ pilePowerRate }} kW
                  </p>
                </div>
                <div class="charging-icon">
                  <v-icon size="48" color="success" class="pulse">
                    mdi-battery-charging
                  </v-icon>
                </div>
              </div>

              <!-- 进度条 -->
              <div class="progress-container">
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-body-2">充电进度</span>
                  <span class="text-h6 font-weight-bold text-success text-glow">
                    {{ chargePercentage.toFixed(1) }}%
                  </span>
                </div>
                <v-progress-linear
                  :model-value="chargePercentage"
                  color="success"
                  height="20"
                  striped
                  class="progress-animated neon-glow"
                  rounded
                >
                  <template v-slot:default="{ value }">
                    <strong class="text-white">{{ Math.ceil(value) }}%</strong>
                  </template>
                </v-progress-linear>
                <div class="d-flex justify-space-between align-center mt-2">
                  <span class="text-caption text-grey-lighten-1">
                    已充电: {{ chargedAmount.toFixed(2) }} kWh
                  </span>
                  <span class="text-caption text-grey-lighten-1">
                    目标: {{ activeRequest.requested_charge_amount }} kWh
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作按钮区域 -->
          <div class="action-buttons">
            <!-- 等待状态的操作 -->
            <div v-if="activeRequest.status === 'WAITING'" class="d-flex flex-wrap gap-3">
              <v-btn
                color="warning"
                variant="outlined"
                class="btn-futuristic mr-4"
                @click="isEditing = !isEditing"
                prepend-icon="mdi-pencil"
              >
                修改请求
              </v-btn>
              <v-btn
                color="error"
                variant="outlined"
                class="btn-futuristic"
                @click="handleCancel"
                prepend-icon="mdi-close-circle"
              >
                取消请求
              </v-btn>
            </div>

            <!-- 充电状态的操作 -->
            <div v-if="activeRequest.status === 'CHARGING'" class="d-flex justify-center gap-4">
              <v-btn
                color="error"
                size="large"
                class="btn-futuristic neon-glow"
                @click="handleStop"
                prepend-icon="mdi-stop-circle"
              >
                停止充电
              </v-btn>
              <v-btn
                color="orange"
                size="large"
                class="btn-futuristic neon-glow"
                @click="handleFaultReport"
                prepend-icon="mdi-alert-circle"
              >
                故障上报
              </v-btn>
            </div>
          </div>

          <!-- 修改表单 -->
          <v-expand-transition>
            <div v-if="isEditing" class="edit-form mt-6">
              <v-card class="glass-morph" elevation="0">
                <v-card-title class="text-h6">
                  <v-icon color="warning" class="mr-2">mdi-pencil</v-icon>
                  修改充电请求
                </v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-select
                        v-model="editForm.type"
                        :items="[
                          { title: '快速充电', value: 'FAST' },
                          { title: '慢速充电', value: 'TRICKLE' }
                        ]"
                        label="充电类型"
                        variant="outlined"
                        prepend-inner-icon="mdi-flash"
                      ></v-select>
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model.number="editForm.amount"
                        label="充电量 (kWh)"
                        type="number"
                        min="1"
                        variant="outlined"
                        prepend-inner-icon="mdi-battery"
                      ></v-text-field>
                    </v-col>
                  </v-row>
                </v-card-text>
                <v-card-actions class="px-4 pb-4">
                  <v-btn
                    color="primary"
                    class="btn-futuristic"
                    @click="handleUpdate"
                    prepend-icon="mdi-content-save"
                  >
                    保存修改
                  </v-btn>
                  <v-spacer></v-spacer>
                  <v-btn
                    variant="outlined"
                    @click="isEditing = false"
                    prepend-icon="mdi-close"
                  >
                    取消
                  </v-btn>
                </v-card-actions>
              </v-card>
            </div>
          </v-expand-transition>
        </div>

        <!-- 新建请求表单 -->
        <div v-else class="new-request-section">
          <div class="text-center mb-6">
            <v-icon size="80" color="primary" class="mb-4 pulse">
              mdi-ev-station
            </v-icon>
            <h3 class="text-h5 mb-2 futuristic-font">创建充电请求</h3>
            <p class="text-body-1 text-grey-lighten-1">
              选择您的充电偏好，我们将为您安排最佳的充电方案
            </p>
          </div>

          <v-form @submit.prevent="handleSubmit" class="request-form">
            <v-alert v-if="error" type="error" class="mb-4 glass-morph">
              {{ error }}
            </v-alert>

            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="form.type"
                  :items="[
                    { title: '快速充电 (推荐)', value: 'FAST' },
                    { title: '慢速充电 (经济)', value: 'TRICKLE' }
                  ]"
                  label="选择充电类型"
                  required
                  variant="outlined"
                  prepend-inner-icon="mdi-flash"
                  class="mb-4"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="form.amount"
                  label="充电量 (kWh)"
                  type="number"
                  min="1"
                  required
                  variant="outlined"
                  prepend-inner-icon="mdi-battery"
                  class="mb-4"
                ></v-text-field>
              </v-col>
            </v-row>

            <div class="text-center">
              <v-btn
                type="submit"
                color="primary"
                size="x-large"
                class="btn-futuristic neon-glow"
                :loading="loading"
                prepend-icon="mdi-send"
              >
                提交充电请求
              </v-btn>
            </div>
          </v-form>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, onUnmounted } from 'vue';
import { useRequest } from '~/composables/useRequest';
import { usePile } from '~/composables/usePile';

const { activeRequest, createRequest, fetchActiveRequest, cancelRequest, updateRequest, fetchWaitingQueue, stopRequest, reportFault } = useRequest();
const { piles, fetchPiles } = usePile();

const loading = ref(false);
const error = ref(null);
const isEditing = ref(false);
const waitingInfo = ref({ carsAhead: 0 });
let pollingInterval = null;

const form = reactive({
  type: 'FAST',
  amount: 10,
});

const editForm = reactive({
  type: '',
  amount: 0,
});

const alertType = computed(() => {
  if (!activeRequest.value) return 'info';
  switch (activeRequest.value.status) {
    case 'WAITING': return 'info';
    case 'CHARGING': return 'success';
    default: return 'secondary';
  }
});

const chargedAmount = computed(() => {
    if (activeRequest.value?.status !== 'CHARGING' || !activeRequest.value.start_time) {
        return 0;
    }
    const pile = piles.value.find(p => p.pile_id === activeRequest.value.assigned_pile_id);
    if (!pile) return 0;

    const startTime = new Date(activeRequest.value.start_time);
    const now = new Date();
    const durationSeconds = (now.getTime() - startTime.getTime()) / 1000;
    return (durationSeconds / 3600) * pile.power_rate;
});

const chargePercentage = computed(() => {
    if (!activeRequest.value || activeRequest.value.requested_charge_amount <= 0) {
        return 0;
    }
    return (chargedAmount.value / activeRequest.value.requested_charge_amount) * 100;
});

const pilePowerRate = computed(() => {
    if (activeRequest.value?.status !== 'CHARGING') return 0;
    const pile = piles.value.find(p => p.pile_id === activeRequest.value.assigned_pile_id);
    return pile ? pile.power_rate : 0;
});

// 新增的状态相关方法
const getStatusIcon = () => {
    if (!activeRequest.value) return 'mdi-information';
    switch (activeRequest.value.status) {
        case 'WAITING': return 'mdi-clock-outline';
        case 'CHARGING': return 'mdi-flash';
        default: return 'mdi-information';
    }
};

const getStatusText = () => {
    if (!activeRequest.value) return '';
    switch (activeRequest.value.status) {
        case 'WAITING': return '排队等待中';
        case 'CHARGING': return '正在充电';
        default: return '未知状态';
    }
};

const getStatusDescription = () => {
    if (!activeRequest.value) return '';
    switch (activeRequest.value.status) {
        case 'WAITING': return '您的充电请求已提交，正在等待充电桩分配';
        case 'CHARGING': return '充电桩已分配，正在为您的车辆充电';
        default: return '';
    }
};

const handleSubmit = async () => {
  loading.value = true;
  error.value = null;
  try {
    await createRequest(form.type, form.amount);
  } catch (e) {
    error.value = e.data?.detail || 'Failed to submit request.';
  } finally {
    loading.value = false;
    await fetchActiveRequest(); // Fetch immediately after submission
  }
};

const handleCancel = async () => {
    if (confirm('Are you sure you want to cancel this request?')) {
        try {
            await cancelRequest(activeRequest.value.request_id);
        } catch (e) {
            alert(e.data?.detail || 'Failed to cancel request.');
        }
    }
};

const handleStop = async () => {
    if (confirm('Are you sure you want to stop charging? This will generate a bill.')) {
        try {
            await stopRequest(activeRequest.value.request_id);
            await fetchActiveRequest(); // Refresh state
        } catch (e) {
            alert(e.data?.detail || 'Failed to stop charging.');
        }
    }
};

const handleUpdate = async () => {
    try {
        await updateRequest(activeRequest.value.request_id, {
            requested_charge_type: editForm.type,
            requested_charge_amount: editForm.amount,
        });
        isEditing.value = false;
    } catch (e) {
        alert(e.data?.detail || 'Failed to update request.');
    }
};

const handleFaultReport = async () => {
    if (confirm('确定要上报充电桩故障吗？这将停止当前充电并设置充电桩为故障状态。')) {
        try {
            await reportFault(activeRequest.value.assigned_pile_id);
            await fetchActiveRequest(); // Refresh state
        } catch (e) {
            alert(e.data?.detail || 'Failed to report fault.');
        }
    }
};

const updateWaitingInfo = async () => {
    if (activeRequest.value && activeRequest.value.status === 'WAITING') {
        const queue = await fetchWaitingQueue();
        const userQueue = activeRequest.value.requested_charge_type === 'FAST'
            ? queue.filter(r => r.requested_charge_type === 'FAST')
            : queue.filter(r => r.requested_charge_type === 'TRICKLE');
        
        const userIndex = userQueue.findIndex(r => r.request_id === activeRequest.value.request_id);
        if (userIndex !== -1) {
            waitingInfo.value.carsAhead = userIndex;
        }
    }
};

onMounted(async () => {
  await fetchPiles();
  await fetchActiveRequest();
  await updateWaitingInfo();
  
  pollingInterval = setInterval(async () => {
    await fetchActiveRequest();
    await updateWaitingInfo();
    // If charging, we need pile data to be fresh for power rate
    if (activeRequest.value?.status === 'CHARGING') {
        await fetchPiles();
    }
  }, 5000); // Poll every 5 seconds

  if (activeRequest.value) {
      editForm.type = activeRequest.value.requested_charge_type;
      editForm.amount = activeRequest.value.requested_charge_amount;
  }
});

onUnmounted(() => {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
});
</script>

<style scoped>
.charging-dashboard {
  max-width: 1000px;
  margin: 0 auto;
}

.dashboard-card {
  border-radius: 20px;
  border: 1px solid rgba(0, 217, 255, 0.2);
  background: rgba(26, 26, 46, 0.8);
}

.dashboard-title {
  padding: 1.5rem 2rem 1rem;
  border-bottom: 1px solid rgba(0, 217, 255, 0.1);
}

.status-alert {
  border-radius: 16px;
  border-left: 4px solid currentColor;
}

.status-content h3 {
  font-weight: 600;
}

.detail-card {
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.detail-card:hover {
  transform: translateY(-2px);
  border-color: rgba(0, 217, 255, 0.3);
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.info-row .label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
}

.info-row .value {
  font-size: 1rem;
  text-align: right;
}

.progress-card {
  border-radius: 16px;
  border: 1px solid rgba(76, 175, 80, 0.3);
  background: rgba(76, 175, 80, 0.05);
}

.progress-container {
  position: relative;
}

.charging-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-buttons {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 2rem;
}

.edit-form {
  border-radius: 16px;
  overflow: hidden;
}

.new-request-section {
  text-align: center;
}

.request-form {
  max-width: 600px;
  margin: 0 auto;
}

/* 动画增强 */
.v-progress-linear {
  overflow: hidden;
}

.v-progress-linear::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-title {
    padding: 1rem;
  }
  
  .detail-card {
    margin-bottom: 1rem;
  }
  
  .progress-card {
    padding: 1rem !important;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .action-buttons .v-btn {
    width: 100%;
    max-width: 300px;
  }
  
  .info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .info-row .value {
    text-align: left;
  }
}

/* 特殊效果 */
.charging-progress {
  position: relative;
}

.charging-progress::before {
  content: '';
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  background: linear-gradient(45deg, #4CAF50, #00D9FF);
  border-radius: 20px;
  z-index: -1;
  opacity: 0.1;
  animation: progressGlow 3s ease-in-out infinite alternate;
}

@keyframes progressGlow {
  0% {
    opacity: 0.1;
  }
  100% {
    opacity: 0.3;
  }
}

.v-chip {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 充电类型选择框特殊样式 */
.charging-dashboard .v-select {
  border-radius: 12px;
}

.charging-dashboard .v-select .v-field {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(0, 217, 255, 0.3) !important;
  transition: all 0.3s ease !important;
}

.charging-dashboard .v-select .v-field:hover {
  background: rgba(255, 255, 255, 0.12) !important;
  border-color: rgba(0, 217, 255, 0.5) !important;
  transform: translateY(-1px) !important;
}

.charging-dashboard .v-select .v-field--focused {
  background: rgba(255, 255, 255, 0.12) !important;
  border-color: var(--text-accent-blue) !important;
  box-shadow: 0 0 12px rgba(0, 217, 255, 0.2) !important;
}

.v-alert .v-icon {
  margin-right: 1rem;
}

/* 等待状态加载器样式 */
.waiting-loader {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  position: relative;
}

.waiting-progress {
  filter: drop-shadow(0 0 4px rgba(0, 217, 255, 0.3)) !important;
  animation: waitingRotate 2s linear infinite !important;
}

@keyframes waitingRotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.waiting-progress :deep(.v-progress-circular__overlay) {
  stroke: rgba(0, 217, 255, 0.8) !important;
  stroke-width: 3px !important;
  stroke-linecap: round !important;
}

.waiting-progress :deep(.v-progress-circular__underlay) {
  stroke: rgba(0, 217, 255, 0.2) !important;
  stroke-width: 3px !important;
}

.waiting-progress :deep(svg) {
  display: block !important;
  width: 40px !important;
  height: 40px !important;
}

.waiting-progress :deep(circle) {
  stroke-dasharray: 75, 200 !important;
  stroke-dashoffset: -5 !important;
}

/* 状态动画区域 */
.status-animation {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  min-height: 48px;
}

/* 备用CSS动画圆圈 */
.custom-spinner {
  width: 40px;
  height: 40px;
  position: relative;
}

.spinner-ring {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 217, 255, 0.2);
  border-top: 3px solid rgba(0, 217, 255, 0.8);
  border-radius: 50%;
  animation: spinnerRotate 1s linear infinite;
  filter: drop-shadow(0 0 4px rgba(0, 217, 255, 0.3));
}

@keyframes spinnerRotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style> 