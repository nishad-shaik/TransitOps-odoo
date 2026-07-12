import { ref } from 'vue';
import { client } from '../api/client';

export function useApiResource(endpoint) {
  const data = ref(null);
  const loading = ref(false);
  const error = ref(null);

  const fetchResource = async () => {
    loading.value = true;
    error.value = null;
    try {
      data.value = await client.get(endpoint);
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  const createResource = async (payload) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await client.post(endpoint, payload);
      await fetchResource(); // Refresh list after create
      return response;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    data,
    loading,
    error,
    fetch: fetchResource,
    create: createResource
  };
}
