<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.search-results-component {
  text-align: right;
}


</style>

<template>
  <div class="search-results-component">
    <br />
    <div class="row" v-for="aya in searchResults">
      <aya-view :aya="aya" :display-surah-name="true"></aya-view>
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
        this.searchResults = response.data
      })
      .catch((error) => {
        console.log(error)
      })
    }
  }
}
</script>

