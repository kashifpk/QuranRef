<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.aya-view-component {
  padding: 10px 15px;
}

.seached-text {
  
}

.surah-en {
  font-size: 11pt;
}

.en-num {
  font-size: 11pt;
  vertical-align: bottom;
  padding-top: 10px;
}

.col-sm-6, col-lg-6, col-lg-4 {
  float: right;
}
</style>

<template>
  <div class="aya-view-component col-xs-12">
    <div class="row">
      <div :class="colSize">
        <div class="row">
          <div class="ar" :class="[displaySurahName ? 'col-xs-8' : 'col-xs-10']">
            {{ aya.texts.arabic[$store.getters.arabicTextType] }}
          </div>
          
          <div class="col-xs-1 en en-num">
            ({{ ayaNumber }})
          </div>
          
          <div class="col-xs-2 ar" v-if="displaySurahName">
            {{ surah.arabic_name }}
            <span class="hidden-xs hidden-sm hidden-md en surah-en">
              ({{ surah.english_name  }})
            </span>
          </div>
          
          <div class="col-xs-1 en en-num" v-if="displaySurahName">
            <strong>{{ surahNumber }}</strong>
          </div>
        </div>
      </div>
      <div :class="colSize" v-for="(trname, tridx) in $store.state.selectedTranslations">
        <div class="row">
          <div class="col-xs-12" :class="trname[0]">
            {{ aya.texts[trname[0]][trname[1]] }}
          </div>
        </div>
      </div>
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
      arabicDigits: {
        '0': '٠',
        '1': '١',
        '2': '٢',
        '3': '٣',
        '4': '٤',
        '5': '٥',
        '6': '٦',
        '7': '٧',
        '8': '٨',
        '9': '٩'
      },
      textsWords: {},
      surah: {},
      surahNumber: '',
      ayaNumber: ''
    }
  },
  mounted () {
    this.setSurah()
    this.breakWords()
  },
  computed: {
    colSize () {
      let trNum = this.$store.state.selectedTranslations.length
      return {
        'col-xs-12': true,
        'col-sm-12': trNum === 0,
        'col-sm-6': trNum > 0,
        'col-lg-12': trNum === 0,
        'col-lg-6': trNum === 1,
        'col-lg-4': trNum > 1
      }
    }
  },
  methods: {
    setSurah () {
      let parts = this.aya.aya_number.split('-')
      this.surahNumber = parts[0]
      this.ayaNumber = parts[1]
      console.log(this.surahNumber)
      console.log(this.$store.getters.surahInfo[this.surahNumber])
      this.surah = this.$store.getters.surahInfo[this.surahNumber]
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

