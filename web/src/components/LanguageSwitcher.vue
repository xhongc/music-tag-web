<template>
    <div class="language-switcher">
        <button @click="setLanguage('en')" :class="{ active: currentLanguage === 'en' }">
            🇬🇧 English
        </button>
        <button @click="setLanguage('zh')" :class="{ active: currentLanguage === 'zh' }">
            🇨🇳 中文
        </button>
    </div>
</template>

<script>
export default {
    name: 'LanguageSwitcher',
    data() {
        return {
            currentLanguage: localStorage.getItem('app-language') || 'en'
        }
    },
    methods: {
        setLanguage(lang) {
            this.currentLanguage = lang
            localStorage.setItem('app-language', lang)
            this.$i18n.locale = lang
            // Opcional: recargar la página para aplicar cambios completos
            window.location.reload()
        }
    }
}
</script>

<style scoped>
.language-switcher {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
    display: flex;
    gap: 10px;
    background: rgba(255, 255, 255, 0.9);
    padding: 8px 12px;
    border-radius: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.language-switcher button {
    background: none;
    border: none;
    padding: 4px 8px;
    cursor: pointer;
    border-radius: 16px;
    font-size: 12px;
    transition: all 0.2s;
}

.language-switcher button.active {
    background: #1facdd;
    color: white;
}

.language-switcher button:hover:not(.active) {
    background: #e0e0e0;
}
</style>