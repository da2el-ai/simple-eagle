import { ref } from 'vue'
import { API_BASE_URL } from '../env'
import type { TImageItem, TFolderItem } from '../types';

class EagleApi {
  private static instance: EagleApi
  private loading = ref(false)
  private error = ref<string | null>(null)
  private folderOpenStates = ref<Record<string, boolean>>({})
  private images = ref<TImageItem[]>([])
  private folders = ref<TFolderItem[]>([])
  private foldersLoading = ref(false)

  private constructor() {}

  public static getInstance(): EagleApi {
    if (!EagleApi.instance) {
      EagleApi.instance = new EagleApi()
    }
    return EagleApi.instance
  }

  /**
   * 最新の画像一覧を取得して内部に保存
   * @param limit 
   * @param folderId 
   */
  public async loadRecentImages(limit: number = 100, folderId?: string): Promise<void> {
    this.loading.value = true
    this.error.value = null
    // console.log('[useEagleApi] loadRecentImages', folderId);

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
        this.images.value = [];
        return;
      }
      // console.log('Number of images received:', data.data.length)
      this.images.value = data.data || [];
    } catch (err) {
      console.error('Error in loadRecentImages:', err)
      this.error.value = err instanceof Error ? err.message : 'Unknown error occurred'
      this.images.value = [];
    } finally {
      this.loading.value = false
    }
  }

  /**
   * 最新の画像一覧を取得（後方互換性のため）
   * @param limit 
   * @returns 
   */
  public async getRecentImages(limit: number = 100, folderId?: string): Promise<TImageItem[]> {
    await this.loadRecentImages(limit, folderId)
    return this.images.value
  }

  /**
   * 保存されている画像リストを取得
   */
  public getImages() {
    return this.images
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
   * フォルダー一覧を取得して内部に保存
   */
  public async loadFolders(): Promise<void> {
    // 既に読み込み中の場合は待機
    if (this.foldersLoading.value) {
      // 読み込み完了まで待機
      while (this.foldersLoading.value) {
        await new Promise(resolve => setTimeout(resolve, 50))
      }
      return
    }

    // 既に読み込み済みの場合はスキップ
    if (this.folders.value.length > 0) {
      return
    }

    this.foldersLoading.value = true
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
        this.folders.value = [];
        return;
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
    
      // 「全て」を先頭に追加して保存
      this.folders.value = [allItem, ...folders]
 
    } catch (err) {
      console.error('Error in loadFolders:', err)
      this.error.value = err instanceof Error ? err.message : 'Unknown error occurred'
      this.folders.value = [];
    } finally {
      this.foldersLoading.value = false
    }
  }


  /**
   * 保存されているフォルダーリストを取得
   */
  public getFoldersSync() {
    return this.folders
  }

  /**
   * 画像情報を更新する
   * @param itemId 画像のID
   * @param data 更新データ（tags, annotation, url, star）
   */
  public async updateItem(itemId: string, data: {
    tags?: string[];
    annotation?: string;
    url?: string;
    star?: number;
  }): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: itemId,
          ...data
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (result.status === 'error') {
        throw new Error(result.message);
      }

      // 成功した場合、現在のimages配列内の該当アイテムも更新
      const index = this.images.value.findIndex(img => img.id === itemId);
      if (index !== -1) {
        this.images.value[index] = {
          ...this.images.value[index],
          ...data
        };
      }

      return result;
    } catch (error) {
      console.error('Error updating item:', error);
      throw error;
    }
  }
}

export const useEagleApi = () => {
  return EagleApi.getInstance()
}
