<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.surah-view-component {
  text-align: right;
  
}
</style>

<template>
  <div class="surah-view-component">
    <div class="row ar" v-for="aya in surahAyas">
      <aya-view :aya="aya"></aya-view>
    </div>
  </div>
</template>

<script>
import appConfig from '../lib/config'
import AyaView from './AyaView'

export default {
  name: 'SurahView',
  data () {
    return {
      surahAyas: []
    }
  },
  mounted () {
    this.getSurahText()
  },
  components: {
    AyaView
  },
  watch: {
    '$store.getters.arabicTextType': function (newVal, oldVal) { // watch it
      console.log('arabicTextType changed: ', newVal, ' | was: ', oldVal)
      this.getSurahText()
    }
  },
  methods: {
    getSurahText () {
      let env = appConfig.getEnvConfig(process.env.NODE_ENV)

      let requestURL = env.API_URL + '/qref/' + this.$route.params.surah_number +
        '/arabic,' + this.$store.getters.arabicTextType

      console.log(requestURL)
      this.axios.get(requestURL).then((response) => {
        console.log(response)
        this.surahAyas = response.data
      })
      .catch((error) => {
        console.log(error)
      })
    }
  }
}
</script>

