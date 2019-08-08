<template>

    <div class="locale-changer">
      <span :class="`option-${ selectedLanguage }`"></span>
        <select class="dropdown" v-model="selectedLanguage">
            <option v-for="(lang, i) in langs" :key="i" :value="lang.code">
                {{ lang.label }}
            </option>
        </select>
    </div>

</template>

<script>
export default {
  data () {
    return {
      langs: [
        {
          label: 'Kalaallisut',
          code: 'kl'
        },
        {
          label: 'Dansk',
          code: 'da'
        }
      ],
      selectedLanguage: localStorage.getItem('language')
    }
  },
  watch: {
    selectedLanguage (val) {
      localStorage.setItem('language', val)
      this.$i18n.locale = val
    }
  }
}
</script>

<style scoped>
.option-da,
.option-kl {
  background: url("../../../assets/img/SVG/flag_gl.svg") no-repeat left center transparent;
  background-size: 1rem auto;
  padding: 0 0 0 1.5rem;
}

.option-da {
  background-image: url("../../../assets/img/SVG/flag_da.svg");
}
</style>
