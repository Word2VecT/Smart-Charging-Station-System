<template>
  <v-card>
    <v-card-title>Charging Dashboard</v-card-title>
    <v-card-text>
      <!-- Show status if there is an active request -->
      <div v-if="activeRequest">
        <v-alert :type="alertType" class="mb-4" prominent>
          <div class="d-flex align-center">
            <v-progress-circular v-if="activeRequest.status === 'WAITING'" indeterminate size="24" class="mr-2"></v-progress-circular>
            <v-icon v-else-if="activeRequest.status === 'CHARGING'" class="mr-2">mdi-flash</v-icon>
            <strong>Status: {{ activeRequest.status }}</strong>
          </div>
        </v-alert>

        <v-list-item-group>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title><strong>Queue Number:</strong> {{ activeRequest.queue_number }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-list-item v-if="activeRequest.status === 'WAITING'">
             <v-list-item-content>
              <v-list-item-title><strong>Cars Ahead:</strong> {{ waitingInfo.carsAhead }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

           <v-list-item v-if="activeRequest.status === 'CHARGING'">
            <v-list-item-content>
              <v-list-item-title><strong>Charging Pile:</strong> #{{ activeRequest.assigned_pile_id }}</v-list-item-title>
              <v-list-item-subtitle>Power Rate: {{ pilePowerRate }} kWh</v-list-item-subtitle>
              <v-progress-linear :model-value="chargePercentage" color="primary" height="20" striped class="mt-2">
                <strong>{{ chargePercentage.toFixed(1) }}%</strong>
              </v-progress-linear>
              <div class="text-caption">
                {{ chargedAmount.toFixed(2) }} / {{ activeRequest.requested_charge_amount }} kWh
              </div>
            </v-list-item-content>
          </v-list-item>

          <v-list-item>
            <v-list-item-content>
              <v-list-item-title><strong>Type:</strong> {{ activeRequest.requested_charge_type }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title><strong>Amount:</strong> {{ activeRequest.requested_charge_amount }} kWh</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>

        <div v-if="activeRequest.status === 'WAITING'" class="mt-4">
          <v-btn color="warning" @click="isEditing = !isEditing" class="mr-2">Modify</v-btn>
          <v-btn color="error" @click="handleCancel">Cancel Request</v-btn>
        </div>

        <div v-if="activeRequest.status === 'CHARGING'" class="mt-4">
           <v-btn color="error" @click="handleStop">Stop Charging</v-btn>
        </div>

        <!-- Modification Form -->
        <v-expand-transition>
          <div v-if="isEditing" class="mt-4">
            <v-select
              v-model="editForm.type"
              :items="['FAST', 'TRICKLE']"
              label="Charging Type"
            ></v-select>
            <v-text-field
              v-model.number="editForm.amount"
              label="Charge Amount (kWh)"
              type="number"
              min="1"
            ></v-text-field>
            <v-btn color="primary" @click="handleUpdate" class="mr-2">Save Changes</v-btn>
            <v-btn @click="isEditing = false">Close</v-btn>
          </div>
        </v-expand-transition>
      </div>

      <!-- Show request form if there is no active request -->
      <v-form v-else @submit.prevent="handleSubmit">
        <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>
        <v-select
          v-model="form.type"
          :items="['FAST', 'TRICKLE']"
          label="Select Charging Type"
          required
        ></v-select>
        <v-text-field
          v-model.number="form.amount"
          label="Charge Amount (kWh)"
          type="number"
          min="1"
          required
        ></v-text-field>
        <v-btn type="submit" color="primary" block :loading="loading">Submit Request</v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted, reactive, computed, onUnmounted } from 'vue';
import { useRequest } from '~/composables/useRequest';
import { usePile } from '~/composables/usePile';

const { activeRequest, createRequest, fetchActiveRequest, cancelRequest, updateRequest, fetchWaitingQueue, stopRequest } = useRequest();
const { piles, fetchPiles } = usePile();

const loading = ref(false);
const error = ref(null);
const isEditing = ref(false);
const waitingInfo = ref({ carsAhead: 0 });
let pollingInterval = null;

const form = reactive({
  type: 'FAST',
  amount: 10,
});

const editForm = reactive({
  type: '',
  amount: 0,
});

const alertType = computed(() => {
  if (!activeRequest.value) return 'info';
  switch (activeRequest.value.status) {
    case 'WAITING': return 'info';
    case 'CHARGING': return 'success';
    default: return 'secondary';
  }
});

const chargedAmount = computed(() => {
    if (activeRequest.value?.status !== 'CHARGING' || !activeRequest.value.start_time) {
        return 0;
    }
    const pile = piles.value.find(p => p.pile_id === activeRequest.value.assigned_pile_id);
    if (!pile) return 0;

    const startTime = new Date(activeRequest.value.start_time);
    const now = new Date();
    const durationSeconds = (now.getTime() - startTime.getTime()) / 1000;
    return (durationSeconds / 3600) * pile.power_rate;
});

const chargePercentage = computed(() => {
    if (!activeRequest.value || activeRequest.value.requested_charge_amount <= 0) {
        return 0;
    }
    return (chargedAmount.value / activeRequest.value.requested_charge_amount) * 100;
});

const pilePowerRate = computed(() => {
    if (activeRequest.value?.status !== 'CHARGING') return 0;
    const pile = piles.value.find(p => p.pile_id === activeRequest.value.assigned_pile_id);
    return pile ? pile.power_rate : 0;
});

const handleSubmit = async () => {
  loading.value = true;
  error.value = null;
  try {
    await createRequest(form.type, form.amount);
  } catch (e) {
    error.value = e.data?.detail || 'Failed to submit request.';
  } finally {
    loading.value = false;
    await fetchActiveRequest(); // Fetch immediately after submission
  }
};

const handleCancel = async () => {
    if (confirm('Are you sure you want to cancel this request?')) {
        try {
            await cancelRequest(activeRequest.value.request_id);
        } catch (e) {
            alert(e.data?.detail || 'Failed to cancel request.');
        }
    }
};

const handleStop = async () => {
    if (confirm('Are you sure you want to stop charging? This will generate a bill.')) {
        try {
            await stopRequest(activeRequest.value.request_id);
            await fetchActiveRequest(); // Refresh state
        } catch (e) {
            alert(e.data?.detail || 'Failed to stop charging.');
        }
    }
};

const handleUpdate = async () => {
    try {
        await updateRequest(activeRequest.value.request_id, {
            requested_charge_type: editForm.type,
            requested_charge_amount: editForm.amount,
        });
        isEditing.value = false;
    } catch (e) {
        alert(e.data?.detail || 'Failed to update request.');
    }
};

const updateWaitingInfo = async () => {
    if (activeRequest.value && activeRequest.value.status === 'WAITING') {
        const queue = await fetchWaitingQueue();
        const userQueue = activeRequest.value.requested_charge_type === 'FAST'
            ? queue.filter(r => r.requested_charge_type === 'FAST')
            : queue.filter(r => r.requested_charge_type === 'TRICKLE');
        
        const userIndex = userQueue.findIndex(r => r.request_id === activeRequest.value.request_id);
        if (userIndex !== -1) {
            waitingInfo.value.carsAhead = userIndex;
        }
    }
};

onMounted(async () => {
  await fetchPiles();
  await fetchActiveRequest();
  await updateWaitingInfo();
  
  pollingInterval = setInterval(async () => {
    await fetchActiveRequest();
    await updateWaitingInfo();
    // If charging, we need pile data to be fresh for power rate
    if (activeRequest.value?.status === 'CHARGING') {
        await fetchPiles();
    }
  }, 5000); // Poll every 5 seconds

  if (activeRequest.value) {
      editForm.type = activeRequest.value.requested_charge_type;
      editForm.amount = activeRequest.value.requested_charge_amount;
  }
});

onUnmounted(() => {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
});
</script> 