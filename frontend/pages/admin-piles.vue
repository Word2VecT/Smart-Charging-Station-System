<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">🔌 充电桩列表</h2>
    <ul v-if="piles.length">
      <li
        v-for="pile in piles"
        :key="pile.pile_id"
        class="mb-4 border p-4 rounded shadow-sm bg-white"
      >
        <p><strong>ID:</strong> {{ pile.pile_id }}</p>
        <p><strong>编号:</strong> {{ pile.pile_code }}</p>
        <p><strong>类型:</strong> {{ pile.type }}</p>
        <p><strong>状态:</strong> {{ pile.status }}</p>
        <p><strong>功率:</strong> {{ pile.power_rate }} kW</p>

        <!-- 启用/停用按钮 -->
        <button
          class="mt-2 px-4 py-2 rounded text-white"
          :class="pile.status === 'OFF' ? 'bg-green-600' : 'bg-red-600'"
          @click="togglePileStatus(pile)"
        >
          {{ pile.status === 'OFF' ? '启用' : '停用' }}
        </button>
      </li>
    </ul>
    <p v-else>暂无充电桩数据</p>
  </div>
</template>

<script setup lang="ts">
import { useAdminPile } from '~/composables/useAdminPile'
import { ref } from 'vue'

const { piles, fetchPiles, apiFetch } = useAdminPile()
await fetchPiles()

const togglePileStatus = async (pile: any) => {
  const newStatus = pile.status === 'OFF' ? 'AVAILABLE' : 'OFF'
  try {
    const updated = await apiFetch(`/admin/piles/${pile.pile_id}/status`, {
      method: 'PATCH',
      body: {
        status: newStatus,
        details: '由管理员手动切换',
      },
    })
    pile.status = updated.status
  } catch (err) {
    console.error('切换失败:', err)
    alert('状态切换失败，请重试')
  }
}
</script>
