<template>

    <div class="locale-changer">
        <select v-model="$i18n.locale">
            <option v-for="(lang, i) in langs" :key="`Lang${i}`" :value="lang.code" :class="`option-${ lang.code }`">
                {{ lang.label }}
            </option>
        </select>
    </div>

</template>

<script>

    export default {
        data () {
            return { 
                langs: [
                    {
                        label: 'Kalaallisut',
                        code: 'kl'
                    },
                    {
                        label: 'Dansk',
                        code: 'da'
                    }
                ] 
            }
        }
    }

</script>

<style>

    .option-da,
    .option-gl {
        background: url('/static/img/SVG/flag_gl.svg') no-repeat left center transparent;
        background-size: 1rem auto;
        padding: 0 0 0 1.5rem;
    }

    .option-da {
        background-image: url('/static/img/SVG/flag_da.svg');
    }

    .option-gl {
        
    }

</style>
