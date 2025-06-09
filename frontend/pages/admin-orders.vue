<template>
  <div class="admin-orders">
    <v-container fluid class="pa-6">
      <!-- 页面标题 -->
      <v-row class="mb-6">
        <v-col>
          <div class="d-flex align-center justify-space-between">
            <div>
              <h1 class="text-h3 font-weight-bold mb-2">
                <v-icon class="mr-3" size="40" color="primary">mdi-receipt</v-icon>
                订单管理
              </h1>
              <p class="text-h6 text-grey-darken-1">查看和管理所有充电订单</p>
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
                <div class="text-h4 font-weight-bold text-primary">{{ totalOrders }}</div>
                <div class="text-body-2 text-grey-darken-1">总订单数</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="120">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-success">¥{{ totalRevenue.toFixed(2) }}</div>
                <div class="text-body-2 text-grey-darken-1">总收入</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="120">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-warning">{{ todayOrders }}</div>
                <div class="text-body-2 text-grey-darken-1">今日订单</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="120">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-info">{{ totalEnergy.toFixed(1) }}</div>
                <div class="text-body-2 text-grey-darken-1">总电量(kWh)</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 订单列表 -->
      <v-card>
        <v-card-title class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-format-list-bulleted</v-icon>
            订单列表
          </div>
          <div class="d-flex align-center gap-3">
            <v-text-field
              v-model="searchQuery"
              placeholder="搜索订单..."
              density="compact"
              hide-details
              prepend-inner-icon="mdi-magnify"
              style="width: 250px;"
              clearable
            ></v-text-field>
            <v-select
              v-model="dateFilter"
              :items="dateFilterOptions"
              label="时间过滤"
              density="compact"
              style="width: 150px;"
              clearable
            ></v-select>
          </div>
        </v-card-title>
        <v-card-text>
          <v-data-table
            :headers="headers"
            :items="filteredOrders"
            :loading="loading"
            item-key="order_id"
            class="elevation-1"
            :items-per-page="15"
          >
            <template v-slot:item.order_id="{ item }">
              <v-chip size="small" color="primary">
                #{{ item.order_id }}
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
            <template v-slot:item.pile_id="{ item }">
              <v-chip size="small" color="info">
                桩 #{{ item.pile_id }}
              </v-chip>
            </template>
            <template v-slot:item.actual_charge_amount="{ item }">
              <div class="d-flex align-center">
                <v-icon size="16" color="warning" class="mr-1">mdi-battery</v-icon>
                {{ item.actual_charge_amount }} kWh
              </div>
            </template>
            <template v-slot:item.charge_duration="{ item }">
              {{ getChargeDuration(item) }}
            </template>
            <template v-slot:item.total_fee="{ item }">
              <div class="d-flex align-center">
                <v-icon size="16" color="success" class="mr-1">mdi-currency-cny</v-icon>
                <span class="font-weight-bold text-success">¥{{ item.total_fee }}</span>
              </div>
            </template>
            <template v-slot:item.created_at="{ item }">
              {{ formatDateTime(item.created_at) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn-group density="compact">
                <v-btn 
                  size="small" 
                  icon="mdi-eye" 
                  @click="viewOrderDetails(item)"
                  color="info"
                ></v-btn>
                <v-btn 
                  size="small" 
                  icon="mdi-download" 
                  @click="downloadReceipt(item)"
                  color="success"
                ></v-btn>
              </v-btn-group>
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>
    </v-container>

    <!-- 订单详情对话框 -->
    <v-dialog v-model="detailsDialog" max-width="700">
      <v-card v-if="selectedOrder">
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2" color="primary">mdi-receipt</v-icon>
          订单详情 - #{{ selectedOrder.order_id }}
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-card variant="outlined" class="pa-3 mb-3">
                <v-card-subtitle class="pa-0 mb-2">基本信息</v-card-subtitle>
                <v-list density="compact">
                  <v-list-item>
                    <v-list-item-title>订单ID</v-list-item-title>
                    <v-list-item-subtitle>#{{ selectedOrder.order_id }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>用户ID</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedOrder.user_id }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>充电桩</v-list-item-title>
                    <v-list-item-subtitle>桩 #{{ selectedOrder.pile_id }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>创建时间</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDateTime(selectedOrder.created_at) }}</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-col>
            <v-col cols="12" md="6">
              <v-card variant="outlined" class="pa-3 mb-3">
                <v-card-subtitle class="pa-0 mb-2">充电信息</v-card-subtitle>
                <v-list density="compact">
                  <v-list-item>
                    <v-list-item-title>开始时间</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDateTime(selectedOrder.start_time) }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>结束时间</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDateTime(selectedOrder.end_time) }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>充电时长</v-list-item-title>
                    <v-list-item-subtitle>{{ getChargeDuration(selectedOrder) }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>充电电量</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedOrder.actual_charge_amount }} kWh</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-col>
            <v-col cols="12">
              <v-card variant="outlined" class="pa-3">
                <v-card-subtitle class="pa-0 mb-2">费用明细</v-card-subtitle>
                <v-row>
                  <v-col cols="6" sm="3">
                    <div class="text-center">
                      <div class="text-h6 text-primary">¥{{ selectedOrder.charge_fee }}</div>
                      <div class="text-caption">充电费</div>
                    </div>
                  </v-col>
                  <v-col cols="6" sm="3">
                    <div class="text-center">
                      <div class="text-h6 text-warning">¥{{ selectedOrder.service_fee }}</div>
                      <div class="text-caption">服务费</div>
                    </div>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <div class="text-center">
                      <div class="text-h5 text-success font-weight-bold">¥{{ selectedOrder.total_fee }}</div>
                      <div class="text-caption">总费用</div>
                    </div>
                  </v-col>
                </v-row>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="downloadReceipt(selectedOrder)" color="success" variant="outlined">
            <v-icon left>mdi-download</v-icon>
            下载收据
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

interface Order {
  order_id: number
  user_id: number
  pile_id: number
  start_time: string
  end_time: string
  actual_charge_amount: number
  charge_fee: number
  service_fee: number
  total_fee: number
  created_at: string
}

const { api } = useAdminAuth()

const loading = ref(false)
const orders = ref<Order[]>([])
const searchQuery = ref('')
const dateFilter = ref<string | null>(null)
const detailsDialog = ref(false)
const selectedOrder = ref<Order | null>(null)

// 表格headers
const headers = [
  { title: '订单ID', key: 'order_id', sortable: true },
  { title: '用户', key: 'user_id', sortable: true },
  { title: '充电桩', key: 'pile_id', sortable: true },
  { title: '充电量', key: 'actual_charge_amount', sortable: true },
  { title: '时长', key: 'charge_duration', sortable: false },
  { title: '费用', key: 'total_fee', sortable: true },
  { title: '创建时间', key: 'created_at', sortable: true },
  { title: '操作', key: 'actions', sortable: false }
]

// 时间过滤选项
const dateFilterOptions = [
  { title: '全部时间', value: null },
  { title: '今天', value: 'today' },
  { title: '本周', value: 'week' },
  { title: '本月', value: 'month' }
]

// 计算属性
const totalOrders = computed(() => orders.value.length)
const totalRevenue = computed(() => orders.value.reduce((sum, order) => sum + parseFloat(order.total_fee.toString()), 0))
const totalEnergy = computed(() => orders.value.reduce((sum, order) => sum + parseFloat(order.actual_charge_amount.toString()), 0))

const todayOrders = computed(() => {
  const today = new Date().toDateString()
  return orders.value.filter(order => new Date(order.created_at).toDateString() === today).length
})

const filteredOrders = computed(() => {
  let result = orders.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(order => 
      order.order_id.toString().includes(query) ||
      order.user_id.toString().includes(query) ||
      order.pile_id.toString().includes(query)
    )
  }
  
  if (dateFilter.value) {
    const now = new Date()
    result = result.filter(order => {
      const orderDate = new Date(order.created_at)
      switch (dateFilter.value) {
        case 'today':
          return orderDate.toDateString() === now.toDateString()
        case 'week':
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          return orderDate >= weekAgo
        case 'month':
          const monthAgo = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
          return orderDate >= monthAgo
        default:
          return true
      }
    })
  }
  
  return result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

// 获取订单数据
const fetchOrders = async () => {
  try {
    loading.value = true
    const data = await api('/admin/orders')
    orders.value = data
  } catch (error) {
    console.error('Failed to fetch orders:', error)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  await fetchOrders()
}

// 查看订单详情
const viewOrderDetails = (order: Order) => {
  selectedOrder.value = order
  detailsDialog.value = true
}

// 下载收据
const downloadReceipt = (order: Order) => {
  console.log('Download receipt for order:', order.order_id)
  // 实现下载收据功能
}

// 工具函数
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

const getChargeDuration = (order: Order) => {
  const start = new Date(order.start_time)
  const end = new Date(order.end_time)
  const duration = Math.floor((end.getTime() - start.getTime()) / 1000)
  
  const hours = Math.floor(duration / 3600)
  const minutes = Math.floor((duration % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

onMounted(async () => {
await fetchOrders()
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
