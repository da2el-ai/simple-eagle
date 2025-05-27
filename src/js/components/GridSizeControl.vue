<template>
  <!-- グリッドサイズ変更ボタン -->
  <div class="fixed bottom-4 right-4 flex items-center bg-white shadow-lg rounded-lg border">
    <button 
      @click="decreaseGridSize"
      :disabled="!canDecrease"
      class="px-3 py-2 text-lg font-bold hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed rounded-l-lg"
    >
      −
    </button>
    <div class="px-2 py-2 text-sm text-gray-500 border-l border-r">
      {{ currentDisplayedGridSize }}
    </div>
    <button 
      @click="increaseGridSize"
      :disabled="!canIncrease"
      class="px-3 py-2 text-lg font-bold hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed rounded-r-lg"
    >
      ＋
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

// プロパティの定義
const props = defineProps<{
  gridSize: {
    base: number
    md: number
    xl: number
  }
}>()

// エミット定義
const emit = defineEmits<{
  'update:gridSize': [gridSize: { base: number, md: number, xl: number }]
}>()

// 画面サイズの検出
const screenSize = ref<'base' | 'md' | 'xl'>('base')

// 最小・最大値の定義
const minGridSize = {
  base: 1,
  md: 2,
  xl: 3
}
const maxGridSize = {
  base: 6,
  md: 8,
  xl: 10
}

// 画面サイズを更新する関数
const updateScreenSize = () => {
  const width = window.innerWidth
  if (width >= 1280) { // xl breakpoint
    screenSize.value = 'xl'
  } else if (width >= 768) { // md breakpoint
    screenSize.value = 'md'
  } else {
    screenSize.value = 'base'
  }
}

// 現在の画面サイズに対応するグリッドサイズを取得
const currentDisplayedGridSize = computed(() => {
  return props.gridSize[screenSize.value]
})

// // 現在の画面サイズに対応する最大値を取得
// const currentMaxGridSize = computed(() => {
//   return maxGridSize[screenSize.value]
// })

// // 現在の画面サイズに対応する最小値を取得
// const currentMinGridSize = computed(() => {
//   return minGridSize[screenSize.value]
// })

// グリッドサイズを増加
const increaseGridSize = () => {
  const newGridSize = { ...props.gridSize }
  
  if (newGridSize.base < maxGridSize.base) {
    newGridSize.base++
  }
  if (newGridSize.md < maxGridSize.md) {
    newGridSize.md++
  }
  if (newGridSize.xl < maxGridSize.xl) {
    newGridSize.xl++
  }
  
  emit('update:gridSize', newGridSize)
}

// グリッドサイズを減少
const decreaseGridSize = () => {
  const newGridSize = { ...props.gridSize }
  
  if (newGridSize.base > minGridSize.base) {
    newGridSize.base--
  }
  if (newGridSize.md > minGridSize.md) {
    newGridSize.md--
  }
  if (newGridSize.xl > minGridSize.xl) {
    newGridSize.xl--
  }
  
  emit('update:gridSize', newGridSize)
}

// 増加可能かどうか
const canIncrease = computed(() => {
  return props.gridSize.base < maxGridSize.base ||
         props.gridSize.md < maxGridSize.md ||
         props.gridSize.xl < maxGridSize.xl
})

// 減少可能かどうか
const canDecrease = computed(() => {
  return props.gridSize.base > minGridSize.base ||
         props.gridSize.md > minGridSize.md ||
         props.gridSize.xl > minGridSize.xl
})

// ライフサイクルフック
onMounted(() => {
  updateScreenSize()
  window.addEventListener('resize', updateScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateScreenSize)
})
</script>
