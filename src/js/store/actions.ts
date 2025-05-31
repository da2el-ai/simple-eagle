import type { TImageItem, TFolderItem } from '../types'
import type { TStoreState } from './index'

export const actions = {
  // 画像一覧を設定
  setImages(this: TStoreState, images: TImageItem[]) {
    this.images = images;
  },
  
  // フォルダ一覧を設定
  setFolders(this: TStoreState, folders: TFolderItem[]) {
    this.folders = folders;
  },
  
  // 現在の画像を設定
  setCurrentImage(this: TStoreState, imageId: string) {
    const image = this.images.find((img: TImageItem) => img.id === imageId);
    this.currentImage = image || null;
  },
  
  // 現在のフォルダIDを設定
  setCurrentFolderId(this: TStoreState, folderId: string) {
    this.currentFolderId = folderId;
  },
  
  // 展開フォルダを追加
  addExpandedFolder(this: TStoreState, folderId: string) {
    if (!this.expandedFolders.includes(folderId)) {
      this.expandedFolders.push(folderId);
    }
  },
  
  // 展開フォルダを削除
  removeExpandedFolder(this: TStoreState, folderId: string) {
    const index = this.expandedFolders.indexOf(folderId);
    if (index > -1) {
      this.expandedFolders.splice(index, 1);
    }
  }
}
