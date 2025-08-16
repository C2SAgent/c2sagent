import api from './index';

export const MediaApi = {
  async list() {
    return await api.get('/app_media/list')
  },
}
