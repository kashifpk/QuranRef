<template>
  <div class="user-menu">
    <Button
      v-if="!store.currentUser"
      icon="pi pi-sign-in"
      @click="store.login"
      text
      rounded
      v-tooltip.bottom="'Sign In'"
    />
    <template v-else>
      <img
        :src="store.currentUser.picture_url"
        :alt="store.currentUser.name"
        class="user-avatar"
        @click="toggleMenu"
        referrerpolicy="no-referrer"
      />
      <Menu ref="menuRef" :model="menuItems" :popup="true" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from '../store';
import Button from 'primevue/button';
import Menu from 'primevue/menu';

const store = useStore();
const router = useRouter();
const menuRef = ref();

const toggleMenu = (event: Event) => {
  menuRef.value.toggle(event);
};

const menuItems = computed(() => [
  {
    label: store.currentUser?.name || '',
    items: [
      {
        label: store.currentUser?.email || '',
        icon: 'pi pi-envelope',
        disabled: true,
      },
      { separator: true },
      {
        label: 'My Bookmarks',
        icon: 'pi pi-bookmark',
        command: () => router.push('/bookmarks'),
      },
      {
        label: 'Sign Out',
        icon: 'pi pi-sign-out',
        command: () => store.logout(),
      },
    ],
  },
]);
</script>

<style scoped>
.user-menu {
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid rgba(255, 255, 255, 0.6);
  transition: border-color 0.2s;
}

.user-avatar:hover {
  border-color: white;
}
</style>
