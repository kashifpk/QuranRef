<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.surah-view-component {
  text-align: right;
  
}
</style>

<template>
  <div class="surah-view-component">
    <arabic-text-type-select v-model="selectedTextType" @text-type-changed="getSurahText()"></arabic-text-type-select>
    <br />
    <div class="row ar" v-for="aya in surahAyas">
      {{ aya }}
    </div>
  </div>
</template>

<script>
import appConfig from '../lib/config'
import ArabicTextTypeSelect from './ArabicTextTypeSelect'

export default {
  name: 'SurahView',
  data () {
    return {
      selectedTextType: '',
      surahAyas: []
    }
  },
  mounted () {
    this.selectedTextType = this.$store.getters.arabicTextType
    this.getSurahText()
  },
  components: {
    ArabicTextTypeSelect
  },
  methods: {
    getSurahText () {
      let env = appConfig.getEnvConfig(process.env.NODE_ENV)

      let requestURL = env.API_URL + '/qref/' + this.selectedTextType +
        '/' + this.$route.params.surah_number

      console.log(requestURL)
      this.axios.get(requestURL).then((response) => {
        console.log(response)
        this.surahAyas = response.data.ayas
      })
      .catch((error) => {
        console.log(error)
      })
    }
  }
}
</script>

