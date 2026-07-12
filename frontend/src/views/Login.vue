<template>
  <div class="login-container">
    <div class="branding-side">
      <div class="branding-content">
        <h1>TransitOps</h1>
        <p>Smart Transport Operations Platform</p>
      </div>
    </div>
    <div class="form-side">
      <div class="form-content">
        <h2>Sign In</h2>
        <p class="subtitle">Enter your credentials to access your dashboard</p>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input
              type="email"
              id="email"
              v-model="email"
              required
              placeholder="e.g., manager@transitops.dev"
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              type="password"
              id="password"
              v-model="password"
              required
              placeholder="••••••••"
            />
          </div>

          <div class="form-group">
            <label for="role">Role (Demo Quick-Select)</label>
            <select id="role" v-model="selectedRole">
              <option value="Fleet Manager">Fleet Manager</option>
              <option value="Dispatcher">Dispatcher</option>
              <option value="Safety Officer">Safety Officer</option>
              <option value="Financial Analyst">Financial Analyst</option>
            </select>
          </div>

          <div class="form-actions">
            <label class="remember-me">
              <input type="checkbox" v-model="rememberMe" />
              Remember me
            </label>
            <a href="#" class="forgot-password" @click.prevent="handleForgotPassword">
              Forgot password?
            </a>
          </div>

          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <button type="submit" class="btn-login" :disabled="loading">
            {{ loading ? 'Signing in...' : 'Sign In' }}
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
      // In a real app, role is backend-authoritative from token.
      // We will save user session locally.
      localStorage.setItem('transitops_token', 'mock-jwt-token');
      localStorage.setItem('transitops_user', JSON.stringify({
        email: email.value,
        role: selectedRole.value
      }));
      
      router.push('/dashboard');
    } else {
      errorMessage.value = 'Invalid credentials. Account locked after 5 failed attempts.';
    }
  }, 800);
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
  background-color: var(--bg);
}

.branding-side {
  flex: 1.2;
  background: linear-gradient(135deg, #aa3bff 0%, #6b21a8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  padding: 3rem;
}

.branding-content h1 {
  font-size: 3.5rem;
  margin: 0;
  font-weight: 800;
  letter-spacing: -1px;
}

.branding-content p {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-top: 0.5rem;
}

.form-side {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background-color: var(--bg);
}

.form-content {
  width: 100%;
  max-width: 420px;
}

.form-content h2 {
  font-size: 2rem;
  margin: 0 0 0.5rem 0;
  color: var(--text-h);
}

.subtitle {
  color: var(--text);
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-h);
}

.form-group input,
.form-group select {
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  font-size: 1rem;
  background-color: var(--bg);
  color: var(--text-h);
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  border-color: var(--accent);
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

.forgot-password {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
}

.forgot-password:hover {
  text-decoration: underline;
}

.error-message {
  padding: 0.75rem 1rem;
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  border-radius: 0.5rem;
  font-size: 0.85rem;
}

.btn-login {
  padding: 0.85rem;
  background-color: var(--accent);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-login:hover {
  opacity: 0.9;
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  .branding-side {
    flex: 0.4;
    padding: 2rem;
  }
  .form-side {
    flex: 1;
    padding: 2rem;
  }
}
</style>
