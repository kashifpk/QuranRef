import { createWebHistory, createRouter } from "vue-router"

import HomeView from "./components/HomeView.vue"
import SurahView from "./components/SurahView.vue"
import NotFoundView from "./components/NotFoundView.vue"
import BrowseByWord from "./views/BrowseByWord.vue"
import ByWordCount from "./views/ByWordCount.vue"
import SearchResults from "./views/SearchResults.vue"

const routes = [
  { name: 'home', path: "/", component: HomeView },
  { name: 'surah_view', path: '/surah/:surah_number', component: SurahView, props: true },
  { name: 'browse_by_word', path: '/by_word', component: BrowseByWord },
  { name: 'by_word_count', path: '/by_word_count', component: ByWordCount },
  { name: 'search', path: '/search/:search_term', component: SearchResults, props: true },
  { path: '/:pathMatch(.*)', component: NotFoundView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
