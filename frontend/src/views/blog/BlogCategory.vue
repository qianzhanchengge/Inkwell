<template>
  <div class="blog-category">
    <!-- 某分类文章列表 -->
    <template v-if="categoryId">
      <header class="blog-category__head">
        <h2 class="blog-category__title">{{ categoryName }}</h2>
        <span class="blog-category__stat">共 {{ total }} 篇</span>
      </header>

      <template v-if="loading">
        <div class="blog-category__grid">
          <ArticleCardSkeleton v-for="i in 4" :key="i" variant="compact" />
        </div>
      </template>
      <template v-else>
        <div v-if="articles.length" class="blog-category__grid">
          <ArticleCard v-for="a in articles" :key="a.id" :article="a" variant="compact" />
        </div>
        <el-empty v-else description="该分类暂无文章" />
      </template>

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
      <header class="blog-category__head">
        <h2 class="blog-category__title">分类</h2>
        <span class="blog-category__stat">共 {{ categories.length }} 个</span>
      </header>

      <div v-loading="loading" class="blog-category__nav">
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
import ArticleCardSkeleton from '@/components/ArticleCardSkeleton.vue'
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
  max-width: var(--blog-container);
  margin: 0 auto;
  padding: 40px 20px 56px;
}

/* 页头：标题 + 统计（左竖条沿用 widget 标题语言） */
.blog-category__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--blog-line);
}

.blog-category__title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--blog-ink);
  text-wrap: balance;
}

.blog-category__title::before {
  content: '';
  width: 3px;
  height: 20px;
  border-radius: 2px;
  background: var(--blog-accent);
  flex: none;
}

.blog-category__stat {
  font-size: 13px;
  color: var(--blog-ink-mute);
  font-variant-numeric: tabular-nums;
}

/* 文章网格 */
.blog-category__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-bottom: 8px;
}

/* 分类导航 */
.blog-category__nav {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
}

.blog-category__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border: 1px solid var(--blog-line);
  border-radius: var(--blog-radius-sm);
  background: var(--blog-surface);
  color: var(--blog-ink);
  box-shadow: var(--blog-shadow-sm);
  transition: border-color 0.2s, color 0.2s, transform 0.2s, box-shadow 0.2s;

  &:hover {
    border-color: var(--blog-accent);
    color: var(--blog-accent);
    box-shadow: var(--blog-shadow-md);
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(1px);
  }
}

.blog-category__count {
  color: var(--blog-ink-mute);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
}

@media (max-width: 900px) {
  .blog-category {
    padding: 28px 16px 48px;
  }

  .blog-category__grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .blog-category__title {
    font-size: 21px;
  }
}
</style>
