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
  publicPath: '',
  devServer: {
    hot: true,
    hotOnly: true,
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
