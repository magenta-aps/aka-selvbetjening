<template>

    <article>

        <h1>{{ $t("form2.title") }}</h1>

        <form @submit.prevent="sendFormRequest()">

            <fieldset>
                <input type="file" @change="getFileData($event.target.files)">
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
            getFileData: function(files) {
                // Check support for the various File APIs
                if (!this.checkFileAPI) {
                    return false
                }
                // 'files' should be FileList object
                // Loop through the FileList and read the file contents
                for (let f = 0; f < files.length; f++) {
                    this.readFile(files[f])
                }
            },
            checkFileAPI: function() {
                if (window.File && window.FileReader && window.FileList && window.Blob) {
                    // Great success! All the File APIs are supported
                    return true
                } else {
                    alert('The File APIs are not fully supported in this browser.')
                    return false
                }
            },
            readFile: function(file) {
                var reader = new FileReader()
                // Closure to capture the file information.
                reader.onload = ((theFile) => {
                    return (e) => {
                        //call the parse function with the proper line terminator and cell terminator
                        this.parseCSV(e.target.result, '\n', ',')
                    }
                })(file)
                // Read the file as text
                reader.readAsText(file)
            },
            parseCSV: function(text, lineTerminator, cellTerminator) {
                this.csv_data = []
                //break the lines apart
                let rows = text.split(lineTerminator);
                for(let r = 0; r < rows.length; r++){
                    if(r !== ""){
                        //split the rows at the cellTerminator character
                        let cells = rows[r].split(cellTerminator)
                        // Add rows and cells to 'csv_data')
                        this.csv_data.push(cells)
                    }
                }
            },
            sendFormRequest: function() {

                axios({
                    url: '/filupload',
                    data: this.csv_data,
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
