<template>
  <div class="blog-home">
    <!-- Hero：给首页一个视觉锚点 -->
    <section class="blog-home__hero">
      <div class="blog-home__hero-inner">
        <h1 class="blog-home__hero-title">最新文章</h1>
        <p class="blog-home__hero-desc">笔记、文章与技术分享</p>
      </div>
    </section>

    <div class="blog-home__body">
      <div class="blog-home__main">
        <div class="blog-home__toolbar">
          <el-radio-group v-model="sort" @change="onSortChange">
            <el-radio-button value="latest">最新</el-radio-button>
            <el-radio-button value="hot">热门</el-radio-button>
          </el-radio-group>
          <div class="blog-home__search">
            <el-input
              v-model="keyword"
              placeholder="搜索文章"
              clearable
              @keyup.enter="onSearch"
              @clear="onClearSearch"
            >
              <template #append>
                <el-button :loading="loading" @click="onSearch">搜索</el-button>
              </template>
            </el-input>
          </div>
        </div>

        <div v-if="searching" class="blog-home__search-tip">
          <span>「{{ keyword }}」的搜索结果（共 {{ total }} 条）</span>
          <button type="button" class="blog-home__search-reset" @click="onClearSearch">
            返回全部文章
          </button>
        </div>

        <template v-if="loading">
          <ArticleCardSkeleton v-for="i in 4" :key="i" />
        </template>
        <template v-else>
          <ArticleCard v-for="a in articles" :key="a.id" :article="a" />
          <el-empty v-if="!articles.length" description="暂无文章" />
        </template>

        <Pagination
          :page="page"
          :page-size="pageSize"
          :total="total"
          @update:page="onPageChange"
          @update:page-size="onSizeChange"
        />
      </div>

      <aside class="blog-home__side">
        <BlogWidget title="分类">
          <div class="blog-home__cat-list">
            <router-link v-for="c in categories" :key="c.id" :to="`/blog/categories/${c.id}`">
              <span>{{ c.name }}</span>
              <span class="blog-home__count">{{ c.article_count ?? '' }}</span>
            </router-link>
            <span v-if="!categories.length" class="blog-home__empty">暂无分类</span>
          </div>
        </BlogWidget>

        <BlogWidget title="标签">
          <TagCloud :tags="tags" />
        </BlogWidget>

        <BlogWidget title="热门文章">
          <ol class="blog-home__hot">
            <li v-for="h in hot" :key="h.id">
              <router-link :to="`/blog/articles/${h.id}`">{{ h.title }}</router-link>
              <span class="blog-home__count">{{ h.view_count }} 阅读</span>
            </li>
            <span v-if="!hot.length" class="blog-home__empty">暂无数据</span>
          </ol>
        </BlogWidget>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ArticleCard from '@/components/ArticleCard.vue'
import ArticleCardSkeleton from '@/components/ArticleCardSkeleton.vue'
import BlogWidget from '@/components/BlogWidget.vue'
import Pagination from '@/components/Pagination.vue'
import TagCloud from '@/components/TagCloud.vue'
import { getBlogFeed, getBlogCategories, getBlogTags, getBlogHot } from '@/api/blog'
import { searchBlogArticles } from '@/api/blogArticle'
import type { Article } from '@/types/article'
import type { CategoryStat, TagStat, HotArticle } from '@/types/blog'

const route = useRoute()
const loading = ref(false)
const sort = ref<'latest' | 'hot'>('latest')
const articles = ref<Article[]>([])
const categories = ref<CategoryStat[]>([])
const tags = ref<TagStat[]>([])
const hot = ref<HotArticle[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')
const searching = ref(false)

async function loadFeed() {
  loading.value = true
  try {
    const data = await getBlogFeed({ page: page.value, page_size: pageSize.value, sort: sort.value })
    articles.value = data.items
    total.value = data.total
  } catch {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

async function loadSidebar() {
  try {
    categories.value = await getBlogCategories()
    tags.value = await getBlogTags()
    hot.value = await getBlogHot(10)
  } catch {
    // 侧栏数据失败不阻塞正文
  }
}

async function doSearch() {
  const kw = keyword.value.trim()
  if (!kw) {
    onClearSearch()
    return
  }
  searching.value = true
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

function onClearSearch() {
  keyword.value = ''
  searching.value = false
  page.value = 1
  loadFeed()
}

function onSortChange() {
  page.value = 1
  searching.value ? doSearch() : loadFeed()
}
function onPageChange(v: number) {
  page.value = v
  searching.value ? doSearch() : loadFeed()
}
function onSizeChange(v: number) {
  pageSize.value = v
  page.value = 1
  searching.value ? doSearch() : loadFeed()
}

onMounted(() => {
  loadFeed()
  loadSidebar()
  const q = route.query.q
  if (q) {
    keyword.value = String(q)
    doSearch()
  }
})
</script>

<style scoped lang="scss">
.blog-home__hero {
  /* 极淡的径向渐变 + 纸感底色，避免纯色平铺 */
  background:
    radial-gradient(620px 220px at 12% 0%, rgba(180, 68, 58, 0.06), transparent 70%),
    var(--blog-paper);
  border-bottom: 1px solid var(--blog-line);
  padding: 48px 20px 40px;
}

.blog-home__hero-inner {
  max-width: var(--blog-container);
  margin: 0 auto;
}

.blog-home__hero-title {
  margin: 0 0 8px;
  font-size: 34px;
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -0.02em;
  color: var(--blog-ink);
  text-wrap: balance;
}

.blog-home__hero-desc {
  margin: 0;
  font-size: 14px;
  color: var(--blog-ink-soft);
  letter-spacing: 0.01em;
}

.blog-home__body {
  max-width: var(--blog-container);
  margin: 0 auto;
  padding: 32px 20px 56px;
  display: flex;
  gap: 24px;
}

.blog-home__main {
  flex: 1;
  min-width: 0;
}

.blog-home__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.blog-home__search {
  width: 280px;
}

.blog-home__search-tip {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
  padding: 10px 14px;
  border-left: 3px solid var(--blog-accent);
  background: var(--blog-accent-soft);
  border-radius: var(--blog-radius-sm);
  color: var(--blog-ink-soft);
  font-size: 14px;
}

.blog-home__search-reset {
  appearance: none;
  border: 0;
  background: transparent;
  padding: 0;
  font: inherit;
  font-size: 14px;
  color: var(--blog-accent);
  cursor: pointer;
  transition: color 0.2s;

  &:hover {
    color: var(--blog-accent-dark);
  }
}

.blog-home__side {
  width: 300px;
  flex-shrink: 0;
}

.blog-home__cat-list {
  display: flex;
  flex-direction: column;

  a {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 7px 0;
    font-size: 14px;
    color: var(--blog-ink-soft);
    border-bottom: 1px solid var(--blog-line);
    transition: color 0.2s, transform 0.2s;

    &:last-child {
      border-bottom: 0;
    }

    &:hover {
      color: var(--blog-accent);
      transform: translateX(2px);
    }

    &:active {
      transform: translateX(2px) translateY(1px);
    }
  }
}

.blog-home__hot {
  margin: 0;
  padding: 0;
  list-style: none;
  counter-reset: hot;

  li {
    counter-increment: hot;
    display: flex;
    align-items: baseline;
    gap: 9px;
    padding: 8px 0;
    font-size: 14px;
    line-height: 1.5;
    border-bottom: 1px solid var(--blog-line);

    &:last-child {
      border-bottom: 0;
    }

    &::before {
      content: counter(hot);
      flex-shrink: 0;
      min-width: 14px;
      font-size: 12px;
      font-variant-numeric: tabular-nums;
      color: var(--blog-accent);
    }
  }

  a {
    flex: 1;
    min-width: 0;
    color: var(--blog-ink-soft);
    transition: color 0.2s;

    &:hover {
      color: var(--blog-accent);
    }
  }
}

.blog-home__count {
  color: var(--blog-ink-mute);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.blog-home__empty {
  color: var(--blog-ink-mute);
  font-size: 13px;
}
</style>
