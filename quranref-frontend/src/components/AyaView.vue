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

.aya-content {
  margin-top: 5px;
  padding: 5px;
}
</style>

<template>
  <div class="aya-view-component col-xs-12">
    <div class="row">
    
      <div class="col-xs-12 col-md-3 col-lg-2 pull-right">
        <span class="badge en" v-if="!displaySurahName">
          {{ ayaNumber }}
        </span>
        
        <span class="btn btn-primary" v-if="displaySurahName">
          <span class="badge badge-primary en">{{ ayaNumber }}</span>
          &nbsp;&nbsp;&nbsp;
          <span class="ar" style="font-size: 14pt;">{{ surah.arabic_name }}</span>
        </span>
      </div>
      <div class="col-xs-12 col-md-9 col-lg-10">
        <div class="row">
          <div :class="colSize" class="ar aya-content">
            {{ aya.texts.arabic[$store.getters.arabicTextType] }}
          </div>
          <div class="aya-content" :class="[colSize, trname[0]]" v-for="(trname, tridx) in $store.state.selectedTranslations">
            
            <span v-if="aya.texts[trname[0]] && aya.texts[trname[0]][trname[1]]">
              {{ aya.texts[trname[0]][trname[1]] }}
            </span>
            
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
      // console.log(this.surahNumber)
      // console.log(this.$store.getters.surahInfo[this.surahNumber])
      this.surah = this.$store.getters.surahInfo[this.surahNumber]
    },
    breakWords () {
      // console.log(this.texts)
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

