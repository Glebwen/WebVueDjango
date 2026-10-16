import { ref } from "vue";
import axios from "axios";
import { defineStore } from "pinia";
import Cookies from 'js-cookie';

export const useUserStore = defineStore("UserStore", () => {
    const isAuthenticated = ref(false);   // ← не null, а false
    const isSuperuser = ref(false);
    const username = ref("");
    const isDoubleAuth = ref(false);

    async function fetchUserInfo() {
        try {
            const r = await axios.get("/api/user/me/");
            isAuthenticated.value = r.data.authenticated;
            if (r.data.authenticated) {
                isSuperuser.value = r.data.user.is_superuser;
                username.value = r.data.user.username;
            } else {
                isSuperuser.value = false;
                username.value = "";
            }
            axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
        } catch (e) {
            console.error("fetchUserInfo error:", e);
            isAuthenticated.value = false;
        }
    }

    return {
        isAuthenticated, isSuperuser, username, isDoubleAuth,
        fetchUserInfo
    };
});