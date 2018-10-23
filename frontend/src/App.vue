<template>

    <div>
        <header class="globalheader">
            <h1 class="globalheader-heading">
                <router-link  to="/">
                    <img class="globalheader-logo" src="/static/img/sullissivik_logo_gl.svg" alt="Sullissivik">
                </router-link>
            </h1>
            <language-toggle></language-toggle>
        </header>
        <main>
            <router-view></router-view>
        </main>
    </div>

</template>

<script>

    import LangToggle from './components/language-toggle/LangToggle.vue'

    export default {
        components: {
            'language-toggle': LangToggle
        }
    }

</script>

<style>

    .globalheader {
        background-color: #63389b;
        color: #fff;
        padding: 1rem 2rem;
    }

    .globalheader-heading {
        font-weight: normal;
        padding: 0;
        margin: 0;
    }

    .globalheader-logo {
        width: 10rem;
        max-width: 100%;
        height: auto;
    }

    @media print {

        .globalheader {
            display: none;
        }
            
    }

</style>