const rules = {
  'eight_or_ten_characters': {
    validate: (value) => {
      if (value === undefined || value === null) {
        return false
      }
      // return (String(value).length === 8 || String(value).length === 10)
      return /^(\d{8}|\d{10})$/.test(String(value))
    }
  },
  'currency': {
    validate: (value) => {
      if (value === undefined || value === null) {
        return false
      }
      return /^([1-9]\d{1,2}(?:\.\d{3})+|[1-9]\d*|0)(,\d{1,2})?$/.test(value)
      //return /^([1-9]\d*|0)(,\d+)?$/.test(String(value))
    }
  }
}

// export an 'install' function.
export default (Validator) => {
  // for every rule we defined above.
  Object.keys(rules).forEach(rule => {
    //  add the rule.
    Validator.extend(rule, rules[rule])
  })
}
