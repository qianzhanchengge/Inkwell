<template>
  <div class="blog-tag">
    <!-- 某标签文章列表 -->
    <template v-if="tagName">
      <h2 class="blog-tag__title"># {{ tagName }}</h2>
      <div v-loading="loading">
        <ArticleCard v-for="a in articles" :key="a.id" :article="a" />
        <el-empty v-if="!loading && !articles.length" description="该标签暂无文章" />
      </div>
      <Pagination
        :page="page"
        :page-size="pageSize"
        :total="total"
        @update:page="onPageChange"
        @update:page-size="onSizeChange"
      />
    </template>

    <!-- 标签云 -->
    <template v-else>
      <h2 class="blog-tag__title">标签</h2>
      <el-card v-loading="loading" shadow="never">
        <TagCloud :tags="tags" />
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ArticleCard from '@/components/ArticleCard.vue'
import Pagination from '@/components/Pagination.vue'
import TagCloud from '@/components/TagCloud.vue'
import { getBlogFeed, getBlogTags } from '@/api/blog'
import type { Article } from '@/types/article'
import type { TagStat } from '@/types/blog'

const route = useRoute()
const loading = ref(false)
const tags = ref<TagStat[]>([])
const articles = ref<Article[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const tagName = computed(() => (route.params.tag ? String(route.params.tag) : ''))

async function loadTags() {
  loading.value = true
  try {
    tags.value = await getBlogTags()
  } catch {
    // 失败不阻塞
  } finally {
    loading.value = false
  }
}

async function loadArticles() {
  if (!tagName.value) return
  loading.value = true
  try {
    const data = await getBlogFeed({
      page: page.value,
      page_size: pageSize.value,
      tag: tagName.value
    })
    articles.value = data.items
    total.value = data.total
  } catch {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

function onPageChange(v: number) {
  page.value = v
  loadArticles()
}
function onSizeChange(v: number) {
  pageSize.value = v
  page.value = 1
  loadArticles()
}

watch(tagName, () => {
  page.value = 1
  loadArticles()
})

onMounted(() => {
  loadTags()
  loadArticles()
})
</script>

<style scoped lang="scss">
.blog-tag {
  max-width: 820px;
  margin: 0 auto;
  padding: 24px 16px;
}
.blog-tag__title {
  margin: 0 0 16px;
  font-size: 22px;
}
</style>
