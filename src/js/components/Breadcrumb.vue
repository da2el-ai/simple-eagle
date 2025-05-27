<template>
  <div class="basis-full text-sm text-blue-500">
    <!-- パンくずリストを表示 -->
    <nav class="flex items-center space-x-2" v-if="breadcrumbPath.length > 0">
      <!-- ホーム -->
      <button 
        @click="handleBreadcrumbClick(null)"
        class="hover:text-gray-600 transition-colors"
        :class="{ 'text-blue-500 font-medium': !currentFolderId }"
      >
        すべて
      </button>
      
      <!-- パンくずの各階層 -->
      <template v-for="(item, index) in breadcrumbPath" :key="item.id">
        <span class="text-gray-300">></span>
        <button 
          @click="handleBreadcrumbClick(item.id)"
          class="hover:text-gray-600 transition-colors truncate max-w-32"
          :class="{ 'text-gray-600 font-medium': item.id === currentFolderId }"
          :title="item.name"
        >
          {{ item.name }}
        </button>
      </template>
    </nav>
    
    <!-- フォルダーが選択されていない場合 -->
    <nav v-else class="flex items-center">
      <span class="text-gray-400 font-medium">すべて</span>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useEagleApi, type TFolderItem } from '../composables/useEagleApi'

const props = defineProps<{
  currentFolderId?: string
}>()

const emit = defineEmits<{
  (e: 'folderSelect', folderId: string | null): void
}>()

const eagleApi = useEagleApi()
const folders = ref<TFolderItem[]>([])

// フォルダーIDから親フォルダーまでのパスを取得する関数
const findFolderPath = (folderId: string, folderList: TFolderItem[]): TFolderItem[] => {
  for (const folder of folderList) {
    if (folder.id === folderId) {
      return [folder]
    }
    
    if (folder.children && folder.children.length > 0) {
      const childPath = findFolderPath(folderId, folder.children)
      if (childPath.length > 0) {
        return [folder, ...childPath]
      }
    }
  }
  return []
}

// パンくずリストのパスを計算
const breadcrumbPath = computed(() => {
  if (!props.currentFolderId || folders.value.length === 0) {
    return []
  }
  return findFolderPath(props.currentFolderId, folders.value)
})

// パンくずリストのクリック処理
const handleBreadcrumbClick = (folderId: string | null) => {
  emit('folderSelect', folderId)
}

// フォルダー一覧を取得
onMounted(async () => {
  folders.value = await eagleApi.getFolders()
})

// currentFolderIdが変更された時にフォルダー一覧を再取得（必要に応じて）
watch(() => props.currentFolderId, () => {
  // 必要に応じてフォルダー一覧を再取得
})
</script>
