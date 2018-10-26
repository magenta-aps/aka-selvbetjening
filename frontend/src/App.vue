<template>

    <div class="wrapper">
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
        <footer>
            Footer
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
        color: #fff;
        padding: 0.75rem;
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: space-between;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        width: 100%;
        z-index: 999;
        box-shadow: 0 .5rem rgba(0,0,0,.1);
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

</style>