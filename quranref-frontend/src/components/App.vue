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
  src: url('/static/fonts/me_quran.ttf') format('truetype'); /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
}

@font-face {
  font-family: 'AlQalam';
  src: url('/static/fonts/AlQalamQuran.ttf') format('truetype'); /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
}

@font-face {
  font-family: 'Noori';
  src: url('/static/fonts/noori.ttf') format('truetype'); /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
}

.ar-num {
  font-family: 'AlQalam';
  text-align: right;
  font-size: large;
  direction: rtl;
  unicode-bidi: bidi-override;
}

.ar, .arabic{
  font-family: 'AlQalam';
  text-align: right;
  font-size: 18pt;
}

.ur, .urdu {
  font-family: 'Noori';
  text-align: right;
  font-size: 14pt;
}

.en, .english {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  text-align: left;
  font-size: 12pt;
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
      <div style="margin: 5px; margin-top: 20px;">
        <router-view></router-view>
      </div>
      
    </div>
    <!-- /.content-wrapper -->
  
    <!-- Main Footer -->
    <footer class="main-footer">
      <strong>
        <i class="fa fa-creative-commons"></i>
        Public service for the good of all
      </strong>
      -
      Arabic texts and translations courtesy of <a href="http://tanzil.net">tanzil.net</a>
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

