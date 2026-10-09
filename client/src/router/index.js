import { createRouter, createWebHistory } from 'vue-router'

import OrdersView from '../views/OrdersView.vue';
import FeedbacksView from '../views/FeedbacksView.vue';
import ClientsView from '../views/ClientsView.vue';
import BearingsView from '../views/BearingsView.vue';
import OrdersCompositionsView from '../views/OrdersCompositionsView.vue';
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';
import { useUserStore } from '@/stores/userStore';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "OrdersView",
      component: OrdersView
    },
    {
      path: "/clients",
      name: "ClientsView",
      component: ClientsView
    },
    {
      path: "/bearings",
      name: "BearingsView",
      component: BearingsView
    },
    {
      path: "/ordersCompositions",
      name: "OrdersCompositionsView",
      component: OrdersCompositionsView
    },
    {
      path: "/feedbacks",
      name: "FeedbacksView",
      component: FeedbacksView
    },
    {
      path: "/login",
      name: "Login",
      component: Login
    },
        {
      path: "/register",
      name: "Register",
      component: Register
    },
  ],
})

router.beforeEach((to, from)=>{
  const userInfoStore = useUserStore();
  if (userInfoStore.isAuthenticated == false && to.name != 'Login'){
    return {name: 'Login'}
  }
})

export default router