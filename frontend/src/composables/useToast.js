import { ref } from 'vue';

const toastMessage = ref('');
const toastType = ref('info'); // 'success', 'warning', 'error', 'info'
const toastVisible = ref(false);
let toastTimeout = null;

export function useToast() {
  const showToast = (message, type = 'info') => {
    if (toastTimeout) {
      clearTimeout(toastTimeout);
    }
    toastMessage.value = message;
    toastType.value = type;
    toastVisible.value = true;

    toastTimeout = setTimeout(() => {
      toastVisible.value = false;
    }, 4000);
  };

  return {
    toastMessage,
    toastType,
    toastVisible,
    showToast
  };
}
