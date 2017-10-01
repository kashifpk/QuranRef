<template>
  <div id="app" class="container-fluid">
    <div class="row" style="height: 75px;">
      <div class="col-xs-12">
        
        <!-- Brand and toggle get grouped for better mobile display -->
        <div>
          <a class="pull-left" href="#">
            <img src="./assets/logo.png" alt="Quran Reference Home" />
          </a>
        </div>
    
        <div class="ar text-success" style="font-size: larger; font-weight: bold;">
              وَلَقَدْ يَسَّرْنَا ٱلْقُرْءَانَ لِلذِّكْرِ فَهَلْ مِن مُّدَّكِر
        </div>
        <div class="ur text-primary hidden-xs hidden-sm">
          ہم نے اِس قرآن کو نصیحت کے لیے آسان ذریعہ بنا دیا ہے، پھر کیا ہے کوئی نصیحت قبول کرنے والا؟
        <br />
        We have made the Qur'an easy to derive lessons from. Is there, then, any who will take heed?
        </div>
      </div><!-- /.container-fluid -->
    </div>
    
    <div class="row menu-bar">
      <div class="col-md-12">
        <ul>
          <li>
            <router-link title="Home" :to="{name: 'home'}">
              Home
            </router-link>
          </li>
          <li>
            <router-link title="Browse By Word" :to="{name: 'browse_by_word'}">
              Browse By Word
            </router-link>
          </li>
          <li class="pull-right no-highlight">
            <search-box></search-box>
          </li>
        </ul>
        
      </div>
    </div>
    <router-view></router-view>
  </div>
</template>

<script>
  import SearchBox from './components/SearchBox'
  
  export default {
    name: 'app',
    components: {
      SearchBox
    }
  }
</script>

<style>
@import '../node_modules/bootstrap/dist/css/bootstrap.css';

#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

@font-face {
  font-family: 'MeQuran';
  src: url('./assets/fonts/me_quran.ttf') format('truetype'); /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
}

@font-face {
  font-family: 'AlQalam';
  src: url('./assets/fonts/AlQalamQuran.ttf') format('truetype'); /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
}

@font-face {
  font-family: 'Noori';
  src: url('./assets/fonts/noori.ttf') format('truetype'); /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
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

.menu-bar {
  background-color: #005500;
  height: 45px;
  color: #ffffff;
  font-weight: bold;
  text-align: left;
  font-size: 12pt;
}

.menu-bar li {
  display: inline-block;
  height: 45px;
  text-align: center;
  vertical-align: middle;
  padding: 5px;
  padding-top: 12px;
}

.menu-bar li:hover {
  background-color: #319031;
}

.menu-bar li.no-highlight {
  background-color: #005500;
  padding-top: 5px;
}
.menu-bar li.no-highlight:hover {
  background-color: #005500;
}

.menu-bar li a {
  text-decoration: none;
  color: #ffffff;
}

.menu-bar li a:visited {
  text-decoration: none;
  color: #ffffff;
}
</style>
