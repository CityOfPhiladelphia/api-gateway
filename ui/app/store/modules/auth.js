import router from '../../router'

export default {
  state: {
    isLoggedIn: false,
    csrf: null,
    user: {
      name: null
    }
  },
  mutations: {
    receiveAuth (state, auth) {
      state.isLoggedIn = true
      state.csrf = auth.csrf
      state.user.name = auth.user.name
    },
    resetAuth (state) {
      state.isLoggedIn = false
      state.csrf = null
      state.user.name = null
    }
  },
  actions: {
    async getStoredAuth ({ commit }) {
      try {
        //const auth = await localForage.getItem('auth')
        if (auth) {
          commit('receiveAuth', auth)
        }
      } catch (err) {
        console.error('Stored auth error', err)
      }
    },
    async login ({ commit }, { username, password }) {
      try {
        // const auth = await api.login(username, password)
        // await localForage.setItem('auth', auth)
        // commit('receiveAuth', auth)
        router.push('/')
      } catch (err) {
        console.error('Login error', err)
      }
    },
    async logout ({ commit }) {
      try {
        //await localForage.removeItem('auth')
        //commit('resetAuth')
      } catch (err) {
        console.error('Logout error', err)
      }
    }
  }
}
