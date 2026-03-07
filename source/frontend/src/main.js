import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // importa il router
import './assets/main.scss'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
    components,
    directives,
    theme: {
        defaultTheme: 'light',
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