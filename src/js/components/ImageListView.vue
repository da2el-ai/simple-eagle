<template>
  <div class="relative pb-12">
    <div :class="gridClasses" ref="containerRef">
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

      <!-- スクロール最下部を検知するエレメント -->
      <div ref="scrollRef"></div>
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
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useEagleApi } from '../composables/useEagleApi'
import { API_BASE_URL, ITEM_GET_COUNT } from '../env'
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
const eagleApi = useEagleApi()

// スクロール検知用のref
const containerRef = ref<HTMLElement | null>(null);
const scrollRef = ref<HTMLElement | null>(null);
const imageRefs = ref<HTMLElement[]>([]);

// IntersectionObserver用の変数
let observer: IntersectionObserver | null = null;

// リスト画像サイズ、リストgapサイズ
const itemSize = {
  width: 0,
  height: 0,
  gapX: 0,
  gapY: 0,
};

/**
 * 表示制限用の状態
 */
const maxVisibleItems = computed(() => {
  if (!containerRef.value || imageRefs.value.length === 0) return ITEM_GET_COUNT

  // 表示エリアのサイズ
  const containerWidth = containerRef.value.clientWidth
  const containerHeight = window.innerHeight

  // グリッドアイテムのサイズを取得
  const itemEl = imageRefs.value[0];
  itemSize.width = itemEl.offsetWidth;
  itemSize.height = itemEl.offsetHeight;
  
  // グリッドのギャップを取得
  const gapEl = document.createElement('div');
  const gridStyle = containerRef.value.style;
  gapEl.style.width = gridStyle.columnGap;
  gapEl.style.height = gridStyle.rowGap;
  itemSize.gapX = gapEl.offsetWidth;
  itemSize.gapY = gapEl.offsetHeight;

  // 表示可能アイテム数
  const itemsPerRow = Math.floor((containerWidth + itemSize.gapX) / (itemSize.width + itemSize.gapX));
  const visibleRows = Math.ceil((containerHeight + itemSize.gapY) / (itemSize.height + itemSize.gapY));
  
  // 表示可能なアイテム数 × 1.5
  return Math.ceil(itemsPerRow * visibleRows * 1.5)
})


/**
 * フィルタリング＆表示制限された画像リスト
 */
const filteredImages = computed(() => {
  // Piniaストアから画像とフォルダーを取得
  const allImages = store.getImages
  const currentFilter = store.getCurrentFilter
  
  // console.log('Current Filter:', currentFilter);

  if (!currentFilter) {
    return allImages
  }
  
  return allImages.filter((image) => {
    // 星評価でフィルタリング
    if (currentFilter.stars && currentFilter.stars.length > 0) {
      const imageStar = image.star || 0
      if (!currentFilter.stars.includes(imageStar)) {
        return false
      }
    }
    
    // 拡張子でフィルタリング
    if (currentFilter.exts && currentFilter.exts.length > 0) {
      if (!currentFilter.exts.includes(image.ext.toLowerCase())) {
        return false
      }
    }
    
    // キーワードでフィルタリング（名前に含まれるかチェック）
    if (currentFilter.keyword && currentFilter.keyword.trim() !== '') {
      const keyword = currentFilter.keyword.toLowerCase()
      if (!image.name.toLowerCase().includes(keyword) && !image.annotation.toLowerCase().includes(keyword)) {
        return false
      }
    }
    
    // タグでフィルタリング
    if (currentFilter.tags && currentFilter.tags.length > 0) {
      const hasMatchingTag = currentFilter.tags.some(filterTag => 
        image.tags.some(imageTag => 
          imageTag.toLowerCase().includes(filterTag.toLowerCase())
        )
      )
      if (!hasMatchingTag) {
        return false
      }
    }
    
    return true
  })
})

/**
 * 表示制限された画像リスト
 */
const images = computed(() => {
  // return filteredImages.value.slice(0, maxVisibleItems.value)
  return filteredImages.value;
})

/**
 * 無限スクロール用のハンドラ
 * IntersectionObserverで scrollRef が画面に入ったら次のアイテムを読み込む
 */
const loadImagesInfinite = async () => {
  if (!eagleApi.isImagesLoading.value) {
    console.log("[ImageListView] loadImagesInfinite triggered by IntersectionObserver");

    const currentFolder = store.getCurrentFolder;
    await eagleApi.loadImagesInfinite({
      folderId: currentFolder?.id,
      limit: ITEM_GET_COUNT,
    });
  }
}

// IntersectionObserverのセットアップ
const setupIntersectionObserver = () => {
  if (!scrollRef.value) return;

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          loadImagesInfinite();
        }
      });
    },
    {
      root: null, // viewport を使用
      rootMargin: '100px', // 100px 手前で検知
      threshold: 0.1
    }
  );

  observer.observe(scrollRef.value);
}

// コンポーネントのマウント時にIntersectionObserverを設定
onMounted(() => {
  setupIntersectionObserver();
})

// コンポーネントのアンマウント時にIntersectionObserverを解除
onUnmounted(() => {
  if (observer) {
    observer.disconnect();
  }
})


const ApiBaseUrl = computed(() => {
  return API_BASE_URL;
})

// object-fitの状態管理
const currentObjectFit = computed(() => settings.getObjectFit())

// グリッドクラスを動的に生成
const gridClasses = computed(() => {
  const gridSize = settings.getGridSize();

  return [
    'c-grid',
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
