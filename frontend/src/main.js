import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Global styling reset (Vite defaults removed)
import './style.css';

const app = createApp(App);
app.use(router);
app.mount('#app');
