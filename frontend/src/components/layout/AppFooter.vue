<template>
  <footer class="app-footer p-3">
    <div class="flex justify-content-between align-items-center">
      <div>
        <span>&copy; {{ currentYear }} Facultatea de Inginerie Electrică și Știința Calculatoarelor</span>
      </div>
      <div>
        <span>Versiune: 1.0.0</span>
      </div>
    </div>
  </footer>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'AppFooter',
  setup() {
    const currentYear = computed(() => new Date().getFullYear())
    
    return {
      currentYear
    }
  }
}
</script>

<style scoped>
.app-footer {
  background-color: var(--surface-card);
  border-top: 1px solid var(--surface-border);
  font-size: 0.9rem;
  color: var(--text-color-secondary);
}
</style>
