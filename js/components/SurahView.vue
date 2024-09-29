<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.surah-view-component {
  text-align: right;

}
</style>

<template>

  <v-container class="surah-view-component">
    <v-row>
      <v-col>
        {{ route.name }}
        {{ surah_number }}

        Hi there<br />
  Hi there<br />
  Hi there<br />
  Hi there<br />
  Hi there<br />
  Hi there<br />
      </v-col>
    </v-row>
    <v-row v-for="aya in surahAyas">

      {{ aya }}
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
  // import { mande } from 'mande';
  import { VContainer, VRow, VCol } from 'vuetify/components';
  import { ref, onMounted, watch, defineProps } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useStore } from '../store'
  import type { SurahInfo } from "../type_defs"

  const props = defineProps({
    surah_number: Number
  })

  const store = useStore()
  const router = useRouter()
  const route = useRoute()

  // import AyaView from './AyaView'
  // <aya-view :aya="aya"></aya-view>
  const surahAyas = ref([])
  const surahInfo = ref<SurahInfo>()


  onMounted(async () => {
    console.log(props.surah_number)
    // const surahNumber = parseInt(route.params.surah_number)
    // parseInt(route.params.surah_number)

    // let idx = parseInt(route.params.surah_number) - 1
    let idx = 1
    surahInfo.value = store.surahInfo[idx]
    await getSurahText()
  })

  watch(() => route.params.surah_number, async (newVal, oldVal) => {
    console.log('route.params.surah_number changed: ', newVal, ' | was: ', oldVal)
    await getSurahText()
  })

  const getSurahText = async () => {
    // const url = import.meta.env.VITE_API_BASE_URL + "/surah/" + route.params.surah_number + "/arabic"
    // const surahsApi = mande(url)
    // const response = await surahsApi.get()

  }

  // watch: {
  //     '$store.getters.arabicTextType': function (newVal, oldVal) { // watch it
  //     console.log('arabicTextType changed: ', newVal, ' | was: ', oldVal)
  //     this.getSurahText()
  //     },
  //     '$store.state.selectedTranslations': function (newVal, oldVal) { // watch it
  //     this.getSurahText()
  //     }
  // },
  // methods: {
  //     getSurahText () {
  //     let env = appConfig.getEnvConfig(process.env.NODE_ENV)

  //     let requestURL = env.API_URL + '/qref/' + this.$route.params.surah_number +
  //         '/arabic,' + this.$store.getters.arabicTextType

  //     let trStr = this.$store.getters.selectedTranslationsString
  //     if (trStr) {
  //         requestURL += '_' + trStr
  //     }

  //     console.log(requestURL)
  //     this.axios.get(requestURL).then((response) => {
  //         console.log(response)
  //         this.surahAyas = response.data
  //     })
  //     .catch((error) => {
  //         console.log(error)
  //     })
  //     }
  // }

</script>

