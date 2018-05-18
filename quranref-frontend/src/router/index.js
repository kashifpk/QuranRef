import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import SurahView from '@/components/SurahView'
import SearchResults from '@/components/SearchResults'
import BrowseByWord from '@/components/BrowseByWord'
import ByWordCount from '@/components/ByWordCount'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    { name: 'home', path: '/', component: Home },
    { name: 'browse_by_word', path: '/by_word', component: BrowseByWord },
    { name: 'by_word_count', path: '/by_word_count', component: ByWordCount },
    { name: 'surah_view', path: '/surah/:surah_number', component: SurahView },
    { name: 'search', path: '/search/:search_term', component: SearchResults }
    /* {
      path: '/',
      name: 'Hello',
      component: Hello
    } */
  ]
})
