<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>

<template>
  <div class="input-group">
    <input type="text" class="form-control" v-model="searchTerm" />
    <span class="input-group-btn">
      <button class="btn btn-success" type="button" @click="doSearch()">
        <i class="fa fa-search"></i>
      </button>
    </span>
  </div><!-- /input-group -->
</template>

<script>
export default {
  name: 'SearchBox',
  data () {
    return {
      searchTerm: ''
    }
  },
  methods: {
    doSearch () {
      this.$router.push({ name: 'search', params: { search_term: this.searchTerm } })
    }
  }
}
</script>

