<template>

    <article class="test">

        <h1>Form example 1</h1>

        <form @submit.prevent="sendFormRequest()">
            <fieldset>
                <label for="inputA">Inputfelt A er required</label>
                <input v-validate="'required'" id="inputA" type="text" name="a" v-model="value_a">
                <span>{{ errors.first('a')}}</span>

                <label for="inputB">Inputfelt B skal være 8 eller 10 tal</label>
                <input v-validate="{ regex: /^([0-9]{8}|[0-9]{10})$/ }" id="inputB" type="text" name="b" v-model="value_b">
              <span>{{ errors.first('b')}}</span>
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
