<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.not-found {
  text-align: center;
  margin-top: 100px;
  margin-bottom: 100px;
  height: 68vh;
}
</style>

<template>
  <v-container class="not-found">
    <v-row>
      <v-col>
        <h2>404 - Not Found</h2>
        <p>
            The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
  // import { mande } from 'mande';
  import { VContainer, VRow, VCol } from 'vuetify/components';
</script>

