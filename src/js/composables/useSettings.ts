import { ref } from 'vue'

// 設定データの型定義
export type TSettings = {
  max_file_size: number | null
  quality: number | null
}

// デフォルト設定値
const DEFAULT_SETTINGS = {
  max_file_size: 768,
  quality: 85
} as const

// localStorage のキー
const STORAGE_KEY = 'eagle_viewer_settings'

export function useSettings() {
  // 設定データ
  const settings = ref<TSettings>({
    max_file_size: null,
    quality: null
  })

  // localStorageから設定を読み込む
  const loadSettings = () => {
    try {
      const savedSettings = localStorage.getItem(STORAGE_KEY)
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings)
        settings.value = {
          max_file_size: parsed.max_file_size || null,
          quality: parsed.quality || null
        }
      }
    } catch (error) {
      console.error('設定の読み込みに失敗しました:', error)
      // エラーの場合はデフォルト値を設定
      resetToDefaults()
    }
  }

  // 設定を保存
  const saveSettings = () => {
    const settingsToSave = {
      max_file_size: settings.value.max_file_size || DEFAULT_SETTINGS.max_file_size,
      quality: settings.value.quality || DEFAULT_SETTINGS.quality
    }
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settingsToSave))
    return settingsToSave
  }

  // デフォルト値にリセット
  const resetToDefaults = () => {
    settings.value = {
      max_file_size: DEFAULT_SETTINGS.max_file_size,
      quality: DEFAULT_SETTINGS.quality
    }
  }

  // 実際の設定値を取得（nullの場合はデフォルト値を返す）
  const getActualSettings = () => {
    return {
      max_file_size: settings.value.max_file_size ?? DEFAULT_SETTINGS.max_file_size,
      quality: settings.value.quality ?? DEFAULT_SETTINGS.quality
    }
  }

  // ファイルサイズ上限を取得
  const getMaxFileSize = (): number => {
    return settings.value.max_file_size ?? DEFAULT_SETTINGS.max_file_size
  }

  // 圧縮率を取得
  const getQuality = (): number => {
    return settings.value.quality ?? DEFAULT_SETTINGS.quality
  }

  // 圧縮が必要かどうかを判定
  const shouldCompress = (fileSizeKB: number): boolean => {
    const maxSize = getMaxFileSize()
    return maxSize > 0 && fileSizeKB > maxSize
  }

  // 設定をクリア
  const clearSettings = () => {
    localStorage.removeItem(STORAGE_KEY)
    settings.value = {
      max_file_size: null,
      quality: null
    }
  }

  // 初期化時に設定を読み込み
  const initialize = () => {
    loadSettings()
  }

  return {
    // リアクティブデータ
    settings,
    
    // 関数
    loadSettings,
    saveSettings,
    resetToDefaults,
    getActualSettings,
    getMaxFileSize,
    getQuality,
    shouldCompress,
    clearSettings,
    initialize,
    
    // 定数
    DEFAULT_SETTINGS
  }
}
