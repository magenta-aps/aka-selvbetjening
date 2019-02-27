<template>
    <div>
    <select
        v-bind:value="value"
        v-on:inpu="$emit('input', $event.target.value)"
    >
        <option value="1" >{{ date.january      }}</option>
        <option value="2" >{{ date.february     }}</option>
        <option value="3" >{{ date.march        }}</option>
        <option value="4" >{{ date.april        }}</option>
        <option value="5" >{{ date.may          }}</option>
        <option value="6" >{{ date.june         }}</option>
        <option value="7" >{{ date.july         }}</option>
        <option value="8" >{{ date.august       }}</option>
        <option value="9" >{{ date.september    }}</option>
        <option value="10">{{ date.october      }}</option>
        <option value="11">{{ date.november     }}</option>
        <option value="12">{{ date.december     }}</option>
    </select>
    </div>
</template> 
<script>
export default {
    props:['value'],
    data: function () {
      return {
        value: month
      } 
    },
    computed: {
        value: function () {
            return this.month
        }
    }
}
</script>