<template>
  <div class="relative pb-12">
    <div :class="gridClasses">
      <!-- 子フォルダーボタン -->
      <div 
        v-for="childFolder in childFolders" 
        :key="`folder-${childFolder.id}`" 
        class="c-grid-item relative aspect-square"
      >
        <div
          class="w-full h-full bg-blue-50 rounded overflow-hidden relative cursor-pointer hover:bg-blue-100 transition-colors flex flex-col items-center justify-center"
          @click="handleFolderClick(childFolder.id)"
        >
          <!-- フォルダーアイコン -->
          <div class="text-blue-500 text-2xl mb-2">📁</div>
          
          <!-- フォルダー名 -->
          <span class="text-xs text-blue-700 text-center px-2 truncate w-full">
            {{ childFolder.name }}
          </span>
          
          <!-- 画像数 -->
          <span class="text-xs text-blue-500 mt-1">
            ({{ childFolder.imageCount }})
          </span>
        </div>
      </div>

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
import { useEagleApi } from '../composables/useEagleApi'
import { API_BASE_URL } from '../env'
import { useSettings } from '../composables/useSettings';
import type { TImageItem, TFolderItem } from '../types'
import GridSizeControl from './GridSizeControl.vue'
import ObjectFitControl from './ObjectFitControl.vue'
import StarRatingMini from './StarRatingMini.vue'

const settings = useSettings()

const props = defineProps<{
  folderId?: string
}>()

const emit = defineEmits<{
  'image-click': [image: TImageItem]
  'folder-click': [folderId: string]
}>()

const eagleApi = useEagleApi()
const images = eagleApi.getImages()
const allFolders = eagleApi.getFoldersSync()

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
const childFolders = computed(() => {
  // if (!props.folderId) {
  //   // ルートレベルの場合、トップレベルフォルダーを返す
  //   return allFolders.value
  // }
  
  // 指定されたフォルダーIDの子フォルダーを検索
  const findChildren = (folders: TFolderItem[], targetId: string): TFolderItem[] => {
    for (const folder of folders) {
      if (folder.id === targetId) {
        return folder.children || []
      }
      if (folder.children && folder.children.length > 0) {
        const result = findChildren(folder.children, targetId)
        if (result.length > 0) {
          return result
        }
      }
    }
    return []
  }
  
  return props.folderId ? findChildren(allFolders.value, props.folderId) : []
})

// クリック可能な画像かどうかを判定
const isClickableImage = (image: TImageItem): boolean => {
  const clickableExtensions = ['png', 'jpg', 'jpeg', 'webp']
  return clickableExtensions.includes(image.ext.toLowerCase())
}

// 画像クリック時の処理
const handleImageClick = (image: TImageItem) => {
  emit('image-click', image)
}

// フォルダークリック時の処理
const handleFolderClick = (folderId: string) => {
  emit('folder-click', folderId)
}

const handleImageError = (image: TImageItem) => {
  console.error('Failed to load image:', image.name, image)
}
</script>
