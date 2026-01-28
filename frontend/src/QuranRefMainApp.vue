<template>
  <div class="app-container" :class="{ 'dark-mode': store.darkMode }">
    <!-- Header Toolbar -->
    <header class="app-header">
      <div class="header-content">
        <div class="header-left">
          <Button
            icon="pi pi-bars"
            @click="drawerVisible = true"
            text
            rounded
            class="menu-button"
          />
          <a href="/" class="app-title ar">القرآن الكريم</a>
        </div>

        <div class="header-center">
          <IconField class="search-field">
            <InputIcon class="pi pi-search" />
            <InputText
              v-model="searchTerm"
              placeholder="Search..."
              @keyup.enter="doSearch"
            />
          </IconField>
        </div>

        <div class="header-right">
          <Button
            icon="pi pi-cog"
            @click="settingsDialogVisible = true"
            text
            rounded
            v-tooltip.bottom="'Text Settings'"
          />
          <Button
            :icon="store.darkMode ? 'pi pi-sun' : 'pi pi-moon'"
            @click="store.toggleDarkMode"
            text
            rounded
            v-tooltip.bottom="store.darkMode ? 'Light Mode' : 'Dark Mode'"
          />
          <Button
            icon="pi pi-home"
            @click="$router.push('/')"
            text
            rounded
            v-tooltip.bottom="'Home'"
          />
          <Button
            icon="pi pi-book"
            @click="$router.push('/by_word')"
            text
            rounded
            v-tooltip.bottom="'Browse by Word'"
          />
        </div>
      </div>
    </header>

    <!-- Navigation Drawer -->
    <Drawer v-model:visible="drawerVisible" header="Navigation" class="app-drawer">
      <div class="drawer-content">
        <div class="nav-section">
          <router-link to="/" class="nav-link" @click="drawerVisible = false">
            <i class="pi pi-home"></i>
            <span>Home</span>
          </router-link>

          <Divider />

          <router-link to="/by_word" class="nav-link" @click="drawerVisible = false">
            <i class="pi pi-book"></i>
            <span>Browse by Word</span>
          </router-link>

          <router-link to="/by_word_count" class="nav-link" @click="drawerVisible = false">
            <i class="pi pi-sort-numeric-down"></i>
            <span>Words by Count</span>
          </router-link>

          <Divider />

          <a class="nav-link" @click="openSettings">
            <i class="pi pi-cog"></i>
            <span>Text Settings</span>
          </a>
        </div>
      </div>
    </Drawer>

    <!-- Text Settings Dialog -->
    <TextSettingsDialog v-model:visible="settingsDialogVisible" />

    <!-- Main Content -->
    <main class="app-main">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <span>Arabic texts and translations courtesy of</span>
      <a href="http://tanzil.net" target="_blank" rel="noopener">tanzil.net</a>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from './store';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import Drawer from 'primevue/drawer';
import Divider from 'primevue/divider';
import TextSettingsDialog from './components/TextSettingsDialog.vue';

const router = useRouter();
const store = useStore();
const searchTerm = ref('');
const drawerVisible = ref(false);
const settingsDialogVisible = ref(false);

// Initialize theme on mount
onMounted(() => {
  store.initializeTheme();
});

const doSearch = () => {
  if (searchTerm.value.trim()) {
    router.push({ name: 'search', params: { search_term: searchTerm.value } });
    drawerVisible.value = false;
  }
};

const openSettings = () => {
  drawerVisible.value = false;
  settingsDialogVisible.value = true;
};
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--app-bg, #fafafa);
  color: var(--app-text, #1a1a1a);
}

/* Header Styles */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-center {
  flex: 1;
  max-width: 400px;
  margin: 0 1rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.menu-button {
  color: white !important;
}

.app-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #E8F5E9;
  text-decoration: none;
}

.app-header :deep(.p-button) {
  color: white;
}

.app-header :deep(.p-button:hover) {
  background: rgba(255, 255, 255, 0.1);
}

.search-field {
  width: 100%;
}

.search-field :deep(.p-inputtext) {
  width: 100%;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 2rem;
}

.search-field :deep(.p-inputtext:focus) {
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
}

/* Drawer Styles */
.app-drawer {
  --p-drawer-background: var(--app-surface, #ffffff);
}

.drawer-content {
  padding: 1rem 0;
}

.nav-section {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: var(--app-text, #1a1a1a);
  text-decoration: none;
  border-radius: 0.5rem;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background: rgba(76, 175, 80, 0.1);
  cursor: pointer;
}

.nav-link i {
  font-size: 1.125rem;
  color: #4CAF50;
}


/* Main Content */
.app-main {
  flex: 1;
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* Footer Styles */
.app-footer {
  background: var(--app-surface, #ffffff);
  border-top: 1px solid var(--p-surface-200, #e5e7eb);
  padding: 1rem;
  text-align: center;
  font-size: 0.875rem;
  color: #666;
}

.app-footer a {
  color: #4CAF50;
  text-decoration: none;
  margin-left: 0.25rem;
}

.app-footer a:hover {
  text-decoration: underline;
}

/* Dark Mode Styles */
.dark-mode {
  --app-bg: #121212;
  --app-surface: #1E1E1E;
  --app-text: #E0E0E0;
}

.dark-mode .app-header {
  background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
}

.dark-mode .app-footer {
  background: #1E1E1E;
  border-color: #333;
  color: #999;
}

.dark-mode .nav-link {
  color: #E0E0E0;
}

/* Responsive Styles */
@media (max-width: 768px) {
  .header-center {
    display: none;
  }

  .app-title {
    font-size: 1rem;
  }

  .app-main {
    padding: 1rem;
  }
}

/* Menu button always visible - drawer contains settings */
</style>
