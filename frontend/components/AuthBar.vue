<template>
  <div>
    <template v-if="user">
      <span>Welcome, {{ user.username }}!</span>
      <v-btn to="/history" small class="ml-4">History</v-btn>
      <v-btn @click="logout" small class="ml-2">Logout</v-btn>
    </template>
    <template v-else>
      <v-btn to="/login" small class="mr-2">Login</v-btn>
      <v-btn to="/register" small>Register</v-btn>
    </template>
  </div>
</template>

<script setup>
import { useAuth } from '~/composables/useAuth';

const { user, logout } = useAuth();
</script> 