<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.aya-view-component {
  text-align: right;
}

.seached-text {}

</style>

<template>
  <div class="aya-view-component">
    <!-- <span v-for="word in texts['simple-clean'].split(' ')">
      {{ word }}
    </span>
    <br />
    <span v-for="word in texts[$store.getters.arabicTextType].split(' ')">
      {{ stripAraab(word) }}
      
    </span> 
    <br /> -->
    {{ texts[$store.getters.arabicTextType] }} <br />
  </div>
</template>

<script>
export default {
  name: 'AyaView',
  props: ['texts', 'searchTerm'],
  data () {
    return {
      textsWords: {}
    }
  },
  mounted () {
    this.breakWords()
  },
  methods: {
    breakWords () {
      console.log(this.texts)
      for (let textType in this.texts) {
        this.textsWords[textType] = this.texts[textType].split(' ')
      }
    },
    stripAraab (word) {
      let araab = ['ِ', 'ْ', 'َ', 'ُ', 'ّ', 'ٍ', 'ً', 'ٌ']
      let newWord = ''
      for (let i in word) {
        let ch = word[i]
        if (!araab.includes(ch)) {
          console.log(ch)
          newWord += ch
        }
      }

      return newWord
    }
  }
}
</script>

