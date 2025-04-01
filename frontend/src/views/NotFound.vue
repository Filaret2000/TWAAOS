<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1 class="text-4xl font-bold mb-4">404</h1>
      <h2 class="text-2xl mb-4">Pagină negăsită</h2>
      <p class="mb-6">Ne pare rău, pagina pe care o căutați nu există sau a fost mutată.</p>
      <router-link to="/" class="p-button p-component">
        <span class="p-button-label">Înapoi la pagina principală</span>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 64px);
  padding: 2rem;
}

.not-found-content {
  text-align: center;
  max-width: 600px;
  padding: 3rem;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
</style>
