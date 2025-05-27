<template>
  <div class="relative">
    <div :class="gridClasses">
      <!-- 子フォルダーボタン -->
      <div 
        v-for="childFolder in childFolders" 
        :key="`folder-${childFolder.id}`" 
        class="relative aspect-square"
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
      <div v-for="image in images" :key="image.id" class="relative aspect-square">
        <div
          :class="[
            'w-full h-full bg-gray-100 rounded overflow-hidden relative',
            isClickableImage(image) ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''
          ]"
          ref="imageRefs"
          @click="isClickableImage(image) ? handleImageClick(image) : null"
        >
          <img
            :src="`${ApiBaseUrl}/get_thumbnail_image?id=${image.id}`"
            :alt="image.name"
            class="w-full h-full object-cover"
            loading="lazy"
            @error="handleImageError(image)"
          />

          <span class="c-badge" :data-clickable="isClickableImage(image) ? 'true' : 'false'">{{ image.ext.toUpperCase() }}</span>

        </div>
      </div>
    </div>

    <!-- グリッドサイズ変更ボタン -->
    <GridSizeControl 
      :grid-size="currentGridSize" 
      @update:grid-size="updateGridSize"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useEagleApi } from '../composables/useEagleApi'
import { API_BASE_URL } from '../composables/useSettings';
import type { TImageItem, TFolderItem } from '../composables/useEagleApi'
import GridSizeControl from './GridSizeControl.vue'

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

// グリッドサイズの状態管理
const currentGridSize = ref({
  base: 4,    // 基本サイズ
  md: 5,      // mdサイズ
  xl: 6       // xlサイズ
})

// グリッドサイズ更新関数
const updateGridSize = (newGridSize: { base: number, md: number, xl: number }) => {
  currentGridSize.value = newGridSize
}

// グリッドクラスを動的に生成
const gridClasses = computed(() => {
  return [
    'grid',
    'gap-6',
    `grid-cols-${currentGridSize.value.base}`,
    `md:grid-cols-${currentGridSize.value.md}`,
    `xl:grid-cols-${currentGridSize.value.xl}`
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
