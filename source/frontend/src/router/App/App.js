import monitoring from "./monitoring/index.js";

export default {
    path: '/',
    component: () => import('../../layout/Main.vue'),
    children: [monitoring]
}