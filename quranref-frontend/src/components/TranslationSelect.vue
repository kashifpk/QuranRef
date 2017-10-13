<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.sidebar-form {
  border: 0px;
  margin: 10px 10px
}

select {
  border-radius: 3px;
  border: 1px solid #00d600;
}

.translation-select {
  text-align: left;
  color: #fff;
}

select, .btn {
  box-shadow: none;
  border: 1px solid transparent;
  height: 35px;
  -webkit-transition: all .3s ease-in-out;
  -o-transition: all .3s ease-in-out;
  transition: all .3s ease-in-out
}
select {
  color: #666;
  border-top-left-radius: 2px;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 2px
}

.btn {
  
  border-top-left-radius: 0;
  border-top-right-radius: 2px;
  border-bottom-right-radius: 2px;
  border-bottom-left-radius: 0
}

.selected-translation {
  
  margin: 10px 10px;
  background-color: #006800;
}
</style>

<template>
  <div class="translation-select">
    <div class="form-group sidebar-form input-group">
      <select class="form-control" size="1" v-model="selectedTranslation"
              placeholder="Select translation" >
        <option v-for="tr in availableTranslations">{{ tr[0] }}-{{ tr[1]}}</option>
      </select>
      <div class="input-group-btn">
        <button class="btn btn-success" @click="addTranslation()">
          <i class="fa fa-plus"></i>
        </button>
      </div>
    </div>
    
    <div class="row selected-translation" v-for="tr in $store.state.selectedTranslations">
      <div class="col-xs-9" style="padding-top: 8px;">
        {{ tr[0] }}-{{ tr[1] }}
      </div>
      <div class="col-xs-2">
        <button class="btn btn-danger" @click="removeTranslation(tr)">
          <i class="fa fa-remove"></i>
        </button>
      </div>
    </div>
    
  </div>
</template>

<script>
import appConfig from '../lib/config'

export default {
  name: 'TranslationSelect',
  data () {
    return {
      selectedTranslation: '',
      availableTranslations: {}
    }
  },
  mounted () {
    console.log('tr-select mounted')
    this.getTranslations()
    // this.selectedType = this.$store.getters.arabicTextType
  },
  methods: {
    getTranslations () {
      if (Object.keys(this.$store.state.availableTranslations).length > 0) {
        console.log('tr-select: have translations')
        this.textTypes = this.$store.getters.availableTextTypes
        this.setAvailableTranslations()
      } else {
        console.log('tr-select: fetching translations')
        let env = appConfig.getEnvConfig(process.env.NODE_ENV)
        let requestURL = env.API_URL + '/text_types'
        let availableTranslations = []

        this.axios.get(requestURL).then((response) => {
          let langNames = Object.keys(response.data).sort()
          for (let i in langNames) {
            let lname = langNames[i]
            if (lname === 'arabic') {
              continue
            }
            for (let j in response.data[lname]) {
              availableTranslations.push([lname, response.data[lname][j]])
            }
          }

          this.$store.commit('setAvailableTranslations', availableTranslations)
          this.selectedTranslations = this.$store.state.selectedTranslations
          this.setAvailableTranslations()
        })
        .catch((error) => {
          console.log(error)
        })
      }
    },
    setAvailableTranslations () {
      this.availableTranslations = []
      for (let i in this.$store.state.availableTranslations) {
        let tr = this.$store.state.availableTranslations[i]
        console.log(tr)
        // if translation is not in selected translations, add to to available translations
        if (this.getSelectedTranslationIndex(tr) === -1) {
          this.availableTranslations.push(tr)
        }
      }
    },
    getSelectedTranslationIndex (translation) {
      for (let i in this.$store.state.selectedTranslations) {
        let tr = this.$store.state.selectedTranslations[i]
        if (tr[0] === translation[0] && tr[1] === translation[1]) {
          return i
        }
      }

      return -1
    },
    addTranslation () {
      if (this.selectedTranslation === '') {
        return
      }

      let parts = this.selectedTranslation.split('-')

      if (this.getSelectedTranslationIndex(parts) !== -1) {
        console.log('translation already exists')
        return
      }

      // Add translation
      this.$store.commit('addTranslation', parts)

      // remove translation from available translations
      this.setAvailableTranslations()
    },
    removeTranslation (translation) {
      let trIdx = this.getSelectedTranslationIndex(translation)
      if (trIdx === -1) {
        console.log('translation does not exist')
        return
      }

      // Remove translation
      this.$store.commit('removeTranslation', trIdx)

      // add translation to available translations
      this.setAvailableTranslations()
    }
  }
}
</script>

