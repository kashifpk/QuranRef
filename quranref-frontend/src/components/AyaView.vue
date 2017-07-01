<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.aya-view-component {
  text-align: right;
}

.seached-text {}

</style>

<template>
  <div class="aya-view-component">
    <div class="ar" :class="[displaySurahName ? 'col-xs-8' : 'col-xs-11']">
      {{ aya.aya_text }}
    </div>
    
    <div class="col-xs-1">
      ({{ aya.aya_number.split('-')[1] }})
    </div>
    
    <div class="col-xs-3 ar" v-if="displaySurahName">
      {{ surah.arabic_name }} ({{ surah.english_name  }})
    </div>
    
  </div>
</template>

<script>
export default {
  name: 'AyaView',
  props: {
    aya: {
      type: Object,
      required: true
    },
    displaySurahName: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      textsWords: {},
      surah: {}
    }
  },
  mounted () {
    this.setSurah()
    this.breakWords()
  },
  methods: {
    setSurah () {
      let sn = this.aya.aya_number.split('-')[0]
      console.log(sn)
      console.log(this.$store.getters.surahInfo[sn])
      this.surah = this.$store.getters.surahInfo[sn]
    },
    breakWords () {
      console.log(this.texts)
      for (let textType in this.texts) {
        this.textsWords[textType] = this.texts[textType].split(' ')
      }
    },
    stripAraab (word) {
      let araab = ['ِ', 'ْ', 'َ', 'ُ', 'ّ', 'ٍ', 'ً', 'ٌ']
      let newWord = ''
      for (let i in word) {
        let ch = word[i]
        if (!araab.includes(ch)) {
          console.log(ch)
          newWord += ch
        }
      }

      return newWord
    }
  }
}
</script>

