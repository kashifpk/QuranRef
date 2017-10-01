<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>

<template>
  <div class="home-component">
    <div class="row">
      <div class="col-xs-12 col-sm-12 col-md-6 col-lg-4">
        <arabic-text-type-select></arabic-text-type-select>
      </div>
      
    </div>
    <div class="row">
      <div class="col-xs-12">
        <surah-list></surah-list>
      </div>
    </div>
    
  </div>
</template>

<script>
import ArabicTextTypeSelect from './ArabicTextTypeSelect'
import SurahList from './SurahList'

export default {
  name: 'home',
  components: {
    ArabicTextTypeSelect,
    SurahList
  },
  data () {
    return { }
  }
}
</script>

