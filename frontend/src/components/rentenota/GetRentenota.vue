<template>

    <article>

        <h1 class="rentenota-title">{{ $t("rentenota.title") }} </h1>

        <div class="rentenota-main">

            <div class="rentenota-actions row">
                <div class="col-4">
                    <select class="dropdown" v-model="month">
                        <option value="1" >{{ $t('common.january')      }}</option>
                        <option value="2" >{{ $t('common.february')     }}</option>
                        <option value="3" >{{ $t('common.march')        }}</option>
                        <option value="4" >{{ $t('common.april')        }}</option>
                        <option value="5" >{{ $t('common.may')          }}</option>
                        <option value="6" >{{ $t('common.june')         }}</option>
                        <option value="7" >{{ $t('common.july')         }}</option>
                        <option value="8" >{{ $t('common.august')       }}</option>
                        <option value="9" >{{ $t('common.september')    }}</option>
                        <option value="10">{{ $t('common.october')      }}</option>
                        <option value="11">{{ $t('common.november')     }}</option>
                        <option value="12">{{ $t('common.december')     }}</option>
                    </select>
                </div>
                <div class="col-4">
                    <select class="dropdown" v-model="year">
                        <option v-for="y in years" :key=y>
                            {{ y }}
                        </option>
                    </select>
                </div>
                <div class="col-4">
                    <button type="submit" @click="requestRentenota">{{ $t('common.send') }}</button>
                </div>
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
                            <th>{{ $t("rentenota.debitorkonto") }}</th>
                            <th>{{ $t("rentenota.faktureringsklassifikation") }}</th>
                            <th>{{ $t("rentenota.bilag") }}</th>
                            <th>{{ $t("rentenota.rentenotanummer") }}</th>
                            <th>{{ $t("rentenota.tekst") }}</th>
                            <th>{{ $t("rentenota.val") }}</th>
                            <th>{{ $t("rentenota.grundlag") }}</th>
                            <th>{{ $t("rentenota.beloeb") }}</th>
                            <th>{{ $t("rentenota.postdato") }}</th>
                            <th>{{ $t("rentenota.faktura") }}</th>
                            <th>{{ $t("rentenota.fradato") }}</th>
                            <th>{{ $t("rentenota.tildato") }}</th>
                            <th>{{ $t("rentenota.dage") }}</th>
                            <th style="border: none;"></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-if="!rentenota_data.poster.length">
                          <td colspan="14" style="text-align: center">
                            Ingen poster
                          </td>
                        </tr>
                        <tr v-for="p in rentenota_data.poster" :key="p.Updated">
                            <td>
                                {{ p.Updated }}
                            </td>
                            <td>
                                {{ p.AccountNum }}
                            </td>
                            <td>
                                {{ p.BillingClassification }}
                            </td>
                            <td>
                                {{ p.Voucher }}
                            </td>
                            <td>
                                {{ p.InterestNote }}
                            </td>
                            <td>
                                {{ p.Txt }}
                            </td>
                            <td class="numbercell">
                                {{ p.DueDate }}
                            </td>
                            <td class="numbercell">
                                {{ p.InvoiceAmount }}
                            </td>
                            <td class="numbercell">
                                {{ p.InterestAmount }}
                            </td>
                            <td>
                                {{ p.TransDate }}
                            </td>
                            <td>
                                {{ p.Invoice }}
                            </td>
                            <td>
                                {{ p.CalcFrom }}
                            </td>
                            <td>
                                {{ p.CalcTo }}
                            </td>
                            <td class="numbercell">
                                {{ p.InterestDays }}
                            </td>
                            <td></td>
                        </tr>
                        <tr>
                            <td colspan="8"></td>
                            <td class="numbercell rentenota-total">
                                {{ total }}
                            </td>
                            <td colspan="6">
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

export default {
  data() {
    return {
      csrftoken: null,
      rentenota_data: null,
      today: new Date(),
      years: [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20].map(
        function (a) {
            return new Date().getFullYear() - a
        }
      ),
      month: new Date().getMonth(), //JS months are zero indexed. We can only pick prior months
      year: new Date().getFullYear()
    };
  },
  computed: {
    total() {
      if (this.rentenota_data) {
        let count_total = 0;
        for (let p of this.rentenota_data.poster) {
          count_total += p.InterestAmount;
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
        url: `/rentenota/${ this.year }/${ this.zeroPadMonth(this.month) }`,
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
    },
    zeroPadMonth: function(x) {
      return x >= 10 ? String(x) : '0'+String(x)
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
