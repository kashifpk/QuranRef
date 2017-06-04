var stateStore = {
  state: {
    arabicTextType: 'simple'
  },
  getters: {
    arabicTextType: state => { return state.arabicTextType }

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
    setArabicTextType (state, textType) { state.arabicTextType = textType }
  }
}

module.exports = {
  stateStore
}
