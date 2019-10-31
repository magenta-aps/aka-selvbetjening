<template>

    <article>

        <h1>{{ $t("form2.title") }}</h1>

        <form @submit.prevent="sendFormRequest()">

            <fieldset>
              <input type="file" name="file" @change="setFileData($event.target.files)">
            </fieldset>

            <fieldset>
                <input type="submit" :value="$t('form2.send')">
            </fieldset>

        </form>

        <hr>

        <table v-if="csv_data">
            <tr v-for="row in csv_data">
                <td v-for="cell in row">{{ cell }}</td>
            </tr>
        </table>

    </article>

</template>


<script>

    import axios from 'axios'

    export default {
        data: function() {
            return {
                csv_data: null,
                csrftoken: null
            }
        },
        methods: {
            getCSRFToken: function() {
                this.csrftoken = document.cookie.replace(/(?:(?:^|.*;\s*)csrftoken\s*\=\s*([^;]*).*$)|^.*$/, "$1");
            },
            setFileData: function(files) {
                this.files = files;
            },
            sendFormRequest: function() {
                let data = new FormData();
                data.append("file", this.files[0]);
                axios({
                    url: '/inkassosag/upload',
                    data: data,
                    method: 'post',
                    headers: {
                        'X-CSRFToken': this.csrftoken,
                        'X-AKA-BRUGER': 'Unknown'
                    },
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

<style>


</style>
