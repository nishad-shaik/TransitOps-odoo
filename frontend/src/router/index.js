import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Dashboard from '../views/Dashboard.vue';
import Vehicles from '../views/Vehicles.vue';
import Drivers from '../views/Drivers.vue';
import Trips from '../views/Trips.vue';
import Maintenance from '../views/Maintenance.vue';
import FuelExpenses from '../views/FuelExpenses.vue';
import Analytics from '../views/Analytics.vue';
import Settings from '../views/Settings.vue';
import Forbidden from '../views/Forbidden.vue';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/vehicles',
    name: 'Vehicles',
    component: Vehicles,
    meta: { requiresAuth: true }
  },
  {
    path: '/drivers',
    name: 'Drivers',
    component: Drivers,
    meta: { requiresAuth: true }
  },
  {
    path: '/trips',
    name: 'Trips',
    component: Trips,
    meta: { requiresAuth: true }
  },
  {
    path: '/maintenance',
    name: 'Maintenance',
    component: Maintenance,
    meta: { requiresAuth: true }
  },
  {
    path: '/fuel-expenses',
    name: 'FuelExpenses',
    component: FuelExpenses,
    meta: { requiresAuth: true }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: Analytics,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: Forbidden,
    meta: { requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

import { useToast } from '../composables/useToast';

// Role-based Access Control Permissions Matrix
const rolePermissions = {
  'Fleet Manager': ['/dashboard', '/vehicles', '/drivers', '/maintenance', '/analytics', '/settings', '/403'],
  'Dispatcher': ['/dashboard', '/vehicles', '/trips', '/403'],
  'Safety Officer': ['/dashboard', '/drivers', '/trips', '/403'],
  'Financial Analyst': ['/dashboard', '/vehicles', '/fuel-expenses', '/analytics', '/403'],
  'Driver': ['/dashboard', '/trips', '/403'],
  'Developer': ['/dashboard', '/vehicles', '/drivers', '/trips', '/maintenance', '/fuel-expenses', '/analytics', '/settings', '/403']
};

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('transitops_token');
  const userStr = localStorage.getItem('transitops_user');
  const { showToast } = useToast();
  
  let user = null;
  if (userStr) {
    try {
      user = JSON.parse(userStr);
    } catch (e) {
      user = null;
    }
  }

  const requiresAuth = to.meta.requiresAuth ?? true;

  if (requiresAuth && !token) {
    next('/login');
  } else if (to.path === '/login' && token) {
    next('/dashboard');
  } else if (token && user) {
    const role = user.role || 'Driver';
    const allowedPaths = rolePermissions[role] || ['/dashboard', '/trips'];
    
    if (!allowedPaths.includes(to.path)) {
      showToast(`Access Denied: Your role (${role}) is forbidden from accessing ${to.path}.`, 'error');
      next('/403');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
