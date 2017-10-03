<style>
  .user-panel .image img {
    border-radius: 50%;
  }
  
  .sidebar-menu>li>a {
    padding: 12px 15px 12px 15px;
  }

  .sidebar-menu li.active>a>.fa-angle-left, .sidebar-menu li.active>a>.pull-right-container>.fa-angle-left {
    animation-name: rotate;
    animation-duration: .2s;
    animation-fill-mode: forwards;
  }

  @keyframes rotate {
    0% {
      transform: rotate(0deg);
    }

    100% {
      transform: rotate(-90deg);
    }
  }
</style>

<template>
  <aside class="main-sidebar">

    <!-- sidebar: style can be found in sidebar.less -->
    <section class="sidebar">

      <!-- Sidebar user panel (optional) -->
      <div class="user-panel">
        <div class="text-center image">
          <img src="/static/img/logo.png" />
        </div>
      </div>

      <!-- search form (Optional) -->
      <form v-on:submit.prevent class="sidebar-form">
        <search-box></search-box>
      </form>
      <!-- /.search form -->

      <!-- Sidebar Menu -->
      <ul class="sidebar-menu">
        <router-link tag="li" class="pageLink" :to="{name: 'home'}">
          <a>
            <i class="fa fa-home"></i>
            <span class="page">Home</span>
          </a>
        </router-link>
        <router-link tag="li" class="pageLink" :to="{name: 'browse_by_word'}">
          <a>
            <i class="fa fa-list"></i>
            <span class="page">By Word</span>
          </a>
        </router-link>
      </ul>
      <!-- /.sidebar-menu -->
    </section>
    <!-- /.sidebar -->
  </aside>
</template>

<script>
import SearchBox from './SearchBox'

export default {
  name: 'Sidebar',
  components: { SearchBox },
  mounted: function () {
    window.jQuery('[data-toggle="hideseek"]').off().hideseek()
  }
}
</script>

