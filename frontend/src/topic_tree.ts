import type { TopicSummary } from './type_defs'

export interface TopicNode {
  key: string
  label: string
  data: TopicSummary
  children?: TopicNode[]
  leaf?: boolean
}

export type Hierarchy = 'thematic' | 'ontology'

const PARENT_FIELD: Record<Hierarchy, keyof TopicSummary> = {
  thematic: 'thematic_parent_id',
  ontology: 'ontology_parent_id',
}

/** Build PrimeVue Tree nodes for one hierarchy from the flat topic list. */
export function buildTopicTree(topics: TopicSummary[], hierarchy: Hierarchy): TopicNode[] {
  const field = PARENT_FIELD[hierarchy]
  const members = topics.filter((t) => t[hierarchy] || t[field])
  const ids = new Set(members.map((t) => t.id))
  const nodes = new Map<string, TopicNode>()
  for (const t of members) {
    nodes.set(t.id, { key: t.id, label: t.name, data: t, children: [] })
  }
  const roots: TopicNode[] = []
  for (const t of members) {
    const node = nodes.get(t.id)!
    const parent = t[field] as string | null
    if (parent && ids.has(parent) && parent !== t.id) {
      nodes.get(parent)!.children!.push(node)
    } else {
      roots.push(node)
    }
  }
  const sortNodes = (list: TopicNode[]) => {
    list.sort((a, b) => a.label.localeCompare(b.label))
    for (const n of list) {
      if (n.children && n.children.length > 0) sortNodes(n.children)
      else {
        delete n.children
        n.leaf = true
      }
    }
  }
  sortNodes(roots)
  return roots
}

/** Case-insensitive match on the English or Arabic name. */
export function matchesTopic(topic: TopicSummary, query: string): boolean {
  const q = query.trim().toLowerCase()
  if (!q) return true
  return topic.name.toLowerCase().includes(q) || (topic.arabic_name || '').includes(q)
}
