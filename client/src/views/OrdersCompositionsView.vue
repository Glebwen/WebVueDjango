<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/userStore';
import ModalOTP from '@/components/ModalOTP.vue';

const userStore = useUserStore();
const { isSuperuser, isDoubleAuth } = storeToRefs(userStore);

const elementToAdd = ref({
  order_id: null,
  bearing_id: null,
  ammount: 0
});

const elementToEdit = ref({
  id: null,
  order_id: null,
  bearing_id: null,
  ammount: 0
});

const clients = ref([]);
const orders = ref([]);
const bearings = ref([]);
const selectedUserId = ref('all');
const loading = ref(false);
const statsLoading = ref(false);
const error = ref(null);
const showEditModal = ref(false);

const filteredElements = ref([]);
const showFilters = ref(false);

const filters = ref({
  order_number: '',
  bearing_name: '',
  ammount_min: '',
  ammount_max: '',
  client_name: ''
});

async function applyFilters() {
  try {
    loading.value = true;
    const response = await axios.post('/api/ordersCompositions/filter/', filters.value);
    filteredElements.value = response.data;
  } catch (error) {
    console.error('Ошибка при фильтрации:', error);
  } finally {
    loading.value = false;
  }
}

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

const stats = ref({
  total_quantity: 0,
  avg_per_order: 0,
  max_quantity: 0,
  min_quantity: 0
});


function resetFilters() {
  filters.value = {
    order_number: '',
    bearing_name: '',
    ammount_min: '',
    ammount_max: '',
    client_name: ''
  };
  selectedUserId.value = 'all';
  applyFilters();
}

async function fetchStats() {
  try {
    statsLoading.value = true;
    const response = await axios.get("/api/ordersCompositions/stats/");
    stats.value = response.data;
  } catch (err) {
    console.error("Ошибка при загрузке статистики:", err);
    error.value = "Не удалось загрузить статистику";
  } finally {
    statsLoading.value = false;
  }
}

async function fetchOrders() {
  try {
    const response = await axios.get("/api/orders/");
    orders.value = response.data;
  } catch (err) {
    console.error("Ошибка при загрузке заказов:", err);
    error.value = "Не удалось загрузить список заказов";
  }
}

async function fetchBearings() {
  try {
    const response = await axios.get("/api/bearings/");
    bearings.value = response.data;
  } catch (err) {
    console.error("Ошибка при загрузке подшипников:", err);
    error.value = "Не удалось загрузить список подшипников";
  }
}
async function fetchClients() {
  try {
    const response = await axios.get("/api/clients/");
    clients.value = response.data;
  } catch (err) {
    console.error("Ошибка при загрузке клиентов:", err);
    error.value = "Не удалось загрузить список клиентов";
  }
}

async function onActivateTOTP() {
  await userStore.fetchUserInfo()
}

async function onElementAdd() {
  try {
    if (!elementToAdd.value.order_id || !elementToAdd.value.bearing_id || !elementToAdd.value.ammount) {
      error.value = "Пожалуйста, заполните все поля";
      return;
    }

    await axios.post("/api/ordersCompositions/", elementToAdd.value);

    elementToAdd.value = { order_id: null, bearing_id: null, ammount: 0 };
    error.value = null;

    await applyFilters();
    await fetchStats();
  } catch (err) {
    console.error("Ошибка при добавлении состава заказа:", err);
    error.value = "Не удалось добавить состав заказа";
  }
}

async function onRemoveClick(element) {
  if (!confirm(`Вы уверены, что хотите удалить этот состав заказа?`)) {
    return;
  }

  try {
    await axios.delete(`/api/ordersCompositions/${element.id}/`);
    await applyFilters();
    await fetchStats();
  } catch (err) {
    console.error("Ошибка при удалении состава заказа:", err);
    error.value = "Не удалось удалить состав заказа";
  }
}

function onElementEditClick(element) {
  elementToEdit.value = {
    ...element,
    order_id: element.order?.id || element.order_id,
    bearing_id: element.bearing?.id || element.bearing_id
  };
  showEditModal.value = true;
}

async function onUpdateElement() {
  try {
    if (!elementToEdit.value.order_id || !elementToEdit.value.bearing_id || !elementToEdit.value.ammount) {
      error.value = "Пожалуйста, заполните все поля";
      return;
    }

    await axios.put(
      `/api/ordersCompositions/${elementToEdit.value.id}/`,
      elementToEdit.value
    );

    error.value = null;
    await applyFilters();
    await fetchStats();

    showEditModal.value = false;
  } catch (err) {
    if (err.response.status == 403) {
      await userStore.fetchUserInfo()
    }
    else {
      console.error("Ошибка при обновлении состава заказа:", err);
      error.value = "Не удалось обновить состав заказа";
    }
  }
}

function closeEditModal() {
  showEditModal.value = false;
}

function formatNumber(num) {
  return new Intl.NumberFormat('ru-RU').format(num);
}

onBeforeMount(async () => {
  await Promise.all([
    fetchOrders(),
    fetchBearings(),
    fetchStats(),
    fetchClients()
  ]);
  await resetFilters();
  await applyFilters();
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
      <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0">
          <i class="bi bi-bar-chart-line me-2"></i>
          Статистика составов заказов
        </h5>
      </div>
      <div class="card-body">
        <div v-if="statsLoading" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-info" role="status">
            <span class="visually-hidden">Загрузка...</span>
          </div>
          <span class="ms-2">Загрузка статистики...</span>
        </div>
        <div v-else class="row g-3">
          <div class="col-md-3 col-6">
            <div class="stats-card bg-light rounded p-3 text-center">
              <div class="stats-icon text-primary mb-2">
                <i class="bi bi-box-seam fs-4"></i>
              </div>
              <h6 class="stats-value fw-bold">{{ formatNumber(stats.total_quantity) }}</h6>
              <p class="stats-label text-muted mb-0 small">Всего подшипников в заказах</p>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="stats-card bg-light rounded p-3 text-center">
              <div class="stats-icon text-success mb-2">
                <i class="bi bi-graph-up fs-4"></i>
              </div>
              <h6 class="stats-value fw-bold">{{ formatNumber(stats.avg_per_order) }}</h6>
              <p class="stats-label text-muted mb-0 small">Среднее на заказ</p>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="stats-card bg-light rounded p-3 text-center">
              <div class="stats-icon text-danger mb-2">
                <i class="bi bi-arrow-up-circle fs-4"></i>
              </div>
              <h6 class="stats-value fw-bold">{{ formatNumber(stats.max_quantity) }}</h6>
              <p class="stats-label text-muted mb-0 small">Макс. количество</p>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="stats-card bg-light rounded p-3 text-center">
              <div class="stats-icon text-info mb-2">
                <i class="bi bi-arrow-down-circle fs-4"></i>
              </div>
              <h6 class="stats-value fw-bold">{{ formatNumber(stats.min_quantity) }}</h6>
              <p class="stats-label text-muted mb-0 small">Мин. количество</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header bg-primary text-white">
        <h5 class="card-title mb-0">
          <i class="bi bi-plus-circle me-2"></i>
          Добавить новый состав заказа
        </h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="onElementAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <div class="form-floating">
                <select class="form-select" id="orderInput" v-model="elementToAdd.order_id" required
                  :disabled="orders.length === 0">
                  <option value="" disabled>Выберите заказ</option>
                  <option :value="o.id" v-for="o in orders" :key="o.id">
                    Заказ №{{ o.number }} ({{ o.client?.name || 'Клиент не указан' }})
                  </option>
                </select>
                <label for="orderInput">Заказ *</label>
              </div>
            </div>
            <div class="col-md-4">
              <div class="form-floating">
                <select class="form-select" id="bearingInput" v-model="elementToAdd.bearing_id" required
                  :disabled="bearings.length === 0">
                  <option value="" disabled>Выберите подшипник</option>
                  <option :value="b.id" v-for="b in bearings" :key="b.id">
                    {{ b.name }} (вн.д: {{ b.inner_d }}, нар.д: {{ b.outer_d }}, высота: {{ b.height }})
                  </option>
                </select>
                <label for="bearingInput">Подшипник *</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="amountInput" v-model="elementToAdd.ammount" required
                  placeholder="Количество" min="1" step="1" />
                <label for="amountInput">Количество *</label>
              </div>
            </div>
            <div class="col-md">
              <button type="submit" class="btn btn-primary w-100"
                :disabled="loading || !elementToAdd.order_id || !elementToAdd.bearing_id || !elementToAdd.ammount || orders.length === 0 || bearings.length === 0">
                Добавить
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0">
          <i class="bi bi-funnel me-2"></i>
          Фильтры составов заказов
        </h5>
        <button class="btn btn-light btn-sm" @click="showFilters = !showFilters">
          <i class="bi" :class="showFilters ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
        </button>
      </div>

      <div v-if="showFilters" class="card-body">
        <form @submit.prevent="applyFilters">
          <div class="row g-3">
            <div class="col-md-3">
              <div class="form-floating">
                <input type="text" class="form-control" id="filterOrderNumber" v-model="filters.order_number"
                  placeholder="Номер заказа" />
                <label for="filterOrderNumber">
                  <i class="bi bi-search me-1"></i> Номер заказа
                </label>
              </div>
            </div>

            <div class="col-md-3">
              <div class="form-floating">
                <input type="text" class="form-control" id="filterBearingName" v-model="filters.bearing_name"
                  placeholder="Название подшипника" />
                <label for="filterBearingName">
                  <i class="bi bi-gear me-1"></i> Название подшипника
                </label>
              </div>
            </div>

            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterAmountMin" v-model="filters.ammount_min"
                  placeholder="От" min="1" step="1" />
                <label for="filterAmountMin">Кол-во от</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterAmountMax" v-model="filters.ammount_max"
                  placeholder="До" min="1" step="1" />
                <label for="filterAmountMax">Кол-во до</label>
              </div>
            </div>

            <div class="col-md-3">
              <div class="form-floating">
                <input type="text" class="form-control" id="filterClientName" v-model="filters.client_name"
                  placeholder="Имя клиента" />
                <label for="filterClientName">
                  <i class="bi bi-person me-1"></i> Имя клиента
                </label>
              </div>
            </div>

            <div class="col-md-4 d-flex gap-2 align-items-end">
              <button type="button" class="btn btn-primary flex-grow-1" @click="applyFilters">
                <i class="bi bi-funnel me-1"></i> Применить фильтры
              </button>
              <button type="button" class="btn btn-outline-secondary" @click="resetFilters">
                <i class="bi bi-x-circle me-1"></i> Сбросить
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
            <i class="bi bi-list-check me-2"></i>
            Список составов заказов
          </h5>
        </div>
      </div>

      <div v-if="loading && filteredElements.length === 0" class="card-body text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-3 text-muted">Загружаем список составов заказов...</p>
      </div>

      <div v-else-if="filteredElements.length > 0" class="list-group list-group-flush">
        <div v-for="item in filteredElements" :key="item.id" class="list-group-item list-group-item-action">
          <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              <div>
                <h6 class="mb-1">Заказ №{{ item.order?.number || 'Неизвестно' }}</h6>
                <p class="text-muted mb-0 small">
                  <i class="bi bi-gear me-1"></i>
                  {{ item.bearing?.name || 'Неизвестный подшипник' }}
                  <span class="ms-3">
                    <i class="bi bi-box-seam me-1"></i>
                    Количество: <strong>{{ item.ammount }}</strong>
                  </span>
                  <span v-if="item.order?.client" class="ms-3">
                    <i class="bi bi-person me-1"></i>
                    Клиент: {{ item.order.client.name }}
                  </span>
                  <span v-if="isSuperuser && item.order?.client?.user" class="ms-3">
                    <i class="bi bi-person-badge me-1"></i>
                    Пользователь: {{ item.order.client.user.username }}
                  </span>
                </p>
              </div>
            </div>
            <div class="btn-group">
              <button class="btn btn-outline-primary btn-sm" @click="onElementEditClick(item)" :disabled="loading"
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
          <i class="bi bi-list-check display-1"></i>
        </div>
        <h5 class="text-muted">Список составов заказов пуст</h5>
        <p class="text-muted">Добавьте первый состав заказа с помощью формы выше</p>
      </div>
    </div>

    <div v-if="showEditModal">
      <div v-if="isDoubleAuth" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="bi bi-pencil-square me-2"></i>
                Редактировать состав заказа
              </h5>
              <button type="button" class="btn-close" @click="closeEditModal" aria-label="Закрыть"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="onUpdateElement" id="editForm">
                <div class="row g-3">
                  <div class="col-12">
                    <div class="form-floating">
                      <select class="form-select" id="editOrder" v-model="elementToEdit.order_id" required
                        :class="{ 'is-invalid': !elementToEdit.order_id }">
                        <option value="" disabled>Выберите заказ</option>
                        <option :value="o.id" v-for="o in orders" :key="o.id">
                          Заказ №{{ o.number }} ({{ o.client?.name || 'Клиент не указан' }})
                        </option>
                      </select>
                      <label for="editOrder">Заказ *</label>
                      <div class="invalid-feedback">
                        Пожалуйста, выберите заказ
                      </div>
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="form-floating">
                      <select class="form-select" id="editBearing" v-model="elementToEdit.bearing_id" required
                        :class="{ 'is-invalid': !elementToEdit.bearing_id }">
                        <option value="" disabled>Выберите подшипник</option>
                        <option :value="b.id" v-for="b in bearings" :key="b.id">
                          {{ b.name }} (вн.д: {{ b.inner_d }}, нар.д: {{ b.outer_d }}, высота: {{ b.height }})
                        </option>
                      </select>
                      <label for="editBearing">Подшипник *</label>
                      <div class="invalid-feedback">
                        Пожалуйста, выберите подшипник
                      </div>
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="form-floating">
                      <input type="number" class="form-control" id="editAmount" v-model="elementToEdit.ammount"
                        placeholder="Количество" required min="1" step="1"
                        :class="{ 'is-invalid': !elementToEdit.ammount }" />
                      <label for="editAmount">Количество *</label>
                      <div class="invalid-feedback">
                        Пожалуйста, введите количество
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
                :disabled="loading || !elementToEdit.order_id || !elementToEdit.bearing_id || !elementToEdit.ammount">
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
  border-bottom: 1px solid rgba(0, 0, 0, .125);
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

.stats-card {
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.stats-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border-color: #dee2e6;
}

.stats-icon {
  opacity: 0.8;
}

.stats-value {
  font-size: 1.5rem;
  margin: 0.5rem 0;
}

.stats-label {
  font-size: 0.85rem;
}

/* Стили для модальных окон */
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
  max-width: 600px;
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

@media (max-width: 768px) {
  .stats-card {
    padding: 1rem !important;
  }

  .stats-value {
    font-size: 1.2rem;
  }

  .stats-label {
    font-size: 0.75rem;
  }
}

.badge.bg-warning {
  font-size: 0.7em;
  vertical-align: middle;
}
</style>