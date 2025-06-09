<template>
  <div class="admin-requests">
    <v-container fluid class="pa-6">
      <!-- 页面标题 -->
      <v-row class="mb-6">
        <v-col>
          <div class="d-flex align-center justify-space-between">
            <div>
              <h1 class="text-h3 font-weight-bold mb-2">
                <v-icon class="mr-3" size="40" color="primary">mdi-format-list-bulleted</v-icon>
                请求管理
              </h1>
              <p class="text-h6 text-grey-darken-1">查看和管理所有充电请求</p>
            </div>
            <v-btn
              color="primary"
              variant="elevated"
              @click="refreshData"
              :loading="loading"
            >
              <v-icon left>mdi-refresh</v-icon>
              刷新数据
            </v-btn>
          </div>
        </v-col>
      </v-row>

      <!-- 统计卡片 -->
      <v-row class="mb-6">
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="120">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-primary">{{ totalRequests }}</div>
                <div class="text-body-2 text-grey-darken-1">总请求数</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="120">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-warning">{{ waitingRequests }}</div>
                <div class="text-body-2 text-grey-darken-1">等待中</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="120">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-success">{{ chargingRequests }}</div>
                <div class="text-body-2 text-grey-darken-1">充电中</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="120">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-info">{{ finishedRequests }}</div>
                <div class="text-body-2 text-grey-darken-1">已完成</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 请求列表 -->
      <v-card>
        <v-card-title class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-clipboard-list</v-icon>
            充电请求列表
          </div>
          <div class="d-flex align-center gap-3">
            <v-text-field
              v-model="searchQuery"
              placeholder="搜索请求..."
              density="compact"
              hide-details
              prepend-inner-icon="mdi-magnify"
              style="width: 250px;"
              clearable
            ></v-text-field>
            <v-select
              v-model="statusFilter"
              :items="statusFilterOptions"
              label="状态过滤"
              density="compact"
              style="width: 150px;"
              clearable
            ></v-select>
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
          <v-data-table
            :headers="headers"
            :items="filteredRequests"
            :loading="loading"
            item-key="request_id"
            class="elevation-1"
            :items-per-page="15"
          >
            <template v-slot:item.request_id="{ item }">
              <v-chip size="small" color="primary">
                #{{ item.request_id }}
              </v-chip>
            </template>
            <template v-slot:item.user_id="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="24" color="secondary" class="mr-2">
                  <v-icon size="12" color="white">mdi-account</v-icon>
                </v-avatar>
                <span class="font-weight-medium">{{ item.user_id }}</span>
              </div>
            </template>
            <template v-slot:item.queue_number="{ item }">
              <v-chip 
                :color="item.queue_number?.startsWith('F') ? 'orange' : 'teal'" 
                size="small"
                class="font-weight-bold"
              >
                {{ item.queue_number || '-' }}
              </v-chip>
            </template>
            <template v-slot:item.requested_charge_type="{ item }">
              <v-chip 
                :color="item.requested_charge_type === 'FAST' ? 'orange' : 'teal'" 
                size="small"
              >
                <v-icon left size="small">
                  {{ item.requested_charge_type === 'FAST' ? 'mdi-flash' : 'mdi-power-plug' }}
                </v-icon>
                {{ item.requested_charge_type === 'FAST' ? '快充' : '慢充' }}
              </v-chip>
            </template>
            <template v-slot:item.requested_charge_amount="{ item }">
              <div class="d-flex align-center">
                <v-icon size="16" color="warning" class="mr-1">mdi-battery</v-icon>
                {{ item.requested_charge_amount }} kWh
              </div>
            </template>
            <template v-slot:item.status="{ item }">
              <v-chip 
                :color="getStatusColor(item.status)" 
                size="small"
              >
                <v-icon left size="small">
                  {{ getStatusIcon(item.status) }}
                </v-icon>
                {{ getStatusText(item.status) }}
              </v-chip>
            </template>
            <template v-slot:item.assigned_pile_id="{ item }">
              <v-chip v-if="item.assigned_pile_id" size="small" color="info">
                桩 #{{ item.assigned_pile_id }}
              </v-chip>
              <span v-else class="text-grey-darken-1">等候区</span>
            </template>
            <template v-slot:item.request_time="{ item }">
              {{ formatDateTime(item.request_time) }}
            </template>
            <template v-slot:item.duration="{ item }">
              {{ getRequestDuration(item) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn-group density="compact">
                <v-btn 
                  size="small" 
                  icon="mdi-eye" 
                  @click="viewRequestDetails(item)"
                  color="info"
                ></v-btn>
                <v-btn 
                  v-if="item.status === 'WAITING' || item.status === 'CHARGING'"
                  size="small" 
                  icon="mdi-close" 
                  @click="cancelRequest(item)"
                  color="error"
                ></v-btn>
              </v-btn-group>
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>
    </v-container>

    <!-- 请求详情对话框 -->
    <v-dialog v-model="detailsDialog" max-width="600">
      <v-card v-if="selectedRequest">
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2" color="primary">mdi-information</v-icon>
          请求详情 - #{{ selectedRequest.request_id }}
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" sm="6">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>请求ID</v-list-item-title>
                  <v-list-item-subtitle>#{{ selectedRequest.request_id }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>用户ID</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedRequest.user_id }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>排队号码</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip 
                      v-if="selectedRequest.queue_number"
                      :color="selectedRequest.queue_number.startsWith('F') ? 'orange' : 'teal'" 
                      size="small"
                    >
                      {{ selectedRequest.queue_number }}
                    </v-chip>
                    <span v-else>未分配</span>
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>充电类型</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip 
                      :color="selectedRequest.requested_charge_type === 'FAST' ? 'orange' : 'teal'" 
                      size="small"
                    >
                      {{ selectedRequest.requested_charge_type === 'FAST' ? '快充' : '慢充' }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>请求电量</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedRequest.requested_charge_amount }} kWh</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
            <v-col cols="12" sm="6">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>状态</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip :color="getStatusColor(selectedRequest.status)" size="small">
                      {{ getStatusText(selectedRequest.status) }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>分配充电桩</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip v-if="selectedRequest.assigned_pile_id" size="small" color="info">
                      桩 #{{ selectedRequest.assigned_pile_id }}
                    </v-chip>
                    <span v-else>未分配</span>
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>请求时间</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDateTime(selectedRequest.request_time) }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>开始时间</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ selectedRequest.start_time ? formatDateTime(selectedRequest.start_time) : '未开始' }}
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>结束时间</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ selectedRequest.end_time ? formatDateTime(selectedRequest.end_time) : '未结束' }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn 
            v-if="selectedRequest.status === 'WAITING' || selectedRequest.status === 'CHARGING'"
            @click="cancelRequest(selectedRequest)" 
            color="error" 
            variant="outlined"
          >
            <v-icon left>mdi-close</v-icon>
            取消请求
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn @click="detailsDialog = false">关闭</v-btn>
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

interface Request {
  request_id: number
  user_id: number
  queue_number: string | null
  requested_charge_type: string
  requested_charge_amount: number
  status: string
  request_time: string
  assigned_pile_id: number | null
  start_time: string | null
  end_time: string | null
}

const { api } = useAdminAuth()

const loading = ref(false)
const requests = ref<Request[]>([])
const searchQuery = ref('')
const statusFilter = ref<string | null>(null)
const typeFilter = ref<string | null>(null)
const detailsDialog = ref(false)
const selectedRequest = ref<Request | null>(null)

// 表格headers
const headers = [
  { title: '请求ID', key: 'request_id', sortable: true },
  { title: '用户', key: 'user_id', sortable: true },
  { title: '排队号', key: 'queue_number', sortable: true },
  { title: '类型', key: 'requested_charge_type', sortable: true },
  { title: '电量', key: 'requested_charge_amount', sortable: true },
  { title: '状态', key: 'status', sortable: true },
  { title: '充电桩', key: 'assigned_pile_id', sortable: false },
  { title: '时长', key: 'duration', sortable: false },
  { title: '操作', key: 'actions', sortable: false }
]

// 过滤选项
const statusFilterOptions = [
  { title: '全部状态', value: null },
  { title: '等待中', value: 'WAITING' },
  { title: '充电中', value: 'CHARGING' },
  { title: '已完成', value: 'FINISHED' },
  { title: '已取消', value: 'CANCELLED' }
]

const typeFilterOptions = [
  { title: '全部类型', value: null },
  { title: '快充', value: 'FAST' },
  { title: '慢充', value: 'TRICKLE' }
]

// 计算属性
const totalRequests = computed(() => requests.value.length)
const waitingRequests = computed(() => requests.value.filter(r => r.status === 'WAITING').length)
const chargingRequests = computed(() => requests.value.filter(r => r.status === 'CHARGING').length)
const finishedRequests = computed(() => requests.value.filter(r => r.status === 'FINISHED').length)

const filteredRequests = computed(() => {
  let result = requests.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(req => 
      req.request_id.toString().includes(query) ||
      req.user_id.toString().includes(query) ||
      req.queue_number?.toLowerCase().includes(query)
    )
  }
  
  if (statusFilter.value) {
    result = result.filter(req => req.status === statusFilter.value)
  }
  
  if (typeFilter.value) {
    result = result.filter(req => req.requested_charge_type === typeFilter.value)
  }
  
  return result.sort((a, b) => new Date(b.request_time).getTime() - new Date(a.request_time).getTime())
})

// 获取请求数据
const fetchRequests = async () => {
  try {
    loading.value = true
    const data = await api('/admin/requests')
    requests.value = data
  } catch (error) {
    console.error('Failed to fetch requests:', error)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  await fetchRequests()
}

// 查看请求详情
const viewRequestDetails = (request: Request) => {
  selectedRequest.value = request
  detailsDialog.value = true
}

// 取消请求
const cancelRequest = (request: Request) => {
  if (confirm(`确定要取消请求 #${request.request_id} 吗？`)) {
    console.log('Cancel request:', request.request_id)
    // 实现取消请求功能
  }
}

// 工具函数
const getStatusColor = (status: string) => {
  switch (status) {
    case 'WAITING': return 'warning'
    case 'CHARGING': return 'success'
    case 'FINISHED': return 'info'
    case 'CANCELLED': return 'error'
    default: return 'grey'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'WAITING': return 'mdi-clock-outline'
    case 'CHARGING': return 'mdi-flash'
    case 'FINISHED': return 'mdi-check-circle'
    case 'CANCELLED': return 'mdi-close-circle'
    default: return 'mdi-help-circle'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'WAITING': return '等待中'
    case 'CHARGING': return '充电中'
    case 'FINISHED': return '已完成'
    case 'CANCELLED': return '已取消'
    default: return '未知'
  }
}

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

const getRequestDuration = (request: Request) => {
  if (request.status === 'CHARGING' && request.start_time) {
    const start = new Date(request.start_time)
    const now = new Date()
    const duration = Math.floor((now.getTime() - start.getTime()) / 1000)
    return formatDuration(duration)
  } else if (request.status === 'WAITING') {
    const start = new Date(request.request_time)
    const now = new Date()
    const duration = Math.floor((now.getTime() - start.getTime()) / 1000)
    return `等待 ${formatDuration(duration)}`
  } else if (request.end_time && request.start_time) {
    const start = new Date(request.start_time)
    const end = new Date(request.end_time)
    const duration = Math.floor((end.getTime() - start.getTime()) / 1000)
    return formatDuration(duration)
  }
  return '-'
}

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

onMounted(async () => {
await fetchRequests()
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

:deep(.v-data-table) {
  border-radius: 12px;
}
</style>
