<template>
  <div class="topic-view">
    <Card v-if="topic">
      <template #content>
        <div class="topic-head">
          <div>
            <h1 class="topic-title">{{ topic.name }}</h1>
            <div class="topic-arabic ar">{{ topic.arabic_name }}</div>
          </div>
          <div class="topic-meta">
            <Tag severity="success">{{ topic.aya_count }} ayas</Tag>
            <Tag v-if="topic.thematic" severity="secondary">thematic</Tag>
            <Tag v-if="topic.ontology" severity="secondary">ontology</Tag>
            <a v-if="topic.wiki_link" :href="topic.wiki_link" target="_blank" rel="noopener" class="wiki-link">
              <i class="pi pi-external-link"></i> Wikipedia
            </a>
          </div>
        </div>
        <div v-if="topic.description" class="topic-description" v-html="topic.description" @click="handleLinkClick"></div>
        <div class="topic-links">
          <div v-if="topic.parents.length" class="topic-link-group">
            <span class="group-label">Part of</span>
            <router-link v-for="p in topic.parents" :key="p.id" :to="{ name: 'topic_view', params: { id: p.id } }" class="topic-chip">{{ p.name }}</router-link>
          </div>
          <div v-if="topic.children.length" class="topic-link-group">
            <span class="group-label">Subtopics</span>
            <router-link v-for="c in topic.children" :key="c.id" :to="{ name: 'topic_view', params: { id: c.id } }" class="topic-chip">
              {{ c.name }} <span class="chip-count" v-if="c.aya_count">{{ c.aya_count }}</span>
            </router-link>
          </div>
          <div v-if="topic.related.length" class="topic-link-group">
            <span class="group-label">Related</span>
            <router-link v-for="r in topic.related" :key="r.id" :to="{ name: 'topic_view', params: { id: r.id } }" class="topic-chip">{{ r.name }}</router-link>
          </div>
        </div>
      </template>
    </Card>
    <aya-paged-list v-if="topic && topic.aya_count > 0" :endpoint="`/topic/${id}/ayas`" />
    <Card v-if="notFound"><template #content>Topic not found.</template></Card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import Tag from 'primevue/tag';
import AyaPagedList from '../components/AyaPagedList.vue';
import type { TopicInfo } from '../type_defs';

const props = defineProps<{ id: string }>();
const router = useRouter();
const topic = ref<TopicInfo | null>(null);
const notFound = ref(false);

async function load() {
  topic.value = null;
  notFound.value = false;
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const resp = await fetch(`${baseUrl}/topic/${encodeURIComponent(props.id)}`);
    if (resp.status === 404) {
      notFound.value = true;
      return;
    }
    topic.value = await resp.json();
  } catch (error) {
    console.error('Failed to load topic:', error);
  }
}

// Cross-links inside the description are plain anchors; route them through the SPA
function handleLinkClick(event: MouseEvent) {
  const link = (event.target as HTMLElement).closest('a');
  const href = link?.getAttribute('href');
  if (href && href.startsWith('/topic/')) {
    event.preventDefault();
    router.push(href);
  }
}

watch(() => props.id, load, { immediate: true });
</script>

<style scoped>
.topic-view {
  max-width: 1200px;
  margin: 0 auto;
}

.topic-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}

.topic-title {
  margin: 0;
  font-size: 2rem;
}

.topic-arabic {
  font-size: 1.6rem;
  font-family: 'AlQalam', 'Amiri', 'Traditional Arabic', serif;
  color: var(--p-text-muted-color, #666);
}

.topic-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.wiki-link {
  color: var(--p-primary-color, #4caf50);
  text-decoration: none;
  font-size: 0.9rem;
}

.topic-description {
  margin-top: 1rem;
  line-height: 1.6;
}

.topic-description :deep(a.topic-link) {
  color: var(--p-primary-color, #4caf50);
  text-decoration: none;
}

.topic-description :deep(a.topic-link:hover) {
  text-decoration: underline;
}

.topic-description :deep(.ar) {
  direction: rtl;
  display: inline-block;
}

.topic-links {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.topic-link-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.group-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--p-text-muted-color, #666);
  margin-right: 0.25rem;
}

.topic-chip {
  padding: 0.25rem 0.6rem;
  border: 1px solid var(--p-content-border-color, #ddd);
  border-radius: 999px;
  text-decoration: none;
  color: inherit;
  font-size: 0.9rem;
}

.topic-chip:hover {
  border-color: var(--p-primary-color, #4caf50);
}

.chip-count {
  color: var(--p-text-muted-color, #666);
  font-size: 0.75rem;
}

.ar {
  direction: rtl;
}
</style>
