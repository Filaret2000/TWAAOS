<template>
  <div class="rooms-container">
    <div class="card">
      <div class="flex justify-content-between align-items-center mb-4">
        <h1 class="text-3xl font-bold m-0">Săli</h1>
        <Button 
          v-if="hasPermission('admin') || hasPermission('secretary')" 
          label="Adaugă sală" 
          icon="pi pi-plus" 
          @click="openNewRoomDialog"
        />
      </div>
      
      <div v-if="loading" class="text-center p-4">
        <ProgressSpinner />
        <p class="mt-2">Se încarcă sălile...</p>
      </div>
      
      <div v-else>
        <DataTable 
          :value="rooms" 
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Afișare {first} - {last} din {totalRecords} săli"
          responsiveLayout="scroll"
          :filters="filters"
          filterDisplay="menu"
          :globalFilterFields="['name', 'shortName', 'building', 'capacity']"
          v-model:selection="selectedRooms"
          :rowHover="true"
          dataKey="id"
          class="p-datatable-sm"
        >
          <template #header>
            <div class="flex justify-content-end">
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText v-model="filters['global'].value" placeholder="Caută..." />
              </span>
            </div>
          </template>
          
          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
          
          <Column field="name" header="Denumire" :sortable="true">
            <template #body="slotProps">
              <span class="font-bold">{{ slotProps.data.name }}</span>
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <InputText 
                v-model="filterModel.value" 
                @input="filterCallback()" 
                class="p-column-filter" 
                placeholder="Caută după denumire" 
              />
            </template>
          </Column>
          
          <Column field="shortName" header="Cod" :sortable="true">
            <template #filter="{ filterModel, filterCallback }">
              <InputText 
                v-model="filterModel.value" 
                @input="filterCallback()" 
                class="p-column-filter" 
                placeholder="Caută după cod" 
              />
            </template>
          </Column>
          
          <Column field="building" header="Clădire" :sortable="true">
            <template #filter="{ filterModel, filterCallback }">
              <Dropdown 
                v-model="filterModel.value" 
                @change="filterCallback()" 
                :options="buildingOptions" 
                placeholder="Toate clădirile" 
                class="p-column-filter" 
              />
            </template>
          </Column>
          
          <Column field="floor" header="Etaj" :sortable="true">
            <template #filter="{ filterModel, filterCallback }">
              <InputNumber 
                v-model="filterModel.value" 
                @input="filterCallback()" 
                class="p-column-filter" 
                placeholder="Etaj" 
              />
            </template>
          </Column>
          
          <Column field="capacity" header="Capacitate" :sortable="true">
            <template #filter="{ filterModel, filterCallback }">
              <InputNumber 
                v-model="filterModel.value" 
                @input="filterCallback()" 
                class="p-column-filter" 
                placeholder="Capacitate minimă" 
              />
            </template>
          </Column>
          
          <Column headerStyle="width: 8rem">
            <template #body="slotProps">
              <Button 
                icon="pi pi-pencil" 
                class="p-button-rounded p-button-text mr-2" 
                @click="editRoom(slotProps.data)"
                v-tooltip.top="'Editează'"
                :disabled="!hasPermission('admin') && !hasPermission('secretary')"
              />
              <Button 
                icon="pi pi-trash" 
                class="p-button-rounded p-button-text p-button-danger" 
                @click="confirmDeleteRoom(slotProps.data)"
                v-tooltip.top="'Șterge'"
                :disabled="!hasPermission('admin')"
              />
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
    
    <!-- Dialog pentru adăugare/editare sală -->
    <Dialog 
      v-model:visible="roomDialog" 
      :style="{width: '450px'}" 
      :header="editingRoom.id ? 'Editare sală' : 'Adăugare sală'" 
      :modal="true" 
      class="p-fluid"
    >
      <div class="field">
        <label for="name">Denumire</label>
        <InputText id="name" v-model.trim="editingRoom.name" required autofocus :class="{'p-invalid': submitted && !editingRoom.name}" />
        <small class="p-error" v-if="submitted && !editingRoom.name">Denumirea este obligatorie.</small>
      </div>
      
      <div class="field">
        <label for="shortName">Cod</label>
        <InputText id="shortName" v-model.trim="editingRoom.shortName" required :class="{'p-invalid': submitted && !editingRoom.shortName}" />
        <small class="p-error" v-if="submitted && !editingRoom.shortName">Codul este obligatoriu.</small>
      </div>
      
      <div class="field">
        <label for="building">Clădire</label>
        <Dropdown id="building" v-model="editingRoom.building" :options="buildingOptions" placeholder="Selectează clădirea" />
      </div>
      
      <div class="field">
        <label for="floor">Etaj</label>
        <InputNumber id="floor" v-model="editingRoom.floor" />
      </div>
      
      <div class="field">
        <label for="capacity">Capacitate</label>
        <InputNumber id="capacity" v-model="editingRoom.capacity" required :class="{'p-invalid': submitted && !editingRoom.capacity}" />
        <small class="p-error" v-if="submitted && !editingRoom.capacity">Capacitatea este obligatorie.</small>
      </div>
      
      <template #footer>
        <Button label="Anulează" icon="pi pi-times" class="p-button-text" @click="hideDialog" />
        <Button label="Salvează" icon="pi pi-check" class="p-button-text" @click="saveRoom" :loading="saving" />
      </template>
    </Dialog>
    
    <!-- Dialog pentru confirmare ștergere -->
    <Dialog v-model:visible="deleteRoomDialog" :style="{width: '450px'}" header="Confirmare" :modal="true">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="editingRoom">Sigur doriți să ștergeți sala <b>{{ editingRoom.name }}</b>?</span>
      </div>
      <template #footer>
        <Button label="Nu" icon="pi pi-times" class="p-button-text" @click="deleteRoomDialog = false" />
        <Button label="Da" icon="pi pi-check" class="p-button-text" @click="deleteRoom" :loading="deleting" />
      </template>
    </Dialog>
    
    <!-- Dialog pentru confirmare ștergere multiplă -->
    <Dialog v-model:visible="deleteRoomsDialog" :style="{width: '450px'}" header="Confirmare" :modal="true">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span>Sigur doriți să ștergeți sălile selectate?</span>
      </div>
      <template #footer>
        <Button label="Nu" icon="pi pi-times" class="p-button-text" @click="deleteRoomsDialog = false" />
        <Button label="Da" icon="pi pi-check" class="p-button-text" @click="deleteSelectedRooms" :loading="deleting" />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useToast } from 'primevue/usetoast'
import { FilterMatchMode } from 'primevue/api'

export default {
  name: 'Rooms',
  setup() {
    const store = useStore()
    const toast = useToast()
    
    const rooms = ref([])
    const selectedRooms = ref([])
    const loading = ref(true)
    const saving = ref(false)
    const deleting = ref(false)
    const submitted = ref(false)
    
    const roomDialog = ref(false)
    const deleteRoomDialog = ref(false)
    const deleteRoomsDialog = ref(false)
    
    const editingRoom = reactive({
      id: null,
      name: '',
      shortName: '',
      building: null,
      floor: null,
      capacity: null
    })
    
    const buildingOptions = [
      'A', 'B', 'C', 'D', 'E', 'FIM', 'Corp R'
    ]
    
    const filters = ref({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS },
      name: { value: null, matchMode: FilterMatchMode.CONTAINS },
      shortName: { value: null, matchMode: FilterMatchMode.CONTAINS },
      building: { value: null, matchMode: FilterMatchMode.EQUALS },
      floor: { value: null, matchMode: FilterMatchMode.EQUALS },
      capacity: { value: null, matchMode: FilterMatchMode.GREATER_THAN_OR_EQUAL_TO }
    })
    
    onMounted(async () => {
      await loadRooms()
    })
    
    const loadRooms = async () => {
      loading.value = true
      
      try {
        // În mod normal, aici ar trebui să facem un apel API pentru a obține sălile
        // Simulăm un răspuns de la server
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Date de exemplu
        rooms.value = [
          { id: 1, name: 'Sala C201', shortName: 'C201', building: 'C', floor: 2, capacity: 30 },
          { id: 2, name: 'Sala C202', shortName: 'C202', building: 'C', floor: 2, capacity: 30 },
          { id: 3, name: 'Sala C203', shortName: 'C203', building: 'C', floor: 2, capacity: 24 },
          { id: 4, name: 'Sala C204', shortName: 'C204', building: 'C', floor: 2, capacity: 24 },
          { id: 5, name: 'Sala C205', shortName: 'C205', building: 'C', floor: 2, capacity: 40 },
          { id: 6, name: 'Sala C301', shortName: 'C301', building: 'C', floor: 3, capacity: 30 },
          { id: 7, name: 'Sala C302', shortName: 'C302', building: 'C', floor: 3, capacity: 30 },
          { id: 8, name: 'Sala C303', shortName: 'C303', building: 'C', floor: 3, capacity: 24 },
          { id: 9, name: 'Sala C304', shortName: 'C304', building: 'C', floor: 3, capacity: 24 },
          { id: 10, name: 'Sala C305', shortName: 'C305', building: 'C', floor: 3, capacity: 40 },
          { id: 11, name: 'Amfiteatrul A1', shortName: 'A1', building: 'A', floor: 1, capacity: 120 },
          { id: 12, name: 'Amfiteatrul A2', shortName: 'A2', building: 'A', floor: 1, capacity: 120 },
          { id: 13, name: 'Amfiteatrul A3', shortName: 'A3', building: 'A', floor: 2, capacity: 80 },
          { id: 14, name: 'Amfiteatrul A4', shortName: 'A4', building: 'A', floor: 2, capacity: 80 },
          { id: 15, name: 'Laborator D101', shortName: 'D101', building: 'D', floor: 1, capacity: 16 }
        ]
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca sălile',
          life: 3000
        })
      } finally {
        loading.value = false
      }
    }
    
    const openNewRoomDialog = () => {
      editingRoom.id = null
      editingRoom.name = ''
      editingRoom.shortName = ''
      editingRoom.building = null
      editingRoom.floor = null
      editingRoom.capacity = null
      submitted.value = false
      roomDialog.value = true
    }
    
    const editRoom = (room) => {
      editingRoom.id = room.id
      editingRoom.name = room.name
      editingRoom.shortName = room.shortName
      editingRoom.building = room.building
      editingRoom.floor = room.floor
      editingRoom.capacity = room.capacity
      roomDialog.value = true
    }
    
    const hideDialog = () => {
      roomDialog.value = false
      submitted.value = false
    }
    
    const saveRoom = async () => {
      submitted.value = true
      
      if (!editingRoom.name || !editingRoom.shortName || !editingRoom.capacity) {
        return
      }
      
      saving.value = true
      
      try {
        // Simulăm un apel API pentru salvarea sălii
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        if (editingRoom.id) {
          // Actualizare sală existentă
          const index = rooms.value.findIndex(r => r.id === editingRoom.id)
          if (index !== -1) {
            rooms.value[index] = { ...editingRoom }
          }
          
          toast.add({
            severity: 'success',
            summary: 'Succes',
            detail: 'Sala a fost actualizată',
            life: 3000
          })
        } else {
          // Adăugare sală nouă
          const newRoom = { 
            ...editingRoom,
            id: rooms.value.length ? Math.max(...rooms.value.map(r => r.id)) + 1 : 1
          }
          rooms.value.push(newRoom)
          
          toast.add({
            severity: 'success',
            summary: 'Succes',
            detail: 'Sala a fost adăugată',
            life: 3000
          })
        }
        
        roomDialog.value = false
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-a putut salva sala',
          life: 3000
        })
      } finally {
        saving.value = false
      }
    }
    
    const confirmDeleteRoom = (room) => {
      editingRoom.id = room.id
      editingRoom.name = room.name
      deleteRoomDialog.value = true
    }
    
    const deleteRoom = async () => {
      deleting.value = true
      
      try {
        // Simulăm un apel API pentru ștergerea sălii
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        rooms.value = rooms.value.filter(r => r.id !== editingRoom.id)
        deleteRoomDialog.value = false
        
        toast.add({
          severity: 'success',
          summary: 'Succes',
          detail: 'Sala a fost ștearsă',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-a putut șterge sala',
          life: 3000
        })
      } finally {
        deleting.value = false
      }
    }
    
    const confirmDeleteSelectedRooms = () => {
      deleteRoomsDialog.value = true
    }
    
    const deleteSelectedRooms = async () => {
      deleting.value = true
      
      try {
        // Simulăm un apel API pentru ștergerea sălilor selectate
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        rooms.value = rooms.value.filter(r => !selectedRooms.value.includes(r))
        deleteRoomsDialog.value = false
        selectedRooms.value = []
        
        toast.add({
          severity: 'success',
          summary: 'Succes',
          detail: 'Sălile au fost șterse',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut șterge sălile',
          life: 3000
        })
      } finally {
        deleting.value = false
      }
    }
    
    const hasPermission = (role) => {
      const user = store.state.auth.user
      if (!user) return false
      
      if (role === 'admin') return user.role === 'ADMIN'
      if (role === 'secretary') return user.role === 'SEC'
      
      return false
    }
    
    return {
      rooms,
      selectedRooms,
      loading,
      saving,
      deleting,
      submitted,
      roomDialog,
      deleteRoomDialog,
      deleteRoomsDialog,
      editingRoom,
      buildingOptions,
      filters,
      loadRooms,
      openNewRoomDialog,
      editRoom,
      hideDialog,
      saveRoom,
      confirmDeleteRoom,
      deleteRoom,
      confirmDeleteSelectedRooms,
      deleteSelectedRooms,
      hasPermission
    }
  }
}
</script>

<style scoped>
.rooms-container {
  padding: 2rem;
}

.confirmation-content {
  display: flex;
  align-items: center;
}
</style>
