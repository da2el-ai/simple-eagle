<template>
  <div class="relative pb-12" ref="viewportRef">
    <!-- 仮想スクロールコンテナ -->
    <div 
      :style="{ height: totalHeight + 'px' }" 
      class="relative"
    >
      <!-- 上部オフセット用のスペーサー -->
      <div :style="{ height: offsetY + 'px' }"></div>
      
      <!-- 実際に表示されるコンテンツ -->
      <div :class="gridClasses" ref="containerRef">
        <!-- 子フォルダーボタン（常に表示） -->
        <ImagelistviewFolder
          v-for="childFolder in childFolders"
          :key="`folder-${childFolder.id}`" 
          :child-folder="childFolder"
        />

        <!-- 仮想化された画像リスト -->
        <div v-for="image in visibleImages" :key="image.id" class="c-grid-item relative">
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
        <div ref="interSectionRef"></div>
      </div>
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
/**
 * size: 91 x 91
 * gap: 5
 * area: 382
 * 配置数: 387 / 96 = 4
 * 総数: 600 item
 * 行数: 600 / 4 = 150
 * 全体高さ: 150 * 96 = 14400
 * 実際の表示: 120000px おかしい
 */

import { computed, ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
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
const viewportRef = ref<HTMLElement | null>(null);
const containerRef = ref<HTMLElement | null>(null);
const interSectionRef = ref<HTMLElement | null>(null);
const imageRefs = ref<HTMLElement[]>([]);

// IntersectionObserver用の変数
let observer: IntersectionObserver | null = null;

// 仮想スクロール用の状態
const scrollTop = ref(0);
const containerHeight = ref(0);
const overscan = 5; // 表示範囲外でも描画するアイテム数

// リスト画像サイズ、リストgapサイズ
const listInfo = ref({
  imageWidth: 0,
  imageHeight: 0,
  gapX: 0,
  gapY: 0,
  lineWidth: 0,
  lineHeight: 200,
  itemsPerLine: 1,
});


// index.py のURL
const ApiBaseUrl = computed(() => { return API_BASE_URL })

// object-fitの状態管理
const currentObjectFit = computed(() => settings.getObjectFit())

// 現在のフォルダーの子フォルダーを取得
const childFolders = computed(() => store.getChildFolders);

// 現在のフォルダーを取得
const currentFolder = computed(() => store.getCurrentFolder);

// 全ての画像
const allImages = computed(() => store.getImages);

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



/**
 * フィルタリング＆表示制限された画像リスト
 */
const filteredImages = computed(() => {
  // Piniaストアから画像とフォルダーを取得
  // const allImages = store.getImages
  const currentFilter = store.getCurrentFilter
  
  // console.log('Current Filter:', currentFilter);

  if (!currentFilter) {
    return allImages.value
  }
  
  return allImages.value.filter((image) => {
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


// スクロールハンドラ（ページ全体のスクロールを監視）
const handleScroll = () => {
  scrollTop.value = window.pageYOffset || document.documentElement.scrollTop
}

/**
 * グリッドレイアウト情報の計算
 */
const gridInfo = computed(() => {
  if (!containerRef.value || listInfo.value.imageWidth === 0) {
    return {
      itemsPerLine: listInfo.value.itemsPerLine,
      totalRows: filteredImages.value.length,
      lineHeight: listInfo.value.lineHeight,
    }
  }
  const totalItems = filteredImages.value.length
  const totalRows = Math.ceil(totalItems / listInfo.value.itemsPerLine)

  console.log("[ImageListView] gridInfo", listInfo.value.itemsPerLine, totalRows, listInfo.value.lineHeight);
  
  return {
    itemsPerLine: listInfo.value.itemsPerLine,
    totalRows,
    lineHeight: listInfo.value.lineHeight
  }
})

/**
 * 表示範囲計算（DOM仮想化の核心部分）- グリッド対応
 */
const visibleRange = computed(() => {
  // ImageListViewコンポーネントの位置を考慮したスクロール計算
  const viewportHeight = window.innerHeight
  const { lineHeight, totalRows, itemsPerLine } = gridInfo.value
  
  // ImageListViewコンポーネントの上端位置を取得
  const componentTop = viewportRef.value?.offsetTop || 0
  const relativeScrollTop = Math.max(0, scrollTop.value - componentTop)
  
  const startRow = Math.max(0, Math.floor(relativeScrollTop / lineHeight) - overscan)
  const endRow = Math.min(
    totalRows - 1,
    Math.ceil((relativeScrollTop + viewportHeight) / lineHeight) + overscan
  )
  console.log(`[ImageListView] visibleRange scrollTop:${scrollTop.value}, componentTop:${componentTop}, relativeScrollTop:${relativeScrollTop}, viewportHeight:${viewportHeight}, lineHeight:${lineHeight}`)
  
  const startIndex = startRow * itemsPerLine
  const endIndex = Math.min(
    filteredImages.value.length - 1,
    (endRow + 1) * itemsPerLine - 1
  )
  console.log(`[ImageListView] visibleRange startIndex:${startIndex}, endIndex:${endIndex}, startRow:${startRow}, endRow:${endRow}`)
  
  return { startIndex, endIndex, startRow, endRow }
})

// 実際にDOMに描画する画像（仮想化されたリスト）
const visibleImages = computed(() => {
  const { startIndex, endIndex } = visibleRange.value
  return filteredImages.value.slice(startIndex, endIndex + 1).map((image, index) => ({
    ...image,
    virtualIndex: startIndex + index // 仮想インデックス
  }))
})

// 全体の高さ（スクロールバー用）- グリッド対応
const totalHeight = computed(() => {
  const { totalRows, lineHeight } = gridInfo.value
  return totalRows * lineHeight
})

// 上部のオフセット（見えない部分の高さ）- グリッド対応
const offsetY = computed(() => {
  const { startRow } = visibleRange.value
  const { lineHeight } = gridInfo.value
  return startRow * lineHeight
})

/**
 * DOM要素が描画されるまで待機する関数
 */
const waitForImageRefs = async (maxRetries = 10, delay = 50): Promise<boolean> => {
  for (let i = 0; i < maxRetries; i++) {
    await nextTick()
    if (imageRefs.value.length > 0) {
      // さらに少し待機してDOM要素が完全に描画されるのを確実にする
      await new Promise(resolve => setTimeout(resolve, delay))
      return true
    }
    await new Promise(resolve => setTimeout(resolve, delay))
  }
  return false
}

/**
 * マウントとリサイズ時に実行
 * アイテムサイズの計算と更新
 */
const updateListInfo = async () => {
  // imageRefsが描画されるまで待機
  const hasImageRefs = await waitForImageRefs()
  
  if (!hasImageRefs) {
    return
  }
  
  if (containerRef.value && imageRefs.value.length > 0) {
    const firstItem = imageRefs.value[0]
    if (firstItem) {
      // グリッドアイテムのサイズを取得
      listInfo.value.imageWidth = firstItem.offsetWidth
      listInfo.value.imageHeight = firstItem.offsetHeight
      
      // グリッドのギャップを取得（CSS gridのgapプロパティから）
      const computedStyle = window.getComputedStyle(containerRef.value)
      const columnGap = computedStyle.columnGap
      const rowGap = computedStyle.rowGap
      
      // ギャップサイズを計算（rem、px、その他の単位に対応）
      const gapEl = document.createElement('div')
      gapEl.style.position = 'absolute'
      gapEl.style.visibility = 'hidden'
      gapEl.style.width = columnGap
      gapEl.style.height = rowGap
      document.body.appendChild(gapEl)
      
      listInfo.value.gapX = Math.floor(gapEl.offsetWidth -1)
      listInfo.value.gapY = Math.floor(gapEl.offsetHeight -1)
      
      document.body.removeChild(gapEl)
      
      // 行の高さを計算（アイテムの高さ + ギャップ）
      listInfo.value.lineHeight = listInfo.value.imageHeight + listInfo.value.gapY
      // 行の幅
      listInfo.value.lineWidth = containerRef.value.clientWidth
      // １行に入る画像数
      listInfo.value.itemsPerLine = Math.floor((listInfo.value.lineWidth + listInfo.value.gapX) / (listInfo.value.imageWidth + listInfo.value.gapX))

      console.log("[ImageListView] updateListInfo", listInfo.value);
    }
  }
  
  if (viewportRef.value) {
    containerHeight.value = viewportRef.value.clientHeight
  }
}

//////////////////////////////
// スクロールでデータ追加
//////////////////////////////

/**
 * 無限スクロール用のハンドラ
 * IntersectionObserverで interSectionRef が画面に入ったら次のアイテムを読み込む
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

/**
 * IntersectionObserverのセットアップ
 */
const setupIntersectionObserver = () => {
  if (!interSectionRef.value) return;

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

  observer.observe(interSectionRef.value);
}

// 読み込み数が変わったらリスト情報更新
watch([allImages, gridClasses], async ()=>{
  await nextTick()
  console.log("[ImageListView] 画像リスト更新された");
  updateListInfo();
});

// スクロール位置の変化を監視
watch(scrollTop, (newScrollTop) => {
  console.log(`[ImageListView] scrollTop changed: ${newScrollTop}`);
});

// 表示範囲の変化を監視
watch(visibleRange, (newRange) => {
  console.log(`[ImageListView] visibleRange changed:`, newRange);
});

// ウィンドウリサイズハンドラ
const handleResize = () => {
  updateListInfo()
}

// コンポーネントマウント時の処理を更新
onMounted(async () => {
  setupIntersectionObserver()
  await updateListInfo()
  window.addEventListener('resize', handleResize)
  window.addEventListener('scroll', handleScroll)
})

// コンポーネントアンマウント時の処理を更新
onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('scroll', handleScroll)
})
</script>
