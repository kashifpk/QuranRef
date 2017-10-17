<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.browse-by-word-component {
  
  
}

.letters_list, words_list {
  font-size: 30pt;
  font-weight: bold;
}

.btn {
  margin: 2px;
  padding: 10px;
  min-width: 50px;
  font-weight: bold;
  font-size: 14pt;
  text-align: center;
}
</style>

<template>
  <div class="browse-by-word-component">
    <div class="row">
      <div class="col-xs-12 letters_list ar" style="text-align: left;">
        <button class="ar btn"
                v-for="letter in letters"
                :class="{ 'btn-success': letter===selectedLetter, 'btn-default': letter!==selectedLetter }"
                @click="getWords(letter)">
          {{ letter }}
        </button>
      </div>
    </div>
    
    
    <div class="words_list ar" style="text-align: left;">
      <div class="row" v-for="word in words">
        <div class="panel panel-success col-xs-12">
          <div class="panel-heading ar" @click="getAyas(word)">
            <h3 class="panel-title">{{ word }}</h3>
          </div>
          <div class="panel-body bg-info" v-if="wordAyas[word]">
            <div class="row ar" v-for="aya in wordAyas[word]">
              <aya-view :aya="aya" :display-surah-name="true"></aya-view>
              <!--<div class="col-xs-2 ar">
                ({{ aya.aya_number.split('-')[1] }})  {{ aya.surah.arabic_name }} 
              </div>
              <div class="col-xs-2">
                {{ aya.surah.english_name  }} ({{ aya.aya_number.split('-')[1] }})
              </div>-->
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import appConfig from '../lib/config'
import AyaView from './AyaView'

export default {
  name: 'BrowseByWord',
  components: {
    AyaView
  },
  data () {
    return {
      letters: [],
      selectedLetter: '',
      words: [],
      selectedWord: '',
      wordAyas: {}
    }
  },
  mounted () {
    this.getLetters()
  },
  watch: {
    '$store.getters.arabicTextType': function (newVal, oldVal) { // watch it
      this.wordAyas = {}
      this.getAyas(this.selectedWord)
    },
    '$store.state.selectedTranslations': function (newVal, oldVal) { // watch it
      this.wordAyas = {}
      this.getAyas(this.selectedWord)
    }
  },
  methods: {
    getLetters () {
      let env = appConfig.getEnvConfig(process.env.NODE_ENV)
      let requestURL = env.API_URL + '/letters'
      console.log(requestURL)
      this.axios.get(requestURL).then((response) => {
        console.log(response)
        this.letters = response.data
      })
      .catch((error) => {
        console.log(error)
      })
    },
    getWords (letter) {
      this.selectedLetter = letter

      let env = appConfig.getEnvConfig(process.env.NODE_ENV)
      let requestURL = env.API_URL + '/words_by_letter/' + letter
      console.log(requestURL)
      this.axios.get(requestURL).then((response) => {
        console.log(response)
        this.words = response.data
      })
      .catch((error) => {
        console.log(error)
      })
    },
    getAyas (word) {
      this.selectedWord = word
      console.log(word)

      if (!this.wordAyas[word]) {
        let env = appConfig.getEnvConfig(process.env.NODE_ENV)
        let requestURL = env.API_URL + '/ayas_by_word/' + word + '/arabic,' +
                         this.$store.getters.arabicTextType

        let trStr = this.$store.getters.selectedTranslationsString
        if (trStr) {
          requestURL += '_' + trStr
        }

        console.log(requestURL)
        this.axios.get(requestURL).then((response) => {
          console.log(response)
          this.$set(this.wordAyas, word, response.data)
        })
        .catch((error) => {
          console.log(error)
        })
      }
    }
  }
}
</script>

