<template>
  <div class="blog-search">
    <h2 class="blog-search__title">搜索</h2>
    <div class="blog-search__bar">
      <el-input
        v-model="keyword"
        placeholder="输入关键词搜索文章"
        clearable
        @keyup.enter="onSearch"
      >
        <template #append>
          <el-button :loading="loading" @click="onSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <div v-if="searched" v-loading="loading" class="blog-search__result">
      <ArticleCard v-for="a in articles" :key="a.id" :article="a" />
      <el-empty v-if="!loading && !articles.length" description="未找到相关文章" />
      <Pagination
        :page="page"
        :page-size="pageSize"
        :total="total"
        @update:page="onPageChange"
        @update:page-size="onSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ArticleCard from '@/components/ArticleCard.vue'
import Pagination from '@/components/Pagination.vue'
import { searchBlogArticles } from '@/api/blogArticle'
import type { Article } from '@/types/article'

const route = useRoute()
const keyword = ref('')
const searched = ref(false)
const loading = ref(false)
const articles = ref<Article[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function doSearch() {
  const kw = keyword.value.trim()
  if (!kw) return
  searched.value = true
  loading.value = true
  try {
    const data = await searchBlogArticles(kw, { page: page.value, page_size: pageSize.value })
    articles.value = data.items
    total.value = data.total
  } catch {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  doSearch()
}
function onPageChange(v: number) {
  page.value = v
  doSearch()
}
function onSizeChange(v: number) {
  pageSize.value = v
  page.value = 1
  doSearch()
}

onMounted(() => {
  const q = route.query.q
  if (q) {
    keyword.value = String(q)
    doSearch()
  }
})
</script>

<style scoped lang="scss">
.blog-search {
  max-width: 820px;
  margin: 0 auto;
  padding: 24px 16px;
}
.blog-search__title {
  margin: 0 0 16px;
  font-size: 22px;
}
.blog-search__bar {
  margin-bottom: 16px;
}
</style>
