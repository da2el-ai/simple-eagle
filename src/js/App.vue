<template>
  <div class="container mx-auto p-4">
    <header class="flex flex-wrap justify-between items-center mb-4 z-10 bg-white sticky top-0">
      <div class="flex items-center gap-4">
        <!-- フォルダビュー表示ボタン -->
        <HamburgerButton @click="showFolderList = true" />

        <!-- タイトル -->
        <h1 class="text-2xl font-bold">Simple Eagle</h1>
      </div>

      <!-- ツール系ボタン -->
      <div class="flex item-center justify-end gap-4">
        <!-- フィルターボタン -->
        <FilterButton @click="showFilter" />
        <!-- 選択ボタンをここに追加 -->
      </div>

      <Breadcrumb />
    </header>

    <!-- 画像一覧表示 -->
    <ImageListView />
    
    <!-- フォルダー一覧モーダル -->
    <FolderTreeView v-model:isOpen="showFolderList" />

    <!-- 設定画面 -->
    <SettingView />

    <!-- フィルター条件設定モーダル -->
    <FilterView />

    <!-- ルータービュー -->
    <router-view />
    
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import ImageListView from './components/ImageListView.vue';
import HamburgerButton from './components/HamburgerButton.vue';
import FolderTreeView from './components/FolderTreeView.vue';
import SettingView from './components/SettingView.vue'
import FilterButton from './components/FilterButton.vue';
import FilterView from './components/FilterView.vue';
import Breadcrumb from './components/Breadcrumb.vue';
import { useEagleApi } from './composables/useEagleApi';
import { useMainStore } from './store';
import { useRoute, useRouter } from 'vue-router';

// モーダルの表示状態
const showFolderList = ref(false);

// サービスの取得
const eagleApi = useEagleApi();
const store = useMainStore();
const route = useRoute();
const router = useRouter();

const loadImages = async (folderId:string) => {
  if ( folderId === store.getCurrentFolderId ) return;

  // console.log("Loading images for folder:", folderId, store.getCurrentFolderId);
  store.setCurrentFolderId(folderId as string);
  await eagleApi.loadImages(100, folderId);
}

// フィルターを表示
const showFilter = () => {
  store.setFilterOpen(true);
}

// URLが変更されたらstoreに反映
watch(
  [() => route.params.folderId, () => route.params.imageId],
  async ([folderId, imageId], [prevFolderId, prevImageId]) => {
    // console.log("Folder ID from URL:", folderId);
    folderId = folderId as string || "all";

    // フォルダーの変更
    if ( folderId !== prevFolderId ) {
      // console.log("Changing folder to:", folderId);
      loadImages(folderId as string);
    }

    if (imageId !== prevImageId && imageId && typeof imageId === 'string') {
      // 初期読み込みが完了している場合は即座に設定
      if (!eagleApi.isImagesLoading.value) {
        store.setCurrentImage(imageId);
      }
    }
  },
)

// 初期読み込み
onMounted(async () => {
  await router.isReady()
  // console.log("App mounted, loading initial data...");
  // console.log(route.params);

  // フォルダー一覧の読み込み
  await eagleApi.loadFolders();

  // 画像の初期読み込み
  const folderId = route.params.folderId as string || "all";
  await loadImages(folderId as string);

  // 初期読み込み完了後、URLにimageIdがある場合は設定
  const imageId = route.params.imageId
  if (imageId && typeof imageId === 'string') {
    store.setCurrentImage(imageId)
  }
})

</script>
