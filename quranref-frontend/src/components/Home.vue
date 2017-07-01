<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>

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
    <surah-list></surah-list>
  </div>
</template>

<script>
import SearchBox from './SearchBox'
import ArabicTextTypeSelect from './ArabicTextTypeSelect'
import SurahList from './SurahList'

export default {
  name: 'home',
  components: {
    SearchBox,
    ArabicTextTypeSelect,
    SurahList
  },
  data () {
    return { }
  }
}
</script>

