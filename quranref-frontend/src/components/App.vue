<style>
#app_main {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  /*margin-top: 60px;*/
}

@font-face {
  font-family: 'MeQuran';
  src: url('../assets/fonts/me_quran.ttf') format('truetype'); /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
}

@font-face {
  font-family: 'AlQalam';
  src: url('../assets/fonts/AlQalamQuran.ttf') format('truetype'); /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
}

@font-face {
  font-family: 'Noori';
  src: url('../assets/fonts/noori.ttf') format('truetype'); /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
}

.ar-num {
  font-family: 'AlQalam';
  text-align: right;
  font-size: large;
  direction: rtl;
  unicode-bidi: bidi-override;
}

.ar{
  font-family: 'AlQalam';
  text-align: right;
  font-size: 18pt;
}

.ur {
  font-family: 'Noori';
  text-align: right;

}

.num {
  font-family: 'AlQalam';
  font-size:small;
  vertical-align: top;
  text-align: left;

}

.content-wrapper {
  padding: 8px;
  padding-top: 65px;
}

.main-sidebar {
  position: fixed;
  height: 100vh;
}

hr.visible-xs-block {
  width: 100%;
  background-color: rgba(0, 0, 0, 0.17);
  height: 1px;
  border-color: transparent;
}
</style>

<template>
  <div id="app_main" :class="['wrapper', classes]">
    <top-header></top-header>
    
    <sidebar />
    
    <!-- Content Wrapper. Contains page content -->
    <div class="content-wrapper">
      <router-view></router-view>
    </div>
    <!-- /.content-wrapper -->
  
    <!-- Main Footer -->
    <footer class="main-footer">
      <strong>
        <i class="fa fa-creative-commons fa-2x"></i>
        Public service
      </strong>
    </footer>
  </div>
</template>

<script>
  import Sidebar from './Sidebar'
  import 'hideseek'
  import TopHeader from './TopHeader'
  import SearchBox from './SearchBox'
  
  export default {
    name: 'app',
    components: {
      SearchBox,
      TopHeader,
      Sidebar
    },
    data () {
      return {
        classes: {
          fixed_layout: false,
          hide_logo: false
        },
        error: ''
      }
    },
    methods: {
      changeloading () {
        this.$store.commit('TOGGLE_SEARCHING')
      }
    }
  }
</script>

