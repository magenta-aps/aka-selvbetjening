<template>

    <article>

        <h1>{{ $t("form2.title") }}</h1>

        <form @submit.prevent="sendFormRequest()">

            <fieldset>
                <label for="inputA">{{ $t("form2.inputa") }}</label>
                <input id="inputA" type="text" name="a" placeholder="test test" v-model="value_a">
                <label for="inputB">{{ $t("form2.inputb") }}</label>
                <input id="inputB" type="text" name="b" v-model="value_b">
            </fieldset>

            <fieldset>
                <input type="file" @change="getFileData($event.target.files)">
            </fieldset>

            <fieldset>
                <input type="submit" :value="$t('form2.send')">
            </fieldset>

        </form>

    </article>

</template>


<script>

    import axios from 'axios'
    import { notify } from '../utils/notify/Notifier.js'

    export default {
        data: function() { 
            return {
                value_a: null,
                value_b: null,
                file: null,
                csrftoken: null
            }
        },
        methods: {
            getCSRFToken: function() {
                this.csrftoken = document.cookie.replace(/(?:(?:^|.*;\s*)csrftoken\s*\=\s*([^;]*).*$)|^.*$/, "$1");
            },
            getFileData: function(files) {
                this.file = files[0]
            },
            sendFormRequest: function() {

                let formdata = new FormData()
                formdata.append('value_a', this.value_a)
                formdata.append('value_b', this.value_b)
                formdata.append('file', this.file)

                axios({
                    url: '/filupload',
                    data: formdata,
                    method: 'post',
                    headers: {
                        'X-CSRFToken': this.csrftoken,
                        'X-AKA-BRUGER': 'Unknown'
                    },
                    onUploadProgress: function (progressEvent) {
                        let percentCompleted = Math.round( (progressEvent.loaded * 100) / progressEvent.total )
                        console.log(percentCompleted)
                    }
                })
                .then(res => {
                    notify('The server has responded and it was happy!')
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
            notify('Welcome to this page')
        }
    }

</script>

<style>


</style>
