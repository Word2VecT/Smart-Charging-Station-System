<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card>
          <v-card-title class="text-center">Register</v-card-title>
          <v-card-text>
            <v-alert v-if="error" type="error" density="compact" class="mb-4">
              {{ error }}
            </v-alert>
            <v-form @submit.prevent="handleRegister">
              <v-text-field
                v-model="username"
                label="Username"
                required
                :disabled="loading"
              ></v-text-field>
              <v-text-field
                v-model="password"
                label="Password"
                type="password"
                required
                :disabled="loading"
              ></v-text-field>
              <v-btn type="submit" color="primary" block :loading="loading" :disabled="loading">Register</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useAuth } from '~/composables/useAuth';

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref(null);

const { register } = useAuth();

const handleRegister = async () => {
  loading.value = true;
  error.value = null;
  try {
    await register(username.value, password.value);
    // On success, useAuth will handle the redirect.
  } catch (e) {
    error.value = e.data?.detail || 'An unknown error occurred during registration.';
  } finally {
    loading.value = false;
  }
};
</script> 