<template>
  <ModalView v-if="isOpen" :showCloseButton="false" @close="handleClose" :fit-width="true">
    <div class="fixed left-0 top-0 w-[min(80vw,20rem)] h-full bg-white shadow-lg overflow-y-auto">
      <div class="p-4">

        <div v-if="loading" class="text-center py-4">
          読み込み中...
        </div>
        
        <div v-else-if="error" class="text-red-500 py-4">
          {{ error }}
        </div>
        <template v-else>
          <FolderTreeItem
            v-for="folder in folders"
            :key="folder.id"
            :folder="folder"
            @select="handleFolderSelect"
          />
        </template>
      </div>
    </div>
  </ModalView>
</template>

<script setup lang="ts">
import { useEagleApi } from '../composables/useEagleApi'
import ModalView from './ModalView.vue'
import FolderTreeItem from './FolderTreeItem.vue'
// import CloseButton from './CloseButton.vue'

defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'update:isOpen', value: boolean): void
  (e: 'select', folderId: string): void
}>()

const eagleApi = useEagleApi()
const folders = eagleApi.getFoldersSync()
const loading = eagleApi.isLoading()
const error = eagleApi.getError()

const handleClose = () => {
  emit('update:isOpen', false)
}

const handleFolderSelect = (folderId: string) => {
  emit('select', folderId)
  emit('update:isOpen', false)
}

</script>
