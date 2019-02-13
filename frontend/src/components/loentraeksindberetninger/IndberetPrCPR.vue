<template>

  <article>

    <form>

      <h1>{{ $t('loentraek.titel2') }}</h1>

      <div class="container-fluid">
        <div class="row">
          <div class="col">
            <button type="submit"
                    @click="isSubmitted = true">
              {{ $t('common.gem') }}
            </button>
            <button @click.prevent="navigateTo('/loentraeksindberetning/indberet_med_fil')">
              {{ $t('loentraek.indlaes_fra_fil') }}
            </button>
            <button @click.prevent="navigateTo('/loentraeksindberetning')">
              {{ $t('common.tilbage') }}
            </button>
            <button>
              {{ $t('loentraek.indlaes_fra_forrige_redegoerelse') }}
            </button>
          </div>
        </div>

        <div class="row">
          <div class="col">
            <strong>{{ $t('loentraek.loentraek') }}</strong>
            <div class="flex-table flex-table--3cols"
                 id="loentraeksberegninger">
              <div class="flex-tr">
                <div class="flex-table-cell">{{ $t('loentraek.fordeling') }}</div>
                <div class="flex-table-cell">{{ $t('loentraek.fordelt') }}</div>
                <div class="flex-table-cell">{{ $t('loentraek.difference') }}</div>
              </div>
              <div class="flex-tr">
                <div class="flex-table-cell">
                  <input
                    class="input--flex-width"
                    type="text"
                    v-model="fordeling"
                    name="fordeling"
                    v-validate="{currency: true}"
                  >
                </div>
                <div class="flex-table-cell">
                  <input
                    class="input--flex-width"
                    type="text"
                    :value="fordelt"
                    name="fordelt"
                    disabled
                  >
                </div>
                <div class="flex-table-cell">
                  <input
                    class="input--flex-width"
                    type="text"
                    :value="difference"
                    name="difference"
                    disabled
                  >
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- INDBERETNINGSSKEMA -->
        <div class="row">
          <div class="col">
            <div class="flex-table flex-table--5cols" id="indberetningsskema">
              <div class="flex-tr flex-tr--head">
                <div class="flex-table-cell">
                  <strong>{{ $t('common.cpr_nr') }}</strong>
                </div>
                <div class="flex-table-cell">
                  <strong>{{ $t('loentraek.aftalenr') }}</strong>
                </div>
                <div class="flex-table-cell">
                  <strong>{{ $t('loentraek.loentraek') }}</strong>
                </div>
                <div class="flex-table-cell">
                  <strong>{{ $t('loentraek.nettoloen') }}</strong>
                </div>
                <div class="flex-table-cell width-sm">
                </div>
              </div>

              <div class="flex-tr"
                   v-for="(aftale, index) in aftaler"
                   :key="index">

                <div class="flex-table-cell">
                  <input
                    class="input--flex-width"
                    type="text"
                    name = "cpr_nr"
                    v-model="aftale.cpr"
                    v-validate="{digits: 10}"
                  >
                </div>
                <div class="flex-table-cell">
                  <input
                    class="input--flex-width"
                    type="text"
                    name="aftalenr"
                    v-model="aftale.aftalenr"
                  >
                </div>
                <div class="flex-table-cell">
                  <input
                    class="input--flex-width"
                    type="text"
                    name="loentraek"
                    v-model="aftale.loentraek"
                    v-validate="{required: cprIsFilled(index), currency: true}"
                  >
                </div>
                <div class="flex-table-cell">
                  <input
                    class="input--flex-width"
                    type="text"
                    name="nettoloen"
                    v-model="aftale.nettoloen"
                    v-validate="{required: cprIsFilled(index)}"
                  >
                </div>
                <div class="flex-table-cell width-sm y-center">
                  <a class="tag-small"
                     @click="removeRow(index)">
                    x
                  </a>
                </div>
              </div>
              <div class="flex-tr">
                <div class="flex-table-cell">
                  <a class="tag-small" @click="addNewRow">Tilføj</a>
                </div>
                <div class="flex-table-cell"></div>
                <div class="flex-table-cell"></div>
                <div class="flex-table-cell"></div>
                <div class="flex-table-cell"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </form>
  </article>

</template>

<script>
// The file fordringsgruppe.js below is generated by the command `make frontend`
// import { notify } from '../utils/notify/Notifier.js'

export default {
  data: function () {
    return {
      fordeling: '0,00',
      aftaler: [
        {
          cpr: '',
          aftalenr: '',
          loentraek: '',
          nettoloen: ''
        }
      ]
    }
  },
  computed: {
    fordelt: function () {
      let result = 0
      this.aftaler.forEach(function (aftale) {
        let loentraek = this.toOre(aftale.loentraek)
        result = result + loentraek
      }.bind(this))
      return this.oreToString(result)
    },
    difference: function () {
      return this.oreToString(this.toOre(this.fordeling) - this.toOre(this.fordelt))
    }
  },
  methods: {
    toOre: function (str) {
      var m = /^([1-9]\d{1,2}(?:\.\d{3})+|[1-9]\d*|0)(?:,(\d+))?$/.exec(str)
      if (m) {
        let kroner = parseInt(m[1].replace(/\./g, ''))
        let ore = 0
        if (m[2]) {
          if (m[2].length === 1) {
            ore = parseInt(m[2]) * 10
          } else {
            ore = parseInt(m[2])
          }
        }
        return 100 * kroner + ore
      }
      return 0
    },
    oreToString: function (amount) {
      let str = String(amount)
      if (str.length === 1) {
        return ['0,0', str].join('')
      } else if (str.length === 2) {
        return ['0,', str].join('')
      } else {
        return [str.slice(0, str.length - 2), ',', str.slice(str.length - 2)].join('')
      }
    },
    navigateTo: function (nav) {
      this.$router.push({
        path: nav
      })
    },
    addNewRow: function () {
      this.aftaler.push({
        cpr: '',
        aftalenr: '',
        loentraek: '',
        nettoloen: ''
      })
    },
    removeRow: function (index) {
      this.aftaler.splice(index, 1)
    },
    cprIsFilled: function (index) {
      return (this.aftaler[index].cpr !== '')
    },
    getCSRFToken: function () {
      this.csrftoken = document.cookie.replace(
        /(?:(?:^|.*;\s*)csrftoken\s*=\s*([^;]*).*$)|^.*$/,
        '$1'
      )
    }
  },
  created: function () {
    this.getCSRFToken()
  }
}
</script>

<style scoped>
#loentraeksberegninger {
  max-width: 25rem;
}
  .width-sm {
    width: 20px;
  }
  .y-center {
    margin-top: 7px;
  }
</style>
