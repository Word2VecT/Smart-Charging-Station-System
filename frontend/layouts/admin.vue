<template>
  <v-app>
    <!-- 粒子背景 -->
    <div class="particles-bg">
      <div
        v-for="i in 50"
        :key="i"
        class="particle"
        :style="{
          left: Math.random() * 100 + '%',
          animationDelay: Math.random() * 10 + 's',
          animationDuration: (Math.random() * 10 + 5) + 's'
        }"
      ></div>
    </div>

    <!-- 现代化导航栏 -->
    <v-app-bar
      app
      elevation="0"
      class="glass-morph"
      style="backdrop-filter: blur(20px);"
      height="80"
    >
      <v-container class="d-flex align-center justify-space-between pa-0">
        <!-- Logo区域 -->
        <div class="d-flex align-center">
          <v-icon
            size="40"
            color="primary"
            class="mr-3 pulse"
          >
            mdi-shield-crown
          </v-icon>
          <NuxtLink to="/admin-dashboard" class="text-decoration-none">
            <h2 class="futuristic-font text-glow ma-0 text-accent-blue">
              ADMIN PANEL
            </h2>
            <p class="text-caption ma-0 text-muted-custom">
              未来充电站管理后台
            </p>
          </NuxtLink>
        </div>

        <!-- 导航菜单 -->
        <div class="d-flex align-center">
          <AdminAuthBar />
        </div>
      </v-container>
    </v-app-bar>

    <!-- 主要内容区域 -->
    <v-main class="main-content">
      <!-- 背景装饰 -->
      <div class="background-decoration">
        <div class="circuit-pattern"></div>
        <div class="floating-shapes">
          <div class="shape shape-1 float"></div>
          <div class="shape shape-2 float" style="animation-delay: -1s;"></div>
          <div class="shape shape-3 float" style="animation-delay: -2s;"></div>
        </div>
      </div>

      <!-- 内容容器 -->
      <v-container fluid>
        <slot />
      </v-container>
    </v-main>

    <!-- 悬浮导航按钮 -->
    <v-menu v-model="fabMenu" location="top" transition="slide-y-reverse-transition">
      <template v-slot:activator="{ props }">
        <v-btn
          v-bind="props"
          icon
          size="x-large"
          color="primary"
          class="fab-nav"
          elevation="8"
        >
          <v-icon>mdi-menu</v-icon>
        </v-btn>
      </template>

      <v-list density="compact" class="fab-menu-list">
        <v-list-item
          v-for="item in navigationItems"
          :key="item.path"
          :to="item.path"
          :prepend-icon="item.icon"
          :title="item.title"
          class="fab-menu-item"
        >
        </v-list-item>
      </v-list>
    </v-menu>

    <!-- 底部装饰线 -->
    <div class="bottom-accent animated-gradient"></div>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AdminAuthBar from '~/components/AdminAuthBar.vue'

const fabMenu = ref(false)

// 导航菜单项
const navigationItems = [
  {
    path: '/admin-dashboard',
    icon: 'mdi-view-dashboard',
    title: '仪表盘',
  },
  {
    path: '/admin-visualization',
    icon: 'mdi-view-dashboard-variant',
    title: '可视化',
  },
  {
    path: '/admin-piles',
    icon: 'mdi-ev-station',
    title: '充电桩管理',
  },
  {
    path: '/admin-users',
    icon: 'mdi-account-group',
    title: '用户管理',
  },
  {
    path: '/admin-orders',
    icon: 'mdi-receipt',
    title: '订单管理',
  },
  {
    path: '/admin-requests',
    icon: 'mdi-format-list-bulleted',
    title: '请求管理',
  }
]
</script>

<style scoped>
/* 继承自 default.vue 的样式 */
.main-content {
  position: relative;
  min-height: 100vh;
}

.background-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: -1;
}

.circuit-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(90deg, rgba(0, 217, 255, 0.1) 1px, transparent 1px),
    linear-gradient(rgba(0, 217, 255, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: circuitMove 20s linear infinite;
}

@keyframes circuitMove {
  0% { transform: translate(0, 0); }
  100% { transform: translate(50px, 50px); }
}

.floating-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, rgba(0, 217, 255, 0.1), rgba(255, 107, 53, 0.1));
  backdrop-filter: blur(10px);
}

.shape-1 { width: 200px; height: 200px; top: 20%; right: 10%; }
.shape-2 { width: 150px; height: 150px; top: 60%; left: 5%; }
.shape-3 { width: 100px; height: 100px; top: 40%; right: 30%; }

.bottom-accent {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  z-index: 1000;
}

.v-app-bar {
  border-bottom: 1px solid rgba(0, 217, 255, 0.2);
}

.fab-nav {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 100;
}

.fab-menu-list {
  background: rgba(40, 40, 60, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 217, 255, 0.3);
  border-radius: 12px;
}

.fab-menu-item {
  color: #fff;
}

.fab-menu-item:hover {
  background: rgba(0, 217, 255, 0.2);
}

.futuristic-font {
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.text-glow {
  text-shadow: 0 0 8px rgba(0, 217, 255, 0.7);
}
</style> 