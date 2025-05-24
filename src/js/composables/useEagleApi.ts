import { ref } from 'vue'

export type TImageItem = {
  id: string
  name: string
  size: number
  ext: string
  tags: string[]
  folders: string[]
  annotation: string
  width: number
  height: number
  modificationTime: number
  lastModified: number
}


class EagleApi {
  private static instance: EagleApi
  private loading = ref(false)
  private error = ref<string | null>(null)

  private constructor() {}

  public static getInstance(): EagleApi {
    if (!EagleApi.instance) {
      EagleApi.instance = new EagleApi()
    }
    return EagleApi.instance
  }

  /**
   * 最新の画像一覧を取得
   * @param limit 
   * @returns 
   */
  public async getRecentImages(limit: number = 100): Promise<TImageItem[]> {
    this.loading.value = true
    this.error.value = null
    console.log('Getting recent images from Python backend...')

    try {
      const response = await fetch(`/api/eagle/recent?limit=${limit}`)
      console.log('API response status:', response.status)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      console.log('API response data:', data)
      console.log('Full API response:', data)
      if (data.status === 'error') {
        console.error('API error:', data.message)
        throw new Error(data.message)
      }
      if (!data.data) {
        console.warn('No data field in response:', data)
        return [];
      }
      console.log('Number of images received:', data.data.length)
      return data.data || [];
    } catch (err) {
      this.error.value = err instanceof Error ? err.message : 'Unknown error occurred'
      return [];
    } finally {
      this.loading.value = false
    }
  }


  public isLoading() {
    return this.loading
  }

  public getError() {
    return this.error
  }
}

export const useEagleApi = () => {
  return EagleApi.getInstance()
}
