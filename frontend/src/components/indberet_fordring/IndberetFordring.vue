<template>

  <article class="indberet_fordring" :key="fordring" v-if="!submittedSuccessfully">
    <form @submit.prevent="sendFormRequest()" :class="{submitted: isSubmitted}">
      <h1>{{ $t('inkasso.title') }}</h1>
      <div class="container-fluid">
        <div class="row">
          <div class="col-4">
            <s-field name="fordringshaver" :label="$t('attributes.fordringshaver')" type="text" v-model="fordringshaver"/>
          </div>
        </div>
        <div class="row">
          <div class="col-4">
            <s-field name="debitor" :label="$t('attributes.debitor')" type="text" required="true" :validate="{eight_or_ten_characters: true}" v-model="debitor"/>
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
          <label id="lbl_dokumentation" for="dokumentation">{{ $t('attributes.dokumentation') }}</label>
          <input id="dokumentation" type="file" multiple @change="selectFiles($event.target.files)">
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
            <td><a @click="deleteFile(index)">{{ $t('inkasso.slet') }}</a>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
      <div class="row">
        <div class="col-4">
          <label id="lbl_fordringsgruppe" for="fordringsgruppe">{{ $t('attributes.fordringsgruppe') }}</label>
          <select class="dropdown" id="fordringsgruppe" v-model="fordringsgruppe" @change="updateType" required>
            <option v-for="(f, index) in fordringsgrupper" :key="index" :value="f">
              {{stringRep(f)}}
            </option>
          </select>
        </div>
      </div>
      <div class="row" v-if="multipleTypes">
        <div class="col-4">
          <label id="lbl_fordringstype" for="fordringstype">{{ $t('attributes.fordringstype') }}</label>
          <select class="dropdown" id="fordringstype" v-model="fordringstype" required>
            <option v-for="(t, index) in fordringsgruppe.sub_groups" :key="index" :value="t">
              {{stringRep(t)}}
            </option>
          </select>
        </div>
      </div>
      <div class="row">
        <div class="col-3">
          <s-field name="barns_cpr" :label="$t('attributes.barns_cpr')" type="text" v-model="barns_cpr" :validate="{digits: 10}"/>
        </div>
      </div>
      <div class="row">
        <div class="col-3">
          <s-field name="ekstern_sagsnummer" :label="$t('attributes.ekstern_sagsnummer')" type="text" v-model="ekstern_sagsnummer" required="true"/>
        </div>
      </div>
      <div class="row">
        <div class="col-3">
          <s-field name="fakturanr" :label="$t('attributes.fakturanr')" type="text" v-model="fakturanr" required="true"/>
        </div>
      </div>
      <div class="row">
        <div class="col-3">
          <s-field name="bnr" :label="$t('attributes.bnr')" type="text" v-model="bnr"/>
        </div>
      </div>
      <div class="row">
        <div class="col-3">
          <c-field name="hovedstol" :label="$t('attributes.hovedstol')" type="text" v-model="hovedstol" required="true" :validate="{currency: true}"/>
        </div>
        <div class="col-6">
          <s-field name="hovedstol_posteringstekst" :label="$t('attributes.posteringstekst')" type="text" v-model="hovedstol_posteringstekst" required="true"/>
        </div>
      </div>
      <div class="row">
        <div class="col-3">
          <s-field name="periodestart" :label="$t('attributes.periodestart')" type="date" v-model="periodestart" required="true"/>
        </div>
        <div class="col-3">
          <s-field name="periodeslut" :label="$t('attributes.periodeslut')" type="date" v-model="periodeslut" required="true"/>
        </div>
        <div class="col-3">
          <s-field name="forfaldsdato" :label="$t('attributes.forfaldsdato')" type="date" v-model="forfaldsdato" required="true"/>
        </div>
      </div>
      <div class="row">
        <div class="col-3">
          <s-field name="betalingsdato" :label="$t('attributes.betalingsdato')" type="date" v-model="betalingsdato" required="true"/>
        </div>
        <div class="col-3">
          <s-field name="foraeldelsesdato" :label="$t('attributes.foraeldelsesdato')" type="date" v-model="foraeldelsesdato" required="true"/>
        </div>
      </div>
      <div class="row">
        <div class="col-4">
          <s-field name="kontaktperson" :label="$t('attributes.kontaktperson')" type="text" v-model="kontaktperson"/>
        </div>
      </div>
      <div class="row">
        <div class="col-4">
          <label for="noter">{{ $t('attributes.noter') }}</label>
          <textarea id="noter" cols="50" v-model="noter" required></textarea>
        </div>
      </div>
      <div class="row" v-for="(meddebitor, index) in meddebitorer" :key="index">
        <div @input.once="addNewMeddebitor">
          <div class="col-4">
            <label :for="meddebitor.index">{{ $t('attributes.meddebitor_nr', {nr: index + 1}) }}</label>
            <input :id="meddebitor.index" type="text" :disabled="meddebitor.cvr !== null && meddebitor.cvr !== ''" v-model="meddebitor.cpr" placeholder="CPR" v-validate="'digits:10'">
          </div>
          <div class="col-4">
            <label style="height: 24px;" class="hidden-sm" :for="meddebitor.index"></label>
            <input type="text" :disabled="meddebitor.cpr !== null && meddebitor.cpr !== ''" v-model="meddebitor.cvr" placeholder="GER" v-validate="'digits:8'">
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

  <article class="success" v-else>
    <form>
      <h1>{{ $t('inkasso.success') }}</h1>
      <div class="container-fluid">
        <div class="row">
          <div class="col-4">
            {{ $t('inkasso.nummervisning', { 'nummer': fordringsnummer }) }}
          </div>
        </div>
        <div class="row">
          <div class="col-4">
            <button @click="reload()">{{ $t('inkasso.reload') }}</button>
            <router-link to="/" tag="button">{{ $t('common.forside') }}</router-link>
          </div>
        </div>
      </div>
    </form>
  </article>

</template>

<script>
import axios from 'axios'
// The file fordringsgruppe.js below is generated by the command `make frontend`
import { groups } from '@/assets/fordringsgruppe'
import { notify, notifyError } from '../utils/notify/Notifier.js'
import formValid from '@/mixins/formValid'

export default {
  mixins: [formValid],
  data: function () {
    return {
      fordring: 1,
      fordringsnummer: null,
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
      isSubmitted: false,
      submittedSuccessfully: false
    }
  },
  computed: {
    fordringstype_id: function () {
      return this.getId(this.fordringstype);
    },
    fordringsgruppe_id: function () {
      return this.getId(this.fordringsgruppe);
    },
    multipleTypes: function () {
      return (this.fordringsgruppe !== null && this.fordringsgruppe['sub_groups'].length > 1);
    }
  },
  methods: {
    addNewMeddebitor: function () {
      this.meddebitorer.push({
        cpr: '',
        cvr: ''
      });
    },
    updateType: function () {
      if (this.fordringsgruppe !== null && this.fordringsgruppe['sub_groups'].length === 1) {
        this.fordringstype = this.fordringsgruppe['sub_groups'][0];
      } else {
        this.fordringstype = null;
      }
    },
    getId: function (dict) {
      if (dict !== null && 'id' in dict) {
        return dict['id'];
      }
      return null;
    },
    stringRep: function (dict) {
      return '' + dict['value'] + ' (' + dict['id'] + ')';
    },
    getCSRFToken: function () {
      this.csrftoken = document.cookie.replace(
        /(?:(?:^|.*;\s*)csrftoken\s*=\s*([^;]*).*$)|^.*$/,
        '$1'
      )
    },
    selectFiles: function (files) {
      for (let i = 0; i < files.length; i++) {
        this.filer.push(files[i]);
      }
    },
    deleteFile: function (index) {
      this.filer.splice(index, 1);
    },
    fetchFormData: function () {
      let formdata = new FormData();
      this.form_fields.forEach(string => {
        if (this[string] !== null) {
          if (string === 'fordringsgruppe' || string === 'fordringstype') {
            formdata.append(string, this[string + '_id']);
          } else {
            formdata.append(string, this[string]);
          }
        }
      });

      this.filer.forEach(function (fil, i) {
        let idx = i + 1;
        formdata.append('fil' + idx, fil);
      });

      this.meddebitorer.forEach(function (meddebitor, i) {
        let idx = i + 1;
        if (meddebitor.cpr !== '') {
          formdata.append('meddebitor' + idx + '_cpr', meddebitor.cpr);
        } else if (meddebitor.cvr !== '') {
          formdata.append('meddebitor' + idx + '_cvr', meddebitor.cvr);
        }
      });
      return formdata
    },
    sendFormRequest: function () {
      if (!this.formValid) {
        this.$validator.validateAll();
        return;
      }

      let formdata = this.fetchFormData();

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
          this.fordringsnummer = res.data['rec_id'] || res.data['response']['rec_id'];
          this.submittedSuccessfully = true;
        })
        .catch(error => {
          notifyError(error, localStorage.getItem('language') || 'kl', this._i18n);
        });
    },
    reload: function () {
      this.form_fields.forEach(name => {
        this[name] = null;
      });
      this.filer = [];
      this.valgte_filer = [];
      this.meddebitorer = [{ cpr: '', cvr: '' }];

      this.fordringsnummer = null;
      this.fordring += 1;
      this.submittedSuccessfully = false;
    }
  },
  created: function () {
    this.getCSRFToken();
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
    textarea {
        resize: none;
    }
</style>
