<template>
  <div class="collection-view">
    <Card v-if="detail" class="collection-header">
      <template #content>
        <div v-if="!editing" class="header-row">
          <div>
            <h1 class="collection-title">{{ detail.name }}</h1>
            <p v-if="detail.description" class="collection-description" dir="auto">{{ detail.description }}</p>
          </div>
          <div class="header-actions">
            <Tag severity="success">{{ detail.items.length }} {{ detail.items.length === 1 ? 'aya' : 'ayas' }}</Tag>
            <Button icon="pi pi-pencil" text rounded size="small" v-tooltip.top="'Edit name and description'" @click="startEdit" />
          </div>
        </div>
        <div v-else class="collection-form">
          <InputText v-model="formName" placeholder="Name" @keyup.enter="saveEdit" />
          <Textarea v-model="formDescription" rows="2" autoResize placeholder="Description" />
          <div class="form-actions">
            <Button label="Save" size="small" :disabled="!formName.trim()" @click="saveEdit" />
            <Button label="Cancel" size="small" text @click="editing = false" />
          </div>
        </div>
      </template>
    </Card>

    <Card v-if="notFound"><template #content>Collection not found.</template></Card>

    <div v-if="detail && detail.items.length === 0" class="empty-state">
      This collection is empty. Use the menu on any aya to add it here.
    </div>

    <div v-if="detail" class="collection-items">
      <div v-for="(item, index) in detail.items" :key="item.id" class="collection-item">
        <div class="item-toolbar">
          <span class="item-index en">{{ index + 1 }}</span>
          <span class="item-key en">{{ item.aya_key }}</span>
          <span class="toolbar-spacer"></span>
          <Button icon="pi pi-arrow-up" text rounded size="small" :disabled="index === 0" v-tooltip.top="'Move up'" @click="move(index, -1)" />
          <Button icon="pi pi-arrow-down" text rounded size="small" :disabled="index === detail.items.length - 1" v-tooltip.top="'Move down'" @click="move(index, 1)" />
          <Button icon="pi pi-comment" text rounded size="small" v-tooltip.top="item.note ? 'Edit note' : 'Add note'" @click="startNote(item)" />
          <Button icon="pi pi-times" severity="danger" text rounded size="small" v-tooltip.top="'Remove from collection'" @click="remove(item)" />
        </div>
        <aya-view v-if="texts[item.aya_key]" :aya="texts[item.aya_key]!" :display-surah-name="true" />
        <div v-else class="item-placeholder">Loading {{ item.aya_key }}...</div>
        <div v-if="noteEditingId === item.id" class="item-note item-note-edit">
          <MarkdownNote v-model="noteText" mode="edit" :rows="3" placeholder="Why is this aya here?" />
          <div class="form-actions">
            <Button label="Save" size="small" @click="saveNote(item)" />
            <Button label="Cancel" size="small" text @click="noteEditingId = null" />
          </div>
        </div>
        <div v-else-if="item.note" class="item-note">
          <MarkdownNote :modelValue="item.note" mode="display" />
        </div>
      </div>
      <div v-if="detail.items.length > loadedCount" class="show-more">
        <Button :label="`Load texts for the next ${Math.min(PAGE, detail.items.length - loadedCount)} ayas`" outlined :loading="loading" @click="loadTexts(loadedCount)" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import Button from 'primevue/button';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Tag from 'primevue/tag';
import Textarea from 'primevue/textarea';
import AyaView from '../components/AyaView.vue';
import MarkdownNote from '../components/MarkdownNote.vue';
import { useStore } from '../store';
import type { AyaInfo, AyaPage, CollectionDetail, CollectionItem } from '../type_defs';

const PAGE = 50;
const props = defineProps<{ id: number }>();
const store = useStore();
const detail = ref<CollectionDetail | null>(null);
const notFound = ref(false);
const texts = ref<Record<string, AyaInfo>>({});
const loadedCount = ref(0);
const loading = ref(false);
const editing = ref(false);
const formName = ref('');
const formDescription = ref('');
const noteEditingId = ref<number | null>(null);
const noteText = ref('');

const apiBase = () => import.meta.env.VITE_API_BASE_URL || '/api/v1';

async function load() {
  detail.value = null;
  notFound.value = false;
  texts.value = {};
  loadedCount.value = 0;
  try {
    const resp = await fetch(`${apiBase()}/collections/${props.id}`, { credentials: 'include' });
    if (resp.status === 404 || resp.status === 401) {
      notFound.value = true;
      return;
    }
    detail.value = await resp.json();
    await loadTexts(0);
  } catch (error) {
    console.error('Failed to load collection:', error);
  }
}

// Texts come from the paged ayas endpoint so the selected translations apply
async function loadTexts(offset: number) {
  if (!detail.value) return;
  loading.value = true;
  try {
    const resp = await fetch(
      `${apiBase()}/collections/${props.id}/ayas?languages=${encodeURIComponent(store.textLanguagesSpec)}&offset=${offset}&limit=${PAGE}`,
      { credentials: 'include' }
    );
    if (!resp.ok) return;
    const page: AyaPage = await resp.json();
    for (const aya of page.ayas) texts.value[aya.aya_key] = aya;
    loadedCount.value = Math.max(loadedCount.value, offset + PAGE);
  } catch (error) {
    console.error('Failed to load collection texts:', error);
  } finally {
    loading.value = false;
  }
}

function startEdit() {
  if (!detail.value) return;
  formName.value = detail.value.name;
  formDescription.value = detail.value.description;
  editing.value = true;
}

async function saveEdit() {
  if (!detail.value || !formName.value.trim()) return;
  const updated = await store.updateCollection(detail.value.id, {
    name: formName.value.trim(),
    description: formDescription.value,
  });
  if (updated) {
    detail.value.name = updated.name;
    detail.value.description = updated.description;
    editing.value = false;
  }
}

async function move(index: number, delta: number) {
  if (!detail.value) return;
  const ids = detail.value.items.map((i) => i.id);
  const target = index + delta;
  if (target < 0 || target >= ids.length) return;
  [ids[index], ids[target]] = [ids[target]!, ids[index]!];
  try {
    const resp = await fetch(`${apiBase()}/collections/${props.id}/order`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ item_ids: ids }),
    });
    if (resp.ok) detail.value = await resp.json();
  } catch (error) {
    console.error('Failed to reorder collection:', error);
  }
}

async function remove(item: CollectionItem) {
  if (!detail.value) return;
  const ok = await store.removeAyaFromCollection(detail.value.id, item.aya_key);
  if (ok) detail.value.items = detail.value.items.filter((i) => i.id !== item.id);
}

function startNote(item: CollectionItem) {
  noteEditingId.value = item.id;
  noteText.value = item.note;
}

async function saveNote(item: CollectionItem) {
  try {
    const resp = await fetch(`${apiBase()}/collections/${props.id}/items/${item.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ note: noteText.value.trim() }),
    });
    if (resp.ok) {
      const updated: CollectionItem = await resp.json();
      item.note = updated.note;
      noteEditingId.value = null;
    }
  } catch (error) {
    console.error('Failed to save note:', error);
  }
}

watch(() => props.id, load, { immediate: true });
watch(() => store.textLanguagesSpec, () => {
  texts.value = {};
  const wanted = loadedCount.value;
  loadedCount.value = 0;
  for (let offset = 0; offset < Math.max(wanted, 1); offset += PAGE) loadTexts(offset);
});
</script>

<style scoped>
.collection-view {
  max-width: 1200px;
  margin: 0 auto;
}

.collection-header {
  margin-bottom: 1rem;
}

.header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.collection-title {
  margin: 0;
  font-size: 1.5rem;
  color: var(--p-primary-color);
}

.collection-description {
  margin: 0.5rem 0 0;
  color: var(--p-text-muted-color);
  white-space: pre-line;
}

.collection-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.empty-state {
  color: var(--p-text-muted-color);
  font-style: italic;
  padding: 1rem 0;
}

.collection-item {
  margin-bottom: 0.5rem;
}

.item-toolbar {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0 0.25rem;
  margin-top: 1rem;
  font-size: 0.8rem;
  color: var(--p-text-muted-color);
}

.item-index {
  font-weight: 600;
  min-width: 1.5rem;
}

.toolbar-spacer {
  flex: 1;
}

.item-placeholder {
  padding: 1rem;
  color: var(--p-text-muted-color);
}

.item-note {
  margin: -0.5rem 0 0.5rem;
  padding: 0.5rem 1rem;
  border-left: 3px solid var(--p-primary-color, #4caf50);
}

.item-note-edit {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.show-more {
  display: flex;
  justify-content: center;
  margin: 1rem 0;
}

.en {
  direction: ltr;
}
</style>
