<template>
  <div class="admin-dashboard">
    <v-container fluid class="pa-6">
      <!-- 页面标题 -->
      <v-row class="mb-6">
        <v-col>
          <div class="d-flex align-center justify-space-between">
            <div>
              <h1 class="text-h3 font-weight-bold mb-2">
                <v-icon class="mr-3" size="40" color="primary">mdi-view-dashboard</v-icon>
                管理员仪表盘
              </h1>
              <p class="text-h6 text-grey-darken-1">实时监控充电站运营状态</p>
            </div>
            <v-btn
              color="primary"
              variant="elevated"
              size="large"
              @click="refreshData"
              :loading="loading"
            >
              <v-icon left>mdi-refresh</v-icon>
              刷新数据
            </v-btn>
          </div>
        </v-col>
      </v-row>

      <!-- 总览统计卡片 -->
      <v-row class="mb-8">
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card" height="120">
            <v-card-text class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-h4 font-weight-bold text-success">{{ totalPiles }}</div>
                <div class="text-body-1 text-grey-darken-1">充电桩总数</div>
              </div>
              <v-icon size="48" color="success">mdi-ev-station</v-icon>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card" height="120">
            <v-card-text class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-h4 font-weight-bold text-primary">{{ activePiles }}</div>
                <div class="text-body-1 text-grey-darken-1">正常运行</div>
              </div>
              <v-icon size="48" color="primary">mdi-check-circle</v-icon>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card" height="120">
            <v-card-text class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-h4 font-weight-bold text-warning">{{ chargingVehicles }}</div>
                <div class="text-body-1 text-grey-darken-1">充电中车辆</div>
              </div>
              <v-icon size="48" color="warning">mdi-car-electric</v-icon>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card" height="120">
            <v-card-text class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-h4 font-weight-bold text-info">{{ waitingVehicles }}</div>
                <div class="text-body-1 text-grey-darken-1">排队等待</div>
              </div>
              <v-icon size="48" color="info">mdi-clock-outline</v-icon>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 充电桩状态监控 -->
      <v-row class="mb-8">
        <v-col>
          <v-card>
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-monitor-dashboard</v-icon>
              充电桩状态监控
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col 
                  v-for="pile in dashboardData?.piles || []" 
                  :key="pile.pile_id"
                  cols="12" 
                  sm="6" 
                  md="4" 
                  lg="3"
                >
                  <v-card 
                    :color="getPileStatusColor(pile.status)"
                    variant="outlined"
                    class="pile-card"
                    height="280"
                  >
                    <v-card-text>
                      <!-- 充电桩基本信息 -->
                      <div class="d-flex align-center justify-space-between mb-3">
                        <div>
                          <h3 class="text-h6 font-weight-bold">{{ pile.pile_code }}</h3>
                          <p class="text-body-2 text-grey-darken-1 mb-0">
                            {{ pile.type === 'FAST' ? '快充桩' : '慢充桩' }}
                          </p>
                        </div>
                        <v-icon :color="getPileStatusColor(pile.status)" size="36">
                          {{ getPileStatusIcon(pile.status) }}
                        </v-icon>
                      </div>

                      <!-- 状态标签 -->
                      <v-chip 
                        :color="getPileStatusColor(pile.status)" 
                        size="small" 
                        class="mb-3"
                      >
                        {{ getPileStatusText(pile.status) }}
                      </v-chip>

                      <!-- 统计数据 -->
                      <div class="statistics-grid">
                        <div class="stat-item">
                          <div class="stat-value">{{ pile.statistics.total_charges }}</div>
                          <div class="stat-label">充电次数</div>
                        </div>
                        <div class="stat-item">
                          <div class="stat-value">{{ formatDuration(pile.statistics.total_charging_duration_seconds) }}</div>
                          <div class="stat-label">累计时长</div>
                        </div>
                        <div class="stat-item">
                          <div class="stat-value">{{ pile.statistics.total_energy_consumed_kwh.toFixed(1) }}</div>
                          <div class="stat-label">累计电量(kWh)</div>
                        </div>
                        <div class="stat-item">
                          <div class="stat-value">{{ pile.power_rate }}</div>
                          <div class="stat-label">功率(kW)</div>
                        </div>
                      </div>

                      <!-- 控制按钮 -->
                      <div class="mt-3">
                        <v-btn
                          :color="pile.status === 'OFF' ? 'success' : 'error'"
                          size="small"
                          variant="elevated"
                          block
                          @click="togglePileStatus(pile)"
                          :loading="pile.updating"
                        >
                          <v-icon left>
                            {{ pile.status === 'OFF' ? 'mdi-play' : 'mdi-stop' }}
                          </v-icon>
                          {{ pile.status === 'OFF' ? '启动' : '关闭' }}
                        </v-btn>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 当前服务车辆 -->
      <v-row>
        <v-col>
          <v-card>
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-car-multiple</v-icon>
              当前服务车辆
            </v-card-title>
            <v-card-text>
              <v-data-table
                :headers="vehicleHeaders"
                :items="dashboardData?.current_vehicles || []"
                :loading="loading"
                item-key="request_id"
                class="elevation-1"
              >
                <template v-slot:item.status="{ item }">
                  <v-chip 
                    :color="getVehicleStatusColor(item.status)" 
                    size="small"
                  >
                    <v-icon left size="small">
                      {{ item.status === 'CHARGING' ? 'mdi-flash' : 'mdi-clock-outline' }}
                    </v-icon>
                    {{ item.status === 'CHARGING' ? '充电中' : '排队中' }}
                  </v-chip>
                </template>
                <template v-slot:item.requested_charge_amount="{ item }">
                  {{ item.requested_charge_amount }} kWh
                </template>
                <template v-slot:item.request_time="{ item }">
                  {{ formatDateTime(item.request_time) }}
                </template>
                <template v-slot:item.pile_code="{ item }">
                  <v-chip v-if="item.pile_code" color="primary" size="small">
                    {{ item.pile_code }}
                  </v-chip>
                  <span v-else class="text-grey-darken-1">等候区</span>
                </template>
                <template v-slot:item.duration="{ item }">
                  {{ getChargingDuration(item) }}
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

definePageMeta({
  layout: 'admin'
})

interface PileStatistics {
  pile_id: number
  total_charges: number
  total_charging_duration_seconds: number
  total_energy_consumed_kwh: number
}

interface CurrentVehicle {
  request_id: number
  user_id: number
  username: string
  queue_number: string
  requested_charge_amount: number
  status: string
  request_time: string
  assigned_pile_id: number | null
  pile_code: string | null
  start_time: string | null
}

interface PileWithStatistics {
  pile_id: number
  pile_code: string
  type: string
  status: string
  power_rate: number
  statistics: PileStatistics
  updating?: boolean
}

interface DashboardData {
  piles: PileWithStatistics[]
  current_vehicles: CurrentVehicle[]
}

const { api } = useAdminAuth()

const loading = ref(false)
const dashboardData = ref<DashboardData | null>(null)
let refreshInterval: NodeJS.Timeout | null = null

// 表格headers
const vehicleHeaders = [
  { title: '用户', key: 'username', sortable: true },
  { title: '排队号', key: 'queue_number', sortable: true },
  { title: '状态', key: 'status', sortable: true },
  { title: '请求电量', key: 'requested_charge_amount', sortable: true },
  { title: '充电桩', key: 'pile_code', sortable: false },
  { title: '请求时间', key: 'request_time', sortable: true },
  { title: '时长', key: 'duration', sortable: false }
]

// 计算属性
const totalPiles = computed(() => dashboardData.value?.piles.length || 0)

const activePiles = computed(() => 
  dashboardData.value?.piles.filter(p => p.status === 'AVAILABLE' || p.status === 'CHARGING').length || 0
)

const chargingVehicles = computed(() => 
  dashboardData.value?.current_vehicles.filter(v => v.status === 'CHARGING').length || 0
)

const waitingVehicles = computed(() => 
  dashboardData.value?.current_vehicles.filter(v => v.status === 'WAITING').length || 0
)

// 获取仪表盘数据
const fetchDashboardData = async () => {
  try {
    loading.value = true
    const data = await api('/admin/dashboard')
    dashboardData.value = data
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  await fetchDashboardData()
}

// 切换充电桩状态
const togglePileStatus = async (pile: PileWithStatistics) => {
  if (pile.updating) return
  
  try {
    pile.updating = true
    const newStatus = pile.status === 'OFF' ? 'AVAILABLE' : 'OFF'
    
    const response = await api(`/admin/piles/${pile.pile_id}/status`, {
      method: 'PATCH',
      body: {
        status: newStatus,
        details: `由管理员${newStatus === 'OFF' ? '关闭' : '启动'}`
      }
    })
    
    // 更新本地状态
    pile.status = response.status
    
  } catch (error) {
    console.error('Failed to toggle pile status:', error)
    alert('状态切换失败，请重试')
  } finally {
    pile.updating = false
  }
}

// 获取充电桩状态颜色
const getPileStatusColor = (status: string) => {
  switch (status) {
    case 'AVAILABLE': return 'success'
    case 'CHARGING': return 'primary'
    case 'FAULTY': return 'error'
    case 'OFF': return 'grey'
    default: return 'grey'
  }
}

// 获取充电桩状态图标
const getPileStatusIcon = (status: string) => {
  switch (status) {
    case 'AVAILABLE': return 'mdi-check-circle'
    case 'CHARGING': return 'mdi-flash'
    case 'FAULTY': return 'mdi-alert-circle'
    case 'OFF': return 'mdi-power'
    default: return 'mdi-help-circle'
  }
}

// 获取充电桩状态文本
const getPileStatusText = (status: string) => {
  switch (status) {
    case 'AVAILABLE': return '空闲'
    case 'CHARGING': return '充电中'
    case 'FAULTY': return '故障'
    case 'OFF': return '关闭'
    default: return '未知'
  }
}

// 获取车辆状态颜色
const getVehicleStatusColor = (status: string) => {
  switch (status) {
    case 'CHARGING': return 'success'
    case 'WAITING': return 'warning'
    default: return 'grey'
  }
}

// 格式化时长
const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取充电时长
const getChargingDuration = (vehicle: CurrentVehicle) => {
  if (vehicle.status === 'CHARGING' && vehicle.start_time) {
    const start = new Date(vehicle.start_time)
    const now = new Date()
    const duration = Math.floor((now.getTime() - start.getTime()) / 1000)
    return formatDuration(duration)
  } else if (vehicle.status === 'WAITING') {
    const start = new Date(vehicle.request_time)
    const now = new Date()
    const duration = Math.floor((now.getTime() - start.getTime()) / 1000)
    return `等待 ${formatDuration(duration)}`
  }
  return '-'
}

onMounted(async () => {
  await fetchDashboardData()
  
  // 设置自动刷新，每30秒更新一次
  refreshInterval = setInterval(fetchDashboardData, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.stat-card {
  border-radius: 12px;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.pile-card {
  border-radius: 16px;
  transition: all 0.3s ease;
}

.pile-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.statistics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 16px 0;
}

.stat-item {
  text-align: center;
  padding: 8px;
  background: rgba(0,0,0,0.03);
  border-radius: 8px;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: bold;
  color: #1976d2;
}

.stat-label {
  font-size: 0.75rem;
  color: #666;
  margin-top: 2px;
}

:deep(.v-data-table) {
  border-radius: 12px;
}
</style>
