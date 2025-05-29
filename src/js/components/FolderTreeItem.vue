<template>
  <div class="c-tree-item text-sm pl-4">

    <!-- ボタン部分 -->
    <div
      class="flex items-center py-2 cursor-pointer hover:bg-gray-100"
      @click="handleClick"
    >
      <!-- 展開ボタン -->
      <button
        v-if="folder.children?.length"
        class="w-4 h-4 mr-2 flex items-center justify-center"
        @click.stop="isOpen = !isOpen"
      >
        {{ isOpen ? '▼' : '▶' }}
      </button>
      <span v-else class="w-4 h-4 mr-2"></span>

      <!-- フォルダー名 -->
      <span class="truncate">{{ folder.name }}</span>
      <span v-if="folder.imageCount > 0" class="ml-2 text-gray-500 text-sm">
        ({{ folder.imageCount }})
      </span>
    </div>

    <!-- 子ツリー -->
    <div v-if="isOpen && folder.children?.length" class="pl-2">
      <FolderTreeItem
        v-for="child in folder.children"
        :key="child.id"
        :folder="child"
        @select="$emit('select', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useEagleApi } from '../composables/useEagleApi'
import type { TFolderItem } from '../types';

const props = defineProps<{
  folder: TFolderItem
}>()

const emit = defineEmits<{
  (e: 'select', folderId: string): void
}>()

const eagleApi = useEagleApi()

// グローバルな開閉状態を使用
const isOpen = computed({
  get: () => eagleApi.getFolderOpenState(props.folder.id),
  set: (value: boolean) => eagleApi.setFolderOpenState(props.folder.id, value)
})

const handleClick = () => {
  emit('select', props.folder.id)
}

// const toggleOpen = () => {
//   isOpen.value = !isOpen.value
// }
</script>
