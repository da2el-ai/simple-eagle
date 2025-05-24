<template>
  <div class="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-6">
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
          :src="`/api/eagle/get_thumbnail_image?id=${image.id}`"
          :alt="image.name"
          class="w-full h-full object-cover"
          loading="lazy"
          @error="handleImageError(image)"
        />

        <span class="c-badge" :data-clickable="isClickableImage(image) ? 'true' : 'false'">{{ image.ext.toUpperCase() }}</span>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useEagleApi } from '../composables/useEagleApi'

import type { TImageItem } from '../composables/useEagleApi'

const eagleApi = useEagleApi()
const images = ref<TImageItem[]>([])

// イベントの定義
const emit = defineEmits<{
  'image-click': [image: TImageItem]
}>()

// クリック可能な画像かどうかを判定
const isClickableImage = (image: TImageItem): boolean => {
  const clickableExtensions = ['png', 'jpg', 'jpeg', 'webp']
  return clickableExtensions.includes(image.ext.toLowerCase())
}

// 画像クリック時の処理
const handleImageClick = (image: TImageItem) => {
  emit('image-click', image)
}

const handleImageError = (image: TImageItem) => {
  console.error('Failed to load image:', image.name)
}

onMounted(async () => {
  console.log('ImageList component mounted')
  images.value = await eagleApi.getRecentImages()
})
</script>
