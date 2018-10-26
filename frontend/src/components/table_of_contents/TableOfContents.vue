<template>

    <nav class="toc">  
        <router-link class="toc-link" to="/designguide">
            Design guide
        </router-link>
        <hr>
        <router-link class="toc-link" to="/form1">
            <span>Form example 1</span>
        </router-link>
        <router-link class="toc-link" to="/form2">
            <span>Form example 2</span>
        </router-link>
        <router-link class="toc-link" to="/upload">
            <span>Upload files with JSON example</span>
        </router-link>
        <router-link class="toc-link" to="/indberetning">
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

</style>
