var stateStore = {
  state: {
    arabicTextType: 'simple',
    surahInfo: '',
    availableTextTypes: [],
    availableTranslations: [],
    selectedTranslations: [],
    callingAPI: false,
    searching: ''
  },
  getters: {
    arabicTextType: state => { return state.arabicTextType },
    surahInfo: state => { return state.surahInfo },
    availableTextTypes: state => { return state.availableTextTypes },
    selectedTranslationsString: state => {
      let s = ''
      for (let i in state.selectedTranslations) {
        let tr = state.selectedTranslations[i]
        s += tr[0] + ',' + tr[1] + '_'
      }

      if (s.length > 0) {
        s = s.slice(0, -1)
      }

      return s
    }
    /* isLoggedIn: (state, getters) => {
      if (state.authToken === '') {
        return false
      }

      let authTokenString = getters.authToken
      let tokenExpDate = jwt.getTokenExpirationDate(authTokenString)
      let currentDate = new Date()
      let secondsToExpiry = (tokenExpDate - currentDate) / 1000

      if (secondsToExpiry > 0) {
        return true
      } else {
        return false
      }
    } */
  },
  mutations: {
    TOGGLE_LOADING (state) {
      state.callingAPI = !state.callingAPI
    },
    TOGGLE_SEARCHING (state) {
      state.searching = (state.searching === '') ? 'loading' : ''
    },
    setArabicTextType (state, textType) { state.arabicTextType = textType },
    setSurahInfo (state, surahData) { state.surahInfo = surahData },
    setAvailableTextTypes (state, textTypes) { state.availableTextTypes = textTypes },
    setAvailableTranslations (state, translations) { state.availableTranslations = translations },
    addTranslation (state, translation) {
      // translation format: [lang, translation], e.g, ['urdu', 'maududi']
      state.selectedTranslations.push(translation)
    },
    removeTranslation (state, trIdx) {
      state.selectedTranslations.splice(trIdx, 1)
    }
  }
}

module.exports = {
  stateStore
}
