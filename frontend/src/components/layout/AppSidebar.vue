<template>
  <aside class="app-sidebar">
    <div class="sidebar-content">
      <div class="user-role p-3 text-center">
        <span class="role-badge" :class="roleBadgeClass">{{ roleLabel }}</span>
      </div>
      
      <div class="menu p-3">
        <ul class="menu-list">
          <li v-for="(item, index) in filteredMenuItems" :key="index" class="menu-item">
            <router-link :to="item.to" class="menu-link p-3" :class="{ active: isActive(item.to) }">
              <i :class="item.icon" class="menu-icon mr-2"></i>
              <span class="menu-text">{{ item.label }}</span>
            </router-link>
          </li>
        </ul>
      </div>
    </div>
  </aside>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'

export default {
  name: 'AppSidebar',
  setup() {
    const store = useStore()
    const route = useRoute()
    
    const user = computed(() => store.state.auth.user)
    const userRole = computed(() => user.value ? user.value.role : '')
    
    const roleLabel = computed(() => {
      switch (userRole.value) {
        case 'ADM': return 'Administrator'
        case 'SEC': return 'Secretariat'
        case 'CD': return 'Cadru Didactic'
        case 'STD': return 'Student'
        default: return 'Utilizator'
      }
    })
    
    const roleBadgeClass = computed(() => {
      switch (userRole.value) {
        case 'ADM': return 'role-admin'
        case 'SEC': return 'role-secretary'
        case 'CD': return 'role-teacher'
        case 'STD': return 'role-student'
        default: return 'role-default'
      }
    })
    
    const menuItems = [
      {
        label: 'Dashboard',
        icon: 'pi pi-home',
        to: '/',
        roles: ['ADM', 'SEC', 'CD', 'STD']
      },
      {
        label: 'Planificare Examene',
        icon: 'pi pi-calendar',
        to: '/schedule',
        roles: ['ADM', 'SEC', 'CD', 'STD']
      },
      {
        label: 'Notificări',
        icon: 'pi pi-bell',
        to: '/notifications',
        roles: ['ADM', 'SEC', 'CD', 'STD']
      },
      {
        label: 'Gestionare Utilizatori',
        icon: 'pi pi-users',
        to: '/users',
        roles: ['ADM']
      },
      {
        label: 'Săli Disponibile',
        icon: 'pi pi-building',
        to: '/rooms',
        roles: ['ADM', 'SEC', 'CD']
      },
      {
        label: 'Export Date',
        icon: 'pi pi-file-export',
        to: '/export',
        roles: ['ADM', 'SEC']
      },
      {
        label: 'Import Date',
        icon: 'pi pi-file-import',
        to: '/import',
        roles: ['ADM', 'SEC']
      },
      {
        label: 'Setări',
        icon: 'pi pi-cog',
        to: '/settings',
        roles: ['ADM', 'SEC', 'CD', 'STD']
      }
    ]
    
    const filteredMenuItems = computed(() => {
      return menuItems.filter(item => {
        return item.roles.includes(userRole.value)
      })
    })
    
    const isActive = (path) => {
      return route.path === path
    }
    
    return {
      roleLabel,
      roleBadgeClass,
      filteredMenuItems,
      isActive
    }
  }
}
</script>

<style scoped>
.app-sidebar {
  width: 250px;
  background-color: var(--surface-card);
  border-right: 1px solid var(--surface-border);
  height: 100%;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.user-role {
  border-bottom: 1px solid var(--surface-border);
}

.role-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: bold;
}

.role-admin {
  background-color: var(--blue-500);
  color: white;
}

.role-secretary {
  background-color: var(--green-500);
  color: white;
}

.role-teacher {
  background-color: var(--orange-500);
  color: white;
}

.role-student {
  background-color: var(--cyan-500);
  color: white;
}

.role-default {
  background-color: var(--gray-500);
  color: white;
}

.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-item {
  margin-bottom: 0.5rem;
}

.menu-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--text-color);
  border-radius: 4px;
  transition: background-color 0.2s;
}

.menu-link:hover {
  background-color: var(--surface-hover);
}

.menu-link.active {
  background-color: var(--primary-color);
  color: var(--primary-color-text);
}

.menu-icon {
  font-size: 1.2rem;
}
</style>
