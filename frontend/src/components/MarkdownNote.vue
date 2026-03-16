<template>
  <!-- Display mode: rendered markdown only -->
  <div v-if="props.mode === 'display'" class="note-markdown" v-html="renderedHtml" @click="handleLinkClick"></div>

  <!-- Edit mode: Write/Preview tabs -->
  <div v-else class="markdown-editor">
    <div class="md-tabs">
      <button
        class="md-tab"
        :class="{ active: activeTab === 'write' }"
        @click="activeTab = 'write'"
      >Write</button>
      <button
        class="md-tab"
        :class="{ active: activeTab === 'preview' }"
        @click="activeTab = 'preview'"
      >Preview</button>
    </div>
    <div v-show="activeTab === 'write'" class="md-write">
      <textarea
        ref="textareaRef"
        class="md-textarea note-font"
        :value="modelValue"
        @input="onInput"
        :placeholder="placeholder"
        :rows="rows"
        dir="auto"
      ></textarea>
      <div class="md-hint">
        Markdown supported. Use <code>@surah:aya</code> to link verses.
      </div>
    </div>
    <div v-show="activeTab === 'preview'" class="md-preview">
      <div
        v-if="modelValue.trim()"
        class="note-markdown"
        v-html="renderedHtml"
        @click="handleLinkClick"
      ></div>
      <div v-else class="md-empty-preview">Nothing to preview</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import MarkdownIt from 'markdown-it';
import type Token from 'markdown-it/lib/token.mjs';

interface Props {
  modelValue: string;
  mode: 'edit' | 'display';
  placeholder?: string;
  rows?: number;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Write your note...',
  rows: 4,
});

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

const router = useRouter();
const activeTab = ref<'write' | 'preview'>('write');
const textareaRef = ref<HTMLTextAreaElement>();

// Initialize markdown-it
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
});

// Plugin: convert @surah:aya references to links
function ayaRefPlugin(mdi: MarkdownIt) {
  // Match @1:7, @2:255, @114:6 etc.
  const AYA_REF_RE = /@(\d{1,3}):(\d{1,3})/g;

  mdi.core.ruler.after('linkify', 'aya_ref', (state) => {
    for (const blockToken of state.tokens) {
      if (blockToken.type !== 'inline' || !blockToken.children) continue;

      const newChildren: Token[] = [];

      for (const token of blockToken.children) {
        if (token.type !== 'text' || !AYA_REF_RE.test(token.content)) {
          newChildren.push(token);
          continue;
        }

        // Split text by aya references
        let lastIndex = 0;
        const content = token.content;
        AYA_REF_RE.lastIndex = 0;
        let match: RegExpExecArray | null;

        while ((match = AYA_REF_RE.exec(content)) !== null) {
          const [fullMatch, surah, aya] = match;

          // Text before the match
          if (match.index > lastIndex) {
            const textToken = new state.Token('text', '', 0);
            textToken.content = content.slice(lastIndex, match.index);
            newChildren.push(textToken);
          }

          // Opening link tag
          const openToken = new state.Token('link_open', 'a', 1);
          openToken.attrSet('href', `/surah/${surah}?aya=${aya}`);
          openToken.attrSet('class', 'aya-ref-link');
          newChildren.push(openToken);

          // Link text
          const linkText = new state.Token('text', '', 0);
          linkText.content = `${surah}:${aya}`;
          newChildren.push(linkText);

          // Closing link tag
          const closeToken = new state.Token('link_close', 'a', -1);
          newChildren.push(closeToken);

          lastIndex = match.index + fullMatch.length;
        }

        // Remaining text after last match
        if (lastIndex < content.length) {
          const textToken = new state.Token('text', '', 0);
          textToken.content = content.slice(lastIndex);
          newChildren.push(textToken);
        }
      }

      blockToken.children = newChildren;
    }
  });
}

// Plugin: add dir="auto" to paragraph and list item tags
function bidiPlugin(mdi: MarkdownIt) {
  const proxy = (tokens: Token[], idx: number, options: object, _env: unknown, self: { renderToken: (t: Token[], i: number, o: object) => string }) =>
    self.renderToken(tokens, idx, options);

  const defaultParagraphOpen = mdi.renderer.rules.paragraph_open || proxy;

  mdi.renderer.rules.paragraph_open = function(tokens, idx, options, env, self) {
    tokens[idx].attrSet('dir', 'auto');
    return defaultParagraphOpen(tokens, idx, options, env, self);
  };

  const defaultListItemOpen = mdi.renderer.rules.list_item_open || proxy;

  mdi.renderer.rules.list_item_open = function(tokens, idx, options, env, self) {
    tokens[idx].attrSet('dir', 'auto');
    return defaultListItemOpen(tokens, idx, options, env, self);
  };
}

md.use(ayaRefPlugin);
md.use(bidiPlugin);

const renderedHtml = computed(() => {
  return md.render(props.modelValue || '');
});

function onInput(event: Event) {
  const target = event.target as HTMLTextAreaElement;
  emit('update:modelValue', target.value);
}

function handleLinkClick(event: MouseEvent) {
  const target = event.target as HTMLElement;
  const link = target.closest('a');
  if (!link) return;

  const href = link.getAttribute('href');
  if (!href) return;

  // Handle internal aya-ref-link clicks via SPA navigation
  if (link.classList.contains('aya-ref-link') || href.startsWith('/surah/')) {
    event.preventDefault();
    router.push(href);
    return;
  }

  // External links: open in new tab
  if (href.startsWith('http://') || href.startsWith('https://')) {
    event.preventDefault();
    window.open(href, '_blank', 'noopener');
  }
}

function focus() {
  nextTick(() => textareaRef.value?.focus());
}

onMounted(() => {
  if (props.mode === 'edit') {
    focus();
  }
});

defineExpose({ focus });
</script>

<style scoped>
.markdown-editor {
  width: 100%;
}

.md-tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--p-content-border-color, #ddd);
  margin-bottom: 0.5rem;
}

.md-tab {
  padding: 0.375rem 0.75rem;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.8125rem;
  color: var(--p-text-muted-color, #666);
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}

.md-tab:hover {
  color: var(--p-text-color);
}

.md-tab.active {
  color: var(--p-primary-color, #4CAF50);
  border-bottom-color: var(--p-primary-color, #4CAF50);
}

.md-write {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.md-textarea {
  width: 100%;
  min-height: 80px;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--p-content-border-color, #ddd);
  border-radius: var(--p-content-border-radius, 6px);
  background: var(--p-form-field-background, #fff);
  color: var(--p-text-color);
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.md-textarea:focus {
  border-color: var(--p-primary-color, #4CAF50);
}

.md-hint {
  font-size: 0.7rem;
  color: var(--p-text-muted-color, #999);
}

.md-hint code {
  font-size: 0.7rem;
  background: rgba(0, 0, 0, 0.06);
  padding: 1px 3px;
  border-radius: 2px;
}

.dark-mode .md-hint code {
  background: rgba(255, 255, 255, 0.1);
}

.md-preview {
  min-height: 80px;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--p-content-border-color, #ddd);
  border-radius: var(--p-content-border-radius, 6px);
  background: var(--p-form-field-background, #fff);
}

.md-empty-preview {
  color: var(--p-text-muted-color, #999);
  font-style: italic;
  font-size: 0.875rem;
}
</style>
