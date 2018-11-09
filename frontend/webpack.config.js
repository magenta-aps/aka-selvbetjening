module.exports = {
  entry: ['@babel/polyfill', './app/js'],
  loaders: [
    { test: /\.js$/, exclude: /node_modules/, loader: 'babel-loader' }
  ]
}
