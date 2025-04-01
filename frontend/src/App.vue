<template>
  <div class="app-container">
    <Toast />
    <ConfirmDialog />
    
    <template v-if="isAuthenticated">
      <AppHeader />
      <div class="content-container">
        <AppSidebar />
        <main class="main-content p-4">
          <router-view />
        </main>
      </div>
      <AppFooter />
    </template>
    
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

export default {
  name: 'App',
  components: {
    AppHeader,
    AppSidebar,
    AppFooter
  },
  setup() {
    const store = useStore()
    
    const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])
    
    onMounted(() => {
      // Verificăm token-ul la încărcarea aplicației
      store.dispatch('auth/checkAuth')
    })
    
    return {
      isAuthenticated
    }
  }
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: var(--font-family);
  background-color: var(--surface-ground);
  color: var(--text-color);
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content-container {
  display: flex;
  flex: 1;
}

.main-content {
  flex: 1;
  overflow-y: auto;
}

/* Stiluri pentru scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--surface-ground);
}

::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary-color-darker);
}
</style>
