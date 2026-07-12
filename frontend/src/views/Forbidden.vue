<template>
  <div class="forbidden-wrapper">
    <div class="forbidden-card">
      <span class="lock-icon">🔒</span>
      <h1>403 - Access Denied</h1>
      <p>Your current security profile claims do not permit viewing this administrative partition.</p>
      <router-link to="/dashboard" class="btn-primary">
        Return to Dashboard
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.forbidden-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  background-color: var(--dark-bg);
  padding: 2rem;
}

.forbidden-card {
  background-color: var(--panel-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: 3rem;
  text-align: center;
  max-width: 480px;
  box-shadow: var(--shadow-lg);
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

.lock-icon {
  font-size: 4rem;
  display: block;
  margin-bottom: 1.5rem;
}

h1 {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: var(--danger);
}

p {
  color: var(--text-secondary);
  margin-bottom: 2rem;
  font-size: 0.95rem;
  line-height: 1.6;
}

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}
</style>
