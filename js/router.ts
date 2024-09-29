import { createWebHistory, createRouter } from "vue-router"

import HomeView from "./components/HomeView.vue"
import SurahView from "./components/SurahView.vue"
import NotFoundView from "./components/NotFoundView.vue"

const routes = [
  { name: 'home', path: "/", component: HomeView },
  { name: 'surah_view', path: '/surah/:surah_number', component: SurahView, props: true },
  { path: '/:pathMatch(.*)', component: NotFoundView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
