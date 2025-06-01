<template>
  <ModalView v-if="isFilterOpen" @close="closeFilter" :showCloseButton="false" :fit-height="true">
    <Dialog @close="closeFilter">
      <div class="max-w-2xl mx-auto">
        <h2 class="text-1xl font-bold mb-6">フィルター条件設定</h2>
        
        <form @submit.prevent="handleApplyFilter" class="space-y-5">
          <!-- 評価 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              評価
            </label>
            <div class="flex flex-wrap gap-x-4 gap-y-2">
              <label v-for="star in 5" :key="star" class="flex items-center">
                <input
                  v-model="filterForm.stars"
                  :value="star"
                  type="checkbox"
                  class="mr-1"
                />
                <span class="flex" style="font-size:0.8rem">
                  <span v-for="i in star" :key="i" class="" style="color:#ff9900">★</span>
                  <span v-for="i in 5 - star" :key="i" class="text-gray-400">★</span>
                </span>
              </label>
            </div>
          </div>

          <!-- 拡張子 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              拡張子
            </label>
            <div class="flex gap-2 gap-x-4 flex-wrap">
              <label v-for="ext in store.getExtList" :key="ext" class="flex items-center">
                <input
                  v-model="filterForm.extensions"
                  :value="ext"
                  type="checkbox"
                  class="mr-1"
                />
                <span class="text-sm">{{ ext.toUpperCase() }}</span>
              </label>
            </div>
          </div>

          <!-- キーワード -->
          <div>
            <label for="keyword" class="block text-sm font-medium text-gray-700 mb-2">
              キーワード
            </label>
            <input
              id="keyword"
              v-model="filterForm.keyword"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="検索キーワードを入力"
            />
          </div>

          <!-- タグ -->
          <div>
            <label for="tags" class="block text-sm font-medium text-gray-700 mb-2">
              タグ
            </label>
            <input
              id="tags"
              v-model="filterForm.tags"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="タグを「,」区切りで入力"
            />
            <p class="mt-1 text-sm text-gray-500">
              複数のタグを「,」区切りで入力してください
            </p>
          </div>

          <!-- ボタン -->
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="closeFilter"
              class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
            >
              キャンセル
            </button>
            <button
              type="submit"
              class="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
            >
              決定
            </button>
          </div>
        </form>
      </div>
    </Dialog>
  </ModalView>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMainStore } from '../store';
import ModalView from './ModalView.vue';
import Dialog from './Dialog.vue';

const store = useMainStore()
const router = useRouter()

// フィルターフォームの状態
const filterForm = ref({
  stars: [] as number[],
  extensions: [] as string[],
  keyword: '',
  tags: ''
})

// フィルターが開いているかどうかをcomputedプロパティで管理
const isFilterOpen = computed(() => {
  return store.getFilterOpen;
})

// フィルターを適用
const handleApplyFilter = () => {
  // いずれかの項目が入力されているかチェック
  const hasFilter = 
    filterForm.value.stars.length > 0 ||
    filterForm.value.extensions.length > 0 ||
    filterForm.value.keyword.trim() !== '' ||
    filterForm.value.tags.trim() !== ''

  if (hasFilter) {
    // 検索ルートに移動
    router.push({
      name: 'search',
      params: { folderId: store.getCurrentFolderId || 'all' },
      query: {
        stars: filterForm.value.stars.join(','),
        ext: filterForm.value.extensions.join(','),
        keyword: filterForm.value.keyword,
        tags: filterForm.value.tags
      }
    })
  } else {
    // 全ての項目が空欄の場合はフォルダールートに移動
    router.push({
      name: 'folder',
      params: { folderId: store.getCurrentFolderId || 'all' }
    })
  }
}

// フィルターを閉じる
const closeFilter = () => {
  store.setFilterOpen(false);
}

// コンポーネントマウント時の処理
onMounted(() => {
  // 必要に応じて初期化処理
})
</script>
