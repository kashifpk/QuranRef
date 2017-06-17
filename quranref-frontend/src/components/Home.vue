<template>
  <div class="home-component">
    <div class="row">
      <div class="col-xs-12 col-sm-12 col-md-6 col-lg-4">
        <search-box></search-box>
      </div>
      <div class="col-xs-12 col-sm-12 col-md-6 col-lg-4">
        <arabic-text-type-select></arabic-text-type-select>
      </div>
      
    </div>
    <div class="row">
      <table class="table table-striped table-bordered table-hover col-xs-12">
        <tr class="bg-primary">
          <th>SNo.</th>
          <th>Surah Name</th>
          <th>Translated Name (EN)</th>
          <th>Ayas</th>
          <th>Rukus</th>
          <th>Nuzool order / location</th>
          <th>Arabic Name</th>
        </tr>
        <tr v-for="surah in surahs">
          <td>
            <router-link title="View Surah"
              :to="{name: 'surah_view', params: {surah_number: surah.surah_number}}">
                {{ surah.surah_number }}
            </router-link>
          </td>
          <td>
            <router-link title="View Surah"
              :to="{name: 'surah_view', params: {surah_number: surah.surah_number}}">
                {{ surah.english_name }}
            </router-link>
          </td>
          <td>
            <router-link title="View Surah"
              :to="{name: 'surah_view', params: {surah_number: surah.surah_number}}">
                {{ surah.translated_name }}
              </router-link>
          </td>
          <td>{{ surah.total_ayas }}</td>
          <td>{{ surah.rukus }}</td>
          <td>{{ surah.nuzool_order }} ({{ surah.nuzool_location }})</td>
          <td class="ar" style="text-align: right">
            <router-link title="View Surah"
              :to="{name: 'surah_view', params: {surah_number: surah.surah_number}}">
                {{ surah.arabic_name }}
            </router-link>
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
import appConfig from '../lib/config'
import SearchBox from './SearchBox'
import ArabicTextTypeSelect from './ArabicTextTypeSelect'

export default {
  name: 'home',
  components: {
    SearchBox,
    ArabicTextTypeSelect
  },
  data () {
    return {
      surahs: {}
    }
  },
  mounted () {
    this.getSurahs()
  },
  methods: {
    getSurahs () {
      // TODO: Later move the API fetch code to lib so it can be called from other pages
      // in cases where those pages are directly accessed and home page was not executed
      // and hence we didn't fetch surah info
      if (!this.$store.getters.surahInfo) {
        let env = appConfig.getEnvConfig(process.env.NODE_ENV)
        console.log(env.API_URL)

        this.axios.get(env.API_URL + '/surahs').then((response) => {
          console.log(response)
          this.$store.commit('setSurahInfo', response.data)
        })
        .catch((error) => {
          console.log(error)
          this.$store.commit('addAlert', {
            type: 'danger',
            title: 'Server not responding',
            text: 'Could not fetch predefined security questions'
          })
        })
      }

      // console.log('Surahs set')
      this.surahs = this.$store.getters.surahInfo
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
td {
  text-align: left;
  padding: 5px;
}
</style>
