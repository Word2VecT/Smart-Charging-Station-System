<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">👤 所有用户</h2>
    <ul v-if="users.length">
      <li v-for="user in users" :key="user.user_id" class="mb-2 border p-4 rounded">
        <p><strong>用户ID:</strong> {{ user.user_id }}</p>
        <p><strong>用户名:</strong> {{ user.username }}</p>
        <p><strong>角色:</strong> {{ user.role }}</p>
      </li>
    </ul>
    <p v-else>暂无用户数据</p>
  </div>
</template>

<script setup lang="ts">
import { useAdminUsers } from '~/composables/useAdminUsers'
const { users, fetchUsers } = useAdminUsers()
await fetchUsers()
</script>
