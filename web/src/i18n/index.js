import { createI18n } from 'vue-i18n';

const messages = {
  en: {
    welcome: 'Welcome',
    goodbye: 'Goodbye'
  },
  zh: {
    welcome: '欢迎',
    goodbye: '再见'
  }
};

const i18n = createI18n({
  locale: 'en', // set default locale
  messages,
});

export default i18n;