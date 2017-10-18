<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.word-ayas-component {
  
}
</style>

<template>
  <div class="panel panel-success col-xs-12 word-ayas-component">
    <div class="panel-heading ar" @click="getAyas()">
      <h3 class="panel-title ar">
        <span class="badge en">{{word.count}}</span>
        &nbsp;&nbsp;&nbsp;
        {{ word.word }}
      </h3>
    </div>
    <div class="panel-body bg-info" v-if="wordAyas.length > 0">
      <div class="row ar" v-for="aya in wordAyas">
        <aya-view :aya="aya" :display-surah-name="true"></aya-view>
      </div>
    </div>
  </div>
</template>

<script>
import appConfig from '../lib/config'
import AyaView from './AyaView'

export default {
  name: 'WordAyas',
  props: {
    word: {
      type: Object,
      required: true
    }
  },
  components: {
    AyaView
  },
  data () {
    return {
      wordAyas: []
    }
  },
  watch: {
    '$store.getters.arabicTextType': function (newVal, oldVal) { // watch it
      this.wordAyas = []
      this.getAyas()
    },
    '$store.state.selectedTranslations': function (newVal, oldVal) { // watch it
      this.wordAyas = []
      this.getAyas()
    }
  },
  methods: {
    getAyas () {
      if (this.wordAyas.length === 0) {
        let env = appConfig.getEnvConfig(process.env.NODE_ENV)
        let requestURL = env.API_URL + '/ayas_by_word/' + this.word.word + '/arabic,' +
                         this.$store.getters.arabicTextType

        let trStr = this.$store.getters.selectedTranslationsString
        if (trStr) {
          requestURL += '_' + trStr
        }

        console.log(requestURL)
        this.axios.get(requestURL).then((response) => {
          console.log(response)
          this.wordAyas = response.data
        })
        .catch((error) => {
          console.log(error)
        })
      }
    }
  }
}
</script>

