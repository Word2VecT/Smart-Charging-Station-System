<template>
  <v-app>
    <v-app-bar app>
      <v-toolbar-title>
        <NuxtLink to="/" class="text-decoration-none black--text">
          Smart Charging Station
        </NuxtLink>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <AuthBar />
    </v-app-bar>
    <v-main>
      <v-container>
        <slot />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import AuthBar from '~/components/AuthBar.vue';
</script>

<style scoped>
.black--text {
  color: black;
}
</style> 