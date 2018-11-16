<template>

    <article class="indberet_fordring">

        <h1>{{ $t('title') }}</h1>

        <form @submit.prevent="sendFormRequest()" :class="{submitted: isSubmitted}">
            <fieldset>
                <label id="lbl_fordringshaver" for="fordringshaver">{{ $t('fordringshaver') }}</label>
                <input id="fordringshaver"
                       type="text"
                       v-model="fordringshaver"
                       required>

                <label id="lbl_debitor" for="debitor">{{ $t('debitor') }}</label>
                <input id="debitor"
                       type="text"
                       v-model="debitor"
                       required>

                <label id="lbl_fordringshaver2" for="fordringshaver2">{{ $t('anden_fordringshaver') }}</label>
                <input id="fordringshaver2"
                       type="text"
                       v-model="fordringshaver2">
                <!--
                    TODO: Placeholder code ala:
                    Vue.component('text-input', {
                        props: ['name', 'isRequired'],
                        template: `
                        <label id="lbl_{{name}}" for="{{name}}">{{name}}</label>
                        <input id="{{name}}" type="text" v-model="{{name}}">
                        `
                    })
                -->
            </fieldset>

            <table>
                <thead>
                    <tr>
                        <th>{{ $t('filnavn') }}</th>
                        <th>{{ $t('stoerelse') }}</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody v-if="filer">
                    <tr v-for="(f, index) in filer" :key="index">
                        <td>{{ f.name }}</td>
                        <td>{{ f.size }} kB</td>
                        <td><a @click="deleteFile(index)">{{ $t('slet') }}</a></td>
                    </tr>
                </tbody>
            </table>
            <input type="file" multiple @change="selectFiles($event.target.files)">

            <div style="display: flex; flex-flow: row wrap;">
                <fieldset>
                    <label id="lbl_fordringsgruppe" for="fordringsgruppe">{{ $t('fordringsgruppe') }}</label>
                    <select
                            id="fordringsgruppe"
                            v-model="fordringsgruppe"
                            @change="updateType"
                            required
                    >
                        <option v-for="(f, index) in fordringsgrupper" :key="index" v-bind:value="f">{{stringRep(f)}}</option>
                    </select>
                </fieldset>

                <!--This is only shown if there are multiple options-->
                <fieldset v-if="multipleTypes">
                    <label id="lbl_fordringstype" for="fordringstype">{{ $t('fordringstype') }}</label>
                    <select
                            id="fordringstype"
                            v-model="fordringstype"
                            required
                    >
                        <option v-for="(t, index) in fordringsgruppe.sub_groups"
                                :key="index"
                                v-bind:value="t">
                            {{stringRep(t)}}
                        </option>
                    </select>
                </fieldset>
            </div>

            <fieldset>
                <label id="lbl_barns_cpr"
                       for="barns_cpr">{{ $t('barns_cpr') }}</label>
                <input id="barns_cpr"
                       type="text"
                       v-model="barns_cpr"
                       minlength="10"
                       maxlength="10">

                <label id="lbl_ekstern_sagsnummer" for="ekstern_sagsnummer">{{ $t('ekstern_sagsnummer') }}</label>
                <input id="ekstern_sagsnummer" type="text" v-model="ekstern_sagsnummer" required>

                <label id="lbl_fakturanr" for="fakturanr">{{ $t('fakturanr') }}</label>
                <input id="fakturanr" type="text" v-model="fakturanr" required>

                <label id="lbl_bnr" for="bnr">{{ $t('bnr') }}</label>
                <input id="bnr" type="text" v-model="bnr">
            </fieldset>

            <fieldset> <!--TODO: Fix wrapping -->
                <label id="lbl_hovedstol" for="hovedstol">{{ $t('hovedstol') }}</label>
                <input id="hovedstol" type="text" v-model="hovedstol" required>
                <label id="lbl_hovedstol_posteringstekst" for="hovedstol_posteringstekst">{{ $t('posteringstekst') }}</label>
                <input id="hovedstol_posteringstekst" type="text" v-model="hovedstol_posteringstekst" required>

                <label id="lbl_bankrente" for="bankrente">{{ $t('bankrente') }}</label>
                <input id="bankrente" type="text"  v-model="bankrente">
                <label id="lbl_bankrente_posteringstekst" for="bankrente_posteringstekst">{{ $t('posteringstekst') }}</label>
                <input id="bankrente_posteringstekst" type="text" v-model="bankrente_posteringstekst">

                <label id="lbl_bankgebyr" for="bankgebyr">{{ $t('bankgebyr') }}</label>
                <input id="bankgebyr" type="text" v-model="bankgebyr">
                <label id="lbl_bankgebyr_posteringstekst" for="bankgebyr_posteringstekst">{{ $t('posteringstekst') }}</label>
                <input id="bankgebyr_posteringstekst" type="text" v-model="bankgebyr_posteringstekst">

                <label id="lbl_rente" for="rente">{{ $t('rente') }}</label>
                <input id="rente" type="text" v-model="rente">
                <label id="lbl_rente_posteringstekst" for="rente_posteringstekst">{{ $t('posteringstekst') }}</label>
                <input id="rente_posteringstekst" type="text" v-model="rente_posteringstekst">
            </fieldset>

            <fieldset> <!--TODO: Fix wrapping -->
                <label id="lbl_periodestart" for="periodestart">{{ $t('periodestart') }}</label>
                <input id="periodestart" type="date" v-model="periodestart">

                <label id="lbl_periodeslut" for="periodeslut">{{ $t('periodeslut') }}</label>
                <input id="periodeslut" type="date" v-model="periodeslut">

                <label id="lbl_forfaldsdato" for="forfaldsdato">{{ $t('forfaldsdato') }}</label>
                <input id="forfaldsdato" type="date" v-model="forfaldsdato" required>

                <label id="lbl_betalingsdato" for="betalingsdato">{{ $t('betalingsdato') }}</label>
                <input id="betalingsdato" type="date" v-model="betalingsdato" required>

                <label id="lbl_foraeldelsesdato" for="foraeldelsesdato">{{ $t('foraeldelsesdato') }}</label>
                <input id="foraeldelsesdato" type="date" v-model="foraeldelsesdato" required>
            </fieldset>

            <fieldset>
                <label id="lbl_kontaktperson" for="kontaktperson">{{ $t('kontaktperson') }}</label>
                <input id="kontaktperson" type="text" v-model="kontaktperson">

                <label id="lbl_noter" for="noter">{{ $t('noter') }}</label>
                <input id="noter" type="text" v-model="noter">
            </fieldset>

            <fieldset>
                <div v-for="(meddebitor, index) in meddebitorer" :key="index">
                    <label v-bind:for="meddebitor.index"> {{ $t('meddebitor') }} {{index +1}}</label>
                    <div v-bind:id="meddebitor.index" @keyup.once="addNewMeddebitor">
                        <input type="text"
                               :disabled="meddebitor.cvr !== null && meddebitor.cvr !== ''"
                               v-model="meddebitor.cpr"
                               placeholder="CPR"
                               minlength="10"
                               maxlength="10">
                        <input type="text"
                               :disabled="meddebitor.cpr !== null && meddebitor.cpr !== ''"
                               v-model="meddebitor.cvr"
                               placeholder="CVR"
                               minlength="8"
                               maxlength="8">
                    </div>
                </div>
            </fieldset>

            <fieldset>
                <input type="submit" v-bind:value="$t('gem')" @click="isSubmitted = true">
            </fieldset>

        </form>

    </article>

</template>

<script>
import axios from 'axios'
// The file fordringsgruppe.js below is generated by the command `make frontend`
import { groups } from '@/assets/fordringsgruppe'
import { notify } from '../utils/notify/Notifier.js'

// Vue.component('text-input', {
//   props: ['name', 'isRequired'],
//   template: `
//     <label id="lbl_{{name}}" for="{{name}}">{{name}}</label>
//     <input id="{{name}}" type="text" v-model="{{name}}">
//     `
// })

export default {
  // components: {}
  data: function () {
    return {
      fordringshaver: null,
      debitor: null,
      fordringshaver2: null,
      fordringsgruppe: null,
      fordringstype: null,
      filer: [],
      valgte_filer: [],
      barns_cpr: null,
      ekstern_sagsnummer: null,
      fakturanr: null,
      bnr: null,
      hovedstol: null,
      hovedstol_posteringstekst: null,
      bankrente: null,
      bankrente_posteringstekst: null,
      bankgebyr: null,
      bankgebyr_posteringstekst: null,
      rente: null,
      rente_posteringstekst: null,
      periodestart: null,
      periodeslut: null,
      forfaldsdato: null,
      betalingsdato: null,
      foraeldelsesdato: null,
      kontaktperson: null,
      noter: null,
      meddebitorer: [
        {
          cpr: '',
          cvr: ''
        }
      ],

      form_fields: [
        'fordringshaver',
        'debitor',
        'fordringshaver2',
        'fordringsgruppe',
        'fordringstype',
        'barns_cpr',
        'ekstern_sagsnummer',
        'fakturanr',
        'bnr',
        'hovedstol',
        'hovedstol_posteringstekst',
        'bankrente',
        'bankrente_posteringstekst',
        'bankgebyr',
        'bankgebyr_posteringstekst',
        'rente',
        'rente_posteringstekst',
        'periodestart',
        'periodeslut',
        'forfaldsdato',
        'betalingsdato',
        'foraeldelsesdato',
        'kontaktperson',
        'noter'
      ],

      fordringsgrupper: groups,
      csrftoken: null,
      isSubmitted: false
    }
  },
  computed: {
    fordringstype_id: function () {
      return this.getId(this.fordringstype)
    },
    fordringsgruppe_id: function () {
      return this.getId(this.fordringsgruppe)
    },
    multipleTypes: function () {
      return (
        this.fordringsgruppe !== null &&
        this.fordringsgruppe['sub_groups'].length > 1
      )
    }
  },
  methods: {
    addNewMeddebitor: function () {
      this.meddebitorer.push({
        cpr: '',
        cvr: ''
      })
    },
    updateType: function () {
      if (
        this.fordringsgruppe !== null &&
        this.fordringsgruppe['sub_groups'].length === 1
      ) {
        this.fordringstype = this.fordringsgruppe['sub_groups'][0]
      } else {
        this.fordringstype = null
      }
    },
    getId: function (dict) {
      if (dict !== null && 'id' in dict) {
        return dict['id']
      }
      return null
    },
    stringRep: function (dict) {
      return '' + dict['id'] + ' (' + dict['value'] + ')'
    },
    getCSRFToken: function () {
      this.csrftoken = document.cookie.replace(
        /(?:(?:^|.*;\s*)csrftoken\s*=\s*([^;]*).*$)|^.*$/,
        '$1'
      )
    },
    selectFiles: function (files) {
      for (var i = 0; i < files.length; i++) {
        this.filer.push(files[i])
      }
    },
    deleteFile: function (index) {
      this.filer.splice(index, 1)
    },
    fetchFormData: function () {
      let formdata = new FormData()

      let that = this
      function appendData (string) {
        if (that[string] !== null) {
          if (string === 'fordringsgruppe' || string === 'fordringstype') {
            formdata.append(string, that[string + '_id'])
          } else {
            formdata.append(string, that[string])
          }
        }
      }

      this.form_fields.forEach(appendData)

      this.filer.forEach(function (fil, i) {
        let idx = i + 1
        formdata.append('fil' + idx, fil)
      })

      this.meddebitorer.forEach(function (meddebitor, i) {
        let idx = i + 1
        if (meddebitor.cpr !== '') {
          formdata.append('meddebitor' + idx + '_cpr', meddebitor.cpr)
        } else if (meddebitor.cvr !== '') {
          formdata.append('meddebitor' + idx + '_cvr', meddebitor.cvr)
        }
      })
      return formdata
    },
    sendFormRequest: function () {
      let formdata = this.fetchFormData()

      axios({
        url: '/inkassosag',
        data: formdata,
        method: 'post',
        headers: {
          'X-CSRFToken': this.csrftoken,
          'X-AKA-BRUGER': 'Unknown'
        }
      })
        .then(res => {
          notify('The server has responded and it was happy!')
          console.log('Server response!')
          console.log(res)
        })
        .catch(err => {
          console.log('there was an error')
          console.log(err.message)
        })
    }
  },
  created: function () {
    this.getCSRFToken()
    notify(`Welcome to this page. ${this.$t('title')}`)
  }
}
</script>

 <style scoped>
    input:focus:invalid {
        border: 2px solid #D7404D;
    }
    form.submitted input:invalid,
    form.submitted select:invalid{
       border: 2px solid #D7404D;
    }
    input[disabled] {
        background-color: #d6dbde;
    }
    table {
       border-collapse: collapse;
    }
    tr {
        border-bottom: 1px solid #ddd;
    }
</style>

<i18n>

  {
    "da": {
      "title": "Inkasso - Opret sag",
      "fordringshaver": "Fordringshaver",
      "anden_fordringshaver": "Anden fordringshaver",
      "debitor": "Debitor",
      "fordringsgruppe": "Ekstern fordringsgruppe",
      "fordringstype": "Ekstern fordringstype",
      "filnavn": "Filnavn",
      "stoerelse": "Størrelse",
      "slet": "Slet",
      "barns_cpr": "Barns CPR-nr",
      "ekstern_sagsnummer": "Ekstern sagsnummer",
      "fakturanr": "Fakturanr",
      "bnr": "B-nr",
      "hovedstol": "Hovedstol",
      "posteringstekst": "Posteringstekst",
      "bankrente": "Bankrente",
      "bankgebyr": "Bankgebyr",
      "rente": "Rente",
      "periodestart": "Periodestart",
      "periodeslut": "Periodeslut",
      "forfaldsdato": "Forfaldsdato",
      "betalingsdato": "Betalingsdato",
      "foraeldelsesdato": "Forældelsesdato",
      "kontaktperson": "Kontaktperson",
      "noter": "Noter",
      "meddebitor": "Meddebitor",
      "gem": "Gem"
    },
    "kl": {
      "title": "Akiliisitsiniarneq - suliamik pilersitsineq",
      "fordringshaver": "Akiligassaqarfigineqartoq",
      "anden_fordringshaver": "Akiligassaqarfigineqartoq alla",
      "debitor": "Akiligassalik",
      "fordringsgruppe": "Akiitsoqarfimmiit suliassiisutip ataatsimooruffiata suussusaa",
      "fordringstype": "Akiitsoqarfimmiit suliasiissutit suussusaa",
      "filnavn": "Fil-ip atia",
      "stoerelse": "Imartussuseq",
      "slet": "Nunguteruk",
      "barns_cpr": "Meeqqap inuup normua",
      "ekstern_sagsnummer": "Suliassiissutip akiitsoqarfimmiit normua",
      "fakturanr": "MANGLER",
      "bnr": "MANGLER",
      "hovedstol": "Akiitsup toqqammavia",
      "posteringstekst": "Nalunaarsornerani oqaasertaq",
      "bankrente": "Aningaaserivimmi erniarititaq",
      "bankgebyr": "Aningaaserivimmut akiliut",
      "rente": "Erniarititaq",
      "periodestart": "Piffissap aallartiffia",
      "periodeslut": "Piffissap naaffia",
      "forfaldsdato": "Ulloq akiligassap kingusinnerpaamik akilerneqarfissaa",
      "betalingsdato": "Ulloq akiliiffik",
      "foraeldelsesdato": "Pisoqalisoorfissaata ullua ",
      "kontaktperson": "Inuk atassuteqaataasoq",
      "noter": "Allaaserisaq",
      "meddebitor": "MANGLER",
      "gem": "Toqqoruk"
    }
  }

</i18n>
