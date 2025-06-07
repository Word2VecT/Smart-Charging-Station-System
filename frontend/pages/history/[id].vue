<template>
  <v-container>
    <v-btn to="/history" prepend-icon="mdi-arrow-left" class="mb-4">
      Back to History
    </v-btn>
    <v-card v-if="loading" :loading="loading">
      <v-card-text>Loading order details...</v-card-text>
    </v-card>
    <v-alert v-else-if="!order" type="error">
      Order not found or you do not have permission to view it.
    </v-alert>
    <v-card v-else>
      <v-card-title>Order Details #{{ order.order_id }}</v-card-title>
      <v-card-subtitle>{{ new Date(order.created_at).toLocaleString() }}</v-card-subtitle>
      <v-divider></v-divider>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title><strong>Total Fee:</strong></v-list-item-title>
            <v-list-item-subtitle>€{{ order.total_fee.toFixed(2) }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title><strong>Service Fee:</strong></v-list-item-title>
            <v-list-item-subtitle>€{{ order.service_fee.toFixed(2) }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title><strong>Charge Fee:</strong></v-list-item-title>
            <v-list-item-subtitle>€{{ order.charge_fee.toFixed(2) }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
         <v-divider></v-divider>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title><strong>Energy Consumed:</strong></v-list-item-title>
            <v-list-item-subtitle>{{ order.actual_charge_amount.toFixed(3) }} kWh</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title><strong>Charging Duration:</strong></v-list-item-title>
            <v-list-item-subtitle>{{ chargeDuration }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
         <v-divider></v-divider>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title><strong>Charging Pile ID:</strong></v-list-item-title>
            <v-list-item-subtitle>#{{ order.pile_id }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title><strong>Request ID:</strong></v-list-item-title>
            <v-list-item-subtitle>#{{ order.request_id }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useOrder } from '~/composables/useOrder';

const route = useRoute();
const { order, fetchOrderById } = useOrder();
const loading = ref(false);

const orderId = route.params.id;

const chargeDuration = computed(() => {
    if (!order.value) return 'N/A';
    const start = new Date(order.value.start_time);
    const end = new Date(order.value.end_time);
    const diffMs = end - start;
    const diffMins = Math.round(diffMs / 60000);
    return `${diffMins} minutes`;
});

onMounted(async () => {
  loading.value = true;
  await fetchOrderById(orderId);
  loading.value = false;
});
</script> 