import axios from 'axios'

const state = {
  users: [],
  currentUser: null,
  loading: false,
  error: null
}

const getters = {
  users: state => state.users,
  currentUser: state => state.currentUser,
  loading: state => state.loading,
  error: state => state.error,
  
  // Filtrează utilizatorii după rol
  usersByRole: state => role => {
    return state.users.filter(user => user.role === role)
  },
  
  // Obține numărul de utilizatori pentru fiecare rol
  userCounts: state => {
    const counts = {
      ADM: 0,
      SEC: 0,
      CD: 0,
      STD: 0
    }
    
    state.users.forEach(user => {
      if (counts[user.role] !== undefined) {
        counts[user.role]++
      }
    })
    
    return counts
  }
}

const mutations = {
  SET_USERS(state, users) {
    state.users = users
  },
  SET_CURRENT_USER(state, user) {
    state.currentUser = user
  },
  ADD_USER(state, user) {
    state.users.push(user)
  },
  UPDATE_USER(state, updatedUser) {
    const index = state.users.findIndex(u => u.id === updatedUser.id)
    if (index !== -1) {
      state.users.splice(index, 1, updatedUser)
    }
  },
  REMOVE_USER(state, userId) {
    state.users = state.users.filter(u => u.id !== userId)
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
  // Obține toți utilizatorii (doar pentru administratori)
  async fetchUsers({ commit, rootState }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get('/api/auth/admin/users', {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_USERS', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la obținerea utilizatorilor')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Obține un utilizator după ID
  async fetchUserById({ commit, rootState }, userId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get(`/api/auth/admin/users/${userId}`, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_CURRENT_USER', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la obținerea utilizatorului')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Creează un nou utilizator (doar pentru administratori)
  async createUser({ commit, rootState }, userData) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.post('/api/auth/admin/users', userData, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('ADD_USER', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la crearea utilizatorului')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Actualizează un utilizator existent (doar pentru administratori)
  async updateUser({ commit, rootState }, { userId, userData }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.put(`/api/auth/admin/users/${userId}`, userData, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('UPDATE_USER', response.data)
      
      // Dacă utilizatorul actualizat este utilizatorul curent, actualizăm și în modulul auth
      if (rootState.auth.user && rootState.auth.user.id === response.data.id) {
        commit('auth/SET_USER', response.data, { root: true })
      }
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la actualizarea utilizatorului')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Șterge un utilizator (doar pentru administratori)
  async deleteUser({ commit, rootState }, userId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      await axios.delete(`/api/auth/admin/users/${userId}`, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('REMOVE_USER', userId)
      
      return true
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la ștergerea utilizatorului')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Importă utilizatori din fișier Excel (doar pentru administratori)
  async importUsers({ commit, rootState }, formData) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.post('/api/auth/admin/users/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      // Actualizăm lista de utilizatori cu cei importați
      await dispatch('fetchUsers')
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la importul utilizatorilor')
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
