<style scoped>
.main-header {
  position: fixed;
  width: 100%;
}

.navbar-custom-menu ul li {
  font-size: 12pt;
  font-weight: bold;
}

.search_box {
  padding: 4px;
  padding-top: 7px;
  
}
.logo-mini,
.logo-lg {
  text-align: left;

  img {
    padding: .4em !important;
  }
}

.logo-lg {
  img {
    display: -webkit-inline-box;
    width: 25%;
  }
}

.xs-header {
  text-decoration: none;
  font-weight: bold;
  color: #fff
}

.ar-header {
  color: #f1f1f1;
  font-weight: bold;
  text-align: center;
}
</style>

<template>
  <header class="main-header">
    
    <!-- Header Navbar -->
    <nav class="navbar navbar-static-top" role="navigation">
      <!-- Sidebar toggle button-->
      <a href="javascript:;" class="sidebar-toggle" data-toggle="offcanvas" role="button">
        <span class="sr-only">Toggle navigation</span>
      </a>
      
      <router-link title="Go to home page" :to="{name: 'home'}" class="xs-header visible-xs ar ar-header">
        القرآن الکریم
      </router-link>
      <span class="hidden-xs ar ar-header">
وَلَقَدْ يَسَّرْنَا ٱلْقُرْءَانَ لِلذِّكْرِ فَهَلْ مِن مُّدَّكِرِ
      </span>
      <!-- Navbar Right Menu -->
      <div class="navbar-custom-menu">
        
        <ul class="nav navbar-nav">
          <li class="hidden-xs">
            <router-link title="Go to home page" :to="{name: 'home'}">
              Home
            </router-link>
          </li>
          <li class="hidden-xs">
            <router-link title="Browse By Word" :to="{name: 'browse_by_word'}">
              Browse By Word
            </router-link>
          </li>
        </ul>
      </div>
    </nav>
  </header>
</template>

<script>
  import SearchBox from './SearchBox'
  
  export default {
    name: 'TopHeader',
    components: {
      SearchBox
    }
  }
</script>
