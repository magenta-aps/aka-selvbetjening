<!--
This component is a copy of SimpleField, but modified to format Currency fields
-->
<template>
  <div>
	<label :id="'lbl_'+name" :for="name">{{label}}</label>
	<input :id="name"
		   :name="name"
		   :type="type"
		   v-model="displayValue"
		   @blur="isInputActive = false"
		   @focus="isInputActive = true"
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
  methods: {
	formatCurrency: function (value) {
	  // This should only format, validation happens afterwards
	  
	  if(value.split(',').length === 2 && value.split(',')[1].length > 2){
		const integers = value.split(',')[0]
		const decimals = value.split(',')[1]
		const firstTwo = decimals.substr(0,2)
		const roundingDecimal = parseInt(decimals.charAt(2),10)
		if(isNaN(roundingDecimal)){
		  return value
		}
		
		if(roundingDecimal >= 5){
		  return integers.concat(",").concat(parseInt(firstTwo,10) + 1)
		} else {
		  return integers.concat(",").concat(firstTwo)
		}
	  } else {
		return value
	  }
  },
  computed: {
	  displayValue: {
		get: function() {
			if(this.isInputActive){
				return this.content
			} else {
				return this.formatCurrency(this.content)
			}
		},
		set: function(newValue) {
			this.content = newValue
		}
	  }
  },
  data () {
	return {
	  content: '',
	  isInputActive: false
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
