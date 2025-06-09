<template>
  <div class="admin-users">
    <v-container fluid class="pa-6">
      <!-- 页面标题 -->
      <v-row class="mb-6">
        <v-col>
          <div class="d-flex align-center justify-space-between">
            <div>
              <h1 class="text-h3 font-weight-bold mb-2">
                <v-icon class="mr-3" size="40" color="primary">mdi-account-group</v-icon>
                用户管理
              </h1>
              <p class="text-h6 text-grey-darken-1">管理系统中的所有用户</p>
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
          <v-card class="stat-card text-center" height="100">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-primary">{{ totalUsers }}</div>
                <div class="text-body-2 text-grey-darken-1">总用户数</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="100">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-success">{{ activeUsers }}</div>
                <div class="text-body-2 text-grey-darken-1">活跃用户</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="100">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-warning">{{ todayRegistrations }}</div>
                <div class="text-body-2 text-grey-darken-1">今日注册</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card text-center" height="100">
            <v-card-text class="d-flex align-center justify-center">
              <div>
                <div class="text-h4 font-weight-bold text-info">{{ adminUsers }}</div>
                <div class="text-body-2 text-grey-darken-1">管理员</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 用户列表 -->
      <v-card>
        <v-card-title class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-account-multiple</v-icon>
            用户列表
          </div>
          <div class="d-flex align-center gap-3">
            <v-text-field
              v-model="searchQuery"
              placeholder="搜索用户..."
              density="compact"
              hide-details
              prepend-inner-icon="mdi-magnify"
              style="width: 250px;"
              clearable
            ></v-text-field>
            <v-select
              v-model="roleFilter"
              :items="roleFilterOptions"
              label="角色过滤"
              density="compact"
              style="width: 150px;"
              clearable
            ></v-select>
          </div>
        </v-card-title>
        <v-card-text>
          <v-data-table
            :headers="headers"
            :items="filteredUsers"
            :loading="loading"
            item-key="user_id"
            class="elevation-1"
            :items-per-page="10"
          >
            <template v-slot:item.user_id="{ item }">
              <v-chip size="small" color="primary">
                #{{ item.user_id }}
              </v-chip>
            </template>
            <template v-slot:item.username="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="32" :color="getUserAvatarColor(item.role)" class="mr-3">
                  <v-icon size="18" color="white">
                    {{ item.role === 'admin' ? 'mdi-shield-crown' : 'mdi-account' }}
                  </v-icon>
                </v-avatar>
                <div>
                  <div class="font-weight-bold">{{ item.username }}</div>
                  <div class="text-caption text-grey-darken-1">
                    ID: {{ item.user_id }}
                  </div>
                </div>
              </div>
            </template>
            <template v-slot:item.role="{ item }">
              <v-chip 
                :color="getRoleColor(item.role)" 
                size="small"
              >
                <v-icon left size="small">
                  {{ item.role === 'admin' ? 'mdi-shield-crown' : 'mdi-account' }}
                </v-icon>
                {{ getRoleText(item.role) }}
              </v-chip>
            </template>
            <template v-slot:item.registration_date="{ item }">
              {{ formatDateTime(item.registration_date) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn-group density="compact">
                <v-btn 
                  size="small" 
                  icon="mdi-eye" 
                  @click="viewUserDetails(item)"
                  color="info"
                ></v-btn>
                <v-btn 
                  size="small" 
                  icon="mdi-pencil" 
                  @click="editUser(item)"
                  color="warning"
                ></v-btn>
                <v-btn 
                  size="small" 
                  icon="mdi-delete" 
                  @click="deleteUser(item)"
                  color="error"
                  :disabled="item.role === 'admin'"
                ></v-btn>
              </v-btn-group>
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>
    </v-container>

    <!-- 用户详情对话框 -->
    <v-dialog v-model="detailsDialog" max-width="600">
      <v-card v-if="selectedUser">
        <v-card-title class="d-flex align-center">
          <v-avatar :color="getUserAvatarColor(selectedUser.role)" class="mr-3">
            <v-icon color="white">
              {{ selectedUser.role === 'admin' ? 'mdi-shield-crown' : 'mdi-account' }}
            </v-icon>
          </v-avatar>
          用户详情 - {{ selectedUser.username }}
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" sm="6">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>用户ID</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedUser.user_id }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>用户名</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedUser.username }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>角色</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip :color="getRoleColor(selectedUser.role)" size="small">
                      {{ getRoleText(selectedUser.role) }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>注册时间</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDateTime(selectedUser.registration_date) }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
            <v-col cols="12" sm="6">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>账户状态</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip color="success" size="small">正常</v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>最后登录</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDateTime(selectedUser.registration_date) }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>充电次数</v-list-item-title>
                  <v-list-item-subtitle>0 次</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>总充电费用</v-list-item-title>
                  <v-list-item-subtitle>¥0.00</v-list-item-subtitle>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

definePageMeta({
  layout: 'admin'
})

interface User {
  user_id: number
  username: string
  role: string
  registration_date: string
}

const { api } = useAdminAuth()

const loading = ref(false)
const users = ref<User[]>([])
const searchQuery = ref('')
const roleFilter = ref<string | null>(null)
const detailsDialog = ref(false)
const selectedUser = ref<User | null>(null)

// 表格headers
const headers = [
  { title: 'ID', key: 'user_id', sortable: true },
  { title: '用户信息', key: 'username', sortable: true },
  { title: '角色', key: 'role', sortable: true },
  { title: '注册时间', key: 'registration_date', sortable: true },
  { title: '操作', key: 'actions', sortable: false }
]

// 角色过滤选项
const roleFilterOptions = [
  { title: '全部角色', value: null },
  { title: '普通用户', value: 'user' },
  { title: '管理员', value: 'admin' }
]

// 计算属性
const totalUsers = computed(() => users.value.length)
const activeUsers = computed(() => users.value.filter(u => u.role === 'user').length)
const adminUsers = computed(() => users.value.filter(u => u.role === 'admin').length)
const todayRegistrations = computed(() => {
  const today = new Date().toDateString()
  return users.value.filter(u => new Date(u.registration_date).toDateString() === today).length
})

const filteredUsers = computed(() => {
  let result = users.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(u => 
      u.username.toLowerCase().includes(query) ||
      u.user_id.toString().includes(query)
    )
  }
  
  if (roleFilter.value) {
    result = result.filter(u => u.role === roleFilter.value)
  }
  
  return result
})

// 获取用户数据
const fetchUsers = async () => {
  try {
    loading.value = true
    const data = await api('/admin/users')
    users.value = data
  } catch (error) {
    console.error('Failed to fetch users:', error)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  await fetchUsers()
}

// 查看用户详情
const viewUserDetails = (user: User) => {
  selectedUser.value = user
  detailsDialog.value = true
}

// 编辑用户
const editUser = (user: User) => {
  console.log('Edit user:', user.username)
  // 实现编辑用户功能
}

// 删除用户
const deleteUser = (user: User) => {
  if (confirm(`确定要删除用户 ${user.username} 吗？`)) {
    console.log('Delete user:', user.username)
    // 实现删除用户功能
  }
}

// 工具函数
const getUserAvatarColor = (role: string) => {
  return role === 'admin' ? 'primary' : 'secondary'
}

const getRoleColor = (role: string) => {
  return role === 'admin' ? 'primary' : 'success'
}

const getRoleText = (role: string) => {
  return role === 'admin' ? '管理员' : '普通用户'
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

onMounted(async () => {
  await fetchUsers()
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
