<template>
  <div class="visualization-page">
    <v-container fluid class="pa-4">
      <!-- 页面标题 -->
      <v-row class="mb-4">
        <v-col>
          <div class="text-center">
            <h1 class="text-h3 font-weight-bold mb-2">
              <v-icon class="mr-3" size="40" color="primary">mdi-view-dashboard-variant</v-icon>
              充电站实时状态
            </h1>
            <p class="text-h6 text-grey-darken-1">实时监控充电桩状态与等待队列</p>
          </div>
        </v-col>
      </v-row>

      <!-- 充电区域 -->
      <v-card class="mb-6" elevation="4">
        <v-card-title class="text-h5 pa-4">
          <v-icon class="mr-2" color="success">mdi-ev-station</v-icon>
          充电区
        </v-card-title>
        <v-card-text class="pa-4">
          <div class="charging-stations">
            <div 
              v-for="pile in piles" 
              :key="pile.pile_id"
              class="station-container"
              :class="getStationClass(pile)"
            >
              <!-- 充电桩 -->
              <div class="charging-pile">
                <v-icon 
                  :color="getPileStatusColor(pile.status)" 
                  size="32"
                  class="pile-icon"
                >
                  {{ pile.type === 'FAST' ? 'mdi-flash' : 'mdi-battery-charging-50' }}
                </v-icon>
                <div class="pile-label">{{ pile.pile_code }}</div>
                <div class="pile-type">{{ pile.type === 'FAST' ? '快充' : '慢充' }}</div>
              </div>
              
              <!-- 车辆位置 -->
              <div class="vehicle-slot">
                <transition name="vehicle-fade" mode="out-in">
                  <div 
                    v-if="getChargingVehicle(pile.pile_id)"
                    class="vehicle charging-vehicle"
                    :class="{ 'fast-charging': pile.type === 'FAST' }"
                  >
                    <v-icon color="white" size="20">mdi-car-electric</v-icon>
                    <div class="vehicle-label">
                      {{ getChargingVehicle(pile.pile_id)?.queue_number }}
                    </div>
                  </div>
                  <div v-else class="empty-slot">
                    <div class="slot-placeholder"></div>
                  </div>
                </transition>
              </div>
            </div>
          </div>
        </v-card-text>
      </v-card>

      <!-- 等待区域 -->
      <v-card class="mb-4" elevation="4">
        <v-card-title class="text-h5 pa-4">
          <v-icon class="mr-2" color="warning">mdi-clock-outline</v-icon>
          等待区
        </v-card-title>
        <v-card-text class="pa-4">
          <v-row>
            <!-- 快充等待队列 -->
            <v-col cols="12" md="6">
              <div class="queue-section">
                <h3 class="text-h6 mb-3 text-orange">
                  <v-icon class="mr-2" color="orange">mdi-flash</v-icon>
                  快充队列
                </h3>
                <div class="queue-grid">
                  <div 
                    v-for="(vehicle, index) in fastWaitingVehicles" 
                    :key="vehicle.request_id"
                    class="waiting-vehicle fast-queue"
                    :style="{ animationDelay: `${index * 0.1}s` }"
                  >
                    <v-icon color="white" size="16">mdi-car-electric</v-icon>
                    <div class="vehicle-queue-label">{{ vehicle.queue_number }}</div>
                  </div>
                  <!-- 空位占位符 -->
                  <div 
                    v-for="i in Math.max(0, 6 - fastWaitingVehicles.length)" 
                    :key="`fast-empty-${i}`"
                    class="empty-queue-slot"
                  ></div>
                </div>
              </div>
            </v-col>

            <!-- 慢充等待队列 -->
            <v-col cols="12" md="6">
              <div class="queue-section">
                <h3 class="text-h6 mb-3 text-teal">
                  <v-icon class="mr-2" color="teal">mdi-battery-charging-50</v-icon>
                  慢充队列
                </h3>
                <div class="queue-grid">
                  <div 
                    v-for="(vehicle, index) in trickleWaitingVehicles" 
                    :key="vehicle.request_id"
                    class="waiting-vehicle trickle-queue"
                    :style="{ animationDelay: `${index * 0.1}s` }"
                  >
                    <v-icon color="white" size="16">mdi-car-electric</v-icon>
                    <div class="vehicle-queue-label">{{ vehicle.queue_number }}</div>
                  </div>
                  <!-- 空位占位符 -->
                  <div 
                    v-for="i in Math.max(0, 6 - trickleWaitingVehicles.length)" 
                    :key="`trickle-empty-${i}`"
                    class="empty-queue-slot"
                  ></div>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- 统计信息 -->
      <v-card elevation="4">
        <v-card-text class="pa-3">
          <v-row class="text-center">
            <v-col cols="6" md="3">
              <div class="stat-item">
                <v-icon color="success" size="24">mdi-ev-station</v-icon>
                <div class="stat-number">{{ availablePiles }}</div>
                <div class="stat-label">可用充电桩</div>
              </div>
            </v-col>
            <v-col cols="6" md="3">
              <div class="stat-item">
                <v-icon color="primary" size="24">mdi-flash</v-icon>
                <div class="stat-number">{{ chargingPiles }}</div>
                <div class="stat-label">充电中</div>
              </div>
            </v-col>
            <v-col cols="6" md="3">
              <div class="stat-item">
                <v-icon color="orange" size="24">mdi-clock-outline</v-icon>
                <div class="stat-number">{{ totalWaitingVehicles }}</div>
                <div class="stat-label">等待中</div>
              </div>
            </v-col>
            <v-col cols="6" md="3">
              <div class="stat-item">
                <v-icon color="info" size="24">mdi-car-multiple</v-icon>
                <div class="stat-number">{{ totalPiles }}</div>
                <div class="stat-label">总充电桩</div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 页面元数据
definePageMeta({
  layout: 'admin'
})

// 类型定义
interface PileData {
  pile_id: number
  pile_code: string
  type: 'FAST' | 'TRICKLE'
  status: string
  power_rate: number
}

interface VehicleData {
  request_id: number
  user_id: number
  username: string
  queue_number: string
  requested_charge_amount: number
  status: string
  request_time: string
  assigned_pile_id?: number
  pile_code?: string
  start_time?: string
}

// 响应式数据
const piles = ref<PileData[]>([])
const currentVehicles = ref<VehicleData[]>([])
const loading = ref(false)
let refreshInterval: NodeJS.Timeout | null = null

// 计算属性
const totalPiles = computed(() => piles.value.length)
const availablePiles = computed(() => piles.value.filter(p => p.status === 'AVAILABLE').length)
const chargingPiles = computed(() => piles.value.filter(p => p.status === 'CHARGING').length)

const fastWaitingVehicles = computed(() => 
  currentVehicles.value.filter(v => 
    v.status === 'WAITING' && v.queue_number?.startsWith('F')
  ).slice(0, 6)
)

const trickleWaitingVehicles = computed(() => 
  currentVehicles.value.filter(v => 
    v.status === 'WAITING' && v.queue_number?.startsWith('T')
  ).slice(0, 6)
)

const totalWaitingVehicles = computed(() => 
  currentVehicles.value.filter(v => v.status === 'WAITING').length
)

// 获取数据的函数
const fetchData = async () => {
  try {
    loading.value = true
    
    const response = await $fetch('http://localhost:8000/admin/dashboard')
    
    piles.value = response.piles || []
    currentVehicles.value = response.current_vehicles || []
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
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

// 获取充电桩样式类
const getStationClass = (pile: PileData) => {
  return {
    'fast-station': pile.type === 'FAST',
    'trickle-station': pile.type === 'TRICKLE',
    'station-charging': pile.status === 'CHARGING',
    'station-available': pile.status === 'AVAILABLE',
    'station-offline': pile.status === 'OFF' || pile.status === 'FAULTY'
  }
}

// 获取正在充电的车辆
const getChargingVehicle = (pileId: number) => {
  return currentVehicles.value.find(v => 
    v.assigned_pile_id === pileId && v.status === 'CHARGING'
  )
}

// 生命周期
onMounted(async () => {
  await fetchData()
  // 每5秒刷新一次数据
  refreshInterval = setInterval(fetchData, 5000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.charging-stations {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 12px;
}

.station-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.fast-station {
  background: linear-gradient(135deg, #ff6b35, #f7931e);
}

.trickle-station {
  background: linear-gradient(135deg, #00b4db, #0083b0);
}

.station-charging {
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.4);
  animation: charging-pulse 2s infinite;
}

.station-available {
  opacity: 0.8;
}

.station-offline {
  opacity: 0.5;
  filter: grayscale(50%);
}

@keyframes charging-pulse {
  0%, 100% { box-shadow: 0 0 15px rgba(0, 255, 0, 0.4); }
  50% { box-shadow: 0 0 20px rgba(0, 255, 0, 0.8); }
}

.charging-pile {
  background: white;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  margin-bottom: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 100px;
}

.pile-icon {
  display: block;
  margin: 0 auto 6px;
}

.pile-label {
  font-weight: bold;
  font-size: 1rem;
  color: #333;
}

.pile-type {
  font-size: 0.8rem;
  color: #666;
}

.vehicle-slot {
  width: 60px;
  height: 50px;
  position: relative;
}

.vehicle {
  width: 100%;
  height: 100%;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.charging-vehicle {
  background: linear-gradient(135deg, #4CAF50, #2E7D32);
  animation: vehicle-charging 3s infinite;
}

.fast-charging {
  animation: vehicle-fast-charging 1.5s infinite;
}

@keyframes vehicle-charging {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@keyframes vehicle-fast-charging {
  0%, 100% { transform: scale(1); box-shadow: 0 0 8px #ff6b35; }
  50% { transform: scale(1.1); box-shadow: 0 0 15px #ff6b35; }
}

.vehicle-label {
  font-size: 0.6rem;
  color: white;
  font-weight: bold;
  margin-top: 2px;
}

.empty-slot {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.slot-placeholder {
  width: 50px;
  height: 35px;
  border: 2px dashed #ccc;
  border-radius: 4px;
}

.vehicle-fade-enter-active, .vehicle-fade-leave-active {
  transition: all 0.5s ease;
}

.vehicle-fade-enter-from, .vehicle-fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.queue-section {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 8px;
  padding: 16px;
  height: 100%;
}

.queue-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.waiting-vehicle {
  width: 50px;
  height: 40px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  animation: waiting-bounce 2s infinite ease-in-out;
}

.fast-queue {
  background: linear-gradient(135deg, #ff6b35, #f7931e);
}

.trickle-queue {
  background: linear-gradient(135deg, #00b4db, #0083b0);
}

@keyframes waiting-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.vehicle-queue-label {
  font-size: 0.55rem;
  color: white;
  font-weight: bold;
  margin-top: 1px;
}

.empty-queue-slot {
  width: 50px;
  height: 40px;
  border: 2px dashed rgba(0, 0, 0, 0.2);
  border-radius: 6px;
}

.stat-item {
  padding: 12px;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 6px 0 3px;
}

.stat-label {
  font-size: 0.8rem;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .charging-stations {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
  }
  
  .station-container {
    padding: 10px;
  }
  
  .queue-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style> 