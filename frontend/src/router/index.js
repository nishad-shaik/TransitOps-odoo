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
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('transitops_token');
  const requiresAuth = to.meta.requiresAuth ?? true;

  if (requiresAuth && !token) {
    next('/login');
  } else if (to.path === '/login' && token) {
    next('/dashboard');
  } else {
    next();
  }
});

export default router;
