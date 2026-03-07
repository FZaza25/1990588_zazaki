export default {
    path: 'indoor-environment',
    name: 'indoor_environment',
    components: {
        sensors: () => import('../../../components/indoor_environment/Sensors.vue'),
    }
}
