<template>
  <div class="blog-tag">
    <!-- 某标签文章列表 -->
    <template v-if="tagName">
      <header class="blog-tag__head">
        <h2 class="blog-tag__title"># {{ tagName }}</h2>
        <span class="blog-tag__stat">共 {{ total }} 篇</span>
      </header>

      <template v-if="loading">
        <div class="blog-tag__grid">
          <ArticleCardSkeleton v-for="i in 4" :key="i" variant="compact" />
        </div>
      </template>
      <template v-else>
        <div v-if="articles.length" class="blog-tag__grid">
          <ArticleCard v-for="a in articles" :key="a.id" :article="a" variant="compact" />
        </div>
        <el-empty v-else description="该标签暂无文章" />
      </template>

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
      <header class="blog-tag__head">
        <h2 class="blog-tag__title">标签</h2>
        <span class="blog-tag__stat">共 {{ tags.length }} 个</span>
      </header>

      <BlogWidget v-loading="loading">
        <TagCloud :tags="tags" />
      </BlogWidget>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ArticleCard from '@/components/ArticleCard.vue'
import ArticleCardSkeleton from '@/components/ArticleCardSkeleton.vue'
import BlogWidget from '@/components/BlogWidget.vue'
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
  max-width: var(--blog-container);
  margin: 0 auto;
  padding: 40px 20px 56px;
}

.blog-tag__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--blog-line);
}

.blog-tag__title {
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

.blog-tag__title::before {
  content: '';
  width: 3px;
  height: 20px;
  border-radius: 2px;
  background: var(--blog-accent);
  flex: none;
}

.blog-tag__stat {
  font-size: 13px;
  color: var(--blog-ink-mute);
  font-variant-numeric: tabular-nums;
}

.blog-tag__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-bottom: 8px;
}

@media (max-width: 900px) {
  .blog-tag {
    padding: 28px 16px 48px;
  }

  .blog-tag__grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .blog-tag__title {
    font-size: 21px;
  }
}
</style>
