module.exports = {
  pluginOptions: {
    i18n: {
      locale: 'kl',
      fallbackLocale: 'da',
      localeDir: 'i18n',
      enableInSFC: true
    }
  },
  assetsDir: 'static',
  baseUrl: '/index',
  devServer: {
    proxy: {
      '/inkassosag': {
        target: 'http://localhost:8000'
      },
      '/rentenota': {
        target: 'http://localhost:8000'
      }
    }
  }
}
