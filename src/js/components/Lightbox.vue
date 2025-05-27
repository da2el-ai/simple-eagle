<template>

    <section class="relative">

        <div class="relative">
            <img :src="`${API_BASE_URL}/get_image?id=${image.id}&ext=${image.ext}&max_file_size=${settings.getMaxFileSize()}&quality=${settings.getQuality()}`"
                :alt="image.name" class="max-w-full max-h-full object-contain" />
            
            <!-- 左ナビゲーションエリア -->
            <button 
                v-if="canGoPrevious"
                @click="goToPrevious"
                class="absolute top-0 left-0 w-1/5 h-full bg-transparent active:bg-white active:bg-opacity-50 cursor-pointer z-10"
            >
                <span class="sr-only">前の画像</span>
            </button>
            
            <!-- 右ナビゲーションエリア -->
            <button 
                v-if="canGoNext"
                @click="goToNext"
                class="absolute top-0 right-0 w-1/5 h-full bg-transparent active:bg-white active:bg-opacity-50 cursor-pointer z-10"
            >
                <span class="sr-only">次の画像</span>
            </button>
        </div>

        <Dialog @close="$emit('close')" :showCloseButton="false">
            <!-- 画像情報パネル -->
            <div>
                <h3 class="text-lg font-semibold mb-4 text-gray-900">画像情報</h3>

                <!-- 画像名 -->
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">ファイル名</label>
                    <p class="text-sm text-gray-900 break-words">{{ image.name }}</p>
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

</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSettings, API_BASE_URL } from '../composables/useSettings'
import Dialog from './Dialog.vue'
import type { TImageItem } from '../composables/useEagleApi'

// プロパティの定義
type TLightboxProps = {
    image: TImageItem
    images: TImageItem[]
}

const props = defineProps<TLightboxProps>()

// エミット定義
const emit = defineEmits<{
    close: []
    'image-change': [image: TImageItem]
}>()

// 設定を取得
const settings = useSettings()


// 現在の画像のインデックス
const currentIndex = computed(() => {
    return props.images.findIndex(img => img.id === props.image.id)
})

// 前の画像に移動可能かどうか
const canGoPrevious = computed(() => {
    return currentIndex.value > 0
})

// 次の画像に移動可能かどうか
const canGoNext = computed(() => {
    return currentIndex.value < props.images.length - 1
})

// 前の画像に移動
const goToPrevious = () => {
    if (canGoPrevious.value) {
        const prevImage = props.images[currentIndex.value - 1]
        emit('image-change', prevImage)
    }
}

// 次の画像に移動
const goToNext = () => {
    if (canGoNext.value) {
        const nextImage = props.images[currentIndex.value + 1]
        emit('image-change', nextImage)
    }
}


// ファイルサイズをフォーマット
const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'

    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 日時をフォーマット
const formatDate = (timestamp: number): string => {
    const date = new Date(timestamp * 1000) // Eagleのタイムスタンプは秒単位
    return date.toLocaleString('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    })
}
</script>
