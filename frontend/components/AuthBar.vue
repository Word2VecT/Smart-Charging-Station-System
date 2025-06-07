<template>
  <div class="auth-bar">
    <template v-if="user">
      <!-- 用户信息显示 -->
      <div class="user-info d-flex align-center mr-4">
        <v-avatar size="40" class="mr-3 neon-glow">
          <v-icon color="primary">mdi-account-circle</v-icon>
        </v-avatar>
        <div class="d-none d-md-block">
          <p class="text-body-2 ma-0 font-weight-medium text-primary">
            {{ user.username }}
          </p>
          <p class="text-caption ma-0 text-grey-lighten-1">
            在线用户
          </p>
        </div>
      </div>

      <!-- 导航按钮 -->
      <div class="nav-buttons d-flex align-center">
        <v-btn
          to="/history"
          variant="outlined"
          color="primary"
          class="btn-futuristic mr-3 text-none"
          size="small"
          prepend-icon="mdi-history"
        >
          <span class="d-none d-sm-inline">充电历史</span>
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
          to="/login"
          variant="outlined"
          color="primary"
          class="btn-futuristic mr-3 text-none"
          size="small"
          prepend-icon="mdi-login"
        >
          登录
        </v-btn>
        
        <v-btn
          to="/register"
          variant="flat"
          color="primary"
          class="btn-futuristic text-none neon-glow"
          size="small"
          prepend-icon="mdi-account-plus"
        >
          注册
        </v-btn>
      </div>
    </template>
  </div>
</template>

<script setup>
import { useAuth } from '~/composables/useAuth';

const { user, logout } = useAuth();
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

/* 响应式设计 */
@media (max-width: 600px) {
  .user-info::after {
    display: none;
  }
  
  .nav-buttons {
    gap: 4px;
  }
  
  .auth-buttons {
    gap: 4px;
  }
}

/* 按钮悬浮动画 */
.v-btn {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.v-btn:hover {
  transform: translateY(-2px);
}

/* 头像脉动效果 */
.v-avatar {
  transition: all 0.3s ease;
}

.v-avatar:hover {
  transform: scale(1.1);
}
</style> 