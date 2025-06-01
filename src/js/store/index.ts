import { defineStore } from 'pinia'
import type { TImageItem, TFolderItem } from '../types'
import { getters } from './getters'
import { actions } from './actions'

// フィルターパラメータの型定義
export type TFilterParam = {
  star?: number
  ext?: string
}

// ストアの状態の型定義
export type TStoreState = {
  images: TImageItem[]
  folders: TFolderItem[]
  currentImage: TImageItem | null
  currentFolderId: string | null
  expandedFolders: string[]
  filterParam: TFilterParam
  extList: string[]  // 拡張子リスト
  isSettingOpen: boolean // 設定画面の開閉状態
  isFilterOpen: boolean // フィルター画面の開閉状態
}

export const useMainStore = defineStore('main', {
  state: (): TStoreState => ({
    images: [],
    folders: [],
    currentImage: null,
    currentFolderId: null,
    expandedFolders: [],
    filterParam: {},
    extList: [],
    isSettingOpen: false,
    isFilterOpen: false,
  }),

  getters,
  actions
})
