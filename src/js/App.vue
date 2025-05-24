<template>
  <div class="container mx-auto p-4">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold mb-4">Simple Eagle</h1>
      <!-- 歯車ボタン（設定画面を開く） -->
      <button
        @click="showSettings = true"
        class="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-full transition-colors"
        title="設定"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
        </svg>
      </button>
    </div>
    <ImageListView @image-click="openLightbox" />
    
    <!-- 設定モーダル -->
    <ModalView v-if="showSettings" @close="showSettings = false" :showCloseButton="false">
      <Dialog @close="showSettings = false">
        <SettingView @close="showSettings = false" />
      </Dialog>
    </ModalView>
    
    <!-- Lightboxモーダル -->
    <ModalView v-if="showLightbox && selectedImage" @close="closeLightbox" :showCloseButton="true">
      <Lightbox :image="selectedImage" @close="closeLightbox" />
    </ModalView>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ImageListView from './components/ImageListView.vue'
import ModalView from './components/ModalView.vue'
import Dialog from './components/Dialog.vue'
import SettingView from './components/SettingView.vue'
import Lightbox from './components/Lightbox.vue'
import type { TImageItem } from './composables/useEagleApi'

// 設定画面の表示状態
const showSettings = ref(false)

// Lightboxの表示状態
const showLightbox = ref(false)
const selectedImage = ref<TImageItem | null>(null)

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
</script>
