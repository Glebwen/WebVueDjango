<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/userStore';

const userStore = useUserStore();
const { isSuperuser } = storeToRefs(userStore);


const elementToAdd = ref({
  name: '',
  inner_d: 0,
  outer_d: 0,
  height: 0,
  price: 0,
  ammount: 0
});

const elementToEdit = ref({
  id: null,
  name: '',
  inner_d: 0,
  outer_d: 0,
  height: 0,
  price: 0,
  ammount: 0
});

const bearingsPictureRef = ref();
const bearingEditPictureRef = ref();
const bearingAddImageUrl = ref();
const bearingEditImageUrl = ref();

const loading = ref(false);
const statsLoading = ref(false);
const exportLoading = ref(false);
const error = ref(null);
const showEditModal = ref(false);
const showImageViewModal = ref(false);
const selectedImage = ref('');

const filteredElements = ref([]);
const showFilters = ref(false);

const filters = ref({
  name: '',
  inner_d_min: '',
  inner_d_max: '',
  outer_d_min: '',
  outer_d_max: '',
  height_min: '',
  height_max: '',
  price_min: '',
  price_max: '',
  ammount_min: '',
  ammount_max: ''
});


async function applyFilters() {
  try {
    loading.value = true;
    const response = await axios.post('/api/bearings/filter/', filters.value);
    filteredElements.value = response.data;
  } catch (error) {
    console.error('Ошибка при фильтрации:', error);
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  filters.value = {
    name: '',
    inner_d_min: '',
    inner_d_max: '',
    outer_d_min: '',
    outer_d_max: '',
    height_min: '',
    height_max: '',
    price_min: '',
    price_max: '',
    ammount_min: '',
    ammount_max: ''
  };
  applyFilters();
}


const stats = ref({
  total_count: 0,
  total_amount: 0,
  avg_price: 0,
  max_price: 0,
  min_price: 0,
  total_value: 0
});

async function fetchStats() {
  try {
    statsLoading.value = true;
    const response = await axios.get("/api/bearings/stats/");
    stats.value = response.data;
  } catch (err) {
    console.error("Ошибка при загрузке статистики:", err);
    error.value = "Не удалось загрузить статистику";
  } finally {
    statsLoading.value = false;
  }
}

async function onElementAdd() {
  try {
    if (!elementToAdd.value.name.trim()) {
      error.value = "Пожалуйста, заполните название";
      return;
    }

    const formData = new FormData();

    formData.append('name', elementToAdd.value.name);
    formData.append('inner_d', elementToAdd.value.inner_d);
    formData.append('outer_d', elementToAdd.value.outer_d);
    formData.append('height', elementToAdd.value.height);
    formData.append('price', elementToAdd.value.price);
    formData.append('ammount', elementToAdd.value.ammount);

    if (bearingsPictureRef.value?.files[0]) {
      formData.append('picture', bearingsPictureRef.value.files[0]);
    }

    await axios.post("/api/bearings/", formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    elementToAdd.value = {
      name: '',
      inner_d: 0,
      outer_d: 0,
      height: 0,
      price: 0,
      ammount: 0
    };
    bearingAddImageUrl.value = null;
    if (bearingsPictureRef.value) {
      bearingsPictureRef.value.value = '';
    }
    error.value = null;

    await applyFilters();
    await fetchStats();
  } catch (err) {
    console.error("Ошибка при добавлении подшипника:", err);
    error.value = err.response?.data?.picture?.[0] || "Не удалось добавить подшипник";
  }
}

function bearingAddPictureChange() {
  if (bearingsPictureRef.value?.files[0]) {
    bearingAddImageUrl.value = URL.createObjectURL(bearingsPictureRef.value.files[0]);
  }
}

function bearingEditPictureChange() {
  if (bearingEditPictureRef.value?.files[0]) {
    bearingEditImageUrl.value = URL.createObjectURL(bearingEditPictureRef.value.files[0]);
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

async function onRemoveClick(element) {
  if (!confirm(`Вы уверены, что хотите удалить подшипник "${element.name}"?`)) {
    return;
  }

  try {
    await axios.delete(`/api/bearings/${element.id}/`);
    await applyFilters();
    await fetchStats();
  } catch (err) {
    console.error("Ошибка при удалении подшипника:", err);
    error.value = "Не удалось удалить подшипник";
  }
}

function onElementEditClick(element) {
  elementToEdit.value = { ...element };
  bearingEditImageUrl.value = null;
  if (bearingEditPictureRef.value) {
    bearingEditPictureRef.value.value = '';
  }
  showEditModal.value = true;
}

async function onUpdateElement() {
  try {
    if (!elementToEdit.value.name.trim()) {
      error.value = "Пожалуйста, заполните название";
      return;
    }

    const formData = new FormData();

    formData.append('name', elementToEdit.value.name);
    formData.append('inner_d', elementToEdit.value.inner_d);
    formData.append('outer_d', elementToEdit.value.outer_d);
    formData.append('height', elementToEdit.value.height);
    formData.append('price', elementToEdit.value.price);
    formData.append('ammount', elementToEdit.value.ammount);

    if (bearingEditPictureRef.value?.files[0]) {
      formData.append('picture', bearingEditPictureRef.value.files[0]);
    }

    await axios.put(
      `/api/bearings/${elementToEdit.value.id}/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );

    error.value = null;
    await applyFilters();
    await fetchStats();

    showEditModal.value = false;
  } catch (err) {
    console.error("Ошибка при обновлении подшипника:", err);
    error.value = err.response?.data?.picture?.[0] || "Не удалось обновить данные подшипника";
  }
}

function closeEditModal() {
  showEditModal.value = false;
}

function formatNumber(num) {
  return new Intl.NumberFormat('ru-RU').format(num);
}

function formatPrice(price) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(price);
}

async function ExportToExcel() {  
  try {
    const token = Cookies.get("csrftoken");
    const url = `/api/bearings/export/?_=${Date.now()}`;
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'bearings_export.xlsx';
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
  } catch (err) {
    console.error("Ошибка при экспорте в Excel:", err);
    error.value = "Не удалось экспортировать данные в Excel";
  }
}

onBeforeMount(async () => {
  await fetchStats();
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


    <div class="card shadow-sm mb-4">
      <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0">
          <i class="bi bi-bar-chart-line me-2"></i>
          Статистика подшипников
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
          <div class="col-md-2 col-6">
            <div class="stats-card bg-light rounded p-3 text-center">
              <div class="stats-icon text-primary mb-2">
                <i class="bi bi-box-seam fs-4"></i>
              </div>
              <h6 class="stats-value fw-bold">{{ formatNumber(stats.total_count) }}</h6>
              <p class="stats-label text-muted mb-0 small">Типов подшипников</p>
            </div>
          </div>
          <div class="col-md-2 col-6">
            <div class="stats-card bg-light rounded p-3 text-center">
              <div class="stats-icon text-success mb-2">
                <i class="bi bi-boxes fs-4"></i>
              </div>
              <h6 class="stats-value fw-bold">{{ formatNumber(stats.total_amount) }}</h6>
              <p class="stats-label text-muted mb-0 small">Всего на складе</p>
            </div>
          </div>
          <div class="col-md-2 col-6">
            <div class="stats-card bg-light rounded p-3 text-center">
              <div class="stats-icon text-warning mb-2">
                <i class="bi bi-currency-exchange fs-4"></i>
              </div>
              <h6 class="stats-value fw-bold">{{ formatPrice(stats.avg_price) }}</h6>
              <p class="stats-label text-muted mb-0 small">Средняя цена</p>
            </div>
          </div>
          <div class="col-md-2 col-6">
            <div class="stats-card bg-light rounded p-3 text-center">
              <div class="stats-icon text-danger mb-2">
                <i class="bi bi-arrow-up-circle fs-4"></i>
              </div>
              <h6 class="stats-value fw-bold">{{ formatPrice(stats.max_price) }}</h6>
              <p class="stats-label text-muted mb-0 small">Макс. цена</p>
            </div>
          </div>
          <div class="col-md-2 col-6">
            <div class="stats-card bg-light rounded p-3 text-center">
              <div class="stats-icon text-info mb-2">
                <i class="bi bi-arrow-down-circle fs-4"></i>
              </div>
              <h6 class="stats-value fw-bold">{{ formatPrice(stats.min_price) }}</h6>
              <p class="stats-label text-muted mb-0 small">Мин. цена</p>
            </div>
          </div>
          <div class="col-md-2 col-6">
            <div class="stats-card bg-light rounded p-3 text-center">
              <div class="stats-icon text-success mb-2">
                <i class="bi bi-cash-stack fs-4"></i>
              </div>
              <h6 class="stats-value fw-bold">{{ formatPrice(stats.total_value) }}</h6>
              <p class="stats-label text-muted mb-0 small">Общая стоимость</p>
            </div>
          </div>
        </div>
      </div>
    </div>


    <div v-if="isSuperuser" class="card shadow-sm mb-4">
      <div class="card-header bg-primary text-white">
        <h5 class="card-title mb-0">
          <i class="bi bi-plus-circle me-2"></i>
          Добавить новый подшипник
        </h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="onElementAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-2">
              <div class="form-floating">
                <input type="text" class="form-control" id="nameInput" v-model="elementToAdd.name" required
                  placeholder="Название" />
                <label for="nameInput">Название *</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="innerDInput" v-model="elementToAdd.inner_d" required
                  placeholder="Внутр. диаметр" min="0" step="0.1" />
                <label for="innerDInput">Внутр. d</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="outerDInput" v-model="elementToAdd.outer_d" required
                  placeholder="Внеш. диаметр" min="0" step="0.1" />
                <label for="outerDInput">Внеш. d</label>
              </div>
            </div>
            <div class="col-md-1">
              <div class="form-floating">
                <input type="number" class="form-control" id="heightInput" v-model="elementToAdd.height" required
                  placeholder="Высота" min="0" step="0.1" />
                <label for="heightInput">Высота</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="priceInput" v-model="elementToAdd.price" required
                  placeholder="Цена" min="0" step="1" />
                <label for="priceInput">Цена</label>
              </div>
            </div>
            <div class="col-md-1">
              <div class="form-floating">
                <input type="number" class="form-control" id="amountInput" v-model="elementToAdd.ammount" required
                  placeholder="Количество" min="0" step="1" />
                <label for="amountInput">Кол-во</label>
              </div>
            </div>
            <div class="col-md">
              <button type="submit" class="btn btn-primary w-100" :disabled="loading || !elementToAdd.name.trim()">
                Добавить
              </button>
            </div>
          </div>

          <div class="row mt-3">
            <div class="col-md-6">
              <input type="file" class="form-control" ref="bearingsPictureRef" @change="bearingAddPictureChange"
                accept="image/*" />
            </div>
            <div class="col-md-6">
              <div v-if="bearingAddImageUrl" class="d-flex align-items-center">
                <span class="me-2">Превью:</span>
                <img :src="bearingAddImageUrl"
                  style="width: 60px; height: 60px; border-radius: 8px; object-fit: cover; cursor: pointer;"
                  alt="Превью изображения" @click="openImageViewModal(bearingAddImageUrl)"
                  title="Нажмите для увеличения">
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0">
          <i class="bi bi-funnel me-2"></i>
          Фильтры подшипников
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
                <input type="text" class="form-control" id="filterName" v-model="filters.name" placeholder="Название" />
                <label for="filterName">
                  <i class="bi bi-search me-1"></i> Название
                </label>
              </div>
            </div>

            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterInnerMin" v-model="filters.inner_d_min"
                  placeholder="От" min="0" step="0.1" />
                <label for="filterInnerMin">Внутр. d от</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterInnerMax" v-model="filters.inner_d_max"
                  placeholder="До" min="0" step="0.1" />
                <label for="filterInnerMax">Внутр. d до</label>
              </div>
            </div>

            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterOuterMin" v-model="filters.outer_d_min"
                  placeholder="От" min="0" step="0.1" />
                <label for="filterOuterMin">Внеш. d от</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterOuterMax" v-model="filters.outer_d_max"
                  placeholder="До" min="0" step="0.1" />
                <label for="filterOuterMax">Внеш. d до</label>
              </div>
            </div>

            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterHeightMin" v-model="filters.height_min"
                  placeholder="От" min="0" step="0.1" />
                <label for="filterHeightMin">Высота от</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterHeightMax" v-model="filters.height_max"
                  placeholder="До" min="0" step="0.1" />
                <label for="filterHeightMax">Высота до</label>
              </div>
            </div>

            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterPriceMin" v-model="filters.price_min"
                  placeholder="От" min="0" step="1" />
                <label for="filterPriceMin">Цена от</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterPriceMax" v-model="filters.price_max"
                  placeholder="До" min="0" step="1" />
                <label for="filterPriceMax">Цена до</label>
              </div>
            </div>

            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterAmountMin" v-model="filters.ammount_min"
                  placeholder="От" min="0" step="1" />
                <label for="filterAmountMin">Кол-во от</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input type="number" class="form-control" id="filterAmountMax" v-model="filters.ammount_max"
                  placeholder="До" min="0" step="1" />
                <label for="filterAmountMax">Кол-во до</label>
              </div>
            </div>

            <div class="col-md-4 d-flex gap-2 align-items-end">
              <button type="submit" class="btn btn-primary flex-grow-1">
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
            <i class="bi bi-gear me-2"></i>
            Список подшипников
          </h5>
          <button 
              class="btn btn-outline-success btn-sm"
              @click="ExportToExcel"
              :disabled="exportLoading || filteredElements.length == 0"
              title="Экспорт"
              v-if="filteredElements.length > 0"
            >
              Экспорт
          </button>
        </div>
      </div>

      <div v-if="loading && filteredElements.length == 0" class="card-body text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-3 text-muted">Загружаем список подшипников...</p>
      </div>

      <div v-else-if="filteredElements.length > 0" class="list-group list-group-flush">
        <div
          v-for="item in filteredElements"
          :key="item.id"
          class="list-group-item list-group-item-action"
        >
          <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              <div v-if="item.picture" class="me-3">
                <img :src="item.picture"
                  style="width: 60px; height: 60px; border-radius: 8px; object-fit: cover; cursor: pointer;"
                  alt="Фото подшипника" @click="openImageViewModal(item.picture)"
                  title="Нажмите для увеличения">
              </div>
              <div v-else
                class="avatar-placeholder bg-primary text-white rounded d-flex align-items-center justify-content-center me-3"
                style="width: 60px; height: 60px;">
                <i class="bi bi-gear-fill"></i>
              </div>
              <div>
                <h6 class="mb-1">{{ item.name }}</h6>
                <p class="text-muted mb-0 small">
                  <i class="bi bi-circle me-1"></i>
                  Внутр. d: {{ item.inner_d }} |
                  <i class="bi bi-circle me-1 ms-2"></i>
                  Внеш. d: {{ item.outer_d }} |
                  <i class="bi bi-rulers me-1 ms-2"></i>
                  Высота: {{ item.height }} |
                  <i class="bi bi-currency-dollar me-1 ms-2"></i>
                  Цена: {{ item.price }} |
                  <i class="bi bi-box me-1 ms-2"></i>
                  Кол-во: {{ item.ammount }}
                </p>
              </div>
            </div>
            <div v-if="isSuperuser" class="btn-group">
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
          <i class="bi bi-gear display-1"></i>
        </div>
        <h5 class="text-muted">Список подшипников пуст</h5>
        <p class="text-muted">Добавьте первый подшипник с помощью формы выше</p>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-pencil-square me-2"></i>
              Редактировать подшипник
            </h5>
            <button type="button" class="btn-close" @click="closeEditModal" aria-label="Закрыть"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="onUpdateElement" id="editForm">
              <div class="row g-3">
                <div class="col-12">
                  <div class="form-floating">
                    <input type="text" class="form-control" id="editName" v-model="elementToEdit.name"
                      placeholder="Название" required :class="{ 'is-invalid': !elementToEdit.name.trim() }" />
                    <label for="editName">Название *</label>
                    <div class="invalid-feedback">
                      Пожалуйста, введите название
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-floating">
                    <input type="number" class="form-control" id="editInnerD" v-model="elementToEdit.inner_d"
                      placeholder="Внутренний диаметр" required min="0" step="0.01" />
                    <label for="editInnerD">Внутренний диаметр</label>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-floating">
                    <input type="number" class="form-control" id="editOuterD" v-model="elementToEdit.outer_d"
                      placeholder="Внешний диаметр" required min="0" step="0.01" />
                    <label for="editOuterD">Внешний диаметр</label>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-floating">
                    <input type="number" class="form-control" id="editHeight" v-model="elementToEdit.height"
                      placeholder="Высота" required min="0" step="0.01" />
                    <label for="editHeight">Высота</label>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-floating">
                    <input type="number" class="form-control" id="editPrice" v-model="elementToEdit.price"
                      placeholder="Цена" required min="0" step="0.01" />
                    <label for="editPrice">Цена</label>
                  </div>
                </div>
                <div class="col-12">
                  <div class="form-floating">
                    <input type="number" class="form-control" id="editAmount" v-model="elementToEdit.ammount"
                      placeholder="Количество" required min="0" step="1" />
                    <label for="editAmount">Количество</label>
                  </div>
                </div>

                <div class="col-12">
                  <label class="form-label">Изменить изображение</label>
                  <input type="file" class="form-control" ref="bearingEditPictureRef" @change="bearingEditPictureChange"
                    accept="image/*" />
                </div>

                <div class="col-12">
                  <div class="d-flex align-items-center mt-3">
                    <div v-if="bearingEditImageUrl" class="me-4">
                      <p class="mb-1 small text-muted">Новое изображение:</p>
                      <img :src="bearingEditImageUrl"
                        style="width: 100px; height: 100px; border-radius: 8px; object-fit: cover; cursor: pointer;"
                        alt="Новое фото" @click="openImageViewModal(bearingEditImageUrl)"
                        title="Нажмите для увеличения">
                    </div>
                    <div v-else-if="elementToEdit.picture" class="me-4">
                      <p class="mb-1 small text-muted">Текущее изображение:</p>
                      <img :src="elementToEdit.picture"
                        style="width: 100px; height: 100px; border-radius: 8px; object-fit: cover; cursor: pointer;"
                        alt="Текущее фото" @click="openImageViewModal(elementToEdit.picture)"
                        title="Нажмите для увеличения">
                    </div>
                    <div v-else class="me-4">
                      <p class="mb-1 small text-muted">Изображение:</p>
                      <div
                        class="avatar-placeholder bg-secondary text-white rounded d-flex align-items-center justify-content-center"
                        style="width: 100px; height: 100px;">
                        <i class="bi bi-gear-fill fs-4"></i>
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
              :disabled="loading || !elementToEdit.name.trim()">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              Сохранить изменения
            </button>
          </div>
        </div>
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
  font-size: 1.2rem;
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

.enlarged-image {
  max-height: 70vh;
  max-width: 100%;
  width: auto;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
}

/* Анимации */
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