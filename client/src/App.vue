<script setup>
import { onBeforeMount, ref } from 'vue';
import * as bootstrap from 'bootstrap';
import axios from 'axios';
import Cookies from 'js-cookie';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/userStore';
import { useRouter } from 'vue-router';

const router = useRouter();

const userInfoStore = useUserStore();
const {
  isAuthenticated,
  username
} = storeToRefs(userInfoStore)

async function logout() {
  const r = await axios.post("api/user/logout/")
  userInfoStore.fetchUserInfo()
  router.push("/login")
}

</script>

<template>
  <div class="container">
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Navbar</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown"
          aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse justify-content-between" id="navbarNavDropdown">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Заказы</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/clients">Клиенты</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/bearings">Подшипники</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/ordersCompositions">Составы заказов</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/feedbacks">Отзывы</router-link>
            </li>
          </ul>

          <ul v-if="isAuthenticated" class="navbar-nav">
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown"
                aria-expanded="false">
                {{username}}
              </a>
              <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="/admin/" target="_blank">Админка</a></li>
                <li>
                  <hr class="dropdown-divider">
                </li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="logout">Выйти</a>
                </li>
              </ul>
            </li>
          </ul>

        </div>
      </div>
    </nav>
  </div>
  <div class="container">
    <router-view />
  </div>
</template>

<style scoped></style>