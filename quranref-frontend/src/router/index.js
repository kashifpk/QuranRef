import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import SurahView from '@/components/SurahView'
import SearchResults from '@/components/SearchResults'

Vue.use(Router)

export default new Router({
  routes: [
    { name: 'home', path: '/', component: Home },
    { name: 'surah_view', path: '/surah/:surah_number', component: SurahView },
    { name: 'search', path: '/search/:search_term', component: SearchResults }
    /* {
      path: '/',
      name: 'Hello',
      component: Hello
    } */
  ]
})
