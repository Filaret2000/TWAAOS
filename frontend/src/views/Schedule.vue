<template>
  <div class="schedule-container">
    <div class="flex align-items-center justify-content-between mb-4">
      <h1 class="text-3xl font-bold m-0">Planificare Examene</h1>
      
      <div>
        <Button 
          v-if="canCreateSchedule" 
          icon="pi pi-plus" 
          label="Adaugă Planificare" 
          @click="openNewScheduleDialog"
          class="mr-2"
        />
        <Button 
          v-if="canExportSchedule" 
          icon="pi pi-file-export" 
          label="Export" 
          class="p-button-outlined"
          @click="navigateToExport"
        />
      </div>
    </div>
    
    <Card class="mb-4">
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6 lg:col-3 mb-3">
            <span class="p-float-label">
              <Dropdown 
                v-model="filters.examPeriod" 
                :options="examPeriods" 
                optionLabel="name" 
                optionValue="id"
                class="w-full"
                @change="loadSchedules"
              />
              <label>Perioada de examinare</label>
            </span>
          </div>
          
          <div class="col-12 md:col-6 lg:col-3 mb-3">
            <span class="p-float-label">
              <Calendar 
                v-model="filters.date" 
                dateFormat="dd.mm.yy" 
                class="w-full"
                @date-select="loadSchedules"
              />
              <label>Data</label>
            </span>
          </div>
          
          <div class="col-12 md:col-6 lg:col-3 mb-3">
            <span class="p-float-label">
              <Dropdown 
                v-model="filters.room" 
                :options="rooms" 
                optionLabel="name" 
                optionValue="id"
                class="w-full"
                @change="loadSchedules"
              />
              <label>Sală</label>
            </span>
          </div>
          
          <div class="col-12 md:col-6 lg:col-3 mb-3">
            <span class="p-float-label">
              <Dropdown 
                v-model="filters.teacher" 
                :options="teachers" 
                :optionLabel="teacherFullName" 
                optionValue="id"
                class="w-full"
                @change="loadSchedules"
              />
              <label>Cadru didactic</label>
            </span>
          </div>
          
          <div class="col-12">
            <div class="flex justify-content-end">
              <Button 
                icon="pi pi-filter-slash" 
                label="Resetează filtrele" 
                class="p-button-text"
                @click="resetFilters"
              />
            </div>
          </div>
        </div>
      </template>
    </Card>
    
    <DataTable 
      :value="filteredSchedules" 
      :paginator="true" 
      :rows="10"
      :rowsPerPageOptions="[10, 20, 50]"
      :loading="loading"
      responsiveLayout="scroll"
      v-model:selection="selectedSchedules"
      :filters="tableFilters"
      filterDisplay="menu"
      class="p-datatable-sm"
    >
      <template #empty>
        <div class="text-center p-4">
          <i class="pi pi-calendar-times text-5xl text-color-secondary mb-3"></i>
          <p>Nu există planificări care să corespundă criteriilor selectate.</p>
        </div>
      </template>
      
      <template #loading>
        <div class="text-center p-4">
          <i class="pi pi-spin pi-spinner text-5xl text-color-secondary mb-3"></i>
          <p>Se încarcă planificările...</p>
        </div>
      </template>
      
      <Column selectionMode="multiple" headerStyle="width: 3rem" v-if="canManageSchedules"></Column>
      
      <Column field="subject.name" header="Disciplină" sortable :filter="true" filterMatchMode="contains">
        <template #body="slotProps">
          <span>{{ slotProps.data.subject?.name || 'N/A' }}</span>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText 
            v-model="filterModel.value" 
            @input="filterCallback()" 
            placeholder="Caută disciplină" 
            class="p-column-filter w-full"
          />
        </template>
      </Column>
      
      <Column field="date" header="Data" sortable :filter="true" filterMatchMode="dateIs">
        <template #body="slotProps">
          <span>{{ formatDate(slotProps.data.date) }}</span>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <Calendar 
            v-model="filterModel.value" 
            dateFormat="dd.mm.yy" 
            @date-select="filterCallback()" 
            placeholder="Selectează data" 
            class="p-column-filter w-full"
          />
        </template>
      </Column>
      
      <Column field="startTime" header="Ora" sortable>
        <template #body="slotProps">
          <span>{{ slotProps.data.startTime }} - {{ slotProps.data.endTime }}</span>
        </template>
      </Column>
      
      <Column field="room.name" header="Sală" sortable :filter="true" filterMatchMode="contains">
        <template #body="slotProps">
          <span>{{ slotProps.data.room?.name || 'N/A' }}</span>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText 
            v-model="filterModel.value" 
            @input="filterCallback()" 
            placeholder="Caută sală" 
            class="p-column-filter w-full"
          />
        </template>
      </Column>
      
      <Column field="teacher.lastName" header="Cadru didactic" sortable :filter="true" filterMatchMode="contains">
        <template #body="slotProps">
          <span>{{ slotProps.data.teacher?.lastName || 'N/A' }} {{ slotProps.data.teacher?.firstName || '' }}</span>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText 
            v-model="filterModel.value" 
            @input="filterCallback()" 
            placeholder="Caută cadru didactic" 
            class="p-column-filter w-full"
          />
        </template>
      </Column>
      
      <Column field="groups" header="Grupe" :filter="true" filterMatchMode="contains">
        <template #body="slotProps">
          <span>{{ formatGroups(slotProps.data.groups) }}</span>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText 
            v-model="filterModel.value" 
            @input="filterCallback()" 
            placeholder="Caută grupă" 
            class="p-column-filter w-full"
          />
        </template>
      </Column>
      
      <Column header="Acțiuni" :exportable="false">
        <template #body="slotProps">
          <div class="flex">
            <Button 
              icon="pi pi-eye" 
              class="p-button-rounded p-button-text p-button-sm mr-2"
              @click="viewSchedule(slotProps.data)"
              v-tooltip.top="'Vizualizează detalii'"
            />
            <Button 
              v-if="canEditSchedule(slotProps.data)"
              icon="pi pi-pencil" 
              class="p-button-rounded p-button-text p-button-sm mr-2"
              @click="editSchedule(slotProps.data)"
              v-tooltip.top="'Editează'"
            />
            <Button 
              v-if="canDeleteSchedule(slotProps.data)"
              icon="pi pi-trash" 
              class="p-button-rounded p-button-text p-button-sm p-button-danger"
              @click="confirmDeleteSchedule(slotProps.data)"
              v-tooltip.top="'Șterge'"
            />
          </div>
        </template>
      </Column>
    </DataTable>
    
    <!-- Dialog pentru adăugarea/editarea unei planificări -->
    <ScheduleDialog 
      v-model:visible="scheduleDialog.visible"
      :schedule="scheduleDialog.schedule"
      :isEdit="scheduleDialog.isEdit"
      @save="saveSchedule"
    />
    
    <!-- Dialog pentru confirmarea ștergerii -->
    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useConfirm } from 'primevue/useconfirm'
import moment from 'moment'
import ScheduleDialog from '@/components/schedule/ScheduleDialog.vue'

export default {
  name: 'Schedule',
  components: {
    ScheduleDialog
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const confirm = useConfirm()
    
    const loading = ref(false)
    const selectedSchedules = ref([])
    
    // Filtre pentru tabel
    const tableFilters = ref({})
    
    // Filtre pentru căutare
    const filters = reactive({
      examPeriod: null,
      date: null,
      room: null,
      teacher: null
    })
    
    // Dialog pentru adăugarea/editarea unei planificări
    const scheduleDialog = reactive({
      visible: false,
      schedule: null,
      isEdit: false
    })
    
    // Obținem datele din store
    const user = computed(() => store.state.auth.user)
    const schedules = computed(() => store.state.schedule.schedules)
    const examPeriods = computed(() => store.state.schedule.examPeriods)
    const rooms = computed(() => store.state.schedule.rooms)
    const teachers = computed(() => store.state.schedule.teachers)
    
    // Verificăm permisiunile utilizatorului
    const canCreateSchedule = computed(() => {
      return user.value && ['ADM', 'SEC'].includes(user.value.role)
    })
    
    const canExportSchedule = computed(() => {
      return user.value && ['ADM', 'SEC'].includes(user.value.role)
    })
    
    const canManageSchedules = computed(() => {
      return user.value && ['ADM', 'SEC'].includes(user.value.role)
    })
    
    // Filtrăm planificările în funcție de filtrele selectate
    const filteredSchedules = computed(() => {
      let result = [...schedules.value]
      
      if (filters.examPeriod) {
        result = result.filter(schedule => schedule.examPeriodId === filters.examPeriod)
      }
      
      if (filters.date) {
        const filterDate = moment(filters.date).format('YYYY-MM-DD')
        result = result.filter(schedule => {
          const scheduleDate = moment(schedule.date).format('YYYY-MM-DD')
          return scheduleDate === filterDate
        })
      }
      
      if (filters.room) {
        result = result.filter(schedule => schedule.roomId === filters.room)
      }
      
      if (filters.teacher) {
        result = result.filter(schedule => schedule.teacherId === filters.teacher)
      }
      
      return result
    })
    
    // Funcție pentru formatarea numelui complet al cadrului didactic
    const teacherFullName = (teacher) => {
      return `${teacher.lastName} ${teacher.firstName}`
    }
    
    // Funcție pentru formatarea datei
    const formatDate = (dateString) => {
      return moment(dateString).format('DD.MM.YYYY')
    }
    
    // Funcție pentru formatarea grupelor
    const formatGroups = (groups) => {
      if (!groups || !groups.length) return 'N/A'
      return groups.map(group => group.name).join(', ')
    }
    
    // Funcție pentru verificarea permisiunii de editare a unei planificări
    const canEditSchedule = (schedule) => {
      if (!user.value) return false
      
      // Administratorii și secretariatul pot edita orice planificare
      if (['ADM', 'SEC'].includes(user.value.role)) return true
      
      // Cadrele didactice pot edita doar propriile planificări
      if (user.value.role === 'CD') {
        return schedule.teacherId === user.value.id
      }
      
      return false
    }
    
    // Funcție pentru verificarea permisiunii de ștergere a unei planificări
    const canDeleteSchedule = (schedule) => {
      if (!user.value) return false
      
      // Doar administratorii și secretariatul pot șterge planificări
      return ['ADM', 'SEC'].includes(user.value.role)
    }
    
    // Funcție pentru încărcarea planificărilor
    const loadSchedules = async () => {
      try {
        loading.value = true
        
        // Încărcăm planificările dacă nu sunt deja încărcate
        if (schedules.value.length === 0) {
          await store.dispatch('schedule/fetchSchedules')
        }
        
        // Încărcăm perioadele de examinare dacă nu sunt deja încărcate
        if (examPeriods.value.length === 0) {
          await store.dispatch('schedule/fetchExamPeriods')
        }
        
        // Încărcăm sălile dacă nu sunt deja încărcate
        if (rooms.value.length === 0) {
          await store.dispatch('schedule/fetchRooms')
        }
        
        // Încărcăm cadrele didactice dacă nu sunt deja încărcate
        if (teachers.value.length === 0) {
          await store.dispatch('schedule/fetchTeachers')
        }
      } catch (error) {
        console.error('Eroare la încărcarea datelor:', error)
      } finally {
        loading.value = false
      }
    }
    
    // Funcție pentru resetarea filtrelor
    const resetFilters = () => {
      filters.examPeriod = null
      filters.date = null
      filters.room = null
      filters.teacher = null
    }
    
    // Funcție pentru deschiderea dialogului de adăugare a unei noi planificări
    const openNewScheduleDialog = () => {
      scheduleDialog.schedule = {
        subjectId: null,
        teacherId: null,
        roomId: null,
        groups: [],
        date: null,
        startTime: null,
        endTime: null,
        examPeriodId: null,
        type: 'EXAMEN'
      }
      scheduleDialog.isEdit = false
      scheduleDialog.visible = true
    }
    
    // Funcție pentru vizualizarea unei planificări
    const viewSchedule = (schedule) => {
      router.push(`/schedule/${schedule.id}`)
    }
    
    // Funcție pentru editarea unei planificări
    const editSchedule = (schedule) => {
      scheduleDialog.schedule = { ...schedule }
      scheduleDialog.isEdit = true
      scheduleDialog.visible = true
    }
    
    // Funcție pentru confirmarea ștergerii unei planificări
    const confirmDeleteSchedule = (schedule) => {
      confirm.require({
        message: `Sunteți sigur că doriți să ștergeți planificarea pentru disciplina "${schedule.subject?.name}" din data de ${formatDate(schedule.date)}?`,
        header: 'Confirmare ștergere',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: () => deleteSchedule(schedule.id),
        reject: () => {}
      })
    }
    
    // Funcție pentru ștergerea unei planificări
    const deleteSchedule = async (scheduleId) => {
      try {
        loading.value = true
        await store.dispatch('schedule/deleteSchedule', scheduleId)
        
        // Afișăm un mesaj de succes
        store.dispatch('toast/add', {
          severity: 'success',
          summary: 'Succes',
          detail: 'Planificarea a fost ștearsă cu succes',
          life: 3000
        })
      } catch (error) {
        console.error('Eroare la ștergerea planificării:', error)
        
        // Afișăm un mesaj de eroare
        store.dispatch('toast/add', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'A apărut o eroare la ștergerea planificării',
          life: 3000
        })
      } finally {
        loading.value = false
      }
    }
    
    // Funcție pentru salvarea unei planificări
    const saveSchedule = async (schedule) => {
      try {
        loading.value = true
        
        if (scheduleDialog.isEdit) {
          // Actualizăm planificarea existentă
          await store.dispatch('schedule/updateSchedule', {
            scheduleId: schedule.id,
            scheduleData: schedule
          })
          
          // Afișăm un mesaj de succes
          store.dispatch('toast/add', {
            severity: 'success',
            summary: 'Succes',
            detail: 'Planificarea a fost actualizată cu succes',
            life: 3000
          })
        } else {
          // Creăm o nouă planificare
          await store.dispatch('schedule/createSchedule', schedule)
          
          // Afișăm un mesaj de succes
          store.dispatch('toast/add', {
            severity: 'success',
            summary: 'Succes',
            detail: 'Planificarea a fost creată cu succes',
            life: 3000
          })
        }
        
        // Închidem dialogul
        scheduleDialog.visible = false
      } catch (error) {
        console.error('Eroare la salvarea planificării:', error)
        
        // Afișăm un mesaj de eroare
        store.dispatch('toast/add', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'A apărut o eroare la salvarea planificării',
          life: 3000
        })
      } finally {
        loading.value = false
      }
    }
    
    // Funcție pentru navigarea către pagina de export
    const navigateToExport = () => {
      router.push('/export')
    }
    
    // Încărcăm datele la montarea componentei
    onMounted(() => {
      loadSchedules()
    })
    
    return {
      loading,
      selectedSchedules,
      tableFilters,
      filters,
      scheduleDialog,
      filteredSchedules,
      examPeriods,
      rooms,
      teachers,
      canCreateSchedule,
      canExportSchedule,
      canManageSchedules,
      teacherFullName,
      formatDate,
      formatGroups,
      canEditSchedule,
      canDeleteSchedule,
      loadSchedules,
      resetFilters,
      openNewScheduleDialog,
      viewSchedule,
      editSchedule,
      confirmDeleteSchedule,
      saveSchedule,
      navigateToExport
    }
  }
}
</script>

<style scoped>
.schedule-container {
  padding-bottom: 2rem;
}
</style>
