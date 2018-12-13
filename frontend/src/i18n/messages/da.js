export default {
  age: (field, [args]) => `Dansk fejlbesked for Age. Field: ${field}. Argument: ${args}.`,
  eight_or_ten_characters: (field) => `Værdien i feltet ${field} har forkert format (skal være 8 eller 10 cifre)`
}
