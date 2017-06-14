<template>
  <div id="app" class="container">
    <nav class="navbar navbar-default" role="navigation" style="height: 120px;">
      <div class="container-fluid">
        
        <!-- Brand and toggle get grouped for better mobile display -->
        <div class="navbar-header">
          <a class="pull-left navbar-brand" href="#">
            <img src="./assets/logo.png" alt="Quran Reference Home" />
          </a>  
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
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
    </nav>
    <div class="row">
      <div class="col-xs-12" style="text-align: left;">
        <router-link class="btn btn-default btn-sm" title="Browse By Word"
                     :to="{name: 'browse_by_word'}">
          Browse By Word
        </router-link>
      </div>
    </div>
    <router-view></router-view>
  </div>
</template>

<script>
  
  export default {
    name: 'app'
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

</style>
