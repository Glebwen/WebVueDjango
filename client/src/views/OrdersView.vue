<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/userStore';
import ModalOTP from '@/components/ModalOTP.vue';

const userStore = useUserStore();
const { isSuperuser, isDoubleAuth } = storeToRefs(userStore);

const orderToAdd = ref({
  number: '',
  client_id: null
});

const orderToEdit = ref({
  id: null,
  number: '',
  client_id: null
});

const orders = ref([]);
const clients = ref([]);
const selectedUserId = ref('all');
const loading = ref(false);
const error = ref(null);
const showEditModal = ref(false);


const uniqueUsers = computed(() => {
  if (!isSuperuser.value) return [];

  const usersDict = {};

  clients.value.forEach(client => {
    if (client.user && client.user.id) {
      const userId = client.user.id;
      if (!usersDict[userId]) {
        usersDict[userId] = {
          id: userId,
          username: client.user.username,
          email: client.user.email || ''
        };
      }
    }
  });

  return Object.values(usersDict).sort((a, b) =>
    a.username.localeCompare(b.username)
  );
});

const filteredOrders = computed(() => {
  if (!isSuperuser.value || selectedUserId.value === 'all') {
    return orders.value;
  }

  return orders.value.filter(order =>
    order.client &&
    order.client.user &&
    order.client.user.id === parseInt(selectedUserId.value)
  );
});

async function fetchClients() {
  try {
    const response = await axios.get("/api/clients/");
    clients.value = response.data;
  } catch (err) {
    console.error("Ошибка при загрузке клиентов:", err);
    error.value = "Не удалось загрузить список клиентов";
  }
}

async function fetchOrders() {
  try {
    loading.value = true;
    error.value = null;
    const response = await axios.get("/api/orders/");
    orders.value = response.data;
  } catch (err) {
    console.error("Ошибка при загрузке заказов:", err);
    error.value = "Не удалось загрузить список заказов";
    orders.value = [];
  } finally {
    loading.value = false;
  }
}
async function onActivateTOTP() {
  await userStore.fetchUserInfo()
}

async function onOrderAdd() {
  try {
    if (!orderToAdd.value.number || !orderToAdd.value.client_id) {
      error.value = "Пожалуйста, заполните все поля";
      return;
    }

    await axios.post("/api/orders/", orderToAdd.value);

    orderToAdd.value = { number: '', client_id: null };
    error.value = null;

    await fetchOrders();
  } catch (err) {
    console.error("Ошибка при добавлении заказа:", err);
    error.value = "Не удалось добавить заказ";
  }
}

async function onRemoveClick(order) {
  if (!confirm(`Вы уверены, что хотите удалить заказ №${order.number}?`)) {
    return;
  }

  try {
    await axios.delete(`/api/orders/${order.id}/`);
    await fetchOrders();
  } catch (err) {
    console.error("Ошибка при удалении заказа:", err);
    error.value = "Не удалось удалить заказ";
  }
}

function onOrderEditClick(order) {
  orderToEdit.value = {
    ...order,
    client_id: order.client?.id || order.client_id
  };
  showEditModal.value = true;
}

async function onUpdateOrder() {
  try {
    if (!orderToEdit.value.number || !orderToEdit.value.client_id) {
      error.value = "Пожалуйста, заполните все поля";
      return;
    }

    await axios.put(
      `/api/orders/${orderToEdit.value.id}/`,
      orderToEdit.value
    );

    error.value = null;
    await fetchOrders();

    showEditModal.value = false;
  } catch (err) {
    if (err.response.status == 403){
      await userStore.fetchUserInfo()
    }
    else{
      console.error("Ошибка при обновлении заказа:", err);
      error.value = "Не удалось обновить заказ";
    }

  }
}

function closeEditModal() {
  showEditModal.value = false;
}

onBeforeMount(async () => {
  await fetchClients();
  await fetchOrders();
});
</script>

<template>
  <div class="container py-4">
    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = null" aria-label="Закрыть"></button>
    </div>

    <div v-if="isSuperuser && orders.length > 0" class="card shadow-sm mb-4">
      <div class="card-header bg-secondary text-white">
        <h5 class="card-title mb-0">
          <i class="bi bi-funnel me-2"></i>
          Фильтр по пользователю
        </h5>
      </div>
      <div class="card-body">
        <div class="row align-items-center">
          <div class="col-md-4">
            <label class="form-label">Пользователь:</label>
            <select class="form-select" v-model="selectedUserId">
              <option value="all">Все пользователи</option>
              <option v-for="user in uniqueUsers" :key="user.id" :value="user.id">
                {{ user.username }}
                <template v-if="user.email">({{ user.email }})</template>
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header bg-primary text-white">
        <h5 class="card-title mb-0">
          <i class="bi bi-cart-plus me-2"></i>
          Добавить новый заказ
        </h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="onOrderAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-3">
              <div class="form-floating">
                <input type="number" class="form-control" id="numberInput" v-model="orderToAdd.number" required
                  placeholder="Номер заказа" min="1" />
                <label for="numberInput">Номер заказа *</label>
              </div>
            </div>
            <div class="col-md-7">
              <div class="form-floating">
                <select class="form-select" id="clientInput" v-model="orderToAdd.client_id" required
                  :disabled="clients.length === 0">
                  <option value="" disabled>Выберите клиента</option>
                  <option :value="c.id" v-for="c in clients" :key="c.id">
                    {{ c.name }} ({{ c.phone }})
                  </option>
                </select>
                <label for="clientInput">Клиент *</label>
              </div>
            </div>
            <div class="col-md-2">
              <button type="submit" class="btn btn-primary w-100"
                :disabled="loading || !orderToAdd.number || !orderToAdd.client_id || clients.length === 0">
                Добавить
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-header bg-light">
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="card-title mb-0">
            <i class="bi bi-cart-check me-2"></i>
            Список заказов
          </h5>
        </div>
      </div>

      <div v-if="loading && orders.length === 0" class="card-body text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-3 text-muted">Загружаем список заказов...</p>
      </div>

      <div v-else-if="filteredOrders.length > 0" class="list-group list-group-flush">
        <div v-for="item in filteredOrders" :key="item.id" class="list-group-item list-group-item-action">
          <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              <div>
                <h6 class="mb-1">Заказ №{{ item.number }}</h6>
                <p class="text-muted mb-0 small">
                  <i class="bi bi-person me-1"></i>
                  {{ item.client?.name || 'Неизвестный клиент' }}
                  <span v-if="item.client?.phone" class="ms-2">
                    <i class="bi bi-telephone me-1"></i>
                    {{ item.client.phone }}
                  </span>
                  <span v-if="isSuperuser && item.client?.user" class="ms-2">
                    <i class="bi bi-person-badge me-1"></i>
                    Пользователь: {{ item.client.user.username }}
                  </span>
                </p>
              </div>
            </div>
            <div class="btn-group">
              <button class="btn btn-outline-primary btn-sm" @click="onOrderEditClick(item)" :disabled="loading"
                title="Редактировать">
                Изменить
              </button>
              <button class="btn btn-outline-danger btn-sm" @click="onRemoveClick(item)" :disabled="loading"
                title="Удалить">
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="card-body text-center py-5">
        <div class="text-muted mb-3">
          <i class="bi bi-cart display-1"></i>
        </div>
        <h5 class="text-muted">Список заказов пуст</h5>
        <p class="text-muted" v-if="isSuperuser && selectedUserId !== 'all'">
          У выбранного пользователя нет заказов
        </p>
        <p class="text-muted" v-else>
          Добавьте первый заказ с помощью формы выше
        </p>
      </div>
    </div>

    <div v-if="showEditModal" >
      <div v-if="isDoubleAuth" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="bi bi-pencil-square me-2"></i>
                Редактировать заказ
              </h5>
              <button type="button" class="btn-close" @click="closeEditModal" aria-label="Закрыть"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="onUpdateOrder" id="editForm">
                <div class="row g-3">
                  <div class="col-12">
                    <div class="form-floating">
                      <input type="number" class="form-control" id="editNumber" v-model="orderToEdit.number"
                        placeholder="Номер заказа" required min="1" :class="{ 'is-invalid': !orderToEdit.number }" />
                      <label for="editNumber">Номер заказа *</label>
                      <div class="invalid-feedback">
                        Пожалуйста, введите номер заказа
                      </div>
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="form-floating">
                      <select class="form-select" id="editClient" v-model="orderToEdit.client_id" required
                        :class="{ 'is-invalid': !orderToEdit.client_id }">
                        <option value="" disabled>Выберите клиента</option>
                        <option :value="c.id" v-for="c in clients" :key="c.id">
                          {{ c.name }} ({{ c.phone }})
                        </option>
                      </select>
                      <label for="editClient">Клиент *</label>
                      <div class="invalid-feedback">
                        Пожалуйста, выберите клиента
                      </div>
                    </div>
                  </div>
                </div>
              </form>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeEditModal" :disabled="loading">
                Отмена
              </button>
              <button type="submit" form="editForm" class="btn btn-primary"
                :disabled="loading || !orderToEdit.number || !orderToEdit.client_id">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                Сохранить изменения
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else>
        <ModalOTP :on-activate="onActivateTOTP" :on-close="closeEditModal"/>
      </div>

    </div>

  </div>
</template>

<style scoped>
.list-group-item:hover {
  background-color: #f8f9fa;
}

.card-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.form-control:focus,
.form-select:focus {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

.btn-outline-primary:hover,
.btn-outline-danger:hover {
  transform: translateY(-1px);
  transition: transform 0.2s;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 1rem;
}

.modal-dialog {
  max-width: 500px;
  width: 100%;
}

.modal-content {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  animation: modalFadeIn 0.3s ease-out;
}

.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-50px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>