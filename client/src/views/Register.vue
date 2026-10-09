<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref, watch } from 'vue';
import router from '@/router';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/userStore';


const userInfoStore = useUserStore();
const {
    isAuthenticated
} = storeToRefs(userInfoStore)


const username = ref('');
const password = ref('');
const email = ref('');
const phone = ref('');

async function register() {
    const r = await axios.post("/api/user/register/", {
        username: username.value,
        password: password.value,
        email: email.value,
        phone: phone.value,
    })

    username.value = '';
    password.value = '';
    email.value = '';
    phone.value = '';

    await userInfoStore.fetchUserInfo()
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken")

    if (isAuthenticated.value) {
        router.push("/")
    }
}


</script>

<template>

    <div>
        <div style="width: 30%" class="border p-5 mx-auto mt-5">
            <div class="mb-4 text-center">
                <h2>Register</h2>
            </div>

            <div class="form-outline mb-3">
                <input type="text" class="form-control" placeholder="Username" v-model="username" />
            </div>

            <div class="form-outline mb-3">
                <input type="text" class="form-control" placeholder="Email" v-model="email" />
            </div>

            <div class="form-outline mb-3">
                <input type="tel" class="form-control" v-model="phone" required 
                placeholder="+7 (999) 999-99-99" />
            </div>

            <div class="form-outline mb-4">
                <input type="password" class="form-control" placeholder="Password" v-model="password" />
            </div>

            <div class="d-flex justify-content-center">
                <button type="submit" class="btn btn-primary mb-3" @click="register()">Register</button>
            </div>
            <div class="text-center">
                <p>Have account? <a href="/login">Login</a></p>
            </div>
        </div>
    </div>
</template>

<style></style>