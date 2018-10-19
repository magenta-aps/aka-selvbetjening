<template>

    <article class="test">

        <h1>Form example 1</h1>

        <form @submit.prevent="sendFormRequest()">
            <fieldset>
                <label for="inputA">Inputfelt A</label>
                <input id="inputA" type="text" name="a" v-model="value_a">
                <label for="inputB">Inputfelt B</label>
                <input id="inputB" type="text" name="b" v-model="value_b">
            </fieldset>
            <fieldset>
                <input type="submit" value="Send">
            </fieldset>
        </form>

        <h2>Server response:</h2>
        <div>{{ response }}</div>

    </article>

</template>


<script>

    import axios from 'axios'
    
    export default {
        data: function() { 
            return {
                value_a: null,
                value_b: null,
                response: null
            }
        },
        methods: {
            sendFormRequest: function() {
                axios.get('/index')
                    .then(res => {
                        console.log('Server response!')
                        this.response = res
                    })
                    .catch(err => {
                        console.log('there was an error')
                        this.response = err
                    })
            }
        }
    }

</script>

<style>

</style>
