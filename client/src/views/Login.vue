<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/userStore';
import router from '@/router';


const userInfoStore = useUserStore();
const {
  isAuthenticated
} = storeToRefs(userInfoStore)


const username = ref('');
const password = ref('');

async function login() {
  const r = await axios.post("api/user/login/", {
    username: username.value,
    password: password.value,
  })

  username.value = '';
  password.value = '';

  await userInfoStore.fetchUserInfo()
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken")

  if (isAuthenticated.value){
    router.push("/")
  }
}

</script>

<template>

    <div>
        <div style="width: 30%" class="border p-5 mx-auto mt-5">
            <div class="mb-4 text-center">
                <h2>Login</h2>
            </div>

            <div class="form-outline mb-3">
                <input type="text" class="form-control" placeholder="Username" v-model="username" />
            </div>

            <div class="form-outline mb-4">
                <input type="password" class="form-control" placeholder="Password" v-model="password" />
            </div>

            <div class="d-flex justify-content-center">
                <button type="submit" class="btn btn-primary mb-3" @click="login()">Sign in</button>
            </div>
            <div class="text-center">
            <p>Not a member? <a href="/register">Register</a></p>
        </div>
        </div>
    </div>

</template>

<style></style>