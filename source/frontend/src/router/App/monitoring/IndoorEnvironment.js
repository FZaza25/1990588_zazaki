export default {
    path: 'indoor-environment',
    name: 'indoor_environment',
    components: {
        sensors: () => import('../../../views/monitoring/indoor_environment/Sensors.vue'),
    }
}
