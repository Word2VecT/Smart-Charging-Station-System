<template>
  <v-container>
    <div v-if="user">
      <h1 class="mb-4">Welcome, {{ user.username }}!</h1>
      <ChargingDashboard />
    </div>
    <div v-else>
      <v-alert type="info" class="mb-4">
        You are not logged in.
      </v-alert>
      <h1 class="text-center mb-4">Welcome to the Smart Charging Station</h1>
      <p class="text-center">Please <NuxtLink to="/login">login</NuxtLink> or <NuxtLink to="/register">register</NuxtLink> to continue.</p>
    </div>
  </v-container>
</template>

<script setup>
import { useAuth } from '~/composables/useAuth';
import ChargingDashboard from '~/components/ChargingDashboard.vue';

const { user } = useAuth();

definePageMeta({
  // This page requires authentication to be useful,
  // so we could add middleware here to redirect non-logged-in users.
  // For now, we show a message.
});
</script> 