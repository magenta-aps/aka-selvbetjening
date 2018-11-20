<template>

    <article class="indberet_fordring">

        <h1>{{ $t('inkasso.title') }}</h1>

        <form @submit.prevent="sendFormRequest()" :class="{submitted: isSubmitted}">
            <fieldset>
              <s-field name="fordringshaver" :label="$t('inkasso.fordringshaver')" type="text" required v-model="fordringshaver"/>
              <s-field name="debitor" :label="$t('inkasso.debitor')" type="text" required v-model="debitor"/>
              <s-field name="fordringshaver2" :label="$t('inkasso.anden_fordringshaver')" type="text" v-model="fordringshaver2"/>
            </fieldset>

            <table>
                <thead>
                    <tr>
                        <th>{{ $t('inkasso.filnavn') }}</th>
                        <th>{{ $t('inkasso.stoerelse') }}</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody v-if="filer">
                    <tr v-for="(f, index) in filer" :key="index">
                        <td>{{ f.name }}</td>
                        <td>{{ f.size }} kB</td>
                        <td><a @click="deleteFile(index)">{{ $t('inkasso.slet') }}</a></td>
                    </tr>
                </tbody>
            </table>
            <input type="file" multiple @change="selectFiles($event.target.files)">

            <div style="display: flex; flex-flow: row wrap;">
                <fieldset>
                    <label id="lbl_fordringsgruppe" for="fordringsgruppe">{{ $t('inkasso.fordringsgruppe') }}</label>
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
                    <label id="lbl_fordringstype" for="fordringstype">{{ $t('inkasso.fordringstype') }}</label>
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
                <s-field name="barns_cpr" :label="$t('inkasso.barns_cpr')" type="text" v-model="barns_cpr"
                         minlength="10" maxlength="10"/>
                <s-field name="ekstern_sagsnummer" :label="$t('inkasso.ekstern_sagsnummer')" type="text"
                         v-model="ekstern_sagsnummer" required/>
                <s-field name="fakturanr" :label="$t('inkasso.fakturanr')" type="text" v-model="fakturanr" required/>
                <s-field name="bnr" :label="$t('inkasso.bnr')" type="text" v-model="bnr"/>
            </fieldset>

            <fieldset> <!--TODO: Fix wrapping -->
                <s-field name="hovedstol" :label="$t('inkasso.hovedstol')" type="text" v-model="hovedstol" required/>
                <s-field name="hovedstol_posteringstekst" :label="$t('inkasso.posteringstekst')" type="text"
                         v-model="hovedstol_posteringstekst" required/>

                <s-field name="bankrente" :label="$t('inkasso.bankrente')" type="text" v-model="bankrente"/>
                <s-field name="bankrente_posteringstekst" :label="$t('inkasso.posteringstekst')" type="text"
                         v-model="bankrente_posteringstekst"/>

                <s-field name="bankgebyr" :label="$t('inkasso.bankgebyr')" type="text" v-model="bankgebyr"/>
                <s-field name="bankgebyr_posteringstekst" :label="$t('inkasso.posteringstekst')" type="text"
                         v-model="bankgebyr_posteringstekst"/>

                <s-field name="rente" :label="$t('inkasso.rente')" type="text" v-model="rente"/>
                <s-field name="rente_posteringstekst" :label="$t('inkasso.posteringstekst')" type="text"
                         v-model="rente_posteringstekst"/>
            </fieldset>

            <fieldset>
                <s-field name="periodestart" :label="$t('inkasso.periodestart')" type="date" v-model="periodestart"/>
                <s-field name="periodeslut" :label="$t('inkasso.periodeslut')" type="date" v-model="periodeslut"/>
                <s-field name="forfaldsdato" :label="$t('inkasso.forfaldsdato')" type="date" v-model="forfaldsdato" required/>
                <s-field name="betalingsdato" :label="$t('inkasso.betalingsdato')" type="date"
                         v-model="betalingsdato" required/>
                <s-field name="foraeldelsesdato" :label="$t('inkasso.foraeldelsesdato')" type="date"
                         v-model="foraeldelsesdato" required/>
            </fieldset>

            <fieldset>
                <s-field name="kontaktperson" :label="$t('inkasso.kontaktperson')" type="text" v-model="kontaktperson"/>
                <s-field name="noter" :label="$t('inkasso.noter')" type="text" v-model="noter"/>
            </fieldset>

            <fieldset>
                <div v-for="(meddebitor, index) in meddebitorer" :key="index">
                    <label v-bind:for="meddebitor.index"> {{ $t('inkasso.meddebitor') }} {{index +1}}</label>
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
                <input type="submit" v-bind:value="$t('inkasso.gem')" @click="isSubmitted = true">
            </fieldset>

        </form>

    </article>

</template>

<script>
import axios from 'axios'
// The file fordringsgruppe.js below is generated by the command `make frontend`
import { groups } from '@/assets/fordringsgruppe'
import { notify } from '../utils/notify/Notifier.js'

export default {
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
    notify(`Welcome to this page. ${this.$t('inkasso.title')}`)
  }
}
</script>

 <style>
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
