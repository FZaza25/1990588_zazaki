import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // importa il router
import './assets/main.scss'
import '@mdi/font/css/materialdesignicons.css'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import i18n from './lang/i18n.js'
import { createPinia } from 'pinia'

const vuetify = createVuetify({
    components,
    directives,
    theme: {
        defaultTheme: 'light',
        icons: {
            defaultSet: 'mdi',
            aliases,
            sets: { mdi },
        },
        themes: {
            light: {
                colors: {
                    background: '#ffffff',
                    border: '#0B304F',
                    primary: '#0B304F'
                },
            },
        },
    },
})

const pinia = createPinia()

createApp(App)
    .use(router)   // registra il router
    .use(vuetify)
    .use(i18n)
    .use(pinia)
    .mount('#app')