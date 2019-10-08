export default {
  eight_or_ten_characters: (field) => `Værdien i feltet ${field} har forkert format (skal være 8 eller 10 cifre)`,
  currency: (field) => `Feltet ${field} har forkert format (skal angives med komma)`,
  date: (field) => `Værdien i feltet ${field} har forkert format (skal være i formatet dd-mm-yyyy)`,
  required: (field) => `Angiv venligst ${field}`
}
