<template>

    <article class="test">

        <h1>Simpel indberetning</h1>

        <form @submit.prevent="sendFormRequest()">

            <fieldset>
                <label for="fordringshaver-input">Fordringshaver</label>
                <input id="fordringshaver-input" type="text" value="NOGH2342" v-model="fordringshaver">
            </fieldset>

            <fieldset>
                <label for="debitor-input">Debitor</label>
                <input id="debitor-input" type="text" v-model="debitor">
            </fieldset>

            <fieldset>
                <label for="anden-fordringshaver-input">Anden fordringshaver</label>
                <input id="anden-fordringshaver-input" type="text" v-model="fordringshaver2">
            </fieldset>

            <fieldset>
                <input type="submit" value="Send">
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
                fordringshaver2: null,
                debitor: null,
            }
        },
        methods: {
            sendFormRequest: function() {

                let formdata = new FormData()
                formdata.append('fordringshaver', this.fordringshaver)
                formdata.append('debitor', this.debitor)
                formdata.append('fordringshaver2', this.fordringshaver2)

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
        }
    }
</script>

<style scoped>

</style>
