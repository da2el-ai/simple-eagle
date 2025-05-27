<template>
  <div class="container mx-auto p-4">
    <header class="flex flex-wrap justify-between items-center mb-4">
      <div class="flex items-center gap-4">
        <!-- フォルダビュー表示ボタン -->
        <HamburgerButton @click="showFolderList = true" />

        <!-- タイトル -->
        <h1 class="text-2xl font-bold">Simple Eagle</h1>
      </div>

      <!-- 設定ボタン -->
      <SettingButton @click="showSettings = true" />

      <Breadcrumb 
        :current-folder-id="currentFolderId" 
        @folder-select="handleFolderSelect"
      />
    </header>

    <!-- 画像一覧表示 -->
    <ImageListView 
      @image-click="openLightbox" 
      @folder-click="handleFolderSelect"
      :folder-id="currentFolderId" 
    />
    
    <!-- 設定モーダル -->
    <ModalView v-if="showSettings" @close="showSettings = false" :showCloseButton="false" :fit-height="true">
      <Dialog @close="showSettings = false">
        <SettingView @close="showSettings = false" />
      </Dialog>
    </ModalView>
    
    <!-- Lightboxモーダル -->
    <ModalView v-if="showLightbox && selectedImage" @close="closeLightbox" :showCloseButton="true">
      <Lightbox 
        :image="selectedImage" 
        :images="currentImages"
        @close="closeLightbox" 
        @image-change="handleImageChange"
      />
    </ModalView>

    <!-- フォルダー一覧モーダル -->
    <FolderTreeView
      v-model:isOpen="showFolderList"
      @select="handleFolderSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import ImageListView from './components/ImageListView.vue'
import ModalView from './components/ModalView.vue'
import Dialog from './components/Dialog.vue'
import SettingView from './components/SettingView.vue'
import Lightbox from './components/Lightbox.vue'
import HamburgerButton from './components/HamburgerButton.vue'
import FolderTreeView from './components/FolderTreeView.vue'
import SettingButton from './components/SettingButton.vue'
import Breadcrumb from './components/Breadcrumb.vue'
import type { TImageItem } from './composables/useEagleApi'
import { useEagleApi } from './composables/useEagleApi'

// モーダルの表示状態
const showSettings = ref(false)
const showFolderList = ref(false)

// Lightboxの表示状態
const showLightbox = ref(false)
const selectedImage = ref<TImageItem | null>(null)

// 現在選択中のフォルダー
const currentFolderId = ref<string | undefined>()

// EagleAPIインスタンス
const eagleApi = useEagleApi()

// 現在の画像リストを取得
const currentImages = eagleApi.getImages()

// Lightboxを開く
const openLightbox = (image: TImageItem) => {
  selectedImage.value = image
  showLightbox.value = true
}

// Lightboxを閉じる
const closeLightbox = () => {
  showLightbox.value = false
  selectedImage.value = null
}

// 画像変更時の処理
const handleImageChange = (image: TImageItem) => {
  selectedImage.value = image
}

// 画像リストを読み込む
const loadImages = async () => {
  await eagleApi.loadRecentImages(100, currentFolderId.value)
}

// フォルダーリストを読み込む
const loadFolders = async () => {
  await eagleApi.loadFolders()
}

// フォルダー選択時の処理（BreadcrumbとFolderTreeViewから）
const handleFolderSelect = (folderId: string | null) => {
  // console.log("handleFolderSelect", folderId)
  currentFolderId.value = folderId || undefined
}

// フォルダーIDが変更されたら画像を再読み込み
watch(() => currentFolderId.value, () => {
  loadImages()
})

// 初期読み込み
onMounted(() => {
  loadFolders()
  loadImages()
})

</script>
