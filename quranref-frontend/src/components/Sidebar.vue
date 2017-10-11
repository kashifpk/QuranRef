<style>
.main-sidebar {
  background-color: #005500;
}

.main-sidebar label {
  color: #fff;
}
.user-panel .image img {
  border-radius: 50%;
}

.user-panel>.info,user-panel>.info>a {
  color: #fff
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

.sidebar-form {
  border-radius: 3px;
  border: 1px solid #00d600;
  margin: 10px 10px
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
      <search-box></search-box>

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
      <arabic-text-type-select></arabic-text-type-select>
    </section>
    <!-- /.sidebar -->
  </aside>
</template>

<script>
import SearchBox from './SearchBox'
import ArabicTextTypeSelect from './ArabicTextTypeSelect'

export default {
  name: 'Sidebar',
  components: {
    SearchBox,
    ArabicTextTypeSelect
  },
  mounted: function () {
    window.jQuery('[data-toggle="hideseek"]').off().hideseek()
  }
}
</script>

