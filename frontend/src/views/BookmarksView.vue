<template>
  <div class="bookmarks-view">
    <h2>My Bookmarks</h2>

    <!-- Not logged in -->
    <div v-if="!store.currentUser" class="auth-prompt">
      <i class="pi pi-lock" style="font-size: 2rem; color: #999;"></i>
      <p>Please sign in to view your bookmarks.</p>
      <Button label="Sign In" icon="pi pi-sign-in" @click="store.login" />
    </div>

    <template v-else>
      <!-- Loading state -->
      <div v-if="store.bookmarksLoading" class="loading-state">
        <i class="pi pi-spin pi-spinner" style="font-size: 1.5rem;"></i>
        <span>Loading bookmarks...</span>
      </div>

      <template v-else>
        <!-- Reading Position Section -->
        <div class="bookmark-section">
          <h3><i class="pi pi-bookmark-fill" style="color: #4CAF50;"></i> Reading Position</h3>
          <Card v-if="store.readingBookmark" class="bookmark-card">
            <template #content>
              <div class="bookmark-card-content">
                <div class="bookmark-info">
                  <span class="aya-ref en">{{ store.readingBookmark.aya_key }}</span>
                  <span class="surah-name" v-if="readingSurahName"> — {{ readingSurahName }}</span>
                </div>
                <div class="bookmark-actions">
                  <Button
                    label="Resume Reading"
                    icon="pi pi-arrow-right"
                    size="small"
                    @click="navigateToReading"
                  />
                  <Button
                    icon="pi pi-trash"
                    severity="danger"
                    text
                    rounded
                    size="small"
                    @click="store.deleteReadingBookmark()"
                    v-tooltip.top="'Remove'"
                  />
                </div>
              </div>
            </template>
          </Card>
          <p v-else class="empty-state">No reading position set. Use the menu on any aya to set one.</p>
        </div>

        <!-- Note Bookmarks Section -->
        <div class="bookmark-section">
          <h3><i class="pi pi-file-edit" style="color: #FF9800;"></i> Note Bookmarks</h3>
          <div v-if="store.noteBookmarks.length > 0" class="notes-list">
            <Card
              v-for="note in store.noteBookmarks"
              :key="note.id"
              class="bookmark-card note-card"
            >
              <template #content>
                <div class="note-card-content">
                  <div class="note-header">
                    <div class="bookmark-info">
                      <span class="aya-ref en">{{ note.aya_key }}</span>
                      <span class="surah-name" v-if="getSurahName(note.aya_key)">
                        — {{ getSurahName(note.aya_key) }}
                      </span>
                    </div>
                    <span class="note-date en">{{ formatDate(note.created_at) }}</span>
                  </div>

                  <!-- Editing mode -->
                  <div v-if="editingNoteId === note.id" class="note-edit">
                    <Textarea
                      v-model="editNoteText"
                      rows="3"
                      class="note-edit-textarea"
                    />
                    <div class="note-edit-actions">
                      <Button label="Save" size="small" @click="saveNoteEdit(note.id)" :disabled="!editNoteText.trim()" />
                      <Button label="Cancel" size="small" text @click="cancelNoteEdit" />
                    </div>
                  </div>

                  <!-- Display mode -->
                  <p v-else class="note-text">{{ note.note }}</p>

                  <div class="note-actions" v-if="editingNoteId !== note.id">
                    <Button
                      icon="pi pi-arrow-right"
                      text
                      rounded
                      size="small"
                      @click="navigateToAya(note.aya_key)"
                      v-tooltip.top="'Go to aya'"
                    />
                    <Button
                      icon="pi pi-pencil"
                      text
                      rounded
                      size="small"
                      @click="startNoteEdit(note)"
                      v-tooltip.top="'Edit'"
                    />
                    <Button
                      icon="pi pi-trash"
                      severity="danger"
                      text
                      rounded
                      size="small"
                      @click="store.deleteNoteBookmark(note.id)"
                      v-tooltip.top="'Delete'"
                    />
                  </div>
                </div>
              </template>
            </Card>
          </div>
          <p v-else class="empty-state">No notes yet. Use the menu on any aya to add one.</p>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from '../store';
import type { Bookmark } from '../type_defs';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Textarea from 'primevue/textarea';

const store = useStore();
const router = useRouter();
const editingNoteId = ref<number | null>(null);
const editNoteText = ref('');

const readingSurahName = computed(() => {
  if (!store.readingBookmark) return '';
  return getSurahName(store.readingBookmark.aya_key);
});

function getSurahName(ayaKey: string): string {
  const surahNum = parseInt(ayaKey.split(':')[0]);
  const surah = store.surahInfo[surahNum - 1];
  return surah ? surah.english_name : '';
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function navigateToReading() {
  if (store.readingBookmark) {
    navigateToAya(store.readingBookmark.aya_key);
  }
}

function navigateToAya(ayaKey: string) {
  const [surahNum, ayaNum] = ayaKey.split(':');
  router.push({ name: 'surah_view', params: { surah_number: surahNum }, query: { aya: ayaNum } });
}

function startNoteEdit(note: Bookmark) {
  editingNoteId.value = note.id;
  editNoteText.value = note.note;
}

function cancelNoteEdit() {
  editingNoteId.value = null;
  editNoteText.value = '';
}

async function saveNoteEdit(noteId: number) {
  if (editNoteText.value.trim()) {
    await store.updateNoteBookmark(noteId, editNoteText.value.trim());
    editingNoteId.value = null;
    editNoteText.value = '';
  }
}
</script>

<style scoped>
.bookmarks-view {
  max-width: 800px;
  margin: 0 auto;
}

.bookmarks-view h2 {
  margin-bottom: 1.5rem;
  color: var(--p-text-color);
}

.bookmarks-view h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
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

.loading-state {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem;
  justify-content: center;
  color: var(--p-text-muted-color);
}

.bookmark-section {
  margin-bottom: 2rem;
}

.bookmark-card {
  margin-bottom: 0.75rem;
}

.bookmark-card-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.bookmark-info {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.aya-ref {
  font-weight: 600;
  color: var(--p-primary-color);
  font-size: 1rem;
}

.surah-name {
  color: var(--p-text-muted-color);
  font-size: 0.875rem;
}

.bookmark-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.note-card-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.note-date {
  color: var(--p-text-muted-color);
  font-size: 0.75rem;
}

.note-text {
  margin: 0;
  color: var(--p-text-color);
  line-height: 1.5;
}

.note-actions {
  display: flex;
  gap: 0.25rem;
  justify-content: flex-end;
}

.note-edit {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.note-edit-textarea {
  width: 100%;
}

.note-edit-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.empty-state {
  color: var(--p-text-muted-color);
  font-style: italic;
  padding: 1rem 0;
}

/* Remove extra card padding */
.bookmark-card :deep(.p-card-body) {
  padding: 0.75rem 1rem;
}

.bookmark-card :deep(.p-card-content) {
  padding: 0;
}
</style>
