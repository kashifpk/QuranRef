<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>

<template>
  <div class="arabic-text-type-component">
    <select class="form-control" :value="value" size="1"
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
      textTypes: []
    }
  },
  mounted () {
    this.getTextTypes()
  },
  methods: {
    getTextTypes () {
      let env = appConfig.getEnvConfig(process.env.NODE_ENV)
      let requestURL = env.API_URL + '/text_types'

      this.axios.get(requestURL).then((response) => {
        console.log(response.data)
        this.textTypes = response.data
      })
      .catch((error) => {
        console.log(error)
      })
    },
    changeTextType (value) {
      this.$store.commit('setArabicTextType', this.value)
      this.$emit('input', value)
      this.$emit('text-type-changed', this.value)
    }
  }
}
</script>

