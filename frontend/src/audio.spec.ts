import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { ayaAudioUrl, DEFAULT_RECITER } from './audio'
import { useStore } from './store'

describe('ayaAudioUrl', () => {
  it('builds the everyayah path with zero padded numbers', () => {
    expect(ayaAudioUrl('Alafasy_128kbps', '2:255')).toBe(
      'https://everyayah.com/data/Alafasy_128kbps/002255.mp3'
    )
    expect(ayaAudioUrl('Husary_128kbps', '114:6')).toBe(
      'https://everyayah.com/data/Husary_128kbps/114006.mp3'
    )
  })

  it('has no file for the bismillah line stored as aya 0', () => {
    expect(ayaAudioUrl(DEFAULT_RECITER, '2:0')).toBeNull()
    expect(ayaAudioUrl(DEFAULT_RECITER, 'bad')).toBeNull()
  })
})

// A stand-in for the browser's Audio element that records what the store asks of it
class FakeAudio {
  static instances: FakeAudio[] = []
  src = ''
  preload = ''
  paused = true
  ended = false
  currentTime = 0
  listeners: Record<string, () => void> = {}
  constructor() {
    FakeAudio.instances.push(this)
  }
  addEventListener(type: string, fn: () => void) {
    this.listeners[type] = fn
  }
  play() {
    this.paused = false
    this.listeners.play?.()
    return Promise.resolve()
  }
  pause() {
    this.paused = true
    this.listeners.pause?.()
  }
  removeAttribute() {
    this.src = ''
  }
  load() {}
  finish() {
    this.ended = true
    this.paused = true
    this.listeners.pause?.()
    this.listeners.ended?.()
  }
}

describe('recitation player in the store', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    FakeAudio.instances = []
    vi.stubGlobal('Audio', FakeAudio)
  })
  afterEach(() => vi.unstubAllGlobals())

  it('plays an aya and advances through the playlist when a file ends', () => {
    const store = useStore()
    expect(store.playAya('1:1', ['1:1', '1:2', '1:3'])).toBe(true)
    const audio = FakeAudio.instances[0]!
    expect(audio.src).toContain('/001001.mp3')
    expect(store.audioCurrent).toBe('1:1')
    expect(store.audioPlaying).toBe(true)

    audio.finish()
    expect(store.audioCurrent).toBe('1:2')
    expect(audio.src).toContain('/001002.mp3')

    store.nextAya()
    expect(store.audioCurrent).toBe('1:3')
    audio.finish()
    expect(store.audioCurrent).toBeNull()
    expect(store.audioPlaying).toBe(false)
  })

  it('stops at the end of the aya when continuous play is off', () => {
    const store = useStore()
    store.audioContinuous = false
    store.playAya('1:1', ['1:1', '1:2'])
    FakeAudio.instances[0]!.finish()
    expect(store.audioCurrent).toBe('1:1')
    expect(store.audioPlaying).toBe(false)
  })

  it('toggles between pause and resume for the current aya', () => {
    const store = useStore()
    store.toggleAya('2:255')
    expect(store.audioPlaying).toBe(true)
    store.toggleAya('2:255')
    expect(store.audioPlaying).toBe(false)
    store.toggleAya('2:255')
    expect(store.audioPlaying).toBe(true)
    store.stopAudio()
    expect(store.audioCurrent).toBeNull()
  })

  it('refuses keys without a recording', () => {
    const store = useStore()
    expect(store.playAya('2:0')).toBe(false)
    expect(store.audioCurrent).toBeNull()
  })
})
