<template>

  <article>

    <form>

      <h1>{{ $t('loentraek.titel2') }}</h1>

      <div class="container-fluid">
        <div class="row">
          <div class="col">
            <button type="submit"
                    @click="isSubmitted = true">
              {{ $t('common.indlaes') }}
            </button>
            <button @click.prevent="navigateTo('/loentraeksindberetning')">
              {{ $t('common.tilbage') }}
            </button>
          </div>
        </div>
        <div class="row">
          <div class="col">
            <input type="file">
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
                    type="number"
                    :value="fordeling"
                    disabled
                  >
                </div>
                <div class="flex-table-cell">
                  <input
                    class="input--flex-width"
                    type="number"
                    :value="fordeling"
                    disabled
                  >
                </div>
                <div class="flex-table-cell">
                  <input
                    class="input--flex-width"
                    type="number"
                    :value="fordeling"
                    disabled
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </form>
  </article>

</template>

<script>
export default {
  data: function () {
    return {
      fil: null,
      fordeling: 0,
      fordelt: 0,
      difference: 0
    }
  },
  methods: {
    navigateTo: function (nav) {
      this.$router.push({
        path: nav
      })
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
    max-width: 400px;
  }
</style>
