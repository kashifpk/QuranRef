<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>

<template>
  <div class="arabic-text-type-component">
    <div class="form-group">
      <form class="form-inline">
        <label for="arabic_text_type">Arabic Text Type: </label>
        <select class="form-control" size="1" v-model="selectedType" id="arabic_text_type"
                placeholder="Select arabic style..."
                @change="changeTextType($event.target.value)">
          <option v-for="tt in textTypes">{{tt}}</option>
        </select>
      </form>
    </div>
  </div>
</template>

<script>
import appConfig from '../lib/config'

export default {
  name: 'TextTypeSelect',
  data () {
    return {
      selectedType: '',
      textTypes: []
    }
  },
  mounted () {
    this.getTextTypes()
    // this.selectedType = this.$store.getters.arabicTextType
  },
  methods: {
    getTextTypes () {
      let env = appConfig.getEnvConfig(process.env.NODE_ENV)
      let requestURL = env.API_URL + '/text_types'

      this.axios.get(requestURL).then((response) => {
        console.log(response.data)
        this.textTypes = response.data
        this.selectedType = this.$store.getters.arabicTextType
      })
      .catch((error) => {
        console.log(error)
      })
    },
    changeTextType (value) {
      this.$store.commit('setArabicTextType', value)
      this.$emit('text-type-changed', value)
      // this.$emit('input', value)
    }
  }
}
</script>

