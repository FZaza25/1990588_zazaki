import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import App from "./App/App.js";

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home
    },
    App
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router