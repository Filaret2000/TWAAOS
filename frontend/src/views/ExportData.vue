<template>
  <div class="export-container">
    <div class="flex align-items-center justify-content-between mb-4">
      <h1 class="text-3xl font-bold m-0">Export Date</h1>
    </div>
    
    <Card class="mb-4">
      <template #header>
        <h2 class="text-xl font-bold m-0">Opțiuni Export</h2>
      </template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6 mb-3">
            <div class="field">
              <label for="exportType" class="font-bold mb-2">Format Export</label>
              <div class="p-formgroup-inline">
                <div class="field-radiobutton mr-4">
                  <RadioButton 
                    id="exportTypeExcel" 
                    name="exportType" 
                    value="EXCEL" 
                    v-model="exportOptions.format"
                  />
                  <label for="exportTypeExcel">Excel</label>
                </div>
                <div class="field-radiobutton mr-4">
                  <RadioButton 
                    id="exportTypePdf" 
                    name="exportType" 
                    value="PDF" 
                    v-model="exportOptions.format"
                  />
                  <label for="exportTypePdf">PDF</label>
                </div>
                <div class="field-radiobutton">
                  <RadioButton 
                    id="exportTypeCsv" 
                    name="exportType" 
                    value="CSV" 
                    v-model="exportOptions.format"
                  />
                  <label for="exportTypeCsv">CSV</label>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-12 md:col-6 mb-3">
            <div class="field">
              <label for="exportContent" class="font-bold mb-2">Conținut Export</label>
              <div class="p-formgroup-inline">
                <div class="field-radiobutton mr-4">
                  <RadioButton 
                    id="exportContentAll" 
                    name="exportContent" 
                    value="ALL" 
                    v-model="exportOptions.content"
                  />
                  <label for="exportContentAll">Toate planificările</label>
                </div>
                <div class="field-radiobutton mr-4">
                  <RadioButton 
                    id="exportContentFiltered" 
                    name="exportContent" 
                    value="FILTERED" 
                    v-model="exportOptions.content"
                  />
                  <label for="exportContentFiltered">Planificări filtrate</label>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-12 md:col-6 mb-3">
            <div class="field">
              <label for="examPeriod" class="font-bold">Perioada de examinare</label>
              <Dropdown 
                id="examPeriod" 
                v-model="exportOptions.examPeriodId" 
                :options="examPeriods" 
                optionLabel="name" 
                optionValue="id"
                placeholder="Selectați perioada de examinare"
                class="w-full"
                :disabled="exportOptions.content === 'ALL'"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-6 mb-3">
            <div class="field">
              <label for="groupBy" class="font-bold">Grupare după</label>
              <Dropdown 
                id="groupBy" 
                v-model="exportOptions.groupBy" 
                :options="groupByOptions" 
                optionLabel="name" 
                optionValue="code"
                placeholder="Selectați criteriul de grupare"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="col-12 mb-3" v-if="exportOptions.content === 'FILTERED'">
            <Fieldset legend="Filtre suplimentare">
              <div class="grid">
                <div class="col-12 md:col-6 lg:col-4 mb-3">
                  <div class="field">
                    <label for="teacher" class="font-bold">Cadru didactic</label>
                    <Dropdown 
                      id="teacher" 
                      v-model="exportOptions.teacherId" 
                      :options="teachers" 
                      :optionLabel="teacherFullName" 
                      optionValue="id"
                      placeholder="Selectați cadrul didactic"
                      class="w-full"
                    />
                  </div>
                </div>
                
                <div class="col-12 md:col-6 lg:col-4 mb-3">
                  <div class="field">
                    <label for="group" class="font-bold">Grupă</label>
                    <Dropdown 
                      id="group" 
                      v-model="exportOptions.groupId" 
                      :options="groups" 
                      optionLabel="name" 
                      optionValue="id"
                      placeholder="Selectați grupa"
                      class="w-full"
                    />
                  </div>
                </div>
                
                <div class="col-12 md:col-6 lg:col-4 mb-3">
                  <div class="field">
                    <label for="room" class="font-bold">Sală</label>
                    <Dropdown 
                      id="room" 
                      v-model="exportOptions.roomId" 
                      :options="rooms" 
                      optionLabel="name" 
                      optionValue="id"
                      placeholder="Selectați sala"
                      class="w-full"
                    />
                  </div>
                </div>
                
                <div class="col-12 md:col-6 mb-3">
                  <div class="field">
                    <label for="startDate" class="font-bold">Data început</label>
                    <Calendar 
                      id="startDate" 
                      v-model="exportOptions.startDate" 
                      dateFormat="dd.mm.yy" 
                      placeholder="Selectați data de început"
                      class="w-full"
                    />
                  </div>
                </div>
                
                <div class="col-12 md:col-6 mb-3">
                  <div class="field">
                    <label for="endDate" class="font-bold">Data sfârșit</label>
                    <Calendar 
                      id="endDate" 
                      v-model="exportOptions.endDate" 
                      dateFormat="dd.mm.yy" 
                      placeholder="Selectați data de sfârșit"
                      class="w-full"
                      :minDate="exportOptions.startDate"
                    />
                  </div>
                </div>
              </div>
            </Fieldset>
          </div>
          
          <div class="col-12 mb-3">
            <Fieldset legend="Opțiuni suplimentare">
              <div class="grid">
                <div class="col-12 md:col-6 mb-3">
                  <div class="field-checkbox">
                    <Checkbox 
                      id="includeHeader" 
                      v-model="exportOptions.includeHeader" 
                      binary
                    />
                    <label for="includeHeader" class="ml-2">Include antet cu informații FIESC</label>
                  </div>
                </div>
                
                <div class="col-12 md:col-6 mb-3">
                  <div class="field-checkbox">
                    <Checkbox 
                      id="includeFooter" 
                      v-model="exportOptions.includeFooter" 
                      binary
                    />
                    <label for="includeFooter" class="ml-2">Include subsol cu data generării</label>
                  </div>
                </div>
                
                <div class="col-12 md:col-6 mb-3">
                  <div class="field-checkbox">
                    <Checkbox 
                      id="landscape" 
                      v-model="exportOptions.landscape" 
                      binary
                      :disabled="exportOptions.format !== 'PDF'"
                    />
                    <label for="landscape" class="ml-2">Orientare peisaj (doar pentru PDF)</label>
                  </div>
                </div>
                
                <div class="col-12 md:col-6 mb-3">
                  <div class="field-checkbox">
                    <Checkbox 
                      id="sendEmail" 
                      v-model="exportOptions.sendEmail" 
                      binary
                    />
                    <label for="sendEmail" class="ml-2">Trimite și pe email</label>
                  </div>
                </div>
                
                <div class="col-12 mb-3" v-if="exportOptions.sendEmail">
                  <div class="field">
                    <label for="emailRecipients" class="font-bold">Destinatari email</label>
                    <Chips 
                      id="emailRecipients" 
                      v-model="exportOptions.emailRecipients" 
                      placeholder="Introduceți adresele de email și apăsați Enter"
                      class="w-full"
                      :class="{ 'p-invalid': submitted && exportOptions.sendEmail && (!exportOptions.emailRecipients || exportOptions.emailRecipients.length === 0) }"
                    />
                    <small v-if="submitted && exportOptions.sendEmail && (!exportOptions.emailRecipients || exportOptions.emailRecipients.length === 0)" class="p-error">Cel puțin o adresă de email este obligatorie.</small>
                  </div>
                </div>
              </div>
            </Fieldset>
          </div>
          
          <div class="col-12 flex justify-content-end">
            <Button 
              label="Generează Export" 
              icon="pi pi-file-export" 
              @click="generateExport"
              :loading="loading"
            />
          </div>
        </div>
      </template>
    </Card>
    
    <Card v-if="previousExports.length > 0">
      <template #header>
        <div class="flex align-items-center justify-content-between">
          <h2 class="text-xl font-bold m-0">Exporturi Recente</h2>
        </div>
      </template>
      <template #content>
        <DataTable :value="previousExports" :paginator="true" :rows="5" responsiveLayout="scroll">
          <Column field="createdAt" header="Data generării">
            <template #body="slotProps">
              <span>{{ formatDate(slotProps.data.createdAt) }}</span>
            </template>
          </Column>
          <Column field="format" header="Format">
            <template #body="slotProps">
              <Tag :value="slotProps.data.format" :severity="getFormatSeverity(slotProps.data.format)" />
            </template>
          </Column>
          <Column field="fileName" header="Nume fișier">
            <template #body="slotProps">
              <span>{{ slotProps.data.fileName }}</span>
            </template>
          </Column>
          <Column field="createdBy" header="Generat de">
            <template #body="slotProps">
              <span>{{ slotProps.data.createdBy?.lastName || 'N/A' }} {{ slotProps.data.createdBy?.firstName || '' }}</span>
            </template>
          </Column>
          <Column header="Acțiuni">
            <template #body="slotProps">
              <Button 
                icon="pi pi-download" 
                class="p-button-rounded p-button-text p-button-sm"
                @click="downloadExport(slotProps.data)"
                v-tooltip.top="'Descarcă'"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import moment from 'moment'

export default {
  name: 'ExportData',
  setup() {
    const store = useStore()
    
    const loading = ref(false)
    const submitted = ref(false)
    
    // Opțiuni pentru export
    const exportOptions = reactive({
      format: 'EXCEL',
      content: 'ALL',
      examPeriodId: null,
      groupBy: 'DATE',
      teacherId: null,
      groupId: null,
      roomId: null,
      startDate: null,
      endDate: null,
      includeHeader: true,
      includeFooter: true,
      landscape: false,
      sendEmail: false,
      emailRecipients: []
    })
    
    // Exporturi anterioare
    const previousExports = ref([])
    
    // Obținem datele din store
    const examPeriods = computed(() => store.state.schedule.examPeriods)
    const teachers = computed(() => store.state.schedule.teachers)
    const groups = computed(() => store.state.schedule.groups)
    const rooms = computed(() => store.state.schedule.rooms)
    
    // Opțiuni pentru grupare
    const groupByOptions = [
      { name: 'Data', code: 'DATE' },
      { name: 'Cadru didactic', code: 'TEACHER' },
      { name: 'Grupă', code: 'GROUP' },
      { name: 'Sală', code: 'ROOM' }
    ]
    
    // Funcție pentru formatarea numelui complet al cadrului didactic
    const teacherFullName = (teacher) => {
      return `${teacher.lastName} ${teacher.firstName}`
    }
    
    // Funcție pentru formatarea datei
    const formatDate = (dateString) => {
      return moment(dateString).format('DD.MM.YYYY HH:mm')
    }
    
    // Funcție pentru obținerea severității tag-ului pentru format
    const getFormatSeverity = (format) => {
      switch (format) {
        case 'EXCEL': return 'success'
        case 'PDF': return 'danger'
        case 'CSV': return 'info'
        default: return 'secondary'
      }
    }
    
    // Funcție pentru generarea exportului
    const generateExport = async () => {
      submitted.value = true
      
      // Verificăm dacă toate câmpurile obligatorii sunt completate
      if (exportOptions.sendEmail && (!exportOptions.emailRecipients || exportOptions.emailRecipients.length === 0)) {
        return
      }
      
      try {
        loading.value = true
        
        // Pregătim datele pentru export
        const exportData = {
          format: exportOptions.format,
          filters: {
            examPeriodId: exportOptions.content === 'ALL' ? null : exportOptions.examPeriodId,
            teacherId: exportOptions.content === 'ALL' ? null : exportOptions.teacherId,
            groupId: exportOptions.content === 'ALL' ? null : exportOptions.groupId,
            roomId: exportOptions.content === 'ALL' ? null : exportOptions.roomId,
            startDate: exportOptions.content === 'ALL' ? null : exportOptions.startDate ? moment(exportOptions.startDate).format('YYYY-MM-DD') : null,
            endDate: exportOptions.content === 'ALL' ? null : exportOptions.endDate ? moment(exportOptions.endDate).format('YYYY-MM-DD') : null
          },
          options: {
            groupBy: exportOptions.groupBy,
            includeHeader: exportOptions.includeHeader,
            includeFooter: exportOptions.includeFooter,
            landscape: exportOptions.landscape,
            sendEmail: exportOptions.sendEmail,
            emailRecipients: exportOptions.sendEmail ? exportOptions.emailRecipients : null
          }
        }
        
        // Trimitem cererea de export
        const response = await fetch('/api/export', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${store.state.auth.token}`
          },
          body: JSON.stringify(exportData)
        })
        
        if (!response.ok) {
          throw new Error('Eroare la generarea exportului')
        }
        
        // Obținem URL-ul pentru descărcare
        const result = await response.json()
        
        // Descărcăm fișierul
        if (result.downloadUrl) {
          window.location.href = result.downloadUrl
        }
        
        // Afișăm un mesaj de succes
        store.dispatch('toast/add', {
          severity: 'success',
          summary: 'Succes',
          detail: 'Exportul a fost generat cu succes',
          life: 3000
        })
        
        // Reîncărcăm exporturile anterioare
        loadPreviousExports()
      } catch (error) {
        console.error('Eroare la generarea exportului:', error)
        
        // Afișăm un mesaj de eroare
        store.dispatch('toast/add', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'A apărut o eroare la generarea exportului',
          life: 3000
        })
      } finally {
        loading.value = false
      }
    }
    
    // Funcție pentru descărcarea unui export anterior
    const downloadExport = (exportItem) => {
      window.location.href = exportItem.downloadUrl
    }
    
    // Funcție pentru încărcarea exporturilor anterioare
    const loadPreviousExports = async () => {
      try {
        const response = await fetch('/api/export/history', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${store.state.auth.token}`
          }
        })
        
        if (!response.ok) {
          throw new Error('Eroare la încărcarea exporturilor anterioare')
        }
        
        const data = await response.json()
        previousExports.value = data
      } catch (error) {
        console.error('Eroare la încărcarea exporturilor anterioare:', error)
      }
    }
    
    // Încărcăm datele la montarea componentei
    onMounted(async () => {
      try {
        loading.value = true
        
        // Încărcăm perioadele de examinare
        if (examPeriods.value.length === 0) {
          await store.dispatch('schedule/fetchExamPeriods')
        }
        
        // Încărcăm cadrele didactice
        if (teachers.value.length === 0) {
          await store.dispatch('schedule/fetchTeachers')
        }
        
        // Încărcăm grupele
        if (groups.value.length === 0) {
          await store.dispatch('schedule/fetchGroups')
        }
        
        // Încărcăm sălile
        if (rooms.value.length === 0) {
          await store.dispatch('schedule/fetchRooms')
        }
        
        // Încărcăm exporturile anterioare
        await loadPreviousExports()
      } catch (error) {
        console.error('Eroare la încărcarea datelor:', error)
      } finally {
        loading.value = false
      }
    })
    
    return {
      loading,
      submitted,
      exportOptions,
      previousExports,
      examPeriods,
      teachers,
      groups,
      rooms,
      groupByOptions,
      teacherFullName,
      formatDate,
      getFormatSeverity,
      generateExport,
      downloadExport
    }
  }
}
</script>

<style scoped>
.export-container {
  padding-bottom: 2rem;
}
</style>
