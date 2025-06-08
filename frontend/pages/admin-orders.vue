<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">📄 所有充电订单</h2>
    <ul v-if="orders.length">
      <li v-for="order in orders" :key="order.order_id" class="mb-2 border p-4 rounded">
        <p><strong>订单ID:</strong> {{ order.order_id }}</p>
        <p><strong>用户ID:</strong> {{ order.user_id }}</p>
        <p><strong>充电量:</strong> {{ order.actual_charge_amount }} kWh</p>
        <p><strong>费用:</strong> ¥{{ order.total_fee }}</p>
        <p><strong>时间:</strong> {{ order.created_at }}</p>
      </li>
    </ul>
    <p v-else>暂无订单数据</p>
  </div>
</template>

<script setup lang="ts">
import { useAdminOrders } from '~/composables/useAdminOrders'
const { orders, fetchOrders } = useAdminOrders()
await fetchOrders()
</script>
