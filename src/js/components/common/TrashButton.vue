<template>
  <!-- ゴミ箱ボタン -->
  <button
    @click="$emit('click')"
    class="p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
    title="削除"
  >
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      class="text-gray-600"
    >
      <path
        d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14zM10 11v6M14 11v6"
        stroke="currentColor"
        stroke-width="2"
        fill="none"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  </button>
</template>

<script setup lang="ts">
// イベントの定義
defineEmits<{
  click: []
}>()
</script>
