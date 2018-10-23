<template>

    <article class="test">

        <h1>Inkasso - Opret sag</h1>

        <form @submit.prevent="sendFormRequest()">

            <fieldset>
                <label id="lbl_fordringshaver" for="fordringshaver">{{ $t("simpel_indberetning.fordringshaver") }}</label>
                <input id="fordringshaver" type="text" value="NOGH2342" v-model="fordringshaver">

                <label id="lbl_debitor" for="debitor">{{ $t("simpel_indberetning.debitor") }}</label>
                <input id="debitor" type="text" v-model="debitor">

                <label id="lbl_fordringshaver2" for="fordringshaver2">{{ $t("simpel_indberetning.anden_fordringshaver") }}</label>
                <input id="fordringshaver2" type="text" value="NOGH2342" v-model="fordringshaver2">
            </fieldset>


            <!--TODO: Allow multiple files and show file list-->
            <fieldset>
                <input type="file" @change="getFileData($event.target.files)">
            </fieldset>


            <div style="display: flex; flex-flow: row wrap;">
                <fieldset>
                    <label id="lbl_fordringsgruppe" for="fordringsgruppe">{{ $t("simpel_indberetning.fordringsgruppe") }}</label>
                    <select
                            id="fordringsgruppe"
                            v-model="fordringsgruppe"
                            @change="setGroup()"
                    >
                        <option v-for="f in fordringsgrupper" v-bind:value="f">{{stringRep(f)}})</option>
                    </select>
                </fieldset>

                <!--This is only shown if there are multiple options-->
                <fieldset v-if="multipleTypes">
                    <label id="lbl_fordringstype" for="fordringstype">{{ $t("simpel_indberetning.fordringstype") }}</label>
                    <select
                            id="fordringstype"
                            v-model="fordringstype"
                            @change="setTypeId()"
                    >
                        <option v-for="t in fordringsgruppe.sub_groups" v-bind:value="t">{{stringRep(t)}}</option>
                    </select>
                </fieldset>
            </div>


            <fieldset>
                <label id="lbl_barns_cpr" for="tb_barns_cpr">Barns CPR-nr</label>
                <input id="tb_barns_cpr" type="text" v-model="barns_cpr">

                <label id="lbl_ekstern_sagsnummer" for="tb_ekstern_sagsnummer">Ekstern sagsnummer</label>
                <input id="tb_ekstern_sagsnummer" type="text" v-model="ekstern_sagsnummer">

                <label id="lbl_fakturanr" for="tb_fakturanr">Fakturanr</label>
                <input id="tb_fakturanr" type="text" v-model="fakturanr">

                <label id="lbl_bnr" for="tb_bnr">B-nr</label>
                <input id="tb_bnr" type="text" v-model="bnr">
            </fieldset>

            <fieldset> <!--TODO: Fix wrapping -->
                <label id="lbl_hovedstol" for="tb_hovedstol">Hovedstol</label>
                <input id="tb_hovedstol" type="text" v-model="hovedstol">
                <label id="lbl_hovedstol_posteringstekst" for="tb_hovedstol_posteringstekst">Posteringstekst</label>
                <input id="tb_hovedstol_posteringstekst" type="text" v-model="hovedstol_posteringstekst">

                <label id="lbl_bankrente" for="tb_bankrente">Bankrente</label>
                <input id="tb_bankrente" type="text" v-model="bankrente">
                <label id="lbl_bankrente_posteringstekst" for="tb_bankrente_posteringstekst">Posteringstekst</label>
                <input id="tb_bankrente_posteringstekst" type="text" v-model="bankrente_posteringstekst">

                <label id="lbl_bankgebyr" for="tb_bankgebyr">Bankgebyr</label>
                <input id="tb_bankgebyr" type="text" v-model="bankgebyr">
                <label id="lbl_bankgebyr_posteringstekst" for="tb_bankgebyr_posteringstekst">Posteringstekst</label>
                <input id="tb_bankgebyr_posteringstekst" type="text" v-model="bankgebyr_posteringstekst">

                <label id="lbl_rente" for="tb_rente">Rente</label>
                <input id="tb_rente" type="text" v-model="rente">
                <label id="lbl_rente_posteringstekst" for="tb_rente_posteringstekst">Posteringstekst</label>
                <input id="tb_rente_posteringstekst" type="text" v-model="rente_posteringstekst">
            </fieldset>

            <fieldset> <!--TODO: Fix wrapping -->
                <label id="lbl_periodestart" for="tb_periodestart">Periodestart</label>
                <input id="tb_periodestart" type="date" v-model="periodestart">

                <label id="lbl_periodeslut" for="tb_periodeslut">Periodeslut</label>
                <input id="tb_periodeslut" type="date" v-model="periodeslut">

                <label id="lbl_forfaldsdato" for="tb_forfaldsdato">Forfaldsdato</label>
                <input id="tb_forfaldsdato" type="date" v-model="forfaldsdato">

                <label id="lbl_betalingsdato" for="tb_betalingsdato">Betalinsgdato</label>
                <input id="tb_betalingsdato" type="date" v-model="betalingsdato">

                <label id="lbl_foraeldelsesdato" for="tb_foraeldelsesdato">Forældelsesdato</label>
                <input id="tb_foraeldelsesdato" type="date" v-model="foraeldelsesdato">
            </fieldset>

            <fieldset>
                <label id="lbl_kontaktperson" for="tb_kontaktperson">Kontaktperson</label>
                <input id="tb_kontaktperson" type="text" v-model="kontaktperson">

                <label id="lbl_noter" for="tb_nrtes">Noter</label>
                <input id="tb_nrtes" type="text" v-model="noter">
            </fieldset>

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
                fordringsgruppe: null,
                fordringstype: null,
                fil: null,  /*TODO: make this a list of files*/
                barns_cpr: null,
                ekstern_sagsnummer: null,
                fakturanr: null,
                bnr: null,
                hovedstol: null,
                hovedstol_posteringstekst: null,
                bankrente: null,
                bankrente_posteringstekst: null,
                bankgebyr: null,
                bankgebyr_posteringstekst: null,
                rente: null,
                rente_posteringstekst: null,
                periodestart: null,
                periodeslut: null,
                forfaldsdato: null,
                betalingsdato: null,
                foraeldelsesdato: null,
                kontaktperson: null,
                noter: null,

                /*TODO: Maybe computed properties?*/
                fordringsgrupper: groups,
                fordringstype_id: null,
                fordringsgruppe_id: null,
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
                this.fil = files[0]
            },
            sendFormRequest: function() {
                let formdata = new FormData();
                formdata.append('fordringshaver', this.fordringshaver);
                formdata.append('debitor', this.debitor);
                formdata.append('fordringshaver2', this.fordringshaver2);
                formdata.append('fordringsgruppe', this.fordringsgruppe_id);
                formdata.append('fordringsgtype', this.fordringstype_id);
                formdata.append('file', this.file);
                formdata.append('barns_cpr', this.barns_cpr);
                formdata.append('ekstern_sagsnummer', this.ekstern_sagsnummer);
                formdata.append('fakturanr', this.fakturanr);
                formdata.append('bnr', this.bnr);
                formdata.append('hovedstol', this.hovedstol);
                formdata.append('hovedstol_posteringstekst', this.hovedstol_posteringstekst);
                formdata.append('bankrente', this.bankrente);
                formdata.append('bankrente_posteringstekst', this.bankrente_posteringstekst);
                formdata.append('bankgebyr', this.bankgebyr);
                formdata.append('bankgebyr_posteringstekst', this.bankgebyr_posteringstekst);
                formdata.append('rente', this.rente);
                formdata.append('rente_posteringstekst', this.rente_posteringstekst);
                formdata.append('periodestart', this.periodestart);
                formdata.append('periodeslut', this.periodeslut);
                formdata.append('forfaldsdato', this.forfaldsdato);
                formdata.append('betalingsdato', this.betalingsdato);
                formdata.append('foraeldelsesdato', this.foraeldelsesdato);
                formdata.append('kontaktperson', this.kontaktperson);
                formdata.append('noter', this.noter);

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
