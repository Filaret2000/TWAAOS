import axios from 'axios'

const state = {
  schedules: [],
  currentSchedule: null,
  examPeriods: [],
  currentExamPeriod: null,
  subjects: [],
  groups: [],
  rooms: [],
  teachers: [],
  conflicts: [],
  loading: false,
  error: null
}

const getters = {
  schedules: state => state.schedules,
  currentSchedule: state => state.currentSchedule,
  examPeriods: state => state.examPeriods,
  currentExamPeriod: state => state.currentExamPeriod,
  subjects: state => state.subjects,
  groups: state => state.groups,
  rooms: state => state.rooms,
  teachers: state => state.teachers,
  conflicts: state => state.conflicts,
  loading: state => state.loading,
  error: state => state.error,
  
  // Obține planificările filtrate după perioada de examinare
  schedulesByPeriod: state => periodId => {
    return state.schedules.filter(schedule => schedule.examPeriodId === periodId)
  },
  
  // Obține planificările filtrate după cadrul didactic
  schedulesByTeacher: state => teacherId => {
    return state.schedules.filter(schedule => schedule.teacherId === teacherId)
  },
  
  // Obține planificările filtrate după grupă
  schedulesByGroup: state => groupId => {
    return state.schedules.filter(schedule => 
      schedule.groups && schedule.groups.some(group => group.id === groupId)
    )
  }
}

const mutations = {
  SET_SCHEDULES(state, schedules) {
    state.schedules = schedules
  },
  SET_CURRENT_SCHEDULE(state, schedule) {
    state.currentSchedule = schedule
  },
  ADD_SCHEDULE(state, schedule) {
    state.schedules.push(schedule)
  },
  UPDATE_SCHEDULE(state, updatedSchedule) {
    const index = state.schedules.findIndex(s => s.id === updatedSchedule.id)
    if (index !== -1) {
      state.schedules.splice(index, 1, updatedSchedule)
    }
  },
  REMOVE_SCHEDULE(state, scheduleId) {
    state.schedules = state.schedules.filter(s => s.id !== scheduleId)
  },
  SET_EXAM_PERIODS(state, periods) {
    state.examPeriods = periods
  },
  SET_CURRENT_EXAM_PERIOD(state, period) {
    state.currentExamPeriod = period
  },
  SET_SUBJECTS(state, subjects) {
    state.subjects = subjects
  },
  SET_GROUPS(state, groups) {
    state.groups = groups
  },
  SET_ROOMS(state, rooms) {
    state.rooms = rooms
  },
  SET_TEACHERS(state, teachers) {
    state.teachers = teachers
  },
  SET_CONFLICTS(state, conflicts) {
    state.conflicts = conflicts
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
  // Obține toate planificările
  async fetchSchedules({ commit, rootState }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get('/api/schedule', {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_SCHEDULES', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la obținerea planificărilor')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Obține o planificare după ID
  async fetchScheduleById({ commit, rootState }, scheduleId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get(`/api/schedule/${scheduleId}`, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_CURRENT_SCHEDULE', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la obținerea planificării')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Creează o nouă planificare
  async createSchedule({ commit, rootState }, scheduleData) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.post('/api/schedule', scheduleData, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('ADD_SCHEDULE', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la crearea planificării')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Actualizează o planificare existentă
  async updateSchedule({ commit, rootState }, { scheduleId, scheduleData }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.put(`/api/schedule/${scheduleId}`, scheduleData, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('UPDATE_SCHEDULE', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la actualizarea planificării')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Șterge o planificare
  async deleteSchedule({ commit, rootState }, scheduleId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      await axios.delete(`/api/schedule/${scheduleId}`, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('REMOVE_SCHEDULE', scheduleId)
      
      return true
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la ștergerea planificării')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Obține toate perioadele de examinare
  async fetchExamPeriods({ commit, rootState }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get('/api/exam-periods', {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_EXAM_PERIODS', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la obținerea perioadelor de examinare')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Obține toate disciplinele
  async fetchSubjects({ commit, rootState }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get('/api/subjects', {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_SUBJECTS', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la obținerea disciplinelor')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Obține toate grupele
  async fetchGroups({ commit, rootState }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get('/api/orar/groups', {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_GROUPS', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la obținerea grupelor')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Obține toate sălile
  async fetchRooms({ commit, rootState }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get('/api/orar/rooms', {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_ROOMS', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la obținerea sălilor')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Obține toate cadrele didactice
  async fetchTeachers({ commit, rootState }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get('/api/orar/teachers', {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_TEACHERS', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la obținerea cadrelor didactice')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Verifică conflictele pentru o planificare
  async checkConflicts({ commit, rootState }, scheduleData) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.post('/api/schedule/check-conflicts', scheduleData, {
        headers: {
          Authorization: `Bearer ${rootState.auth.token}`
        }
      })
      
      commit('SET_CONFLICTS', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Eroare la verificarea conflictelor')
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
