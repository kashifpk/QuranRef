<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.search-results-component {
  text-align: right;
}


</style>

<template>
  <div class="search-results-component">
    <br />
    <div class="row" v-for="sr in searchResults">
      <div class="col-xs-8 ar">
        <aya-view :search-term="$route.params.search_term" :texts="sr.texts"></aya-view>
      </div>
      <div class="col-xs-2 ar">
        ({{ sr.aya_number.split('-')[1] }})  {{ sr.surah.arabic_name  }} 
      </div>
      <div class="col-xs-2">
        {{ sr.surah.english_name  }} ({{ sr.aya_number.split('-')[1] }})
      </div>
      
    </div>
    
  </div>
</template>

<script>
import appConfig from '../lib/config'
import AyaView from './AyaView'

export default {
  name: 'SearchResults',
  components: {
    AyaView
  },
  data () {
    return {
      searchResults: []
    }
  },
  mounted () {
    this.getSearchResults()
  },
  methods: {
    getSearchResults () {
      // http://127.0.0.1:6543/api/search/جبار/uthmani
      let env = appConfig.getEnvConfig(process.env.NODE_ENV)
      let requestURL = env.API_URL + '/search/' + this.$route.params.search_term + '/' +
                       this.$store.getters.arabicTextType

      console.log(requestURL)
      this.axios.get(requestURL).then((response) => {
        console.log(response.data)
        this.searchResults = response.data
      })
      .catch((error) => {
        console.log(error)
      })
    }
  }
}
</script>

