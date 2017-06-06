<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>

<template>
  <div class="arabic-text-type-component">
    <select class="form-control" :value="value" size="1" v-model="selectedType"
            @change="changeTextType($event.target.value)">
      <option v-for="tt in textTypes">{{tt}}</option>
    </select>
  </div>
</template>

<script>
import appConfig from '../lib/config'

export default {
  name: 'TextTypeSelect',
  props: ['value'],
  data () {
    return {
      selectedType: '',
      textTypes: []
    }
  },
  mounted () {
    this.getTextTypes()
    this.selectedType = this.value
  },
  methods: {
    getTextTypes () {
      let env = appConfig.getEnvConfig(process.env.NODE_ENV)
      let requestURL = env.API_URL + '/text_types'

      this.axios.get(requestURL).then((response) => {
        console.log(response.data)
        this.textTypes = response.data
        this.selectedType = this.value
      })
      .catch((error) => {
        console.log(error)
      })
    },
    changeTextType (value) {
      this.$store.commit('setArabicTextType', value)
      this.$emit('text-type-changed', value)
      this.$emit('input', value)
    }
  }
}
</script>

