<template>
  <div class="home-component">
    <div class="row">
      <table class="table table-striped table-bordered table-hover">
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
          <td>{{ surah._key }}</td>
          <td>{{ surah.english_name }}</td>
          <td>{{ surah.translated_name }}</td>
          <td>{{ surah.total_ayas }}</td>
          <td>{{ surah.rukus }}</td>
          <td>{{ surah.nuzool_order }} ({{ surah.nuzool_location }})</td>
          <td class="ar" style="text-align: right">{{ surah.arabic_name }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
import appConfig from '../lib/config'

export default {
  name: 'home',
  data () {
    return {
      surahs: []
    }
  },
  mounted () {
    this.getSurahs()
  },
  methods: {
    getSurahs () {
      let env = appConfig.getEnvConfig(process.env.NODE_ENV)
      console.log(env.API_URL)

      this.axios.get(env.API_URL + '/surahs').then((response) => {
        console.log(response)
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
