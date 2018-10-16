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
                    <label for="fordringsgruppe">{{ $t("simpel_indberetning.fordringsgruppe") }}</label>
                    <select
                            id="fordringsgruppe"
                            v-model="fordringsgruppe"
                            name="fordringsgruppe"
                    >
                        <!--TODO: Flyt logik til metode-->
                        <option v-for="f in fordringsgrupper" v-bind:value="f">{{f["id"]}} ({{ f["value"] }})</option>
                    </select>
                </fieldset>

                <!--This is only shown if there are multiple options-->
                <fieldset v-if="fordringsgruppe !== null && fordringsgruppe.sub_groups.length > 1">
                    <label for="fordringstype">{{ $t("simpel_indberetning.fordringstype") }}</label>
                    <select
                            id="fordringstype"
                            v-model="fordringstype"
                            name="fordringstype"
                    >
                        <option v-for="t in fordringsgruppe.sub_groups" >{{t["id"]}} ({{ t["value"] }})</option>
                    </select>
                </fieldset>
                <!--TODO: Set fordringstype if the above fieldset is not rendered-->
            </div>

            <fieldset>
                <input type="submit" v-bind:value="$t('simpel_indberetning.gem')">
            </fieldset>

        </form>

    </article>

</template>

<script>

    import axios from 'axios'
    import {groups} from '../../../assets/fordringsgruppe'

    export default {
        data: function() {
            return {
                fordringshaver: null,
                debitor: null,
                fordringsgrupper: groups,
                fordringsgruppe: null,
                fordringstype: null,
                fordringshaver2: null,
                csrftoken: null
                // testValue: null,
                // subTest: null,
                // dummyfordringsgruppe: {
                //     "Fordringsgruppe 1": ["Type 1 for fordringsgruppe 1", "Type 2 for fordringsgruppe 1"],
                //     "Fordringsgruppe 2": ["Fordringsgruppe 2"]
                // },
            }
        },
        // computed: {
        //     hideSelector() {
        //         return this.dummyfordringsgruppe.length > 0
        //     }
        // },
        // mounted () {
        //     api.getSuperGroups().then(response => {
        //         this.testValue = response
        //
        //         console.log(this.testValue)
        //
        //         this.getSubGroup(response[0])
        //     })
        // },
        methods: {
            getCSRFToken: function() {
                this.csrftoken = document.cookie.replace(/(?:(?:^|.*;\s*)csrftoken\s*\=\s*([^;]*).*$)|^.*$/, "$1");
            },
            sendFormRequest: function() {

                let formdata = {
                    fordringshaver: this.fordringshaver,
                    debitor: this.debitor,
                    fordringshaver2: this.fordringshaver2,
                    fordringsgruppe: this.fordringsgruppe,
                    fordringstype: this.fordringstype
                }

                axios({
                    url: '/inkassosag',
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
        },
        created: function() {
            this.getCSRFToken()
        }
    }
</script>

<style scoped>

</style>
