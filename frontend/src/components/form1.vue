<template>

    <article class="test">

        <h1>Halluuuuu</h1>

        <form @submit.prevent="sendFormRequest()">
            <fieldset>
                <label for="inputA"></label>
                <input id="inputA" type="text" name="a" v-model="value_a">
            </fieldset>
            <fieldset>
                <label for="inputB"></label>
                <input id="inputB" type="text" name="b" v-model="value_b">
            </fieldset>
            <fieldset>
                <input type="submit" value="Send">
            </fieldset>
        </form>

    </article>

</template>


<script>

    import axios from 'axios'
    
    export default {
        data: function() { 
            return {
                value_a: null,
                value_b: null
            }
        },
        methods: {
            sendFormRequest: function() {
                axios.post({
                    data: [
                        this.value_a,
                        this.value_b
                    ]
                })
            }
        }
    }

</script>


<style>

    .test h1 {
        
    }

</style>
