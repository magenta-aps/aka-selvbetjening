<template>

    <article>

        <h1>Designguide</h1>

        <p><a href="http://sullissivik.designguiden.dk/website">Designguiden kan findes her.</a></p>

        <h2>Formularer</h2>

        <form @submit.prevent="sendFormRequest()">

            <fieldset>
                <label for="inputA">{{ $t('inputa') }}</label>
                <input id="inputA" type="text" name="a" placeholder="test test" v-model="value_a">
                <label for="inputB">{{ $t('inputb') }}</label>
                <input id="inputB" type="text" name="b" v-model="value_b">
            </fieldset>

            <fieldset>
                <input type="submit" :value="$t('send')">
            </fieldset>

        </form>

        <h2>Tiles</h2>

        <div style="display: flex; padding: 2rem; background-color: #eaecee;">
            <div style="margin: 2rem;">

                <h3>Tile type A</h3>

                <a class="tile-a">
                    <img class="tile-a--icon" src="/static/img/SVG/sullisivk_bolig-og-flytning.svg" alt="">
                    Meld flytning
                </a>

            </div>
            <div style="margin: 2rem;">

                <h3>Tile type B</h3>

                <div class="tile-b">
                    <a href="#" class="tile-b--header">
                        <img class="tile-b--icon" src="/static/img/SVG/sullisivk_erhverv.svg" alt="">
                        <span class="tile-b--headertext">Ineqarneq nuunnerlu</span>
                    </a>
                    <nav class="tile-b--categories">
                        <a href="#" class="tile-b--category">Arbejdsmarked</a>
                        <a href="#" class="tile-b--category">Kurser</a>
                        <a href="#" class="tile-b--category">Straffeattest</a>
                        <a href="#" class="tile-b--category">Offentlig ansat</a>
                        <a href="#" class="tile-b--category">Overenskomstgrupper</a>
                    </nav>
                    <a class="tile-b--more">Se alle</a>
                </div>

            </div>
            <div style="margin: 2rem;">

                <h3>Tile type C</h3>

                <a class="tile-c" href="#">
                    <span class="tile-c--header">Hent din bopælsattest</span>
                    <span class="tile-c--byline">
                        En bopælsattest er en attest, du skal bruge til at bevise hvem du er og hvor du bor.
                    </span>
                    <span class="tile-c--more">Læs mere</span>
                </a>

            </div>
        </div>

    </article>

</template>


<script>

    import axios from 'axios'
    import { notify } from '../utils/notify/Notifier.js'

    export default {
        data: function() { 
            return {
                value_a: null,
                value_b: null
            }
        },
        methods: {
            sendFormRequest: function() {
                notify(`A request was sent`)    
            }
            
        },
        created: function() {
            notify(`Welcome to this page.`)
        }
    }

</script>

<style>


</style>

<i18n>

    {
        "da": {
            "title": "Designguide",
            "forms": "Formularer",
            "tiles": "Tiles"
        },
        "kl": {
            "title": "Designguide - oversættelse mangler",
            "forms": "Formularer - oversættelse mangler",
            "tiles": "Tiles - oversættelse mangler"
        }
    }

</i18n>
