<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
td, th {
  text-align: left;
  padding: 5px;
}

.surah-list-component {
  margin: 5px;
}

.table-heading {
  background-color: #005500;
  color: #fff;
  font-weight: bold;
}

a {
  
}
</style>

<template>
  <div class="row surah-list-component">
    <table class="table table-striped table-bordered table-hover col-xs-12">
      <tr class="table-heading">
        <th>SNo.</th>
        <th>Surah Name</th>
        <th class="hidden-xs hidden-sm">Translated Name (EN)</th>
        <th>Ayas</th>
        <th class="hidden-xs">Rukus</th>
        <th class="hidden-xs">Nuzool</th>
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
        <td class="hidden-xs hidden-sm">
          <router-link title="View Surah"
            :to="{name: 'surah_view', params: {surah_number: surah.surah_number}}">
              {{ surah.translated_name }}
            </router-link>
        </td>
        <td>{{ surah.total_ayas }}</td>
        <td class="hidden-xs">{{ surah.rukus }}</td>
        <td class="hidden-xs">{{ surah.nuzool_order }} ({{ surah.nuzool_location }})</td>
        <td class="ar" style="text-align: right">
          <router-link title="View Surah"
            :to="{name: 'surah_view', params: {surah_number: surah.surah_number}}">
              {{ surah.arabic_name }}
          </router-link>
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
import appConfig from '../lib/config'

export default {
  name: 'SurahList',
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
      if (!this.$store.getters.surahInfo) {
        let env = appConfig.getEnvConfig(process.env.NODE_ENV)
        console.log(env.API_URL)

        this.axios.get(env.API_URL + '/surahs').then((response) => {
          console.log(response)
          this.$store.commit('setSurahInfo', response.data)
          this.surahs = response.data
        })
        .catch((error) => {
          console.log(error)
          this.$store.commit('addAlert', {
            type: 'danger',
            title: 'Server not responding',
            text: 'Could not fetch predefined security questions'
          })
        })
      } else {
        // console.log('Surahs set')
        this.surahs = this.$store.getters.surahInfo
      }
    }
  }
}
</script>
