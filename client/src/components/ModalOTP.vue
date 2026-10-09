<script setup>
import axios from 'axios';
import { ref, watch } from 'vue';
import QRCode from 'qrcode'

const key = ref('');
const totpUrl = ref('');
const qrcodeUrl = ref('');

const props = defineProps({ 
    onActivate: Function,
    onClose: Function
});

watch(totpUrl, async () => {
    qrcodeUrl.value = await QRCode.toDataURL(totpUrl.value);
})

async function onActivate() {
    await axios.post("/api/user/otp-login/", {
        key: key.value
    })
    await props.onActivate();
}

async function getTotpKey() {
    let r = await axios.get('/api/user/get-totp/')
    totpUrl.value = r.data.url;
}
</script>

<template>
    <div class="modal-overlay" @click.self="onClose">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        Настройка двухфакторной аутентификации
                    </h5>
                    <button type="button" class="btn-close" @click="onClose" aria-label="Закрыть"></button>
                </div>

                <div class="modal-body">
                    <div class="mb-4">                        
                        <div class="mb-3">
                            <button 
                                class="btn btn-primary w-100 mb-2" 
                                @click="getTotpKey"
                            >
                                Сгенерировать QR-код
                            </button>
                        </div>

                        <div v-if="qrcodeUrl" class="mb-4">
                            <div class="text-center mb-3">
                                <h6>Отсканируйте QR-код</h6>
                                <img :src="qrcodeUrl" alt="QR Code" class="img-fluid border rounded p-2 bg-light">
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="otp-code" class="form-label">
                                Введите код из приложения
                            </label>
                            <input 
                                type="text" 
                                id="otp-code"
                                v-model="key"
                                placeholder="6-значный код"
                                class="form-control text-center"
                                maxlength="6"
                            />
                        </div>
                    </div>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" @click="onClose">
                        Отмена
                    </button>
                    <button 
                        type="button" 
                        class="btn btn-primary" 
                        @click="onActivate"
                        :disabled="!key || key.length !== 6"
                    >
                        Активировать
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>

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


.form-control {
  font-size: 1.1rem;
  letter-spacing: 2px;
  font-family: monospace;
}



</style>