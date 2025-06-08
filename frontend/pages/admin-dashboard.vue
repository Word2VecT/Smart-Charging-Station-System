<template>
  <div class="p-12 text-center">
    <h1 class="text-h3 mb-4">欢迎，管理员！</h1>
    <p class="mb-6">请选择你要管理的模块</p>

    <div class="space-y-2">
      <NuxtLink to="/admin-users">👤 管理用户</NuxtLink><br />
      <NuxtLink to="/admin-orders">📄 查看订单</NuxtLink><br />
      <NuxtLink to="/admin-piles">🔌 管理充电桩</NuxtLink><br />
      <NuxtLink to="/admin-requests">📥 查看请求</NuxtLink>
    </div>
  </div>
</template>
