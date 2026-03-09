export default {
    path: 'actuators',
    name: 'actuators',
    components: {
        actuators: () => import('../../../views/monitoring/actuators/Actuators.vue')
    }
}