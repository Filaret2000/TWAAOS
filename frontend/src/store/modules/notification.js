import axios from 'axios'

const state = {
  notifications: [],
  unreadCount: 0,
  notificationSettings: null,
  loading: false,
  error: null
}

const getters = {
  notifications: state => state.notifications,
  unreadCount: state => state.unreadCount,
  notificationSettings: state => state.notificationSettings,
  loading: state => state.loading,
  error: state => state.error
}

const mutations = {
  SET_NOTIFICATIONS(state, notifications) {
    state.notifications = notifications
  },
  SET_UNREAD_COUNT(state, count) {
    state.unreadCount = count
  },
  SET_NOTIFICATION_SETTINGS(state, settings) {
    state.notificationSettings = settings
  },
  ADD_NOTIFICATION(state, notification) {
    state.notifications.unshift(notification)
    if (!notification.read) {
      state.unreadCount++
    }
  },
  MARK_AS_READ(state, notificationId) {
    const notification = state.notifications.find(n => n.id === notificationId)
    if (notification && !notification.read) {
      notification.read = true
      state.unreadCount = Math.max(0, state.unreadCount - 1)
    }
  },
  MARK_ALL_AS_READ(state) {
    state.notifications.forEach(notification => {
      notification.read = true
    })
    state.unreadCount = 0
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
  // Obține toate notificările utilizatorului
  async fetchNotifications({ commit, rootState }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get('/api/notifications', {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_NOTIFICATIONS', response.data)
      
      // Calculăm numărul de notificări necitite
      const unreadCount = response.data.filter(notification => !notification.read).length
      commit('SET_UNREAD_COUNT', unreadCount)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la obținerea notificărilor')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Obține setările de notificare ale utilizatorului
  async fetchNotificationSettings({ commit, rootState }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get('/api/notifications/settings', {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_NOTIFICATION_SETTINGS', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la obținerea setărilor de notificare')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Actualizează setările de notificare ale utilizatorului
  async updateNotificationSettings({ commit, rootState }, settings) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.put('/api/notifications/settings', settings, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_NOTIFICATION_SETTINGS', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la actualizarea setărilor de notificare')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Marchează o notificare ca citită
  async markAsRead({ commit, rootState }, notificationId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      await axios.put(`/api/notifications/${notificationId}/read`, {}, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('MARK_AS_READ', notificationId)
      
      return true
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la marcarea notificării ca citită')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Marchează toate notificările ca citite
  async markAllAsRead({ commit, rootState }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      await axios.put('/api/notifications/read-all', {}, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('MARK_ALL_AS_READ')
      
      return true
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la marcarea tuturor notificărilor ca citite')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Trimite o notificare (doar pentru administratori și secretariat)
  async sendNotification({ commit, rootState }, notificationData) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.post('/api/notifications', notificationData, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la trimiterea notificării')
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
