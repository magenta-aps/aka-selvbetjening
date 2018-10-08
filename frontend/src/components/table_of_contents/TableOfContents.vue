<template>


    <nav class="toc">
        <h1>Table of contents</h1>        
        <router-link class="toc-link" to="/form1">Form example 1</router-link>
        <router-link class="toc-link" to="/form2">Form example 2</router-link>
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
