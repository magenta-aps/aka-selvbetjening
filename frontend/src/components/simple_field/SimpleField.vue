<template>
  <div>
    <label :id="'lbl_'+name" :for="name">{{label}}</label>
    <input :id="name" :type="type" v-model="content" :required="required"
    :minlength="minlength" :maxlength="maxlength">
  </div>
</template>

<script>
export default {
  name: 'SimpleField',

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
    required: Boolean,
    minlength: String,
    maxlength: String

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
