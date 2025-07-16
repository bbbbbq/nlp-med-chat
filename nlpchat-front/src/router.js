import { createRouter, createWebHistory } from 'vue-router';
import Login from './components/login.vue';

import Register from './components/Register.vue';
import AdminDashboard from './components/AdminDashboard.vue';


const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },

  { path: '/register', component: Register },
  { path: '/admin/dashboard', component: AdminDashboard }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
