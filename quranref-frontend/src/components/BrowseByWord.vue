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
        <button class="btn ar"
                v-for="letter in letters"
                :class="{ 'btn-success': letter===selectedLetter, 'btn-default': letter!==selectedLetter }"
                @click="getWords(letter)">
          {{ letter }}
        </button>
      </div>
    </div>
    
    <div class="words_list ar" style="text-align: left;">
      <div class="row" v-for="word in words">
        <word-ayas :word="{word: word[0], count: word[1]}" />
      </div>
    </div>
  </div>
</template>

<script>
import appConfig from '../lib/config'
import WordAyas from './WordAyas'

export default {
  name: 'BrowseByWord',
  components: {
    WordAyas
  },
  data () {
    return {
      letters: [],
      selectedLetter: '',
      words: []
    }
  },
  mounted () {
    this.getLetters()
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
    }
  }
}
</script>

