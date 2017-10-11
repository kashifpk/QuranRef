<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>

<template>
  <div class="home-component">
    <section class="content">
      <div class="row" style="height: 75px;">
        <div class="col-xs-12">
          
          <!-- Brand and toggle get grouped for better mobile display -->
          <div>
            <a class="pull-left" href="#">
              <img src="/static/img/logo.png" alt="Quran Reference Home" />
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
      
      <div class="row">
        <div class="col-xs-12">
          <surah-list></surah-list>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import SurahList from './SurahList'

export default {
  name: 'home',
  components: {
    SurahList
  },
  data () {
    return { }
  }
}
</script>

