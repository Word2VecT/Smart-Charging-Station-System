<template>
  <div class="admin-piles">
    <v-container fluid class="pa-6">
      <!-- 页面标题 -->
      <v-row class="mb-6">
        <v-col>
          <div class="d-flex align-center justify-space-between">
            <div>
              <h1 class="text-h3 font-weight-bold mb-2">
                <v-icon class="mr-3" size="40" color="primary">mdi-ev-station</v-icon>
                充电桩管理
              </h1>
              <p class="text-h6 text-grey-darken-1">管理和监控所有充电桩</p>
            </div>
            <div class="d-flex gap-3">
              <v-btn
                color="primary"
                variant="elevated"
                @click="refreshData"
                :loading="loading"
              >
                <v-icon left>mdi-refresh</v-icon>
                刷新数据
              </v-btn>
              <v-btn
                color="secondary"
                variant="outlined"
                @click="showBatchOperations = !showBatchOperations"
              >
                <v-icon left>mdi-cog</v-icon>
                批量操作
              </v-btn>
              <v-btn
                color="info"
                variant="outlined"
                @click="openSetupDialog"
                :disabled="!allPilesAvailable"
              >
                <v-icon left>mdi-wrench</v-icon>
                设置桩数量
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>

      <!-- 批量操作面板 -->
      <v-expand-transition>
        <v-card v-show="showBatchOperations" class="mb-6" color="surface-variant">
          <v-card-title>
            <v-icon class="mr-2">mdi-format-list-bulleted</v-icon>
            批量操作
          </v-card-title>
          <v-card-text>
            <v-row align="center">
              <v-col cols="auto">
                <v-btn-toggle v-model="batchAction" mandatory>
                  <v-btn value="start" color="success">
                    <v-icon left>mdi-play</v-icon>
                    启动
                  </v-btn>
                  <v-btn value="stop" color="error">
                    <v-icon left>mdi-stop</v-icon>
                    关闭
                  </v-btn>
                </v-btn-toggle>
              </v-col>
              <v-col cols="auto">
                <v-btn
                  :color="batchAction === 'start' ? 'success' : 'error'"
                  variant="elevated"
                  @click="executeBatchOperation"
                  :disabled="selectedPiles.length === 0"
                  :loading="batchLoading"
                >
                  执行批量{{ batchAction === 'start' ? '启动' : '关闭' }}
                  ({{ selectedPiles.length }})
                </v-btn>
              </v-col>
              <v-col>
                <v-chip-group v-if="selectedPiles.length > 0">
                  <v-chip 
                    v-for="pileId in selectedPiles" 
                    :key="pileId"
                    closable
                    @click:close="removePileFromSelection(pileId)"
                  >
                    {{ getPileCode(pileId) }}
                  </v-chip>
                </v-chip-group>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-expand-transition>

      <!-- 统计概览 -->
      <v-row class="mb-6">
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="100">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-success">{{ totalPiles }}</div>
                <div class="text-body-2 text-grey-darken-1">总充电桩</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="100">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-primary">{{ availablePiles }}</div>
                <div class="text-body-2 text-grey-darken-1">可用</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="100">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-warning">{{ chargingPiles }}</div>
                <div class="text-body-2 text-grey-darken-1">充电中</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="100">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-error">{{ offlinePiles }}</div>
                <div class="text-body-2 text-grey-darken-1">离线/故障</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 充电桩列表 -->
      <v-card>
        <v-card-title class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-view-list</v-icon>
            充电桩列表
          </div>
          <div class="d-flex align-center gap-3">
            <!-- 状态过滤器 -->
            <v-select
              v-model="statusFilter"
              :items="statusFilterOptions"
              label="状态过滤"
              density="compact"
              style="width: 150px;"
              clearable
            ></v-select>
            <!-- 类型过滤器 -->
            <v-select
              v-model="typeFilter"
              :items="typeFilterOptions"
              label="类型过滤"
              density="compact"
              style="width: 150px;"
              clearable
            ></v-select>
          </div>
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col 
              v-for="pile in filteredPiles" 
              :key="pile.pile_id"
              cols="12" 
              sm="6" 
              md="4" 
              lg="3"
            >
              <v-card 
                class="pile-card" 
                :class="{ 'pile-selected': selectedPiles.includes(pile.pile_id) }"
                @click="togglePileSelection(pile.pile_id)"
              >
                <v-card-text class="d-flex flex-column pa-4">
                  <!-- 选择框和菜单 -->
                  <div class="d-flex align-center justify-space-between mb-2">
                    <v-checkbox 
                      :model-value="selectedPiles.includes(pile.pile_id)"
                      hide-details
                      density="compact"
                      @click.stop="togglePileSelection(pile.pile_id)"
                    ></v-checkbox>
                    <v-menu offset-y>
                      <template v-slot:activator="{ props }">
                        <v-btn
                          icon="mdi-dots-vertical"
                          size="small"
                          variant="text"
                          v-bind="props"
                          @click.stop
                        ></v-btn>
                      </template>
                      <v-list density="compact">
                        <v-list-item @click="viewPileDetails(pile)">
                          <v-list-item-title>查看详情</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="viewPileLogs(pile)">
                          <v-list-item-title>查看日志</v-list-item-title>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item @click="toggleSinglePileStatus(pile)">
                          <v-list-item-title>
                            {{ pile.status === 'OFF' ? '启动充电桩' : '关闭充电桩' }}
                          </v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </div>

                  <!-- 充电桩信息 -->
                  <div class="text-center">
                    <v-avatar 
                      :color="getPileStatusColor(pile.status)" 
                      size="60" 
                      class="mb-2"
                    >
                      <v-icon size="30" color="white">
                        {{ getPileStatusIcon(pile.status) }}
                      </v-icon>
                    </v-avatar>
                    <h3 class="text-h6 font-weight-bold">{{ pile.pile_code }}</h3>
                    <p class="text-body-2 text-grey-darken-1 mb-2">
                      {{ pile.type === 'FAST' ? '快充桩' : '慢充桩' }}
                    </p>
                    <v-chip 
                      :color="getPileStatusColor(pile.status)" 
                      size="small"
                      class="mb-3"
                    >
                      {{ getPileStatusText(pile.status) }}
                    </v-chip>
                  </div>
                  
                  <!-- 详细信息 -->
                  <div class="info-grid mb-3">
                    <div class="info-item">
                      <div class="info-label">功率</div>
                      <div class="info-value">{{ pile.power_rate }} kW</div>
                    </div>
                    <div class="info-item">
                      <div class="info-label">充电次数</div>
                      <div class="info-value">{{ pile.statistics?.total_charges || 0 }}</div>
                    </div>
                    <div class="info-item">
                      <div class="info-label">累计时长</div>
                      <div class="info-value">{{ formatDuration(pile.statistics?.total_charging_duration_seconds || 0) }}</div>
                    </div>
                    <div class="info-item">
                      <div class="info-label">累计电量</div>
                      <div class="info-value">{{ (pile.statistics?.total_energy_consumed_kwh || 0).toFixed(1) }} kWh</div>
                    </div>
                  </div>

                  <!-- 伸缩空间 -->
                  <v-spacer></v-spacer>

                  <!-- 操作按钮 -->
                  <v-btn
                    :color="pile.status === 'OFF' ? 'success' : 'error'"
                    size="small"
                    variant="elevated"
                    block
                    @click.stop="toggleSinglePileStatus(pile)"
                    :loading="pile.updating"
                  >
                    <v-icon left>
                      {{ pile.status === 'OFF' ? 'mdi-play' : 'mdi-stop' }}
                    </v-icon>
                    {{ pile.status === 'OFF' ? '启动' : '关闭' }}
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-container>

    <!-- 充电桩详情对话框 -->
    <v-dialog v-model="detailsDialog" max-width="600">
      <v-card v-if="selectedPileDetails">
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2" color="primary">mdi-information</v-icon>
          充电桩详情 - {{ selectedPileDetails.pile_code }}
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" sm="6">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>充电桩ID</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedPileDetails.pile_id }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>编号</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedPileDetails.pile_code }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>类型</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedPileDetails.type === 'FAST' ? '快充桩' : '慢充桩' }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>状态</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip :color="getPileStatusColor(selectedPileDetails.status)" size="small">
                      {{ getPileStatusText(selectedPileDetails.status) }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>功率</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedPileDetails.power_rate }} kW</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
            <v-col cols="12" sm="6">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>总充电次数</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedPileDetails.statistics?.total_charges || 0 }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>累计充电时长</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDuration(selectedPileDetails.statistics?.total_charging_duration_seconds || 0) }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>累计充电电量</v-list-item-title>
                  <v-list-item-subtitle>{{ (selectedPileDetails.statistics?.total_energy_consumed_kwh || 0).toFixed(2) }} kWh</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="detailsDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 充电桩数量设置弹窗 -->
    <v-dialog v-model="setupDialog" max-width="600px" persistent>
      <v-card>
        <v-card-title>
          <span class="text-h5">设置充电桩数量</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-alert
              type="warning"
              variant="tonal"
              class="mb-4"
              title="重要提示"
              text="此操作将清空所有现有的充电桩及其相关数据（如订单和日志），并根据您输入的数量重新创建。仅当所有充电桩都处于'可用'状态时才能执行此操作。"
            ></v-alert>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="fastPileCount"
                  label="快充桩数量"
                  type="number"
                  min="0"
                  variant="outlined"
                  density="compact"
                  prepend-inner-icon="mdi-flash"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="tricklePileCount"
                  label="慢充桩数量"
                  type="number"
                  min="0"
                  variant="outlined"
                  density="compact"
                  prepend-inner-icon="mdi-timer-outline"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue-darken-1" variant="text" @click="setupDialog = false">
            取消
          </v-btn>
          <v-btn
            color="blue-darken-1"
            variant="elevated"
            @click="setupPiles"
            :loading="isSettingUp"
          >
            确认
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
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

interface PileWithStatistics {
  pile_id: number
  pile_code: string
  type: string
  status: string
  power_rate: number
  statistics?: PileStatistics
  updating?: boolean
}

const { api } = useAdminAuth()

const loading = ref(false)
const batchLoading = ref(false)
const piles = ref<PileWithStatistics[]>([])
const selectedPiles = ref<number[]>([])
const showBatchOperations = ref(false)
const batchAction = ref<'start' | 'stop'>('start')
const statusFilter = ref<string | null>(null)
const typeFilter = ref<string | null>(null)
const detailsDialog = ref(false)
const selectedPileDetails = ref<PileWithStatistics | null>(null)

// 过滤选项
const statusFilterOptions = [
  { title: '全部状态', value: null },
  { title: '可用', value: 'AVAILABLE' },
  { title: '充电中', value: 'CHARGING' },
  { title: '故障', value: 'FAULTY' },
  { title: '关闭', value: 'OFF' }
]

const typeFilterOptions = [
  { title: '全部类型', value: null },
  { title: '快充桩', value: 'FAST' },
  { title: '慢充桩', value: 'TRICKLE' }
]

// 计算属性
const totalPiles = computed(() => piles.value.length)
const availablePiles = computed(() => piles.value.filter(p => p.status === 'AVAILABLE').length)
const chargingPiles = computed(() => piles.value.filter(p => p.status === 'CHARGING').length)
const offlinePiles = computed(() => piles.value.filter(p => p.status === 'OFF' || p.status === 'FAULTY').length)

const filteredPiles = computed(() => {
  let result = piles.value
  
  if (statusFilter.value) {
    result = result.filter(p => p.status === statusFilter.value)
  }
  
  if (typeFilter.value) {
    result = result.filter(p => p.type === typeFilter.value)
  }
  
  return result
})

// 获取充电桩数据
const fetchPilesData = async () => {
  try {
    loading.value = true
    const data = await api('/admin/dashboard')
    piles.value = data.piles
  } catch (error) {
    console.error('Failed to fetch piles data:', error)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  await fetchPilesData()
}

// 选择/取消选择充电桩
const togglePileSelection = (pileId: number) => {
  const index = selectedPiles.value.indexOf(pileId)
  if (index > -1) {
    selectedPiles.value.splice(index, 1)
  } else {
    selectedPiles.value.push(pileId)
  }
}

// 从选择中移除充电桩
const removePileFromSelection = (pileId: number) => {
  const index = selectedPiles.value.indexOf(pileId)
  if (index > -1) {
    selectedPiles.value.splice(index, 1)
  }
}

// 获取充电桩编号
const getPileCode = (pileId: number) => {
  const pile = piles.value.find(p => p.pile_id === pileId)
  return pile?.pile_code || `ID:${pileId}`
}

// 切换单个充电桩状态
const toggleSinglePileStatus = async (pile: PileWithStatistics) => {
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
    
    pile.status = response.status
    
  } catch (error) {
    console.error('Failed to toggle pile status:', error)
    alert('状态切换失败，请重试')
  } finally {
    pile.updating = false
  }
}

// 执行批量操作
const executeBatchOperation = async () => {
  if (selectedPiles.value.length === 0) return
  
  try {
    batchLoading.value = true
    const newStatus = batchAction.value === 'start' ? 'AVAILABLE' : 'OFF'
    
    const promises = selectedPiles.value.map(pileId => 
      api(`/admin/piles/${pileId}/status`, {
        method: 'PATCH',
        body: {
          status: newStatus,
          details: `批量${batchAction.value === 'start' ? '启动' : '关闭'}`
        }
      })
    )
    
    await Promise.all(promises)
    
    // 更新本地状态
    selectedPiles.value.forEach(pileId => {
      const pile = piles.value.find(p => p.pile_id === pileId)
      if (pile) {
        pile.status = newStatus
      }
    })
    
    selectedPiles.value = []
    showBatchOperations.value = false
    
  } catch (error) {
    console.error('Failed to execute batch operation:', error)
    alert('批量操作失败，请重试')
  } finally {
    batchLoading.value = false
  }
}

// 查看充电桩详情
const viewPileDetails = (pile: PileWithStatistics) => {
  selectedPileDetails.value = pile
  detailsDialog.value = true
}

// 查看充电桩日志
const viewPileLogs = (pile: PileWithStatistics) => {
  // 跳转到日志页面或显示日志对话框
  console.log('View logs for pile:', pile.pile_code)
}

// 获取状态相关函数
const getPileStatusColor = (status: string) => {
  switch (status) {
    case 'AVAILABLE': return 'success'
    case 'CHARGING': return 'primary'
    case 'FAULTY': return 'error'
    case 'OFF': return 'grey'
    default: return 'grey'
  }
}

const getPileStatusIcon = (status: string) => {
  switch (status) {
    case 'AVAILABLE': return 'mdi-check-circle'
    case 'CHARGING': return 'mdi-flash'
    case 'FAULTY': return 'mdi-alert-circle'
    case 'OFF': return 'mdi-power'
    default: return 'mdi-help-circle'
  }
}

const getPileStatusText = (status: string) => {
  switch (status) {
    case 'AVAILABLE': return '空闲'
    case 'CHARGING': return '充电中'
    case 'FAULTY': return '故障'
    case 'OFF': return '关闭'
    default: return '未知'
  }
}

// 格式化时长
const formatDuration = (seconds: number) => {
  if (seconds < 60) return `${seconds}秒`
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

// ===============================
// 充电桩数量设置
// ===============================
const setupDialog = ref(false)
const fastPileCount = ref(0)
const tricklePileCount = ref(0)
const isSettingUp = ref(false)

const allPilesAvailable = computed(() => {
  if (totalPiles.value === 0) return true
  return availablePiles.value === totalPiles.value
})

const openSetupDialog = () => {
  fastPileCount.value = piles.value.filter(p => p.type === 'FAST').length
  tricklePileCount.value = piles.value.filter(p => p.type === 'TRICKLE').length
  setupDialog.value = true
}

const setupPiles = async () => {
  isSettingUp.value = true
  try {
    await api('/admin/piles/setup', {
      method: 'POST',
      body: {
        fast_piles: fastPileCount.value,
        trickle_piles: tricklePileCount.value,
      },
    })
    setupDialog.value = false
    await refreshData()
  } catch (error: any) {
    console.error('Failed to setup piles:', error)
    alert(`设置失败: ${error.data?.detail || error.message}`)
  } finally {
    isSettingUp.value = false
  }
}

onMounted(async () => {
  await fetchPilesData()
})
</script>

<style scoped>
.stat-card {
  border-radius: 12px;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.pile-card {
  border-radius: 16px;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.pile-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.pile-selected {
  border-color: #1976d2 !important;
  background: rgba(25, 118, 210, 0.05);
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.info-item {
  padding: 4px;
  background: rgba(128, 128, 128, 0.08);
  border-radius: 8px;
  text-align: center;
}

.info-label {
  font-size: 0.7rem;
  color: #888;
  margin-bottom: 2px;
}

.info-value {
  font-size: 0.8rem;
  font-weight: 600;
}
</style>
