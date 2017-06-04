module.exports = {
  'getEnvConfig': (envName) => {
    var envConfig = require('../../config/' + envName)
    return envConfig
  }
}
