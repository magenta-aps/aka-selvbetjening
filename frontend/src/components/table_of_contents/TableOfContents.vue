<template>

    <nav class="toc">  
        <router-link class="toc-link tile" to="/form1">
            <img class="tile-icon" src="/static/img/SVG/sullisivik_skatter-afgifter-og-gaeld.svg" alt="">
            <span>Form example 1</span>
        </router-link>
        <router-link class="toc-link tile" to="/form2">
            <img class="tile-icon" src="/static/img/SVG/sullisivik_skatter-afgifter-og-gaeld.svg" alt="">
            <span>Form example 2</span>
        </router-link>
        <router-link class="toc-link tile" to="/upload">
            <img class="tile-icon" src="/static/img/SVG/sullisivik_skatter-afgifter-og-gaeld.svg" alt="">
            <span>Upload files with JSON example</span>
        </router-link>
        <router-link class="toc-link tile" to="/indberetning">
            <img class="tile-icon" src="/static/img/SVG/sullisivik_skatter-afgifter-og-gaeld.svg" alt="">
            <span>Opret sag</span>
        </router-link>
    </nav>

</template>

<style>

    .toc {
        padding: 1rem 2rem;
    }

    .toc-link {
        display: block;
    }

    /* Tiles */

    .tile,
    .tile:link,
    .tile:visited {
        text-decoration: none;
        background-color: #31495b;
        color: #fff;
        padding: 2.5rem;
        display: flex;
        flex-flow: column nowrap;
        align-items: center;
        justify-content: center;
        margin: 0 0 1rem;
    }

    .tile:hover,
    .tile:active {
        background-color: #83929D;
    }

    .tile-icon {
        width: 2rem;
        height: auto;
        margin: 0 0 .5rem;
    }

</style>
