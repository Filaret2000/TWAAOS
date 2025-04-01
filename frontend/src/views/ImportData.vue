<template>
  <div class="import-container">
    <div class="flex align-items-center justify-content-between mb-4">
      <h1 class="text-3xl font-bold m-0">Import Date</h1>
    </div>
    
    <Card class="mb-4">
      <template #header>
        <h2 class="text-xl font-bold m-0">Import Planificări Examene</h2>
      </template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6 mb-4">
            <div class="field">
              <label for="examPeriod" class="font-bold mb-2">Perioada de examinare</label>
              <Dropdown 
                id="examPeriod" 
                v-model="importOptions.examPeriodId" 
                :options="examPeriods" 
                optionLabel="name" 
                optionValue="id"
                placeholder="Selectați perioada de examinare"
                class="w-full"
                :class="{ 'p-invalid': submitted && !importOptions.examPeriodId }"
              />
              <small v-if="submitted && !importOptions.examPeriodId" class="p-error">Perioada de examinare este obligatorie.</small>
            </div>
          </div>
          
          <div class="col-12 md:col-6 mb-4">
            <div class="field">
              <label for="importType" class="font-bold mb-2">Tip import</label>
              <div class="p-formgroup-inline">
                <div class="field-radiobutton mr-4">
                  <RadioButton 
                    id="importTypeAdd" 
                    name="importType" 
                    value="ADD" 
                    v-model="importOptions.importType"
                  />
                  <label for="importTypeAdd">Adaugă noi planificări</label>
                </div>
                <div class="field-radiobutton">
                  <RadioButton 
                    id="importTypeReplace" 
                    name="importType" 
                    value="REPLACE" 
                    v-model="importOptions.importType"
                  />
                  <label for="importTypeReplace">Înlocuiește planificările existente</label>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-12 mb-4">
            <div class="field">
              <label for="importFile" class="font-bold mb-2">Fișier Excel</label>
              <FileUpload 
                id="importFile" 
                mode="advanced" 
                accept=".xlsx,.xls" 
                :maxFileSize="5000000"
                chooseLabel="Selectează fișier"
                uploadLabel="Încarcă"
                cancelLabel="Anulează"
                :customUpload="true"
                @uploader="onUpload"
                :auto="false"
                :class="{ 'p-invalid': submitted && !importFile }"
              />
              <small v-if="submitted && !importFile" class="p-error">Fișierul este obligatoriu.</small>
            </div>
          </div>
          
          <div class="col-12 mb-4">
            <Fieldset legend="Opțiuni suplimentare">
              <div class="grid">
                <div class="col-12 md:col-6 mb-3">
                  <div class="field-checkbox">
                    <Checkbox 
                      id="skipValidation" 
                      v-model="importOptions.skipValidation" 
                      binary
                    />
                    <label for="skipValidation" class="ml-2">Sari peste validarea datelor</label>
                  </div>
                </div>
                
                <div class="col-12 md:col-6 mb-3">
                  <div class="field-checkbox">
                    <Checkbox 
                      id="sendNotifications" 
                      v-model="importOptions.sendNotifications" 
                      binary
                    />
                    <label for="sendNotifications" class="ml-2">Trimite notificări utilizatorilor</label>
                  </div>
                </div>
                
                <div class="col-12 md:col-6 mb-3">
                  <div class="field-checkbox">
                    <Checkbox 
                      id="ignoreConflicts" 
                      v-model="importOptions.ignoreConflicts" 
                      binary
                    />
                    <label for="ignoreConflicts" class="ml-2">Ignoră conflictele</label>
                  </div>
                </div>
                
                <div class="col-12 md:col-6 mb-3">
                  <div class="field-checkbox">
                    <Checkbox 
                      id="dryRun" 
                      v-model="importOptions.dryRun" 
                      binary
                    />
                    <label for="dryRun" class="ml-2">Simulare (fără modificări efective)</label>
                  </div>
                </div>
              </div>
            </Fieldset>
          </div>
          
          <div class="col-12 flex justify-content-end">
            <Button 
              label="Descarcă Template" 
              icon="pi pi-download" 
              class="p-button-outlined mr-2"
              @click="downloadTemplate"
            />
            <Button 
              label="Importă Date" 
              icon="pi pi-upload" 
              @click="importData"
              :loading="loading"
            />
          </div>
        </div>
      </template>
    </Card>
    
    <Card v-if="importResult.visible">
      <template #header>
        <div class="flex align-items-center justify-content-between">
          <h2 class="text-xl font-bold m-0">Rezultat Import</h2>
          <Button 
            icon="pi pi-times" 
            class="p-button-rounded p-button-text p-button-sm"
            @click="importResult.visible = false"
          />
        </div>
      </template>
      <template #content>
        <div v-if="importResult.success" class="import-success">
          <div class="text-center mb-4">
            <i class="pi pi-check-circle text-5xl text-green-500 mb-3"></i>
            <h3 class="text-xl font-bold">Import finalizat cu succes</h3>
          </div>
          
          <div class="grid">
            <div class="col-12 md:col-4 mb-3">
              <div class="import-stat p-3 text-center border-round bg-green-50">
                <div class="text-3xl font-bold text-green-500 mb-2">{{ importResult.stats.added }}</div>
                <div class="text-sm">Planificări adăugate</div>
              </div>
            </div>
            
            <div class="col-12 md:col-4 mb-3">
              <div class="import-stat p-3 text-center border-round bg-blue-50">
                <div class="text-3xl font-bold text-blue-500 mb-2">{{ importResult.stats.updated }}</div>
                <div class="text-sm">Planificări actualizate</div>
              </div>
            </div>
            
            <div class="col-12 md:col-4 mb-3">
              <div class="import-stat p-3 text-center border-round bg-orange-50">
                <div class="text-3xl font-bold text-orange-500 mb-2">{{ importResult.stats.skipped }}</div>
                <div class="text-sm">Planificări ignorate</div>
              </div>
            </div>
          </div>
          
          <div v-if="importResult.warnings.length > 0" class="mt-4">
            <h4 class="text-lg font-bold mb-2">Avertismente</h4>
            <ul class="warning-list">
              <li v-for="(warning, index) in importResult.warnings" :key="index" class="warning-item p-3 mb-2">
                {{ warning }}
              </li>
            </ul>
          </div>
        </div>
        
        <div v-else class="import-error">
          <div class="text-center mb-4">
            <i class="pi pi-times-circle text-5xl text-red-500 mb-3"></i>
            <h3 class="text-xl font-bold">Import eșuat</h3>
          </div>
          
          <div v-if="importResult.errors.length > 0" class="mt-4">
            <h4 class="text-lg font-bold mb-2">Erori</h4>
            <ul class="error-list">
              <li v-for="(error, index) in importResult.errors" :key="index" class="error-item p-3 mb-2">
                {{ error }}
              </li>
            </ul>
          </div>
        </div>
      </template>
    </Card>
    
    <Card class="mt-4">
      <template #header>
        <h2 class="text-xl font-bold m-0">Istoric Importuri</h2>
      </template>
      <template #content>
        <DataTable :value="importHistory" :paginator="true" :rows="5" responsiveLayout="scroll">
          <Column field="createdAt" header="Data importului">
            <template #body="slotProps">
              <span>{{ formatDate(slotProps.data.createdAt) }}</span>
            </template>
          </Column>
          <Column field="fileName" header="Nume fișier">
            <template #body="slotProps">
              <span>{{ slotProps.data.fileName }}</span>
            </template>
          </Column>
          <Column field="importType" header="Tip import">
            <template #body="slotProps">
              <Tag :value="slotProps.data.importType" :severity="getImportTypeSeverity(slotProps.data.importType)" />
            </template>
          </Column>
          <Column field="status" header="Status">
            <template #body="slotProps">
              <Tag :value="slotProps.data.status" :severity="getStatusSeverity(slotProps.data.status)" />
            </template>
          </Column>
          <Column field="stats" header="Statistici">
            <template #body="slotProps">
              <span>{{ formatStats(slotProps.data.stats) }}</span>
            </template>
          </Column>
          <Column field="createdBy" header="Importat de">
            <template #body="slotProps">
              <span>{{ slotProps.data.createdBy?.lastName || 'N/A' }} {{ slotProps.data.createdBy?.firstName || '' }}</span>
            </template>
          </Column>
          <Column header="Acțiuni">
            <template #body="slotProps">
              <Button 
                icon="pi pi-eye" 
                class="p-button-rounded p-button-text p-button-sm mr-2"
                @click="viewImportDetails(slotProps.data)"
                v-tooltip.top="'Vizualizează detalii'"
              />
              <Button 
                icon="pi pi-download" 
                class="p-button-rounded p-button-text p-button-sm"
                @click="downloadImportFile(slotProps.data)"
                v-tooltip.top="'Descarcă fișier'"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
    
    <!-- Dialog pentru detaliile importului -->
    <Dialog 
      v-model:visible="importDetailsDialog.visible" 
      :style="{ width: '50vw' }" 
      :modal="true"
      :header="importDetailsDialog.import ? `Detalii Import: ${importDetailsDialog.import.fileName}` : 'Detalii Import'"
    >
      <div v-if="importDetailsDialog.import" class="import-details">
        <div class="grid">
          <div class="col-12 md:col-6 mb-3">
            <div class="import-detail-item">
              <span class="font-bold">Data importului:</span>
              <span>{{ formatDate(importDetailsDialog.import.createdAt) }}</span>
            </div>
          </div>
          
          <div class="col-12 md:col-6 mb-3">
            <div class="import-detail-item">
              <span class="font-bold">Status:</span>
              <Tag :value="importDetailsDialog.import.status" :severity="getStatusSeverity(importDetailsDialog.import.status)" />
            </div>
          </div>
          
          <div class="col-12 md:col-6 mb-3">
            <div class="import-detail-item">
              <span class="font-bold">Tip import:</span>
              <span>{{ getImportTypeLabel(importDetailsDialog.import.importType) }}</span>
            </div>
          </div>
          
          <div class="col-12 md:col-6 mb-3">
            <div class="import-detail-item">
              <span class="font-bold">Perioada de examinare:</span>
              <span>{{ getExamPeriodName(importDetailsDialog.import.examPeriodId) }}</span>
            </div>
          </div>
          
          <div class="col-12 md:col-6 mb-3">
            <div class="import-detail-item">
              <span class="font-bold">Importat de:</span>
              <span>{{ importDetailsDialog.import.createdBy?.lastName || 'N/A' }} {{ importDetailsDialog.import.createdBy?.firstName || '' }}</span>
            </div>
          </div>
          
          <div class="col-12 md:col-6 mb-3">
            <div class="import-detail-item">
              <span class="font-bold">Opțiuni:</span>
              <div class="mt-2">
                <Tag v-if="importDetailsDialog.import.options.skipValidation" value="Fără validare" severity="warning" class="mr-1" />
                <Tag v-if="importDetailsDialog.import.options.sendNotifications" value="Cu notificări" severity="info" class="mr-1" />
                <Tag v-if="importDetailsDialog.import.options.ignoreConflicts" value="Ignoră conflicte" severity="danger" class="mr-1" />
                <Tag v-if="importDetailsDialog.import.options.dryRun" value="Simulare" severity="secondary" class="mr-1" />
              </div>
            </div>
          </div>
        </div>
        
        <Divider />
        
        <div class="grid">
          <div class="col-12 md:col-4 mb-3">
            <div class="import-stat p-3 text-center border-round bg-green-50">
              <div class="text-3xl font-bold text-green-500 mb-2">{{ importDetailsDialog.import.stats.added }}</div>
              <div class="text-sm">Planificări adăugate</div>
            </div>
          </div>
          
          <div class="col-12 md:col-4 mb-3">
            <div class="import-stat p-3 text-center border-round bg-blue-50">
              <div class="text-3xl font-bold text-blue-500 mb-2">{{ importDetailsDialog.import.stats.updated }}</div>
              <div class="text-sm">Planificări actualizate</div>
            </div>
          </div>
          
          <div class="col-12 md:col-4 mb-3">
            <div class="import-stat p-3 text-center border-round bg-orange-50">
              <div class="text-3xl font-bold text-orange-500 mb-2">{{ importDetailsDialog.import.stats.skipped }}</div>
              <div class="text-sm">Planificări ignorate</div>
            </div>
          </div>
        </div>
        
        <div v-if="importDetailsDialog.import.warnings && importDetailsDialog.import.warnings.length > 0" class="mt-4">
          <h4 class="text-lg font-bold mb-2">Avertismente</h4>
          <ul class="warning-list">
            <li v-for="(warning, index) in importDetailsDialog.import.warnings" :key="index" class="warning-item p-3 mb-2">
              {{ warning }}
            </li>
          </ul>
        </div>
        
        <div v-if="importDetailsDialog.import.errors && importDetailsDialog.import.errors.length > 0" class="mt-4">
          <h4 class="text-lg font-bold mb-2">Erori</h4>
          <ul class="error-list">
            <li v-for="(error, index) in importDetailsDialog.import.errors" :key="index" class="error-item p-3 mb-2">
              {{ error }}
            </li>
          </ul>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import moment from 'moment'

export default {
  name: 'ImportData',
  setup() {
    const store = useStore()
    
    const loading = ref(false)
    const submitted = ref(false)
    const importFile = ref(null)
    
    // Opțiuni pentru import
    const importOptions = reactive({
      examPeriodId: null,
      importType: 'ADD',
      skipValidation: false,
      sendNotifications: true,
      ignoreConflicts: false,
      dryRun: false
    })
    
    // Rezultatul importului
    const importResult = reactive({
      visible: false,
      success: false,
      stats: {
        added: 0,
        updated: 0,
        skipped: 0
      },
      warnings: [],
      errors: []
    })
    
    // Dialog pentru detaliile importului
    const importDetailsDialog = reactive({
      visible: false,
      import: null
    })
    
    // Istoric importuri
    const importHistory = ref([])
    
    // Obținem datele din store
    const examPeriods = computed(() => store.state.schedule.examPeriods)
    
    // Funcție pentru formatarea datei
    const formatDate = (dateString) => {
      return moment(dateString).format('DD.MM.YYYY HH:mm')
    }
    
    // Funcție pentru obținerea severității tag-ului pentru tipul de import
    const getImportTypeSeverity = (importType) => {
      switch (importType) {
        case 'ADD': return 'success'
        case 'REPLACE': return 'warning'
        default: return 'info'
      }
    }
    
    // Funcție pentru obținerea etichetei tipului de import
    const getImportTypeLabel = (importType) => {
      switch (importType) {
        case 'ADD': return 'Adăugare'
        case 'REPLACE': return 'Înlocuire'
        default: return importType
      }
    }
    
    // Funcție pentru obținerea severității tag-ului pentru status
    const getStatusSeverity = (status) => {
      switch (status) {
        case 'SUCCESS': return 'success'
        case 'PARTIAL': return 'warning'
        case 'FAILED': return 'danger'
        default: return 'info'
      }
    }
    
    // Funcție pentru formatarea statisticilor
    const formatStats = (stats) => {
      if (!stats) return 'N/A'
      return `+${stats.added} / ~${stats.updated} / -${stats.skipped}`
    }
    
    // Funcție pentru obținerea numelui perioadei de examinare
    const getExamPeriodName = (examPeriodId) => {
      const period = examPeriods.value.find(p => p.id === examPeriodId)
      return period ? period.name : 'N/A'
    }
    
    // Funcție pentru gestionarea încărcării fișierului
    const onUpload = (event) => {
      importFile.value = event.files[0]
    }
    
    // Funcție pentru descărcarea template-ului
    const downloadTemplate = () => {
      window.location.href = '/api/import/template'
    }
    
    // Funcție pentru importul datelor
    const importData = async () => {
      submitted.value = true
      
      // Verificăm dacă toate câmpurile obligatorii sunt completate
      if (!importOptions.examPeriodId || !importFile.value) {
        return
      }
      
      try {
        loading.value = true
        
        // Creăm un obiect FormData pentru a trimite fișierul
        const formData = new FormData()
        formData.append('file', importFile.value)
        formData.append('examPeriodId', importOptions.examPeriodId)
        formData.append('importType', importOptions.importType)
        formData.append('skipValidation', importOptions.skipValidation)
        formData.append('sendNotifications', importOptions.sendNotifications)
        formData.append('ignoreConflicts', importOptions.ignoreConflicts)
        formData.append('dryRun', importOptions.dryRun)
        
        // Trimitem cererea de import
        const response = await fetch('/api/import', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${store.state.auth.token}`
          },
          body: formData
        })
        
        const result = await response.json()
        
        if (response.ok) {
          // Importul a fost realizat cu succes
          importResult.success = true
          importResult.stats = result.stats
          importResult.warnings = result.warnings || []
          importResult.errors = []
        } else {
          // Importul a eșuat
          importResult.success = false
          importResult.stats = { added: 0, updated: 0, skipped: 0 }
          importResult.warnings = []
          importResult.errors = result.errors || [result.error || 'A apărut o eroare la importul datelor']
        }
        
        // Afișăm rezultatul importului
        importResult.visible = true
        
        // Reîncărcăm istoricul importurilor
        await loadImportHistory()
        
        // Resetăm formularul dacă importul a fost realizat cu succes
        if (importResult.success) {
          resetForm()
        }
      } catch (error) {
        console.error('Eroare la importul datelor:', error)
        
        // Afișăm un mesaj de eroare
        store.dispatch('toast/add', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'A apărut o eroare la importul datelor',
          life: 3000
        })
        
        // Setăm rezultatul importului
        importResult.success = false
        importResult.stats = { added: 0, updated: 0, skipped: 0 }
        importResult.warnings = []
        importResult.errors = [error.message || 'A apărut o eroare la importul datelor']
        importResult.visible = true
      } finally {
        loading.value = false
      }
    }
    
    // Funcție pentru resetarea formularului
    const resetForm = () => {
      importOptions.examPeriodId = null
      importOptions.importType = 'ADD'
      importOptions.skipValidation = false
      importOptions.sendNotifications = true
      importOptions.ignoreConflicts = false
      importOptions.dryRun = false
      importFile.value = null
      submitted.value = false
    }
    
    // Funcție pentru încărcarea istoricului importurilor
    const loadImportHistory = async () => {
      try {
        const response = await fetch('/api/import/history', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${store.state.auth.token}`
          }
        })
        
        if (!response.ok) {
          throw new Error('Eroare la încărcarea istoricului importurilor')
        }
        
        const data = await response.json()
        importHistory.value = data
      } catch (error) {
        console.error('Eroare la încărcarea istoricului importurilor:', error)
      }
    }
    
    // Funcție pentru vizualizarea detaliilor importului
    const viewImportDetails = (importItem) => {
      importDetailsDialog.import = importItem
      importDetailsDialog.visible = true
    }
    
    // Funcție pentru descărcarea fișierului importat
    const downloadImportFile = (importItem) => {
      window.location.href = `/api/import/download/${importItem.id}`
    }
    
    // Încărcăm datele la montarea componentei
    onMounted(async () => {
      try {
        loading.value = true
        
        // Încărcăm perioadele de examinare
        if (examPeriods.value.length === 0) {
          await store.dispatch('schedule/fetchExamPeriods')
        }
        
        // Încărcăm istoricul importurilor
        await loadImportHistory()
      } catch (error) {
        console.error('Eroare la încărcarea datelor:', error)
      } finally {
        loading.value = false
      }
    })
    
    return {
      loading,
      submitted,
      importFile,
      importOptions,
      importResult,
      importDetailsDialog,
      importHistory,
      examPeriods,
      formatDate,
      getImportTypeSeverity,
      getImportTypeLabel,
      getStatusSeverity,
      formatStats,
      getExamPeriodName,
      onUpload,
      downloadTemplate,
      importData,
      viewImportDetails,
      downloadImportFile
    }
  }
}
</script>

<style scoped>
.import-container {
  padding-bottom: 2rem;
}

.import-detail-item {
  display: flex;
  flex-direction: column;
}

.warning-list, .error-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.warning-item {
  background-color: var(--yellow-50);
  border-left: 4px solid var(--yellow-500);
  border-radius: 4px;
}

.error-item {
  background-color: var(--red-50);
  border-left: 4px solid var(--red-500);
  border-radius: 4px;
}
</style>
