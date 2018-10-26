<template>

    <article>

        <h1>Designguide</h1>

        <p>Designguiden fra 1508 <a href="http://sullissivik.designguiden.dk/website">kan findes her.</a></p>

        <h2>Typografi</h2>

        <div class="grid">

            <div class="grid--2-3 color--background--light">
                <div style="padding: .75rem;">
                    <h1>Heading 1 - Bold 24pt/30pt</h1>
                    <h2>Heading 2</h2>
                    <h3>Heading 3</h3>
                    <h4>Heading 4</h4>
                    <p>Body/regular 16pt/24pt</p>
                    <ul>
                        <li>Bullet - regular 16pt/24pt</li>
                        <li>Bullet - regular 16pt/24pt</li>
                        <li>Bullet - regular 16pt/24pt</li>
                    </ul>
                    <ol>
                        <li>Number - regular 16pt/24pt</li>
                        <li>Number - regular 16pt/24pt</li>
                        <li>Number - regular 16pt/24pt</li>
                    </ol>
                    <h1><a href="">Large link - header</a></h1>
                    <a class="h1" href="">Large link - not header</a>
                    <a href="">Small link</a>
                </div>
            </div>    

            <div class="color--header">
                <div style="padding: .75rem;">
                    <h1>Heading 1 - Bold 24pt/30pt</h1>
                    <h2>Heading 2</h2>
                    <h3>Heading 3</h3>
                    <h4>Heading 4</h4>
                    <p>Body/regular 16pt/24pt</p>
                    <ul>
                        <li>Bullet - regular 16pt/24pt</li>
                        <li>Bullet - regular 16pt/24pt</li>
                        <li>Bullet - regular 16pt/24pt</li>
                    </ul>
                    <ol>
                        <li>Number - regular 16pt/24pt</li>
                        <li>Number - regular 16pt/24pt</li>
                        <li>Number - regular 16pt/24pt</li>
                    </ol>
                    <h1><a href="">Large link - header</a></h1>
                    <a class="h1" href="">Large link - not header</a>
                    <a href="">Small link</a>
                </div>
            </div>

        </div>

        <h2>Grid</h2>

        <div class="wrap-this-grid">

            <div class="grid"> 
                <div class="grid--3-3">
                    .grid--3-3 - Grid cell that spans the whole width
                </div>
                <div>
                    No class - Grid cell that spans 1/3 of width
                </div>
                <div class="grid--2-3">
                    .grid--2-3 - Grid cell that spans 2/3 of width
                </div>
                <div>

                    <div class="grid"> 
                        <div class="grid--3-3">
                            Grid within a grid
                        </div>
                        <div class="grid--2-3"></div>
                        <div></div>
                        <div></div>
                        <div></div>
                        <div></div>
                    </div>

                </div>
                <div></div>
                <div></div>
            </div>

        </div>

        <h2>Formularer</h2>

        <form @submit.prevent="sendFormRequest()">

            <h3>Inputfelter</h3>
            <fieldset>
                <label for="inputA">Inputfelt</label>
                <input id="inputA" type="text" placeholder="Tips til at udfylde">
                <label for="inputA">Inputfelt</label>
                <input id="inputA" type="text" value="Præudfyldt værdi">
                <label for="inputB">Dato-inputfelt</label>
                <input id="inputB" type="date">
            </fieldset>

            <h3>Knapper</h3>
            <fieldset>
                <input type="submit" value="Primær handling: Send/Gem">
                <button>Sekundær action: Annullér/Reset</button>
            </fieldset>

        </form>

        <h2>Tags</h2>

        <h3>Store tags</h3>
        <p>
            <a class="tag-large" href="#">Hover</a>
            <a class="tag-large" href="#">Bopælsattest</a>
            <a class="tag-large" href="#">NEMID</a>
            <a class="tag-large" href="#">Skattekort</a>
            <a class="tag-large" href="#">Pas</a>
            <a class="tag-large" href="#">Boligsikring</a>
            <a class="tag-large" href="#">Selvangivelse</a>
        </p>

        <h3>Små tags</h3>
        <p>
            <a class="tag-small" href="#">Arbejdsmarked</a>
            <a class="tag-small" href="#">Kurser</a>
            <a class="tag-small" href="#">Straffeattest</a>
            <a class="tag-small" href="#">Offentlig ansat</a>
            <a class="tag-small" href="#">Overenskomstgrupper</a>
        </p>

        <h2>Tiles</h2>

        <div class="grid">
            <div>

                <h3>Tile type A</h3>

                <a class="tile-a">
                    <img class="tile-a--icon" src="/static/img/SVG/sullisivk_bolig-og-flytning.svg" alt="">
                    Meld flytning
                </a>

            </div>
            <div>

                <h3>Tile type B</h3>

                <div class="tile-b">
                    <a href="#" class="tile-b--header">
                        <img class="tile-b--icon" src="/static/img/SVG/sullisivik_skatter-afgifter-og-gaeld_dark.svg" alt="">
                        <span class="tile-b--headertext">Ineqarneq nuunnerlu</span>
                    </a>
                    <nav class="tile-b--categories">
                        <a href="#" class="tag-small">Arbejdsmarked</a>
                        <a href="#" class="tag-small">Kurser</a>
                        <a href="#" class="tag-small">Straffeattest</a>
                        <a href="#" class="tag-small">Offentlig ansat</a>
                        <a href="#" class="tag-small">Overenskomstgrupper</a>
                    </nav>
                    <a class="tile-b--more">Se alle</a>
                </div>

            </div>
            <div>

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

        <h2>Dropdown handle</h2>

        <button class="dropdown">
            <span>Dropdown static</span>
            <img class="icon" src="/static/img/SVG/sullisivk_arrow.svg" alt="">
        </button>    

        <h2>Ikoner</h2>
        <p>
            <img class="icon" src="/static/img/SVG/sullisivk_arrow.svg" alt="">
        </p>
        <p>
            <img class="icon" src="/static/img/SVG/sullisivk_close.svg" alt="">
        </p>
        <p>
            <img class="icon" src="/static/img/SVG/sullisivk_search-small.svg" alt="">
        </p>
        <p>
            <img class="icon" src="/static/img/SVG/sullisivk_Search-large.svg" alt="">
        </p>
        <p>
            <img class="icon" src="/static/img/SVG/sullisivk_login.svg" alt="">
        </p>

        <h2>Farver</h2>

        <div class="colorswatches">

            <div class="color--header">
                .color--header
            </div>
            <div class="color--header--dark">
                .color--header--dark
            </div>
            <div class="color--header--light">
                .color--header--light
            </div>
            <div class="color--text">
                .color--text
            </div>
            <div class="color--link">
                .color--link
            </div>
            <div class="color--link--hover">
                .color--link--hover
            </div>
            <div class="color--background">
                .color--background
            </div>
            <div class="color--background--light">
                .color--background--light
            </div>
            <div class="color--background--dark">
                .color--background--dark
            </div>
            <div class="color--cta">
                .color--cta
            </div>
            <div class="color--cta--light">
                .color--cta--light
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
            notify('')
        }
    }

</script>

<style>

    .colorswatches {
        display: flex;
        flex-flow: row wrap;
    }

    .colorswatches > div {
        flex: 1 0 13rem;
        height: 5rem;
        padding: 1rem;
    }

    .wrap-this-grid .grid > div {
        background-color: #31495b;
        padding: 1rem;
        color: #fff;
    }

    .wrap-this-grid .grid .grid > div {
        background-color: #83929D;
        min-height: 3rem;
    }

</style>

<i18n>

    {
        "da": {
            "title": "Designguide"
        },
        "kl": {
            "title": "Designguide - oversættelse mangler"
        }
    }

</i18n>
