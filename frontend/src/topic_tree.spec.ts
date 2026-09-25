import { describe, expect, it } from 'vitest'
import { buildTopicTree, matchesTopic } from './topic_tree'
import type { TopicSummary } from './type_defs'

const topic = (over: Partial<TopicSummary>): TopicSummary => ({
  id: '0', name: '', arabic_name: '', aya_count: 0, thematic: false, ontology: false,
  parent_id: null, thematic_parent_id: null, ontology_parent_id: null, ...over,
})

const topics: TopicSummary[] = [
  topic({ id: '3', name: 'Doctrine', thematic: true }),
  topic({ id: '2', name: 'Mercy', arabic_name: 'رحمة', thematic: true, thematic_parent_id: '3' }),
  topic({ id: '1', name: 'Allah', arabic_name: 'الله', ontology: true, ontology_parent_id: '9' }),
  topic({ id: '9', name: 'Unseen', ontology: true }),
  topic({ id: '5', name: 'Belief', thematic: true, thematic_parent_id: '3' }),
]

describe('buildTopicTree', () => {
  it('builds the thematic tree with sorted children and leaf flags', () => {
    const tree = buildTopicTree(topics, 'thematic')
    expect(tree.map((n) => n.label)).toEqual(['Doctrine'])
    expect(tree[0].children!.map((n) => n.label)).toEqual(['Belief', 'Mercy'])
    expect(tree[0].children![0].leaf).toBe(true)
    expect(tree[0].children![0].children).toBeUndefined()
  })

  it('keeps the hierarchies apart', () => {
    const tree = buildTopicTree(topics, 'ontology')
    expect(tree.map((n) => n.label)).toEqual(['Unseen'])
    expect(tree[0].children!.map((n) => n.data.id)).toEqual(['1'])
  })
})

describe('matchesTopic', () => {
  it('matches English and Arabic names, ignoring case and blank queries', () => {
    expect(matchesTopic(topics[1], 'MER')).toBe(true)
    expect(matchesTopic(topics[1], 'رحم')).toBe(true)
    expect(matchesTopic(topics[1], 'zzz')).toBe(false)
    expect(matchesTopic(topics[1], '  ')).toBe(true)
  })
})
