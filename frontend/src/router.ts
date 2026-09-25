import { createWebHistory, createRouter } from "vue-router"

import HomeView from "./components/HomeView.vue"
import SurahView from "./components/SurahView.vue"
import NotFoundView from "./components/NotFoundView.vue"
import BrowseByWord from "./views/BrowseByWord.vue"
import ByWordCount from "./views/ByWordCount.vue"
import SearchResults from "./views/SearchResults.vue"
import BookmarksView from "./views/BookmarksView.vue"
import BrowseByRoot from "./views/BrowseByRoot.vue"
import LemmaView from "./views/LemmaView.vue"
import RootView from "./views/RootView.vue"
import TopicsView from "./views/TopicsView.vue"
import TopicView from "./views/TopicView.vue"
import PhraseView from "./views/PhraseView.vue"
import StructureView from "./views/StructureView.vue"
import ReadUnitView from "./views/ReadUnitView.vue"

const routes = [
  { name: 'home', path: "/", component: HomeView },
  {
    name: 'surah_view',
    path: '/surah/:surah_number',
    component: SurahView,
    props: (route: { params: { surah_number: string } }) => ({
      surah_number: Number(route.params.surah_number)
    })
  },
  { name: 'browse_by_word', path: '/by_word', component: BrowseByWord },
  { name: 'by_word_count', path: '/by_word_count', component: ByWordCount },
  { name: 'search', path: '/search/:search_term', component: SearchResults, props: true },
  { name: 'bookmarks', path: '/bookmarks', component: BookmarksView },
  { name: 'browse_by_root', path: '/by_root', component: BrowseByRoot },
  { name: 'root_view', path: '/root/:root', component: RootView, props: true },
  { name: 'lemma_view', path: '/lemma/:lemma', component: LemmaView, props: true },
  { name: 'topics', path: '/topics', component: TopicsView },
  { name: 'topic_view', path: '/topic/:id', component: TopicView, props: true },
  { name: 'phrase_view', path: '/phrase/:id', component: PhraseView, props: true },
  { name: 'structure', path: '/structure', component: StructureView },
  { name: 'read_unit', path: '/read/:unit/:n', component: ReadUnitView, props: true },
  { path: '/:pathMatch(.*)', component: NotFoundView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
