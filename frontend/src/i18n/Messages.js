import attributesDa from './attributes/da.js'
import attributesKl from './attributes/kl.js'
export const messages = {
  da: {
    common: {
      send: 'Send',
      print: 'Print',
      gem: 'Gem',
      indberet: 'Indberet',
      tilbage: 'Tilbage',
      cpr_nr: 'CPR-nr',
      indlaes: 'Indlæs',
      fejl: 'Fejl'
    },
    rentenota: {
      titel: 'Hent rentenota',
      datefrom: 'Fra dato',
      dateto: 'Til dato',
      dato: 'Dato',
      postdato: 'Postdato',
      bilag: 'Bilag',
      faktura: 'Faktura',
      tekst: 'Tekst',
      fradato: 'Fradato',
      dage: 'Dage',
      grundlag: 'Grundlag',
      val: 'Val',
      beloeb: 'Beløb',
      konto: 'Konto',
      telefon: 'Oq/Telefon',
      fax: 'Fax',
      email: 'Email',
      webadresse: 'Web-adresse'
    },
    form2: {
      title: 'Formular nummer 2',
      inputa: 'Inputfelt A',
      inputb: 'Inputfelt B',
      send: 'Send'
    },
    inkasso: {
      title: 'Inkasso - Opret sag',
      filnavn: 'Filnavn',
      stoerelse: 'Størrelse',
      slet: 'Slet'
    },
    loentraek: {
      titel1: 'Løntræk - Indberet',
      titel2: 'Løntræk - Indberet pr. CPR-nr.',
      ger_nr: 'GER-nr.',
      traekmaaned: 'Trækmåned',
      loentraek: 'Løntræk',
      fordel_pr_cpr: 'Fordel pr. CPR-nr',
      indlaes_fra_fil: 'Indlæs fra fil',
      indlaes_fra_forrige_redegoerelse: 'Indlæs fra forrige redegørelse',
      aftalenr: 'Aftalanr',
      nettoloen: 'Nettoløn',
      fordeling: 'Fordeling',
      fordelt: 'Fordelt',
      difference: 'Difference'
    },
    beskeder: {
      ekstern_sagsnummer_findes_allerede: 'Fejl: Fordringshaver har allerede en inkassosag med det angivede eksterne sagsnummer',
      ekstern_sagsnummer_findes_i_kladde: 'Fejl: Fordringshaver har allerede en inkassosag med det angivede eksterne sagsnummer (under oprettelse)',
      arbejdsgiver_ikke_fundet: 'Fejl: Arbejdsgiver ikke fundet ud fra debitor-kontonummer',
      inkasso_sag_oprettet: 'Inkasso-sagen er nu blevet oprettet',
      inkassosag_kvittering: 'Kvittering: Der blev oprettet en inkassosag | Kvittering: Der blev oprettet {n} inkassosager',
      datafil_ikke_indlaest: 'Datafilen blev ikke indlæst',
      linjer_i_datafil: 'Linjer i datafil',
      afviste: 'afviste',
      linjeangivelse: 'Fordringshaver angivet på linje {0} er ikke tilladt'
    },
    attributes: attributesDa
  },
  kl: {
    common: {
      send: 'Send - oversættelse mangler',
      print: 'Print - oversættelse mangler',
      gem: 'Toqqoruk',
      indberet: 'Nalunaarneq',
      tilbage: 'Uterit',
      cpr_nr: 'Inuup normua',
      indlaes: 'Indlæs - oversættelse mangler',
      fejl: 'Fejl - oversættelse mangler'
    },
    rentenota: {
      title: 'Hent rentenota - oversættelse mangler',
      datefrom: 'Fra dato - oversættelse mangler',
      dateto: 'Til dato - oversættelse mangler',
      dato: 'Dato - oversættelse mangler',
      postdato: 'Postdato - oversættelse mangler',
      bilag: 'Bilag - oversættelse mangler',
      faktura: 'Faktura - oversættelse mangler',
      tekst: 'Tekst - oversættelse mangler',
      fradato: 'Fradato - oversættelse mangler',
      dage: 'Dage - oversættelse mangler',
      grundlag: 'Grundlag - oversættelse mangler',
      val: 'Val - oversættelse mangler',
      beloeb: 'Beløb - oversættelse mangler',
      konto: 'Konto - oversættelse mangler',
      telefon: 'Oq/Telefon - oversættelse mangler',
      fax: 'Fax - oversættelse mangler',
      email: 'Email - oversættelse mangler',
      webadresse: 'Web-adresse - oversættelse mangler'
    },
    form2: {
      title: 'Sullinnermi Sullinnermi',
      inputa: 'Sullinnermi',
      inputb: 'Sullinnermi',
      send: 'Sullinnermi'
    },
    inkasso: {
      title: 'Akiliisitsiniarneq - suliamik pilersitsineq',
      filnavn: 'Fil-ip atia',
      stoerelse: 'Imartussuseq',
      slet: 'Nunguteruk'
    },
    loentraek: {
      titel1: 'Aningaasarsianit ilanngartuineq - Immersoruk',
      titel2: 'Aningaasarsianit ilanngartuinermi - Inuup normukaarlugit nalunaarsuigit',
      ger_nr: 'GER-normu',
      traekmaaned: 'Qaammat ilanngaanneqarfik',
      loentraek: 'Isumaqatigiissutip aningaasartaa',
      fordel_pr_cpr: 'Inuup normuinut agguataarlugit',
      indlaes_fra_fil: 'Fiilimit atuaagit',
      indlaes_fra_forrige_redegoerelse: 'Nalunaarummit siusinnerusumit atuaagit',
      aftalenr: 'Isumaqatigiissutip normua',
      nettoloen: 'Aningaasarsiat tunniussat',
      fordeling: 'Agguaassassaq',
      fordelt: 'Agguakkat',
      difference: 'Nikingassutaasut'
    },
    beskeder: {
      ekstern_sagsnummer_findes_allerede: 'Fejl: Fordringshaver har allerede en inkassosag med det angivede eksterne sagsnummer - oversættelse mangler',
      ekstern_sagsnummer_findes_i_kladde: 'Fejl: Fordringshaver har allerede en inkassosag med det angivede eksterne sagsnummer (under oprettelse) - oversættelse mangler',
      arbejdsgiver_ikke_fundet: 'Fejl: Arbejdsgiver ikke fundet ud fra debitor-kontonummer - oversættelse mangler',
      inkasso_sag_oprettet: 'Inkasso-sagen er nu blevet oprettet - oversættelse mangler',
      inkassosag_kvittering: 'Kvittering: Der blev oprettet en inkassosag - oversættelse mangler | Kvittering: Der blev oprettet {n} inkassosager - oversættelse mangler',
      datafil_ikke_indlaest: 'Datafilen blev ikke indlæst',
      linjer_i_datafil: 'Linjer i datafil',
      afviste: 'afviste',
      linjeangivelse: 'Fordringshaver angivet på linje {0} er ikke tilladt - oversættelse mangler'
    },
    attributes: attributesKl
  }
}
