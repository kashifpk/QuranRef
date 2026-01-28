<template>
  <div class="not-found">
    <Card>
      <template #content>
        <div class="not-found-content">
          <i class="pi pi-exclamation-circle error-icon"></i>
          <h2>404 - Not Found</h2>
          <p>
            The page you are looking for might have been removed, had its name changed, or is
            temporarily unavailable.
          </p>
          <Button label="Go Home" icon="pi pi-home" @click="$router.push('/')" severity="success" />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import Card from 'primevue/card';
import Button from 'primevue/button';
</script>

<style scoped>
.not-found {
  max-width: 600px;
  margin: 100px auto;
  padding: 0 1rem;
}

.not-found-content {
  text-align: center;
  padding: 2rem;
}

.error-icon {
  font-size: 4rem;
  color: #f44336;
  margin-bottom: 1rem;
}

.not-found-content h2 {
  color: var(--app-text, #333);
  margin: 0 0 1rem;
}

.dark-mode .not-found-content h2 {
  color: #e0e0e0;
}

.not-found-content p {
  color: #666;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.dark-mode .not-found-content p {
  color: #999;
}
</style>
