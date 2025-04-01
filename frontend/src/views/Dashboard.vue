<template>
  <div class="dashboard-container">
    <h1 class="text-3xl font-bold mb-4">Dashboard</h1>
    
    <div class="grid">
      <!-- Statistici generale -->
      <div class="col-12 lg:col-6 xl:col-3">
        <Card class="mb-4 dashboard-card">
          <template #header>
            <div class="flex align-items-center justify-content-between">
              <h2 class="text-xl font-bold m-0">Examene Planificate</h2>
              <i class="pi pi-calendar text-2xl text-primary"></i>
            </div>
          </template>
          <template #content>
            <div class="text-center">
              <span class="text-5xl font-bold">{{ schedulesCount }}</span>
              <p class="mt-2">în perioada curentă</p>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-6 xl:col-3">
        <Card class="mb-4 dashboard-card">
          <template #header>
            <div class="flex align-items-center justify-content-between">
              <h2 class="text-xl font-bold m-0">Notificări</h2>
              <i class="pi pi-bell text-2xl text-warning"></i>
            </div>
          </template>
          <template #content>
            <div class="text-center">
              <span class="text-5xl font-bold">{{ unreadNotificationsCount }}</span>
              <p class="mt-2">necitite</p>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-6 xl:col-3">
        <Card class="mb-4 dashboard-card">
          <template #header>
            <div class="flex align-items-center justify-content-between">
              <h2 class="text-xl font-bold m-0">Săli Disponibile</h2>
              <i class="pi pi-building text-2xl text-success"></i>
            </div>
          </template>
          <template #content>
            <div class="text-center">
              <span class="text-5xl font-bold">{{ availableRoomsCount }}</span>
              <p class="mt-2">pentru astăzi</p>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-6 xl:col-3">
        <Card class="mb-4 dashboard-card">
          <template #header>
            <div class="flex align-items-center justify-content-between">
              <h2 class="text-xl font-bold m-0">Utilizatori</h2>
              <i class="pi pi-users text-2xl text-info"></i>
            </div>
          </template>
          <template #content>
            <div class="text-center">
              <span class="text-5xl font-bold">{{ usersCount }}</span>
              <p class="mt-2">activi în sistem</p>
            </div>
          </template>
        </Card>
      </div>
      
      <!-- Examene recente -->
      <div class="col-12 lg:col-8">
        <Card class="mb-4">
          <template #header>
            <div class="flex align-items-center justify-content-between">
              <h2 class="text-xl font-bold m-0">Examene Recente</h2>
              <Button 
                icon="pi pi-external-link" 
                label="Vezi toate" 
                class="p-button-text p-button-sm"
                @click="navigateToSchedule"
              />
            </div>
          </template>
          <template #content>
            <DataTable :value="recentSchedules" :paginator="false" :rows="5" responsiveLayout="scroll">
              <Column field="subject.name" header="Disciplină">
                <template #body="slotProps">
                  <span>{{ slotProps.data.subject?.name || 'N/A' }}</span>
                </template>
              </Column>
              <Column field="date" header="Data">
                <template #body="slotProps">
                  <span>{{ formatDate(slotProps.data.date) }}</span>
                </template>
              </Column>
              <Column field="startTime" header="Ora">
                <template #body="slotProps">
                  <span>{{ slotProps.data.startTime }} - {{ slotProps.data.endTime }}</span>
                </template>
              </Column>
              <Column field="room.name" header="Sală">
                <template #body="slotProps">
                  <span>{{ slotProps.data.room?.name || 'N/A' }}</span>
                </template>
              </Column>
              <Column field="teacher.name" header="Profesor">
                <template #body="slotProps">
                  <span>{{ slotProps.data.teacher?.lastName || 'N/A' }} {{ slotProps.data.teacher?.firstName || '' }}</span>
                </template>
              </Column>
              <Column header="Acțiuni">
                <template #body="slotProps">
                  <Button 
                    icon="pi pi-eye" 
                    class="p-button-rounded p-button-text p-button-sm"
                    @click="viewSchedule(slotProps.data.id)"
                  />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
      
      <!-- Notificări recente -->
      <div class="col-12 lg:col-4">
        <Card class="mb-4">
          <template #header>
            <div class="flex align-items-center justify-content-between">
              <h2 class="text-xl font-bold m-0">Notificări Recente</h2>
              <Button 
                icon="pi pi-external-link" 
                label="Vezi toate" 
                class="p-button-text p-button-sm"
                @click="navigateToNotifications"
              />
            </div>
          </template>
          <template #content>
            <div v-if="recentNotifications.length === 0" class="text-center p-4">
              <i class="pi pi-inbox text-5xl text-color-secondary mb-3"></i>
              <p>Nu aveți notificări recente</p>
            </div>
            <ul v-else class="notification-list p-0">
              <li v-for="notification in recentNotifications" :key="notification.id" class="notification-item p-3 mb-2">
                <div class="flex align-items-start">
                  <i :class="getNotificationIcon(notification.type)" class="notification-icon mr-3 text-xl"></i>
                  <div class="notification-content flex-1">
                    <div class="flex align-items-center justify-content-between mb-1">
                      <h3 class="text-base font-bold m-0">{{ notification.title }}</h3>
                      <span class="text-sm text-color-secondary">{{ formatTimeAgo(notification.createdAt) }}</span>
                    </div>
                    <p class="m-0 notification-message">{{ notification.message }}</p>
                  </div>
                </div>
              </li>
            </ul>
          </template>
        </Card>
      </div>
      
      <!-- Calendar cu examene -->
      <div class="col-12">
        <Card>
          <template #header>
            <div class="flex align-items-center justify-content-between">
              <h2 class="text-xl font-bold m-0">Calendar Examene</h2>
              <div>
                <Button 
                  icon="pi pi-calendar-plus" 
                  label="Adaugă Examen" 
                  class="p-button-sm mr-2"
                  v-if="canCreateSchedule"
                  @click="navigateToCreateSchedule"
                />
                <Button 
                  icon="pi pi-file-export" 
                  label="Export" 
                  class="p-button-sm p-button-outlined"
                  v-if="canExportSchedule"
                  @click="navigateToExport"
                />
              </div>
            </div>
          </template>
          <template #content>
            <Calendar 
              v-model="selectedDate" 
              :inline="true" 
              :showWeek="true"
              :dateTemplate="dateTemplate"
            />
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import moment from 'moment'

export default {
  name: 'Dashboard',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const selectedDate = ref(new Date())
    
    // Obținem datele din store
    const user = computed(() => store.state.auth.user)
    const schedules = computed(() => store.state.schedule.schedules)
    const notifications = computed(() => store.state.notification.notifications)
    const rooms = computed(() => store.state.schedule.rooms)
    const users = computed(() => store.state.user.users)
    
    // Calculăm statisticile
    const schedulesCount = computed(() => schedules.value.length)
    const unreadNotificationsCount = computed(() => store.state.notification.unreadCount)
    const availableRoomsCount = computed(() => rooms.value.length)
    const usersCount = computed(() => users.value.length)
    
    // Obținem examenele recente
    const recentSchedules = computed(() => {
      return [...schedules.value]
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .slice(0, 5)
    })
    
    // Obținem notificările recente
    const recentNotifications = computed(() => {
      return [...notifications.value]
        .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
        .slice(0, 5)
    })
    
    // Verificăm permisiunile utilizatorului
    const canCreateSchedule = computed(() => {
      return user.value && ['ADM', 'SEC'].includes(user.value.role)
    })
    
    const canExportSchedule = computed(() => {
      return user.value && ['ADM', 'SEC'].includes(user.value.role)
    })
    
    // Funcție pentru formatarea datei
    const formatDate = (dateString) => {
      return moment(dateString).format('DD.MM.YYYY')
    }
    
    // Funcție pentru formatarea timpului relativ
    const formatTimeAgo = (dateString) => {
      return moment(dateString).fromNow()
    }
    
    // Funcție pentru obținerea iconului notificării
    const getNotificationIcon = (type) => {
      switch (type) {
        case 'SCHEDULE_CREATED': return 'pi pi-calendar-plus text-success'
        case 'SCHEDULE_UPDATED': return 'pi pi-calendar-times text-warning'
        case 'SCHEDULE_DELETED': return 'pi pi-calendar-minus text-danger'
        case 'SYSTEM': return 'pi pi-info-circle text-info'
        default: return 'pi pi-bell text-primary'
      }
    }
    
    // Funcție pentru template-ul de dată în calendar
    const dateTemplate = (date) => {
      // Verificăm dacă există examene în această zi
      const hasSchedules = schedules.value.some(schedule => {
        const scheduleDate = new Date(schedule.date)
        return scheduleDate.getDate() === date.day && 
               scheduleDate.getMonth() === date.month && 
               scheduleDate.getFullYear() === date.year
      })
      
      return {
        class: hasSchedules ? 'has-schedules' : ''
      }
    }
    
    // Funcții de navigare
    const navigateToSchedule = () => {
      router.push('/schedule')
    }
    
    const navigateToNotifications = () => {
      router.push('/notifications')
    }
    
    const navigateToCreateSchedule = () => {
      router.push('/schedule/create')
    }
    
    const navigateToExport = () => {
      router.push('/export')
    }
    
    const viewSchedule = (scheduleId) => {
      router.push(`/schedule/${scheduleId}`)
    }
    
    // Încărcăm datele la montarea componentei
    onMounted(async () => {
      try {
        // Încărcăm planificările
        if (schedules.value.length === 0) {
          await store.dispatch('schedule/fetchSchedules')
        }
        
        // Încărcăm notificările
        if (notifications.value.length === 0) {
          await store.dispatch('notification/fetchNotifications')
        }
        
        // Încărcăm sălile
        if (rooms.value.length === 0) {
          await store.dispatch('schedule/fetchRooms')
        }
        
        // Încărcăm utilizatorii (doar pentru administratori)
        if (user.value && user.value.role === 'ADM' && users.value.length === 0) {
          await store.dispatch('user/fetchUsers')
        }
      } catch (error) {
        console.error('Eroare la încărcarea datelor:', error)
      }
    })
    
    return {
      selectedDate,
      schedulesCount,
      unreadNotificationsCount,
      availableRoomsCount,
      usersCount,
      recentSchedules,
      recentNotifications,
      canCreateSchedule,
      canExportSchedule,
      formatDate,
      formatTimeAgo,
      getNotificationIcon,
      dateTemplate,
      navigateToSchedule,
      navigateToNotifications,
      navigateToCreateSchedule,
      navigateToExport,
      viewSchedule
    }
  }
}
</script>

<style scoped>
.dashboard-card {
  height: 100%;
}

.notification-list {
  list-style: none;
  max-height: 350px;
  overflow-y: auto;
}

.notification-item {
  border-radius: 4px;
  background-color: var(--surface-hover);
}

.notification-item:not(:last-child) {
  margin-bottom: 0.5rem;
}

.notification-message {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

:deep(.has-schedules) {
  background-color: var(--primary-100);
  color: var(--primary-700);
  font-weight: bold;
  border-radius: 50%;
}
</style>
