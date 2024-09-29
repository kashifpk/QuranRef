<style scoped></style>

<template>
  <v-responsive>
    <v-app>

      <v-app-bar :elevation="0" class="bg-green">
        <template v-slot:prepend>
          <v-app-bar-nav-icon></v-app-bar-nav-icon>
        </template>
        <v-app-bar-title class="d-flex w-100 justify-center">
          <a href="/"
            class="d-flex xs-header visible-xs ar ar-header text-decoration-none font-weight-bold text-green-lighten-5">
            القرآن الکریم
          </a>
        </v-app-bar-title>

        <template v-slot:append>
          <v-text-field label="Search" append-inner-icon="mdi-magnify" variant="inverted" min-width="200" density="compact" single-line hide-details @click:append-inner="doSearch()"></v-text-field>
          <v-icon icon="mdi-account"></v-icon>
          <v-btn href="/" icon="mdi-heart"></v-btn>
          <v-btn href="/words" title="Explore words" icon="mdi-file-word-box"></v-btn>
          <v-btn icon="mdi-dots-vertical"></v-btn>
        </template>


      </v-app-bar>

      <v-navigation-drawer class="bg-green">
        <v-list>
          <v-list-item>
            <router-link to="/" title="Home" class="text-decoration-none font-weight-bold text-green-lighten-5"><v-icon icon="mdi-home"></v-icon></router-link>
          </v-list-item>

          <v-divider></v-divider>

          <v-list-item class="text-left pl-8">
            <a href="/" title="by-word" class="text-decoration-none font-weight-bold text-green-lighten-5">By Word</a>
          </v-list-item>

          <v-list-item class="text-left pl-8">
            <a href="/" title="by-word" class="text-decoration-none font-weight-bold text-green-lighten-5">Words by count</a>
          </v-list-item>

          <v-list-item class="text-left pl-8">
            <a href="/" title="by-word" class="text-decoration-none font-weight-bold text-green-lighten-5">Arabic text type</a>
          </v-list-item>

          <v-list-item class="text-left pl-8">
            <a href="/" title="by-word" class="text-decoration-none font-weight-bold text-green-lighten-5">Translations</a>
          </v-list-item>

        </v-list>
      </v-navigation-drawer>

      <v-main>
        <router-view />

      </v-main>

      <v-footer class="justify-center" border>
        Arabic texts and translations courtesy of <a class="pl-2" href="http://tanzil.net">tanzil.net</a>
      </v-footer>
    </v-app>


  </v-responsive>


</template>


<script setup>
  import {
    VApp, VResponsive, VMain, VAppBar, VFooter, VAppBarNavIcon, VNavigationDrawer, VDivider, VList, VListItem, VBtn, VIcon, VTextField
  } from 'vuetify/components';
  import { RouterView, RouterLink } from 'vue-router';

  // import { mdiAccount, mdiHeart } from '@mdi/js';
  // import HelloWorld from './components/HelloWorld.vue'

  const doSearch = async () => {
    console.log('doSearch');
  }
</script>