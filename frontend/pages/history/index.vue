<template>
  <div class="history-page">
    <!-- 背景装饰 -->
    <div class="history-background">
      <div class="data-grid"></div>
      <div class="floating-icons">
        <div
          v-for="i in 12"
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

    <v-container class="history-container">
      <!-- 页面标题 -->
      <div class="page-header mb-8">
        <div class="d-flex align-center justify-space-between flex-wrap">
          <div class="header-content">
            <div class="d-flex align-center mb-2">
              <v-icon size="48" color="success" class="mr-4 pulse">
                mdi-history
              </v-icon>
              <h1 class="text-h2 futuristic-font text-glow text-accent-blue ma-0">
                充电历史
              </h1>
            </div>
            <p class="text-h6 text-secondary-custom mb-0">
              查看您的充电记录和账单信息
            </p>
          </div>
          <div class="header-actions d-flex align-center">
            <v-btn
              @click="router.push('/')"
              variant="outlined"
              color="primary"
              class="btn-futuristic mr-3"
              prepend-icon="mdi-home"
            >
              返回首页
            </v-btn>
            <v-btn
              @click="loadHistory"
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

      <!-- 数据统计卡片 -->
      <div class="stats-section mb-8">
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <div class="stat-card glass-morph card-hover pa-4 text-center">
              <v-icon size="40" color="primary" class="mb-3">mdi-counter</v-icon>
              <h3 class="text-h5 text-primary-custom mb-2">{{ historyItems.length }}</h3>
              <p class="text-body-2 text-muted-custom">总记录数</p>
            </div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="stat-card glass-morph card-hover pa-4 text-center">
              <v-icon size="40" color="success" class="mb-3">mdi-check-circle</v-icon>
              <h3 class="text-h5 text-success-custom mb-2">{{ completedCount }}</h3>
              <p class="text-body-2 text-muted-custom">已完成</p>
            </div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="stat-card glass-morph card-hover pa-4 text-center">
              <v-icon size="40" color="warning" class="mb-3">mdi-currency-cny</v-icon>
              <h3 class="text-h5 text-warning-custom mb-2">¥{{ totalFee.toFixed(2) }}</h3>
              <p class="text-body-2 text-muted-custom">总费用</p>
            </div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="stat-card glass-morph card-hover pa-4 text-center">
              <v-icon size="40" color="info" class="mb-3">mdi-lightning-bolt</v-icon>
              <h3 class="text-h5 text-accent-blue mb-2">{{ totalEnergy.toFixed(1) }}</h3>
              <p class="text-body-2 text-muted-custom">总充电量(kWh)</p>
            </div>
          </v-col>
        </v-row>
      </div>

      <!-- 数据表格 -->
      <div class="table-section">
        <v-card class="data-table-card glass-morph card-hover" elevation="0">
          <v-card-title class="data-table-header pa-6">
            <div class="d-flex align-center">
              <v-icon size="32" color="info" class="mr-3">
                mdi-table
              </v-icon>
              <span class="futuristic-font text-glow text-primary-custom">
                充电记录详情
              </span>
            </div>
          </v-card-title>
          
          <v-card-text class="pa-0">
            <v-data-table
              :headers="headers"
              :items="historyItems"
              :loading="loading"
              class="futuristic-table"
              @click:row="viewDetails"
              item-value="item_id"
              hover
              :items-per-page="10"
              :loading-text="'正在加载数据...'"
              :no-data-text="'暂无充电记录'"
            >
              <!-- 自定义表头 -->
              <template v-slot:headers="{ columns }">
                <tr class="table-header-row">
                  <th 
                    v-for="column in columns" 
                    :key="column.key"
                    class="table-header-cell"
                  >
                    <div class="d-flex align-center">
                      <v-icon 
                        :icon="getHeaderIcon(column.key)" 
                        size="16" 
                        class="mr-2"
                        :color="getHeaderColor(column.key)"
                      ></v-icon>
                      <span class="text-primary-custom font-weight-bold">
                        {{ column.title }}
                      </span>
                    </div>
                  </th>
                </tr>
              </template>

              <!-- 类型列 -->
              <template v-slot:item.item_type="{ item }">
                <v-chip 
                  :color="item.item_type === 'ORDER' ? 'success' : 'primary'"
                  variant="outlined"
                  size="small"
                  class="font-weight-bold"
                >
                  <v-icon 
                    :icon="item.item_type === 'ORDER' ? 'mdi-receipt' : 'mdi-flash'"
                    size="12"
                    class="mr-1"
                  ></v-icon>
                  {{ item.item_type === 'ORDER' ? '订单' : '请求' }}
                </v-chip>
              </template>

              <!-- 状态列 -->
              <template v-slot:item.status="{ item }">
                <v-chip 
                  :color="getStatusColor(item.status)" 
                  variant="elevated"
                  size="small"
                  class="font-weight-bold status-chip"
                >
                  <v-icon 
                    :icon="getStatusIcon(item.status)"
                    size="12"
                    class="mr-1"
                  ></v-icon>
                  {{ getStatusText(item.status) }}
                </v-chip>
              </template>

              <!-- 日期列 -->
              <template v-slot:item.date="{ item }">
                <div class="date-cell">
                  <div class="text-primary-custom font-weight-medium">
                    {{ formatDate(item.date) }}
                  </div>
                  <div class="text-caption text-muted-custom">
                    {{ formatTime(item.date) }}
                  </div>
                </div>
              </template>

              <!-- 充电类型列 -->
              <template v-slot:item.charge_type="{ item }">
                <v-chip 
                  :color="item.charge_type === 'FAST' ? 'warning' : 'info'"
                  variant="outlined"
                  size="small"
                >
                  <v-icon 
                    :icon="item.charge_type === 'FAST' ? 'mdi-flash' : 'mdi-battery'"
                    size="12"
                    class="mr-1"
                  ></v-icon>
                  {{ item.charge_type === 'FAST' ? '快充' : '慢充' }}
                </v-chip>
              </template>

              <!-- 充电量列 -->
              <template v-slot:item.actual_charge_amount="{ item }">
                <div class="energy-cell text-center">
                  <div class="text-success-custom font-weight-bold">
                    {{ item.actual_charge_amount || 0 }}
                  </div>
                  <div class="text-caption text-muted-custom">
                    kWh
                  </div>
                </div>
              </template>

              <!-- 费用列 -->
              <template v-slot:item.total_fee="{ item }">
                <div class="fee-cell text-center">
                  <div class="text-warning-custom font-weight-bold">
                    ¥{{ item.total_fee || '0.00' }}
                  </div>
                </div>
              </template>

              <!-- 操作列 -->
              <template v-slot:item.actions="{ item }">
                <v-btn
                  size="small"
                  variant="outlined"
                  color="primary"
                  class="btn-futuristic"
                  @click.stop="viewDetails(null, { item })"
                >
                  <v-icon size="16">mdi-eye</v-icon>
                  查看
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </div>
    </v-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useHistory } from '~/composables/useHistory';

const { historyItems, fetchHistory } = useHistory();
const router = useRouter();
const loading = ref(false);

const headers = [
  { title: '类型', key: 'item_type', sortable: true },
  { title: '状态', key: 'status', sortable: true },
  { title: '日期时间', key: 'date', sortable: true },
  { title: '充电模式', key: 'charge_type', sortable: true },
  { title: '充电量', key: 'actual_charge_amount', sortable: false },
  { title: '费用', key: 'total_fee', sortable: true },
  { title: '操作', key: 'actions', sortable: false },
];

// 计算统计数据
const completedCount = computed(() => {
  return historyItems.value.filter(item => item.status === 'COMPLETED').length;
});

const totalFee = computed(() => {
  return historyItems.value.reduce((sum, item) => sum + (parseFloat(item.total_fee) || 0), 0);
});

const totalEnergy = computed(() => {
  return historyItems.value.reduce((sum, item) => sum + (parseFloat(item.actual_charge_amount) || 0), 0);
});

const getStatusColor = (status) => {
  const colors = {
    'COMPLETED': 'success',
    'CHARGING': 'primary',
    'WAITING': 'warning',
    'CANCELLED': 'error'
  };
  return colors[status] || 'grey';
};

const getStatusIcon = (status) => {
  const icons = {
    'COMPLETED': 'mdi-check-circle',
    'CHARGING': 'mdi-flash',
    'WAITING': 'mdi-clock',
    'CANCELLED': 'mdi-close-circle'
  };
  return icons[status] || 'mdi-help-circle';
};

const getStatusText = (status) => {
  const texts = {
    'COMPLETED': '已完成',
    'CHARGING': '充电中',
    'WAITING': '等待中',
    'CANCELLED': '已取消'
  };
  return texts[status] || status;
};

const getHeaderIcon = (key) => {
  const icons = {
    'item_type': 'mdi-shape',
    'status': 'mdi-information',
    'date': 'mdi-calendar',
    'charge_type': 'mdi-flash',
    'actual_charge_amount': 'mdi-battery',
    'total_fee': 'mdi-currency-cny',
    'actions': 'mdi-cog'
  };
  return icons[key] || 'mdi-circle';
};

const getHeaderColor = (key) => {
  const colors = {
    'item_type': 'primary',
    'status': 'info',
    'date': 'secondary',
    'charge_type': 'warning',
    'actual_charge_amount': 'success',
    'total_fee': 'warning',
    'actions': 'grey'
  };
  return colors[key] || 'primary';
};

const getRandomIcon = () => {
  const icons = ['mdi-flash', 'mdi-battery', 'mdi-car-electric', 'mdi-ev-station'];
  return icons[Math.floor(Math.random() * icons.length)];
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN');
};

const formatTime = (dateString) => {
  return new Date(dateString).toLocaleTimeString('zh-CN');
};

const loadHistory = async () => {
  loading.value = true;
  try {
    await fetchHistory();
  } finally {
    loading.value = false;
  }
};

const viewDetails = (event, { item }) => {
  if (item.item_type === 'ORDER') {
    router.push(`/history/${item.item_id}`);
  } else {
    // For requests (WAITING, CHARGING), navigate to the homepage to see live status
    router.push('/');
  }
};

onMounted(() => {
  loadHistory();
});

definePageMeta({
  layout: 'default'
});
</script>

<style scoped>
.history-page {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(135deg, #0F0F23 0%, #1A1A2E 100%) !important;
}

.history-background {
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

.history-container {
  position: relative;
  z-index: 2;
  padding-top: 2rem;
}

.page-header {
  position: relative;
}

.header-content {
  position: relative;
}

.header-actions {
  gap: 1rem;
}

.stats-section .stat-card {
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
}

.stats-section .stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(76, 175, 80, 0.3);
  box-shadow: 0 6px 15px rgba(76, 175, 80, 0.1);
}

.data-table-card {
  border-radius: 20px;
  border: 1px solid rgba(76, 175, 80, 0.2);
  background: rgba(26, 26, 46, 0.8);
  overflow: hidden;
}

.data-table-header {
  border-bottom: 1px solid rgba(76, 175, 80, 0.2);
  background: rgba(76, 175, 80, 0.05);
}

.futuristic-table :deep(.v-table) {
  background: transparent;
  color: var(--text-primary);
}

.futuristic-table :deep(.v-data-table__tr:hover) {
  background: rgba(76, 175, 80, 0.1) !important;
  cursor: pointer;
}

.table-header-row {
  background: rgba(76, 175, 80, 0.1);
}

.table-header-cell {
  padding: 1rem !important;
  border-bottom: 2px solid rgba(76, 175, 80, 0.3) !important;
}

.futuristic-table :deep(.v-data-table__td) {
  padding: 1rem !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.date-cell,
.energy-cell,
.fee-cell {
  text-align: center;
}

.status-chip {
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.futuristic-table :deep(.v-data-table-footer) {
  background: rgba(26, 26, 46, 0.9);
  border-top: 1px solid rgba(76, 175, 80, 0.2);
}

.futuristic-table :deep(.v-data-table-footer .v-btn) {
  color: var(--text-primary) !important;
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
  
  .futuristic-table :deep(.v-data-table__td),
  .table-header-cell {
    padding: 0.5rem !important;
    font-size: 0.875rem;
  }
}

/* 加载状态 */
.futuristic-table :deep(.v-data-table-progress) {
  background: rgba(76, 175, 80, 0.1);
}

.futuristic-table :deep(.v-progress-linear) {
  background: rgba(76, 175, 80, 0.3) !important;
}
</style> 