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


createApp(App)
    .use(router)   // registra il router
    .use(vuetify)
    .mount('#app')