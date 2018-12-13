const rules = {
  'eight_or_ten_characters': {
    validate: (value) => {
      if (value === undefined || value === null) {
        return false
      }
      return (String(value).length === 8 || String(value).length === 10)
    },
    'age': {
      validate: (value, [args]) => parseInt(value) >= parseInt(args)
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
