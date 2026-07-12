<template>
  <div class="login-container">
    <!-- Branding Side (Left) -->
    <div class="branding-side">
      <div class="glow-sphere"></div>
      <div class="branding-content">
        <div class="logo-wrapper">
          <span class="logo-icon">🔮</span>
          <h1>TransitOps</h1>
        </div>
        <p class="branding-desc">The next-generation logistics and transport management platform.</p>
        
        <div class="features-list">
          <div class="feature-item">
            <span class="check-icon">✓</span>
            <span>Real-time dispatch automation</span>
          </div>
          <div class="feature-item">
            <span class="check-icon">✓</span>
            <span>AI-driven route & load compliance</span>
          </div>
          <div class="feature-item">
            <span class="check-icon">✓</span>
            <span>Automatic fuel & maintenance rollups</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Form Side (Right) -->
    <div class="form-side">
      <div class="form-content">
        <div class="header-block">
          <h2>Welcome back</h2>
          <p class="subtitle">Please enter your credentials to sign in</p>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="email">Email Address</label>
            <div class="input-wrapper">
              <span class="input-icon">✉</span>
              <input
                type="email"
                id="email"
                v-model="email"
                required
                placeholder="manager@transitops.dev"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <div class="input-wrapper">
              <span class="input-icon">🔑</span>
              <input
                type="password"
                id="password"
                v-model="password"
                required
                placeholder="••••••••"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="role">Role Permission Level</label>
            <div class="input-wrapper">
              <span class="input-icon">🛡️</span>
              <select id="role" v-model="selectedRole">
                <option value="Fleet Manager">Fleet Manager</option>
                <option value="Dispatcher">Dispatcher</option>
                <option value="Safety Officer">Safety Officer</option>
                <option value="Financial Analyst">Financial Analyst</option>
              </select>
            </div>
          </div>

          <div class="form-actions">
            <label class="remember-me">
              <input type="checkbox" v-model="rememberMe" />
              <span class="check-box-label">Remember me</span>
            </label>
            <a href="#" class="forgot-password" @click.prevent="handleForgotPassword">
              Forgot password?
            </a>
          </div>

          <div v-if="errorMessage" class="error-message">
            <span class="err-icon">⚠️</span>
            <span>{{ errorMessage }}</span>
          </div>

          <button type="submit" class="btn-primary btn-login" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span>{{ loading ? 'Signing in...' : 'Sign In' }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const email = ref('');
const password = ref('');
const selectedRole = ref('Fleet Manager');
const rememberMe = ref(false);
const loading = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';
  
  // Simulate network request
  setTimeout(() => {
    loading.value = false;
    
    // Check credentials (mock check for scaffold)
    if (email.value && password.value) {
      localStorage.setItem('transitops_token', 'mock-jwt-token');
      localStorage.setItem('transitops_user', JSON.stringify({
        email: email.value,
        role: selectedRole.value
      }));
      
      router.push('/dashboard');
    } else {
      errorMessage.value = 'Invalid credentials. Account locked after 5 failed attempts.';
    }
  }, 1000);
};

const handleForgotPassword = () => {
  alert('Password reset link has been simulated to your email.');
};
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #090a0f;
}

/* Left Branding Side */
.branding-side {
  flex: 1.2;
  background: linear-gradient(145deg, #12131a 0%, #090a0f 100%);
  border-right: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 3.5rem;
}

.glow-sphere {
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(170, 59, 255, 0.08) 0%, rgba(0, 0, 0, 0) 70%);
  top: -10%;
  left: -10%;
  pointer-events: none;
}

.branding-content {
  max-width: 520px;
  position: relative;
  z-index: 2;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.logo-icon {
  font-size: 2.25rem;
}

.branding-content h1 {
  font-size: 2.75rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, #fff 0%, #aa3bff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.branding-desc {
  font-size: 1.15rem;
  color: var(--text-secondary);
  margin-bottom: 3rem;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.check-icon {
  color: var(--primary);
  font-weight: bold;
  font-size: 1.1rem;
}

.feature-item span {
  font-size: 0.95rem;
  color: var(--text-primary);
}

/* Right Form Side */
.form-side {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background-color: #090a0f;
}

.form-content {
  width: 100%;
  max-width: 400px;
}

.header-block {
  margin-bottom: 2.5rem;
}

.header-block h2 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
  color: #fff;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  color: var(--text-muted);
  font-size: 1rem;
  pointer-events: none;
}

.input-wrapper input,
.input-wrapper select {
  padding-left: 2.75rem;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.remember-me input {
  width: auto;
  cursor: pointer;
}

.check-box-label {
  color: var(--text-secondary);
}

.forgot-password {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.forgot-password:hover {
  color: var(--primary-hover);
}

.error-message {
  padding: 0.75rem 1rem;
  background-color: var(--danger-glow);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: var(--danger);
  border-radius: var(--border-radius-sm);
  font-size: 0.85rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-login {
  width: 100%;
  padding: 0.85rem;
  margin-top: 0.75rem;
  border-radius: var(--border-radius-sm);
}

.spinner {
  display: inline-block;
  width: 1.1rem;
  height: 1.1rem;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 900px) {
  .login-container {
    flex-direction: column;
  }
  .branding-side {
    flex: 0.5;
    padding: 2.5rem;
  }
  .form-side {
    flex: 1.5;
    padding: 2.5rem;
  }
  .branding-desc {
    margin-bottom: 1.5rem;
  }
}
</style>
