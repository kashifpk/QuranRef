<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

input[type="text"], .btn {
  box-shadow: none;
  background-color: #fff;
  border: 1px solid transparent;
  height: 35px;
  -webkit-transition: all .3s ease-in-out;
  -o-transition: all .3s ease-in-out;
  transition: all .3s ease-in-out
}

input[type="text"] {
  color: #666;
  border-top-left-radius: 2px;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 2px
}

input[type="text"]:focus, .sidebar-form input[type="text"]:focus+.input-group-btn .btn {
  background-color: #fff;
  color: #666
}

input[type="text"]:focus+.input-group-btn .btn {
  border-left-color: #fff
}

.btn {
  color: #006100;
  background-color: #fff;
  border-top-left-radius: 0;
  border-top-right-radius: 2px;
  border-bottom-right-radius: 2px;
  border-bottom-left-radius: 0
}
</style>

<template>
  <form class="sidebar-form" @submit.prevent="doSearch">
    <div class="input-group">
      <input type="text" class="form-control" v-model="searchTerm" />
      <span class="input-group-btn">
        <button class="btn btn-success" type="submit" @click="doSearch()">
          <i class="fa fa-search"></i>
        </button>
      </span>
    </div><!-- /input-group -->
  </form>
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

