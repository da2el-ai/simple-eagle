<template>
  <ModalView @close="closeLightbox" :showCloseButton="true">
    <section class="c-lightbox relative">
      <figure class="relative text-center" v-if="image">
        <img
          :src="`${API_BASE_URL}/get_image?id=${image.id}&ext=${image.ext}&max_file_size=${settings.getMaxFileSize()}&quality=${settings.getQuality()}`"
          :alt="image.name" class="m-auto max-w-full max-h-full object-contain" />

        <!-- 左ナビゲーションエリア -->
        <button v-if="canGoPrevious" @click="goToPrevious"
          class="absolute top-0 left-0 w-1/5 h-full bg-transparent active:bg-white active:bg-opacity-50 cursor-pointer z-10">
          <span class="sr-only">前の画像</span>
        </button>

        <!-- 右ナビゲーションエリア -->
        <button v-if="canGoNext" @click="goToNext"
          class="absolute top-0 right-0 w-1/5 h-full bg-transparent active:bg-white active:bg-opacity-50 cursor-pointer z-10">
          <span class="sr-only">次の画像</span>
        </button>
      </figure>

      <Dialog :showCloseButton="false" v-if="image">
        <!-- 画像情報パネル -->
        <div>
          <!-- 評価 -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">評価</label>
            <StarRating v-model="currentRating" @change="updateRating" />
          </div>

          <!-- 画像名 -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">ファイル名</label>
            <p class="text-sm text-gray-900">{{ image.name }}</p>
          </div>

          <!-- フォルダ -->
          <div class="mb-4" v-if="image.folders && image.folders.length > 0">
            <label class="block text-sm font-medium text-gray-700 mb-1">フォルダ</label>
            <div class="flex flex-wrap gap-1">
              <span v-for="folder in image.folders" :key="folder"
                class="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                {{ folder }}
              </span>
            </div>
          </div>

          <!-- タグ -->
          <div class="mb-4" v-if="image.tags && image.tags.length > 0">
            <label class="block text-sm font-medium text-gray-700 mb-1">タグ</label>
            <div class="flex flex-wrap gap-1">
              <span v-for="tag in image.tags" :key="tag"
                class="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                {{ tag }}
              </span>
            </div>
          </div>

          <!-- 注釈 -->
          <div class="mb-4" v-if="image.annotation">
            <label class="block text-sm font-medium text-gray-700 mb-1">注釈</label>
            <p class="text-sm text-gray-900 whitespace-pre-wrap">{{ image.annotation }}</p>
          </div>

          <!-- ファイル情報 -->
          <div class="mb-4">
            <div class="text-sm text-gray-600 space-y-1">
              <div>サイズ: {{ formatFileSize(image.size) }}</div>
              <div>形式: {{ image.ext.toUpperCase() }}</div>
              <div>解像度: {{ image.width }} × {{ image.height }}px</div>
              <div>更新日時: {{ formatDate(image.modificationTime) }}</div>
              <div>最終変更: {{ formatDate(image.lastModified) }}</div>
            </div>
          </div>
        </div>
      </Dialog>
    </section>
  </ModalView>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { API_BASE_URL } from '../env';
import { useSettings } from '../composables/useSettings';
import { useEagleApi } from '../composables/useEagleApi';
import { useMainStore } from '../store';
import ModalView from './ModalView.vue';
import Dialog from './Dialog.vue';
import StarRating from './StarRating.vue';
import { formatFileSize, formatDate } from '../modules/util';

const router = useRouter()

// サービスの取得
const settings = useSettings()
const eagleApi = useEagleApi()
const store = useMainStore()

// // マウント時に現在の画像を設定
// onMounted(() => {
//   console.log('Lightbox mounted, current image:', store.getCurrentImage);
// })

// 現在の画像（Piniaストアから取得）
const image = computed(() => store.getCurrentImage)

// 前の画像に移動可能かどうか
const canGoPrevious = computed(() => {
  return store.getPrevImage !== null
})

// 次の画像に移動可能かどうか
const canGoNext = computed(() => {
  return store.getNextImage !== null
})

// 前の画像に移動
const goToPrevious = () => {
  if (store.getPrevImage) {
    router.push({name: 'folderDetail', params: { folderId: store.getCurrentFolderId, imageId: store.getPrevImage.id }});
  }
}

// 次の画像に移動
const goToNext = () => {
  if (store.getNextImage) {
    router.push({name: 'folderDetail', params: { folderId: store.getCurrentFolderId, imageId: store.getNextImage.id }});
  }
}

// 閉じる
const closeLightbox = () => {
  router.push({name: 'folder', params: { folderId: store.getCurrentFolderId }});
}


// 評価の状態管理
const currentRating = ref(image.value?.star || 0)

// 評価値の更新とAPI呼び出し
const updateRating = async (rating: number) => {
  if (!image.value) return

  const oldRating = currentRating.value
  try {
    await eagleApi.updateItem(image.value.id, {
      star: rating
    })
  } catch (error) {
    currentRating.value = oldRating
    console.error('評価の更新に失敗しました:', error)
  }
}

// 画像が変更されたときに評価値を更新
watch(() => image.value, (newImage) => {
  currentRating.value = newImage?.star || 0
}, { immediate: true })

</script>
