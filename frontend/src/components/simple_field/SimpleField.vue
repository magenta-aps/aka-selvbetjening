<template>
  <div>
    <label :id="'lbl_'+name" :for="name">{{label}}</label>
    <input :id="name"
           :name="name"
           :type="type"
           v-model="content"
           v-validate="validate"
    :minlength="minlength" :maxlength="maxlength">
    <span class="err-msg">{{ errors.first(name)}}</span>
  </div>
</template>

<script>
export default {
  name: 'SimpleField',

  inject: {
    $validator: '$validator'
  },

  props: {
    name: {
      type: String,
      required: true
    },
    type: {
      type: String,
      default: 'text'
    },
    label: String,
    minlength: String,
    maxlength: String,
    validate: Object
  },
  data () {
    return {
      content: ''
    }
  },
  watch: {
    content (val) {
      this.$emit('input', val)
    }
  }
}
</script>
<style>
  .err-msg {
    color: red;
  }
</style>
