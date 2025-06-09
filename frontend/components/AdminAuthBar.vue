<template>
  <div class="auth-bar">
    <template v-if="admin">
      <!-- 用户信息显示 -->
      <div class="user-info d-flex align-center mr-4">
        <v-avatar size="40" class="mr-3 neon-glow" color="primary">
          <v-icon color="white">mdi-shield-crown</v-icon>
        </v-avatar>
        <div class="d-none d-md-block">
          <p class="text-body-2 ma-0 font-weight-medium text-primary">
            {{ admin.username }}
          </p>
          <p class="text-caption ma-0 text-grey-lighten-1">
            管理员
          </p>
        </div>
      </div>

      <!-- 导航按钮 -->
      <div class="nav-buttons d-flex align-center">
        <v-btn
          to="/admin-visualization"
          variant="outlined"
          color="info"
          class="btn-futuristic mr-3 text-none"
          size="small"
          prepend-icon="mdi-view-dashboard-variant"
        >
          <span class="d-none d-sm-inline">可视化</span>
        </v-btn>
        
        <v-btn
          @click="logout"
          variant="outlined"
          color="secondary"
          class="btn-futuristic text-none"
          size="small"
          prepend-icon="mdi-logout"
        >
          <span class="d-none d-sm-inline">退出登录</span>
        </v-btn>
      </div>
    </template>

    <template v-else>
      <!-- 未登录状态 -->
      <div class="auth-buttons d-flex align-center">
        <v-btn
          to="/admin-login"
          variant="flat"
          color="primary"
          class="btn-futuristic text-none neon-glow"
          size="small"
          prepend-icon="mdi-login"
        >
          管理员登录
        </v-btn>
      </div>
    </template>
  </div>
</template>

<script setup>
import { useAdminAuth } from '~/composables/useAdminAuth';

const { admin, logout } = useAdminAuth();
</script>

<style scoped>
.auth-bar {
  display: flex;
  align-items: center;
}

.user-info {
  position: relative;
}

.user-info::after {
  content: '';
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 1px;
  height: 40px;
  background: linear-gradient(180deg, transparent, rgba(0, 217, 255, 0.5), transparent);
}

.nav-buttons,
.auth-buttons {
  gap: 8px;
}

@media (max-width: 600px) {
  .user-info::after {
    display: none;
  }
}

.v-btn {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.v-btn:hover {
  transform: translateY(-2px);
}

.v-avatar {
  transition: all 0.3s ease;
}

.v-avatar:hover {
  transform: scale(1.1);
}
</style> 