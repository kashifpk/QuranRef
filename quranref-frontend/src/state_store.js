var stateStore = {
  state: {
    arabicTextType: 'simple',
    surahInfo: '',
    availableTextTypes: []
  },
  getters: {
    arabicTextType: state => { return state.arabicTextType },
    surahInfo: state => { return state.surahInfo },
    availableTextTypes: state => { return state.availableTextTypes }

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
    setArabicTextType (state, textType) { state.arabicTextType = textType },
    setSurahInfo (state, surahData) { state.surahInfo = surahData },
    setAvailableTextTypes (state, textTypes) { state.availableTextTypes = textTypes }
  }
}

module.exports = {
  stateStore
}
