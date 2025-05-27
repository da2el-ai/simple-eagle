import { ref } from 'vue'
import { API_BASE_URL } from './useSettings';

export type TFolderItem = {
  id: string
  name: string
  description: string
  children: TFolderItem[]
  modificationTime: number
  tags: string[]
  imageCount: number
  descendantImageCount: number
  pinyin: string
  extendTags: string[]
}

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
  private folderOpenStates = ref<Record<string, boolean>>({})

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
  public async getRecentImages(limit: number = 100, folderId?: string): Promise<TImageItem[]> {
    this.loading.value = true
    this.error.value = null
    // console.log('[useEagleApi] getRecentImages', folderId);

    try {
      const url = new URL(`${API_BASE_URL}/recent`, window.location.origin)
      url.searchParams.append('limit', limit.toString())
      if (folderId) {
        url.searchParams.append('folder_id', folderId)
      }
      const response = await fetch(url)
      // console.log('API response status:', response.status)
      if (!response.ok) {
        console.error(`HTTP error! status: ${response.status}`)
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      // console.log('API response data:', data)
      if (data.status === 'error') {
        console.error('API error:', data.message)
        throw new Error(data.message)
      }
      if (!data.data) {
        console.warn('No data field in response:', data)
        return [];
      }
      // console.log('Number of images received:', data.data.length)
      return data.data || [];
    } catch (err) {
      console.error('Error in getRecentImages:', err)
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

  /**
   * フォルダーの開閉状態を取得
   */
  public getFolderOpenState(folderId: string): boolean {
    return this.folderOpenStates.value[folderId] || false
  }

  /**
   * フォルダーの開閉状態を設定
   */
  public setFolderOpenState(folderId: string, isOpen: boolean): void {
    this.folderOpenStates.value[folderId] = isOpen
  }

  /**
   * フォルダーの開閉状態を切り替え
   */
  public toggleFolderOpenState(folderId: string): boolean {
    const currentState = this.getFolderOpenState(folderId)
    const newState = !currentState
    this.setFolderOpenState(folderId, newState)
    return newState
  }

  /**
   * 子フォルダの imageCount の合計を親フォルダの imageCount に設定する
   */
  calculateTotalImageCount(folders: TFolderItem[]): number {
    let total = 0
    
    for (const folder of folders) {
      // 子フォルダーがある場合、再帰的に処理
      if (folder.children && folder.children.length > 0) {
        // 子フォルダーの imageCount を再帰的に計算
        const childrenTotal = this.calculateTotalImageCount(folder.children)
        // 親フォルダーの imageCount を子フォルダーの合計 + 自身の imageCount に設定
        folder.imageCount = folder.imageCount + childrenTotal
      }
      
      // 全体の合計に追加
      total += folder.imageCount
    }
    
    return total
  }

  /**
   * フォルダー一覧を取得
   */
  public async getFolders(): Promise<TFolderItem[]> {
    this.loading.value = true
    this.error.value = null

    try {
      const response = await fetch(`${API_BASE_URL}/folders`)
      // console.log('API response status:', response.status)
      if (!response.ok) {
        console.error(`HTTP error! status: ${response.status}`)
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      if (data.status === 'error') {
        console.error('API error:', data.message)
        throw new Error(data.message)
      }
      if (!data.data) {
        console.warn('No data field in response:', data)
        return [];
      }

      const folders = data.data;

      // 全てのフォルダーのimageCountを合計
      const totalImageCount = this.calculateTotalImageCount(folders);

      // 「全て」アイテムを作成
      const allItem: TFolderItem = {
        id: "",
        name: "全て",
        description: "",
        children: [],
        modificationTime: Date.now(),
        tags: [],
        imageCount: totalImageCount,
        descendantImageCount: 0,
        pinyin: "",
        extendTags: []
      }
    
      // 「全て」を先頭に追加して返す
      return [allItem, ...folders]
 
    } catch (err) {
      console.error('Error in getFolders:', err)
      this.error.value = err instanceof Error ? err.message : 'Unknown error occurred'
      return [];
    } finally {
      this.loading.value = false
    }
  }
}

export const useEagleApi = () => {
  return EagleApi.getInstance()
}
