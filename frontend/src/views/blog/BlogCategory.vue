<template>
  <div class="blog-category">
    <!-- 某分类文章列表 -->
    <template v-if="categoryId">
      <h2 class="blog-category__title">{{ categoryName }}</h2>
      <div v-loading="loading">
        <ArticleCard v-for="a in articles" :key="a.id" :article="a" />
        <el-empty v-if="!loading && !articles.length" description="该分类暂无文章" />
      </div>
      <Pagination
        :page="page"
        :page-size="pageSize"
        :total="total"
        @update:page="onPageChange"
        @update:page-size="onSizeChange"
      />
    </template>

    <!-- 分类导航列表 -->
    <template v-else>
      <h2 class="blog-category__title">分类</h2>
      <div v-loading="loading" class="blog-category__grid">
        <router-link
          v-for="c in categories"
          :key="c.id"
          :to="`/blog/categories/${c.id}`"
          class="blog-category__item"
        >
          <span class="blog-category__name">{{ c.name }}</span>
          <span class="blog-category__count">{{ c.article_count ?? 0 }} 篇</span>
        </router-link>
      </div>
      <el-empty v-if="!loading && !categories.length" description="暂无分类" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ArticleCard from '@/components/ArticleCard.vue'
import Pagination from '@/components/Pagination.vue'
import { getBlogFeed, getBlogCategories } from '@/api/blog'
import type { Article } from '@/types/article'
import type { CategoryStat } from '@/types/blog'

const route = useRoute()
const loading = ref(false)
const categories = ref<CategoryStat[]>([])
const articles = ref<Article[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const categoryId = computed(() => {
  const id = route.params.id
  return id ? Number(id) : null
})

const categoryName = computed(
  () => categories.value.find((c) => c.id === categoryId.value)?.name || '分类文章'
)

async function loadCategories() {
  loading.value = true
  try {
    categories.value = await getBlogCategories()
  } catch {
    // 失败不阻塞
  } finally {
    loading.value = false
  }
}

async function loadArticles() {
  if (!categoryId.value) return
  loading.value = true
  try {
    const data = await getBlogFeed({
      page: page.value,
      page_size: pageSize.value,
      category_id: categoryId.value
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

watch(categoryId, () => {
  page.value = 1
  loadArticles()
})

onMounted(() => {
  loadCategories()
  loadArticles()
})
</script>

<style scoped lang="scss">
.blog-category {
  max-width: 820px;
  margin: 0 auto;
  padding: 24px 16px;
}
.blog-category__title {
  margin: 0 0 16px;
  font-size: 22px;
}
.blog-category__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}
.blog-category__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  color: #303133;
  &:hover {
    border-color: #409eff;
    color: #409eff;
  }
}
.blog-category__count {
  color: #c0c4cc;
  font-size: 12px;
}
</style>
