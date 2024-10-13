<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.surah-view-component {
  text-align: right;

}

.surah-name {
  font-size: 26pt;
  font-weight: bold;
}
</style>

<template>

  <v-container class="surah-view-component">
    <v-row>
      <v-col class="text-center ar surah-name">
        {{ surahInfo?.arabic_name }}
      </v-col>
    </v-row>

    <aya-view v-for="aya in surahAyas" :aya="aya" :display-surah-name="false"></aya-view>

  </v-container>
</template>

<script setup lang="ts">
  import { mande } from 'mande';
  import { VContainer, VRow, VCol } from 'vuetify/components';
  import { ref, onMounted, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useStore } from '../store'
  import type { SurahInfo, AyaInfo } from "../type_defs"
  import AyaView from './AyaView.vue';

  const props = defineProps({
    surah_number: Number
  })

  const store = useStore()
  const router = useRouter()
  const route = useRoute()

  // import AyaView from './AyaView'
  // <aya-view :aya="aya"></aya-view>
  const surahAyas = ref<AyaInfo[]>()
  const surahInfo = ref<SurahInfo>()


  onMounted(async () => {
    if (props.surah_number !== undefined) {
      console.log(props.surah_number)

      surahInfo.value = store.surahInfo[props.surah_number - 1]
      await getSurahText()
    } else {
      console.error('surah_number is undefined')
    }
  })

  watch(() => route.params.surah_number, async (newVal, oldVal) => {
    console.log('route.params.surah_number changed: ', newVal, ' | was: ', oldVal)
    await getSurahText()
  })

  const getSurahText = async () => {
    console.log('getSurahText')
    const url = import.meta.env.VITE_API_BASE_URL + "/text/" + props.surah_number + "/arabic:uthmani_urdu:maududi"
    console.log(url)
    const surahsApi = mande(url)
    const response = await surahsApi.get()
    console.log(response)
    surahAyas.value = response as AyaInfo[]
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

