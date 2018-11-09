<template>

    <article class="indberet_fordring">

        <h1>{{ $t("title") }}</h1>
        <!--
            General notes:
            Code looks neat and functional. Good job!
            But do make use of HTML form validation. It's easy to implement and saves users a lot of headache.

            The quickest fix is to set the "required" attribute on mandatory input fields.
            This will prevent the browser from submitting the form if there are inputs missing.
            The browser will gently remind users of this. ( ... I think)

            This fascinating subject can be studied in detail here :D
            https://developer.mozilla.org/en-US/docs/Learn/HTML/Forms/Form_validation#Using_built-in_form_validation
        -->

        <form @submit.prevent="sendFormRequest()">

            <fieldset>
                <label id="lbl_fordringshaver" for="fordringshaver">{{ $t("fordringshaver") }}</label>
                <input id="fordringshaver"
                       type="text"
                       :class="{submitted: isSubmitted}"
                       v-model="fordringshaver"
                       required>

                <label id="lbl_debitor" for="debitor">{{ $t("debitor") }}</label>
                <input id="debitor"
                       type="text"
                       :class="{submitted: isSubmitted}"
                       v-model="debitor"
                       required>

                <label id="lbl_fordringshaver2" for="fordringshaver2">{{ $t("anden_fordringshaver") }}</label>
                <input id="fordringshaver2"
                       type="text"
                       :class="{submitted: isSubmitted}"
                       v-model="fordringshaver2">
                <!--
                    TODO: Placeholder code ala:
                    Vue.component('text-input', {
                        props: ['name', 'isRequired'],
                        template: `
                        <label id="lbl_{{name}}" for="tb_{{name}}">{{name}}</label>
                        <input id="{{name}}" type="text" :class="{submitted: isSubmitted}" v-model="{{name}}">
                        `
                    })
                -->
            </fieldset>


            <!--TODO: Allow multiple files and show file list-->
            <!--
               This is actually quite easy. Add the "multiple" attribute  to the input element.
               Then use getFileData to extract the list of files.
               The template should magically display it if you add something like
               ```
                   <table v-if="files">
                     <tr v-for="(f, index) in files" :key="index">
                       <td>{{ f.name }}</td>
                       <td>{{ f.size }} kB</td>
                     </tr>
                   </table>
               ```
               Maybe iterating over af Filelist like this will cause you problems.
               Then you should convert it to an array in getFileData.
               See https://developer.mozilla.org/en-US/docs/Web/API/FileList
               and https://developer.mozilla.org/en-US/docs/Web/API/File for more info on working with files.
            -->
            <fieldset>
                <input type="file" :class="{submitted: isSubmitted}" @change="getFileData($event.target.files)">
            </fieldset>


            <div style="display: flex; flex-flow: row wrap;">
                <fieldset>
                    <label id="lbl_fordringsgruppe" for="fordringsgruppe">{{ $t("fordringsgruppe") }}</label>
                    <select
                            id="fordringsgruppe"
                            :class="{submitted: isSubmitted}"
                            v-model="fordringsgruppe"
                            @change="updateType"
                            required
                    >
                        <option v-for="f in fordringsgrupper" v-bind:value="f">{{stringRep(f)}})</option>
                    </select>
                </fieldset>

                <!--This is only shown if there are multiple options-->
                <fieldset v-if="multipleTypes">
                    <label id="lbl_fordringstype" for="fordringstype">{{ $t("fordringstype") }}</label>
                    <select
                            :class="{submitted: isSubmitted}"
                            id="fordringstype"
                            v-model="fordringstype"
                            required
                    >
                        <option v-for="t in fordringsgruppe.sub_groups"
                                v-bind:value="t">
                            {{stringRep(t)}}
                        </option>
                    </select>
                </fieldset>
            </div>


            <fieldset>
                <label id="lbl_barns_cpr"
                       for="tb_barns_cpr">{{ $t("barns_cpr") }}</label>
                <input id="tb_barns_cpr"
                       type="text"
                       :class="{submitted: isSubmitted}"
                       v-model="barns_cpr"
                       minlength="10"
                       maxlength="10">

                <label id="lbl_ekstern_sagsnummer" for="tb_ekstern_sagsnummer">{{ $t("ekstern_sagsnummer") }}</label>
                <input id="tb_ekstern_sagsnummer" type="text" :class="{submitted: isSubmitted}" v-model="ekstern_sagsnummer" required>

                <label id="lbl_fakturanr" for="tb_fakturanr">{{ $t("fakturanr") }}</label>
                <input id="tb_fakturanr" type="text" :class="{submitted: isSubmitted}" v-model="fakturanr" required>

                <label id="lbl_bnr" for="tb_bnr">{{ $t("bnr") }}</label>
                <input id="tb_bnr" type="text" :class="{submitted: isSubmitted}" v-model="bnr">
            </fieldset>

            <fieldset> <!--TODO: Fix wrapping -->
                <label id="lbl_hovedstol" for="tb_hovedstol">{{ $t("hovedstol") }}</label>
                <input id="tb_hovedstol" type="text" :class="{submitted: isSubmitted}" v-model="hovedstol" required>
                <label id="lbl_hovedstol_posteringstekst" for="tb_hovedstol_posteringstekst">{{ $t("posteringstekst") }}</label>
                <input id="tb_hovedstol_posteringstekst" type="text" :class="{submitted: isSubmitted}" v-model="hovedstol_posteringstekst" required>

                <label id="lbl_bankrente" for="tb_bankrente">{{ $t("bankrente") }}</label>
                <input id="tb_bankrente" type="text" :class="{submitted: isSubmitted}" v-model="bankrente">
                <label id="lbl_bankrente_posteringstekst" for="tb_bankrente_posteringstekst">{{ $t("posteringstekst") }}</label>
                <input id="tb_bankrente_posteringstekst" type="text" :class="{submitted: isSubmitted}" v-model="bankrente_posteringstekst">

                <label id="lbl_bankgebyr" for="tb_bankgebyr">{{ $t("bankgebyr") }}</label>
                <input id="tb_bankgebyr" type="text" :class="{submitted: isSubmitted}" v-model="bankgebyr">
                <label id="lbl_bankgebyr_posteringstekst" for="tb_bankgebyr_posteringstekst">{{ $t("posteringstekst") }}</label>
                <input id="tb_bankgebyr_posteringstekst" type="text" :class="{submitted: isSubmitted}" v-model="bankgebyr_posteringstekst">

                <label id="lbl_rente" for="tb_rente">{{ $t("rente") }}</label>
                <input id="tb_rente" type="text" :class="{submitted: isSubmitted}" v-model="rente">
                <label id="lbl_rente_posteringstekst" for="tb_rente_posteringstekst">{{ $t("posteringstekst") }}</label>
                <input id="tb_rente_posteringstekst" type="text" :class="{submitted: isSubmitted}" v-model="rente_posteringstekst">
            </fieldset>

            <fieldset> <!--TODO: Fix wrapping -->
                <label id="lbl_periodestart" for="tb_periodestart">{{ $t("periodestart") }}</label>
                <input id="tb_periodestart" type="date" :class="{submitted: isSubmitted}" v-model="periodestart">

                <label id="lbl_periodeslut" for="tb_periodeslut">{{ $t("periodeslut") }}</label>
                <input id="tb_periodeslut" type="date" :class="{submitted: isSubmitted}" v-model="periodeslut">

                <label id="lbl_forfaldsdato" for="tb_forfaldsdato">{{ $t("forfaldsdato") }}</label>
                <input id="tb_forfaldsdato" type="date" :class="{submitted: isSubmitted}" v-model="forfaldsdato" required>

                <label id="lbl_betalingsdato" for="tb_betalingsdato">{{ $t("betalingsdato") }}</label>
                <input id="tb_betalingsdato" type="date" :class="{submitted: isSubmitted}" v-model="betalingsdato" required>

                <label id="lbl_foraeldelsesdato" for="tb_foraeldelsesdato">{{ $t("foraeldelsesdato") }}</label>
                <input id="tb_foraeldelsesdato" type="date" :class="{submitted: isSubmitted}" v-model="foraeldelsesdato" required>
            </fieldset>

            <fieldset>
                <label id="lbl_kontaktperson" for="tb_kontaktperson">{{ $t("kontaktperson") }}</label>
                <input id="tb_kontaktperson" type="text" :class="{submitted: isSubmitted}" v-model="kontaktperson">

                <label id="lbl_noter" for="tb_nrtes">{{ $t("noter") }}</label>
                <input id="tb_nrtes" type="text" :class="{submitted: isSubmitted}" v-model="noter">
            </fieldset>

            <fieldset>
                <div v-for="(meddebitor, index) in meddebitorer">
                    <label v-bind:for="meddebitor.index"> {{ $t("meddebitor") }} {{index +1}}</label>
                    <div v-bind:id="meddebitor.index" @keyup.once="addNewMeddebitor">
                        <input type="text"
                               :class="{submitted: isSubmitted}"
                               :disabled="meddebitor.cvr !== null && meddebitor.cvr !== ''"
                               v-model="meddebitor.cpr"
                               placeholder="CPR"
                               minlength="10"
                               maxlength="10">
                        <input type="text"
                               :class="{submitted: isSubmitted}"
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
import axios from "axios"
// The file fordringsgruppe.js below is generated by the command `make frontend`
import { groups } from "@/assets/fordringsgruppe"
import { notify } from "../utils/notify/Notifier.js"

export default {
  data: function() {
    return {
      fordringshaver: null,
      debitor: null,
      fordringshaver2: null,
      fordringsgruppe: null,
      fordringstype: null,
      fil: null /*TODO: make this a list of files*/,
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
          cpr: "",
          cvr: ""
        }
      ],

      form_fields: [
        "fordringshaver",
        "debitor",
        "fordringshaver2",
        "fordringsgruppe",
        "fordringstype",
        "fil",
        "barns_cpr",
        "ekstern_sagsnummer",
        "fakturanr",
        "bnr",
        "hovedstol",
        "hovedstol_posteringstekst",
        "bankrente",
        "bankrente_posteringstekst",
        "bankgebyr",
        "bankgebyr_posteringstekst",
        "rente",
        "rente_posteringstekst",
        "periodestart",
        "periodeslut",
        "forfaldsdato",
        "betalingsdato",
        "foraeldelsesdato",
        "kontaktperson",
        "noter"
      ],

      fordringsgrupper: groups,
      csrftoken: null
    };
  },
  computed: {
    fordringstype_id: function() {
      return this.getId(this.fordringstype);
    },
    fordringsgruppe_id: function() {
      return this.getId(this.fordringsgruppe);
    },
    multipleTypes: function() {
      return (
        this.fordringsgruppe !== null &&
        this.fordringsgruppe["sub_groups"].length > 1
      );
    }
  },
  methods: {
    addNewMeddebitor: function() {
      this.meddebitorer.push({
        cpr: "",
        cvr: ""
      });
    },
    updateType: function() {
      if (
        this.fordringsgruppe !== null &&
        this.fordringsgruppe["sub_groups"].length === 1
      ) {
        this.fordringstype = this.fordringsgruppe["sub_groups"][0];
      } else {
        this.fordringstype = null;
      }
    },
    getId: function(dict) {
      if (dict !== null && "id" in dict) {
        return dict["id"];
      }
      return null;
    },
    stringRep: function(dict) {
      return "" + dict["id"] + " (" + dict["value"] + ")";
    },
    getCSRFToken: function() {
      this.csrftoken = document.cookie.replace(
        /(?:(?:^|.*;\s*)csrftoken\s*\=\s*([^;]*).*$)|^.*$/,
        "$1"
      );
    },
    getFileData: function(files) {
      this.fil = files[0];
    },
    fetchFormData: function() {
      let formdata = new FormData();
      let that = this;
      function appendData(string) {
        if (that[string] !== null) {
          if (string === "fordringsgruppe" || string === "fordringstype") {
            formdata.append(string, that[string + "_id"]);
          } else {
            formdata.append(string, that[string]);
          }
        }
      }

      this.form_fields.forEach(appendData);

      this.meddebitorer.forEach(function(meddebitor, i) {
        let idx = i + 1;
        if (!(meddebitor.cpr === "" || meddebitor.cvr === "")) {
          formdata.append("meddebitor" + idx + "_cpr", meddebitor.cpr);
          formdata.append("meddebitor" + idx + "_cvr", meddebitor.cvr);
        }
      });
      return formdata;
    },
    sendFormRequest: function() {
      let formdata = this.fetchFormData();
      // formdata.append('fordringshaver', this.fordringshaver);
      // formdata.append('debitor', this.debitor);
      // formdata.append('fordringshaver2', this.fordringshaver2);
      // formdata.append('fordringsgruppe', this.fordringsgruppe_id);
      // formdata.append('fordringstype', this.fordringstype_id);
      // formdata.append('file', this.file);
      // formdata.append('barns_cpr', this.barns_cpr);
      // formdata.append('ekstern_sagsnummer', this.ekstern_sagsnummer);
      // formdata.append('fakturanr', this.fakturanr);
      // formdata.append('bnr', this.bnr);
      // formdata.append('hovedstol', this.hovedstol);
      // formdata.append('hovedstol_posteringstekst', this.hovedstol_posteringstekst);
      // formdata.append('bankrente', this.bankrente);
      // formdata.append('bankrente_posteringstekst', this.bankrente_posteringstekst);
      // formdata.append('bankgebyr', this.bankgebyr);
      // formdata.append('bankgebyr_posteringstekst', this.bankgebyr_posteringstekst);
      // formdata.append('rente', this.rente);
      // formdata.append('rente_posteringstekst', this.rente_posteringstekst);
      // formdata.append('periodestart', this.periodestart);
      // formdata.append('periodeslut', this.periodeslut);
      // formdata.append('forfaldsdato', this.forfaldsdato);
      // formdata.append('betalingsdato', this.betalingsdato);
      // formdata.append('foraeldelsesdato', this.foraeldelsesdato);
      // formdata.append('kontaktperson', this.kontaktperson);
      // formdata.append('noter', this.noter);

      axios({
        url: "/inkassosag",
        data: formdata,
        method: "post",
        headers: {
          "X-CSRFToken": this.csrftoken,
          "X-AKA-BRUGER": "Unknown"
        }
      })
        .then(res => {
          notify("The server has responded and it was happy!");
          console.log("Server response!");
          console.log(res);
        })
        .catch(err => {
          console.log("there was an error");
          console.log(err.message);
        });
    }
  },
  created: function() {
    this.getCSRFToken();
    notify(`Welcome to this page. ${this.$t("title")}`);
  }
};
</script>

<style scoped>
    input:focus:invalid {
        border: 2px solid #D7404D;
    }
    .submitted:invalid {
        border: 2px solid #D7404D;
    }
    input[disabled] {
        background-color: #d6dbde;
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
