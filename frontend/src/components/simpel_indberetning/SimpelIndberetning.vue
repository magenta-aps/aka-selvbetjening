<template>

    <article class="test">

        <h1>Simpel indberetning</h1>

        <form @submit.prevent="sendFormRequest()">

            <fieldset>
                <label for="fordringshaver-input">{{ $t("simpel_indberetning.fordringshaver") }}</label>
                <input id="fordringshaver-input" type="text" value="NOGH2342" v-model="fordringshaver">
            </fieldset>

            <fieldset>
                <label for="debitor-input">{{ $t("simpel_indberetning.debitor") }}</label>
                <input id="debitor-input" type="text" v-model="debitor">
            </fieldset>

            <fieldset>
                <label for="anden-fordringshaver-input">{{ $t("simpel_indberetning.anden_fordringshaver") }}</label>
                <input id="anden-fordringshaver-input" type="text" v-model="fordringshaver2">
            </fieldset>

            <div style="display: flex; flex-flow: row wrap;">
                <fieldset>
                    <label for="fordringsgruppe">Ekstern fordringsgruppe</label>
                    <select
                            id="fordringsgruppe"
                            v-model="fordringsgruppe"
                            name="fordringsgruppe"
                    >
                        <option v-for="f in Object.keys(fordringsgrupper)">{{ f }}</option>
                    </select>
                </fieldset>

                <!-- This is only shown if there are multiple options-->
                <fieldset v-if="fordringsgruppe !== null &&
                                fordringsgrupper[fordringsgruppe].length > 1">
                    <label for="fordringstype">Ekstern fordringstype</label>
                    <select
                            id="fordringstype"
                            v-model="fordringstype"
                            name="fordringstype"
                    >
                        <option v-for="t in fordringsgrupper[fordringsgruppe]">{{ t }}</option>
                    </select>
                </fieldset>
            </div>

            <!--TODO: Set fordringstype if the above fieldset is not rendered-->




            <fieldset>
                <input type="submit" v-bind:value="$t('simpel_indberetning.gem')">
            </fieldset>

        </form>

    </article>

</template>

<script>

    import axios from 'axios'

    export default {
        data: function() {
            return {
                fordringshaver: null,
                debitor: null,
                fordringshaver2: null,

                fordringsgrupper: {
                    "Fordringsgruppe 1": ["Type 1 for fordringsgruppe 1", "Type 2 for fordringsgruppe 1"],
                    "Fordringsgruppe 2": ["Fordringsgruppe 2"]
                },
                fordringsgruppe: null,
                fordringstype: null,
            }
        },
        methods: {
            sendFormRequest: function() {

                let formdata = new FormData()
                formdata.append('fordringshaver', this.fordringshaver)
                formdata.append('debitor', this.debitor)
                formdata.append('fordringshaver2', this.fordringshaver2)

                axios({
                    url: '/whatever', /* TODO: Make rest interface and set url */
                    data: formdata,
                    method: 'post',
                    headers: {
                        'X-CSRFToken': this.csrftoken,
                        'X-AKA-BRUGER': 'Unknown'
                    }
                })
                .then(res => {
                    console.log('Server response!')
                    console.log(res)
                })
                .catch(err => {
                    console.log('there was an error')
                    console.log(err.message)
                })
            }
        }
    }
</script>

<style scoped>

</style>