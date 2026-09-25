<template>
  <div class="collections-view">
    <div class="view-head">
      <h2>My Collections</h2>
      <Button
        v-if="store.currentUser"
        label="New collection"
        icon="pi pi-plus"
        size="small"
        @click="openCreate"
      />
    </div>

    <div v-if="!store.currentUser" class="auth-prompt">
      <i class="pi pi-lock" style="font-size: 2rem; color: #999;"></i>
      <p>Please sign in to keep collections of ayas.</p>
      <Button label="Sign In" icon="pi pi-sign-in" @click="store.login" />
    </div>

    <template v-else>
      <p v-if="store.collectionsLoading && store.collections.length === 0" class="empty-state">
        Loading collections...
      </p>
      <p v-else-if="store.collections.length === 0" class="empty-state">
        No collections yet. Use the menu on any aya, or the button above, to start one.
      </p>
      <div class="collection-cards">
        <Card v-for="c in store.collections" :key="c.id" class="collection-card">
          <template #content>
            <div class="card-row">
              <router-link :to="{ name: 'collection_view', params: { id: c.id } }" class="collection-name">
                {{ c.name }}
              </router-link>
              <Tag severity="success">{{ c.item_count }} {{ c.item_count === 1 ? 'aya' : 'ayas' }}</Tag>
            </div>
            <p v-if="c.description" class="collection-description" dir="auto">{{ c.description }}</p>
            <div class="card-actions">
              <Button icon="pi pi-pencil" text rounded size="small" v-tooltip.top="'Edit'" @click="openEdit(c)" />
              <Button icon="pi pi-trash" severity="danger" text rounded size="small" v-tooltip.top="'Delete'" @click="askDelete(c)" />
            </div>
          </template>
        </Card>
      </div>
    </template>

    <Dialog
      v-model:visible="formVisible"
      :header="editing ? 'Edit collection' : 'New collection'"
      :modal="true"
      :style="{ width: '440px', maxWidth: '95vw' }"
    >
      <div class="collection-form">
        <label class="form-field">
          <span>Name</span>
          <InputText v-model="formName" autofocus @keyup.enter="save" />
        </label>
        <label class="form-field">
          <span>Description</span>
          <Textarea v-model="formDescription" rows="3" autoResize />
        </label>
        <small v-if="formError" class="form-error">{{ formError }}</small>
      </div>
      <template #footer>
        <Button label="Cancel" text @click="formVisible = false" />
        <Button label="Save" :disabled="!formName.trim()" @click="save" />
      </template>
    </Dialog>

    <Dialog v-model:visible="deleteVisible" header="Delete collection" :modal="true" :style="{ width: '400px' }">
      <p>Delete "{{ deleting?.name }}" and its {{ deleting?.item_count }} ayas? The ayas themselves are not affected.</p>
      <template #footer>
        <Button label="Cancel" text @click="deleteVisible = false" />
        <Button label="Delete" severity="danger" @click="doDelete" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Tag from 'primevue/tag';
import Textarea from 'primevue/textarea';
import { useStore } from '../store';
import type { CollectionSummary } from '../type_defs';

const store = useStore();
const formVisible = ref(false);
const editing = ref<CollectionSummary | null>(null);
const formName = ref('');
const formDescription = ref('');
const formError = ref('');
const deleteVisible = ref(false);
const deleting = ref<CollectionSummary | null>(null);

function openCreate() {
  editing.value = null;
  formName.value = '';
  formDescription.value = '';
  formError.value = '';
  formVisible.value = true;
}

function openEdit(c: CollectionSummary) {
  editing.value = c;
  formName.value = c.name;
  formDescription.value = c.description;
  formError.value = '';
  formVisible.value = true;
}

async function save() {
  const name = formName.value.trim();
  if (!name) return;
  const result = editing.value
    ? await store.updateCollection(editing.value.id, { name, description: formDescription.value })
    : await store.createCollection(name, formDescription.value);
  if (!result) {
    formError.value = 'Could not save. A collection with that name may already exist.';
    return;
  }
  formVisible.value = false;
}

function askDelete(c: CollectionSummary) {
  deleting.value = c;
  deleteVisible.value = true;
}

async function doDelete() {
  if (deleting.value) await store.deleteCollection(deleting.value.id);
  deleteVisible.value = false;
  deleting.value = null;
}
</script>

<style scoped>
.collections-view {
  max-width: 800px;
  margin: 0 auto;
}

.view-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.view-head h2 {
  margin: 0;
  color: var(--p-text-color);
}

.auth-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
  color: var(--p-text-muted-color);
}

.empty-state {
  color: var(--p-text-muted-color);
  font-style: italic;
  padding: 1rem 0;
}

.collection-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.card-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.collection-name {
  font-weight: 600;
  font-size: 1.05rem;
  color: var(--p-primary-color);
  text-decoration: none;
}

.collection-name:hover {
  text-decoration: underline;
}

.collection-description {
  margin: 0.5rem 0 0;
  color: var(--p-text-muted-color);
  white-space: pre-line;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.25rem;
  margin-top: 0.25rem;
}

.collection-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.875rem;
}

.form-error {
  color: var(--p-red-500, #d32f2f);
}

.collection-card :deep(.p-card-body) {
  padding: 0.75rem 1rem;
}

.collection-card :deep(.p-card-content) {
  padding: 0;
}
</style>
