<template>
    <div>
    <select v-model="month"
        v-bind:value="value"
        v-on:input="$emit('input', month)"
    >
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
    <select v-model="year">
        <option v-for="y in years" :key=y>
            {{ y }}
        </option>


    </select>
    </div>
</template> 
<script>
export default {
    data: function () {
        return {
            years: [2019, 2018, 2017, 2016],
            year: 0,
            month: 0
        }
    },
    computed: {
        value: function () {
            return this.year + " - " + this.month
            }
    }
}
</script>