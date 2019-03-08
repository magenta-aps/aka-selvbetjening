<template>

    <article class="indberet_fordring">

        <form @submit.prevent="sendFormRequest()" :class="{submitted: isSubmitted}">

          <h1>{{ $t('inkasso.title') }}</h1>

<!--          <ul v-if="isSubmitted">
            <li v-for="error in errors.items">{{ error.msg }}</li>
          </ul>-->

          <div class="container-fluid">
            <div class="row">
              <div class="col-4">
                <s-field name="fordringshaver" :label="$t('attributes.fordringshaver')" type="text" :validate="{required: true}" v-model="fordringshaver"/>
              </div>
            </div>
            <div class="row">
              <div class="col-4">
                <s-field name="debitor" :label="$t('attributes.debitor')" type="text" :validate="{required: true, eight_or_ten_characters: true}" v-model="debitor"/>
              </div>
            </div>
            <div class="row">
              <div class="col-4">
                <s-field name="fordringshaver2" :label="$t('attributes.anden_fordringshaver')" type="text" v-model="fordringshaver2"/>
              </div>
            </div>
            </div>
            <div class="row">
              <div class="col-12">
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
              </div>
            </div>
            <div class="row">
              <div class="col-12">
                <input type="file" multiple @change="selectFiles($event.target.files)">
              </div>
            </div>
            <div class="row">
              <div class="col-4">
                <label id="lbl_fordringsgruppe" for="fordringsgruppe">{{ $t('attributes.fordringsgruppe') }}</label>
                <select
                  class="dropdown"
                  id="fordringsgruppe"
                  v-model="fordringsgruppe"
                  @change="updateType"
                  v-validate="{required: true}"
                >
                  <option v-for="(f, index) in fordringsgrupper" :key="index" :value="f">{{stringRep(f)}}</option>
                </select>
              </div>
            </div>
            <div class="row" v-if="multipleTypes">
              <div class="col-4">
                <label id="lbl_fordringstype" for="fordringstype">{{ $t('attributes.fordringstype') }}</label>
                <select
                  class="dropdown"
                  id="fordringstype"
                  v-model="fordringstype"
                  v-validate="{required: true}"
                >
                  <option v-for="(t, index) in fordringsgruppe.sub_groups"
                          :key="index"
                          :value="t">
                    {{stringRep(t)}}
                  </option>
                </select>
              </div>
            </div>
            <div class="row">
              <div class="col-3">
                <s-field name="barns_cpr" :label="$t('attributes.barns_cpr')" type="text" v-model="barns_cpr"
                         :validate="{digits: 10}"/>
              </div>
            </div>
            <div class="row">
              <div class="col-3">
                <s-field name="ekstern_sagsnummer" :label="$t('attributes.ekstern_sagsnummer')" type="text"
                         v-model="ekstern_sagsnummer" :validate="{required: true}"/>
              </div>
            </div>
            <div class="row">
              <div class="col-3">
                <s-field name="fakturanr" :label="$t('attributes.fakturanr')" type="text" v-model="fakturanr" :validate="{required: true}"/>
              </div>
            </div>
            <div class="row">
              <div class="col-3">
                <s-field name="bnr" :label="$t('attributes.bnr')" type="text" v-model="bnr"/>
              </div>
            </div>
            <div class="row">
              <div class="col-3">
                <s-field name="hovedstol" :label="$t('attributes.hovedstol')" type="text" v-model="hovedstol" :validate="{required: true, currency: true}"/>
              </div>
              <div class="col-6">
                <s-field name="hovedstol_posteringstekst" :label="$t('attributes.posteringstekst')" type="text"
                         v-model="hovedstol_posteringstekst" :validate="{required: true}" />
              </div>
            </div>
            <div class="row">
              <div class="col-3">
                <s-field name="bankrente" :label="$t('attributes.bankrente')" type="text" v-model="bankrente"/>
              </div>
              <div class="col-6">
                <s-field name="bankrente_posteringstekst" :label="$t('attributes.posteringstekst')" type="text"
                         v-model="bankrente_posteringstekst"/>
              </div>
            </div>
            <div class="row">
              <div class="col-3">
                <s-field name="bankgebyr" :label="$t('attributes.bankgebyr')" type="text" v-model="bankgebyr" :validate="{currency: true}"/>
              </div>
              <div class="col-6">
                <s-field name="bankgebyr_posteringstekst" :label="$t('attributes.posteringstekst')" type="text"
                         v-model="bankgebyr_posteringstekst"/>
              </div>
            </div>
            <div class="row">
              <div class="col-3">
                <s-field name="rente" :label="$t('attributes.rente')" type="text" v-model="rente"/>
                </div>
              <div class="col-6">
                <s-field name="rente_posteringstekst" :label="$t('attributes.posteringstekst')" type="text"
                         v-model="rente_posteringstekst"/>
              </div>
            </div>
            <div class="row">
              <div class="col-3">
                <s-field name="periodestart" :label="$t('attributes.periodestart')" type="date" v-model="periodestart"/>
              </div>
              <div class="col-3">
                <s-field name="periodeslut" :label="$t('attributes.periodeslut')" type="date" v-model="periodeslut"/>
              </div>
              <div class="col-3">
                <s-field name="forfaldsdato" :label="$t('attributes.forfaldsdato')" type="date" v-model="forfaldsdato" :validate="{required: true}"/>
              </div>
            </div>
            <div class="row">
              <div class="col-3">
                <s-field name="betalingsdato" :label="$t('attributes.betalingsdato')" type="date"
                         v-model="betalingsdato" :validate="{required: true}"/>
              </div>
              <div class="col-3">
                <s-field name="foraeldelsesdato" :label="$t('attributes.foraeldelsesdato')" type="date"
                         v-model="foraeldelsesdato" :validate="{required: true}"/>
              </div>
            </div>
            <div class="row">
              <div class="col-4">
                <s-field name="kontaktperson" :label="$t('attributes.kontaktperson')" type="text" v-model="kontaktperson"/>
              </div>
            </div>
            <div class="row">
              <div class="col-4">
                <!--<s-field name="noter" :label="$t('attributes.noter')" type="text" v-model="noter"/>-->
                <label for="noter">{{ $t('attributes.noter') }}</label>
                <textarea id="noter" cols="50" v-model="noter"></textarea>
              </div>
            </div>

            <div class="row" v-for="(meddebitor, index) in meddebitorer" :key="index">
                <div @keyup.once="addNewMeddebitor">
                  <div class="col-4">
                    <label :for="meddebitor.index"> {{ $t('attributes.meddebitor') }} {{index +1}}</label>
                    <input :id="meddebitor.index"
                           type="text"
                           :disabled="meddebitor.cvr !== null && meddebitor.cvr !== ''"
                           v-model="meddebitor.cpr"
                           placeholder="CPR"
                           v-validate="'digits:10'">
                  </div>
                  <div class="col-4">
                    <label style="height: 24px;" class="hidden-sm" :for="meddebitor.index"></label>
                    <input type="text"
                           :disabled="meddebitor.cpr !== null && meddebitor.cpr !== ''"
                           v-model="meddebitor.cvr"
                           placeholder="GER"
                           v-validate="'digits:8'">
                  </div>
                </div>
            </div>

          <div class="row">
            <div class="col-2">
                <input type="submit" :value="$t('common.gem')" @click="isSubmitted = true">
            </div>
          </div>

        </form>

    </article>

</template>

<script>
import axios from 'axios'
// The file fordringsgruppe.js below is generated by the command `make frontend`
import { groups } from '@/assets/fordringsgruppe'
import { notify } from '../utils/notify/Notifier.js'
import formValid from '@/mixins/formValid'

export default {
  mixins: [formValid],
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
      if (!this.formValid) {
        this.$validator.validateAll()
        return
      }

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

 <style scoped>
    tr {
        border-bottom: 1px solid #ddd;
    }
    .dropdown {
      border: 1px solid #EAECEE;
    }
</style>
