<script>
import { defineComponent } from 'vue';
export default defineComponent({
    name: 'MangeHome',
    created() {
        console.log('Manage Home Component Created');
    },
});

</script>

<template>
    <div class="card  manage-container">

        <div class="welcome-message">
            <h2 class="text-center">{{ $t('WELCOME.TITLE') }}</h2>
            <p>{{ $t('WELCOME.DESCRIPTION1') }}</p>
            <p>{{ $t('WELCOME.DESCRIPTION2') }}</p>
            <p class="footer-text">{{ $t('WELCOME.FOOTER') }}</p>
        </div>
    </div>
</template>

<style scoped>
.welcome-message {
    width: 100%;
    margin: 20px auto;
    padding: 20px;
    background-color: #f0f4f8;
    border-radius: 8px;
    text-align: center;
    font-size: 14px;
    color: #333;
    font-family: Arial, sans-serif;
    text-align: justify;
}

.footer-text {
    font-style: italic;
    color: #666;
    margin-top: 1em;
}

.manage-container {
    min-height: 90vh;
}

</style>