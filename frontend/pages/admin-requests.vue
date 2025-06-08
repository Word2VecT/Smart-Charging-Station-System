<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">📥 所有充电请求</h2>
    <ul v-if="requests.length">
      <li v-for="req in requests" :key="req.request_id" class="mb-2 border p-4 rounded">
        <p><strong>请求ID:</strong> {{ req.request_id }}</p>
        <p><strong>用户ID:</strong> {{ req.user_id }}</p>
        <p><strong>类型:</strong> {{ req.requested_charge_type }}</p>
        <p><strong>状态:</strong> {{ req.status }}</p>
        <p><strong>时间:</strong> {{ req.request_time }}</p>
      </li>
    </ul>
    <p v-else>暂无请求数据</p>
  </div>
</template>

<script setup lang="ts">
import { useAdminRequests } from '~/composables/useAdminRequests'
const { requests, fetchRequests } = useAdminRequests()
await fetchRequests()
</script>
