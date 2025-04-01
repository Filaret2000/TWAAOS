<template>
  <Dialog 
    :visible="visible" 
    :style="{ width: '50vw' }" 
    :modal="true"
    :closable="false"
    :header="dialogTitle"
  >
    <div class="p-fluid">
      <div class="field">
        <label for="subject">Disciplină</label>
        <Dropdown 
          id="subject" 
          v-model="formData.subjectId" 
          :options="subjects" 
          optionLabel="name" 
          optionValue="id"
          placeholder="Selectați disciplina"
          :class="{ 'p-invalid': submitted && !formData.subjectId }"
        />
        <small v-if="submitted && !formData.subjectId" class="p-error">Disciplina este obligatorie.</small>
      </div>
      
      <div class="field">
        <label for="teacher">Cadru didactic</label>
        <Dropdown 
          id="teacher" 
          v-model="formData.teacherId" 
          :options="teachers" 
          :optionLabel="teacherFullName" 
          optionValue="id"
          placeholder="Selectați cadrul didactic"
          :class="{ 'p-invalid': submitted && !formData.teacherId }"
        />
        <small v-if="submitted && !formData.teacherId" class="p-error">Cadrul didactic este obligatoriu.</small>
      </div>
      
      <div class="field">
        <label for="groups">Grupe</label>
        <MultiSelect 
          id="groups" 
          v-model="selectedGroups" 
          :options="groups" 
          optionLabel="name" 
          placeholder="Selectați grupele"
          :class="{ 'p-invalid': submitted && (!selectedGroups || selectedGroups.length === 0) }"
          display="chip"
        />
        <small v-if="submitted && (!selectedGroups || selectedGroups.length === 0)" class="p-error">Cel puțin o grupă este obligatorie.</small>
      </div>
      
      <div class="field">
        <label for="room">Sală</label>
        <Dropdown 
          id="room" 
          v-model="formData.roomId" 
          :options="rooms" 
          optionLabel="name" 
          optionValue="id"
          placeholder="Selectați sala"
          :class="{ 'p-invalid': submitted && !formData.roomId }"
        />
        <small v-if="submitted && !formData.roomId" class="p-error">Sala este obligatorie.</small>
      </div>
      
      <div class="field">
        <label for="examPeriod">Perioada de examinare</label>
        <Dropdown 
          id="examPeriod" 
          v-model="formData.examPeriodId" 
          :options="examPeriods" 
          optionLabel="name" 
          optionValue="id"
          placeholder="Selectați perioada de examinare"
          :class="{ 'p-invalid': submitted && !formData.examPeriodId }"
        />
        <small v-if="submitted && !formData.examPeriodId" class="p-error">Perioada de examinare este obligatorie.</small>
      </div>
      
      <div class="field">
        <label for="date">Data</label>
        <Calendar 
          id="date" 
          v-model="formData.date" 
          dateFormat="dd.mm.yy" 
          placeholder="Selectați data"
          :class="{ 'p-invalid': submitted && !formData.date }"
          :minDate="minDate"
          :maxDate="maxDate"
        />
        <small v-if="submitted && !formData.date" class="p-error">Data este obligatorie.</small>
      </div>
      
      <div class="grid">
        <div class="col-6 field">
          <label for="startTime">Ora de început</label>
          <Dropdown 
            id="startTime" 
            v-model="formData.startTime" 
            :options="timeOptions" 
            placeholder="Selectați ora de început"
            :class="{ 'p-invalid': submitted && !formData.startTime }"
            @change="updateEndTimeOptions"
          />
          <small v-if="submitted && !formData.startTime" class="p-error">Ora de început este obligatorie.</small>
        </div>
        
        <div class="col-6 field">
          <label for="endTime">Ora de sfârșit</label>
          <Dropdown 
            id="endTime" 
            v-model="formData.endTime" 
            :options="filteredEndTimeOptions" 
            placeholder="Selectați ora de sfârșit"
            :class="{ 'p-invalid': submitted && !formData.endTime }"
            :disabled="!formData.startTime"
          />
          <small v-if="submitted && !formData.endTime" class="p-error">Ora de sfârșit este obligatorie.</small>
        </div>
      </div>
      
      <div class="field">
        <label for="type">Tip examen</label>
        <Dropdown 
          id="type" 
          v-model="formData.type" 
          :options="examTypes" 
          optionLabel="name" 
          optionValue="code"
          placeholder="Selectați tipul de examen"
          :class="{ 'p-invalid': submitted && !formData.type }"
        />
        <small v-if="submitted && !formData.type" class="p-error">Tipul de examen este obligatoriu.</small>
      </div>
      
      <div class="field">
        <label for="notes">Observații</label>
        <Textarea 
          id="notes" 
          v-model="formData.notes" 
          rows="3" 
          placeholder="Introduceți observații (opțional)"
        />
      </div>
    </div>
    
    <template #footer>
      <Button 
        label="Anulează" 
        icon="pi pi-times" 
        class="p-button-text" 
        @click="hideDialog"
      />
      <Button 
        label="Verifică conflicte" 
        icon="pi pi-search" 
        class="p-button-outlined mr-2" 
        @click="checkConflicts"
        :loading="checkingConflicts"
      />
      <Button 
        label="Salvează" 
        icon="pi pi-check" 
        class="p-button-primary" 
        @click="saveSchedule"
        :loading="saving"
      />
    </template>
  </Dialog>
  
  <!-- Dialog pentru afișarea conflictelor -->
  <Dialog 
    v-model:visible="conflictsDialog.visible" 
    :style="{ width: '40vw' }" 
    :modal="true"
    header="Conflicte detectate"
  >
    <div v-if="conflictsDialog.conflicts.length > 0">
      <p class="text-lg font-bold text-red-500 mb-3">
        Au fost detectate următoarele conflicte:
      </p>
      
      <ul class="conflict-list">
        <li v-for="(conflict, index) in conflictsDialog.conflicts" :key="index" class="conflict-item p-3 mb-2">
          <div class="conflict-type font-bold mb-1">{{ getConflictTypeLabel(conflict.type) }}</div>
          <div class="conflict-details">{{ conflict.message }}</div>
        </li>
      </ul>
      
      <p class="mt-3">
        Doriți să continuați cu salvarea planificării în ciuda conflictelor?
      </p>
    </div>
    
    <div v-else class="text-center">
      <i class="pi pi-check-circle text-5xl text-green-500 mb-3"></i>
      <p class="text-lg">Nu au fost detectate conflicte.</p>
    </div>
    
    <template #footer>
      <Button 
        v-if="conflictsDialog.conflicts.length > 0"
        label="Anulează" 
        icon="pi pi-times" 
        class="p-button-text" 
        @click="conflictsDialog.visible = false"
      />
      <Button 
        label="Continuă" 
        icon="pi pi-check" 
        :class="conflictsDialog.conflicts.length > 0 ? 'p-button-warning' : 'p-button-success'" 
        @click="proceedWithSave"
      />
    </template>
  </Dialog>
</template>

<script>
import { ref, computed, watch, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import moment from 'moment'

export default {
  name: 'ScheduleDialog',
  props: {
    visible: {
      type: Boolean,
      required: true
    },
    schedule: {
      type: Object,
      default: null
    },
    isEdit: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:visible', 'save'],
  setup(props, { emit }) {
    const store = useStore()
    
    const submitted = ref(false)
    const saving = ref(false)
    const checkingConflicts = ref(false)
    const selectedGroups = ref([])
    
    // Dialog pentru conflicte
    const conflictsDialog = reactive({
      visible: false,
      conflicts: []
    })
    
    // Datele formularului
    const formData = reactive({
      id: null,
      subjectId: null,
      teacherId: null,
      roomId: null,
      date: null,
      startTime: null,
      endTime: null,
      examPeriodId: null,
      type: 'EXAMEN',
      notes: ''
    })
    
    // Obținem datele din store
    const subjects = computed(() => store.state.schedule.subjects)
    const teachers = computed(() => store.state.schedule.teachers)
    const groups = computed(() => store.state.schedule.groups)
    const rooms = computed(() => store.state.schedule.rooms)
    const examPeriods = computed(() => store.state.schedule.examPeriods)
    
    // Opțiuni pentru tipurile de examen
    const examTypes = [
      { name: 'Examen', code: 'EXAMEN' },
      { name: 'Colocviu', code: 'COLOCVIU' },
      { name: 'Verificare', code: 'VERIFICARE' },
      { name: 'Restanță', code: 'RESTANTA' },
      { name: 'Mărire', code: 'MARIRE' }
    ]
    
    // Opțiuni pentru orele de început și sfârșit
    const timeOptions = [
      '08:00', '09:00', '10:00', '11:00', '12:00', 
      '13:00', '14:00', '15:00', '16:00', '17:00', 
      '18:00', '19:00', '20:00'
    ]
    
    // Filtrăm opțiunile pentru ora de sfârșit în funcție de ora de început
    const filteredEndTimeOptions = ref([])
    
    // Actualizăm opțiunile pentru ora de sfârșit
    const updateEndTimeOptions = () => {
      if (!formData.startTime) {
        filteredEndTimeOptions.value = []
        return
      }
      
      const startIndex = timeOptions.findIndex(time => time === formData.startTime)
      if (startIndex === -1) return
      
      // Ora de sfârșit trebuie să fie după ora de început
      filteredEndTimeOptions.value = timeOptions.slice(startIndex + 1)
      
      // Resetăm ora de sfârșit dacă nu mai este validă
      if (formData.endTime && !filteredEndTimeOptions.value.includes(formData.endTime)) {
        formData.endTime = null
      }
    }
    
    // Calculăm data minimă și maximă în funcție de perioada de examinare selectată
    const minDate = computed(() => {
      if (!formData.examPeriodId) return null
      
      const examPeriod = examPeriods.value.find(period => period.id === formData.examPeriodId)
      if (!examPeriod) return null
      
      return new Date(examPeriod.startDate)
    })
    
    const maxDate = computed(() => {
      if (!formData.examPeriodId) return null
      
      const examPeriod = examPeriods.value.find(period => period.id === formData.examPeriodId)
      if (!examPeriod) return null
      
      return new Date(examPeriod.endDate)
    })
    
    // Titlul dialogului
    const dialogTitle = computed(() => {
      return props.isEdit ? 'Editare Planificare' : 'Adăugare Planificare'
    })
    
    // Funcție pentru formatarea numelui complet al cadrului didactic
    const teacherFullName = (teacher) => {
      return `${teacher.lastName} ${teacher.firstName}`
    }
    
    // Funcție pentru obținerea etichetei tipului de conflict
    const getConflictTypeLabel = (type) => {
      switch (type) {
        case 'ROOM_CONFLICT': return 'Conflict de sală'
        case 'TEACHER_CONFLICT': return 'Conflict de cadru didactic'
        case 'GROUP_CONFLICT': return 'Conflict de grupă'
        case 'TIME_CONFLICT': return 'Conflict de timp'
        default: return 'Conflict'
      }
    }
    
    // Inițializăm formularul cu datele planificării
    const initForm = () => {
      if (props.schedule) {
        formData.id = props.schedule.id
        formData.subjectId = props.schedule.subjectId
        formData.teacherId = props.schedule.teacherId
        formData.roomId = props.schedule.roomId
        formData.date = props.schedule.date ? new Date(props.schedule.date) : null
        formData.startTime = props.schedule.startTime
        formData.endTime = props.schedule.endTime
        formData.examPeriodId = props.schedule.examPeriodId
        formData.type = props.schedule.type || 'EXAMEN'
        formData.notes = props.schedule.notes || ''
        
        // Setăm grupele selectate
        selectedGroups.value = props.schedule.groups || []
        
        // Actualizăm opțiunile pentru ora de sfârșit
        updateEndTimeOptions()
      } else {
        resetForm()
      }
    }
    
    // Resetăm formularul
    const resetForm = () => {
      formData.id = null
      formData.subjectId = null
      formData.teacherId = null
      formData.roomId = null
      formData.date = null
      formData.startTime = null
      formData.endTime = null
      formData.examPeriodId = null
      formData.type = 'EXAMEN'
      formData.notes = ''
      
      selectedGroups.value = []
      submitted.value = false
    }
    
    // Ascundem dialogul
    const hideDialog = () => {
      emit('update:visible', false)
      resetForm()
    }
    
    // Verificăm conflictele
    const checkConflicts = async () => {
      submitted.value = true
      
      // Verificăm dacă toate câmpurile obligatorii sunt completate
      if (!formData.subjectId || !formData.teacherId || !formData.roomId || 
          !formData.date || !formData.startTime || !formData.endTime || 
          !formData.examPeriodId || !formData.type || 
          !selectedGroups.value || selectedGroups.value.length === 0) {
        return
      }
      
      try {
        checkingConflicts.value = true
        
        // Pregătim datele pentru verificarea conflictelor
        const scheduleData = {
          id: formData.id,
          subjectId: formData.subjectId,
          teacherId: formData.teacherId,
          roomId: formData.roomId,
          date: moment(formData.date).format('YYYY-MM-DD'),
          startTime: formData.startTime,
          endTime: formData.endTime,
          examPeriodId: formData.examPeriodId,
          groupIds: selectedGroups.value.map(group => group.id)
        }
        
        // Verificăm conflictele
        const conflicts = await store.dispatch('schedule/checkConflicts', scheduleData)
        
        // Afișăm dialogul de conflicte
        conflictsDialog.conflicts = conflicts
        conflictsDialog.visible = true
      } catch (error) {
        console.error('Eroare la verificarea conflictelor:', error)
        
        // Afișăm un mesaj de eroare
        store.dispatch('toast/add', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'A apărut o eroare la verificarea conflictelor',
          life: 3000
        })
      } finally {
        checkingConflicts.value = false
      }
    }
    
    // Continuăm cu salvarea planificării după verificarea conflictelor
    const proceedWithSave = () => {
      conflictsDialog.visible = false
      saveSchedule(true)
    }
    
    // Salvăm planificarea
    const saveSchedule = async (skipConflictCheck = false) => {
      submitted.value = true
      
      // Verificăm dacă toate câmpurile obligatorii sunt completate
      if (!formData.subjectId || !formData.teacherId || !formData.roomId || 
          !formData.date || !formData.startTime || !formData.endTime || 
          !formData.examPeriodId || !formData.type || 
          !selectedGroups.value || selectedGroups.value.length === 0) {
        return
      }
      
      // Verificăm conflictele dacă nu am sărit peste această verificare
      if (!skipConflictCheck) {
        await checkConflicts()
        return
      }
      
      try {
        saving.value = true
        
        // Pregătim datele pentru salvare
        const scheduleData = {
          id: formData.id,
          subjectId: formData.subjectId,
          teacherId: formData.teacherId,
          roomId: formData.roomId,
          date: moment(formData.date).format('YYYY-MM-DD'),
          startTime: formData.startTime,
          endTime: formData.endTime,
          examPeriodId: formData.examPeriodId,
          type: formData.type,
          notes: formData.notes,
          groups: selectedGroups.value
        }
        
        // Emitem evenimentul de salvare
        emit('save', scheduleData)
        
        // Ascundem dialogul
        hideDialog()
      } catch (error) {
        console.error('Eroare la salvarea planificării:', error)
      } finally {
        saving.value = false
      }
    }
    
    // Observăm schimbările în props.visible
    watch(() => props.visible, (newValue) => {
      if (newValue) {
        initForm()
      }
    })
    
    // Observăm schimbările în props.schedule
    watch(() => props.schedule, (newValue) => {
      if (newValue && props.visible) {
        initForm()
      }
    })
    
    // Observăm schimbările în formData.examPeriodId
    watch(() => formData.examPeriodId, (newValue) => {
      if (newValue && formData.date) {
        // Verificăm dacă data selectată este în intervalul perioadei de examinare
        const date = moment(formData.date)
        const minDateMoment = moment(minDate.value)
        const maxDateMoment = moment(maxDate.value)
        
        if (date.isBefore(minDateMoment) || date.isAfter(maxDateMoment)) {
          formData.date = null
        }
      }
    })
    
    // Observăm schimbările în formData.startTime
    watch(() => formData.startTime, () => {
      updateEndTimeOptions()
    })
    
    // Încărcăm datele necesare la montarea componentei
    onMounted(async () => {
      try {
        // Încărcăm disciplinele dacă nu sunt deja încărcate
        if (subjects.value.length === 0) {
          await store.dispatch('schedule/fetchSubjects')
        }
        
        // Încărcăm cadrele didactice dacă nu sunt deja încărcate
        if (teachers.value.length === 0) {
          await store.dispatch('schedule/fetchTeachers')
        }
        
        // Încărcăm grupele dacă nu sunt deja încărcate
        if (groups.value.length === 0) {
          await store.dispatch('schedule/fetchGroups')
        }
        
        // Încărcăm sălile dacă nu sunt deja încărcate
        if (rooms.value.length === 0) {
          await store.dispatch('schedule/fetchRooms')
        }
        
        // Încărcăm perioadele de examinare dacă nu sunt deja încărcate
        if (examPeriods.value.length === 0) {
          await store.dispatch('schedule/fetchExamPeriods')
        }
      } catch (error) {
        console.error('Eroare la încărcarea datelor:', error)
      }
    })
    
    return {
      submitted,
      saving,
      checkingConflicts,
      selectedGroups,
      conflictsDialog,
      formData,
      subjects,
      teachers,
      groups,
      rooms,
      examPeriods,
      examTypes,
      timeOptions,
      filteredEndTimeOptions,
      minDate,
      maxDate,
      dialogTitle,
      teacherFullName,
      getConflictTypeLabel,
      updateEndTimeOptions,
      hideDialog,
      checkConflicts,
      proceedWithSave,
      saveSchedule
    }
  }
}
</script>

<style scoped>
.conflict-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.conflict-item {
  background-color: var(--red-50);
  border-left: 4px solid var(--red-500);
  border-radius: 4px;
}

.conflict-type {
  color: var(--red-700);
}
</style>
