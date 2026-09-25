<template>
  <div class="topics-view">
    <Card>
      <template #title>Topics</template>
      <template #content>
        <p class="hint">
          Concepts of the Quran and the ayas about them, from the Quranic Universal Library.
          Browse the thematic or ontology tree, or search by name.
        </p>
        <IconField class="topic-search">
          <InputIcon class="pi pi-search" />
          <InputText v-model="query" placeholder="Search topics (English or Arabic)" />
        </IconField>

        <div v-if="query.trim()" class="search-results">
          <router-link
            v-for="t in matches"
            :key="t.id"
            :to="{ name: 'topic_view', params: { id: t.id } }"
            class="topic-row"
          >
            <span class="topic-name">{{ t.name }}</span>
            <span class="topic-arabic ar">{{ t.arabic_name }}</span>
            <Tag severity="secondary">{{ t.aya_count }}</Tag>
          </router-link>
          <p v-if="matches.length === 0" class="hint">No topic matches "{{ query }}".</p>
        </div>

        <Tabs v-else value="thematic">
          <TabList>
            <Tab value="thematic">Thematic</Tab>
            <Tab value="ontology">Ontology</Tab>
          </TabList>
          <TabPanels>
            <TabPanel v-for="h in hierarchies" :key="h" :value="h">
              <Tree
                :value="trees[h]"
                selectionMode="single"
                @node-select="openTopic"
                class="topic-tree"
              >
                <template #default="{ node }">
                  <span class="topic-name">{{ node.label }}</span>
                  <span class="topic-arabic ar">{{ node.data.arabic_name }}</span>
                  <Tag v-if="node.data.aya_count" severity="secondary" class="topic-count">{{ node.data.aya_count }}</Tag>
                </template>
              </Tree>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </template>
    </Card>
    <div v-if="store.topicsLoading" class="loading-state"><ProgressSpinner strokeWidth="4" /></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import Tag from 'primevue/tag';
import Tabs from 'primevue/tabs';
import TabList from 'primevue/tablist';
import Tab from 'primevue/tab';
import TabPanels from 'primevue/tabpanels';
import TabPanel from 'primevue/tabpanel';
import Tree from 'primevue/tree';
import InputText from 'primevue/inputtext';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import ProgressSpinner from 'primevue/progressspinner';
import { useStore } from '../store';
import type { TreeNode } from 'primevue/treenode';
import { buildTopicTree, matchesTopic, type Hierarchy, type TopicNode } from '../topic_tree';

const store = useStore();
const router = useRouter();
const query = ref('');
const hierarchies: Hierarchy[] = ['thematic', 'ontology'];

onMounted(() => {
  store.loadTopics();
});

const trees = computed<Record<Hierarchy, TopicNode[]>>(() => ({
  thematic: buildTopicTree(store.topics, 'thematic'),
  ontology: buildTopicTree(store.topics, 'ontology'),
}));

const matches = computed(() => store.topics.filter((t) => matchesTopic(t, query.value)).slice(0, 200));

function openTopic(node: TreeNode) {
  if (node.key) router.push({ name: 'topic_view', params: { id: String(node.key) } });
}
</script>

<style scoped>
.topics-view {
  max-width: 1000px;
  margin: 0 auto;
}

.hint {
  margin: 0 0 1rem;
  color: var(--p-text-muted-color, #666);
}

.topic-search {
  width: 100%;
  margin-bottom: 1rem;
}

.topic-search :deep(input) {
  width: 100%;
}

.search-results {
  display: flex;
  flex-direction: column;
}

.topic-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.4rem 0.5rem;
  border-radius: 6px;
  text-decoration: none;
  color: inherit;
}

.topic-row:hover {
  background: var(--p-content-hover-background, rgba(76, 175, 80, 0.08));
}

.topic-name {
  flex: 1;
}

.topic-arabic {
  color: var(--p-text-muted-color, #666);
  font-size: 1.1rem;
}

.topic-count {
  margin-left: 0.5rem;
}

.topic-tree :deep(.p-tree-node-content) {
  gap: 0.5rem;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.ar {
  direction: rtl;
}
</style>
