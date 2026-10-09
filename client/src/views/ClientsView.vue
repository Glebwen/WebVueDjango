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
  name: '',
  phone: ''
});

const elementToEdit = ref({
  id: null,
  name: '',
  phone: ''
});

const clientsPictureRef = ref();
const clientEditPictureRef = ref();
const clientAddImageUrl = ref();
const clientEditImageUrl = ref();

const elements = ref([]);
const selectedUserId = ref('all');
const loading = ref(false);
const error = ref(null);
const showEditModal = ref(false);
const showImageViewModal = ref(false);
const selectedImage = ref('');

const uniqueUsers = computed(() => {
  if (!isSuperuser.value) return [];

  const usersDict = {};

  elements.value.forEach(client => {
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

const filteredElements = computed(() => {
  if (!isSuperuser.value || selectedUserId.value === 'all') {
    return elements.value;
  }

  return elements.value.filter(client =>
    client.user && client.user.id === parseInt(selectedUserId.value)
  );
});

async function fetchElements() {
  try {
    loading.value = true;
    error.value = null;
    const response = await axios.get("/api/clients/");
    elements.value = response.data;
  } catch (err) {
    console.error("Ошибка при загрузке клиентов:", err);
    error.value = "Не удалось загрузить список клиентов";
    elements.value = [];
  } finally {
    loading.value = false;
  }
}

async function onActivateTOTP() {
  await userStore.fetchUserInfo()
}

async function onElementAdd() {
  try {
    if (!elementToAdd.value.name.trim() || !elementToAdd.value.phone.trim()) {
      error.value = "Пожалуйста, заполните все поля";
      return;
    }

    const formData = new FormData();

    if (clientsPictureRef.value?.files[0]) {
      formData.append('picture', clientsPictureRef.value.files[0]);
    }

    formData.append('name', elementToAdd.value.name);
    formData.append('phone', elementToAdd.value.phone);

    await axios.post("/api/clients/", formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    elementToAdd.value = { name: '', phone: '' };
    clientAddImageUrl.value = null;
    if (clientsPictureRef.value) {
      clientsPictureRef.value.value = '';
    }
    error.value = null;

    await fetchElements();
  } catch (err) {
    console.error("Ошибка при добавлении клиента:", err);
    error.value = err.response?.data?.picture?.[0] || "Не удалось добавить клиента";
  }
}

function clientAddPictureChange() {
  if (clientsPictureRef.value?.files[0]) {
    clientAddImageUrl.value = URL.createObjectURL(clientsPictureRef.value.files[0]);
  }
}

function clientEditPictureChange() {
  if (clientEditPictureRef.value?.files[0]) {
    clientEditImageUrl.value = URL.createObjectURL(clientEditPictureRef.value.files[0]);
  }
}

async function onRemoveClick(element) {
  if (!confirm(`Вы уверены, что хотите удалить клиента "${element.name}"?`)) {
    return;
  }

  try {
    await axios.delete(`/api/clients/${element.id}/`);
    await fetchElements();
  } catch (err) {
    console.error("Ошибка при удалении клиента:", err);
    error.value = "Не удалось удалить клиента";
  }
}

function openImageViewModal(imageUrl) {
  selectedImage.value = imageUrl;
  showImageViewModal.value = true;
}

function closeImageViewModal() {
  showImageViewModal.value = false;
  selectedImage.value = '';
}

function onElementEditClick(element) {
  elementToEdit.value = { ...element };
  clientEditImageUrl.value = null;
  if (clientEditPictureRef.value) {
    clientEditPictureRef.value.value = '';
  }
  showEditModal.value = true;
}

async function onUpdateElement() {
  try {
    if (!elementToEdit.value.name.trim() || !elementToEdit.value.phone.trim()) {
      error.value = "Пожалуйста, заполните все поля";
      return;
    }

    const formData = new FormData();

    formData.append('name', elementToEdit.value.name);
    formData.append('phone', elementToEdit.value.phone);

    if (clientEditPictureRef.value?.files[0]) {
      formData.append('picture', clientEditPictureRef.value.files[0]);
    }

    await axios.put(
      `/api/clients/${elementToEdit.value.id}/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );

    error.value = null;
    await fetchElements();

    showEditModal.value = false;
  } catch (err) {
    if (err.response.status == 403){
      await userStore.fetchUserInfo()
    }
    else{
      console.error("Ошибка при обновлении клиента:", err);
      error.value = err.response?.data?.picture?.[0] || "Не удалось обновить данные клиента";
    }
  }
}

function closeEditModal() {
  showEditModal.value = false;
}

onBeforeMount(async () => {
  await fetchElements();
});
</script>

<template>
  <div class="container py-4">
    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = null" aria-label="Закрыть"></button>
    </div>

    <div v-if="isSuperuser && elements.length > 0" class="card shadow-sm mb-4">
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
          <i class="bi bi-person-plus me-2"></i>
          Добавить нового клиента
        </h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="onElementAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-5">
              <div class="form-floating">
                <input type="text" class="form-control" id="nameInput" v-model="elementToAdd.name" required />
                <label for="nameInput">ФИО *</label>
              </div>
            </div>
            <div class="col-md-5">
              <div class="form-floating">
                <input type="tel" class="form-control" id="phoneInput" v-model="elementToAdd.phone" required />
                <label for="phoneInput">Номер телефона *</label>
              </div>
            </div>
            <div class="col-auto">
              <input class="form-control" type="file" ref="clientsPictureRef" @change="clientAddPictureChange"
                accept="image/*" />
            </div>
            <div class="col-auto">
              <img v-if="clientAddImageUrl" :src="clientAddImageUrl"
                style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; cursor: pointer;" alt="Превью"
                @click="openImageViewModal(clientAddImageUrl)" title="Нажмите для увеличения">
            </div>
            <div class="col-md-2">
              <button type="submit" class="btn btn-primary w-100"
                :disabled="loading || !elementToAdd.name.trim() || !elementToAdd.phone.trim()">
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
            <i class="bi bi-people me-2"></i>
            Список клиентов
          </h5>
        </div>
      </div>

      <div v-if="loading && elements.length === 0" class="card-body text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-3 text-muted">Загружаем список клиентов...</p>
      </div>

      <div v-else-if="filteredElements.length > 0" class="list-group list-group-flush">
        <div v-for="item in filteredElements" :key="item.id" class="list-group-item list-group-item-action">
          <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              <div v-if="item.picture" class="me-3">
                <img :src="item.picture"
                  style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; cursor: pointer;"
                  alt="Фото клиента" @click="openImageViewModal(item.picture)" title="Нажмите для увеличения">
              </div>
              <div v-else
                class="avatar-placeholder bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                style="width: 50px; height: 50px;">
                {{ item.name.charAt(0).toUpperCase() }}
              </div>
              <div>
                <h6 class="mb-1">{{ item.name }}</h6>
                <p class="text-muted mb-0 small">
                  <i class="bi bi-telephone me-1"></i>
                  {{ item.phone }}
                  <span v-if="isSuperuser && item.user" class="ms-2">
                    <i class="bi bi-person-badge me-1"></i>
                    Пользователь: {{ item.user.username }}
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
          <i class="bi bi-people display-1"></i>
        </div>
        <h5 class="text-muted">Список клиентов пуст</h5>
        <p class="text-muted" v-if="isSuperuser && selectedUserId !== 'all'">
          У выбранного пользователя нет клиентов
        </p>
        <p class="text-muted" v-else>
          Добавьте первого клиента с помощью формы выше
        </p>
      </div>
    </div>

    <div v-if="showEditModal">

      <div v-if="isDoubleAuth" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="bi bi-pencil-square me-2"></i>
                Редактировать клиента
              </h5>
              <button type="button" class="btn-close" @click="closeEditModal" aria-label="Закрыть"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="onUpdateElement" id="editForm">
                <div class="row g-3">
                  <div class="col-12">
                    <div class="form-floating">
                      <input type="text" class="form-control" id="editName" v-model="elementToEdit.name"
                        placeholder="ФИО" required :class="{ 'is-invalid': !elementToEdit.name.trim() }" />
                      <label for="editName">ФИО *</label>
                      <div class="invalid-feedback">
                        Пожалуйста, введите ФИО
                      </div>
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="form-floating">
                      <input type="tel" class="form-control" id="editPhone" v-model="elementToEdit.phone"
                        placeholder="Номер телефона" required pattern="^\+?[0-9\s\-\(\)]+$"
                        :class="{ 'is-invalid': !elementToEdit.phone.trim() }" />
                      <label for="editPhone">Номер телефона *</label>
                      <div class="invalid-feedback">
                        Пожалуйста, введите корректный номер телефона
                      </div>
                    </div>
                  </div>
                  <div v-if="isSuperuser && elementToEdit.user" class="col-12">
                    <div class="alert alert-info">
                      <i class="bi bi-person-badge me-2"></i>
                      Клиент принадлежит пользователю: <strong>{{ elementToEdit.user.username }}</strong>
                      <template v-if="elementToEdit.user.email"> ({{ elementToEdit.user.email }})</template>
                    </div>
                  </div>
                  <div class="col-12">
                    <label class="form-label">Изменить изображение</label>
                    <input type="file" class="form-control" ref="clientEditPictureRef" @change="clientEditPictureChange"
                      accept="image/*" />
                  </div>
                  <div class="col-12">
                    <div class="d-flex align-items-center mt-3">
                      <div v-if="clientEditImageUrl" class="me-4">
                        <p class="mb-1 small text-muted">Новое изображение:</p>
                        <img :src="clientEditImageUrl"
                          style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; cursor: pointer;"
                          alt="Новое фото" @click="openImageViewModal(clientEditImageUrl)"
                          title="Нажмите для увеличения">
                      </div>
                      <div v-else-if="elementToEdit.picture" class="me-4">
                        <p class="mb-1 small text-muted">Текущее изображение:</p>
                        <img :src="elementToEdit.picture"
                          style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; cursor: pointer;"
                          alt="Текущее фото" @click="openImageViewModal(elementToEdit.picture)"
                          title="Нажмите для увеличения">
                      </div>
                      <div v-else class="me-4">
                        <p class="mb-1 small text-muted">Изображение:</p>
                        <div
                          class="avatar-placeholder bg-secondary text-white rounded-circle d-flex align-items-center justify-content-center"
                          style="width: 80px; height: 80px;">
                          {{ elementToEdit.name?.charAt(0)?.toUpperCase() || '?' }}
                        </div>
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
                :disabled="loading || !elementToEdit.name.trim() || !elementToEdit.phone.trim()">
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



    <div v-if="showImageViewModal" class="modal-overlay image-view-overlay" @click.self="closeImageViewModal">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Просмотр изображения</h5>
            <button type="button" class="btn-close" @click="closeImageViewModal" aria-label="Закрыть"></button>
          </div>
          <div class="modal-body text-center">
            <img :src="selectedImage" class="enlarged-image" alt="Увеличенное изображение">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.avatar-placeholder {
  font-weight: bold;
  font-size: 1.5rem;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.card-header {
  border-bottom: 1px solid rgba(0, 0, 0, .125);
}

.form-control:focus {
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

.image-view-overlay {
  background-color: rgba(0, 0, 0, 0.9);
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

/* Увеличенное изображение */
.enlarged-image {
  max-height: 70vh;
  max-width: 100%;
  width: auto;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
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

@keyframes imageZoomIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

.enlarged-image {
  animation: imageZoomIn 0.3s ease-out;
}

</style>