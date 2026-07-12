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
        <!-- Login/Register Selection Tabs -->
        <div class="tabs-header">
          <button 
            @click="activeTab = 'signin'" 
            class="tab-btn" 
            :class="{ active: activeTab === 'signin' }"
          >
            Sign In
          </button>
          <button 
            @click="activeTab = 'register'" 
            class="tab-btn" 
            :class="{ active: activeTab === 'register' }"
          >
            Register
          </button>
        </div>

        <div class="header-block">
          <h2>{{ activeTab === 'signin' ? 'Welcome back' : 'Create Account' }}</h2>
          <p class="subtitle">
            {{ activeTab === 'signin' ? 'Please enter your credentials to sign in' : 'Set up a new organizational profile' }}
          </p>
        </div>

        <!-- SIGN IN FORM -->
        <form v-if="activeTab === 'signin'" @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="email">Email Address</label>
            <div class="input-wrapper">
              <Mail class="input-icon-svg" />
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
              <Key class="input-icon-svg" />
              <input
                type="password"
                id="password"
                v-model="password"
                required
                placeholder="••••••••"
              />
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
            <AlertTriangle class="err-icon-svg text-danger" />
            <span class="err-text">{{ errorMessage }}</span>
          </div>

          <button type="submit" class="btn-primary btn-login" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span>{{ loading ? 'Signing in...' : 'Sign In' }}</span>
          </button>
        </form>

        <!-- REGISTER FORM -->
        <form v-else @submit.prevent="handleRegister" class="login-form">
          <div class="form-group">
            <label for="reg-email">Email Address</label>
            <div class="input-wrapper">
              <Mail class="input-icon-svg" />
              <input
                type="email"
                id="reg-email"
                v-model="regEmail"
                required
                placeholder="user@transitops.dev"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="reg-password">Password</label>
            <div class="input-wrapper">
              <Key class="input-icon-svg" />
              <input
                type="password"
                id="reg-password"
                v-model="regPassword"
                required
                placeholder="••••••••"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="reg-confirm">Confirm Password</label>
            <div class="input-wrapper">
              <Lock class="input-icon-svg" />
              <input
                type="password"
                id="reg-confirm"
                v-model="regConfirmPassword"
                required
                placeholder="••••••••"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="reg-role">Role Permission Level</label>
            <div class="input-wrapper">
              <Shield class="input-icon-svg" />
              <select id="reg-role" v-model="regRole">
                <option value="Fleet Manager">Fleet Manager</option>
                <option value="Dispatcher">Dispatcher</option>
                <option value="Safety Officer">Safety Officer</option>
                <option value="Financial Analyst">Financial Analyst</option>
                <option value="Driver">Driver (Trips &amp; Dashboard only)</option>
              </select>
            </div>
          </div>

          <div v-if="regErrorMessage" class="error-message">
            <AlertTriangle class="err-icon-svg text-danger" />
            <span class="err-text">{{ regErrorMessage }}</span>
          </div>

          <button type="submit" class="btn-primary btn-login" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span>{{ loading ? 'Creating account...' : 'Register User' }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Mail, Key, Lock, Shield, AlertTriangle } from '@lucide/vue';
import { client } from '../api/client';
import { useToast } from '../composables/useToast';



const router = useRouter();
const { showToast } = useToast();

const activeTab = ref('signin');

// Sign In Fields
const email = ref('');
const password = ref('');
const rememberMe = ref(false);
const loading = ref(false);
const errorMessage = ref('');

// Registration Fields
const regEmail = ref('');
const regPassword = ref('');
const regConfirmPassword = ref('');
const regRole = ref('Fleet Manager');
const regErrorMessage = ref('');

// Load remembered email
onMounted(() => {
  const savedEmail = localStorage.getItem('transitops_remembered_email');
  if (savedEmail) {
    email.value = savedEmail;
    rememberMe.value = true;
  }
});

// Input Sanitization helper (OWASP XSS / Injection Mitigation)
const sanitizeInput = (val) => {
  if (!val) return '';
  // Basic scrubbing of potential HTML tags and script injections
  return val.trim().replace(/[<>'"&]/g, (match) => {
    const map = {
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;',
      '&': '&amp;'
    };
    return map[match];
  });
};

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';

  const cleanEmail = sanitizeInput(email.value);
  const cleanPassword = password.value; // OWASP: Don't sanitize passwords; transmit as typed to prevent hash mismatches

  if (!cleanEmail || !cleanPassword) {
    errorMessage.value = 'Email and password are required.';
    loading.value = false;
    return;
  }

  // OWASP: Client-Side Lockout Security check
  const lockoutKey = `lockout_until_${cleanEmail}`;
  const attemptsKey = `login_attempts_${cleanEmail}`;
  const lockoutTime = localStorage.getItem(lockoutKey);

  if (lockoutTime && parseInt(lockoutTime) > Date.now()) {
    const remaining = Math.round((parseInt(lockoutTime) - Date.now()) / 1000);
    errorMessage.value = `Invalid credentials. Account locked after 5 failed attempts. Please retry in ${remaining}s.`;
    loading.value = false;
    return;
  }

  try {
    const data = await client.post('/auth/login', { email: cleanEmail, password: cleanPassword });
    
    // Clear failed login attempts counter
    localStorage.removeItem(attemptsKey);
    localStorage.removeItem(lockoutKey);

    // Remember me logic
    if (rememberMe.value) {
      localStorage.setItem('transitops_remembered_email', cleanEmail);
    } else {
      localStorage.removeItem('transitops_remembered_email');
    }

    // Save session
    localStorage.setItem('transitops_token', data.token);
    localStorage.setItem('transitops_user', JSON.stringify({
      email: data.user.email,
      role: data.user.role
    }));

    showToast('Logged in successfully!', 'success');
    router.push('/dashboard');
  } catch (err) {
    // Increment failed login count
    const attempts = (parseInt(localStorage.getItem(attemptsKey)) || 0) + 1;
    localStorage.setItem(attemptsKey, attempts.toString());

    if (attempts >= 5) {
      const lockoutExpiration = Date.now() + 30000; // 30 seconds block
      localStorage.setItem(lockoutKey, lockoutExpiration.toString());
      errorMessage.value = 'Invalid credentials. Account locked after 5 failed attempts.';
      showToast('Login blocked: account locked for 30 seconds.', 'error');
    } else {
      const remainingAttempts = 5 - attempts;
      errorMessage.value = `${err.message || 'Invalid credentials'}. ${remainingAttempts} attempts remaining.`;
    }
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  regErrorMessage.value = '';
  loading.value = true;

  const cleanEmail = sanitizeInput(regEmail.value);
  const cleanPassword = regPassword.value; // OWASP: Transmit passwords raw to prevent hash mismatches
  const cleanConfirm = regConfirmPassword.value;

  // Validate passwords match
  if (cleanPassword !== cleanConfirm) {
    regErrorMessage.value = 'Passwords do not match.';
    loading.value = false;
    return;
  }

  // Password length constraint check (minimum 6 chars)
  if (cleanPassword.length < 6) {
    regErrorMessage.value = 'Password must be at least 6 characters.';
    loading.value = false;
    return;
  }

  try {
    await client.post('/auth/register', { email: cleanEmail, password: cleanPassword, role: regRole.value });
    showToast('Registration successful! Please log in.', 'success');

    // Switch tab to signin
    activeTab.value = 'signin';
    email.value = cleanEmail;
    password.value = '';
    
    // Clear registration fields
    regEmail.value = '';
    regPassword.value = '';
    regConfirmPassword.value = '';
  } catch (err) {
    regErrorMessage.value = err.message || 'Registration failed.';
  } finally {
    loading.value = false;
  }
};

const handleForgotPassword = () => {
  showToast('Simulated: A password reset link has been dispatched to your address.', 'info');
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

.tabs-header {
  display: flex;
  background-color: var(--panel-bg);
  border: 1px solid var(--border-color);
  padding: 0.25rem;
  border-radius: var(--border-radius-sm);
  margin-bottom: 2rem;
}

.tab-btn {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-secondary);
  padding: 0.5rem 0;
  font-weight: 700;
  cursor: pointer;
  border-radius: var(--border-radius-sm);
  transition: all 0.2s ease;
}

.tab-btn.active {
  background-color: var(--card-bg);
  color: #fff;
  box-shadow: var(--shadow-sm);
}

.header-block {
  margin-bottom: 2rem;
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
