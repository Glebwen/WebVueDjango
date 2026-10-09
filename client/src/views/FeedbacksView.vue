<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/userStore';

const userStore = useUserStore();
const { isSuperuser } = storeToRefs(userStore);

const feedbackToAdd = ref({
  review: '',
  client_id: null
});

const feedbackToEdit = ref({
  id: null,
  review: '',
  client_id: null
});

const feedbacks = ref([]);
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

const filteredFeedbacks = computed(() => {
  if (!isSuperuser.value || selectedUserId.value === 'all') {
    return feedbacks.value;
  }
  
  return feedbacks.value.filter(feedback => 
    feedback.client && 
    feedback.client.user && 
    feedback.client.user.id === parseInt(selectedUserId.value)
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

async function fetchFeedbacks() {
  try {
    loading.value = true;
    error.value = null;
    const response = await axios.get("/api/feedbacks/");
    feedbacks.value = response.data;
  } catch (err) {
    console.error("Ошибка при загрузке отзывов:", err);
    error.value = "Не удалось загрузить список отзывов";
    feedbacks.value = [];
  } finally {
    loading.value = false;
  }
}

async function onFeedbackAdd() {
  try {
    if (!feedbackToAdd.value.review.trim() || !feedbackToAdd.value.client_id) {
      error.value = "Пожалуйста, заполните все поля";
      return;
    }

    await axios.post("/api/feedbacks/", feedbackToAdd.value);
    
    feedbackToAdd.value = { review: '', client_id: null };
    error.value = null;
    
    await fetchFeedbacks();
  } catch (err) {
    console.error("Ошибка при добавлении отзыва:", err);
    error.value = "Не удалось добавить отзыв";
  }
}

async function onRemoveClick(feedback) {
  if (!confirm(`Вы уверены, что хотите удалить этот отзыв?`)) {
    return;
  }

  try {
    await axios.delete(`/api/feedbacks/${feedback.id}/`);
    await fetchFeedbacks();
  } catch (err) {
    console.error("Ошибка при удалении отзыва:", err);
    error.value = "Не удалось удалить отзыв";
  }
}

function onFeedbackEditClick(feedback) {
  feedbackToEdit.value = {
    ...feedback,
    client_id: feedback.client?.id || feedback.client_id
  };
  showEditModal.value = true;
}

async function onUpdateFeedback() {
  try {
    if (!feedbackToEdit.value.review.trim() || !feedbackToEdit.value.client_id) {
      error.value = "Пожалуйста, заполните все поля";
      return;
    }

    await axios.put(
      `/api/feedbacks/${feedbackToEdit.value.id}/`, 
      feedbackToEdit.value
    );
    
    error.value = null;
    await fetchFeedbacks();
    
    showEditModal.value = false;
  } catch (err) {
    console.error("Ошибка при обновлении отзыва:", err);
    error.value = "Не удалось обновить отзыв";
  }
}

function closeEditModal() {
  showEditModal.value = false;
}

onBeforeMount(async () => {
  await fetchClients();
  await fetchFeedbacks();
});
</script>

<template>
  <div class="container py-4">
    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = null" aria-label="Закрыть"></button>
    </div>

    <div v-if="isSuperuser && feedbacks.length > 0" class="card shadow-sm mb-4">
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
          <i class="bi bi-chat-left-text me-2"></i>
          Добавить новый отзыв
        </h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="onFeedbackAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-7">
              <div class="form-floating">
                <textarea
                  class="form-control"
                  id="reviewInput"
                  v-model="feedbackToAdd.review"
                  required
                  placeholder="Текст отзыва"
                  rows="3"
                  style="min-height: 80px;"
                ></textarea>
                <label for="reviewInput">Текст отзыва *</label>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-floating">
                <select
                  class="form-select"
                  id="clientInput"
                  v-model="feedbackToAdd.client_id"
                  required
                >
                  <option value="" disabled>Выберите клиента</option>
                  <option :value="c.id" v-for="c in clients" :key="c.id">
                    {{ c.name }}
                  </option>
                </select>
                <label for="clientInput">Клиент *</label>
              </div>
            </div>
            <div class="col-md">
              <button 
                type="submit" 
                class="btn btn-primary w-100"
                :disabled="loading || !feedbackToAdd.review.trim() || !feedbackToAdd.client_id"
              >
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
            <i class="bi bi-chat-left-quote me-2"></i>
            Список отзывов
          </h5>
        </div>
      </div>
      
      <div v-if="loading && feedbacks.length === 0" class="card-body text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-3 text-muted">Загружаем список отзывов...</p>
      </div>

      <div v-else-if="filteredFeedbacks.length > 0" class="list-group list-group-flush">
        <div
          v-for="item in filteredFeedbacks"
          :key="item.id"
          class="list-group-item list-group-item-action"
        >
          <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              <div class="avatar-placeholder bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                   style="width: 40px; height: 40px;">
                {{ item.client?.name?.charAt(0).toUpperCase() || '?' }}
              </div>
              <div style="max-width: calc(100% - 120px);">
                <h6 class="mb-1">{{ item.client?.name || 'Неизвестный клиент' }}</h6>
                <p class="text-muted mb-0 small text-truncate">
                  {{ item.review }}
                </p>
                <p class="text-muted mb-0 small" v-if="isSuperuser && item.client?.user">
                  <i class="bi bi-person-badge me-1"></i>
                  Пользователь: {{ item.client.user.username }}
                </p>
              </div>
            </div>
            <div v-if="isSuperuser" class="btn-group">
              <button
                class="btn btn-outline-primary btn-sm"
                @click="onFeedbackEditClick(item)"
                :disabled="loading"
                title="Редактировать"
              >
                Изменить
              </button>
              <button
                class="btn btn-outline-danger btn-sm"
                @click="onRemoveClick(item)"
                :disabled="loading"
                title="Удалить"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="card-body text-center py-5">
        <div class="text-muted mb-3">
          <i class="bi bi-chat-left-text display-1"></i>
        </div>
        <h5 class="text-muted">Список отзывов пуст</h5>
        <p class="text-muted" v-if="isSuperuser && selectedUserId !== 'all'">
          У выбранного пользователя нет отзывов
        </p>
        <p class="text-muted" v-else>
          Добавьте первый отзыв с помощью формы выше
        </p>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-pencil-square me-2"></i>
              Редактировать отзыв
            </h5>
            <button
              type="button"
              class="btn-close"
              @click="closeEditModal"
              aria-label="Закрыть"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="onUpdateFeedback" id="editForm">
              <div class="row g-3">
                <div class="col-12">
                  <div class="form-floating">
                    <textarea
                      class="form-control"
                      id="editReview"
                      v-model="feedbackToEdit.review"
                      placeholder="Текст отзыва"
                      required
                      rows="4"
                      style="min-height: 100px;"
                      :class="{ 'is-invalid': !feedbackToEdit.review.trim() }"
                    ></textarea>
                    <label for="editReview">Текст отзыва *</label>
                    <div class="invalid-feedback">
                      Пожалуйста, введите текст отзыва
                    </div>
                  </div>
                </div>
                <div class="col-12">
                  <div class="form-floating">
                    <select
                      class="form-select"
                      id="editClient"
                      v-model="feedbackToEdit.client_id"
                      required
                      :class="{ 'is-invalid': !feedbackToEdit.client_id }"
                    >
                      <option value="" disabled>Выберите клиента</option>
                      <option :value="c.id" v-for="c in clients" :key="c.id">
                        {{ c.name }}
                      </option>
                    </select>
                    <label for="editClient">Клиент *</label>
                    <div class="invalid-feedback">
                      Пожалуйста, выберите клиента
                    </div>
                  </div>
                </div>
                <div v-if="isSuperuser && feedbackToEdit.client?.user" class="col-12">
                  <div class="alert alert-info">
                    <i class="bi bi-person-badge me-2"></i>
                    Клиент принадлежит пользователю: <strong>{{ feedbackToEdit.client.user.username }}</strong>
                    <template v-if="feedbackToEdit.client.user.email"> ({{ feedbackToEdit.client.user.email }})</template>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="closeEditModal"
              :disabled="loading"
            >
              Отмена
            </button>
            <button
              type="submit"
              form="editForm"
              class="btn btn-primary"
              :disabled="loading || !feedbackToEdit.review.trim() || !feedbackToEdit.client_id"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              Сохранить изменения
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.avatar-placeholder {
  font-weight: bold;
  font-size: 1.2rem;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.card-header {
  border-bottom: 1px solid rgba(0,0,0,.125);
}

.form-control:focus,
.form-select:focus {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

.btn-outline-primary:hover, .btn-outline-danger:hover {
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
</style>