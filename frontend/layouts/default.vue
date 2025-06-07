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
            mdi-flash-circle
          </v-icon>
          <NuxtLink to="/" class="text-decoration-none">
            <h2 class="futuristic-font text-glow ma-0 text-accent-blue">
              SMART CHARGE
            </h2>
            <p class="text-caption ma-0 text-muted-custom">
              未来充电站
            </p>
          </NuxtLink>
        </div>

        <!-- 导航菜单 -->
        <div class="d-flex align-center">
          <AuthBar />
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
      <v-container class="py-8">
        <slot />
      </v-container>
    </v-main>

    <!-- 底部装饰线 -->
    <div class="bottom-accent animated-gradient"></div>
  </v-app>
</template>

<script setup>
import AuthBar from '~/components/AuthBar.vue';
</script>

<style scoped>
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
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
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

.shape-1 {
  width: 200px;
  height: 200px;
  top: 20%;
  right: 10%;
}

.shape-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  left: 5%;
}

.shape-3 {
  width: 100px;
  height: 100px;
  top: 40%;
  right: 30%;
}

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

/* 移动端适配 */
@media (max-width: 768px) {
  .shape {
    display: none;
  }
  
  .circuit-pattern {
    background-size: 25px 25px;
  }
  
  .futuristic-font {
    font-size: 1.4rem !important;
  }
}
</style> 