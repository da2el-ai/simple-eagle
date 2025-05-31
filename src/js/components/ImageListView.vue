<template>
  <div class="relative pb-12">
    <div :class="gridClasses">
      <!-- 子フォルダーボタン -->
      <ImagelistviewFolder
        v-for="childFolder in childFolders"
        :key="`folder-${childFolder.id}`" 
        :child-folder="childFolder"
      />

      <!-- 画像リスト -->
      <div v-for="image in images" :key="image.id" class="c-grid-item relative">
        <div
          :class="[
            'bg-gray-100 rounded overflow-hidden relative aspect-square',
            isClickableImage(image) ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''
          ]"
          ref="imageRefs"
          @click="isClickableImage(image) ? handleImageClick(image) : null"
        >
          <img
            :src="`${ApiBaseUrl}/get_thumbnail_image?id=${image.id}`"
            :alt="image.name"
            :class="['w-full h-full', `object-${currentObjectFit}`]"
            loading="lazy"
            @error="handleImageError(image)"
          />

          <span class="c-badge" :data-clickable="isClickableImage(image) ? 'true' : 'false'">{{ image.ext.toUpperCase() }}</span>
        </div>

        <div class="py-1">
          <StarRatingMini :model-value="image.star || 0" />
        </div>
      </div>
      <!-- /.c-grid-item -->
    </div>

    <div class="fixed bottom-4 right-4 flex items-center gap-2">
      <!-- object-fit 変更ボタン -->
      <ObjectFitControl />

      <!-- グリッドサイズ変更ボタン -->
      <GridSizeControl />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { API_BASE_URL } from '../env'
import { useSettings } from '../composables/useSettings'
import { useMainStore } from '../store'
import { useRouter } from 'vue-router'
import type { TImageItem } from '../types'
import GridSizeControl from './GridSizeControl.vue'
import ObjectFitControl from './ObjectFitControl.vue'
import StarRatingMini from './StarRatingMini.vue'
import ImagelistviewFolder from './ImageListFolder.vue';

const settings = useSettings()
const store = useMainStore()
const router = useRouter()

// Piniaストアから画像とフォルダーを取得
const images = computed(() => store.getImages)


const ApiBaseUrl = computed(() => {
  return API_BASE_URL;
})

// object-fitの状態管理
const currentObjectFit = computed(() => settings.getObjectFit())

// グリッドクラスを動的に生成
const gridClasses = computed(() => {
  const gridSize = settings.getGridSize();

  return [
    'grid',
    'gap-6',
    `grid-cols-${gridSize.base}`,
    `md:grid-cols-${gridSize.md}`,
    `xl:grid-cols-${gridSize.xl}`
  ].join(' ')
})

// 現在のフォルダーの子フォルダーを取得
const childFolders = computed(() => store.getChildFolders);
// 現在のフォルダーを取得
const currentFolder = computed(() => store.getCurrentFolder);

// クリック可能な画像かどうかを判定
const isClickableImage = (image: TImageItem): boolean => {
  return true;
  // const clickableExtensions = ['png', 'jpg', 'jpeg', 'webp']
  // return clickableExtensions.includes(image.ext.toLowerCase())
}

// 画像クリック時の処理
const handleImageClick = (image: TImageItem) => {
  router.push(`/folder/${currentFolder.value?.id || 'all'}/detail/${image.id}`)
}

const handleImageError = (image: TImageItem) => {
  console.error('Failed to load image:', image.name, image)
}
</script>
