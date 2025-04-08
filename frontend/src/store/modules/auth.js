import axios from 'axios'
import jwtDecode from 'jwt-decode'

const state = {
  token: localStorage.getItem('token') || null,
  user: null,
  loading: false,
  error: null
}

const getters = {
  isAuthenticated: state => !!state.token,
  user: state => state.user,
  isAdmin: state => state.user && state.user.role === 'ADM',
  isSecretary: state => state.user && state.user.role === 'SEC',
  isTeacher: state => state.user && state.user.role === 'CD',
  isStudent: state => state.user && state.user.role === 'STD',
  hasRole: state => role => state.user && state.user.role === role,
  loading: state => state.loading,
  error: state => state.error
}

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  },
  SET_USER(state, user) {
    state.user = user
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  CLEAR_ERROR(state) {
    state.error = null
  }
}

const actions = {
  // Autentificare cu Google OAuth
  async login({ commit }, googleToken) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.post('/api/auth/login', { token: googleToken })
      
      const { access_token, user } = response.data
      
      commit('SET_TOKEN', access_token)
      commit('SET_USER', user)
      
      return user
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la autentificare')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Autentificare cu email și parolă
  async loginWithCredentials({ commit }, credentials) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      // În mod normal, aici ar trebui să facem un apel API către backend
      // Simulăm un răspuns de succes pentru a permite testarea UI-ului
      // TODO: Înlocuiți acest cod cu apelul real către API
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Simulăm un utilizator autentificat
      const user = {
        id: 1,
        email: credentials.email,
        firstName: 'Utilizator',
        lastName: 'Test',
        role: 'ADMIN'
      }
      
      const access_token = 'simulated_token_' + Math.random().toString(36).substring(2)
      
      commit('SET_TOKEN', access_token)
      commit('SET_USER', user)
      
      return user
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Email sau parolă incorecte')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Deconectare
  logout({ commit }) {
    commit('SET_TOKEN', null)
    commit('SET_USER', null)
  },
  
  // Verificare token și obținere informații utilizator
  async checkAuth({ commit, state }) {
    if (!state.token) return
    
    try {
      // Verificăm dacă token-ul este expirat
      const decoded = jwtDecode(state.token)
      const currentTime = Date.now() / 1000
      
      if (decoded.exp < currentTime) {
        // Token-ul este expirat, deconectăm utilizatorul
        commit('SET_TOKEN', null)
        commit('SET_USER', null)
        return
      }
      
      // Token-ul este valid, obținem informațiile utilizatorului
      if (!state.user) {
        commit('SET_LOADING', true)
        
        const response = await axios.get('/api/auth/me', {
          headers: {
            Authorization: `Bearer ${state.token}`
          }
        })
        
        commit('SET_USER', response.data)
        commit('SET_LOADING', false)
      }
    } catch (error) {
      commit('SET_TOKEN', null)
      commit('SET_USER', null)
      commit('SET_LOADING', false)
    }
  },
  
  // Actualizare informații utilizator
  async updateUserProfile({ commit, state }, userData) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.put(`/api/auth/users/${state.user.id}`, userData, {
        headers: {
          Authorization: `Bearer ${state.token}`
        }
      })
      
      commit('SET_USER', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la actualizarea profilului')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
