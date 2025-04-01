<template>
  <header class="app-header">
    <Menubar :model="items" class="border-noround">
      <template #start>
        <div class="flex align-items-center">
          <img src="@/assets/logo.svg" alt="Logo FIESC" height="40" class="mr-2" />
          <h1 class="text-xl font-bold">Planificare Examene FIESC</h1>
        </div>
      </template>
      <template #end>
        <div class="flex align-items-center">
          <span class="mr-2">{{ userFullName }}</span>
          <Menu ref="menu" :model="profileItems" :popup="true" />
          <Button icon="pi pi-user" @click="toggleMenu" aria-haspopup="true" aria-controls="profile_menu" class="p-button-rounded p-button-text" />
        </div>
      </template>
    </Menubar>
  </header>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'AppHeader',
  setup() {
    const store = useStore()
    const router = useRouter()
    const menu = ref(null)
    
    const user = computed(() => store.state.auth.user)
    const userFullName = computed(() => {
      if (user.value) {
        return `${user.value.firstName} ${user.value.lastName}`
      }
      return ''
    })
    
    const toggleMenu = (event) => {
      menu.value.toggle(event)
    }
    
    const logout = () => {
      store.dispatch('auth/logout')
      router.push('/login')
    }
    
    const items = [
      {
        label: 'Acasă',
        icon: 'pi pi-home',
        to: '/'
      },
      {
        label: 'Planificare',
        icon: 'pi pi-calendar',
        to: '/schedule'
      },
      {
        label: 'Notificări',
        icon: 'pi pi-bell',
        to: '/notifications'
      }
    ]
    
    const profileItems = [
      {
        label: 'Profil',
        icon: 'pi pi-user',
        command: () => router.push('/profile')
      },
      {
        label: 'Setări',
        icon: 'pi pi-cog',
        command: () => router.push('/settings')
      },
      {
        separator: true
      },
      {
        label: 'Deconectare',
        icon: 'pi pi-sign-out',
        command: logout
      }
    ]
    
    return {
      menu,
      items,
      profileItems,
      userFullName,
      toggleMenu
    }
  }
}
</script>

<style scoped>
.app-header {
  background-color: var(--surface-card);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}
</style>
