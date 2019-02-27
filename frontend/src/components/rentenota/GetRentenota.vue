<template>

    <article>

        <h1 class="rentenota-title">{{ $t("rentenota.title") }} </h1>

        <div class="rentenota-main">

            <div class="rentenota-actions">
                <p>Selected month: {{ month }}</p>
                <month-selector v-model="month"></month-selector>

                <form @submit.prevent="requestRentenota()" class="rentenota-dateform">
                    <!--fieldset>
                        <label for="date-to">{{ $t("rentenota.month") }}</label>
                        <input type="month" id="month" v-model="month" required :max="dateto">
                    </fieldset-->
                    <fieldset>
                        <input type="submit" :value="$t('common.send')">
                    </fieldset>
                </form>

            </div>

            <div v-if="rentenota_data" class="rentenota-data">

                <div class="rentenota-data-title">
                    <h2>Namminersorlutik Oqartussat - Grønlands Selvstyre</h2>
                    <div>
                        <button class="rentenota-btn-print" @click="print()">{{ $t("common.print") }}</button>
                    </div>
                </div>

                <p>
                    <strong>Akileraartarnermut Aqutsisoqarfik</strong><br>
                    <strong>Skattestyrelsen</strong>
                </p>

                <div class="notaheader">

                    <p>
                        <em>{{ rentenota_data.firmanavn }}</em><br>
                        {{ rentenota_data.adresse.gade }}<br>
                        {{ rentenota_data.adresse.postnr }} {{ rentenota_data.adresse.by }}<br>
                        {{ rentenota_data.adresse.land }}
                    </p>

                    <div>

                        <h3>Rentenota</h3>

                        <table class="rentenota-address-table">
                            <tr>
                                <th>{{ $t("rentenota.konto") }}</th>
                                <td>10276179</td>
                            </tr>
                            <tr>
                                <th>{{ $t("rentenota.dato") }}</th>
                                <td>{{ today.toLocaleDateString() }}</td>
                            </tr>
                        </table>

                        <address>

                            <p>
                                Postboks 1605<br>
                                3900 Nuuk
                            </p>

                            <table class="rentenota-address-table">
                                <tr>
                                    <th>{{ $t("rentenota.telefon") }}</th>
                                    <td>346500</td>
                                </tr>
                                <tr>
                                    <th>{{ $t("rentenota.fax") }}</th>
                                    <td>346577</td>
                                </tr>
                                <tr>
                                    <th>{{ $t("rentenota.email") }}</th>
                                    <td>sulinal@nanoq.gl</td>
                                </tr>
                                <tr>
                                    <th>{{ $t("rentenota.webadresse") }}</th>
                                    <td>www.aka.gl</td>
                                </tr>
                            </table>

                        </address>

                    </div>

                </div>

                <table>
                    <thead>
                        <tr>
                            <th>{{ $t("rentenota.dato") }}</th>
                            <th>{{ $t("rentenota.postdato") }}</th>
                            <th>{{ $t("rentenota.bilag") }}</th>
                            <th>{{ $t("rentenota.faktura") }}</th>
                            <th>{{ $t("rentenota.tekst") }}</th>
                            <th>{{ $t("rentenota.fradato") }}</th>
                            <th>{{ $t("rentenota.dage") }}</th>
                            <th>{{ $t("rentenota.grundlag") }}</th>
                            <th>{{ $t("rentenota.val") }}</th>
                            <th>{{ $t("rentenota.grundlag") }}</th>
                            <th>{{ $t("rentenota.beloeb") }}</th>
                            <th style="border: none;"></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="p in rentenota_data.poster" :key="p.dato">
                            <td>
                                {{ p.dato }}
                            </td>
                            <td>
                                {{ p.postdato }}
                            </td>
                            <td>
                                {{ p.bilag }}
                            </td>
                            <td>
                                {{ p.faktura }}
                            </td>
                            <td>
                                {{ p.tekst }}
                            </td>
                            <td>
                                {{ p.fradato }}
                            </td>
                            <td class="numbercell">
                                {{ p.dage }}
                            </td>
                            <td class="numbercell">
                                {{ p.grundlag }}
                            </td>
                            <td class="numbercell">
                                {{ p.val }}
                            </td>
                            <td class="numbercell">
                                {{ p.grundlag2 }}
                            </td>
                            <td class="numbercell">
                                {{ p.beloeb }}
                            </td>
                            <td></td>
                        </tr>
                        <tr>
                            <td colspan="10"></td>
                            <td class="numbercell rentenota-total">
                                {{ total }}
                            </td>
                            <td>
                                kr
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

        </div>

    </article>

</template>


<script>
import axios from "axios";
import Month from '@/components/utils/month-selector/Month.vue'

export default {
  components: {
      'month-selector': Month
  },
  data() {
    return {
      csrftoken: null,
      rentenota_data: null,
      today: new Date(),
      dateto: null,
      datefrom: null,
      month: 0
    };
  },
  computed: {
    total() {
      if (this.rentenota_data) {
        let count_total = 0;
        for (let p of this.rentenota_data.poster) {
          count_total += p.beloeb;
        }
        return count_total;
      }
    }
  },
  methods: {
    getCSRFToken() {
      this.csrftoken = document.cookie.replace(
        /(?:(?:^|.*;\s*)csrftoken\s*\=\s*([^;]*).*$)|^.*$/,
        "$1"
      );
    },
    requestRentenota() {
      axios({
        url: `/rentenota/from${ this.datefrom }to${ this.dateto }`,
        method: "get",
        headers: {
          "X-CSRFToken": this.csrftoken,
          "X-AKA-BRUGER": "Unknown"
        }
      })
        .then(res => {
          this.rentenota_data = res.data;
        })
        .catch(err => {
          alert(err.message);
        });
    },
    print: function() {
      window.print();
    },
    setDates: function() {
      let d = new Date();
      this.dateto = d.toISOString().substr(0, 10);
      d.setMonth(d.getMonth() - 1);
      this.datefrom = d.toISOString().substr(0, 10);
    }
  },
  created() {
    this.getCSRFToken();
    this.setDates();
  }
};
</script>

<style>
.rentenota-data {
  padding: 1rem;
  border: solid 1px #eaecee;
  margin: 1rem 0;
}

.rentenota-main .numbercell {
  text-align: right;
}

.rentenota-dateform {
  margin: 0;
  display: flex;
  flex-flow: row wrap;
  align-items: flex-end;
}

.rentenota-data-title {
  display: flex;
  justify-content: space-between;
}

.rentenota-btn-print {
  float: right;
}

.rentenota-total {
  border-top: solid 1px #465c6c;
  border-bottom: solid 0.25rem #465c6c;
}

.rentenota-main .notaheader {
  display: flex;
  justify-content: space-between;
  margin: 1rem 0 2rem;
}

.rentenota-address-table {
  width: 100%;
}

.rentenota-address-table th,
.rentenota-address-table td {
  padding: 0;
}

.rentenota-address-table th {
  border: none;
  font-weight: normal;
}

.rentenota-address-table td {
  text-align: right;
}

@media print {
  .rentenota-title,
  .rentenota-actions,
  .rentenota-btn-print {
    display: none;
  }

  .rentenota-data {
    padding: 0;
    border: none;
    margin: 0;
  }
}
</style>
