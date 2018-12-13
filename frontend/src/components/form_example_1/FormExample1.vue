<template>

    <article class="test">

        <h1>Form example 1</h1>

        <form @submit.prevent="sendFormRequest()">
            <fieldset>
                <label for="inputA">Inputfelt A er required</label>
                <input v-validate="'required'" id="inputA" type="text" name="a" v-model="value_a">
                <span>{{ errors.first('a')}}</span>

                <label for="beloeb">Pengebeløb: skal kun acceptere komma</label>
                <!--<input v-validate="{ regex: /^([0-9]{8}|[0-9]{10})$/ }" id="inputB" type="text" name="b" v-model="value_b">-->
                <input v-validate="'currency'" id="beloeb" type="text" name="beloeb" v-model="value_b">
                <span>{{ errors.first('beloeb')}}</span>

                <label for="debitor">Debitor</label>
                <input v-validate=" 'eight_or_ten_characters' " id="debitor" type="text" name="debitor">
                <span>{{ errors.first('debitor')}}</span>
            </fieldset>
            <fieldset>
                <input type="submit" value="Send">
            </fieldset>
        </form>

      {{formValid}}

        <h2>Server response:</h2>
        <div>{{ response }}</div>

    </article>

</template>

<script>
import axios from 'axios'

export default {
  data: function () {
    return {
      value_a: null,
      value_b: null,
      response: null
    }
  },
  computed: {
    /**
     * Loop over all contents of the fields object and check if they exist and valid.
     */
    formValid () {
      return Object.keys(this.fields).every(field => {
        return this.fields[field] && this.fields[field].valid
      })
    }
  },
  methods: {
    sendFormRequest: function () {
      if (this.formValid) {
        axios.get('/index')
          .then(res => {
            console.log('Server response!')
            this.response = res
          })
          .catch(err => {
            console.log('there was an error')
            this.response = err
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}

</script>

<style>

</style>
