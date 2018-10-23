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


            <fieldset>
                <input type="file" @change="getFileData($event.target.files)">
            </fieldset>


            <div style="display: flex; flex-flow: row wrap;">
                <fieldset>
                    <label for="fordringsgruppe">{{ $t("simpel_indberetning.fordringsgruppe") }}</label>
                    <select
                            id="fordringsgruppe"
                            v-model="fordringsgruppe"
                            name="fordringsgruppe"
                            @change="setGroup()"
                    >
                        <option v-for="f in fordringsgrupper" v-bind:value="f">{{stringRep(f)}})</option>
                    </select>
                </fieldset>

                <!--This is only shown if there are multiple options-->
                <fieldset v-if="multipleTypes">
                    <label for="fordringstype">{{ $t("simpel_indberetning.fordringstype") }}</label>
                    <select
                            id="fordringstype"
                            v-model="fordringstype"
                            name="fordringstype"
                            @change="setTypeId()"
                    >
                        <option v-for="t in fordringsgruppe.sub_groups" v-bind:value="t">{{stringRep(t)}}</option>
                    </select>
                </fieldset>
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
                fordringshaver2: null,
                fordringsgrupper: groups,
                fordringsgruppe: null,
                fordringsgruppe_id: null,
                fordringstype: null,
                fordringstype_id: null,
                multipleTypes: false,
                csrftoken: null
            }
        },
        methods: {
            setTypeId: function() {
                this.fordringstype_id = this.fordringstype["id"];
            },
            setGroupId: function() {
                this.fordringsgruppe_id = this.fordringsgruppe["id"];
            },
            setGroup: function() {
                if (this.fordringsgruppe["sub_groups"].length === 1) {
                    this.fordringstype = this.fordringsgruppe["sub_groups"][0];
                    this.setTypeId();
                    this.multipleTypes = false;
                } else {
                    this.multipleTypes = true;
                }
                this.setGroupId();
            },
            stringRep: function(dict) {
                return "" + dict["id"] + " (" + dict["value"] + ")";
            },
            getCSRFToken: function() {
                this.csrftoken = document.cookie.replace(/(?:(?:^|.*;\s*)csrftoken\s*\=\s*([^;]*).*$)|^.*$/, "$1");
            },
            getFileData: function(files) {
                this.file = files[0]
            },
            sendFormRequest: function() {
                let formdata = new FormData()
                formdata.append('fordringshaver', this.fordringshaver)
                formdata.append('debitor', this.debitor)
                formdata.append('fordringshaver2', this.fordringshaver2)
                formdata.append('fordringsgruppe', this.fordringsgruppe_id)
                formdata.append('fordringsgtype', this.fordringstype_id)
                formdata.append('file', this.file)

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
                    console.log('Server response!');
                    console.log(res);
                })
                .catch(err => {
                    console.log('there was an error');
                    console.log(err.message);
                })
            }
        },
        created: function() {
            this.getCSRFToken();
        }
    }
</script>

<style scoped>

</style>
