import { onBeforeMount, ref } from "vue";
import axios from "axios";
import { defineStore } from "pinia";
import Cookies from 'js-cookie';

export const useUserStore = defineStore("UserStore", () => {
    const isAuthenticated = ref(null)
    const isSuperuser = ref(false)
    const username = ref("")
    const isDoubleAuth = ref(false)


    async function fetchUserInfo() {
        const r = await axios.get("/api/user/info/");
        isAuthenticated.value = r.data.is_authenticated
        isSuperuser.value = r.data.is_superuser
        username.value = r.data.name
        isDoubleAuth.value = r.data.is_double

        axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken")
    }

    onBeforeMount(async () => {
        fetchUserInfo();
    });

    return {
        isAuthenticated, isSuperuser, username, isDoubleAuth,
        fetchUserInfo
    }
})