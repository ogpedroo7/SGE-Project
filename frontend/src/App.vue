<script setup>
</script>


<template>
  <RouterView />
</template>


<style scoped>

main {
  font-family: Arial, sans-serif;
  max-width: 800px;
  margin: 80px auto;
  padding: 30px;
  text-align: center;
  background-color: #1e293b;
  border-radius: 16px;
}

h1 {
  color: #60a5fa;
  font-size: 36px;
}

p {
  color: #cbd5e1;
  font-size: 18px;
}

:global(body) {
  margin: 0;
  background-color: #0f172a;
}

.acoes {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 30px;
}

button {
  padding: 12px 28px;
  border: none;
  border-radius: 8px;
  background-color: #3b82f6;
  color: white;
  font-size: 16px;
  cursor: pointer;
}

button:hover {
  background-color: #2563eb;
}

</style>