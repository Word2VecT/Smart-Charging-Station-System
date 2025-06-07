<template>
  <v-container>
    <v-card>
      <v-card-title>
        History
        <v-spacer></v-spacer>
        <v-btn icon @click="router.push('/')">
          <v-icon>mdi-home</v-icon>
        </v-btn>
        <v-btn icon @click="loadHistory">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="historyItems"
          :loading="loading"
          class="elevation-1"
          @click:row="viewDetails"
          item-value="item_id"
          hover
        >
          <template v-slot:item.total_fee="{ item }">
            <span>¥{{ item.total_fee }}</span>
          </template>
          <template v-slot:item.date="{ item }">
            <span>{{ new Date(item.date).toLocaleString() }}</span>
          </template>
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" variant="elevated">
              {{ item.status }}
            </v-chip>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useHistory } from '~/composables/useHistory';

const { historyItems, fetchHistory } = useHistory();
const router = useRouter();
const loading = ref(false);

const headers = [
  { title: 'Type', value: 'item_type', sortable: true },
  { title: 'Status', value: 'status', sortable: true },
  { title: 'Date', value: 'date', sortable: true },
  { title: 'Charge Mode', value: 'charge_type', sortable: true },
  { title: 'Energy (kWh)', value: 'actual_charge_amount', sortable: false },
  { title: 'Total Fee', value: 'total_fee', sortable: true },
];

const getStatusColor = (status) => {
  switch (status) {
    case 'COMPLETED':
      return 'success';
    case 'CHARGING':
      return 'primary';
    case 'WAITING':
      return 'warning';
    case 'CANCELLED':
      return 'grey';
    default:
      return 'default';
  }
};

const loadHistory = async () => {
  loading.value = true;
  await fetchHistory();
  loading.value = false;
};

const viewDetails = (event, { item }) => {
  if (item.item_type === 'ORDER') {
    router.push(`/history/${item.item_id}`);
  } else {
    // For requests (WAITING, CHARGING), navigate to the homepage to see live status
    router.push('/');
  }
};

onMounted(() => {
  loadHistory();
});
</script>

<style scoped>
.v-data-table :deep(tbody tr) {
  cursor: pointer;
}
</style> 