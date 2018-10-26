<template>

    <div class="wrapper">
        <header class="globalheader">
            <div class="globalheader-wrapper">
                <h1 class="globalheader-heading">
                    <router-link  to="/">
                        <img class="globalheader-logo" src="/static/img/sullissivik_logo_gl.svg" alt="Sullissivik">
                    </router-link>
                </h1>
                <language-toggle></language-toggle>
            </div>
        </header>
        <main>
            <router-view></router-view>
        </main>
        <footer>
            <div class="footer-wrapper">
                Footer
            </div>
        </footer>
    </div>

</template>

<script>

    import LangToggle from './components/utils/language-toggle/LangToggle.vue'

    export default {
        components: {
            'language-toggle': LangToggle
        }
    }

</script>

<style>

    .globalheader {
        background-color: #63389b;
        box-shadow: 0 .5rem rgba(0,0,0,.1);
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        width: 100%;
        z-index: 999;
        color: #fff;
        padding: 0.75rem;
    }

    .globalheader-wrapper {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: space-between;
    }

    .globalheader-heading {
        font-weight: normal;
        padding: 0;
        margin: 0;
    }

    .globalheader-logo {
        width: 8rem;
        max-width: 100%;
        height: auto;
    }

    @media screen and (min-width: 35rem) {

        .globalheader-logo {
            width: 10rem;
        }

    }

    @media screen and (min-width: 60rem) {

        .globalheader-wrapper,
        .footer-wrapper {
            max-width: 75rem;
            margin: 0 auto 2.25rem;
        }

        .globalheader-wrapper {
            margin-bottom: 0;
        }

    }

</style>